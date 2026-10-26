# 🏭 Supply Chain AI

> **Full-stack AI data platform for supply chain analytics** — FastAPI · PostgreSQL/DuckDB · dbt · LangChain · Groq (Llama 3.3) · Streamlit · Docker-ready.

[![CI](https://github.com/vinidias/supply-chain-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/vinidias/supply-chain-ai/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![dbt](https://img.shields.io/badge/dbt-1.8-FF694B.svg)](https://www.getdbt.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

**Real outputs (validated end-to-end, 2026-10-25):**

**Q1: "Qual o supplier com maior GMV?"**
```
SQL gerado:
SELECT s.id, s.name, SUM(o.quantity * o.unit_price) AS gmv
FROM orders o
JOIN products p ON o.product_id = p.id
JOIN suppliers s ON p.supplier_id = s.id
WHERE o.status = 'delivered'
GROUP BY s.id, s.name
ORDER BY gmv DESC
LIMIT 1

Resposta: O fornecedor com maior GMV é Supplier_012 (ID 12) com GMV R$ 20.883.441,46
```

**Q2: "Quantos pedidos foram atrasados?"**
```
SQL: SELECT COUNT(*) AS delayed_orders FROM orders WHERE status = 'delayed'
Resposta: Foram 312 pedidos atrasados.
```

**Q3: "Qual o ticket medio dos pedidos?"**
```
SQL: SELECT AVG(quantity * unit_price) AS average_ticket FROM orders
Resposta: O ticket médio dos pedidos é R$ 82.352,05.
```

**Provider comparison** (both tested with the same 3 questions, 2026-10-25):

| Provider | Model | Latency | Answer quality | Cost |
|---|---|---|---|---|
| **Groq** | `openai/gpt-oss-120b` | ~2s | ✅ identical to Ark | Free tier (1k req/day) |
| **BytePlus Ark** | `seed-2-0-lite-260428` | ~5s | ✅ identical to Ark | Pay-per-token |

**Both providers returned identical answers** for all 3 questions:
- "Qual o supplier com maior GMV?" → **Supplier_012 · R$ 20.883.441,46**
- "Quantos pedidos foram atrasados?" → **312**
- "Qual o ticket médio?" → **R$ 82.352,05**

### Supported models

**Groq** (via `GROQ_MODEL`):
- `openai/gpt-oss-120b` (default, recommended)
- `openai/gpt-oss-20b` (faster, smaller)
- `qwen/qwen3.8-27b`
- `allam-2-7b`

**BytePlus Ark** (via `ARK_MODEL`):
- `seed-2-0-lite-260428` (tested ✅)
- `seed-2-0-mini-260428` (tested ✅)
- `deepseek-v4-flash-260425` (requires activation in console)
- `deepseek-v4-1-flash-260910` (requires activation)
- `glm-5-3-flash-260828` (requires activation)

**Which to choose?**
- **Groq** for speed + zero cost (best for demos)
- **Ark** for production (SLA, enterprise support, payment terms)

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
