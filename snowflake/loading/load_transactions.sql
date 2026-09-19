-- Replace the batch id before running, or have Airflow bind it as a session variable.
set RETAILIQ_BATCH_ID = 'replace-with-airflow-batch-id';

-- CTAS intentionally leaves the two ingestion metadata fields nullable until they are populated below.
create or replace temporary table RETAILIQ.RAW.TRANSACTIONS_LANDING as
select * from RETAILIQ.RAW.TRANSACTIONS where 1 = 0;

copy into RETAILIQ.RAW.TRANSACTIONS_LANDING (
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
    sales_amount,
    cost,
    profit,
    store_id,
    store_location,
    payment_method,
    customer_segment
)
from @__RETAILIQ_STAGE_PATH__
file_format = (
    type = csv
    skip_header = 1
    field_optionally_enclosed_by = '"'
    null_if = ('', 'NULL', 'null')
    empty_field_as_null = true
)
on_error = 'ABORT_STATEMENT';

update RETAILIQ.RAW.TRANSACTIONS_LANDING
set ingestion_batch_id = $RETAILIQ_BATCH_ID,
    source_file_name = 'RETAILIQ_STAGE_LOAD';

merge into RETAILIQ.RAW.TRANSACTIONS as target
using RETAILIQ.RAW.TRANSACTIONS_LANDING as source
    on target.transaction_id = source.transaction_id
when matched then update set
    transaction_date = source.transaction_date,
    customer_id = source.customer_id,
    product_id = source.product_id,
    product_name = source.product_name,
    category = source.category,
    subcategory = source.subcategory,
    quantity = source.quantity,
    unit_price = source.unit_price,
    discount = source.discount,
    sales_amount = source.sales_amount,
    cost = source.cost,
    profit = source.profit,
    store_id = source.store_id,
    store_location = source.store_location,
    payment_method = source.payment_method,
    customer_segment = source.customer_segment,
    ingestion_batch_id = source.ingestion_batch_id,
    source_file_name = source.source_file_name,
    loaded_at = current_timestamp()
when not matched then insert (
    transaction_id, transaction_date, customer_id, product_id, product_name,
    category, subcategory, quantity, unit_price, discount, sales_amount, cost,
    profit, store_id, store_location, payment_method, customer_segment,
    ingestion_batch_id, source_file_name
)
values (
    source.transaction_id, source.transaction_date, source.customer_id, source.product_id,
    source.product_name, source.category, source.subcategory, source.quantity,
    source.unit_price, source.discount, source.sales_amount, source.cost, source.profit,
    source.store_id, source.store_location, source.payment_method, source.customer_segment,
    source.ingestion_batch_id, source.source_file_name
);
