{{ config(materialized='table') }}

select
    product_key,
    product_id,
    p.product_name,
    p.category,
    p.subcategory,
    sum(f.quantity) as units_sold,
    count(distinct f.transaction_id) as transaction_count,
    sum(f.net_sales)::number(18, 2) as revenue,
    sum(f.profit)::number(18, 2) as profit,
    (sum(f.profit) / nullif(sum(f.net_sales), 0))::number(18, 6) as profit_margin
from {{ ref('fct_sales') }} f
join {{ ref('dim_product') }} p using (product_key)
group by product_key, product_id, p.product_name, p.category, p.subcategory

