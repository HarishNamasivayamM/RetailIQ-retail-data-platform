# DAX measures

Use these measures against the `fct_sales` model. Names match the KPI dictionary.

```DAX
Total Revenue = SUM(fct_sales[net_sales])

Total Profit = SUM(fct_sales[profit])

Profit Margin % = DIVIDE([Total Profit], [Total Revenue])

Total Transactions = DISTINCTCOUNT(fct_sales[transaction_id])

Average Order Value = DIVIDE([Total Revenue], [Total Transactions])

Units Sold = SUM(fct_sales[quantity])

Customer Count = DISTINCTCOUNT(fct_sales[customer_key])

Revenue per Customer = DIVIDE([Total Revenue], [Customer Count])

Repeat Customer Rate % =
VAR RepeatCustomers =
    COUNTROWS(
        FILTER(
            VALUES(dim_customer[customer_key]),
            CALCULATE([Total Transactions]) > 1
        )
    )
RETURN DIVIDE(RepeatCustomers, [Customer Count])

Revenue Growth % =
VAR PriorRevenue =
    CALCULATE([Total Revenue], DATEADD(dim_date[calendar_date], -1, YEAR))
RETURN DIVIDE([Total Revenue] - PriorRevenue, PriorRevenue)

Top Product Contribution % =
VAR TopProductRevenue =
    MAXX(
        TOPN(1, ALLSELECTED(dim_product[product_key]), [Total Revenue], DESC),
        [Total Revenue]
    )
RETURN DIVIDE(TopProductRevenue, [Total Revenue])
```

