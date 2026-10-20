const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1248, height: 816 } });
  await p.goto('file://' + __dirname + '/chiloemagico-dossier-diseno.html', { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const over = await p.evaluate(() => [...document.querySelectorAll('.R,.L')].map((e, i) => {
    const r = e.getBoundingClientRect(); const bad = [];
    e.querySelectorAll('*').forEach(c => { if (c.closest('.pf')) return; const q = c.getBoundingClientRect();
      if (q.height && q.bottom > r.bottom - (e.classList.contains('R') ? 40 : 0) + 1) bad.push(c.className || c.tagName); });
    return bad.length ? Math.floor(i / 2) + 1 + ':' + bad.slice(0, 3).join(',') : null; }).filter(Boolean));
  console.log('overflow', JSON.stringify(over));
  await p.pdf({ path: __dirname + '/chiloemagico-dossier-diseno.pdf', width: '13in', height: '8.5in', printBackground: true });
  const lams = await p.$$('.lam');
  for (let i = 0; i < lams.length; i++) await lams[i].screenshot({ path: `${__dirname}/pages/p-${String(i + 1).padStart(2, '0')}.png` });
  await b.close();
})();
