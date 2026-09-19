select f.transaction_id
from {{ ref('fct_sales') }} f
left join {{ ref('dim_customer') }} c using (customer_key)
left join {{ ref('dim_product') }} p using (product_key)
left join {{ ref('dim_date') }} d using (date_key)
left join {{ ref('dim_store') }} s using (store_key)
where c.customer_key is null
   or p.product_key is null
   or d.date_key is null
   or s.store_key is null

