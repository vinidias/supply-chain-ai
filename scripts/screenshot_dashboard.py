from playwright.sync_api import sync_playwright
from pathlib import Path

url = "file:///D:/Dev/supply-chain-ai/docs/dashboard_anofox.html"
out = Path("docs/images/dashboard_full.png")
out.parent.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1400, "height": 1000})
    page.goto(url, wait_until="networkidle")
    page.wait_for_timeout(1000)
    page.screenshot(path=str(out), full_page=True)
    browser.close()

print(f"[OK] screenshot: {out} ({out.stat().st_size:,} bytes)")
