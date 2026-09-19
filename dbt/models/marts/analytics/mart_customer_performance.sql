{{ config(materialized='table') }}

select
    customer_key,
    c.customer_id,
    c.customer_segment,
    count(distinct f.transaction_id) as transaction_count,
    sum(f.net_sales)::number(18, 2) as revenue,
    sum(f.profit)::number(18, 2) as profit,
    iff(count(distinct f.transaction_id) > 1, true, false) as is_repeat_customer
from {{ ref('fct_sales') }} f
join {{ ref('dim_customer') }} c using (customer_key)
group by customer_key, c.customer_id, c.customer_segment

