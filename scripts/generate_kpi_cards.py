import duckdb
from pathlib import Path

OUT = Path("docs/images/anofox")
OUT.mkdir(parents=True, exist_ok=True)

con = duckdb.connect("data/supply_chain.duckdb", read_only=True)

# Coletar valores reais
kpis = con.execute("""
    SELECT
        (SELECT ROUND(SUM(quantity * unit_price), 2) FROM orders) AS gmv,
        (SELECT COUNT(*) FROM orders) AS n_orders,
        (SELECT COUNT(*) FROM orders WHERE status = 'delayed') AS n_delayed,
        (SELECT COUNT(*) FROM suppliers) AS n_suppliers,
        (SELECT ROUND(100.0 * SUM(CASE WHEN status='delayed' THEN 1 ELSE 0 END) / COUNT(*), 2) FROM orders) AS delay_rate,
        (SELECT ROUND(AVG(quantity * unit_price), 2) FROM orders) AS ticket_avg
""").fetchone()

gmv, n_orders, n_delayed, n_suppliers, delay_rate, ticket_avg = kpis
con.close()


def fmt_brl(v):
    """Formata 20883441.46 -> R$ 20,88M"""
    if v >= 1e9:
        return f"R$ {v/1e9:.2f}B"
    if v >= 1e6:
        return f"R$ {v/1e6:.2f}M"
    if v >= 1e3:
        return f"R$ {v/1e3:.1f}K"
    return f"R$ {v:.2f}"


def fmt_num(v):
    if v >= 1e6:
        return f"{v/1e6:.2f}M"
    if v >= 1e3:
        return f"{v/1e3:.1f}K"
    return f"{v:,.0f}"


def make_kpi_svg(label, value, subtitle=None, color="#0A66C2"):
    """Gera KPI card como SVG."""
    subtitle_y = 100 if subtitle else 85
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="240" height="120" viewBox="0 0 240 120">
  <rect x="0" y="0" width="240" height="120" fill="white" stroke="#e5e7eb" stroke-width="1" rx="8"/>
  <text x="20" y="28" font-family="system-ui,-apple-system,sans-serif" font-size="11" fill="#6b7280" font-weight="500" letter-spacing="0.5">{label.upper()}</text>
  <text x="20" y="70" font-family="system-ui,-apple-system,sans-serif" font-size="32" fill="{color}" font-weight="700">{value}</text>
  {f'<text x="20" y="{subtitle_y}" font-family="system-ui,sans-serif" font-size="12" fill="#9ca3af">{subtitle}</text>' if subtitle else ''}
</svg>'''
    return svg


kpi_defs = [
    ("kpi_gmv", "GMV Total", fmt_brl(gmv), "Soma de todas as ordens", "#0A66C2"),
    ("kpi_orders", "Pedidos", fmt_num(n_orders), "Ordens processadas", "#0A66C2"),
    ("kpi_delayed", "Atrasados", fmt_num(n_delayed), "Pedidos com status delayed", "#D62828"),
    ("kpi_delay_rate", "Taxa de Atraso", f"{delay_rate:.2f}%", "Delayed / Total", "#D62828"),
    ("kpi_suppliers", "Suppliers", str(n_suppliers), "Fornecedores ativos", "#2A9D8F"),
    ("kpi_ticket", "Ticket Medio", fmt_brl(ticket_avg), "Valor medio por pedido", "#2A9D8F"),
]

for name, label, value, subtitle, color in kpi_defs:
    svg = make_kpi_svg(label, value, subtitle, color)
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
    print(f"[OK] {name}.svg -> {value}")

print(f"\n{len(kpi_defs)} KPIs gerados")
