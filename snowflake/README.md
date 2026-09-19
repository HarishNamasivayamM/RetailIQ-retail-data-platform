# Snowflake setup

The SQL in this directory creates the `RETAILIQ` database, `RAW`, `STAGING`, and
`ANALYTICS` schemas, a small auto-suspending warehouse, and a typed raw table.
Credentials are intentionally not included. Set the variables in `.env` or use
an Airflow connection named `retailiq_snowflake`.

Run the scripts in order:

1. `setup/01_create_database.sql`
2. `setup/02_create_schemas.sql`
3. `setup/03_create_warehouse_and_stage.sql`
4. `tables/raw_transactions.sql`
5. Upload a source CSV to `@RETAILIQ.RAW.RETAILIQ_STAGE`.
6. Execute `loading/load_transactions.sql` with a batch id.
7. Run `validation/source_validation.sql`.

The load uses a landing table plus `MERGE` on `transaction_id`, so replaying the
same batch updates the existing source record instead of appending a duplicate.

