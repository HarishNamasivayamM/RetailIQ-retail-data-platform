#!/usr/bin/env python
"""Run cheap repository contract checks that do not require cloud credentials."""

from __future__ import annotations

from pathlib import Path


REQUIRED_FILES = (
    "README.md",
    ".env.example",
    "src/retailiq/ingestion/csv_loader.py",
    "src/retailiq/validation/rules.py",
    "dags/retailiq_pipeline.py",
    "dbt/dbt_project.yml",
    "dbt/models/sources.yml",
    "dbt/models/marts/facts/fct_sales.sql",
    "snowflake/tables/raw_transactions.sql",
    "powerbi/measures.md",
    "docs/architecture.md",
    "docs/data_quality.md",
    "docs/kpi_dictionary.md",
)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    missing = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise SystemExit(f"Missing required project files: {missing}")
    forbidden = ("C:" + "\\Users\\", "D:" + "\\", "/Users/", "password" + "=", "api_key" + "=")
    ignored_parts = {
        ".git",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "retailiq.egg-info",
        ".venv",
        "target",
        "logs",
        "artifacts",
        "data",
    }
    scanned = [
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.resolve() != Path(__file__).resolve()
        and not ignored_parts.intersection(path.parts)
    ]
    violations = []
    for path in scanned:
        if path.suffix.lower() in {".csv", ".parquet", ".pbix"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(token in text for token in forbidden):
            violations.append(str(path.relative_to(root)))
    if violations:
        raise SystemExit(f"Possible machine-specific paths or secrets found in: {violations}")
    print(f"Project contract checks passed ({len(REQUIRED_FILES)} required files present)")


if __name__ == "__main__":
    main()
