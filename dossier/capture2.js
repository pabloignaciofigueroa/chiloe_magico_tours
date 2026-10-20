// Ajustes finos: recaptura con desplazamiento dy en px
const { chromium } = require('playwright');
const OUT = __dirname + '/shots/', B = 'http://localhost:8765';
const S = [['tours', '/', '.tsec', 95], ['reviews', '/', '.rsec', -60]];
(async () => {
  const b = await chromium.launch();
  const c = await b.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.5, locale: 'es-CL' });
  const p = await c.newPage(); await p.goto(B + '/'); await p.waitForTimeout(1500);
  for (const [k, path, sel, dy] of S) {
    const y = await p.evaluate(s => document.querySelector(s).getBoundingClientRect().top + scrollY, sel);
    await p.evaluate(y => scrollTo(0, y), y + dy); await p.waitForTimeout(400);
    await p.evaluate(() => scrollBy(0, 1)); await p.waitForTimeout(2600);
    await p.evaluate(() => { const n = document.querySelector('[data-hdr]'); n && n.classList.remove('is-hidden'); });
    await p.waitForTimeout(500);
    await p.screenshot({ path: `${OUT}d-${k}.jpg`, type: 'jpeg', quality: 84 });
  }
  await b.close();
})();
