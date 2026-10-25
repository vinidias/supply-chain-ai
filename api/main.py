"""
Supply Chain AI — FastAPI backend.

Endpoints:
    GET  /health              — healthcheck
    GET  /suppliers           — list suppliers (paginado)
    GET  /products            — list products
    GET  /orders/recent       — ultimos N pedidos
    GET  /inventory/low-stock — produtos abaixo do reorder point
    GET  /metrics/summary     — KPIs agregados
    POST /ask                 — RAG: pergunta em NL sobre os dados
"""
from __future__ import annotations

import os
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api import db
from api.models import AskRequest, AskResponse

app = FastAPI(
    title="Supply Chain AI",
    description="API de supply chain com RAG sobre dados operacionais",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    try:
        rows = db.query("SELECT 1 AS ok")
        return {"status": "ok", "db": rows[0]["ok"] == 1}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


@app.get("/suppliers")
def list_suppliers(
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    country: str | None = None,
):
    sql = "SELECT * FROM suppliers"
    params = {}
    if country:
        sql += " WHERE country = :country"
        params["country"] = country
    sql += " ORDER BY rating DESC LIMIT :limit"
    params["limit"] = limit
    return db.query(sql, params)


@app.get("/products")
def list_products(
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    category: str | None = None,
):
    sql = "SELECT * FROM products"
    params = {}
    if category:
        sql += " WHERE category = :category"
        params["category"] = category
    sql += " ORDER BY unit_cost DESC LIMIT :limit"
    params["limit"] = limit
    return db.query(sql, params)


@app.get("/orders/recent")
def recent_orders(
    days: Annotated[int, Query(ge=1, le=180)] = 7,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
):
    sql = f"""
        SELECT o.id, o.product_id, o.order_date, o.quantity,
               o.unit_price, o.status, p.name AS product_name
        FROM orders o
        LEFT JOIN products p ON p.id = o.product_id
        WHERE o.order_date >= (SELECT MAX(order_date) FROM orders) - INTERVAL '{days}' DAY
        ORDER BY o.order_date DESC
        LIMIT :limit
    """
    return db.query(sql, {"limit": limit})


@app.get("/inventory/low-stock")
def low_stock(limit: Annotated[int, Query(ge=1, le=200)] = 50):
    sql = """
        WITH latest AS (
            SELECT product_id, stock_level, reorder_point, snapshot_date,
                   ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY snapshot_date DESC) AS rn
            FROM inventory
        )
        SELECT l.product_id, p.name AS product_name, l.stock_level, l.reorder_point,
               l.stock_level - l.reorder_point AS gap
        FROM latest l
        LEFT JOIN products p ON p.id = l.product_id
        WHERE l.rn = 1 AND l.stock_level < l.reorder_point
        ORDER BY gap ASC
        LIMIT :limit
    """
    return db.query(sql, {"limit": limit})


@app.get("/suppliers/performance")
def supplier_performance(limit: Annotated[int, Query(ge=1, le=100)] = 20):
    """Performance agregada por supplier (usa dbt mart)."""
    try:
        return db.query(
            "SELECT * FROM marts.mart_supplier_performance ORDER BY gmv DESC LIMIT :limit",
            {"limit": limit},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"dbt mart indisponivel: {e}. Rode dbt run primeiro.")


@app.get("/metrics/summary")
def metrics_summary():
    rows = db.query("""
        SELECT
          (SELECT COUNT(*) FROM suppliers) AS n_suppliers,
          (SELECT COUNT(*) FROM products) AS n_products,
          (SELECT COUNT(*) FROM orders) AS n_orders,
          (SELECT ROUND(SUM(quantity * unit_price), 2) FROM orders) AS gmv,
          (SELECT ROUND(AVG(rating), 2) FROM suppliers) AS avg_supplier_rating,
          (SELECT COUNT(*) FROM orders WHERE status = 'delayed') AS n_delayed_orders
    """)
    return rows[0]


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """RAG sobre os dados: pergunta em NL, resposta fundamentada em SQL."""
    if not (os.getenv("GROQ_API_KEY") or os.getenv("ARK_API_KEY") or os.getenv("OPENAI_API_KEY")):
        raise HTTPException(
            status_code=503,
            detail="Nenhum LLM configurado. Sete GROQ_API_KEY, ARK_API_KEY ou OPENAI_API_KEY no .env",
        )

    try:
        from rag.llm import answer_question
        answer, sources, model = answer_question(req.question)
        return AskResponse(answer=answer, sources=sources, model=model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no LLM: {e}")
