# 🏭 Supply Chain AI

> **Full-stack AI data platform for supply chain analytics** — FastAPI · PostgreSQL/DuckDB · dbt · LangChain · Groq (Llama 3.3) · Streamlit · Docker-ready.

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![dbt](https://img.shields.io/badge/dbt-1.8-FF694B.svg)](https://www.getdbt.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)

---

## 🎯 What this demonstrates

This project was built to showcase the stack required for a **Senior Data Developer / AI Solutions** role:

| Capability | Where it lives |
|---|---|
| **FastAPI REST backend** with async + Pydantic | `api/main.py` |
| **SQLAlchemy** + DuckDB (portable) / PostgreSQL (prod) | `api/db.py` |
| **Advanced SQL** (CTEs, window functions, aggregations) | `dbt_project/models/` |
| **dbt** (staging → marts + tests) | `dbt_project/` |
| **LLM integration** via Groq (Llama 3.3 70B) | `rag/llm.py` |
| **RAG pattern**: NL → SQL → execute → synthesize | `rag/llm.py` |
| **AI Agent** with tool calling (LangChain) | `agents/supply_agent.py` |
| **Streamlit UI** for business users | `frontend/app.py` |
| **Docker-ready** (multi-service compose) | `docker/` |
| **Production patterns**: CORS, health checks, env vars, read-only SQL protection | throughout |

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Streamlit  │────▶│   FastAPI   │────▶│  DuckDB /   │
│  (frontend) │     │  (REST API) │     │  PostgreSQL │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Groq LLM   │     │ dbt models  │
                    │ (Llama 3.3) │     │ (stg → mart)│
                    └─────────────┘     └─────────────┘
```

---

## 🚀 Quick start (local, 2 min)

```bash
# 1. clone + venv
git clone <repo-url> supply-chain-ai
cd supply-chain-ai
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate      # Linux/macOS

# 2. install
pip install -r requirements.txt

# 3. seed database
python -m api.seed

# 4. (optional) run dbt models
cd dbt_project && dbt run --profiles-dir . && cd ..

# 5. run API
uvicorn api.main:app --reload --port 8000
# → http://localhost:8000/docs

# 6. run frontend (new terminal)
streamlit run frontend/app.py
# → http://localhost:8501
```

**Optional**: get a free Groq API key at [console.groq.com/keys](https://console.groq.com/keys) and add to `.env`:

```bash
cp .env.example .env
# edit .env and paste your GROQ_API_KEY
```

---

## 🐳 Docker

```bash
cd docker
docker compose up --build
# API:      http://localhost:8000
# Frontend: http://localhost:8501
```

---

## 📡 API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Healthcheck (includes DB) |
| GET | `/suppliers` | List suppliers (paginated, filter by country) |
| GET | `/products` | List products (paginated, filter by category) |
| GET | `/orders/recent` | Recent orders (last N days) |
| GET | `/inventory/low-stock` | Products below reorder point |
| GET | `/metrics/summary` | Aggregated KPIs |
| POST | `/ask` | RAG: natural language question → SQL → answer |

### Example

```bash
curl -X POST http://localhost:8000/ask \\
  -H "Content-Type: application/json" \\
  -d '{"question": "Which supplier has the highest number of delayed orders?"}'
```

Response:
```json
{
  "answer": "Supplier_017 from Vietnam has 12 delayed orders (28% delay rate), followed by Supplier_042 from China with 9 delayed orders (21% rate).",
  "sources": ["SQL: SELECT supplier_name, n_delayed, delay_pct FROM mart_supplier_performance ORDER BY n_delayed DESC LIMIT 5"],
  "model": "llama-3.3-70b-versatile"
}
```

---

## 🧪 dbt models

```
models/
├── staging/
│   ├── stg_suppliers.sql   -- view: raw suppliers
│   └── stg_orders.sql      -- view: enriched orders with product join
└── marts/
    └── mart_supplier_performance.sql   -- table: GMV + delay rate per supplier
```

**Tests included**: `unique` and `not_null` on primary keys and critical metrics.

```bash
cd dbt_project
dbt run          # materialize models
dbt test         # run schema tests
dbt docs generate && dbt docs serve   # lineage graph
```

---

## 🔒 Production considerations

- **SQL injection protection**: all queries use parameter binding (`text()` with `:param`)
- **Read-only mode**: DuckDB connection uses `read_only=True` in the Streamlit UI
- **LLM prompt protection**: forbidden DML tokens blocked in `run_sql` tool
- **Health checks**: `/health` verifies DB connectivity
- **Containerized**: Dockerfile + docker-compose ready for Cloud Run / ECS / Kubernetes
- **Secrets**: only via environment variables (`.env`, never hardcoded)

---

## 🗺️ Roadmap

- [ ] **PostgreSQL** backend (code is SQLAlchemy-portable; just set `DATABASE_URL`)
- [ ] **BigQuery** adapter (swap the SQLAlchemy dialect)
- [ ] **Vector search** with pgvector for document RAG (contracts, specs)
- [ ] **Agent workflows** with LangGraph (multi-step procurement)
- [ ] **dbt Cloud / dbt tests in CI**
- [ ] **Observability**: OpenTelemetry traces on every /ask call

---

## 📚 Stack

| Layer | Technology |
|---|---|
| **API** | FastAPI 0.115 · Pydantic v2 · Uvicorn |
| **Database** | DuckDB (local) · PostgreSQL (prod) · SQLAlchemy 2.0 |
| **Analytics** | dbt-core 1.8 · dbt-duckdb / dbt-postgres |
| **LLM** | Groq (Llama 3.3 70B) · LangChain 0.3 |
| **Frontend** | Streamlit 1.40 |
| **Deploy** | Docker · docker-compose |

---

## 📄 License

MIT — free for study and portfolio use.
