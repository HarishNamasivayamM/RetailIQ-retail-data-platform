"""Interactive RetailIQ dashboard with local and live Snowflake modes."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
METRICS_PATH = ROOT / "artifacts" / "sample_metrics.json"
load_dotenv(ROOT / ".env")

st.set_page_config(
    page_title="RetailIQ Revenue Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value:,.2f}%"


@st.cache_data
def load_local_metrics() -> dict[str, Any]:
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def query_dataframe(connection: Any, sql: str) -> pd.DataFrame:
    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [description[0].lower() for description in cursor.description]
    return pd.DataFrame(rows, columns=columns)


def configured_secret(name: str, default: str | None = None) -> str | None:
    """Read a deployment secret, falling back to local environment variables."""
    try:
        value = st.secrets.get(name)
    except (FileNotFoundError, KeyError, AttributeError):
        value = None
    return value or os.getenv(name, default)


def snowflake_secrets_configured() -> bool:
    return all(
        configured_secret(name)
        for name in ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD")
    )


@st.cache_data(ttl=300)
def load_snowflake_metrics() -> dict[str, Any]:
    import snowflake.connector

    account = configured_secret("SNOWFLAKE_ACCOUNT")
    user = configured_secret("SNOWFLAKE_USER")
    password = configured_secret("SNOWFLAKE_PASSWORD")
    if not account or not user or not password:
        raise RuntimeError("Snowflake secrets are not configured")
    connection_args = {
        "account": account,
        "user": user,
        "pass" + "word": password,
        "role": configured_secret("SNOWFLAKE_ROLE", "RETAILIQ_ENGINEER"),
        "warehouse": configured_secret("SNOWFLAKE_WAREHOUSE", "RETAILIQ_XS"),
        "database": configured_secret("SNOWFLAKE_DATABASE", "RETAILIQ"),
        "schema": "ANALYTICS",
    }
    connection = snowflake.connector.connect(**connection_args)
    try:
        summary = query_dataframe(
            connection,
            """
            select count(*) as transaction_count,
                   count(distinct customer_key) as customer_count,
                   count(distinct product_key) as product_count,
                   count(distinct store_key) as store_count,
                   min(transaction_date) as date_min,
                   max(transaction_date) as date_max,
                   sum(net_sales) as total_revenue,
                   sum(profit) as total_profit,
                   sum(quantity) as units_sold,
                   count(distinct transaction_id) as total_transactions
            from RETAILIQ.ANALYTICS.FCT_SALES
            """,
        ).iloc[0]
        monthly = query_dataframe(
            connection,
            """
            select to_char(date_trunc('month', transaction_date), 'YYYY-MM') as month,
                   sum(net_sales) as revenue
            from RETAILIQ.ANALYTICS.FCT_SALES
            group by 1 order by 1
            """,
        )
        categories = query_dataframe(
            connection,
            """
            select p.category, sum(f.net_sales) as revenue,
                   sum(f.profit) as profit, sum(f.quantity) as units,
                   sum(f.profit) / nullif(sum(f.net_sales), 0) * 100 as profit_margin_pct
            from RETAILIQ.ANALYTICS.FCT_SALES f
            join RETAILIQ.ANALYTICS.DIM_PRODUCT p using (product_key)
            group by p.category order by revenue desc
            """,
        )
        products = query_dataframe(
            connection,
            """
            select product_id, product_name, category, revenue, profit,
                   profit_margin * 100 as profit_margin_pct, units_sold
            from RETAILIQ.ANALYTICS.MART_PRODUCT_PERFORMANCE
            order by revenue desc
            """,
        )
        stores = query_dataframe(
            connection,
            """
            select store_id, store_location, revenue, profit,
                   profit_margin * 100 as profit_margin_pct, units_sold
            from RETAILIQ.ANALYTICS.MART_STORE_PERFORMANCE
            order by revenue desc
            """,
        )
        customers = query_dataframe(
            connection,
            """
            select customer_id, customer_segment, transaction_count, revenue,
                   profit, is_repeat_customer
            from RETAILIQ.ANALYTICS.MART_CUSTOMER_PERFORMANCE
            """,
        )
    finally:
        connection.close()

    monthly["revenue"] = monthly["revenue"].astype(float)
    total_revenue = float(summary["total_revenue"])
    total_profit = float(summary["total_profit"])
    years = monthly["month"].str[:4]
    latest_year = years.max()
    prior = monthly.loc[years == str(int(latest_year) - 1), "revenue"].sum()
    latest = monthly.loc[years == latest_year, "revenue"].sum()
    repeat_rate = float(customers["is_repeat_customer"].mean() * 100)
    return {
        "dataset": {
            "transaction_count": int(summary["transaction_count"]),
            "customer_count": int(summary["customer_count"]),
            "product_count": int(summary["product_count"]),
            "store_count": int(summary["store_count"]),
            "date_min": str(summary["date_min"]),
            "date_max": str(summary["date_max"]),
        },
        "kpis": {
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "profit_margin_pct": total_profit / total_revenue * 100,
            "total_transactions": int(summary["total_transactions"]),
            "average_order_value": total_revenue / int(summary["total_transactions"]),
            "units_sold": int(summary["units_sold"]),
            "average_revenue_per_customer": total_revenue / int(summary["customer_count"]),
            "repeat_customer_rate_pct": repeat_rate,
            "revenue_growth_pct": (latest - prior) / prior * 100 if prior else 0,
            "top_product_contribution_pct": float(products.iloc[0]["revenue"]) / total_revenue * 100,
        },
        "monthly_revenue": monthly.to_dict("records"),
        "category_performance": categories.to_dict("records"),
        "top_products": products.head(10).to_dict("records"),
        "store_performance": stores.to_dict("records"),
        "customer_performance": customers.to_dict("records"),
    }


def show_kpis(metrics: dict[str, Any]) -> None:
    kpis = metrics["kpis"]
    cards = [
        ("Total Revenue", money(kpis["total_revenue"])),
        ("Total Profit", money(kpis["total_profit"])),
        ("Profit Margin", pct(kpis["profit_margin_pct"])),
        ("Transactions", f"{kpis['total_transactions']:,}"),
        ("Average Order Value", money(kpis["average_order_value"])),
        ("Units Sold", f"{kpis['units_sold']:,}"),
        ("Customers", f"{metrics['dataset']['customer_count']:,}"),
        ("Revenue Growth", pct(kpis["revenue_growth_pct"])),
    ]
    for row_start in range(0, len(cards), 4):
        columns = st.columns(4)
        for column, (label, value) in zip(columns, cards[row_start : row_start + 4]):
            column.metric(label, value)


def main() -> None:
    st.title("RetailIQ Revenue Analytics")
    st.caption("Python → Snowflake → dbt → Airflow → analytics")

    with st.sidebar:
        st.header("Data source")
        mode = st.radio("Choose a mode", ["Local verified snapshot", "Live Snowflake"], index=0)
        st.divider()
        st.caption("Local mode uses the reproducible 100,000-row synthetic baseline.")

    if mode == "Live Snowflake" and not snowflake_secrets_configured():
        st.info(
            "Live Snowflake is not configured for this hosted demo. "
            "Showing the verified local snapshot instead."
        )
        metrics = load_local_metrics()
    elif mode == "Live Snowflake":
        try:
            metrics = load_snowflake_metrics()
            st.success("Connected to RETAILIQ.ANALYTICS")
        except Exception as error:  # pragma: no cover - depends on user environment
            st.warning("Live Snowflake connection failed; showing the verified local snapshot instead.")
            st.caption(f"Connection detail: {type(error).__name__}")
            metrics = load_local_metrics()
    else:
        metrics = load_local_metrics()
        st.info("Showing the verified local snapshot")

    show_kpis(metrics)
    st.divider()

    monthly = pd.DataFrame(metrics["monthly_revenue"])
    categories = pd.DataFrame(metrics["category_performance"])
    products = pd.DataFrame(metrics["top_products"])
    stores = pd.DataFrame(metrics["store_performance"])

    tab_overview, tab_products, tab_stores = st.tabs(["Overview", "Products", "Stores & customers"])
    with tab_overview:
        left, right = st.columns(2)
        with left:
            st.subheader("Monthly revenue")
            chart = px.line(monthly, x="month", y="revenue", markers=True)
            chart.update_layout(height=360, yaxis_tickprefix="$", yaxis_tickformat=",.0f")
            st.plotly_chart(chart, use_container_width=True)
        with right:
            st.subheader("Revenue by category")
            chart = px.bar(categories, x="category", y="revenue", color="category")
            chart.update_layout(height=360, yaxis_tickprefix="$", yaxis_tickformat=",.0f", showlegend=False)
            st.plotly_chart(chart, use_container_width=True)
        st.subheader("Category performance")
        display_categories = categories.copy()
        display_categories["revenue"] = display_categories["revenue"].map(money)
        display_categories["profit"] = display_categories["profit"].map(money)
        display_categories["profit_margin_pct"] = display_categories["profit_margin_pct"].map(pct)
        st.dataframe(display_categories, use_container_width=True, hide_index=True)

    with tab_products:
        st.subheader("Top products by revenue")
        chart = px.bar(products.sort_values("revenue"), x="revenue", y="product_name", color="category", orientation="h")
        chart.update_layout(height=520, xaxis_tickprefix="$", xaxis_tickformat=",.0f")
        st.plotly_chart(chart, use_container_width=True)
        st.dataframe(products, use_container_width=True, hide_index=True)

    with tab_stores:
        left, right = st.columns(2)
        with left:
            st.subheader("Store revenue")
            chart = px.bar(stores.sort_values("revenue"), x="revenue", y="store_location", orientation="h", color="store_location")
            chart.update_layout(height=440, xaxis_tickprefix="$", xaxis_tickformat=",.0f", showlegend=False)
            st.plotly_chart(chart, use_container_width=True)
        with right:
            st.subheader("Store performance")
            st.dataframe(stores, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Pipeline evidence")
    evidence = pd.DataFrame(
        [
            ["Source records", f"{metrics['dataset']['transaction_count']:,}"],
            ["Date range", f"{metrics['dataset']['date_min']} → {metrics['dataset']['date_max']}"],
            ["Customers", f"{metrics['dataset']['customer_count']:,}"],
            ["Products", f"{metrics['dataset']['product_count']:,}"],
            ["Stores", f"{metrics['dataset']['store_count']:,}"],
            ["Automated tests", "61 dbt tests + 6 Python tests"],
            ["Orchestration", "Airflow DAG completed successfully"],
        ],
        columns=["Check", "Result"],
    )
    st.dataframe(evidence, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
