"""
Gera dados sintéticos de supply chain (suppliers, products, orders, inventory).

Schema:
    suppliers  : id, name, country, category, rating
    products   : id, name, category, supplier_id, unit_cost, lead_time_days
    orders     : id, product_id, order_date, quantity, unit_price, status
    inventory  : product_id, snapshot_date, stock_level, reorder_point
"""
from __future__ import annotations
import random
from datetime import datetime, timedelta
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

DB_PATH = Path(__file__).parent.parent / "data" / "supply_chain.duckdb"
random.seed(42)
np.random.seed(42)


COUNTRIES = ["Brazil", "China", "USA", "Germany", "India", "Mexico", "Vietnam"]
CATEGORIES = ["Electronics", "Packaging", "Raw Materials", "Logistics", "Components"]
STATUSES = ["delivered", "in_transit", "delayed", "cancelled"]


def generate() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    con = duckdb.connect(str(DB_PATH))

    # Suppliers
    n_suppliers = 50
    suppliers = pd.DataFrame({
        "id": range(1, n_suppliers + 1),
        "name": [f"Supplier_{i:03d}" for i in range(1, n_suppliers + 1)],
        "country": np.random.choice(COUNTRIES, n_suppliers),
        "category": np.random.choice(CATEGORIES, n_suppliers),
        "rating": np.round(np.random.uniform(2.5, 5.0, n_suppliers), 1),
    })
    con.execute("CREATE TABLE suppliers AS SELECT * FROM suppliers_df", {"suppliers_df": suppliers})

    # Products
    n_products = 200
    products = pd.DataFrame({
        "id": range(1, n_products + 1),
        "name": [f"Product_{i:04d}" for i in range(1, n_products + 1)],
        "category": np.random.choice(CATEGORIES, n_products),
        "supplier_id": np.random.randint(1, n_suppliers + 1, n_products),
        "unit_cost": np.round(np.random.uniform(5, 500, n_products), 2),
        "lead_time_days": np.random.randint(3, 45, n_products),
    })
    con.execute("CREATE TABLE products AS SELECT * FROM products_df", {"products_df": products})

    # Orders (last 180 days)
    n_orders = 5000
    base_date = datetime(2026, 10, 25)
    order_dates = [base_date - timedelta(days=int(d)) for d in np.random.randint(0, 180, n_orders)]
    order_products = np.random.randint(1, n_products + 1, n_orders)
    unit_prices = [
        float(products.iloc[p - 1]["unit_cost"]) * random.uniform(1.1, 1.5)
        for p in order_products
    ]
    orders = pd.DataFrame({
        "id": range(1, n_orders + 1),
        "product_id": order_products,
        "order_date": order_dates,
        "quantity": np.random.randint(1, 500, n_orders),
        "unit_price": np.round(unit_prices, 2),
        "status": np.random.choice(STATUSES, n_orders, p=[0.80, 0.12, 0.06, 0.02]),
    })
    con.execute("CREATE TABLE orders AS SELECT * FROM orders_df", {"orders_df": orders})

    # Inventory snapshots (last 30 days, 3 per day)
    inv_rows = []
    for day in range(30):
        snap_date = base_date - timedelta(days=day)
        for pid in np.random.choice(range(1, n_products + 1), 100, replace=False):
            inv_rows.append({
                "product_id": int(pid),
                "snapshot_date": snap_date,
                "stock_level": int(np.random.uniform(0, 2000)),
                "reorder_point": int(np.random.uniform(50, 500)),
            })
    inventory = pd.DataFrame(inv_rows)
    con.execute("CREATE TABLE inventory AS SELECT * FROM inventory_df", {"inventory_df": inventory})

    con.close()
    print(f"[OK] {DB_PATH}")
    print(f"     suppliers: {len(suppliers)}")
    print(f"     products:  {len(products)}")
    print(f"     orders:    {len(orders)}")
    print(f"     inventory: {len(inventory)}")


if __name__ == "__main__":
    generate()