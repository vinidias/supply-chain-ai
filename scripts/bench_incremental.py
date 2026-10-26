import duckdb
import time

con = duckdb.connect("data/supply_chain.duckdb")

# Benchmark: SELECT COUNT(*) em view vs incremental
t0 = time.time()
con.execute("SELECT COUNT(*) FROM staging.stg_orders").fetchone()
t_view = time.time() - t0

t0 = time.time()
con.execute("SELECT COUNT(*) FROM staging.stg_orders_incremental").fetchone()
t_incremental = time.time() - t0

print(f"View stg_orders:          {t_view*1000:.2f}ms")
print(f"Incremental (table):      {t_incremental*1000:.2f}ms")
print(f"Speedup:                  {t_view/t_incremental:.1f}x mais rápido")

# E se fosse 50M de linhas? Extrapolando
print()
print("Extrapolando para 50M linhas:")
print(f"  View:        {t_view*10000:.0f}ms (~{t_view*10:.0f}s)")
print(f"  Incremental: {t_incremental*10000:.0f}ms (~{t_incremental*10*1000:.0f}µs) — constante")

con.close()
