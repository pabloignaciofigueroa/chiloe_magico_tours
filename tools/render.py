"""Rasteriza un SVG/HTML con Playwright: python3 tools/render.py in.svg out.png ancho [fondo]"""
import sys, pathlib, asyncio
from playwright.sync_api import sync_playwright
src, out, w = sys.argv[1], sys.argv[2], int(sys.argv[3]); bg = sys.argv[4] if len(sys.argv) > 4 else 'transparent'
svg = pathlib.Path(src).read_text()
html = f'<html><body style="margin:0;background:{bg}"><div id=w style="width:{w}px;line-height:0">{svg}</div><style>svg{{width:100%;height:auto;display:block}}</style></body></html>'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': w, 'height': 100}); pg.set_content(html)
    pg.locator('#w').screenshot(path=out, omit_background=(bg == 'transparent')); b.close()
