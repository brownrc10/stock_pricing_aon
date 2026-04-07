import duckdb


def main():
    sql = """
        SELECT
        (2*LN(1+("3 YR"/100)*(1/2)))*100 AS continous_rfr
        FROM treasury_yield.parquet
    where Date = '10/30/2025'
    """
    conn = duckdb.connect()
    conn.sql(sql).show()


if __name__ == "__main__":
    main()
