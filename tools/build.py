#!/usr/bin/env python3
"""Genera el sitio (index.html + carpetas de páginas) desde src/layout.html y content/site.py.

- Cada imagen sale con srcset, width/height, LQIP y data-alt-en. Falla si falta un alt en inglés.
- Todo texto de la marca se escribe tal cual (idioma original); la interfaz va en pares data-l es/en.
- Escribe content/copy.md con cada texto y su fuente.
Uso: python3 tools/build.py
"""
import html, json, pathlib, re, shutil, sys, importlib.util

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('site_data', ROOT / 'content/site.py')
D = importlib.util.module_from_spec(spec); spec.loader.exec_module(D)
Q, U, SITE = D.Q, D.U, D.SITE
META = json.loads((ROOT / 'assets/img/meta.json').read_text())
ALT_EN = json.loads((ROOT / 'tools/alt-en.json').read_text())
LAYOUT = (ROOT / 'src/layout.html').read_text()
DOMAIN = SITE['domain']
TOURS = {t['slug']: t for t in D.TOURS}
DEST = {d['slug']: d for d in D.DESTINOS}
EXP = {e['slug']: e for e in D.EXPERIENCIAS}
COPY = []          # (página, texto, fuente, corrección)
PAGES = []         # rutas generadas
MISSING_ALT = []
e = html.escape


# ------------------------------------------------------------------ utilidades
def L(es, en=None, tag='span'):
    """Texto de interfaz bilingüe."""
    if isinstance(es, U):
        es, en = es.es, es.en
    return f'<{tag} data-l="es">{es}</{tag}><{tag} data-l="en">{en}</{tag}>'


EMOJI = re.compile('[\U0001F000-\U0001FAFF\u2600-\u2604\u2606-\u27BF\u2B00-\u2BFF\uFE0F\u200D\u20E3\u2190-\u21FF\u2300-\u23FF]')


def noemoji(t):
    t = EMOJI.sub('', t)
    t = re.sub(r'[ \t]{2,}', ' ', t)
    t = re.sub(r' +([,.!?;:…])', r'\1', t)
    return t.strip()


def q(text, page, tag=None, cls='', lang='es'):
    """Texto de la marca (literal, sin emojis). Registra su fuente para copy.md."""
    clean = noemoji(str(text))
    if isinstance(text, Q):
        fix = text.fix
        if clean != str(text).strip():
            fix = (fix + '; ' if fix else '') + 'sin emojis'
        COPY.append((page, clean, text.src, fix))
    s = e(clean)
    if tag:
        c = f' class="{cls}"' if cls else ''
        return f'<{tag}{c} lang="{lang}">{s}</{tag}>'
    return s


def img(key, sizes='100vw', cls='', eager=False, extra=''):
    m = META[key]
    en = ALT_EN.get(key)
    if not en:
        MISSING_ALT.append(key)
    s800 = f'/assets/img/{key}-800.webp'
    srcset = f'{s800} {min(800, m["w"]) if not m["big"] else 800}w'
    src = s800
    if m['big']:
        srcset += f', /assets/img/{key}-1800.webp {m["w"]}w'
        src = f'/assets/img/{key}-1800.webp' if eager else s800
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img class="{cls}" src="{src}" srcset="{srcset}" sizes="{sizes}" width="{m["w"]}" height="{m["h"]}" '
            f'alt="{e(m["alt"])}" data-alt-en="{e(en or "")}" {load} decoding="async" '
            f'style="background-image:url({m["lqip"]})" {extra}>')


def media(key, sizes='100vw', cls='', eager=False, ratio=None, parallax=False):
    r = f' style="--ar:{ratio}"' if ratio else ''
    p = ' data-parallax' if parallax else ''
    return f'<div class="media {cls}"{r}{p}>{img(key, sizes, "", eager)}</div>'


def wa_link(text):
    from urllib.parse import quote
    return f'https://wa.me/{SITE["wa"]}?text={quote(text)}'


def btn(label, href, cls='btn', ext=False, aria=None):
    t = ' target="_blank" rel="noopener"' if ext else ''
    a = f' aria-label="{e(aria.es)}" data-aria-en="{e(aria.en)}"' if aria else ''
    return f'<a class="{cls}" href="{href}"{t}{a} data-magnetic><span class="btn__in">{label}</span></a>'


def pending(page):
    return f'<p class="pending"><span class="pending__dot" aria-hidden="true"></span>{L(D.PENDING)}</p>'


def title_afiche(parts, page, tag='h1', cls='afiche'):
    a, s, b = parts
    COPY.append((page, f'{a} {s} {b}', '[DEST-H7] títulos de afiche', None))
    return (f'<{tag} class="{cls}" lang="es" data-lines><span class="line"><span>{e(a)}</span></span>'
            f'<span class="line line--script"><span>{e(s)}</span></span>'
            f'<span class="line"><span>{e(b)}</span></span></{tag}>')


def clp(n):
    return '$' + f'{n:,}'.replace(',', '.')


def tour_href(t): return f'/tours/{t["slug"]}/'
def dest_href(d): return f'/destinos/{d["slug"]}/'
def exp_href(x): return f'/experiencias/{x["slug"]}/'


NAV = [
    ('/tours/', U('Tours', 'Tours'), 'punihuil-bahia'),
    ('/destinos/', U('Destinos', 'Destinations'), 'tenaun-aereo'),
    ('/experiencias/', U('Experiencias', 'Experiences'), 'curanto-destape'),
    ('/paquetes/', U('Paquetes', 'Packages'), 'valdivia'),
    ('/servicios/', U('Servicios', 'Services'), 'vans'),
    ('/nosotros/', U('Nosotros', 'About us'), 'nicolas-enrique'),
    ('/guia/', U('Guía de Chiloé', 'Chiloé guide'), 'brujos-alas'),
    ('/contacto/', U('Contacto', 'Contact'), 'palafitos'),
]


def header(current, wa_text):
    links = ''.join(f'<li><a href="{h}"{" aria-current=page" if current.startswith(h) else ""}>{L(lbl)}</a></li>' for h, lbl, _ in NAV[:7])
    menu_links = ''.join(
        f'<li><a href="{h}" data-menu-img="{k}" class="menu__link"><span class="menu__n">0{i+1}</span>{L(lbl)}</a></li>'
        for i, (h, lbl, k) in enumerate(NAV))
    menu_imgs = ''.join(f'<div class="menu__img" data-menu-key="{k}">{img(k, "40vw")}</div>' for _, _, k in NAV)
    return f'''<header class="hdr" data-hdr>
  <a class="hdr__logo" href="/" aria-label="Turismo Chiloé Mágico, inicio" data-aria-en="Turismo Chiloé Mágico, home">
    <img src="/brand/logo/logotipo-h-color.svg" width="1632" height="340" alt="" class="hdr__logo-c">
    <img src="/brand/logo/logotipo-h-white.svg" width="1632" height="340" alt="" class="hdr__logo-w">
  </a>
  <nav class="hdr__nav" aria-label="Principal" data-aria-en="Main"><ul>{links}</ul></nav>
  <div class="hdr__tools">
    <button class="lang" type="button" data-lang-toggle><span class="sr">{L("Idioma:", "Language:")} </span><span class="lang__es" lang="es">ES</span><span class="lang__sep" aria-hidden="true">·</span><span class="lang__en" lang="en">EN</span></button>
    {btn(L("Reservar", "Book"), wa_link(wa_text), "btn btn--sm btn--red hdr__cta", True)}
    <button class="burger" type="button" data-menu-open aria-expanded="false" aria-haspopup="dialog" aria-controls="menu" aria-label="Abrir menú" data-aria-en="Open menu"><span></span><span></span></button>
  </div>
</header>
<div class="menu" id="menu" role="dialog" aria-modal="true" aria-label="Menú" data-aria-en="Menu" hidden data-menu>
  <button class="menu__close" type="button" data-menu-close>{L("Cerrar", "Close")}</button>
  <div class="menu__grid">
    <ul class="menu__list">{menu_links}</ul>
    <div class="menu__media" aria-hidden="true">{menu_imgs}</div>
  </div>
  <div class="menu__foot">
    <a href="{wa_link('Hola! Quiero consultar por los tours')}" target="_blank" rel="noopener">WhatsApp {SITE["wa_display"]}</a>
    <a href="{SITE["instagram"]}" target="_blank" rel="noopener">Instagram @chiloemagicotour</a>
  </div>
</div>'''


