from retailiq.validation.rules import validate_rows
from retailiq.validation.schema import SchemaValidationError, validate_headers


def _row(**overrides):
    row = {
        "transaction_id": "TXN-1",
        "transaction_date": "2025-01-01",
        "customer_id": "C001",
        "product_id": "P001",
        "product_name": "Laptop",
        "category": "Electronics",
        "subcategory": "Computers",
        "quantity": "2",
        "unit_price": "100.00",
        "discount": "0.10",
        "sales_amount": "180.00",
        "cost": "120.00",
        "profit": "60.00",
        "store_id": "S001",
        "store_location": "Chicago",
        "payment_method": "Credit Card",
        "customer_segment": "Regular",
    }
    row.update(overrides)
    return row


def test_valid_row_is_accepted():
    accepted, rejected, summary = validate_rows([_row()])
    assert len(accepted) == 1
    assert rejected == []
    assert summary["accepted_rows"] == 1


def test_duplicate_and_invalid_values_are_rejected():
    accepted, rejected, summary = validate_rows([_row(), _row(quantity="0")])
    assert accepted == []
    assert len(rejected) == 2
    assert "duplicate_transaction_id" in rejected[0]["_validation_errors"]
    assert summary["rejected_non_positive_quantity"] == 1


def test_schema_normalization_and_missing_field_detection():
    headers = validate_headers(
        ["Transaction ID", "transaction_date"]
        + [field for field in _row() if field not in {"transaction_id", "transaction_date"}]
    )
    assert headers[0] == "transaction_id"
    try:
        validate_headers(["transaction_id"])
    except SchemaValidationError as exc:
        assert "Missing required columns" in str(exc)
    else:
        raise AssertionError("Expected schema validation to fail")

    try:
        validate_headers(list(_row()) + ["new_source_field"])
    except SchemaValidationError as exc:
        assert "Unexpected columns" in str(exc)
    else:
        raise AssertionError("Expected additive schema drift to fail")
