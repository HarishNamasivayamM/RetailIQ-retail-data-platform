{{ config(materialized='table') }}

select
    date_key,
    transaction_date,
    sum(net_sales)::number(18, 2) as total_revenue,
    sum(profit)::number(18, 2) as total_profit,
    (sum(profit) / nullif(sum(net_sales), 0))::number(18, 6) as profit_margin,
    count(distinct transaction_id) as total_transactions,
    sum(quantity) as units_sold,
    count(distinct customer_key) as customer_count,
    (sum(net_sales) / nullif(count(distinct transaction_id), 0))::number(18, 2) as average_order_value
from {{ ref('fct_sales') }}
group by date_key, transaction_date

