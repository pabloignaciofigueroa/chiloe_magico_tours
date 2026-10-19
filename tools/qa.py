"""Fase 18: QA sirviendo public/ (8765) contra la raíz (8766).
Para cada página: 4xx, errores JS, alto, desborde horizontal y CLS (carga + recorrido)."""
import sys, time, json, pathlib
from playwright.sync_api import sync_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
pages = ['/'] + sorted('/' + p.parent.relative_to(ROOT / 'public').as_posix() + '/' for p in (ROOT / 'public').rglob('index.html') if p.parent != ROOT / 'public')
widths = [int(w) for w in (sys.argv[1].split(',') if len(sys.argv) > 1 else ['1536', '390'])]
CLS_JS = """window.__cls=0;new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__cls+=e.value}).observe({type:'layout-shift',buffered:true});"""
fail = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for w in widths:
        ctx = b.new_context(viewport={'width': w, 'height': 864 if w > 800 else 844})
        ctx.add_init_script(CLS_JS)
        for path in pages:
            res = {}
            for port in (8765, 8766):
                pg = ctx.new_page(); errs = []; bad = []
                pg.on('pageerror', lambda e: errs.append(str(e)))
                pg.on('response', lambda r: r.status >= 400 and bad.append(f'{r.status} {r.url}'))
                pg.goto(f'http://localhost:{port}{path}', wait_until='networkidle'); time.sleep(.6)
                H = pg.evaluate('document.documentElement.scrollHeight')
                for y in range(0, H, 700):
                    pg.evaluate(f'window.__lenis?window.__lenis.scrollTo({y},{{immediate:true}}):scrollTo(0,{y})'); time.sleep(.12)
                time.sleep(.5)
                ov = pg.evaluate('document.documentElement.scrollWidth - innerWidth')
                res[port] = dict(H=H, cls=round(pg.evaluate('window.__cls'), 4), errs=errs, bad=[x for x in bad if 'openstreetmap' not in x], ov=ov)
                pg.close()
            a, r = res[8765], res[8766]
            issues = []
            if a['bad']: issues.append('4xx ' + ', '.join(a['bad'][:3]))
            if a['errs']: issues.append('JS ' + '; '.join(a['errs'][:2]))
            if abs(a['H'] - r['H']) > 2: issues.append(f'alto {a["H"]} vs raíz {r["H"]}')
            if a['ov'] > 0: issues.append(f'desborde {a["ov"]}px')
            if a['cls'] >= 0.01: issues.append(f'CLS {a["cls"]}')
            print(f'{w:>5} {path:<40} H={a["H"]:<6} CLS={a["cls"]:<7} ' + ('OK' if not issues else '✗ ' + ' | '.join(issues)))
            if issues: fail.append((w, path, issues))
        ctx.close()
    b.close()
print('\nFALLAS:', len(fail))
sys.exit(1 if fail else 0)
