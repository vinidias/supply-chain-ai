import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

r = httpx.post(
    "http://localhost:8000/ask",
    json={"question": "Qual o supplier com maior GMV?"},
    timeout=60.0,
)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:1000]}")