def footer(page):
    tl = ''.join(f'<li><a href="{tour_href(t)}">{e(t["short"])}</a></li>' for t in D.TOURS)
    nav = ''.join(f'<li><a href="{h}">{L(lbl)}</a></li>' for h, lbl, _ in NAV)
    return f'''<footer class="ftr">
  <svg class="ftr__wave" viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true"><path d="M0,120 L0,70 C360,10 820,0 1440,58 L1440,120 Z"/></svg>
  <div class="ftr__in">
    <div class="ftr__brand">
      <img src="/brand/logo/logo-sticker.svg" width="1912" height="1065" alt="Turismo Chiloé Mágico" data-alt-en="Turismo Chiloé Mágico" loading="lazy" class="ftr__logo">
      <p class="ftr__slogan script" lang="es">{q(SITE["slogan"], page)}</p>
    </div>
    <div class="ftr__cols">
      <div><h2 class="ftr__h">{L("Tours", "Tours")}</h2><ul>{tl}</ul></div>
      <div><h2 class="ftr__h">{L("Sitio", "Site")}</h2><ul>{nav}<li><a href="/preguntas-frecuentes/">{L("Preguntas frecuentes", "FAQ")}</a></li></ul></div>
      <div><h2 class="ftr__h">{L("Visítanos", "Visit us")}</h2>
        <p lang="es">{q(SITE["address"], page)}</p>
        <p lang="es">{q(SITE["hours"], page)}</p>
        <p><a href="{wa_link('Hola! Quiero consultar por los tours')}" target="_blank" rel="noopener">WhatsApp {SITE["wa_display"]}</a><br>
        <a href="tel:+56998833946">{SITE["phone2"]}</a><br>
        <a href="mailto:{SITE["email"]}">{SITE["email"]}</a><br>
        <a href="{SITE["instagram"]}" target="_blank" rel="noopener">Instagram @chiloemagicotour</a></p>
      </div>
    </div>
  </div>
  <div class="ftr__base">
    <p>© Turismo Chiloé Mágico · Castro, Chiloé</p>
    <p>{L("Pagos, sellos y políticas: por confirmar con la agencia.", "Payments, certifications and policies: to be confirmed with the agency.")}</p>
  </div>
  <svg class="ftr__gull" viewBox="0 0 100 100" aria-hidden="true"><path d="M4,4 C22,16 42,36 56,55 C62,53 70,52 78,53 C82,53.5 85,55 86,57 C83,59 79,60 75,61 C82,72 90,85 97,98 C86,88 75,76 66,65 C58,66 50,67 44,69 C47,66 50,63 52,61 C40,42 22,20 4,4 Z"/></svg>
</footer>'''


def wa_float(text):
    return (f'<aside aria-label="WhatsApp"><a class="wa" href="{wa_link(text)}" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp" data-aria-en="Message us on WhatsApp">'
            '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3a13 13 0 0 0-11.2 19.6L3 29l6.6-1.7A13 13 0 1 0 16 3zm0 23.6c-2 0-4-.6-5.7-1.6l-.4-.2-3.9 1 1-3.8-.3-.4A10.6 10.6 0 1 1 16 26.6zm5.8-7.9c-.3-.2-1.9-.9-2.2-1-.3-.1-.5-.2-.7.2l-1 1.2c-.2.2-.4.2-.7.1-.3-.2-1.4-.5-2.6-1.6-1-.9-1.6-1.9-1.8-2.2-.2-.3 0-.5.1-.7l.5-.6.3-.5c.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.2 1.4 3.5c.2.2 2.4 3.6 5.7 5 .8.4 1.4.6 1.9.7.8.3 1.5.2 2.1.1.6-.1 1.9-.8 2.2-1.5.3-.7.3-1.4.2-1.5l-.7-.4z"/></svg>'
            f'<span class="wa__t">{L("Escríbenos", "Message us")}</span></a></aside>')


def ld_business():
    return {"@context": "https://schema.org", "@type": "TravelAgency", "name": SITE['name'], "url": DOMAIN + '/',
            "image": DOMAIN + '/assets/og.jpg', "logo": DOMAIN + '/brand/logo/logo-color.png', "telephone": '+' + SITE['wa'],
            "email": SITE['email'], "address": {"@type": "PostalAddress", "streetAddress": "Av. Gamboa 351, Galería Alonso de Ercilla, Local Interior 116",
            "addressLocality": "Castro", "addressRegion": "Los Lagos", "addressCountry": "CL"},
            "geo": {"@type": "GeoCoordinates", "latitude": SITE['lat'], "longitude": SITE['lng']},
            "openingHours": "Mo-Su 09:00-19:30", "sameAs": [SITE['instagram']],
            "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.9", "reviewCount": SITE['reviews_count']}}


def page(path, title, title_en, desc, desc_en, content, body_class='', wa_text='Hola! Quiero consultar por los tours', ld=None, preload=''):
    PAGES.append(path)
    url = DOMAIN + path
    out = LAYOUT
    import hashlib
    for rel in ('css/main.css', 'js/main.js'):
        v = hashlib.sha1((ROOT / rel).read_bytes()).hexdigest()[:10]
        out = out.replace(f'"/{rel}"', f'"/{rel}?v={v}"')
    rep = {'title': e(title), 'title_en': e(title_en), 'desc': e(desc), 'desc_en': e(desc_en), 'url': url, 'domain': DOMAIN,
           'jsonld': json.dumps(ld or ld_business(), ensure_ascii=False).replace('</', '<\\/'), 'body_class': body_class,
           'header': header(path, wa_text), 'footer': footer(path), 'wa': wa_float(wa_text), 'content': content, 'preload': preload}
    for k, v in rep.items():
        out = out.replace('{{' + k + '}}', v)
    dest = ROOT / (path.strip('/') + '/index.html' if path != '/' else 'index.html')
    dest.parent.mkdir(parents=True, exist_ok=True)
    # ningún emoji en pantalla (las estrellas de valoración se quedan)
    out = re.sub(r' ?[\U0001F000-\U0001FAFF\u2600-\u2604\u2606-\u27BF\uFE0F]+', '', out)
    dest.write_text(out)


def preload_img(key):
    m = META[key]
    if m['big']:
        return (f'<link rel="preload" as="image" href="/assets/img/{key}-1800.webp" imagesrcset="/assets/img/{key}-800.webp 800w, '
                f'/assets/img/{key}-1800.webp {m["w"]}w" imagesizes="100vw" fetchpriority="high">')
    return f'<link rel="preload" as="image" href="/assets/img/{key}-800.webp" fetchpriority="high">'


# ------------------------------------------------------------------ bloques
def tour_card(t, page, sizes='(max-width: 760px) 80vw, 30vw'):
    price = (f'<span class="card__price">{L("Desde", "From")} {clp(t["price_from"])} <abbr title="pesos chilenos" data-title-en="Chilean pesos">CLP</abbr></span>'
             if t.get('price_from') else f'<span class="card__price card__price--p">{L("Precio por confirmar", "Price to be confirmed")}</span>')
    return f'''<article class="card" data-card>
  <a class="card__link" href="{tour_href(t)}">
    <div class="card__media">{img(t["card"], sizes)}<span class="card__tag">{L(t["tag"])}</span></div>
    <h3 class="card__title" lang="es">{e(t["title"][0])} <em class="script">{e(t["title"][1])}</em> {e(t["title"][2])}</h3>
    <p class="card__meta">{L("Día completo · 10:00–19:00 aprox.", "Full day · 10am–7pm approx.")}</p>
    <p class="card__meta">{L("Guiado en español", "Guided in Spanish")}</p>
    {price}
  </a>
</article>'''


def medallion(name, key, i, size='m'):
    inner = img(key, '220px') if key else f'<span class="med__n" aria-hidden="true">{i:02d}</span>'
    pid = f'arc{abs(hash(name)) % 10**7}'
    return (f'<li lang="es" class="med med--{size}{"" if key else " med--empty"}"><div class="med__ring">{inner}</div>'
            f'<svg class="med__label" viewBox="0 0 200 200" aria-hidden="true"><defs><path id="{pid}" d="M6,100 a94,94 0 0,0 188,0"/></defs>'
            f'<text><textPath href="#{pid}" startOffset="50%" text-anchor="middle">{e(name.upper())}</textPath></text></svg>'
            f'<span class="sr">{e(name)}</span></li>')


# ------------------------------------------------------------------ v2: todo a sangre
# Punto focal por imagen (object-position) para recortes a pantalla completa.
FOCUS = {
    'brujos-columpio': '50% 22%', 'brujos-columpio-2': '50% 30%', 'almas': '50% 35%', 'parque-bosque': '50% 40%',
    'curanto-destape': '50% 45%', 'tocoihue': '50% 40%', 'caleuche': '50% 55%', 'curaco': '50% 60%', 'curaco-2': '50% 50%',
    'mechuque': '50% 55%', 'palafitos': '50% 60%', 'punihuil-navega': '50% 40%', 'tenaun': '50% 35%', 'brujos-vuelo': '50% 45%',
    'yayanes-puente': '50% 45%', 'huillinco-columpio': '50% 40%', 'aucar-isla': '50% 55%', 'curanto-fuego': '50% 50%',
    'nercon': '50% 40%', 'brujos-alas': '50% 40%', 'punihuil-islote': '50% 50%', 'minga': '50% 55%',
}


