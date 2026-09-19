# Airflow orchestration

`dags/retailiq_pipeline.py` is deliberately thin. It coordinates the following
tasks and delegates business logic to reusable Python modules, Snowflake SQL, and
dbt:

`start` → `validate_source` → `ingest_raw_data` → `load_to_snowflake` →
`run_dbt_build` → `run_reconciliation` → `validate_analytics` → `end`

Configure an Airflow Connection named `retailiq_snowflake` for the Snowflake
account. `DBT_PROFILES_DIR` and `RETAILIQ_PROJECT_ROOT` are environment-based,
and no credentials are embedded in the DAG. Retries are two attempts with a
five-minute delay; `max_active_runs=1` prevents overlapping batch mutations.

