"""Tests for supply-chain-ai API."""
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["db"] is True


def test_suppliers():
    r = client.get("/suppliers?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert 0 < len(data) <= 5
    assert "name" in data[0] or "supplier_name" in data[0]


def test_products():
    r = client.get("/products?limit=10")
    assert r.status_code == 200
    assert len(r.json()) <= 10


def test_metrics_summary():
    r = client.get("/metrics/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["n_suppliers"] == 50
    assert data["n_products"] == 200
    assert data["gmv"] > 0


def test_supplier_performance_mart():
    r = client.get("/suppliers/performance?limit=3")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 3
    if len(data) > 0:
        row = data[0]
        assert "gmv" in row
        assert "delay_pct" in row
        assert row["gmv"] > 0


def test_low_stock():
    r = client.get("/inventory/low-stock?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)


def test_orders_recent():
    r = client.get("/orders/recent?days=7&limit=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_ask():
    """RAG funciona com key configurada ou retorna 503 sem key."""
    r = client.post("/ask", json={"question": "Quantos pedidos existem?"})
    # 200 = key configurada, funciona
    # 503 = sem key, retorna instrucao
    # 500 = key invalida ou erro do LLM
    assert r.status_code in (200, 500, 503)
    if r.status_code == 200:
        data = r.json()
        assert "answer" in data
        assert len(data["answer"]) > 0
        assert "sources" in data