import duckdb
from datetime import datetime, timedelta

con = duckdb.connect("data/supply_chain.duckdb")

# Adicionar 5 pedidos novos (hoje + 1 dia)
max_date = con.execute("SELECT MAX(order_date) FROM orders").fetchone()[0]
print(f"Max date atual: {max_date}")

new_date = max_date + timedelta(days=1)
for i in range(5):
    con.execute("""
        INSERT INTO orders (id, product_id, order_date, quantity, unit_price, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [9990 + i, 1 + i, new_date, 10, 100.0, 'delivered'])

new_count = con.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
print(f"Novo count em orders: {new_count}")
print(f"Novos pedidos adicionados em: {new_date}")
con.close()
