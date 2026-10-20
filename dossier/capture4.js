// Ajuste fino en celular: «Elige tu tour» con su título entero
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const m = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2.5, isMobile: true, hasTouch: true, locale: 'es-CL' });
  const q = await m.newPage(); await q.goto('http://localhost:8765/'); await q.waitForTimeout(1500);
  const y = await q.evaluate(() => document.querySelector('.tsec').getBoundingClientRect().top + scrollY);
  await q.evaluate(y => scrollTo(0, y), y - 70); await q.waitForTimeout(400);
  await q.evaluate(() => scrollBy(0, 1)); await q.waitForTimeout(2600);
  await q.evaluate(() => document.querySelector('[data-hdr]').classList.remove('is-hidden'));
  await q.waitForTimeout(500);
  await q.screenshot({ path: __dirname + '/shots/m-tours.jpg', type: 'jpeg', quality: 84 });
  await b.close();
})();
