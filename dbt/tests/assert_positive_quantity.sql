select transaction_id
from {{ ref('fct_sales') }}
where quantity <= 0

