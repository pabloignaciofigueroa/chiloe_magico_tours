const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1248, height: 816 } });
  await p.goto('file://' + __dirname + '/chiloemagico-dossier-diseno.html', { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const over = await p.evaluate(() => [...document.querySelectorAll('.lam')].map((l, i) => {
    const L = l.getBoundingClientRect(); const bad = [];
    l.querySelectorAll('.tx').forEach(t => { const r = t.getBoundingClientRect();
      if (r.bottom > L.bottom - 18 || r.right > L.right - 10) bad.push((t.innerText || '').slice(0, 30)); });
    return bad.length ? (i + 1) + ':' + bad.join(' | ') : null; }).filter(Boolean));
  console.log('overflow', JSON.stringify(over));
  await p.pdf({ path: __dirname + '/chiloemagico-dossier-diseno.pdf', width: '13in', height: '8.5in', printBackground: true });
  const lams = await p.$$('.lam');
  for (let i = 0; i < lams.length; i++) await lams[i].screenshot({ path: `${__dirname}/pages/p-${String(i + 1).padStart(2, '0')}.png` });
  await b.close();
})();