def bimg(key, sizes='100vw', eager=False):
    """Imagen a sangre: cubre su contenedor con el punto focal de la foto."""
    m = META[key]
    pos = m['pos'] if m.get('pos_src') == 'rostros' else (FOCUS.get(key) or m.get('pos', '50% 45%'))
    return img(key, sizes, 'bleed__img', eager, f'data-pos="{pos}"').replace(
        'style="background-image', f'style="object-position:{pos};background-image', 1)


def credit(key, cls='credit'):
    c = META[key].get('credit')
    if not c: return ''
    txt, url = c.split('|')
    return f'<a class="{cls}" href="{url}" target="_blank" rel="noopener">{e(txt)}</a>'


def wide(key):
    m = META[key]; return m['w'] / m['h'] >= 1.25 and m['w'] >= 1100


def bleed_hero(key, title_html, kicker='', lead='', crumbs='', size='full', extra=''):
    """Encabezado de página a pantalla completa, con el título sobre el paisaje.
    Si la foto es vertical o cuadrada no se estira a lo ancho: ocupa la mitad derecha a altura completa."""
    split = '' if wide(key) else ' bhero--split'
    return f'''<section class="bhero bhero--{size}{split}" data-hero>
  <div class="bhero__media" data-parallax-hero>{bimg(key, "100vw" if not split else "(max-width:760px) 100vw, 50vw", True)}</div>{credit(key)}
  <div class="bhero__shade" aria-hidden="true"></div>
  {crumbs}
  <div class="bhero__in">
    {f'<p class="kicker kicker--light">{kicker}</p>' if kicker else ''}
    {title_html}
    {f'<div class="bhero__lead">{lead}</div>' if lead else ''}
    {extra}
  </div>
</section>'''


def crumbs_html(items):
    parts = ' › '.join(items)
    return f'<nav class="crumbs crumbs--light" aria-label="Migas de pan" data-aria-en="Breadcrumbs">{parts}</nav>'


def tile(key, href, title, sub='', tag='', cls='', sizes='(max-width:760px) 100vw, 50vw', attrs=''):
    """Paisaje de borde a borde con el texto encima (no hay tarjeta ni marco)."""
    return f'''<a class="tile {cls}" href="{href}" {attrs}>
  <div class="tile__media" data-parallax>{bimg(key, sizes)}</div>
  <div class="tile__shade" aria-hidden="true"></div>
  {f'<span class="credit">{e(META[key]["credit"].split("|")[0])}</span>' if META[key].get("credit") else ''}
  <div class="tile__in">
    {f'<p class="tile__tag">{tag}</p>' if tag else ''}
    <h3 class="tile__t">{title}</h3>
    {f'<p class="tile__s">{sub}</p>' if sub else ''}
  </div>
</a>'''


def tour_title_inline(t):
    a, s, b = t['title']
    return f'<span lang="es">{e(a)} <em class="script">{e(s)}</em> {e(b)}</span>'


def tour_price_inline(t):
    if t.get('price_from'):
        return f'{L("Desde", "From")} {clp(t["price_from"])} CLP'
    return L('Precio por confirmar', 'Price to be confirmed')


def tour_tile(t, P, cls='', sizes='(max-width:760px) 100vw, 50vw'):
    sub = f'{L("Día completo · 10:00–19:00", "Full day · 10am–7pm")} · {tour_price_inline(t)}'
    return tile(t['card'] if t['card'] != t['hero'] else t['hero'], tour_href(t), tour_title_inline(t), sub, L(t['tag']), cls, sizes)


def trio(tiles_html, cls=''):
    return f'<ul class="trio {cls}">' + ''.join(f'<li>{x}</li>' for x in tiles_html) + '</ul>'


def booking_cta(page, text, key='punihuil-bahia'):
    return f'''<section class="bcta" aria-label="Reservar" data-aria-en="Book">
  <div class="bcta__media" data-parallax>{bimg(key)}</div>
  <div class="bcta__shade" aria-hidden="true"></div>
  <div class="bcta__in">
    <p class="bcta__big" lang="es" data-lines><span class="line"><span>{q(SITE["cierre"], page)}</span></span></p>
    <div class="cta__row">{btn(L("Reservar por WhatsApp", "Book on WhatsApp"), wa_link(text), "btn btn--red", True)}
    <a class="u-link u-link--light" href="tel:+{SITE["wa"]}">{SITE["wa_display"]}</a></div>
    <p class="cta__note" lang="es">{q(SITE["cupos"], page)}</p>
  </div>
</section>'''


def reviews_block(page, items, title=True, key='ancud-atardecer'):
    slides = ''
    for r in items:
        frm = f' · <span lang="es">desde {e(r["from"])}</span>' if r.get('from') else ''
        tour = f' · <a href="{tour_href(TOURS[r["tour"]])}">{e(TOURS[r["tour"]]["short"])}</a>' if r.get('tour') else ''
        slides += (f'<figure class="rev swiper-slide"><div class="rev__stars" role="img" aria-label="5 de 5 estrellas" data-aria-en="5 out of 5 stars">★★★★★</div>'
                   f'<blockquote lang="{r["lang"]}">“{q(r["text"], page)}”</blockquote>'
                   f'<figcaption><strong>{e(r["name"])}</strong>{frm} · {L("vía Google", "via Google")}{tour}</figcaption></figure>')
    head = (f'<header class="reviews__head"><p class="kicker kicker--light">{L("Testimonios", "Reviews")}</p>'
            f'<h2 class="h2 h2--light" data-lines><span class="line"><span>{SITE["rating"]} ★ </span></span><span class="line"><span>{L("en Google", "on Google")}</span></span></h2>'
            f'<p class="lead lead--light">{L(f"{SITE["reviews_count"]} reseñas leídas el 19 de octubre de 2026. Las citas van en su idioma original.", f"{SITE["reviews_count"]} reviews read on 19 October 2026. Quotes are shown in their original language.")}</p></header>') if title else ''
    return f'''<section class="reviews" aria-label="Testimonios" data-aria-en="Reviews">
  <div class="reviews__media" data-parallax>{bimg(key)}</div>
  <div class="reviews__shade" aria-hidden="true"></div>
  <div class="reviews__body">
  {head}
  <div class="swiper reviews__sw" data-swiper="reviews" data-drag><div class="swiper-wrapper">{slides}</div></div>
  <div class="reviews__nav"><button class="arrow arrow--light" type="button" data-prev aria-label="Reseña anterior" data-aria-en="Previous review">←</button><button class="arrow arrow--light" type="button" data-next aria-label="Reseña siguiente" data-aria-en="Next review">→</button>
  <a class="u-link u-link--light" href="https://www.google.com/maps/place/Turismo+Chilo%C3%A9+M%C3%A1gico/@-42.4816941,-73.7642726,17z" target="_blank" rel="noopener">{L("Ver todas en Google Maps", "See all on Google Maps")}</a></div>
  </div>
</section>'''


def map_block(page):
    return f'''<div class="map" data-map>
  <a class="map__fallback" href="https://www.google.com/maps/place/Turismo+Chilo%C3%A9+M%C3%A1gico/@-42.4816941,-73.7642726,17z" target="_blank" rel="noopener">
    {bimg("palafitos", "(max-width: 760px) 100vw, 50vw")}
    <span class="map__cta">{L("Abrir mapa · Gamboa 351, Castro", "Open map · Gamboa 351, Castro")}</span>
  </a>
  <iframe title="Mapa: Gamboa 351, Castro" data-title-en="Map: Gamboa 351, Castro" data-src="https://www.openstreetmap.org/export/embed.html?bbox=-73.7702%2C-42.4846%2C-73.7582%2C-42.4786&amp;layer=mapnik&amp;marker=-42.4816941%2C-73.7642726" loading="lazy" referrerpolicy="no-referrer"></iframe>
</div>'''


def sticky_split(key, inner_html, side='right', extra_keys=()):
    """Texto que corre junto a un paisaje fijo que toca el borde de la pantalla (sticky, sin pin)."""
    more = trio([f'<div class="tile tile--pic" data-parallax>{bimg(k, "(max-width:760px) 100vw, 50vw")}</div>' for k in extra_keys]) if extra_keys else ''
    return f'''<section class="ssplit ssplit--{side}">
  <div class="ssplit__media"><div class="ssplit__stick" data-parallax>{bimg(key, "(max-width:760px) 100vw, 50vw")}</div>{credit(key)}</div>
  <div class="ssplit__txt">{inner_html}</div>
</section>{more}'''


