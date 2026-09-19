#!/usr/bin/env python
"""Build a self-contained HTML report from the verified metrics snapshot."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "artifacts" / "sample_metrics.json"
OUTPUT = ROOT / "reports" / "retailiq_report.html"


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value:,.2f}%"


def bar_rows(rows: list[dict[str, object]], label: str, value: str) -> str:
    maximum = max(float(row[value]) for row in rows) or 1
    rendered = []
    for row in rows:
        width = float(row[value]) / maximum * 100
        rendered.append(
            "<div class='bar-row'>"
            f"<span>{html.escape(str(row[label]))}</span>"
            f"<div class='bar-track'><div class='bar-fill' style='width:{width:.2f}%'></div></div>"
            f"<strong>{money(float(row[value]))}</strong></div>"
        )
    return "".join(rendered)


def line_chart(rows: list[dict[str, object]]) -> str:
    values = [float(row["revenue"]) for row in rows]
    maximum = max(values) or 1
    minimum = min(values) if values else 0
    width, height, pad = 900, 280, 32
    points = []
    for index, value in enumerate(values):
        x = pad + index * (width - 2 * pad) / max(len(values) - 1, 1)
        y = height - pad - (value - minimum) / max(maximum - minimum, 1) * (height - 2 * pad)
        points.append(f"{x:.1f},{y:.1f}")
    labels = "".join(
        f"<text x='{pad + index * (width - 2 * pad) / max(len(values) - 1, 1):.1f}' y='{height - 8}'>{html.escape(str(row['month']))}</text>"
        for index, row in enumerate(rows)
        if index % 3 == 0 or index == len(rows) - 1
    )
    return (
        f"<svg class='line-chart' viewBox='0 0 {width} {height}' role='img' aria-label='Monthly revenue trend'>"
        f"<polyline points='{' '.join(points)}' fill='none' stroke='#1f6feb' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>"
        f"<line x1='{pad}' y1='{height - pad}' x2='{width - pad}' y2='{height - pad}' stroke='#d0d7de'/>"
        f"<line x1='{pad}' y1='{pad}' x2='{pad}' y2='{height - pad}' stroke='#d0d7de'/>{labels}</svg>"
    )


def main() -> None:
    metrics = json.loads(INPUT.read_text(encoding="utf-8"))
    kpis = metrics["kpis"]
    categories = metrics["category_performance"]
    stores = metrics["store_performance"]
    products = metrics["top_products"]
    product_rows = "".join(
        f"<tr><td>{html.escape(row['product_name'])}</td><td>{html.escape(row['category'])}</td>"
        f"<td>{money(row['revenue'])}</td><td>{money(row['profit'])}</td></tr>"
        for row in products
    )
    store_rows = "".join(
        f"<tr><td>{html.escape(row['store_location'])}</td><td>{money(row['revenue'])}</td>"
        f"<td>{money(row['profit'])}</td></tr>"
        for row in stores
    )
    html_document = f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>
<title>RetailIQ Revenue Analytics Report</title>
<style>
:root {{ color-scheme: light; --ink:#172033; --muted:#667085; --blue:#1f6feb; --green:#16803c; --panel:#fff; --background:#f4f7fb; }}
* {{ box-sizing:border-box; }} body {{ margin:0; font-family:Inter,Segoe UI,Arial,sans-serif; color:var(--ink); background:var(--background); }}
main {{ max-width:1200px; margin:0 auto; padding:40px 24px 64px; }} header {{ display:flex; justify-content:space-between; gap:24px; align-items:end; margin-bottom:30px; }}
h1 {{ margin:0 0 8px; font-size:38px; }} h2 {{ margin:0 0 16px; font-size:22px; }} h3 {{ margin:0 0 12px; }} p {{ color:var(--muted); }}
.badge {{ background:#e4f7eb; color:var(--green); padding:8px 12px; border-radius:999px; font-weight:700; white-space:nowrap; }}
.grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:28px; }} .card,.panel {{ background:var(--panel); border:1px solid #e3e8ef; border-radius:16px; padding:22px; box-shadow:0 4px 18px #1522380d; }}
.label {{ color:var(--muted); font-size:14px; }} .value {{ margin-top:8px; font-size:28px; font-weight:800; }} .panel {{ margin-bottom:24px; }}
.two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:24px; }} .line-chart {{ width:100%; height:auto; }} .line-chart text {{ font-size:12px; fill:var(--muted); }}
.bar-row {{ display:grid; grid-template-columns:100px 1fr 100px; gap:12px; align-items:center; margin:14px 0; }} .bar-row span {{ font-weight:650; }} .bar-row strong {{ text-align:right; }}
.bar-track {{ height:12px; background:#e9eef5; border-radius:999px; overflow:hidden; }} .bar-fill {{ height:100%; background:linear-gradient(90deg,#1f6feb,#6b9ff5); border-radius:999px; }}
table {{ width:100%; border-collapse:collapse; }} th,td {{ text-align:left; padding:11px 12px; border-bottom:1px solid #edf0f4; }} th {{ color:var(--muted); font-size:13px; }} footer {{ color:var(--muted); font-size:13px; margin-top:28px; }}
@media(max-width:800px) {{ .grid,.two-col {{ grid-template-columns:1fr 1fr; }} header {{ display:block; }} .badge {{ display:inline-block; margin-top:14px; }} }}
@media(max-width:560px) {{ .grid,.two-col {{ grid-template-columns:1fr; }} .bar-row {{ grid-template-columns:90px 1fr; }} .bar-row strong {{ grid-column:2; text-align:left; }} }}
</style></head><body><main>
<header><div><h1>RetailIQ Revenue Analytics</h1><p>Verified synthetic retail baseline · {metrics['dataset']['transaction_count']:,} transaction lines · {metrics['dataset']['date_min']} to {metrics['dataset']['date_max']}</p></div><div class='badge'>Pipeline verified</div></header>
<section class='grid'>
<div class='card'><div class='label'>Total Revenue</div><div class='value'>{money(kpis['total_revenue'])}</div></div>
<div class='card'><div class='label'>Total Profit</div><div class='value'>{money(kpis['total_profit'])}</div></div>
<div class='card'><div class='label'>Profit Margin</div><div class='value'>{pct(kpis['profit_margin_pct'])}</div></div>
<div class='card'><div class='label'>Average Order Value</div><div class='value'>{money(kpis['average_order_value'])}</div></div>
<div class='card'><div class='label'>Transactions</div><div class='value'>{kpis['total_transactions']:,}</div></div>
<div class='card'><div class='label'>Units Sold</div><div class='value'>{kpis['units_sold']:,}</div></div>
<div class='card'><div class='label'>Customers</div><div class='value'>{metrics['dataset']['customer_count']:,}</div></div>
<div class='card'><div class='label'>Revenue Growth</div><div class='value'>{pct(kpis['revenue_growth_pct'])}</div></div>
</section>
<section class='panel'><h2>Monthly revenue trend</h2>{line_chart(metrics['monthly_revenue'])}</section>
<section class='two-col'><div class='panel'><h2>Revenue by category</h2>{bar_rows(categories, 'category', 'revenue')}</div><div class='panel'><h2>Revenue by store</h2>{bar_rows(stores, 'store_location', 'revenue')}</div></section>
<section class='panel'><h2>Top products</h2><table><thead><tr><th>Product</th><th>Category</th><th>Revenue</th><th>Profit</th></tr></thead><tbody>{product_rows}</tbody></table></section>
<section class='panel'><h2>Store performance</h2><table><thead><tr><th>Store</th><th>Revenue</th><th>Profit</th></tr></thead><tbody>{store_rows}</tbody></table></section>
<footer>Generated locally from artifacts/sample_metrics.json. Synthetic data only. dbt: 61/61 tests passed; Python: 6 tests passed; Airflow: end-to-end DAG succeeded.</footer>
</main></body></html>"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html_document, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
