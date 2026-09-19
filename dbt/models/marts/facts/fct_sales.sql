{{ config(
    materialized='incremental',
    unique_key='transaction_id',
    incremental_strategy='merge',
    on_schema_change='fail'
) }}

select
    t.transaction_id,
    c.customer_key,
    p.product_key,
    d.date_key,
    s.store_key,
    t.customer_id,
    t.product_id,
    t.store_id,
    t.transaction_date,
    t.quantity,
    t.unit_price,
    t.discount,
    t.gross_sales,
    t.discount_amount,
    t.net_sales,
    t.cost,
    t.profit,
    t.profit_margin,
    t.payment_method,
    t.ingestion_batch_id,
    t.loaded_at
from {{ ref('int_transaction_enriched') }} t
join {{ ref('dim_customer') }} c using (customer_id)
join {{ ref('dim_product') }} p using (product_id)
join {{ ref('dim_date') }} d on t.transaction_date = d.calendar_date
join {{ ref('dim_store') }} s using (store_id)
{% if is_incremental() %}
where t.loaded_at >= (
    select coalesce(max(loaded_at), to_timestamp_ntz('1900-01-01')) from {{ this }}
) - interval '2 day'
{% endif %}