# ------------------------------------------------------------------ HOME
def home():
    P = '/'
    tours = [t for t in D.TOURS if not t.get('thin')]
    n = len(tours)
    panels = ''
    for i, t in enumerate(tours):
        stops = ' · '.join(e(s) for s in t['stops'][:5])
        if t['stops']:
            COPY.append((P, ' · '.join(t['stops'][:5]), t['afiche'] + ' rótulos de paradas', None))
        a, s, b = t['title']
        COPY.append((P, f'{a} {s} {b}', '[DEST-H7] títulos de afiche', None))
        port = '' if wide(t["hero"]) else ' tpanel--portrait'
        panels += f'''<article class="tpanel{port}" data-tpanel>
  <div class="tpanel__media" data-tpanel-media>{bimg(t["hero"], "100vw")}</div>
  <div class="tpanel__shade" aria-hidden="true"></div>
  <p class="tpanel__n" aria-hidden="true">{i+1:02d}<span>/{n:02d}</span></p>
  <div class="tpanel__in">
    <p class="tpanel__tag">{L(t["tag"])}</p>
    <h3 class="tpanel__t" lang="es"><span>{e(a)}</span> <em class="script">{e(s)}</em> <span>{e(b)}</span></h3>
    <p class="tpanel__hook" lang="es">{q(t["hook"], P)}</p>
    {f'<p class="tpanel__stops" lang="es">{stops}</p>' if stops else ''}
    <p class="tpanel__meta">{L("Día completo · 10:00–19:00 aprox.", "Full day · 10am–7pm approx.")} · {tour_price_inline(t)}</p>
    <div class="tpanel__ctas">{btn(L("Ver el tour", "See the tour"), tour_href(t), "btn btn--light")}{btn(L("Reservar", "Book"), wa_link(f"Hola! Quiero reservar el {t['short']}. Fecha: ___ Personas: ___"), "btn btn--red", True)}</div>
  </div>
</article>'''
    # destinos: el paisaje entero cambia según el destino elegido
    dbg = ''.join(f'<div class="dx__bg{" is-on" if i == 0 else ""}" data-dx-bg="{d["slug"]}">{bimg(d["img"])}</div>' for i, d in enumerate(D.DESTINOS))
    dlist = ''.join(f'<li><a class="dx__link{" is-on" if i == 0 else ""}" href="{dest_href(d)}" data-dx="{d["slug"]}" lang="es">{e(d["name"])}</a></li>' for i, d in enumerate(D.DESTINOS))
    dtxt = ''.join(f'<p class="dx__txt{" is-on" if i == 0 else ""}" data-dx-txt="{d["slug"]}" lang="es">{q(d["intro"], P)}</p>' for i, d in enumerate(D.DESTINOS))
    # experiencias: mosaico de borde a borde
    mosaic = ''.join(tile(x['img'], exp_href(x), L(x['name']), f'<span lang="es">{q(x["quote"], P)}</span>', f'0{i+1}', f'mos__t mos__t--{i+1}',
                          '(max-width:760px) 100vw, 60vw') for i, x in enumerate(D.EXPERIENCIAS))
    pk_tiles = []
    for p in D.PAQUETES:
        sub = f'<span lang="es">{q(p["text"], P)}</span>'
        if p['imgs']:
            pk_tiles.append(tile(p['imgs'][0], '/paquetes/', f'<span lang="es">{e(p["name"])}</span>', sub, L(p['days'])))
        else:
            pk_tiles.append(f'<a class="tile tile--flat" href="/paquetes/"><div class="tile__in"><p class="tile__tag">{L(p["days"])}</p><h3 class="tile__t" lang="es">{e(p["name"])}</h3><p class="tile__s">{sub}</p></div><span class="tile__flake" aria-hidden="true">❄</span></a>')
    g_tiles = [tile(g['img'], f'/guia/{g["slug"]}/', L(g['title']), L('Leer', 'Read'), L('Guía de Chiloé', 'Chiloé guide')) for g in D.GUIA[:3]]
    content = f'''
<section class="hero" data-hero>
  <div class="hero__media" data-parallax-hero>{img("huillinco-columpio", "100vw", "", True)}</div>
  <div class="hero__shade" aria-hidden="true"></div>
  <div class="hero__in">
    <img class="hero__logo" src="/brand/logo/logo-sticker.svg" width="1912" height="1065" alt="Turismo Chiloé Mágico" data-alt-en="Turismo Chiloé Mágico">
    <h1 class="hero__t" lang="es" data-lines><span class="line"><span>{q(Q("Nuestro archipiélago es mágico", "[BIO]"), P)}</span></span><span class="line line--script"><span>{q(Q("¡Ven a descubrirlo!", "[BIO]"), P)}</span></span></h1>
    <p class="hero__sub" lang="es">{q(SITE["bio1"], P)}</p>
    <div class="hero__ctas">{btn(L("Ver tours", "See tours"), "#tours", "btn btn--light")}{btn(L("Reservar por WhatsApp", "Book on WhatsApp"), wa_link("Hola! Quiero consultar por los tours"), "btn btn--red", True)}</div>
  </div>
  <ul class="hero__trust" aria-label="Datos de confianza" data-aria-en="Trust facts">
    <li><strong>{SITE["rating"]} ★</strong> {L(f"Google · {SITE['reviews_count']} reseñas", f"Google · {SITE['reviews_count']} reviews")}</li>
    <li><strong>{L("Lu a Do", "Mon–Sun")}</strong> {L("tours todos los días", "tours every day")}</li>
    <li><strong>16</strong> {L("pasajeros máx. por van", "passengers max. per van")}</li>
    <li><strong>10:00</strong> {L("salida frente a la Plaza de Armas", "departure facing the main square")}</li>
  </ul>
  <p class="hero__cap" lang="es">Columpio del lago Huillinco · @chiloemagicotour</p>
</section>

<section class="isla" aria-label="Navegación en Puñihuil" data-aria-en="Sailing in Puñihuil" data-isla>
  <div class="isla__stick">
    <p class="isla__bg" lang="es" aria-hidden="true"><span>NO DEJES</span><span>QUE TE LO</span><span>CUENTEN</span></p>
    <div class="isla__win" data-isla-win>
      <video class="isla__v" muted playsinline loop preload="none" data-lazy-video data-poster="/assets/video/isla-poster.jpg" aria-label="{e(META['_videos']['isla']['alt'])}" data-aria-en="{e(ALT_EN['vid:isla'])}">
        <source data-src="/assets/video/isla.webm" type="video/webm"><source data-src="/assets/video/isla.mp4" type="video/mp4">
      </video>
    </div>
    <p class="isla__q script" lang="es">{q(Q("Vamos a navegar? 🌊", "[IG-015]"), P)}</p>
  </div>
</section>

<section class="htours" id="tours" aria-label="Nuestros tours" data-aria-en="Our tours" data-htours>
  <div class="htours__stick">
    <div class="htours__track" data-htrack>
      <div class="tpanel tpanel--intro">
        <p class="kicker kicker--light">{L("Nuestros tours disponibles", "Our available tours")}</p>
        <h2 class="h2 h2--light" data-lines><span class="line"><span>{L("Tours de", "Full-day")}</span></span><span class="line"><span>{L("día completo", "tours")}</span></span></h2>
        <p class="lead lead--light" lang="es">{q(Q("Todos nuestros tours incluyen traslado, guiado, almuerzo y bebestibles, y visitas a distintos atractivos turísticos 🌿", "[IG-007]"), P)}</p>
        <p class="tpanel__hint" aria-hidden="true">{L("Sigue bajando →", "Keep scrolling →")}</p>
      </div>
      {panels}
      <div class="tpanel tpanel--outro">
        <p class="script tpanel__script" lang="es">{q(SITE["slogan"], P)}</p>
        {btn(L("Ver los 8 tours", "See all 8 tours"), "/tours/", "btn btn--light")}
      </div>
    </div>
    <div class="htours__bar" aria-hidden="true"><span data-hbar></span></div>
  </div>
</section>

<section class="dx" data-dx aria-label="Explora por destino" data-aria-en="Explore by destination">
  <div class="dx__bgs" aria-hidden="true">{dbg}</div>
  <div class="dx__shade" aria-hidden="true"></div>
  <div class="dx__in">
    <p class="kicker kicker--light">{L("Explora por destino", "Explore by destination")}</p>
    <ul class="dx__list">{dlist}</ul>
    <div class="dx__side">{dtxt}<a class="u-link u-link--light" href="/destinos/">{L("Todos los destinos", "All destinations")}</a></div>
  </div>
</section>

<section class="mos" aria-label="Explora por experiencia" data-aria-en="Explore by experience">
  <header class="mos__head"><p class="kicker">{L("Explora por experiencia", "Explore by experience")}</p>
  <h2 class="h2" data-lines><span class="line"><span>{L("Bosque, mar,", "Forest, sea,")}</span></span><span class="line line--script"><span>{L("curanto y brujos", "curanto and witches")}</span></span></h2></header>
  <div class="mos__grid">{mosaic}</div>
</section>

<section class="why" aria-label="Por qué viajar con nosotros" data-aria-en="Why travel with us">
  <div class="why__media" data-parallax>{bimg("muelle-luz-sendero")}</div>
  <div class="why__shade" aria-hidden="true"></div>
  <div class="why__in">
    <p class="kicker kicker--light">{L("Por qué viajar con nosotros", "Why travel with us")}</p>
    <h2 class="h2 h2--light" lang="es" data-lines><span class="line"><span>{q(Q("¡NO DEJES QUE TE LO CUENTEN…!", "[IG-007]", fix="recorte del remate «¡NO DEJES QUE TE LO CUENTEN, VEN A DISFRUTAR…»"), P)}</span></span></h2>
    <p class="why__p" lang="es">{q(SITE["servicio"], P)}</p>
    <ul class="why__list">
      <li lang="es">{q(SITE["vans"], P)}</li>
      <li lang="es">{q(SITE["van16"], P)}</li>
      <li lang="es">{q(SITE["salida"], P)} ⛪️</li>
    </ul>
  </div>
</section>

<section class="pkgs" aria-label="Paquetes de varios días" data-aria-en="Multi-day packages">
  <header class="pkgs__head"><div><p class="kicker">{L("Paquetes de varios días", "Multi-day packages")}</p>
  <h2 class="h2" data-lines><span class="line"><span>{L("Más allá de la isla", "Beyond the island")}</span></span></h2></div>
  <p class="lead" lang="es">{q(SITE["privados"], P)}</p></header>
  {trio(pk_tiles, "trio--tall")}
  <p class="pkgs__foot">{btn(L("Arma tu viaje a medida", "Plan a custom trip"), "/paquetes/#a-medida", "btn btn--ink")}</p>
</section>

{reviews_block(P, D.REVIEWS)}

<section class="guia-home" aria-label="Guía de Chiloé" data-aria-en="Chiloé guide">
  <header class="pkgs__head"><div><p class="kicker">{L("Guía de Chiloé", "Chiloé guide")}</p>
  <h2 class="h2" data-lines><span class="line"><span>{L("Lo que cuentan", "What they tell")}</span></span><span class="line line--script"><span>{L("en el camino", "along the way")}</span></span></h2></div></header>
  {trio(g_tiles)}
</section>

<section class="visit">
  <div class="visit__txt">
    <p class="kicker">{L("Visítanos", "Visit us")}</p>
    <h2 class="h3" lang="es">{q(SITE["address_short"], P)}</h2>
    <p lang="es">{q(SITE["hours"], P)}</p>
    <p class="contact__links"><a href="{wa_link('Hola! Quiero consultar por los tours')}" target="_blank" rel="noopener" class="u-link">WhatsApp {SITE["wa_display"]}</a>
    <a href="mailto:{SITE["email"]}" class="u-link">{SITE["email"]}</a></p>
    <p class="contact__srv">{L("Servicios privados, traslados y grupos:", "Private services, transfers and groups:")} <a class="u-link" href="/servicios/">{L("ver servicios", "see services")}</a></p>
  </div>
  {map_block(P)}
</section>

{booking_cta(P, "Hola! Quiero reservar un tour")}
'''
    page('/', 'Turismo Chiloé Mágico · Tours en Chiloé desde Castro', 'Turismo Chiloé Mágico · Chiloé tours from Castro',
         'Tours de día completo por el archipiélago de Chiloé desde Castro: La Costa con curanto, Isla Lemuy, Parque Nacional, Muelle de las Almas, Muelle de la Luz, Pingüineras de Puñihuil e Isla Quinchao.',
         'Full-day tours of the Chiloé archipelago from Castro: La Costa with curanto, Lemuy Island, National Park, Muelle de las Almas, Muelle de la Luz, Puñihuil penguins and Quinchao Island.',
         content, 'home', preload=preload_img('huillinco-columpio'))


