"""Airflow orchestration for the RetailIQ batch pipeline.

Business logic stays in ``src``/dbt. This DAG coordinates validation, raw loading,
dbt, and warehouse-side reconciliation through an Airflow Connection.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.operators.bash import BashOperator

from retailiq.config import PipelineConfig
from retailiq.ingestion.csv_loader import ingest_csv, read_csv
from retailiq.validation.rules import validate_rows

SNOWFLAKE_CONN_ID = "retailiq_snowflake"
PROJECT_ROOT = Path(os.getenv("RETAILIQ_PROJECT_ROOT", str(Path(__file__).resolve().parents[1])))


def validate_source(**context) -> None:
    """Run fail-fast source checks before writing a processed batch."""

    config = PipelineConfig.from_env()
    rows = read_csv(config.source_path)
    _, rejected, summary = validate_rows(rows)
    context["ti"].xcom_push(key="source_summary", value=summary)
    # Row-level rejects are persisted by the next task so the batch has an
    # auditable reject artifact before the run is marked failed.
    if rejected:
        context["ti"].log.warning("Source contains %s rows that will be quarantined", len(rejected))


def ingest_raw_data(**context) -> None:
    """Persist accepted/rejected validation artifacts for the batch."""

    config = PipelineConfig.from_env()
    batch_id = context["run_id"]
    summary = ingest_csv(
        config.source_path,
        config.processed_path,
        config.rejects_path,
        config.report_path,
        batch_id,
    )
    context["ti"].xcom_push(key="ingestion_summary", value=summary)
    if summary["rejected_rows"]:
        raise AirflowFailException(f"Ingestion rejected rows; see {config.rejects_path}")


def load_to_snowflake(**context) -> None:
    """Execute the reviewed MERGE load using the configured Airflow connection."""

    sql_path = PROJECT_ROOT / "snowflake" / "loading" / "load_transactions.sql"
    sql = sql_path.read_text(encoding="utf-8")
    batch_id = context["run_id"].replace("'", "''")
    stage_path = os.getenv("SNOWFLAKE_STAGE_PATH", "RETAILIQ.RAW.RETAILIQ_STAGE")
    sql = sql.replace("replace-with-airflow-batch-id", batch_id)
    sql = sql.replace("__RETAILIQ_STAGE_PATH__", stage_path)
    SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID).run(
        sql, autocommit=True, split_statements=True
    )


def reconcile_warehouse(**_context) -> None:
    """Reconcile raw and modeled counts/revenue; fail on unexplained loss."""

    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    query = """
        select
            (select count(*) from RETAILIQ.RAW.TRANSACTIONS) as raw_rows,
            (select count(*) from RETAILIQ.ANALYTICS.FCT_SALES) as fact_rows,
            (select coalesce(sum(sales_amount), 0) from RETAILIQ.RAW.TRANSACTIONS) as raw_revenue,
            (select coalesce(sum(net_sales), 0) from RETAILIQ.ANALYTICS.FCT_SALES) as fact_revenue
    """
    raw_rows, fact_rows, raw_revenue, fact_revenue = hook.get_first(query)
    if raw_rows != fact_rows or abs(float(raw_revenue) - float(fact_revenue)) > 0.01:
        raise AirflowFailException(
            f"Reconciliation failed: raw_rows={raw_rows}, fact_rows={fact_rows}, "
            f"raw_revenue={raw_revenue}, fact_revenue={fact_revenue}"
        )


def validate_analytics(**_context) -> None:
    """Run final semantic checks against the fact table."""

    hook = SnowflakeHook(snowflake_conn_id=SNOWFLAKE_CONN_ID)
    invalid_rows = hook.get_first(
        """
        select count(*)
        from RETAILIQ.ANALYTICS.FCT_SALES
        where quantity <= 0 or net_sales < 0 or abs(profit - (net_sales - cost)) > 0.01
        """
    )[0]
    if invalid_rows:
        raise AirflowFailException(f"Analytics validation found {invalid_rows} invalid fact rows")


with DAG(
    dag_id="retailiq_pipeline",
    description="RetailIQ source validation, Snowflake load, dbt build, and reconciliation",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "retailiq", "retries": 2, "retry_delay": timedelta(minutes=5)},
    tags=["retailiq", "elt", "snowflake", "dbt"],
) as dag:
    start = EmptyOperator(task_id="start")
    validate = PythonOperator(task_id="validate_source", python_callable=validate_source)
    ingest = PythonOperator(task_id="ingest_raw_data", python_callable=ingest_raw_data)
    load = PythonOperator(task_id="load_to_snowflake", python_callable=load_to_snowflake)
    dbt_build = BashOperator(
        task_id="run_dbt_build",
        bash_command="dbt build --project-dir ${RETAILIQ_PROJECT_ROOT}/dbt --profiles-dir ${DBT_PROFILES_DIR}",
        env={
            "RETAILIQ_PROJECT_ROOT": str(PROJECT_ROOT),
            "DBT_PROFILES_DIR": os.getenv("DBT_PROFILES_DIR", ".dbt"),
        },
        append_env=True,
    )
    reconcile = PythonOperator(task_id="run_reconciliation", python_callable=reconcile_warehouse)
    validate_marts = PythonOperator(
        task_id="validate_analytics", python_callable=validate_analytics
    )
    end = EmptyOperator(task_id="end")

    start >> validate >> ingest >> load >> dbt_build >> reconcile >> validate_marts >> end
