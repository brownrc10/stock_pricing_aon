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
        )
        SELECT
            STDDEV(log_return) * SQRT(252 * 78) AS annualized_vol
        FROM log_returns
        WHERE log_return IS NOT NULL
    """
    conn = duckdb.connect()
    conn.sql(sql).show()


if __name__ == "__main__":
    main()
