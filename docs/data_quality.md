# Data quality strategy

| Check | Where | Failure behavior |
|---|---|---|
| Required headers and schema drift | Python `schema.py` | Fail closed before load; missing, unexpected, or duplicate normalized headers are reported. |
| Missing identifiers | Python `rules.py`, dbt not-null tests | Row is written to the reject artifact; Airflow fails the batch. |
| Duplicate transaction IDs | Python, Snowflake validation, dbt unique tests | Batch fails; Snowflake `MERGE` remains idempotent for safe reruns. |
| Positive quantities and valid numeric ranges | Python and singular dbt tests | Batch/model test fails; no silent correction. |
| Revenue/profit reconciliation | Python, Snowflake SQL, dbt singular test | Batch fails with the offending IDs. |
| Dimension referential integrity | dbt relationships tests and Airflow final query | Build fails on orphaned fact keys. |
| Freshness | dbt source freshness | Warning after 24 hours, error after 72 hours. |
| Raw/fact reconciliation | Airflow `run_reconciliation` | Counts and revenue must match within one cent. |

The local ingestion writes `validated_transactions.csv`,
`rejected_transactions.csv`, and a JSON summary. Rejected records are not
silently discarded. In production, those artifacts would be retained in an
audit location with alerting and a replay workflow.
