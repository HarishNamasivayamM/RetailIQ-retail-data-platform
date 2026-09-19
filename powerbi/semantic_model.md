# Power BI semantic model

## Tables

| Table | Role | Grain |
|---|---|---|
| `fct_sales` | fact | one row per retail transaction line |
| `dim_date` | dimension | one row per calendar date |
| `dim_customer` | dimension | one row per current customer |
| `dim_product` | dimension | one row per current product |
| `dim_store` | dimension | one row per current store |
| `mart_product_performance` | aggregate | one row per product |
| `mart_customer_performance` | aggregate | one row per customer |
| `mart_store_performance` | aggregate | one row per store |

## Relationships

Create single-direction, one-to-many relationships:

```text
dim_date[date_key]       1 ──── * fct_sales[date_key]
dim_customer[customer_key] 1 ── * fct_sales[customer_key]
dim_product[product_key] 1 ── * fct_sales[product_key]
dim_store[store_key]     1 ──── * fct_sales[store_key]
```

Mark `dim_date[calendar_date]` as the date table. Hide technical keys from the
report canvas. Prefer measures over calculated columns for business KPIs.

