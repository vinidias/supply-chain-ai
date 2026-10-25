.PHONY: help venv install seed dbt api frontend docker clean

help:
	@echo "Targets:"
	@echo "  install   install dependencies"
	@echo "  seed      generate synthetic data"
	@echo "  dbt       run dbt models + tests"
	@echo "  api       run FastAPI (port 8000)"
	@echo "  frontend  run Streamlit (port 8501)"
	@echo "  docker    docker compose up"
	@echo "  clean     remove generated files"

install:
	pip install -r requirements.txt

seed:
	python -m api.seed

dbt:
	cd dbt_project && dbt run --profiles-dir . && dbt test --profiles-dir .

api:
	uvicorn api.main:app --reload --port 8000

frontend:
	streamlit run frontend/app.py

docker:
	cd docker && docker compose up --build

clean:
	rm -f data/*.duckdb data/*.duckdb.wal
	rm -rf dbt_project/target dbt_project/logs