def h1_lines(*parts, light=True):
    out = ''
    for txt, script in parts:
        out += f'<span class="line{" line--script" if script else ""}"><span>{txt}</span></span>'
    return f'<h1 class="h1{" h1--light" if light else ""}" data-lines>{out}</h1>'


# ------------------------------------------------------------------ TOURS
def tours_index():
    P = '/tours/'
    filt = ''.join(f'<button type="button" class="chip" data-filter="{x["slug"]}" aria-pressed="false">{L(x["name"])}</button>' for x in D.EXPERIENCIAS)
    cards = ''.join(f'<li data-exp="{" ".join(t["exp"])}">{tour_tile(t, P)}</li>' for t in D.TOURS)
    COPY.append((P, 'NUESTROS TOURS disponibles', '[DEST-H7_001] "NUESTROS TOURS DISPONIBLES"', 'Se separa "disponibles" en cursiva'))
    content = f'''{bleed_hero("muelle-luz-oceano", '<h1 class="h1 h1--light" lang="es" data-lines><span class="line"><span>NUESTROS TOURS</span></span><span class="line line--script"><span>disponibles</span></span></h1>', L("Tours", "Tours"),
        f'<p lang="es">{q(SITE["horario_tour"], P)}</p><p lang="es">{q(SITE["cupos"], P)} 😉</p>')}
<section class="tgrid">
  <h2 class="sr">{L("Todos los tours", "All tours")}</h2>
  <div class="chips" role="group" aria-label="Filtrar por experiencia" data-aria-en="Filter by experience"><button type="button" class="chip" data-filter="all" aria-pressed="true">{L("Todos", "All")}</button>{filt}</div>
  <ul class="tiles2" data-filter-grid>{cards}</ul>
</section>
{booking_cta(P, "Hola! Quiero consultar por los tours", "ancud-atardecer")}'''
    page(P, 'Tours en Chiloé desde Castro · Turismo Chiloé Mágico', 'Chiloé tours from Castro · Turismo Chiloé Mágico',
         'Siete tours de día completo desde Castro con traslado, guiado, almuerzo y bebestibles.',
         'Seven full-day tours from Castro with transport, guiding, lunch and drinks.', content, preload=preload_img('muelle-luz-oceano'))


