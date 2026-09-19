{{ config(materialized='table') }}

select
    {{ retailiq_surrogate_key(['customer_id']) }} as customer_key,
    customer_id,
    max(customer_segment) as customer_segment,
    min(transaction_date) as first_purchase_date,
    max(transaction_date) as last_purchase_date,
    count(distinct transaction_id) as transaction_count,
    sum(net_sales)::number(18, 2) as lifetime_net_sales,
    current_timestamp()::timestamp_ntz as dbt_updated_at
from {{ ref('int_transaction_enriched') }}
group by customer_id

