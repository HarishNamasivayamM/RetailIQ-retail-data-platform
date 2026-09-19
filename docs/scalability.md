# Scalability and production evolution

| Scale | Practical evolution |
|---|---|
| 100K | X-Small warehouse, table materializations, local synthetic demo, no clustering. |
| 1M | Keep incremental `MERGE`, stage files in partitions, increase dbt threads/warehouse only when measured. |
| 10M | Partition upstream files by event date, monitor Snowflake query history, consider clustering only for proven selective access paths. |
| 100M+ | Use cloud object storage plus Snowpipe/managed ingestion, workload-specific warehouses, stronger observability, backfills, and modeled aggregates. |

The current design uses `loaded_at` with a two-day lookback for late-arriving
records and `transaction_id` merge semantics for corrections. A production
implementation should retain batch manifests, quarantine bad files, record
watermark state, and use an explicit replay/backfill runbook. Clustering is
intentionally not used at 100K rows because it would add maintenance without a
measured benefit.

