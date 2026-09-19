# Data dictionary

## Source and staging fields

| Field | Type | Required | Meaning and transformation |
|---|---|---:|---|
| `transaction_id` | varchar | yes | Stable source line identifier; unique grain key. |
| `transaction_date` | date | yes | Business date used by `dim_date`. |
| `customer_id` | varchar | yes | Natural customer identifier; mapped to `customer_key`. |
| `product_id` | varchar | yes | Natural product identifier; mapped to `product_key`. |
| `product_name` | varchar | no | Source product description; Type 1 current attribute. |
| `category` | varchar | no | Product category used for slicing. |
| `subcategory` | varchar | no | Product subcategory used for drill-down. |
| `quantity` | integer | yes | Positive units in the line. |
| `unit_price` | decimal(18,2) | yes | Pre-discount price per unit. |
| `discount` | decimal(8,4) | yes | Fractional discount from 0 through 1. |
| `sales_amount` / `net_sales` | decimal(18,2) | yes | Quantity × unit price × (1 − discount). |
| `cost` | decimal(18,2) | yes | Source cost for the line. |
| `profit` | decimal(18,2) | yes | Net sales − cost; reconciled in Python, Snowflake, and dbt. |
| `store_id` | varchar | no | Natural store identifier; mapped to `store_key`. |
| `store_location` | varchar | no | Human-readable store location. |
| `payment_method` | varchar | no | Payment channel from source. |
| `customer_segment` | varchar | no | Current customer segment; Type 1 in this reference feed. |
| `ingestion_batch_id` | varchar | yes in RAW | Airflow/local run identifier. |
| `source_file_name` | varchar | yes in RAW | File or stage source identifier. |
| `loaded_at` | timestamp | yes in RAW | Warehouse arrival timestamp and incremental watermark. |

## Warehouse models

`fct_sales` has one row per transaction line. Its measures are `quantity`,
`gross_sales`, `discount_amount`, `net_sales`, `cost`, `profit`, and
`profit_margin`. Dimensions use deterministic MD5 surrogate keys while retaining
natural IDs for traceability.

