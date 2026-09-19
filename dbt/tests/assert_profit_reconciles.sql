select transaction_id
from {{ ref('fct_sales') }}
where abs(profit - (net_sales - cost)) > 0.01

