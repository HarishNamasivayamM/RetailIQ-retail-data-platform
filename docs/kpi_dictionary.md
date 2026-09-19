# KPI dictionary

| KPI | Definition | Formula | Source model / Power BI measure |
|---|---|---|---|
| Total Revenue | Net sales across selected context | `SUM(net_sales)` | `fct_sales` / `Total Revenue` |
| Total Profit | Revenue after source cost | `SUM(profit)` | `fct_sales` / `Total Profit` |
| Profit Margin % | Profit as a share of revenue | `Total Profit / Total Revenue` | `fct_sales` / `Profit Margin %` |
| Total Transactions | Distinct transaction lines | `DISTINCTCOUNT(transaction_id)` | `fct_sales` / `Total Transactions` |
| Average Order Value | Revenue per transaction line | `Total Revenue / Total Transactions` | `fct_sales` / `Average Order Value` |
| Units Sold | Total quantity sold | `SUM(quantity)` | `fct_sales` / `Units Sold` |
| Revenue per Customer | Revenue per distinct customer | `Total Revenue / Customer Count` | `fct_sales` / `Revenue per Customer` |
| Repeat Customer Rate % | Customers with more than one transaction | `repeat customers / customers` | `mart_customer_performance` / `Repeat Customer Rate %` |
| Revenue Growth % | Current year/context versus prior year | `(current - prior) / prior` | `dim_date` / `Revenue Growth %` |
| Top Product Contribution % | Revenue share of top selected product | `top product revenue / total revenue` | `mart_product_performance` / `Top Product Contribution %` |

KPI is a metric; an insight is the business interpretation of a KPI or a group
of KPIs. The metrics in `artifacts/sample_metrics.json` are calculated from the
deterministic synthetic demo rather than hard-coded in the pipeline.

