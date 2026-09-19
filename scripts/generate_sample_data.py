#!/usr/bin/env python
"""Generate deterministic synthetic retail transactions."""

from __future__ import annotations

import argparse
from pathlib import Path

from retailiq.sample_data import write_transactions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("data/sample/retail_transactions.csv"))
    args = parser.parse_args()
    write_transactions(args.output, rows=args.rows, seed=args.seed)
    print(f"Generated {args.rows:,} synthetic transactions at {args.output} (seed={args.seed})")


if __name__ == "__main__":
    main()
