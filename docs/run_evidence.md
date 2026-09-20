# Verified run evidence

This page records the sanitized evidence for the RetailIQ pipeline. It is safe
to keep in GitHub because it contains no passwords, connection tokens, Airflow
metadata database, or generated dbt catalog.

## Pipeline result

The last verified end-to-end run completed successfully through:

```text
start
  -> validate_source
  -> ingest_raw_data
  -> load_to_snowflake
  -> run_dbt_build
  -> run_reconciliation
  -> validate_analytics
  -> end
```

Airflow DAG: `retailiq_pipeline`

| Check | Verified result |
|---|---:|
| Source/fact transaction rows | 100,000 |
| Customers / products / stores | 2,000 / 27 / 8 |
| Revenue reconciliation | $33,129,143.92 |
| Profit / margin | $5,579,892.30 / 16.84% |
| dbt models built | 11 |
| dbt tests/checks passed | 50 tests; 61/61 total checks |
| Date range | 2024-01-01 to 2025-12-31 |

## What is stored in GitHub

- `dags/retailiq_pipeline.py`: Airflow orchestration and task graph.
- `docker-compose.yml` and `docker/airflow/`: reproducible local Airflow setup.
- `dbt/models/`: staging, intermediate, dimensions, facts, and analytics marts.
- `dbt/tests/` and model `schema.yml` files: data-quality contracts.
- `snowflake/`: database, stage, table, load, and validation SQL.
- `docs/sample_metrics.json` and `artifacts/sample_metrics.json`: sanitized
  verified metrics for reproducible demonstrations.
- `assets/dbt-dag.png`: captured dbt lineage graph showing source, models, marts,
  and quality assertions.
- `notebooks/`, `reports/`, and `streamlit_app.py`: presentation outputs.

## How to show the evidence locally

Start Airflow:

```powershell
docker compose up -d
```

Then open [Airflow](http://localhost:8080), sign in, and show the green
`retailiq_pipeline` graph.

Generate and serve dbt docs:

```powershell
docker compose exec -T airflow bash -lc "cd /opt/retailiq && dbt docs generate --project-dir /opt/retailiq/dbt --profiles-dir /opt/retailiq/docker/airflow"
docker compose exec -d airflow bash -lc "cd /opt/retailiq && dbt docs serve --project-dir /opt/retailiq/dbt --profiles-dir /opt/retailiq/docker/airflow --host 0.0.0.0 --port 8081"
```

Then open [dbt docs](http://localhost:8081) to show lineage, columns, and
test metadata.

Open the hosted dashboard at the [RetailIQ Streamlit app](https://retailiq-retail-data-platform-bv7cmxx76gmya93dhfzscx.streamlit.app/).

## What must never be committed

Keep `.env`, Snowflake passwords, Streamlit secrets, Airflow's local metadata
database, `dbt/target/`, and generated operational logs outside GitHub. The
repository `.gitignore` is configured for these files.
