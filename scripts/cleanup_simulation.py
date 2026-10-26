import duckdb

con = duckdb.connect("data/supply_chain.duckdb")
con.execute("DELETE FROM orders WHERE id >= 9990")
con.execute("DROP TABLE IF EXISTS staging.stg_orders_incremental")
print("Limpo:", con.execute("SELECT COUNT(*) FROM orders").fetchone()[0], "pedidos restantes")
con.close()