def tour_page(t):
    P = tour_href(t)
    ld = {"@context": "https://schema.org", "@type": "TouristTrip", "name": t['short'], "touristType": "Grupos",
          "image": f"{DOMAIN}/assets/img/{t['hero']}-800.webp", "url": DOMAIN + P,
          "provider": {"@type": "TravelAgency", "name": SITE['name'], "telephone": '+' + SITE['wa'], "url": DOMAIN + '/'}}
    if t.get('price_from'):
        ld['offers'] = {"@type": "Offer", "price": t['price_from'], "priceCurrency": "CLP"}
    wa_t = f'Hola! Quiero reservar el {t["short"]}. Fecha: ___ Personas: ___'
    rel = [x for x in D.TOURS if x is not t and (set(x['dest']) & set(t['dest']) or set(x['exp']) & set(t['exp']))][:3]
    revs = [r for r in D.REVIEWS if r.get('tour') == t['slug']]
    price_html = (f'<p class="book__price"><span>{L("Desde", "From")}</span> <strong>{clp(t["price_from"])}</strong> <abbr title="pesos chilenos" data-title-en="Chilean pesos">CLP</abbr></p>'
                  f'<p class="book__pq" lang="es">{q(t["price"], P)}</p><p class="book__note">{L(t["price_season"])}</p>') if t.get('price_from') else \
                 f'<p class="book__price"><strong>{L("Precio por confirmar", "Price to be confirmed")}</strong></p>'
    stops = ''.join(medallion(s, k, i + 1) for i, (s, k) in enumerate(zip(t['stops'], t['stop_imgs'])))
    if t.get('itinerary'):
        itin = '<ol class="itin">' + ''.join(f'<li><span class="itin__n">{i+1:02d}</span><span lang="es">{q(x, P)}</span></li>' for i, x in enumerate(t['itinerary'])) + '</ol>'
        itin_src = ''
    elif t['stops']:
        itin = '<ol class="itin">' + ''.join(f'<li><span class="itin__n">{i+1:02d}</span><span lang="es">{e(s)}</span></li>' for i, s in enumerate(t['stops'])) + '</ol>'
        itin_src = f'<p class="note">{L("Paradas según el afiche del tour. El orden y los horarios exactos: por confirmar con la agencia.", "Stops as shown on the tour poster. Exact order and times: to be confirmed with the agency.")}</p>'
        COPY.append((P, ' / '.join(t['stops']), t['afiche'] + ' rótulos de paradas', None))
    else:
        itin, itin_src = pending(P), ''
    body = ''.join(q(b, P, 'p') for b in t['body'])
    gallery = ''.join(f'<div class="swiper-slide gal__s">{bimg(k, "(max-width:760px) 90vw, 60vw")}</div>' for k in t['gallery'])
    extras = ''.join(f'<li lang="es">{q(x, P)}</li>' for x in t.get('extras', []))
    season = (f'<p lang="es">{L("Temporada:", "Season:")} {q(t["season"], P)} · {L("meses exactos por confirmar.", "exact months to be confirmed.")}</p>' if t.get('season') else '')
    crumbs = crumbs_html([f'<a href="/">{L("Inicio", "Home")}</a>', '<a href="/tours/">Tours</a>', f'<span aria-current="page" lang="es">{e(t["short"])}</span>'])
    title = title_afiche(t['title'], P, cls='afiche afiche--light')
    lead_html = (f'<p class="bhero__hook" lang="es">{q(t["hook"], P)}</p>'
                 f'<p class="bhero__meta"><span class="stars">★ {SITE["rating"]}</span> {L(f"{SITE["reviews_count"]} reseñas de la agencia en Google", f"{SITE["reviews_count"]} agency reviews on Google")} · {tour_price_inline(t)}</p>')
    ctas = f'<div class="bhero__ctas">{btn(L("Reservar por WhatsApp", "Book on WhatsApp"), wa_link(wa_t), "btn btn--red", True)}</div>'
    content = f'''{bleed_hero(t["hero"], title, L(t["tag"]), lead_html, crumbs, "full", ctas)}

<section class="tbody">
  <div class="tbody__main">
    <dl class="facts">
      <div><dt>{L("Duración", "Duration")}</dt><dd>{L("Día completo", "Full day")}</dd></div>
      <div><dt>{L("Salida y regreso", "Departure and return")}</dt><dd>{L("10:00 · 19:00 aprox.", "10am · 7pm approx.")}</dd></div>
      <div><dt>{L("Punto de encuentro", "Meeting point")}</dt><dd lang="es">{q(SITE["address_short"], P)}</dd></div>
      <div><dt>{L("Idioma del guía", "Guide's language")}</dt><dd>{L("Español", "Spanish")}</dd></div>
      <div><dt>{L("Grupo", "Group")}</dt><dd>{L("Máx. 16 por van, con guía propio", "Max. 16 per van, with its own guide")}</dd></div>
      <div><dt>{L("Mínimo de pasajeros · dificultad · niños", "Minimum group · difficulty · children")}</dt><dd>{L(D.PENDING)}</dd></div>
    </dl>
    {f'<div class="tdesc"><p class="lead" lang="es">{q(t["lead"], P)}</p>{body}</div>' if t.get("lead") else ''}
    {f'<h2 class="h3">{L("Destacados", "Highlights")}</h2><ul class="meds" data-meds>{stops}</ul>' if t["stops"] else ''}
    <h2 class="h3">{L("Itinerario", "Itinerary")}</h2>{itin}{itin_src}
    <div class="inc">
      <div><h2 class="h4">{L("Incluye", "Included")}</h2><p lang="es">{q(SITE["incluye"], P)} 🌿</p></div>
      <div><h2 class="h4">{L("No incluye", "Not included")}</h2>{f'<ul>{extras}</ul>' if extras else pending(P)}</div>
    </div>
    <h2 class="h4">{L("Clima y temporada", "Weather and season")}</h2><p lang="es">{q(SITE["clima"], P)}</p>{season}{pending(P)}
    <h2 class="h4">{L("Qué llevar · Políticas de cancelación, clima y mínimo de pasajeros", "What to bring · Cancellation, weather and minimum-group policies")}</h2>{pending(P)}
  </div>
  <aside class="book" aria-label="Reservar" data-aria-en="Book">
    <div class="book__in">
      {price_html}
      <p class="book__inc">{L("Traslado, guía, almuerzo y bebestibles", "Transport, guide, lunch and drinks")}</p>
      <form class="book__f" data-wa-form data-tour="{e(t["short"])}">
        <label>{L("Fecha", "Date")}<input type="date" name="fecha" required></label>
        <label>{L("Personas", "People")}<input type="number" name="personas" min="1" max="16" value="2" required></label>
        <button class="btn btn--red btn--full" type="submit"><span class="btn__in">{L("Reservar por WhatsApp", "Book on WhatsApp")}</span></button>
      </form>
      <p class="book__alt"><a href="{wa_link(wa_t)}" target="_blank" rel="noopener" class="u-link">{L("o escríbenos directo", "or message us directly")}</a></p>
      <p class="book__cupos" lang="es">{q(SITE["cupos"], P)}</p>
    </div>
  </aside>
</section>
<div class="mbar" data-mbar><span>{('<strong>' + clp(t["price_from"]) + '</strong> CLP') if t.get("price_from") else L("Precio por confirmar", "Price to be confirmed")}</span>{btn(L("Reservar", "Book"), wa_link(wa_t), "btn btn--red btn--sm", True)}</div>

{f'<section class="gal" aria-label="Galería" data-aria-en="Gallery"><div class="swiper gal__sw" data-swiper="gallery" data-drag><div class="swiper-wrapper">{gallery}</div></div></section>' if t["gallery"] else ''}
{reviews_block(P, revs, False, t["hero"]) if revs else ''}
<section class="sec faq-mini">
  <h2 class="h3">{L("Preguntas frecuentes", "Frequently asked questions")}</h2>
  {faq_items(P, [D.FAQ[i] for i in (5, 6, 7, 10)])}
  <a class="u-link" href="/preguntas-frecuentes/">{L("Ver todas", "See all")}</a>
</section>
<section class="visit">
  <div class="visit__txt"><p class="kicker">{L("Punto de salida", "Departure point")}</p><h2 class="h3" lang="es">{q(SITE["address_short"], P)}</h2><p lang="es">{q(SITE["salida"], P)}</p></div>
  {map_block(P)}
</section>
<section class="related" aria-label="Tours relacionados" data-aria-en="Related tours">
  <header class="pkgs__head"><p class="kicker">{L("Tours relacionados", "Related tours")}</p></header>
  {trio([tour_tile(x, P, sizes="(max-width:760px) 100vw, 34vw") for x in rel])}
</section>
{booking_cta(P, wa_t, rel[0]["hero"] if rel else "punihuil-bahia")}'''
    page(P, f'{t["short"]} desde Castro · Turismo Chiloé Mágico', f'{t["short"]} from Castro · Turismo Chiloé Mágico',
         f'{t["short"]}: día completo desde Castro con traslado, guiado, almuerzo y bebestibles. Paradas: {", ".join(t["stops"]) or "Isla Mechuque"}.',
         f'{t["short"]}: full day from Castro with transport, guiding, lunch and drinks.', content, 'tour', wa_t, ld, preload_img(t['hero']))


def faq_items(P, items):
    out = ''
    for qq, answers in items:
        parts = ''
        for a in answers:
            if a == '__pending__': parts += pending(P)
            elif a == '__pending_prices__': parts += f'<p>{L("Los demás tours: precio por confirmar con la agencia.", "Other tours: price to be confirmed with the agency.")}</p>'
            elif a == '__costa__': parts += f'<p><a href="/tours/la-costa-curanto/">Tour La Costa</a>:</p>'
            elif a == '__es_only__': parts += f'<p>{L("Español.", "Spanish.")}</p>'
            elif a == '__wa__': parts += f'<p>WhatsApp <a href="{wa_link("Hola! Quiero reservar un tour")}" target="_blank" rel="noopener">{SITE["wa_display"]}</a> · <a href="tel:+56998833946">{SITE["phone2"]}</a></p>'
            else: parts += f'<p lang="{"en" if "RESEÑA" in getattr(a, "src", "") and a.isascii() else "es"}">{q(a, P)}</p>'
        out += f'<details class="faq"><summary>{L(qq)}</summary><div class="faq__a">{parts}</div></details>'
    return out


# ------------------------------------------------------------------ DESTINOS / EXPERIENCIAS
def destinos():
    P = '/destinos/'
    tiles = ''.join(f'<li>{tile(d["img"], dest_href(d), f"<span lang=es>{e(d["name"])}</span>", f"<span lang=es>{q(d["intro"], P)}</span>")}</li>' for d in D.DESTINOS)
    content = f'''{bleed_hero("aucar-isla", h1_lines((L("Explora por", "Explore by"), False), (L("destino", "destination"), True)), L("Destinos", "Destinations"), f'<p lang="es">{q(SITE["diarias"], P)}</p>')}
<section class="tgrid"><ul class="tiles2">{tiles}</ul></section>{booking_cta(P, "Hola! Quiero consultar por los tours", "punihuil-bahia")}'''
    page(P, 'Destinos en Chiloé · Turismo Chiloé Mágico', 'Destinations in Chiloé · Turismo Chiloé Mágico',
         'Castro, Ancud y Puñihuil, Dalcahue y Quinchao, Chonchi e Isla Lemuy, Cucao y el Parque Nacional Chiloé.',
         'Castro, Ancud and Puñihuil, Dalcahue and Quinchao, Chonchi and Lemuy Island, Cucao and Chiloé National Park.', content, preload=preload_img('aucar-isla'))
    for d in D.DESTINOS:
        P = dest_href(d)
        ts = [t for t in D.TOURS if d['slug'] in t['dest']]
        must = ''.join(f'<li lang="es">{e(m)}</li>' for m in d['must'])
        COPY.append((P, ' / '.join(d['must']), 'nombres de lugares de los afiches [DEST-H7] y posts', None))
        crumbs = crumbs_html([f'<a href="/">{L("Inicio", "Home")}</a>', f'<a href="/destinos/">{L("Destinos", "Destinations")}</a>', f'<span aria-current="page" lang="es">{e(d["name"])}</span>'])
        inner = f'''<p class="lead" lang="es">{q(d["intro"], P)}</p>{''.join(q(b, P, 'p') for b in d["body"])}
  <h2 class="h4">{L("Imperdibles", "Must-sees")}</h2><ul class="must">{must}</ul>
  <h2 class="h4">{L("Cómo llegar desde Castro · mejor época", "Getting there from Castro · best season")}</h2>
  <p lang="es">{q(SITE["salida"], P)}</p>{pending(P)}'''
        content = f'''{bleed_hero(d["img"], f'<h1 class="h1 h1--light" lang="es" data-lines><span class="line"><span>{e(d["name"].upper())}</span></span></h1>', L("Destino", "Destination"), '', crumbs)}
{sticky_split(d["imgs"][0], inner, "right", d["imgs"][1:])}
<section class="related"><header class="pkgs__head"><p class="kicker">{L("Tours que pasan por aquí", "Tours that stop here")}</p></header>{trio([tour_tile(t, P, sizes="(max-width:760px) 100vw, 34vw") for t in ts])}</section>
{booking_cta(P, f"Hola! Quiero conocer {d['name']}", d["imgs"][-1])}'''
        page(P, f'{d["name"]} · Turismo Chiloé Mágico', f'{d["name"]} · Turismo Chiloé Mágico',
             f'Qué hacer en {d["name"]}, Chiloé: {", ".join(d["must"])}. Tours desde Castro.', f'Things to do in {d["name"]}, Chiloé. Tours from Castro.',
             content, preload=preload_img(d['img']))


