-- Treat every returned row as a failed data-quality check.
select 'duplicate_transaction_id' as check_name, transaction_id, count(*) as row_count
from RETAILIQ.RAW.TRANSACTIONS
group by transaction_id
having count(*) > 1;

select 'invalid_amount_reconciliation' as check_name, transaction_id
from RETAILIQ.RAW.TRANSACTIONS
where abs(sales_amount - (quantity * unit_price * (1 - discount))) > 0.01
   or abs(profit - (sales_amount - cost)) > 0.01;

select
    count(*) as loaded_row_count,
    sum(sales_amount) as loaded_revenue,
    sum(profit) as loaded_profit,
    min(transaction_date) as min_transaction_date,
    max(transaction_date) as max_transaction_date
from RETAILIQ.RAW.TRANSACTIONS;

