import duckdb


def main():
    sql = """
    WITH log_returns AS (
        SELECT
            *,
            LN(close / LAG(close) OVER (
                PARTITION BY DATE(window_start)
                ORDER BY window_start
            )) AS log_return
        FROM hsy_stock_data.parquet
    ),
    params AS (
        SELECT
            STDDEV(log_return) * SQRT(252 * 78)*100  AS annualized_vol,
            LAST(close ORDER BY window_start) 
                FILTER (WHERE DATE(window_start) = '2025-10-30')  AS spot_price
        FROM log_returns
        WHERE log_return IS NOT NULL
    )
    SELECT
        annualized_vol,
        (1.370 * 4 / spot_price)*100 AS dividend_yield
    FROM params
"""
    conn = duckdb.connect()
    conn.sql(sql).show()


if __name__ == "__main__":
    main()
