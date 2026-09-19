{{ config(materialized='table') }}

select
    store_key,
    s.store_id,
    s.store_location,
    count(distinct f.transaction_id) as transaction_count,
    sum(f.quantity) as units_sold,
    sum(f.net_sales)::number(18, 2) as revenue,
    sum(f.profit)::number(18, 2) as profit,
    (sum(f.profit) / nullif(sum(f.net_sales), 0))::number(18, 6) as profit_margin
from {{ ref('fct_sales') }} f
join {{ ref('dim_store') }} s using (store_key)
group by store_key, s.store_id, s.store_location

