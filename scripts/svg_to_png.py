from pathlib import Path
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

SVG_DIR = Path("docs/images/anofox")
PNG_DIR = Path("docs/images/anofox_png")
PNG_DIR.mkdir(parents=True, exist_ok=True)

svgs = sorted(SVG_DIR.glob("*.svg"))
ok = 0
for svg in svgs:
    png = PNG_DIR / (svg.stem + ".png")
    try:
        drawing = svg2rlg(str(svg))
        if drawing is None:
            print(f"[SKIP] {svg.stem}: svg2rlg returned None")
            continue
        renderPM.drawToFile(drawing, str(png), fmt="PNG", dpi=100)
        print(f"[OK] {svg.stem}.png: {png.stat().st_size:,} bytes")
        ok += 1
    except Exception as e:
        print(f"[ERR] {svg.stem}: {str(e)[:150]}")

print(f"\n{ok}/{len(svgs)} convertidos")
