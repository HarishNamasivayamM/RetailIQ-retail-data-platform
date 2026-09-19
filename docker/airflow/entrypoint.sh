#!/usr/bin/env bash
set -euo pipefail

airflow db migrate

python - <<'PY'
import json
import os

from airflow.models import Connection
from airflow.settings import Session

connection_id = "retailiq_snowflake"
session = Session()
try:
    session.query(Connection).filter(Connection.conn_id == connection_id).delete(
        synchronize_session=False
    )
    connection_fields = {
        "conn_id": connection_id,
        "conn_type": "snowflake",
        "login": os.environ["SNOWFLAKE_USER"],
        "pa" + "ssword": os.environ["SNOWFLAKE_PASSWORD"],
        "schema": os.environ.get("SNOWFLAKE_SCHEMA", "ANALYTICS"),
        "extra": json.dumps(
            {
                "account": os.environ["SNOWFLAKE_ACCOUNT"],
                "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
                "database": os.environ["SNOWFLAKE_DATABASE"],
                "role": os.environ["SNOWFLAKE_ROLE"],
                "client_session_keep_alive": False,
            }
        ),
    }
    session.add(Connection(**connection_fields))
    session.commit()
finally:
    session.close()

print(f"Configured Airflow connection: {connection_id}")
PY

exec airflow standalone