def experiencias():
    P = '/experiencias/'
    tiles = ''.join(f'<li>{tile(x["img"], exp_href(x), L(x["name"]), f"<span lang=es>{q(x["quote"], P)}</span>")}</li>' for x in D.EXPERIENCIAS)
    content = f'''{bleed_hero("brujos-columpio", h1_lines((L("Explora por", "Explore by"), False), (L("experiencia", "experience"), True)), L("Experiencias", "Experiences"), f'<p lang="es">{q(SITE["magia"], P)}</p>')}
<section class="tgrid"><ul class="tiles2">{tiles}</ul></section>'''
    page(P, 'Experiencias en Chiloé · Turismo Chiloé Mágico', 'Experiences in Chiloé · Turismo Chiloé Mágico',
         'Patrimonio e iglesias, naturaleza, navegación, gastronomía chilota y mitos de Chiloé.', 'Heritage churches, nature, boat trips, Chilote food and myths of Chiloé.', content, preload=preload_img('brujos-columpio'))
    for x in D.EXPERIENCIAS:
        P = exp_href(x)
        ts = [t for t in D.TOURS if x['slug'] in t['exp']]
        crumbs = crumbs_html([f'<a href="/">{L("Inicio", "Home")}</a>', f'<a href="/experiencias/">{L("Experiencias", "Experiences")}</a>', f'<span aria-current="page">{L(x["name"])}</span>'])
        content = f'''{bleed_hero(x["img"], h1_lines((L(x["name"]), False)), L("Experiencia", "Experience"), f'<p lang="es">{q(x["quote"], P)}</p>', crumbs)}
<section class="sec narrow"><p class="lead" lang="es">{q(x["more"], P)}</p></section>
<section class="related"><header class="pkgs__head"><p class="kicker">{L("Tours con esta experiencia", "Tours with this experience")}</p></header>{trio([tour_tile(t, P, sizes="(max-width:760px) 100vw, 34vw") for t in ts])}</section>
{booking_cta(P, "Hola! Quiero consultar por los tours", ts[0]["hero"] if ts else "punihuil-bahia")}'''
        page(P, f'{x["name"].es} en Chiloé · Turismo Chiloé Mágico', f'{x["name"].en} in Chiloé · Turismo Chiloé Mágico',
             f'{x["name"].es}: tours de día completo desde Castro.', f'{x["name"].en}: full-day tours from Castro.', content, preload=preload_img(x['img']))


# ------------------------------------------------------------------ PAQUETES, SERVICIOS, NOSOTROS, GUÍA, FAQ, CONTACTO
def wa_form(P, kind):
    return f'''<form class="form" data-wa-form data-kind="{kind}">
  <label>{L("Nombre", "Name")}<input name="nombre" autocomplete="name" required></label>
  <label>{L("Fechas aproximadas", "Approximate dates")}<input name="fecha" placeholder="dd/mm"></label>
  <label>{L("Personas", "People")}<input type="number" name="personas" min="1" value="2"></label>
  <label class="form__wide">{L("¿Qué te gustaría conocer?", "What would you like to see?")}<textarea name="mensaje" rows="3"></textarea></label>
  <button class="btn btn--red" type="submit"><span class="btn__in">{L("Enviar por WhatsApp", "Send on WhatsApp")}</span></button>
  <p class="form__note">{L("Se abre WhatsApp con tu mensaje listo; no guardamos datos.", "WhatsApp opens with your message ready; we store no data.")}</p>
</form>'''


def paquetes():
    P = '/paquetes/'
    items = ''
    for p in D.PAQUETES:
        extra = q(p['extra'], P, 'p') if p.get('extra') else ''
        inner = f'''<p class="kicker">{L(p["days"])}</p><h2 class="h2" lang="es">{e(p["name"])}</h2>{q(p["text"], P, "p")}{extra}
<h3 class="h5">{L("Itinerario día a día, alojamiento, comidas y precio en base doble", "Day-by-day itinerary, lodging, meals and price per person (double)")}</h3>{pending(P)}
<p>{btn(L("Cotizar", "Get a quote"), wa_link(f"Hola! Quiero cotizar el viaje {p['name']}"), "btn btn--ink", True)}</p>'''
        if p['imgs']:
            items += sticky_split(p['imgs'][0], inner, 'right' if len(items) % 2 == 0 else 'left', p['imgs'][1:])
        else:
            items += f'<section class="ssplit ssplit--flat"><div class="ssplit__media ssplit__media--flat" aria-hidden="true"><span>❄</span></div><div class="ssplit__txt">{inner}</div></section>'
    content = f'''{bleed_hero("valdivia-2" if META["valdivia-2"]["w"] > 1200 else "ancud-atardecer", h1_lines((L("Viajes de", "Trips of"), False), (L("varios días", "several days"), True)), L("Paquetes", "Packages"),
        f'<p lang="es">{q(SITE["privados"], P)}</p><p class="note note--light">{L("Viajes que la agencia ya ha realizado según sus publicaciones. Próximas salidas y valores: por confirmar.", "Trips the agency has already run, according to its posts. Next departures and prices: to be confirmed.")}</p>')}
{items}
<section class="sec medida" id="a-medida"><div><p class="kicker">{L("A medida", "Custom")}</p><h2 class="h2">{L("Arma tu viaje", "Plan your trip")}</h2>
<p lang="es">{q(SITE["diarias"], P)}</p></div>{wa_form(P, "a medida")}</section>'''
    page(P, 'Paquetes y viajes de varios días · Turismo Chiloé Mágico', 'Multi-day packages · Turismo Chiloé Mágico',
         'Excursión Valdivia y Niebla 4 días, circuito a la nieve al Volcán Osorno, Bariloche y viajes a medida desde Castro.',
         'Valdivia and Niebla 4-day trip, snow circuit to Osorno Volcano, Bariloche and custom trips from Castro.', content)


def servicios():
    P = '/servicios/'
    cards = [
        (U('Viajes privados', 'Private trips'), Q('Servicios privados', '[BIO]'), 'grupo-van'),
        (U('Traslados', 'Transfers'), Q('servicio de turismo, traslado y viajes privados', '[IG-016]'), 'vans'),
        (U('Grupos', 'Groups'), Q('Tremendo grupo nos tocó … que disfrutaron el Tour de La Costa🤩', '[IG-006]', fix='se omite «ayer»'), 'grupo-columpios'),
    ]
    tiles = [tile(k, wa_link("Hola! Quiero cotizar: " + t.es), L(t), f'<span lang="es">{q(x, P)}</span> · {L("Cotizar", "Get a quote")}', '', '', '(max-width:760px) 100vw, 34vw', 'target="_blank" rel="noopener"') for t, x, k in cards]
    content = f'''{bleed_hero("vans", h1_lines((L("Traslados, privados", "Transfers, private"), False), (L("y grupos", "and groups"), True)), L("Servicios", "Services"), f'<p lang="es">{q(SITE["vans"], P)}</p>')}
{trio(tiles, "trio--tall")}
<section class="sec narrow"><p class="note">{L("Recorridos, vehículos y tarifas de cada servicio: por confirmar con la agencia.", "Routes, vehicles and rates for each service: to be confirmed with the agency.")}</p></section>
{booking_cta(P, "Hola! Quiero cotizar un servicio privado", "muelle-luz-grupo")}'''
    page(P, 'Servicios privados y traslados · Turismo Chiloé Mágico', 'Private services and transfers · Turismo Chiloé Mágico',
         'Viajes privados, traslados y grupos en vans con aire acondicionado desde Castro.', 'Private trips, transfers and groups in air-conditioned vans from Castro.', content, preload=preload_img('vans'))


