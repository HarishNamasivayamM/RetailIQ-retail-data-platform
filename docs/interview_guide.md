# Interview guide

### Why Snowflake?

Snowflake provides separated storage/compute, SQL-first ELT, secure stages, and
elastic warehouses. This project keeps the raw source and analytics layers
separate so compute can scale independently.

### Why dbt?

dbt makes SQL transformations modular, dependency-aware, documented, tested,
and reviewable. Python validates files; dbt owns warehouse business logic.

### Why Airflow?

Airflow expresses dependencies, retries, schedules, backfills, and operational
ownership. The DAG coordinates reusable code instead of becoming a monolith.

### Why dimensional modeling?

The star schema gives BI users predictable filter paths and makes measures clear:
`fct_sales` is the transaction-line fact, with customer, product, date, and store
dimensions.

### Why separate RAW, STAGING, INTERMEDIATE, and MARTS?

RAW preserves evidence, STAGING standardizes types, INTERMEDIATE centralizes
reusable calculations, and MARTS publish stable business-facing grains.

### What is the grain and how are keys handled?

`fct_sales` is one row per retail transaction line. Natural IDs remain for
traceability; deterministic MD5 surrogate keys support dimensional relationships.

### How are SCDs handled?

Customer, product, and store are Type 1 because the reference source contains a
current embedded snapshot and no effective-dated history. If historical segment,
catalog, or location reporting becomes a requirement, introduce dbt snapshots
with `valid_from`, `valid_to`, and `is_current`, then resolve the fact key using
the transaction date.

### How do incremental processing and idempotency work?

RAW uses a landing table and `MERGE` on `transaction_id`. dbt staging and the fact
model are incremental with `unique_key=transaction_id`, a `loaded_at` watermark,
and a two-day lookback for late arrivals. Replaying a batch updates the same
business key rather than creating duplicates.

### How are late data and schema changes handled?

The lookback reprocesses recent arrival windows; corrections merge by business
key. Python fails on missing or normalized-duplicate headers, and dbt uses
`on_schema_change='fail'` so new or changed columns cannot silently alter metrics.

### How is quality and reconciliation handled?

Python records accepted/rejected rows. dbt tests uniqueness, nullability,
relationships, and profit rules. Airflow compares RAW and fact row counts and
revenue, while Snowflake SQL checks duplicates and amount formulas.

### How would this scale and be productionized?

Move files to object storage, use managed ingestion, separate warehouses by
workload, add batch manifests and alerting, retain rejected files, add CI/CD and
lineage observability, and tune incremental partitions from query history.

