import duckdb
from pathlib import Path

OUT = Path("docs/images/anofox")
OUT.mkdir(parents=True, exist_ok=True)

con = duckdb.connect("data/supply_chain.duckdb", read_only=True)
con.execute("LOAD anofox_visualization")

panels = {
    # === KPIs (big number tiles) ===
    "kpi_gmv": """
        SELECT ROUND(SUM(quantity * unit_price), 2)::MONEY AS "GMV total"
        FROM orders
    """,
    "kpi_orders": """
        SELECT COUNT(*)::METRIC AS "Pedidos"
        FROM orders
    """,
    "kpi_delayed": """
        SELECT COUNT(*)::METRIC AS "Pedidos atrasados"
        FROM orders WHERE status = 'delayed'
    """,
    "kpi_suppliers": """
        SELECT COUNT(*)::METRIC AS "Suppliers"
        FROM suppliers
    """,
    "kpi_delay_rate": """
        SELECT ROUND(100.0 * SUM(CASE WHEN status='delayed' THEN 1 ELSE 0 END) / COUNT(*), 2)::PERCENT AS "Taxa de atraso"
        FROM orders
    """,

    # === Charts ===
    "bar_top_suppliers": """
        SELECT anofox_bar(supplier_name, gmv)
        FROM (SELECT supplier_name, gmv FROM marts.mart_supplier_performance ORDER BY gmv DESC LIMIT 10)
    """,
    "bar_status": """
        SELECT anofox_bar(status, n)
        FROM (SELECT status, COUNT(*) AS n FROM orders GROUP BY status ORDER BY n DESC)
    """,
    "line_orders_day": """
        SELECT anofox_line(day, n_orders)
        FROM (
            SELECT order_date::DATE AS day, COUNT(*) AS n_orders
            FROM orders GROUP BY 1 ORDER BY 1
        )
    """,
    "area_gmv_day": """
        SELECT anofox_area(day, gmv)
        FROM (
            SELECT order_date::DATE AS day, ROUND(SUM(quantity * unit_price), 2) AS gmv
            FROM orders GROUP BY 1 ORDER BY 1
        )
    """,
    "scatter_rating_delay": """
        SELECT anofox_scatter(rating, delay_pct)
        FROM marts.mart_supplier_performance
        WHERE n_orders > 50
    """,
    "bar_top_products": """
        SELECT anofox_bar(product_name, total_sold)
        FROM (
            SELECT p.name AS product_name, ROUND(SUM(o.quantity * o.unit_price), 2) AS total_sold
            FROM orders o JOIN products p ON p.id = o.product_id
            GROUP BY p.name
            ORDER BY total_sold DESC
            LIMIT 10
        )
    """,
}

results = {}
for name, sql in panels.items():
    try:
        r = con.execute(sql).fetchone()
        svg = r[0] if r and r[0] else None
        if svg:
            (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
            results[name] = {"status": "OK", "bytes": len(svg)}
            print(f"[OK] {name}: {len(svg):,} bytes")
        else:
            results[name] = {"status": "NULL"}
            print(f"[NULL] {name}")
    except Exception as e:
        results[name] = {"status": "ERR", "error": str(e)[:200]}
        print(f"[ERR] {name}: {str(e)[:120]}")

con.close()

ok = sum(1 for r in results.values() if r["status"] == "OK")
print(f"\nTotal: {ok}/{len(panels)} paineis gerados")
