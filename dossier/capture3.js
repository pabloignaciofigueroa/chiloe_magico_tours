// La isla recién abriéndose, con el cuadro del video visible (en captura sin reproducción)
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const c = await b.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1.5, locale: 'es-CL' });
  const p = await c.newPage(); await p.goto('http://localhost:8765/'); await p.waitForTimeout(1500);
  await p.evaluate(() => { const v = document.querySelector('.isla__v'); v.poster = v.dataset.poster; });
  const y = await p.evaluate(() => { const e = document.querySelector('.isla'); return e.getBoundingClientRect().top + scrollY + (e.offsetHeight - 900) * 0.12; });
  await p.evaluate(y => scrollTo(0, y), y); await p.waitForTimeout(400);
  await p.evaluate(() => scrollBy(0, 1)); await p.waitForTimeout(2600);
  await p.evaluate(() => document.querySelector('[data-hdr]').classList.remove('is-hidden'));
  await p.waitForTimeout(500);
  await p.screenshot({ path: __dirname + '/shots/d-isla-a.jpg', type: 'jpeg', quality: 84 });
  await b.close();
})();
