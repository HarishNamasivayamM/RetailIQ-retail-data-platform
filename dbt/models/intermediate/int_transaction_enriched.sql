{{ config(materialized='view') }}

select
    transaction_id,
    transaction_date,
    customer_id,
    product_id,
    product_name,
    category,
    subcategory,
    quantity,
    unit_price,
    discount,
    (quantity * unit_price)::number(18, 2) as gross_sales,
    ((quantity * unit_price) - net_sales)::number(18, 2) as discount_amount,
    net_sales,
    cost,
    profit,
    (profit / nullif(net_sales, 0))::number(18, 6) as profit_margin,
    store_id,
    store_location,
    payment_method,
    customer_segment,
    ingestion_batch_id,
    source_file_name,
    loaded_at
from {{ ref('stg_transactions') }}

