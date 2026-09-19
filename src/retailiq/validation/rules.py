"""Row-level business rules for retail transaction sources."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

MONEY_QUANTUM = Decimal("0.01")


def _decimal(value: str, field: str) -> Decimal:
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, AttributeError) as exc:
        raise ValueError(f"{field} is not numeric") from exc


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def validate_rows(
    rows: Iterable[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, int]]:
    """Validate rows and return accepted rows, rejected rows, and reason counts.

    Validation is intentionally performed before warehouse loading. A rejected row
    retains its source values plus a deterministic reason so that failures are
    observable and recoverable rather than silently dropped.
    """

    materialized = list(rows)
    transaction_counts = Counter(row.get("transaction_id", "").strip() for row in materialized)
    accepted: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    reasons: Counter[str] = Counter()

    for row_number, row in enumerate(materialized, start=2):
        row = {key: (value or "").strip() for key, value in row.items()}
        row["_source_row_number"] = str(row_number)
        row_reasons: list[str] = []
        transaction_id = row.get("transaction_id", "")
        if not transaction_id:
            row_reasons.append("missing_transaction_id")
        elif transaction_counts[transaction_id] > 1:
            row_reasons.append("duplicate_transaction_id")

        for field in ("customer_id", "product_id", "store_id"):
            if not row.get(field):
                row_reasons.append(f"missing_{field}")

        try:
            transaction_date = date.fromisoformat(row.get("transaction_date", ""))
            if transaction_date > date.today():
                row_reasons.append("future_transaction_date")
        except ValueError:
            row_reasons.append("invalid_transaction_date")

        numeric: dict[str, Decimal] = {}
        for field in ("quantity", "unit_price", "discount", "sales_amount", "cost", "profit"):
            try:
                numeric[field] = _decimal(row.get(field, ""), field)
            except ValueError as exc:
                row_reasons.append(str(exc))

        if "quantity" in numeric and numeric["quantity"] <= 0:
            row_reasons.append("non_positive_quantity")
        if "unit_price" in numeric and numeric["unit_price"] < 0:
            row_reasons.append("negative_unit_price")
        if "discount" in numeric and not Decimal("0") <= numeric["discount"] <= Decimal("1"):
            row_reasons.append("discount_out_of_range")
        if "cost" in numeric and numeric["cost"] < 0:
            row_reasons.append("negative_cost")

        if all(
            field in numeric for field in ("quantity", "unit_price", "discount", "sales_amount")
        ):
            expected_sales = _money(
                numeric["quantity"] * numeric["unit_price"] * (Decimal("1") - numeric["discount"])
            )
            if abs(expected_sales - _money(numeric["sales_amount"])) > MONEY_QUANTUM:
                row_reasons.append("sales_amount_mismatch")
        if all(field in numeric for field in ("sales_amount", "cost", "profit")):
            expected_profit = _money(numeric["sales_amount"] - numeric["cost"])
            if abs(expected_profit - _money(numeric["profit"])) > MONEY_QUANTUM:
                row_reasons.append("profit_mismatch")

        if row_reasons:
            row["_validation_errors"] = "|".join(sorted(set(row_reasons)))
            rejected.append(row)
            reasons.update(set(row_reasons))
        else:
            accepted.append(row)

    summary = {
        "source_rows": len(materialized),
        "accepted_rows": len(accepted),
        "rejected_rows": len(rejected),
        **{f"rejected_{key}": value for key, value in sorted(reasons.items())},
    }
    return accepted, rejected, summary
