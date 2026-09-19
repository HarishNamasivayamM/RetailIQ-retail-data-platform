{{ config(materialized='table') }}

select
    {{ retailiq_surrogate_key(['product_id']) }} as product_key,
    product_id,
    max(product_name) as product_name,
    max(category) as category,
    max(subcategory) as subcategory,
    current_timestamp()::timestamp_ntz as dbt_updated_at
from {{ ref('int_transaction_enriched') }}
group by product_id

