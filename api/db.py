"""Database access layer (DuckDB via SQLAlchemy)."""
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DB_PATH = Path(__file__).parent.parent / "data" / "supply_chain.duckdb"

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(f"duckdb:///{DB_PATH}", pool_pre_ping=True)
    return _engine


def query(sql: str, params: dict | None = None) -> list[dict]:
    with get_engine().connect() as conn:
        result = conn.execute(text(sql), params or {})
        return [dict(row._mapping) for row in result]