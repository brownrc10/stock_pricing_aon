# Hershey Stock Reward Valuation Project

## Calculating Volatillity
Volatillity was calculated using minute aggregate data set from massive.com api. Data was restricted to trading hours between 9:30-4:30pm and resampled using pandas to a five minute window.
### Sample Data ![Sample Data](images/sample_data.png)
```sql
WITH log_returns AS (
    SELECT
        *,
        LN(close / LAG(close) OVER (PARTITION BY DATE(window_start) ORDER BY window_start
        )) AS log_return
    FROM hsy_stock_data_min.parquet
    )
    SELECT
        STDDEV(log_return) * SQRT(252 * 390) AS annualized_vol
        FROM log_returns
    WHERE log_return IS NOT NULL;
```
Volatillity Calculation: 0.2688474392751574
