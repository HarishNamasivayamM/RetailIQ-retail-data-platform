# Dashboard specification

## Executive Overview

KPI cards: Total Revenue, Total Profit, Profit Margin %, Total Transactions,
Average Order Value, Units Sold, Customer Count, and Revenue Growth %. Add a
monthly revenue/profit line chart, category revenue bar chart, and slicers for
date, category, customer segment, store location, and payment method.

## Product Performance

Use `mart_product_performance` for a ranked product table with revenue, units,
profit, and margin. Add category/subcategory decomposition and a scatter plot
of revenue versus margin to surface high-revenue/low-margin products.

## Customer Analytics

Use `mart_customer_performance` for customer revenue, transaction count, profit,
segment, and repeat flag. Include segment revenue, top customers, repeat rate,
and a distribution of customer value.

## Store and Time Analysis

Use `mart_store_performance` for store/location ranking. Add daily/monthly trend,
year-over-year comparison when both years are present, and store margin versus
revenue.

