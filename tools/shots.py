"""Capturas de QA: python3 tools/shots.py URL salida_prefijo ancho alto [pasos]"""
import sys, time
from playwright.sync_api import sync_playwright
url, out, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]); steps = int(sys.argv[5]) if len(sys.argv) > 5 else 8
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': w, 'height': h})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
    bad = []; pg.on('response', lambda r: r.status >= 400 and bad.append(f'{r.status} {r.url}'))
    pg.goto(url, wait_until='networkidle'); time.sleep(1.5)
    H = pg.evaluate('document.documentElement.scrollHeight'); print('alto', H)
    for i in range(steps):
        y = int(i * (H - h) / max(1, steps - 1))
        pg.mouse.wheel(0, 0); pg.evaluate(f'window.__lenis ? window.__lenis.scrollTo({y}, {{immediate:true}}) : scrollTo(0,{y})'); time.sleep(1.4)
        pg.screenshot(path=f'{out}_{i:02d}.jpg', type='jpeg', quality=70)
    print('errores', errs[:10]); print('4xx', bad[:10]); b.close()