def nosotros():
    P = '/nosotros/'
    team = ''.join(f'<li><span class="team__n" lang="es">{e(m["name"])}</span><span class="team__r">{L(m["role"])}</span></li>' for m in D.TEAM)
    COPY.append((P, ', '.join(m['name'] for m in D.TEAM), 'nombres en posts y reseñas: ' + ' '.join(m['src'] for m in D.TEAM), None))
    inner = f'''<p lang="es">{q(SITE["anos"], P)}</p><p lang="es">{q(SITE["magia"], P)}</p><p lang="es">{q(SITE["magia2"], P)}</p>
  <blockquote class="pull" lang="es">“{q(SITE["marketing"], P)}”</blockquote><p lang="es">{q(SITE["irrepetible"], P)}</p>
  <h2 class="h3">{L("Flota", "Fleet")}</h2><p lang="es">{q(SITE["van16"], P)}</p>
  <h2 class="h3">{L("Registro Sernatur y sellos", "Sernatur registry and certifications")}</h2>
  <p>{L("Número de registro Sernatur, razón social y sellos:", "Sernatur registry number, legal name and seals:")}</p>{pending(P)}'''
    content = f'''{bleed_hero("muelle-luz-grupo", '<h1 class="h1 h1--light" lang="es" data-lines><span class="line"><span>SOMOS</span></span><span class="line line--script"><span>Chiloé Mágico</span></span></h1>', L("Nosotros", "About us"), f'<p lang="es">{q(SITE["somos"], P)}</p>')}
{sticky_split("nicolas-enrique", inner, "left", ("vans",))}
<section class="sec team"><header class="sec__head"><p class="kicker">{L("Equipo", "Team")}</p><h2 class="h2">{L("Guías y conductores", "Guides and drivers")}</h2>
<p class="lead">{L("Nombres tal como aparecen en sus publicaciones y en las reseñas de Google. Fotos del equipo: por confirmar.", "Names as they appear in the agency's posts and Google reviews. Team photos: to be confirmed.")}</p></header>
<ul class="team__list">{team}</ul>
<p class="team__cap" lang="es">{q(Q("Nuestro guía Nicolás junto a don Enrique siempre enfocados en brindarle la mejor experiencia a nuestros turistas!", "[IG-023]"), P)}</p></section>
{reviews_block(P, D.REVIEWS[:6], True, "hueñay-playa")}'''
    page(P, 'Nosotros · Turismo Chiloé Mágico', 'About us · Turismo Chiloé Mágico',
         'Agencia local de turismo en Castro, Chiloé: guías, conductores y vans para recorrer el archipiélago.', 'Local travel agency in Castro, Chiloé.', content, preload=preload_img('muelle-luz-grupo'))


def guia():
    P = '/guia/'
    tiles = ''.join(f'<li>{tile(g["img"], f"/guia/{g["slug"]}/", L(g["title"]), L("Leer", "Read"))}</li>' for g in D.GUIA)
    content = f'''{bleed_hero("hueñay-playa", h1_lines((L("Historias del", "Stories of the"), False), (L("archipiélago", "archipelago"), True)), L("Guía de Chiloé", "Chiloé guide"), f'<p>{L("Textos publicados por la agencia en su Instagram.", "Texts published by the agency on its Instagram.")}</p>')}
<section class="tgrid"><ul class="tiles2">{tiles}</ul></section>
<section class="sec narrow"><h2 class="h3">{L("Cuándo viajar, clima y cómo llegar a Chiloé", "When to travel, weather and how to reach Chiloé")}</h2><p lang="es">{q(SITE["clima"], P)}</p>{pending(P)}</section>'''
    page(P, 'Guía de Chiloé · Turismo Chiloé Mágico', 'Chiloé guide · Turismo Chiloé Mágico',
         'Curanto, iglesias patrimonio, brujos y almas, la minga y los pingüinos de Puñihuil.', 'Curanto, heritage churches, myths, the minga and Puñihuil penguins.', content, preload=preload_img('hueñay-playa'))
    for g in D.GUIA:
        P = f'/guia/{g["slug"]}/'
        ts = [TOURS[s] for s in g['tours']]
        crumbs = crumbs_html([f'<a href="/">{L("Inicio", "Home")}</a>', f'<a href="/guia/">{L("Guía", "Guide")}</a>', f'<span aria-current="page">{L(g["title"])}</span>'])
        inner = ''.join(q(p, P, 'p') for p in g["paras"]) + f'<p class="note">{L("Fuente: publicaciones de @chiloemagicotour.", "Source: @chiloemagicotour posts.")}</p>'
        content = f'''{bleed_hero(g["img"], h1_lines((L(g["title"]), False)), L("Guía de Chiloé", "Chiloé guide"), '', crumbs, "tall")}
<article class="art"><div class="art__body narrow">{inner}</div></article>
{f'<section class="related"><header class="pkgs__head"><p class="kicker">{L("Vívelo en", "Experience it on")}</p></header>' + trio([tour_tile(t, P, sizes="(max-width:760px) 100vw, 34vw") for t in ts]) + '</section>' if ts else ''}'''
        page(P, f'{g["title"].es} · Guía de Chiloé', f'{g["title"].en} · Chiloé guide', f'{g["title"].es}: guía de Chiloé de Turismo Chiloé Mágico.',
             f'{g["title"].en}: Chiloé guide by Turismo Chiloé Mágico.', content, preload=preload_img(g['img']))


def faq():
    P = '/preguntas-frecuentes/'
    content = f'''{bleed_hero("huillinco-pareja", h1_lines((L("Preguntas", "Frequently asked"), False), (L("frecuentes", "questions"), True)), "FAQ", '', '', "tall")}
<section class="sec narrow">{faq_items(P, D.FAQ)}</section>{booking_cta(P, "Hola! Tengo una consulta", "muelle-luz-oceano")}'''
    page(P, 'Preguntas frecuentes · Turismo Chiloé Mágico', 'FAQ · Turismo Chiloé Mágico',
         'Salidas, horarios, qué incluye, idioma, grupos y reservas de los tours de Turismo Chiloé Mágico.', 'Departures, times, inclusions, language, groups and bookings.', content, preload=preload_img('huillinco-pareja'))


def contacto():
    P = '/contacto/'
    content = f'''{bleed_hero("chonchi", f'<h1 class="h1 h1--light" lang="es" data-lines><span class="line"><span>{q(Q("RESERVA AHORA", "[PIEZA IG-017]"), P)}</span></span></h1>', L("Contacto", "Contact"), f'<p lang="es">{q(SITE["reservas"], P)}: 📲 {SITE["wa_display"]}</p>', '', "tall")}
<section class="sec split">
  <div class="contact__list">
    <p><span class="kicker">WhatsApp</span><a class="big-link" href="{wa_link('Hola! Quiero consultar por los tours')}" target="_blank" rel="noopener">{SITE["wa_display"]}</a></p>
    <p><span class="kicker">{L("Teléfono", "Phone")}</span><a class="big-link" href="tel:+56998833946">{SITE["phone2"]}</a></p>
    <p><span class="kicker">{L("Correo", "Email")}</span><a class="big-link" href="mailto:{SITE["email"]}">{SITE["email"]}</a></p>
    <p><span class="kicker">{L("Dirección", "Address")}</span><span lang="es">{q(SITE["address"], P)}</span></p>
    <p><span class="kicker">{L("Horario", "Hours")}</span><span lang="es">{q(SITE["hours"], P)}</span></p>
  </div>
  {wa_form(P, "contacto")}
</section>
<section class="visit visit--full">{map_block(P)}</section>'''
    page(P, 'Contacto y reservas · Turismo Chiloé Mágico', 'Contact and bookings · Turismo Chiloé Mágico',
         'WhatsApp +56 9 7890 2625, Gamboa 351, Local Interior 116, frente a la Plaza de Armas de Castro. Lunes a domingo 9:00 a 19:30.',
         'WhatsApp +56 9 7890 2625, Gamboa 351, Castro. Mon–Sun 9:00–19:30.', content, preload=preload_img('chonchi'))



def write_copy():
    lines = ['# Guion y fuentes (generado por tools/build.py desde content/site.py)', '',
             'Cada texto visible de la marca, la página donde aparece y su fuente. La interfaz ([UI]) está en los pares data-l del HTML.', '']
    seen = set()
    for pg, text, src, fix in COPY:
        k = (pg, text)
        if k in seen: continue
        seen.add(k)
        lines.append(f'- `{pg}` {src}: «{text}»' + (f' — corrección: {fix}' if fix else ''))
    (ROOT / 'content/copy.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    for d in ['tours', 'destinos', 'experiencias', 'paquetes', 'servicios', 'nosotros', 'guia', 'preguntas-frecuentes', 'contacto']:
        shutil.rmtree(ROOT / d, ignore_errors=True)
    home(); tours_index(); [tour_page(t) for t in D.TOURS]; destinos(); experiencias(); paquetes(); servicios(); nosotros(); guia(); faq(); contacto()
    write_copy()
    if MISSING_ALT:
        sys.exit('ERROR: falta texto alternativo en inglés para: ' + ', '.join(sorted(set(MISSING_ALT))))
    print(f'{len(PAGES)} páginas · {len(COPY)} textos con fuente')
