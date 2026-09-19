{{ config(materialized='table') }}

with bounds as (
    select min(transaction_date) as min_date, max(transaction_date) as max_date
    from {{ ref('stg_transactions') }}
), dates as (
    select dateadd(day, seq4(), min_date) as calendar_date
    from bounds, table(generator(rowcount => 3660))
), filtered_dates as (
    select d.calendar_date
    from dates d
    cross join bounds b
    where d.calendar_date <= b.max_date
)
select
    to_number(to_char(calendar_date, 'YYYYMMDD')) as date_key,
    calendar_date,
    year(calendar_date) as year_number,
    quarter(calendar_date) as quarter_number,
    month(calendar_date) as month_number,
    monthname(calendar_date) as month_name,
    weekofyear(calendar_date) as week_number,
    dayofweekiso(calendar_date) as day_of_week,
    dayname(calendar_date) as day_name,
    iff(dayofweekiso(calendar_date) >= 6, true, false) as is_weekend
from filtered_dates
