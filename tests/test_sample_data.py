import csv

from retailiq.sample_data import generate_transactions, write_transactions
from retailiq.validation.schema import EXPECTED_COLUMNS


def test_sample_generation_is_deterministic():
    first = list(generate_transactions(rows=3, seed=42))
    second = list(generate_transactions(rows=3, seed=42))
    assert first == second
    assert list(first[0]) == list(EXPECTED_COLUMNS)


def test_sample_writer_creates_requested_row_count(tmp_path):
    path = tmp_path / "transactions.csv"
    write_transactions(path, rows=10, seed=7)
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 10
    assert len({row["transaction_id"] for row in rows}) == 10
