#!/usr/bin/env python
"""Validate a source file and write accepted/rejected local artifacts."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from retailiq.config import PipelineConfig
from retailiq.ingestion.csv_loader import ingest_csv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source")
    parser.add_argument("--processed")
    parser.add_argument("--rejects")
    parser.add_argument("--report")
    parser.add_argument("--batch-id")
    parser.add_argument("--fail-on-rejects", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    defaults = PipelineConfig.from_env()
    config = PipelineConfig(
        source_path=defaults.source_path if not args.source else Path(args.source),
        processed_path=defaults.processed_path if not args.processed else Path(args.processed),
        rejects_path=defaults.rejects_path if not args.rejects else Path(args.rejects),
        report_path=defaults.report_path if not args.report else Path(args.report),
        batch_id=args.batch_id or defaults.batch_id,
    )
    config.ensure_output_directories()
    summary = ingest_csv(
        config.source_path,
        config.processed_path,
        config.rejects_path,
        config.report_path,
        config.batch_id,
    )
    if args.fail_on_rejects and summary["rejected_rows"]:
        raise SystemExit(f"Rejected rows found: {summary['rejected_rows']}")


if __name__ == "__main__":
    main()
