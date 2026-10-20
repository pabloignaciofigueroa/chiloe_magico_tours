// Capturas del sitio para el dossier. Sirve public/ en :8765 antes de ejecutar.
const { chromium } = require('playwright');
const OUT = __dirname + '/shots/';
const B = 'http://localhost:8765';
// [clave, ruta, selector, modo, x]
const S = [
  ['hero', '/', '.hero', 'top'],
  ['isla-a', '/', '.isla', 'frac', 0.08],
  ['isla-b', '/', '.isla', 'frac', 0.96],
  ['tours', '/', '.tsec', 'offset', 0.0],
  ['reviews', '/', '.rsec', 'center'],
  ['bcta', '/', '.bcta', 'center'],
  ['foot', '/', '.ftr', 'bottom'],
  ['tlist', '/tours/', '.phead2', 'top'],
  ['tlist2', '/tours/', '.tsec', 'offset', 0.12],
  ['ficha', '/tours/la-costa-curanto/', '.th', 'top'],
  ['ficha-info', '/tours/la-costa-curanto/', '.tw', 'offset', -0.12],
  ['ficha-fotos', '/tours/la-costa-curanto/', '.tfotos', 'offset', 0.0],
  ['ficha-cot', '/tours/la-costa-curanto/', '.tcot', 'center'],
  ['paquetes', '/paquetes/', '.bhero', 'top'],
  ['paquetes2', '/paquetes/', '.ssplit', 'offset', 0.0],
  ['nosotros', '/nosotros/', '.bhero', 'top'],
  ['nosotros2', '/nosotros/', '.ssplit', 'offset', 0.0],
  ['servicios', '/servicios/', '.bhero', 'top'],
  ['faq', '/preguntas-frecuentes/', '.sec', 'offset', 0.0],
  ['contacto', '/contacto/', '.bhero', 'top'],
  ['contacto2', '/contacto/', '.sec', 'offset', 0.0],
  ['destinos', '/destinos/', '.bhero', 'top'],
  ['destinos2', '/destinos/', '.tgrid', 'offset', 0.0],
  ['experiencias', '/experiencias/', '.bhero', 'top'],
  ['experiencias2', '/experiencias/', '.tgrid', 'offset', 0.0],
  ['guia', '/guia/', '.bhero', 'top'],
  ['guia2', '/guia/', '.tgrid', 'offset', 0.0],
  ['guia-art', '/guia/que-es-el-curanto/', '.bhero', 'top'],
];
async function shoot(ctx, vh, prefix, list) {
  const p = await ctx.newPage();
  let cur = '';
  for (const [k, path, sel, mode, x] of list) {
    if (path !== cur) { await p.goto(B + path, { waitUntil: 'load' }); await p.waitForTimeout(1500); cur = path; }
    const y = await p.evaluate(([sel, mode, x, vh]) => {
      const e = document.querySelector(sel); if (!e) return -1;
      const top = e.getBoundingClientRect().top + scrollY, h = e.offsetHeight;
      if (mode === 'top') return top; if (mode === 'frac') return top + (h - vh) * x;
      if (mode === 'offset') return top + h * x; if (mode === 'bottom') return top + h - vh;
      return top + (h - vh) / 2;
    }, [sel, mode, x, vh]);
    if (y < 0) { console.log('falta', k, sel); continue; }
    await p.evaluate(y => scrollTo(0, y), Math.max(0, y)); await p.waitForTimeout(400);
    await p.evaluate(y => scrollTo(0, y), Math.max(0, y) + 1); await p.waitForTimeout(2600);
    await p.evaluate(() => { const n = document.querySelector('[data-hdr]'); n && n.classList.remove('is-hidden'); });
    await p.waitForTimeout(500);
    await p.screenshot({ path: `${OUT}${prefix}-${k}.jpg`, type: 'jpeg', quality: 84 });
  }
  await p.close();
}
(async () => {
  const b = await chromium.launch();
  const c = await b.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.5, locale: 'es-CL' });
  await shoot(c, 900, 'd', S);
  // menú abierto
  const p = await c.newPage(); await p.setViewportSize({ width: 1000, height: 900 });
  await p.goto(B + '/tours/'); await p.waitForTimeout(1500);
  await p.click('[data-menu-open]'); await p.waitForTimeout(1500);
  await p.hover('[data-menu-img="nicolas-enrique"]'); await p.waitForTimeout(1200);
  await p.screenshot({ path: OUT + 'd-menu.jpg', type: 'jpeg', quality: 84 });
  // versión en inglés
  await p.keyboard.press('Escape'); await p.waitForTimeout(500);
  await p.goto(B + '/'); await p.waitForTimeout(1200);
  await p.setViewportSize({ width: 1440, height: 900 });
  await p.click('[data-lang-toggle]'); await p.waitForTimeout(1500);
  await p.evaluate(() => { const e = document.querySelector('.tsec'); scrollTo(0, e.getBoundingClientRect().top + scrollY); });
  await p.waitForTimeout(400); await p.evaluate(() => scrollBy(0, 1)); await p.waitForTimeout(2600);
  await p.screenshot({ path: OUT + 'd-en.jpg', type: 'jpeg', quality: 84 });
  await c.close();
  const m = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2.5, isMobile: true, hasTouch: true, locale: 'es-CL' });
  await shoot(m, 844, 'm', S.filter(s => !['isla-a'].includes(s[0])));
  await b.close();
})();
