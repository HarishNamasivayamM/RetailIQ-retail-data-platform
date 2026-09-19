# RetailIQ demonstration guide

RetailIQ can be demonstrated without Power BI. The options below are designed
for a portfolio walkthrough, interview, or local review.

## 1. Streamlit dashboard

Install the optional demo dependencies:

```powershell
python -m pip install -r requirements-demo.txt
```

Start the interactive dashboard:

```powershell
streamlit run streamlit_app.py
```

The default local mode uses the verified `artifacts/sample_metrics.json`
snapshot. The sidebar also has a Live Snowflake mode that reads the existing
private `.env` connection values without displaying the password.

## 2. Airflow orchestration

Start the already-configured local Airflow service:

```powershell
docker compose up -d
```

Open [http://localhost:8080](http://localhost:8080), select `retailiq_pipeline`,
and show the green task graph. The verified run includes source validation,
Python ingestion, Snowflake loading, dbt build, reconciliation, and analytics
validation.

## 3. dbt lineage and test documentation

Generate dbt's documentation inside the running Airflow container:

```powershell
docker compose exec -T airflow bash -lc "cd /opt/retailiq && dbt docs generate --project-dir /opt/retailiq/dbt --profiles-dir /opt/retailiq/docker/airflow"
```

Serve it on port 8081:

```powershell
docker compose exec -d airflow bash -lc "cd /opt/retailiq && dbt docs serve --project-dir /opt/retailiq/dbt --profiles-dir /opt/retailiq/docker/airflow --host 0.0.0.0 --port 8081"
```

Open [http://localhost:8081](http://localhost:8081) to show model lineage,
sources, columns, and test coverage.

## 4. Jupyter analysis notebook

Install the demo dependencies, then run:

```powershell
jupyter lab notebooks/retailiq_analysis.ipynb
```

The notebook reproduces the headline KPIs and renders category, monthly,
product, and store charts from the same verified snapshot.

## 5. Static HTML report

Build the shareable report:

```powershell
python scripts/build_static_report.py
```

Open [`reports/retailiq_report.html`](../reports/retailiq_report.html) in any
browser. It has no server dependency and can be attached to a portfolio or
opened from a local folder.

## 6. GitHub/README walkthrough

The root README is the narrative handoff: architecture, verified metrics,
quality controls, model design, insights, setup, and links to each demo. A
strong walkthrough order is:

1. Show the architecture and data-quality contract in the README.
2. Open Airflow and show the successful DAG graph.
3. Open dbt docs and show lineage plus tests.
4. Open Streamlit for interactive KPIs and charts.
5. Open the static HTML report for a portable artifact.
6. Finish with the notebook to explain the analysis choices.
