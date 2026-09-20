"""Build a sanitized RetailIQ evidence PDF for portfolio sharing."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "artifacts" / "sample_metrics.json"
OUTPUT = ROOT / "output" / "pdf" / "retailiq_evidence_report.pdf"

NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#1F6FEB")
TEAL = colors.HexColor("#0F766E")
LIGHT_BLUE = colors.HexColor("#EAF2FF")
LIGHT_TEAL = colors.HexColor("#E7F7F3")
LIGHT_GRAY = colors.HexColor("#F4F7FA")
MID_GRAY = colors.HexColor("#52606D")


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value:,.2f}%"


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def styled_table(data: list[list[str]], widths: list[float], header_color= NAVY) -> Table:
    header_style = ParagraphStyle(
        "TableHeaderCell",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=10,
        textColor=colors.white,
    )
    body_style = ParagraphStyle(
        "TableBodyCell",
        fontName="Helvetica",
        fontSize=8.5,
        leading=10,
        textColor=NAVY,
    )
    wrapped_data = [
        [
            cell if isinstance(cell, Paragraph) else Paragraph(str(cell), header_style if row_index == 0 else body_style)
            for cell in row
        ]
        for row_index, row in enumerate(data)
    ]
    table = Table(wrapped_data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), header_color),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8.5),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 8.5),
                ("TEXTCOLOR", (0, 1), (-1, -1), NAVY),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D9E2EC")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    width, height = letter
    if doc.page > 1:
        canvas.setStrokeColor(colors.HexColor("#D9E2EC"))
        canvas.line(doc.leftMargin, height - 0.48 * inch, width - doc.rightMargin, height - 0.48 * inch)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(NAVY)
        canvas.drawString(doc.leftMargin, height - 0.35 * inch, "RETAILIQ | EVIDENCE REPORT")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MID_GRAY)
    canvas.drawString(doc.leftMargin, 0.38 * inch, "Synthetic baseline | No credentials included")
    canvas.drawRightString(width - doc.rightMargin, 0.38 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build() -> None:
    metrics = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    dataset = metrics["dataset"]
    kpis = metrics["kpis"]

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=29,
        leading=34,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=8,
    )
    subtitle = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=MID_GRAY,
        alignment=TA_CENTER,
        spaceAfter=18,
    )
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=NAVY,
        spaceBefore=2,
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=TEAL,
        spaceBefore=8,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.7,
        leading=14,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=7,
    )
    small = ParagraphStyle(
        "Small",
        parent=body,
        fontSize=8.5,
        leading=11,
        textColor=MID_GRAY,
    )
    code = ParagraphStyle(
        "Code",
        parent=body,
        fontName="Courier",
        fontSize=8.5,
        leading=12,
        backColor=LIGHT_GRAY,
        borderColor=colors.HexColor("#D9E2EC"),
        borderWidth=0.5,
        borderPadding=7,
        spaceAfter=9,
    )

    story: list = []
    story.extend(
        [
            Spacer(1, 0.8 * inch),
            p("RetailIQ", title),
            p("Retail Data Platform & Revenue Analytics", subtitle),
            p("Portfolio evidence report", ParagraphStyle("CoverTag", parent=subtitle, fontSize=11, textColor=BLUE)),
            Spacer(1, 0.32 * inch),
            p(
                "An end-to-end demonstration of validated ingestion, Snowflake warehousing, "
                "dbt transformation, Airflow orchestration, and analytics delivery.",
                ParagraphStyle("CoverLead", parent=body, fontSize=13, leading=19, alignment=TA_CENTER),
            ),
            Spacer(1, 0.35 * inch),
        ]
    )

    cover_table = Table(
        [
            [p("TRANSACTIONS", small), p("REVENUE", small), p("PROFIT MARGIN", small)],
            [p(f"{dataset['transaction_count']:,}", h1), p(money(kpis["total_revenue"]), h1), p(pct(kpis["profit_margin_pct"]), h1)],
        ],
        colWidths=[2.05 * inch] * 3,
        hAlign="CENTER",
    )
    cover_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#B8D4FF")),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B8D4FF")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.append(cover_table)
    story.append(Spacer(1, 0.48 * inch))
    story.append(p(f"Verified baseline | Generated {date.today().isoformat()}", small))
    story.append(PageBreak())

    story.append(p("1. Executive summary", h1))
    story.append(
        p(
            "RetailIQ turns a synthetic retail transaction feed into a tested analytics layer. "
            "Python performs source validation, Snowflake stores the warehouse layers, dbt builds "
            "the dimensional model and marts, and Airflow coordinates the batch from validation "
            "through final reconciliation.",
            body,
        )
    )
    story.append(p("Verified business metrics", h2))
    summary_data = [
        ["Metric", "Verified value", "Metric", "Verified value"],
        ["Transactions", f"{dataset['transaction_count']:,}", "Customers", f"{dataset['customer_count']:,}"],
        ["Products / stores", f"{dataset['product_count']:,} / {dataset['store_count']:,}", "Units sold", f"{kpis['units_sold']:,}"],
        ["Revenue", money(kpis["total_revenue"]), "Profit", money(kpis["total_profit"])],
        ["Profit margin", pct(kpis["profit_margin_pct"]), "Average order value", money(kpis["average_order_value"])],
        ["Date range", f"{dataset['date_min']} to {dataset['date_max']}", "Revenue growth", pct(kpis["revenue_growth_pct"])],
    ]
    story.append(styled_table(summary_data, [1.45 * inch, 1.55 * inch, 1.6 * inch, 1.6 * inch]))

    story.append(p("Architecture", h2))
    architecture = [
        ["Source", "Validation", "Warehouse", "Transformation", "Delivery"],
        ["Retail CSV", "Python rules", "Snowflake RAW", "dbt STAGING -> INTERMEDIATE -> MARTS", "Streamlit / Power BI / HTML"],
    ]
    story.append(styled_table(architecture, [1.1 * inch, 1.1 * inch, 1.15 * inch, 2.0 * inch, 1.3 * inch], header_color=TEAL))
    story.append(p("Airflow is the orchestration layer across validation, loading, dbt, reconciliation, and analytics checks.", small))

    story.append(PageBreak())
    story.append(p("2. Airflow orchestration evidence", h1))
    story.append(p("DAG: retailiq_pipeline | Local UI: http://localhost:8080", body))
    airflow_data = [
        ["Order", "Task", "Purpose", "Status"],
        ["1", "start", "Begin the scheduled batch", "PASS"],
        ["2", "validate_source", "Check headers, types, formulas, dates, and identifiers", "PASS"],
        ["3", "ingest_raw_data", "Persist accepted, rejected, and batch-summary artifacts", "PASS"],
        ["4", "load_to_snowflake", "Run the reviewed stage-to-RAW MERGE", "PASS"],
        ["5", "run_dbt_build", "Build models and execute dbt tests", "PASS"],
        ["6", "run_reconciliation", "Compare raw and fact row counts and revenue", "PASS"],
        ["7", "validate_analytics", "Check fact-table formulas and positive quantities", "PASS"],
        ["8", "end", "Mark the pipeline complete", "PASS"],
    ]
    airflow_table = styled_table(airflow_data, [0.60 * inch, 1.35 * inch, 3.30 * inch, 0.75 * inch])
    airflow_table.setStyle(TableStyle([("TEXTCOLOR", (-1, 1), (-1, -1), TEAL), ("FONTNAME", (-1, 1), (-1, -1), "Helvetica-Bold")]))
    story.append(airflow_table)
    story.append(Spacer(1, 0.12 * inch))
    story.append(p("The DAG uses retries, a single active run, and warehouse-side reconciliation before success.", body))
    story.append(p("Show it locally", h2))
    story.append(p("docker compose up -d\nOpen http://localhost:8080 and select the green retailiq_pipeline graph.", code))

    story.append(p("3. dbt transformation and test evidence", h1))
    story.append(p("dbt docs UI: http://localhost:8081", body))
    dbt_data = [
        ["dbt area", "Contents", "Evidence"],
        ["Sources", "RAW transaction source", "Source contract documented"],
        ["Staging", "stg_transactions", "Type and freshness logic"],
        ["Intermediate", "int_transaction_enriched", "Reusable transaction grain"],
        ["Dimensions", "Customer, product, store, date", "Deterministic surrogate keys"],
        ["Fact", "fct_sales", "One row per transaction line"],
        ["Marts", "KPI, customer, product, store performance", "Analytics-ready outputs"],
        ["Tests", "Schema and singular SQL tests", "50 tests; 61/61 checks passed"],
    ]
    story.append(styled_table(dbt_data, [1.05 * inch, 2.35 * inch, 2.6 * inch], header_color=TEAL))
    story.append(Spacer(1, 0.12 * inch))
    story.append(p("Generate and serve the documentation from the Airflow container:", body))
    story.append(p("dbt docs generate --project-dir /opt/retailiq/dbt --profiles-dir /opt/retailiq/docker/airflow<br/>dbt docs serve --host 0.0.0.0 --port 8081", code))

    story.append(PageBreak())
    story.append(p("4. dbt lineage screenshot", h1))
    story.append(
        p(
            "This captured dbt graph shows the tested path from the raw transaction source through "
            "staging and intermediate enrichment into dimensions, the sales fact, analytics marts, "
            "and singular quality assertions.",
            body,
        )
    )
    dbt_image = ROOT / "tmp" / "pdfs" / "dbt-dag-cropped.png"
    story.append(Image(str(dbt_image), width=7.05 * inch, height=3.13 * inch, hAlign="CENTER"))
    story.append(Spacer(1, 0.16 * inch))
    lineage_data = [
        ["Layer", "Models or tests visible in the graph"],
        ["Source", "retailiq_raw_transactions"],
        ["Staging", "stg_transactions"],
        ["Intermediate", "int_transaction_enriched"],
        ["Dimensions", "dim_customer, dim_product, dim_date, dim_store"],
        ["Fact and marts", "fct_sales; mart_kpi_summary, mart_product_performance, mart_store_performance, mart_customer_performance"],
        ["Quality assertions", "assert_no_orphaned_fact_keys, assert_positive_quantity, assert_profit_reconciles"],
    ]
    story.append(styled_table(lineage_data, [1.35 * inch, 5.7 * inch], header_color=TEAL))

    story.append(PageBreak())
    story.append(p("5. Analytics and presentation outputs", h1))
    story.append(p("The same verified baseline is available through several presentation surfaces:", body))
    outputs = [
        ["Surface", "Access", "What it demonstrates"],
        ["Streamlit", "Hosted public dashboard", "Interactive KPI cards, charts, product, store, and customer views"],
        ["Airflow", "http://localhost:8080", "Successful orchestration and green task graph"],
        ["dbt docs", "http://localhost:8081", "Model lineage, columns, and test metadata"],
        ["Jupyter", "notebooks/retailiq_analysis.ipynb", "Narrated analysis with charts"],
        ["Static HTML", "reports/retailiq_report.html", "Portable report with no server dependency"],
        ["Power BI", "powerbi/", "Semantic model, relationships, and DAX handoff"],
    ]
    story.append(styled_table(outputs, [1.1 * inch, 1.75 * inch, 3.15 * inch]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(p("Hosted dashboard", h2))
    story.append(p("https://retailiq-retail-data-platform-bv7cmxx76gmya93dhfzscx.streamlit.app/", code))

    story.append(p("6. Security and reproducibility", h1))
    story.append(
        p(
            "The repository contains source code, SQL, model contracts, tests, sanitized metrics, "
            "and repeatable commands. It intentionally excludes .env files, passwords, Streamlit "
            "secrets, Airflow's metadata database, dbt/target runtime output, and operational logs.",
            body,
        )
    )
    security_data = [
        ["Item", "Repository treatment"],
        ["Synthetic data", "Safe baseline; 100,000 rows generated with seed 42"],
        ["Credentials", "Environment variables or hosting secret store only"],
        ["Airflow metadata", "Docker volume only; never committed"],
        ["dbt catalog and logs", "Generated locally when needed; ignored by Git"],
        ["Evidence", "Sanitized metrics and documented commands committed"],
    ]
    story.append(styled_table(security_data, [1.55 * inch, 4.45 * inch], header_color=TEAL))
    story.append(Spacer(1, 0.25 * inch))
    story.append(p("Repository reference", h2))
    story.append(p("https://github.com/HarishNamasivayamM/RetailIQ-retail-data-platform", code))
    story.append(p("This report is generated from the committed project snapshot and can be rebuilt with scripts/build_pdf_report.py.", small))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.62 * inch,
        title="RetailIQ Evidence Report",
        author="RetailIQ",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
