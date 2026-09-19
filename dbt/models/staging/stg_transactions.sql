{{ config(
    materialized='incremental',
    unique_key='transaction_id',
    incremental_strategy='merge',
    on_schema_change='fail'
) }}

with source_transactions as (
    select *
    from {{ source('retailiq_raw', 'transactions') }}
    {% if is_incremental() %}
      where loaded_at >= (
          select coalesce(max(loaded_at), to_timestamp_ntz('1900-01-01')) from {{ this }}
      ) - interval '2 day'
    {% endif %}
), normalized as (
    select
        transaction_id::varchar as transaction_id,
        transaction_date::date as transaction_date,
        customer_id::varchar as customer_id,
        product_id::varchar as product_id,
        product_name::varchar as product_name,
        category::varchar as category,
        subcategory::varchar as subcategory,
        quantity::number(18, 0) as quantity,
        unit_price::number(18, 2) as unit_price,
        discount::number(8, 4) as discount,
        sales_amount::number(18, 2) as net_sales,
        cost::number(18, 2) as cost,
        profit::number(18, 2) as profit,
        store_id::varchar as store_id,
        store_location::varchar as store_location,
        payment_method::varchar as payment_method,
        customer_segment::varchar as customer_segment,
        ingestion_batch_id::varchar as ingestion_batch_id,
        source_file_name::varchar as source_file_name,
        loaded_at::timestamp_ntz as loaded_at
    from source_transactions
)
select *
from normalized

