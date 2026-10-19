import sys, time
from playwright.sync_api import sync_playwright
url, w = sys.argv[1], int(sys.argv[2])
JS = """window.__ls=[];new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__ls.push({v:e.value,t:Math.round(e.startTime),s:(e.sources||[]).map(s=>{const n=s.node;return n?(n.nodeName+'.'+(n.className||'').toString().slice(0,40)+' '+JSON.stringify(s.previousRect)+'→'+JSON.stringify(s.currentRect)):'?'})})}).observe({type:'layout-shift',buffered:true});"""
with sync_playwright() as p:
    b = p.chromium.launch(); c = b.new_context(viewport={'width': w, 'height': 864 if w > 800 else 844}); c.add_init_script(JS); pg = c.new_page()
    pg.goto(url, wait_until='networkidle'); time.sleep(.6)
    H = pg.evaluate('document.documentElement.scrollHeight')
    for y in range(0, H, 700):
        pg.evaluate(f'window.__lenis?window.__lenis.scrollTo({y},{{immediate:true}}):scrollTo(0,{y})'); time.sleep(.12)
    time.sleep(.5)
    for e in pg.evaluate('window.__ls'): print(round(e['v'], 4), e['t'], e['s'][:3])
    b.close()
