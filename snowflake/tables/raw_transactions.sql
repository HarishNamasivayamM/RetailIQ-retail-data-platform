create table if not exists RETAILIQ.RAW.TRANSACTIONS (
    transaction_id varchar not null,
    transaction_date date not null,
    customer_id varchar not null,
    product_id varchar not null,
    product_name varchar,
    category varchar,
    subcategory varchar,
    quantity number(18, 0),
    unit_price number(18, 2),
    discount number(8, 4),
    sales_amount number(18, 2),
    cost number(18, 2),
    profit number(18, 2),
    store_id varchar,
    store_location varchar,
    payment_method varchar,
    customer_segment varchar,
    ingestion_batch_id varchar not null,
    source_file_name varchar not null,
    loaded_at timestamp_ntz not null default current_timestamp(),
    constraint pk_raw_transactions primary key (transaction_id)
)
comment = 'Raw retail transaction lines; source values are retained with ingestion metadata';

