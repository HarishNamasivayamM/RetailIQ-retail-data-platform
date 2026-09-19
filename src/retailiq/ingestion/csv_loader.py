"""CSV ingestion and durable validation outputs."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any

from retailiq.validation.rules import validate_rows
from retailiq.validation.schema import EXPECTED_COLUMNS, validate_headers

LOGGER = logging.getLogger(__name__)


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read and normalize a CSV source, failing closed on schema drift."""

    if not path.exists():
        raise FileNotFoundError(f"Source file does not exist: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        source_headers = reader.fieldnames or []
        headers = validate_headers(source_headers)
        header_map = dict(zip(source_headers, headers))
        rows: list[dict[str, str]] = []
        for source_row in reader:
            rows.append(
                {
                    normalized: (source_row.get(source) or "")
                    for source, normalized in header_map.items()
                    if normalized in EXPECTED_COLUMNS
                }
            )
    return rows


def _write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def ingest_csv(
    source_path: Path,
    processed_path: Path,
    rejects_path: Path,
    report_path: Path,
    batch_id: str,
) -> dict[str, Any]:
    """Validate a source file and write accepted, rejected, and summary artifacts."""

    rows = read_csv(source_path)
    accepted, rejected, summary = validate_rows(rows)
    for row in accepted:
        row["ingestion_batch_id"] = batch_id
        row["source_file_name"] = source_path.name
    summary.update({"batch_id": batch_id, "source_file": str(source_path)})
    _write_csv(
        processed_path,
        accepted,
        list(EXPECTED_COLUMNS) + ["ingestion_batch_id", "source_file_name", "_source_row_number"],
    )
    _write_csv(
        rejects_path,
        rejected,
        list(EXPECTED_COLUMNS) + ["_source_row_number", "_validation_errors"],
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    LOGGER.info(
        "Validated %s: %s accepted, %s rejected",
        source_path,
        summary["accepted_rows"],
        summary["rejected_rows"],
    )
    return summary
