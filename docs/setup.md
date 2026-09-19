# Setup and execution

## Minimum local demonstration

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/generate_sample_data.py --rows 100000 --seed 42
python scripts/run_ingestion.py --fail-on-rejects
pytest
```

The generator is deterministic and synthetic. Generated CSVs are ignored by
Git. The local pipeline does not require Snowflake, Airflow, or Power BI.

## Snowflake and dbt

1. Copy `.env.example` to `.env` and set real values locally.
2. Execute the Snowflake setup scripts in order and upload the source CSV to the
   documented stage.
3. Copy `dbt/profiles.yml.example` to a private dbt profiles directory and set
   the environment variables.
4. Install `requirements-dbt.txt` alongside `requirements.txt`.
5. Run `dbt debug`, `dbt build`, and `dbt docs generate` from the `dbt/` project.

## Airflow

Install Airflow using its official version-specific constraints, install the
Snowflake provider, add a connection named `retailiq_snowflake`, and expose the
repository at the path configured by `RETAILIQ_PROJECT_ROOT`. The DAG is
`dags/retailiq_pipeline.py`.

## Power BI

Use `powerbi/semantic_model.md` and `powerbi/measures.md` to build the report in
Power BI Desktop. A `.pbix` is intentionally not generated outside Power BI.

