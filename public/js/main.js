/* Turismo Chiloé Mágico · interacción. Curva única expo-out; sin pin de ScrollTrigger. */
(() => {
  'use strict';
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const EASE = 'expo.out';
  const WA = '56978902625';

  /* ---------- idioma (solo interfaz; el contenido de la marca queda en su idioma) ---------- */
  const ATTRS = [['alt', 'data-alt-en'], ['aria-label', 'data-aria-en'], ['title', 'data-title-en']];
  const store = { get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} } };
  const titleEs = document.title;
  const metaDesc = $('meta[name="description"]');
  const descEs = metaDesc ? metaDesc.content : '';
  function applyLang(lang) {
    root.lang = lang;
    $$('[data-alt-en],[data-aria-en],[data-title-en]').forEach(el => {
      ATTRS.forEach(([a, d]) => {
        if (!el.hasAttribute(d) || (a === 'title' && el === root)) return;
        const keep = 'data-' + a.replace('-', '') + '-es';
        if (!el.hasAttribute(keep)) el.setAttribute(keep, el.getAttribute(a) || '');
        el.setAttribute(a, lang === 'en' ? el.getAttribute(d) : el.getAttribute(keep));
      });
    });
    document.title = lang === 'en' ? (root.dataset.titleEn || titleEs) : titleEs;
    if (metaDesc) metaDesc.content = lang === 'en' ? (metaDesc.dataset.metaEn || descEs) : descEs;
    if (window.__swipers) window.__swipers.forEach(s => s.__a11y && s.__a11y(lang));
  }
  if (root.lang === 'en') applyLang('en');
  $$('[data-lang-toggle]').forEach(b => b.addEventListener('click', () => {
    const next = root.lang === 'en' ? 'es' : 'en';
    store.set('cm-lang', next); applyLang(next);
  }));

  /* ---------- salto al contenido ---------- */
  $$('.skip').forEach(a => a.addEventListener('click', e => { e.preventDefault(); const m = $('#main'); m.focus({ preventScroll: true }); m.scrollIntoView(); }));

  /* ---------- fuentes: esperar con tiempo máximo ---------- */
  const fontsReady = Promise.race([
    Promise.allSettled(['400 1em Anton', '400 1em Montserrat', '600 1em Montserrat'].map(f => document.fonts ? document.fonts.load(f) : Promise.resolve())),
    new Promise(r => setTimeout(r, 1800)),
  ]);

  /* ---------- revelados de línea ---------- */
  const lineIO = 'IntersectionObserver' in window ? new IntersectionObserver(es => es.forEach(en => {
    if (en.isIntersecting) { en.target.classList.add('is-in'); lineIO.unobserve(en.target); }
  }), { rootMargin: '0px 0px -8% 0px' }) : null;
  fontsReady.then(() => $$('[data-lines]').forEach(el => (lineIO && !reduce.matches) ? lineIO.observe(el) : el.classList.add('is-in')));

  /* ---------- cabecera ---------- */
  const hdr = $('[data-hdr]');
  const menu = $('[data-menu]');
  let lastY = 0;
  function onScrollHdr(y) {
    if (!hdr) return;
    hdr.classList.toggle('is-solid', y > (document.body.classList.contains('home') ? innerHeight * .8 : 10));
    const d = y - lastY;
    if (Math.abs(d) < 6) return;
    hdr.classList.toggle('is-hidden', !(menu && !menu.hidden) && y > 400 && d > 0);
    lastY = y;
  }
  addEventListener('scroll', () => onScrollHdr(scrollY), { passive: true });
  onScrollHdr(scrollY);

  /* ---------- videos diferidos: póster y fuentes al acercarse ---------- */
  const vids = $$('video[data-lazy-video]');
  const loadVideo = v => {
    if (v.dataset.loaded) return; v.dataset.loaded = '1';
    if (v.dataset.poster) v.poster = v.dataset.poster;
    $$('source[data-src]', v).forEach(s => { s.src = s.dataset.src; });
    v.load();
  };
  if ('IntersectionObserver' in window) {
    const near = new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) { loadVideo(en.target); near.unobserve(en.target); } }), { rootMargin: '120% 0px' });
    const seen = new IntersectionObserver(es => es.forEach(en => {
      const v = en.target;
      if (en.isIntersecting && !reduce.matches) { const p = v.play(); if (p) p.catch(() => {}); } else v.pause();
    }), { threshold: .15 });
    vids.forEach(v => { near.observe(v); seen.observe(v); });
  } else vids.forEach(loadVideo);

  /* ---------- mapa diferido ---------- */
  $$('[data-map]').forEach(m => {
    const f = $('iframe', m);
    const io = new IntersectionObserver(es => { if (es[0].isIntersecting) { io.disconnect(); f.setAttribute('tabindex', '-1'); f.src = f.dataset.src; f.addEventListener('load', () => { m.classList.add('is-loaded'); f.removeAttribute('tabindex'); }, { once: true }); } }, { rootMargin: '60% 0px' });
    io.observe(m);
  });

  /* ---------- Swiper diferido ---------- */
  window.__swipers = [];
  let swiperP = null;
  function loadSwiper() {
    if (swiperP) return swiperP;
    swiperP = new Promise((res, rej) => {
      const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = '/vendor/swiper-bundle.min.css'; document.head.appendChild(l);
      const s = document.createElement('script'); s.src = '/vendor/swiper-bundle.min.js'; s.onload = () => res(window.Swiper); s.onerror = rej; document.head.appendChild(s);
    });
    return swiperP;
  }
  const A11Y = {
    es: { prevSlideMessage: 'Anterior', nextSlideMessage: 'Siguiente', firstSlideMessage: 'Primera', lastSlideMessage: 'Última', slideLabelMessage: '{{index}} de {{slidesLength}}', containerRoleDescriptionMessage: 'carrusel', itemRoleDescriptionMessage: 'diapositiva' },
    en: { prevSlideMessage: 'Previous', nextSlideMessage: 'Next', firstSlideMessage: 'First', lastSlideMessage: 'Last', slideLabelMessage: '{{index}} of {{slidesLength}}', containerRoleDescriptionMessage: 'carousel', itemRoleDescriptionMessage: 'slide' },
  };
  const nativeNav = el => { const sec = el.closest('section'); if (!sec) return;
    const step = d => el.scrollBy({ left: d * el.clientWidth * .8, behavior: 'auto' });
    const p = $('[data-prev]', sec), n = $('[data-next]', sec); if (p) p.onclick = () => step(-1); if (n) n.onclick = () => step(1); };
  function initSwiper(el) {
    if (el.swiper || reduce.matches) { el.classList.add('is-native'); nativeNav(el); return; }
    loadSwiper().then(Swiper => {
      const kind = el.dataset.swiper;
      const sec = el.closest('section');
      const opts = { slidesPerView: 'auto', spaceBetween: kind === 'gallery' ? 6 : 24, grabCursor: true, speed: 900, a11y: A11Y[root.lang === 'en' ? 'en' : 'es'], keyboard: { enabled: true, onlyInViewport: true }, freeMode: kind !== 'reviews' ? { enabled: true, momentumRatio: .6 } : false };
      if (kind === 'reviews' && sec) opts.navigation = { prevEl: $('[data-prev]', sec), nextEl: $('[data-next]', sec) };
      const sw = new Swiper(el, opts);
      sw.__a11y = lang => {
        const m = A11Y[lang]; Object.assign(sw.params.a11y, m);
        el.setAttribute('aria-roledescription', m.containerRoleDescriptionMessage);
        sw.slides.forEach((s, i) => { s.setAttribute('aria-roledescription', m.itemRoleDescriptionMessage); s.setAttribute('aria-label', m.slideLabelMessage.replace('{{index}}', i + 1).replace('{{slidesLength}}', sw.slides.length)); });
      };
      el.addEventListener('focusin', e => {
        el.scrollLeft = 0;
        const s = e.target.closest('.swiper-slide'); if (!s) return;
        const r = s.getBoundingClientRect(), c = { left: 8, right: innerWidth - 8 };
        if (r.left < c.left || r.right > c.right) sw.slideTo(sw.slides.indexOf(s), 0);
      });
      el.addEventListener('scroll', () => { if (el.scrollLeft) el.scrollLeft = 0; });
      window.__swipers.push(sw);
    }).catch(() => { el.classList.add('is-native'); nativeNav(el); });
  }
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) { io.unobserve(en.target); initSwiper(en.target); } }), { rootMargin: '80% 0px' });
    $$('[data-swiper]').forEach(el => io.observe(el));
  }

  /* ---------- etiqueta "Arrastrar" (sin ocultar el cursor) ---------- */
  if (fine.matches) {
    const tag = document.createElement('div');
    tag.className = 'js-drag-label'; tag.setAttribute('aria-hidden', 'true');
    tag.innerHTML = '<span data-l="es">Arrastrar</span><span data-l="en">Drag</span>';
    document.body.appendChild(tag);
    $$('[data-drag]').forEach(z => {
      z.addEventListener('pointerenter', () => tag.classList.add('is-on'));
      z.addEventListener('pointerleave', () => tag.classList.remove('is-on'));
      z.addEventListener('pointermove', e => { tag.style.left = e.clientX + 'px'; tag.style.top = e.clientY + 'px'; });
    });
  }

  /* ---------- experiencias: imagen al pasar ---------- */
  $$('[data-hover-zone]').forEach(zone => {
    const fl = $('.exps__float', zone); if (!fl || !fine.matches) return;
    let x = 0, y = 0, tx = 0, ty = 0, raf = 0;
    const loop = () => { x += (tx - x) * .18; y += (ty - y) * .18; fl.style.transform = `translate(${x}px,${y}px)`; raf = requestAnimationFrame(loop); };
    $$('[data-hover-img]', zone).forEach(a => {
      a.addEventListener('pointerenter', () => { $$('.exp__img', fl).forEach(i => i.classList.toggle('is-on', i.dataset.hoverKey === a.dataset.hoverImg)); fl.classList.add('is-on'); if (!raf) raf = requestAnimationFrame(loop); });
      a.addEventListener('pointermove', e => { tx = e.clientX + 24; ty = e.clientY - fl.offsetHeight / 2; });
    });
    $('.exps__list', zone).addEventListener('pointerleave', () => { fl.classList.remove('is-on'); cancelAnimationFrame(raf); raf = 0; });
  });

  /* ---------- destinos: el paisaje cambia con el destino elegido ---------- */
  $$('[data-dx]').forEach(sec => {
    const set = slug => {
      $$('[data-dx-bg]', sec).forEach(x => x.classList.toggle('is-on', x.dataset.dxBg === slug));
      $$('[data-dx-txt]', sec).forEach(x => x.classList.toggle('is-on', x.dataset.dxTxt === slug));
      $$('.dx__link', sec).forEach(x => x.classList.toggle('is-on', x.dataset.dx === slug));
    };
    $$('.dx__link', sec).forEach(a => { a.addEventListener('pointerenter', () => set(a.dataset.dx)); a.addEventListener('focus', () => set(a.dataset.dx)); });
  });

  /* ---------- formularios → WhatsApp ---------- */
  $$('[data-wa-form]').forEach(f => f.addEventListener('submit', e => {
    e.preventDefault();
    const d = new FormData(f);
    const parts = [];
    if (f.dataset.tour) parts.push(`Hola! Quiero reservar el ${f.dataset.tour}.`); else parts.push(`Hola! Consulta (${f.dataset.kind || 'web'}).`);
    if (d.get('nombre')) parts.push(`Nombre: ${d.get('nombre')}`);
    if (d.get('fecha')) parts.push(`Fecha: ${d.get('fecha')}`);
    if (d.get('personas')) parts.push(`Personas: ${d.get('personas')}`);
    if (d.get('mensaje')) parts.push(d.get('mensaje'));
    window.open(`https://wa.me/${WA}?text=${encodeURIComponent(parts.join('\n'))}`, '_blank', 'noopener');
  }));

  /* ---------- filtro de tours ---------- */
  const grid = $('[data-filter-grid]');
  if (grid) $$('[data-filter]').forEach(b => b.addEventListener('click', () => {
    $$('[data-filter]').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    const f = b.dataset.filter;
    $$('li', grid).forEach(li => li.classList.toggle('is-out', f !== 'all' && !li.dataset.exp.split(' ').includes(f)));
    if (window.ScrollTrigger) ScrollTrigger.refresh();
  }));

  /* ---------- barra móvil de reserva ---------- */
  const mbar = $('[data-mbar]'), book = $('.book');
  if (mbar && book) {
    const io = new IntersectionObserver(es => mbar.classList.toggle('is-on', !es[0].isIntersecting && es[0].boundingClientRect.top < 0), { threshold: 0 });
    io.observe(book);
  }

  /* ---------- menú (dialog accesible) ---------- */
  const openBtn = $('[data-menu-open]'), closeBtn = $('[data-menu-close]');
  let lastFocus = null;
  const outside = () => $$('body > *').filter(el => el !== menu && el.tagName !== 'SCRIPT');
  function openMenu() {
    lastFocus = menu.contains(document.activeElement) ? openBtn : document.activeElement; menu.hidden = false; openBtn.setAttribute('aria-expanded', 'true');
    outside().forEach(el => el.inert = true);
    document.body.style.overflow = 'hidden'; window.__lenis && window.__lenis.stop();
    if (window.gsap && !reduce.matches) { gsap.killTweensOf([menu, '.menu__link']); gsap.fromTo(menu, { clipPath: 'inset(0 0 100% 0)' }, { clipPath: 'inset(0 0 0% 0)', duration: .9, ease: EASE }); gsap.fromTo('.menu__link', { yPercent: 60, opacity: 0 }, { yPercent: 0, opacity: 1, duration: .9, ease: EASE, stagger: .04, delay: .15 }); }
    closeBtn.focus();
  }
  function closeMenu() {
    const done = () => { menu.hidden = true; openBtn.setAttribute('aria-expanded', 'false'); outside().forEach(el => el.inert = false); document.body.style.overflow = ''; window.__lenis && window.__lenis.start(); lastFocus && lastFocus.focus(); };
    if (window.gsap && !reduce.matches) { gsap.killTweensOf([menu, '.menu__link']); gsap.to(menu, { clipPath: 'inset(0 0 100% 0)', duration: .6, ease: 'expo.inOut', onComplete: done }); } else done();
  }
  if (menu) {
    openBtn.addEventListener('click', openMenu); closeBtn.addEventListener('click', closeMenu);
    menu.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeMenu();
      if (e.key === 'Tab') { const f = $$('a,button', menu).filter(x => x.offsetParent); const a = f[0], z = f[f.length - 1]; if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); } else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); } }
    });
    $$('[data-menu-img]', menu).forEach(a => { const on = () => $$('.menu__img', menu).forEach(i => i.classList.toggle('is-on', i.dataset.menuKey === a.dataset.menuImg)); a.addEventListener('pointerenter', on); a.addEventListener('focus', on); });
    const first = $('.menu__img', menu); first && first.classList.add('is-on');
  }

  /* ---------- botones magnéticos ---------- */
  if (fine.matches && !reduce.matches) $$('[data-magnetic]').forEach(b => {
    b.addEventListener('pointermove', e => { const r = b.getBoundingClientRect(); b.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * .18}px,${(e.clientY - r.top - r.height / 2) * .28}px)`; });
    b.addEventListener('pointerleave', () => { b.style.transform = ''; });
  });

  /* ---------- conservar lo que se está leyendo al cambiar el ancho ---------- */
  let anchor = null, anchorTop = 0, rzRaf = 0, remT = 0;
  const remember = () => {
    if (menu && !menu.hidden) return;
    const hit = document.elementFromPoint(innerWidth / 2, innerHeight * .35);
    const el = hit && hit.closest('main p, main li, main h1, main h2, main h3, main figure, main section, main article, footer');
    if (el) { anchor = el; anchorTop = el.getBoundingClientRect().top; }
  };
  function restore() {
    if (!anchor || !anchor.isConnected) return;
    const y = Math.max(0, scrollY + anchor.getBoundingClientRect().top - anchorTop);
    window.__lenis ? window.__lenis.scrollTo(y, { immediate: true, force: true }) : scrollTo(0, y);
  }
  addEventListener('scroll', () => { clearTimeout(remT); remT = setTimeout(remember, 150); }, { passive: true });
  remember();
  addEventListener('resize', () => { cancelAnimationFrame(rzRaf); rzRaf = requestAnimationFrame(() => { if (!window.ScrollTrigger) restore(); }); });

  /* ---------- GSAP + Lenis ---------- */
  window.addEventListener('load', () => {
    if (!window.gsap || !window.ScrollTrigger) return;
    gsap.registerPlugin(ScrollTrigger);
    if (!reduce.matches && window.Lenis) {
      const lenis = new Lenis({ duration: 1.15, easing: t => 1 - Math.pow(2, -10 * t), smoothWheel: true });
      window.__lenis = lenis;
      lenis.on('scroll', () => ScrollTrigger.update());
      gsap.ticker.add(t => lenis.raf(t * 1000)); gsap.ticker.lagSmoothing(0);
      $$('a[href^="#"]').forEach(a => a.addEventListener('click', e => { const t = $(a.getAttribute('href')); if (t && !a.classList.contains('skip')) { e.preventDefault(); lenis.scrollTo(t, { offset: -80 }); } }));
    }
    const mm = gsap.matchMedia();
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      const hero = $('[data-parallax-hero]');
      if (hero) gsap.to(hero, { yPercent: 12, scale: 1.06, ease: 'none', scrollTrigger: { trigger: '[data-hero]', start: 'top top', end: 'bottom top', scrub: true } });
      $$('[data-parallax] img').forEach(img => gsap.fromTo(img, { yPercent: -5 }, { yPercent: 5, ease: 'none', scrollTrigger: { trigger: img.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } }));
      $$('[data-card]').forEach((c, i) => gsap.from(c, { y: 60 + (i % 3) * 30, opacity: 0, duration: 1.2, ease: EASE, scrollTrigger: { trigger: c, start: 'top 92%', once: true } }));
      /* tours: paneles a pantalla completa que avanzan en horizontal (sticky + transform, sin pin) */
      const hs = $('[data-htours]');
      if (hs && matchMedia('(min-width: 761px)').matches) {
        const track = $('[data-htrack]', hs), bar = $('[data-hbar]', hs);
        hs.classList.add('is-h');
        const dist = () => Math.max(0, track.scrollWidth - innerWidth);
        const setH = () => { hs.style.height = (dist() + innerHeight) + 'px'; };
        setH(); ScrollTrigger.addEventListener('refreshInit', setH);
        const tw = gsap.to(track, { x: () => -dist(), ease: 'none', scrollTrigger: { trigger: hs, start: 'top top', end: 'bottom bottom', scrub: .6, invalidateOnRefresh: true, onUpdate: st => { if (bar) bar.style.transform = `scaleX(${st.progress})`; } } });
        $$('[data-tpanel-media]', hs).forEach(m => gsap.fromTo(m, { xPercent: 5 }, { xPercent: -5, ease: 'none', scrollTrigger: { trigger: m.parentElement, containerAnimation: tw, start: 'left right', end: 'right left', scrub: true } }));
        hs.addEventListener('focusin', e => {
          const p = e.target.closest('.tpanel'); if (!p) return;
          const y = hs.getBoundingClientRect().top + scrollY + p.offsetLeft;
          window.__lenis ? window.__lenis.scrollTo(y, { immediate: true }) : scrollTo(0, y);
        });
        ScrollTrigger.refresh();
      }
      /* el momento: la isla se abre */
      const isla = $('[data-isla]');
      if (isla) {
        const win = $('[data-isla-win]', isla);
        const tl = gsap.timeline({ scrollTrigger: { trigger: isla, start: 'top top', end: 'bottom bottom', scrub: 1, invalidateOnRefresh: true } });
        tl.fromTo(win, { scale: .62, rotate: -6 }, { scale: () => Math.max(innerWidth * .75 / win.offsetWidth, 1.2), rotate: 0, ease: 'power2.in' }, 0)
          .fromTo('.isla__bg span', { yPercent: 30, opacity: .2 }, { yPercent: -30, opacity: 1, stagger: .05, ease: 'none' }, 0)
          .to('.isla__q', { opacity: 0, y: -40, ease: 'none', duration: .3 }, .55);
      }
      return () => {};
    });
    ScrollTrigger.addEventListener('refreshInit', () => onScrollHdr(scrollY));
    ScrollTrigger.addEventListener('refresh', restore);
  });
})();
