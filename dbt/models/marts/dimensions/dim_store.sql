{{ config(materialized='table') }}

select
    {{ retailiq_surrogate_key(['store_id']) }} as store_key,
    store_id,
    max(store_location) as store_location,
    current_timestamp()::timestamp_ntz as dbt_updated_at
from {{ ref('int_transaction_enriched') }}
group by store_id

