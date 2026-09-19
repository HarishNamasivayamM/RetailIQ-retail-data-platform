"""Environment-driven configuration for local runs and orchestration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    """Paths and identifiers used by the local ingestion stage."""

    source_path: Path = Path("data/sample/retail_transactions.csv")
    processed_path: Path = Path("data/processed/validated_transactions.csv")
    rejects_path: Path = Path("data/processed/rejected_transactions.csv")
    report_path: Path = Path("artifacts/sample_metrics.json")
    batch_id: str = "local-demo"

    @classmethod
    def from_env(cls) -> "PipelineConfig":
        """Build configuration from environment variables with portable defaults."""

        return cls(
            source_path=Path(os.getenv("RETAILIQ_SOURCE_PATH", str(cls.source_path))),
            processed_path=Path(os.getenv("RETAILIQ_PROCESSED_PATH", str(cls.processed_path))),
            rejects_path=Path(os.getenv("RETAILIQ_REJECTS_PATH", str(cls.rejects_path))),
            report_path=Path(os.getenv("RETAILIQ_REPORT_PATH", str(cls.report_path))),
            batch_id=os.getenv("RETAILIQ_BATCH_ID", cls.batch_id),
        )

    def ensure_output_directories(self) -> None:
        """Create only the configured output directories."""

        for path in (self.processed_path, self.rejects_path, self.report_path):
            path.parent.mkdir(parents=True, exist_ok=True)
