"""Schema normalization and validation for retail transaction files."""

from __future__ import annotations

import re
from collections.abc import Iterable

EXPECTED_COLUMNS = (
    "transaction_id",
    "transaction_date",
    "customer_id",
    "product_id",
    "product_name",
    "category",
    "subcategory",
    "quantity",
    "unit_price",
    "discount",
    "sales_amount",
    "cost",
    "profit",
    "store_id",
    "store_location",
    "payment_method",
    "customer_segment",
)


class SchemaValidationError(ValueError):
    """Raised when a source file cannot be safely interpreted."""


def normalize_column_name(name: str) -> str:
    """Convert source headers to predictable snake_case names."""

    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower()).strip("_")
    return normalized


def normalize_headers(headers: Iterable[str | None]) -> list[str]:
    """Normalize headers and reject duplicates created by normalization."""

    normalized = [normalize_column_name(header or "") for header in headers]
    duplicates = sorted({name for name in normalized if normalized.count(name) > 1})
    if duplicates:
        raise SchemaValidationError(f"Duplicate columns after normalization: {duplicates}")
    return normalized


def validate_headers(headers: Iterable[str | None]) -> list[str]:
    """Return normalized headers when all required source fields are present."""

    normalized = normalize_headers(headers)
    missing = sorted(set(EXPECTED_COLUMNS) - set(normalized))
    if missing:
        raise SchemaValidationError(f"Missing required columns: {missing}")
    unexpected = sorted(set(normalized) - set(EXPECTED_COLUMNS))
    if unexpected:
        raise SchemaValidationError(f"Unexpected columns; review the source contract: {unexpected}")
    return normalized
