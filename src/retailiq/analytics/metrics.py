"""Dataset profiling and KPI calculations for the local demonstration."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


def _money(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calculate_metrics(path: Path) -> dict[str, Any]:
    """Calculate verified project metrics from a transaction CSV."""

    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("Cannot profile an empty dataset")

    revenue = Decimal("0")
    profit = Decimal("0")
    units = 0
    customers: Counter[str] = Counter()
    products: Counter[str] = Counter()
    categories: Counter[str] = Counter()
    stores: Counter[str] = Counter()
    category_stats: dict[str, dict[str, Decimal | int]] = defaultdict(
        lambda: {"revenue": Decimal("0"), "profit": Decimal("0"), "units": 0}
    )
    product_stats: dict[str, dict[str, Decimal | int | str]] = defaultdict(
        lambda: {
            "revenue": Decimal("0"),
            "profit": Decimal("0"),
            "product_name": "",
            "category": "",
        }
    )
    customer_revenue: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    monthly_revenue: defaultdict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    store_stats: dict[str, dict[str, Decimal | str]] = defaultdict(
        lambda: {"revenue": Decimal("0"), "profit": Decimal("0"), "store_location": ""}
    )

    for row in rows:
        row_revenue = Decimal(row["sales_amount"])
        row_profit = Decimal(row["profit"])
        row_units = int(row["quantity"])
        revenue += row_revenue
        profit += row_profit
        units += row_units
        customers[row["customer_id"]] += 1
        products[row["product_id"]] += 1
        categories[row["category"]] += 1
        stores[row["store_id"]] += 1
        customer_revenue[row["customer_id"]] += row_revenue
        month = row["transaction_date"][:7]
        monthly_revenue[month] += row_revenue
        category_stats[row["category"]]["revenue"] += row_revenue
        category_stats[row["category"]]["profit"] += row_profit
        category_stats[row["category"]]["units"] += row_units
        product_stats[row["product_id"]]["revenue"] += row_revenue
        product_stats[row["product_id"]]["profit"] += row_profit
        product_stats[row["product_id"]]["product_name"] = row["product_name"]
        product_stats[row["product_id"]]["category"] = row["category"]
        store_stats[row["store_id"]]["revenue"] += row_revenue
        store_stats[row["store_id"]]["profit"] += row_profit
        store_stats[row["store_id"]]["store_location"] = row["store_location"]

    ordered_months = sorted(monthly_revenue)
    latest_year = max(month[:4] for month in ordered_months)
    prior_year = str(int(latest_year) - 1)
    latest_year_revenue = sum(
        (value for month, value in monthly_revenue.items() if month.startswith(latest_year)),
        Decimal("0"),
    )
    prior_year_revenue = sum(
        (value for month, value in monthly_revenue.items() if month.startswith(prior_year)),
        Decimal("0"),
    )
    growth = (
        (latest_year_revenue - prior_year_revenue) / prior_year_revenue * Decimal("100")
        if prior_year_revenue
        else Decimal("0")
    )
    top_product = max(product_stats.items(), key=lambda item: item[1]["revenue"])
    category_rows = [
        {
            "category": category,
            "revenue": _money(stats["revenue"]),
            "profit": _money(stats["profit"]),
            "profit_margin_pct": _money(stats["profit"] / stats["revenue"] * Decimal("100")),
            "units": stats["units"],
        }
        for category, stats in sorted(
            category_stats.items(), key=lambda item: item[1]["revenue"], reverse=True
        )
    ]
    product_rows = [
        {
            "product_id": product_id,
            "product_name": stats["product_name"],
            "category": stats["category"],
            "revenue": _money(stats["revenue"]),
            "profit": _money(stats["profit"]),
        }
        for product_id, stats in sorted(
            product_stats.items(), key=lambda item: item[1]["revenue"], reverse=True
        )
    ]
    store_rows = [
        {
            "store_id": store_id,
            "store_location": stats["store_location"],
            "revenue": _money(stats["revenue"]),
            "profit": _money(stats["profit"]),
        }
        for store_id, stats in sorted(
            store_stats.items(), key=lambda item: item[1]["revenue"], reverse=True
        )
    ]
    repeat_customers = sum(1 for count in customers.values() if count > 1)
    return {
        "dataset": {
            "path": str(path),
            "transaction_count": len(rows),
            "customer_count": len(customers),
            "product_count": len(products),
            "category_count": len(categories),
            "store_count": len(stores),
            "date_min": min(row["transaction_date"] for row in rows),
            "date_max": max(row["transaction_date"] for row in rows),
        },
        "kpis": {
            "total_revenue": _money(revenue),
            "total_profit": _money(profit),
            "profit_margin_pct": _money(profit / revenue * Decimal("100")),
            "total_transactions": len(rows),
            "average_order_value": _money(revenue / Decimal(len(rows))),
            "units_sold": units,
            "average_revenue_per_customer": _money(revenue / Decimal(len(customers))),
            "repeat_customer_rate_pct": _money(
                Decimal(repeat_customers) / Decimal(len(customers)) * Decimal("100")
            ),
            "revenue_growth_pct": _money(growth),
            "top_product_contribution_pct": _money(
                top_product[1]["revenue"] / revenue * Decimal("100")
            ),
        },
        "category_performance": category_rows,
        "top_products": product_rows[:10],
        "store_performance": store_rows,
        "monthly_revenue": [
            {"month": month, "revenue": _money(monthly_revenue[month])} for month in ordered_months
        ],
        "customer_revenue_percentiles": {
            "top_customer_revenue": _money(max(customer_revenue.values())),
            "median_customer_revenue": _money(
                sorted(customer_revenue.values())[len(customer_revenue) // 2]
            ),
        },
    }


def write_metrics(path: Path, output_path: Path) -> None:
    """Calculate metrics and write stable JSON for documentation and review."""

    metrics = calculate_metrics(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
