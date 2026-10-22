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


_W = {}
def w800(key):
    """Ancho real del archivo -800 (las verticales miden 640): el srcset no debe mentir."""
    if key not in _W:
        from PIL import Image
        _W[key] = Image.open(ROOT / f'assets/img/{key}-800.webp').size[0]
    return _W[key]


def img(key, sizes='100vw', cls='', eager=False, extra=''):
    m = META[key]
    en = ALT_EN.get(key)
    if not en:
        MISSING_ALT.append(key)
    s800 = f'/assets/img/{key}-800.webp'
    srcset = f'{s800} {w800(key)}w'
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


DEST_EN = {'Ancud y Puñihuil': 'Ancud and Puñihuil', 'Chonchi e Isla Lemuy': 'Chonchi and Lemuy Island', 'Cucao y Parque Nacional': 'Cucao and the National Park', 'Cucao y Parque Nacional Chiloé': 'Cucao and Chiloé National Park', 'Dalcahue y Quinchao': 'Dalcahue and Quinchao'}


def clp(n, unit=False):
    """Precio: $35.000 (CLP) en español, CLP 35,000 en inglés."""
    es = '$' + f'{n:,}'.replace(',', '.') + (' CLP' if unit else '')
    return f'<span data-l="es">{es}</span><span data-l="en">CLP {n:,}</span>'


def tour_href(t): return f'/tours/{t["slug"]}/'
def dest_href(d): return f'/destinos/{d["slug"]}/'
def exp_href(x): return f'/experiencias/{x["slug"]}/'


NAV = [
    ('/', U('Inicio', 'Home'), 'huillinco-pareja'),
    ('/tours/', U('Tours', 'Tours'), 'punihuil-bahia'),
    ('/paquetes/', U('Paquetes', 'Packages'), 'valdivia'),
    ('/nosotros/', U('Nosotros', 'About us'), 'nicolas-enrique'),
    ('/contacto/', U('Contacto', 'Contact'), 'palafitos'),
]


def header(current, wa_text):
    links = ''.join(f'<li><a href="{h}"{" aria-current=page" if (current == h if h == "/" else current.startswith(h)) else ""}>{L(lbl)}</a></li>' for h, lbl, _ in NAV)
    menu_links = ''.join(
        f'<li><a href="{h}" data-menu-img="{k}" class="menu__link"><span class="menu__n">0{i+1}</span>{L(lbl)}</a></li>'
        for i, (h, lbl, k) in enumerate(NAV))
    menu_imgs = ''.join(f'<div class="menu__img" data-menu-key="{k}">{img(k, "40vw")}</div>' for _, _, k in NAV)
    return f'''<header class="hdr" data-hdr>
  <a class="hdr__logo" href="/" aria-label="Turismo Chiloé Mágico, inicio" data-aria-en="Turismo Chiloé Mágico, home">
    <img src="/brand/logo/logo-color.svg" width="1812" height="965" alt="" class="hdr__logo-c">
    <img src="/brand/logo/logo-white.svg" width="1812" height="965" alt="" class="hdr__logo-w">
  </a>
  <nav class="hdr__nav" aria-label="Principal" data-aria-en="Main"><ul>{links}</ul></nav>
  <div class="hdr__tools">
    <button class="lang" type="button" data-lang-toggle><span class="sr">{L("Idioma:", "Language:")} </span><span class="lang__es" lang="es">ES</span><span class="lang__sep" aria-hidden="true">·</span><span class="lang__en" lang="en">EN</span></button>
    {btn(L("Cotizar", "Quote"), wa_link(wa_text), "btn btn--sm btn--red hdr__cta", True)}
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
    <a href="{wa_link('¡Hola! Quiero cotizar un tour.')}" target="_blank" rel="noopener">WhatsApp {SITE["wa_display"]}</a>
    <a href="{SITE["instagram"]}" target="_blank" rel="noopener">Instagram @chiloemagicotour</a>
  </div>
</div>'''


def footer(page):
    nav = ''.join(f'<li><a href="{h}">{L(lbl)}</a></li>' for h, lbl, _ in NAV)
    return f'''<footer class="ftr">
  <svg class="ftr__wave" viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true"><path d="M0,120 L0,70 C360,10 820,0 1440,58 L1440,120 Z"/></svg>
  <div class="ftr__in">
    <div class="ftr__brand">
      <img src="/brand/logo/logo-sticker.svg" width="1912" height="1065" alt="Turismo Chiloé Mágico" data-alt-en="Turismo Chiloé Mágico" loading="lazy" class="ftr__logo">
      <p class="ftr__slogan" lang="es">{q(Q("Chiloé Mágico te espera. ¡Ven a descubrirlo!", "[BIO]", fix="puntuación: «te espera, Ven a descubrirlo!»"), page)}</p>
    </div>
    <div class="ftr__act">
      <p class="ftr__addr"><a href="{wa_link('¡Hola! Quiero cotizar un tour.')}" target="_blank" rel="noopener">WhatsApp {SITE["wa_display"]}</a><br><span lang="es">{q(SITE["address_short"], page)}</span><br><span lang="es">{q(SITE["hours"], page)}</span></p>
    </div>
  </div>
  <nav class="ftr__nav" aria-label="Pie de página" data-aria-en="Footer"><ul>{nav}<li><a href="/guia/">{L("Guía de Chiloé", "Chiloé guide")}</a></li><li><a href="/preguntas-frecuentes/">{L("Preguntas frecuentes", "FAQ")}</a></li><li><a href="{SITE["instagram"]}" target="_blank" rel="noopener">Instagram</a></li></ul></nav>
  <p class="ftr__base">© Turismo Chiloé Mágico · Castro, Chiloé</p>
</footer>'''


def wa_float(text):
    return (f'<aside aria-label="WhatsApp"><a class="wa" href="{wa_link(text)}" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp" data-aria-en="Message us on WhatsApp">'
            '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3a13 13 0 0 0-11.2 19.6L3 29l6.6-1.7A13 13 0 1 0 16 3zm0 23.6c-2 0-4-.6-5.7-1.6l-.4-.2-3.9 1 1-3.8-.3-.4A10.6 10.6 0 1 1 16 26.6zm5.8-7.9c-.3-.2-1.9-.9-2.2-1-.3-.1-.5-.2-.7.2l-1 1.2c-.2.2-.4.2-.7.1-.3-.2-1.4-.5-2.6-1.6-1-.9-1.6-1.9-1.8-2.2-.2-.3 0-.5.1-.7l.5-.6.3-.5c.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.2 1.4 3.5c.2.2 2.4 3.6 5.7 5 .8.4 1.4.6 1.9.7.8.3 1.5.2 2.1.1.6-.1 1.9-.8 2.2-1.5.3-.7.3-1.4.2-1.5l-.7-.4z"/></svg>'
            f'<span class="wa__t">{L("Cotizar", "Quote")}</span></a></aside>')


def ld_business():
    return {"@context": "https://schema.org", "@type": "TravelAgency", "name": SITE['name'], "url": DOMAIN + '/',
            "image": DOMAIN + '/assets/og.jpg', "logo": DOMAIN + '/brand/logo/logo-color.png', "telephone": '+' + SITE['wa'],
            "email": SITE['email'], "address": {"@type": "PostalAddress", "streetAddress": "Av. Gamboa 351, Galería Alonso de Ercilla, Local Interior 116",
            "addressLocality": "Castro", "addressRegion": "Los Lagos", "addressCountry": "CL"},
            "geo": {"@type": "GeoCoordinates", "latitude": SITE['lat'], "longitude": SITE['lng']},
            "openingHours": "Mo-Su 09:00-19:30", "sameAs": [SITE['instagram']],
            "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.9", "reviewCount": SITE['reviews_count']}}


EN = json.loads((ROOT / 'content/en.json').read_text())
_EN_RX = None


def translate(html):
    """Todo texto marcado lang="es" que tenga traducción pasa a llevar su par en inglés (el botón ES · EN lo alterna)."""
    global _EN_RX
    for es in sorted(EN, key=len, reverse=True):
        for raw in {es, es.replace('"', '&quot;')}:
            rx = re.compile(r'(<(\w+)\b[^>]*?)\slang="?es"?([^>]*>)' + re.escape(raw) + r'(</\2>)')
            html = rx.sub(lambda m, raw=raw, es=es: f'{m.group(1)}{m.group(3)}<span data-l="es" lang="es">{raw}</span><span data-l="en" lang="en">{EN[es]}</span>{m.group(4)}', html)
    return html


def page(path, title, title_en, desc, desc_en, content, body_class='', wa_text='¡Hola! Quiero cotizar un tour.', ld=None, preload=''):
    PAGES.append(path)
    url = DOMAIN + path
    out = LAYOUT
    import hashlib
    for rel in ('css/main.css', 'js/main.js'):
        v = hashlib.sha1((ROOT / rel).read_bytes()).hexdigest()[:10]
        out = out.replace(f'"/{rel}"', f'"/{rel}?v={v}"')
    def brand_first(t):
        for s in (' · Turismo Chiloé Mágico', 'Turismo Chiloé Mágico · '):
            t = t.replace(s, '')
        return 'Chiloé Mágico Tour'
    title, title_en = brand_first(title), brand_first(title_en)
    rep = {'title': e(title), 'title_en': e(title_en), 'desc': e(desc), 'desc_en': e(desc_en), 'url': url, 'domain': DOMAIN,
           'jsonld': json.dumps(ld or ld_business(), ensure_ascii=False).replace('</', '<\\/'), 'body_class': body_class,
           'header': header(path, wa_text), 'footer': footer(path), 'wa': wa_float(wa_text), 'content': content, 'preload': preload}
    for k, v in rep.items():
        out = out.replace('{{' + k + '}}', v)
    dest = ROOT / (path.strip('/') + '/index.html' if path != '/' else 'index.html')
    dest.parent.mkdir(parents=True, exist_ok=True)
    out = translate(out)
    # ningún emoji en pantalla (las estrellas de valoración se quedan)
    out = re.sub(r' ?[\U0001F000-\U0001FAFF\u2600-\u2604\u2606-\u27BF\uFE0F]+', '', out)
    dest.write_text(out)


def preload_img(key):
    m = META[key]
    if m['big']:
        return (f'<link rel="preload" as="image" href="/assets/img/{key}-1800.webp" imagesrcset="/assets/img/{key}-800.webp {w800(key)}w, '
                f'/assets/img/{key}-1800.webp {m["w"]}w" imagesizes="100vw" fetchpriority="high">')
    return f'<link rel="preload" as="image" href="/assets/img/{key}-800.webp" fetchpriority="high">'


# ------------------------------------------------------------------ bloques
def tour_card(t, page, sizes='(max-width: 760px) 80vw, 30vw'):
    price = (f'<span class="card__price">{L("Desde", "From")} {clp(t["price_from"])}<span data-l="es"> <abbr title="pesos chilenos">CLP</abbr></span></span>'
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
    'brujos-columpio': '68% 18%', 'brujos-columpio-2': '50% 30%', 'almas': '50% 35%', 'parque-bosque': '50% 40%',
    'curanto-destape': '50% 45%', 'tocoihue': '50% 40%', 'caleuche': '50% 55%', 'curaco': '50% 60%', 'curaco-2': '50% 50%',
    'mechuque': '50% 55%', 'palafitos': '50% 78%', 'punihuil-navega': '50% 40%', 'tenaun': '50% 35%', 'brujos-vuelo': '50% 45%',
    'yayanes-puente': '50% 45%', 'huillinco-columpio': '50% 40%', 'aucar-isla': '50% 55%', 'curanto-fuego': '50% 50%',
    'nercon': '50% 40%', 'brujos-alas': '50% 40%', 'punihuil-islote': '50% 50%', 'minga': '50% 55%',
    'palafitos': '50% 92%', 'vans': '50% 70%', 'nicolas-enrique': '25% 45%', 'valdivia': '50% 28%', 'muelle-luz-grupo': '60% 40%', 'parque-muelle': '50% 55%',
}


FORCE = {'nicolas-enrique', 'valdivia'}


def bimg(key, sizes='100vw', eager=False):
    """Imagen a sangre: cubre su contenedor con el punto focal de la foto."""
    m = META[key]
    pos = FOCUS[key] if key in FORCE else (m['pos'] if m.get('pos_src') == 'rostros' else (FOCUS.get(key) or m.get('pos', '50% 45%')))
    return img(key, sizes, 'bleed__img', eager, f'data-pos="{pos}"').replace(
        'style="background-image', f'style="object-position:{pos};background-image', 1)


def credit(key, cls='credit'):
    c = META[key].get('credit')
    if not c: return ''
    txt, url = c.split('|')
    lab = L(e(txt), e(txt.replace('Foto:', 'Photo:', 1))) if txt.startswith('Foto:') else e(txt)
    return f'<a class="{cls}" href="{url}" target="_blank" rel="noopener">{lab}</a>'


def wide(key):
    """Solo una foto panorámica soporta la franja de encabezado (≈2:1 o más) sin perder el paisaje."""
    m = META[key]; return m['w'] / m['h'] >= 1.7 and m['w'] >= 1100


def bleed_hero(key, title_html, kicker='', lead='', crumbs='', size='full', extra=''):
    """Encabezado de página a pantalla completa, con el título sobre el paisaje.
    Si la foto es vertical o cuadrada no se estira a lo ancho: ocupa la mitad derecha a altura completa."""
    m = META[key]
    split = '' if wide(key) else (' bhero--split bhero--land' if m['w'] / m['h'] >= 1.2 else ' bhero--split')
    return f'''<section class="bhero bhero--{size}{split}" data-hero>
  <div class="bhero__media" data-parallax-hero>{bimg(key, "100vw" if not split else "(max-width:760px) 100vw, 50vw", True)}</div>{credit(key)}
  <div class="bhero__shade" aria-hidden="true"></div>
  {crumbs}
  <div class="bhero__in">
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
        return clp(t["price_from"], unit=True)
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
        tour = f' · <a href="{tour_href(TOURS[r["tour"]])}">{L(e(TOURS[r["tour"]]["short"]), e(EN.get(TOURS[r["tour"]]["short"], TOURS[r["tour"]]["short"])))}</a>' if r.get('tour') else ''
        slides += (f'<figure class="rev swiper-slide"><div class="rev__stars" role="img" aria-label="5 de 5 estrellas" data-aria-en="5 out of 5 stars">{STARS}</div>'
                   f'<blockquote lang="{r["lang"]}">“{q(r["text"], page)}”</blockquote>'
                   f'<figcaption><strong>{e(r["name"])}</strong>{frm} · {L("vía Google", "via Google")}{tour}</figcaption></figure>')
    head = (f'<header class="reviews__head"><p class="kicker kicker--light">{L("Testimonios", "Reviews")}</p>'
            f'<h2 class="h2 h2--light" data-lines><span class="line"><span>{SITE["rating"]} ★ </span></span><span class="line"><span>{L("en Google", "on Google")}</span></span></h2>'
            f'<p class="lead lead--light">{L(f"{SITE["reviews_count"]} reseñas leídas el 19 de octubre de 2026. Las citas van en su idioma original.", f"{SITE["reviews_count"]} reviews read on 19 October 2026. Reviews written in Spanish are translated; read the originals on Google Maps.")}</p></header>') if title else ''
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
  <button class="map__lock" type="button" data-map-lock><span>{L("Toca para mover el mapa", "Tap to use the map")}</span></button>
  <iframe title="Mapa: Gamboa 351, Castro" data-title-en="Map: Gamboa 351, Castro" data-src="https://www.openstreetmap.org/export/embed.html?bbox=-73.7702%2C-42.4846%2C-73.7582%2C-42.4786&amp;layer=mapnik&amp;marker=-42.4816941%2C-73.7642726" loading="lazy" referrerpolicy="no-referrer"></iframe>
</div>'''


def sticky_split(key, inner_html, side='right', extra_keys=(), force_sm=False):
    """Texto que corre junto a un paisaje fijo que toca el borde de la pantalla (sticky, sin pin)."""
    more = trio([f'<div class="tile tile--pic" data-parallax>{bimg(k, "(max-width:760px) 100vw, 50vw")}</div>' for k in extra_keys]) if extra_keys else ''
    sm = ' ssplit--sm' if META[key]['w'] < 1000 or force_sm else ''
    return f'''<section class="ssplit ssplit--{side}{sm}">
  <div class="ssplit__media"><div class="ssplit__stick" data-parallax>{bimg(key, "(max-width:760px) 100vw, 50vw")}</div>{credit(key, "credit credit--below" if sm else "credit")}</div>
  <div class="ssplit__txt" data-rv>{inner_html}</div>
</section>{more}'''


# ------------------------------------------------------------------ v5: cada tour se explica solo
STARS = '<svg class="stars5" viewBox="0 0 100 18" aria-hidden="true"><path d="M9 1l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L9 13.4 4 16.2l1.2-5.6L1 6.8l5.6-.6zM29 1l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L29 13.4 24 16.2l1.2-5.6L21 6.8l5.6-.6zM49 1l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L49 13.4 44 16.2l1.2-5.6L41 6.8l5.6-.6zM69 1l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L69 13.4 64 16.2l1.2-5.6L61 6.8l5.6-.6zM89 1l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L89 13.4 84 16.2l1.2-5.6L81 6.8l5.6-.6z"/></svg>'

def det(t): return D.DETAIL[t['slug']]


def price_short(t):
    return (f'<strong>{clp(t["price_from"])}</strong> <span class="u-small">{L("por persona", "per person")}</span>'
            if t.get('price_from') else f'<span class="u-muted">{L("Precio según fecha y grupo", "Price depends on date and group")}</span>')


def trow(t, P, sizes='(max-width:700px) 92vw, (max-width:1099px) 46vw, 25vw', h='h3'):
    """Fila de tour: foto + qué es + horario/almuerzo + precio. Toda la fila es el enlace."""
    d = det(t)
    return f'''<li class="tr" data-rv><a class="tr__a" href="{tour_href(t)}">
  <div class="tr__img">{bimg(t["card"], sizes)}</div>
  <div class="tr__txt">
    <{h} class="tr__t" lang="es">{e(t["short"])}</{h}>
    <p class="tr__que">{L(d["corto"])}</p>
    <ul class="tr__tags">{''.join(f'<li>{L(x)}</li>' for x in d["tags"])}</ul>
    <p class="tr__meta"><span class="tr__ml">{L("Almuerzo:", "Lunch:")}</span> <span>{L(d["lunch"])}</span></p>
    <p class="tr__foot"><span class="tr__price">{price_short(t)}</span><span class="tr__go">{L("Ver tour", "See tour")} <span aria-hidden="true">→</span></span></p>
  </div>
</a></li>'''


def tour_list(P, items, cls='', h='h3'):
    return f'<ul class="tl {cls}">' + ''.join(trow(t, P, h=h) for t in items) + '</ul>'


def reviews_solid(page, items, head=None):
    slides = ''
    for r in items:
        frm = f' · <span lang="es">desde {e(r["from"])}</span>' if r.get('from') else ''
        tour = f' · <a href="{tour_href(TOURS[r["tour"]])}">{L(e(TOURS[r["tour"]]["short"]), e(EN.get(TOURS[r["tour"]]["short"], TOURS[r["tour"]]["short"])))}</a>' if r.get('tour') else ''
        slides += (f'<figure class="rev swiper-slide"><div class="rev__stars" role="img" aria-label="5 de 5 estrellas" data-aria-en="5 out of 5 stars">{STARS}</div>'
                   f'<blockquote lang="{r["lang"]}">“{q(r["text"], page)}”</blockquote>'
                   f'<figcaption><strong>{e(r["name"])}</strong>{frm} · {L("vía Google", "via Google")}{tour}</figcaption></figure>')
    return f'''<section class="rsec" aria-labelledby="rsec-t">{WAVE}
  <header class="rsec__head" data-rv>
    {head or f'''<h2 class="h2 h2--light" id="rsec-t">{L(f"{SITE['rating']} <em>en</em> Google", f"{SITE['rating_en']} <em>on</em> Google")}</h2>
    <p class="rsec__sub">{STARS} {L(f"{SITE['reviews_count']} reseñas de viajeros. Las citas van en su idioma original.", f"{SITE['reviews_count']} traveller reviews. Reviews written in Spanish are translated.")}</p>'''}
  </header>
  <div class="swiper rsec__sw" data-swiper="reviews" data-drag><div class="swiper-wrapper">{slides}</div></div>
  <div class="snav snav--light"><button class="arrow arrow--light" type="button" data-prev aria-label="Reseña anterior" data-aria-en="Previous review">←</button><button class="arrow arrow--light" type="button" data-next aria-label="Reseña siguiente" data-aria-en="Next review">→</button>
  <a class="u-link u-link--light" href="https://www.google.com/maps/place/Turismo+Chilo%C3%A9+M%C3%A1gico/@-42.4816941,-73.7642726,17z" target="_blank" rel="noopener">{L("Leer todas en Google Maps", "Read them all on Google Maps")}</a></div>
</section>'''


def closing(page, text, key='punihuil-bahia'):
    """Cierre: una foto, una frase corta, WhatsApp y dónde estamos."""
    COPY.append((page, '¡No dejes que te lo cuenten! / Ven a disfrutar de esta mágica isla junto a nosotros', '[IG-007]', 'remate partido en dos: título y frase'))
    return f'''<section class="bcta bcta--red" aria-labelledby="bcta-t">
  {GULL}
  <div class="bcta__pols" aria-hidden="true"><div class="pol2 pol2--a">{bimg(key, "(max-width:760px) 60vw, 26vw")}</div><div class="pol2 pol2--b">{bimg("muelle-luz-oceano", "(max-width:760px) 50vw, 22vw")}</div><div class="pol2 pol2--c">{bimg("curanto-destape", "(max-width:760px) 44vw, 18vw")}</div></div>
  <div class="bcta__in">
    <h2 class="bcta__big" id="bcta-t" lang="es">¡No dejes que te lo <em>cuenten</em>!</h2>
    <p class="bcta__p" lang="es">Ven a disfrutar de esta mágica isla junto a nosotros.</p>
    <div class="cta__row">{btn(L("Cotizar por WhatsApp", "Get a quote on WhatsApp"), wa_link(text), "btn btn--red", True)}</div>
  </div>
</section>'''


WAVE = '<svg class="wave" viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true"><path d="M0,120 L0,70 C360,10 820,0 1440,58 L1440,120 Z"/></svg>'
GULL = '<svg class="gull" viewBox="0 0 100 100" aria-hidden="true"><path d="M4,4 C22,16 42,36 56,55 C62,53 70,52 78,53 C82,53.5 85,55 86,57 C83,59 79,60 75,61 C82,72 90,85 97,98 C86,88 75,76 66,65 C58,66 50,67 44,69 C47,66 50,63 52,61 C40,42 22,20 4,4 Z"/></svg>'


def wave(fill, flip=False):
    """Ola entre dos campos de color (la misma curva del logo y del footer)."""
    return (f'<svg class="wave{" wave--top" if flip else ""}" viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true">'
            f'<path d="M0,120 L0,70 C360,10 820,0 1440,58 L1440,120 Z" fill="{fill}"/></svg>')


def seal(top, bottom, ring, sid='sr'):
    return f'''<svg class="seal" viewBox="0 0 200 200" aria-hidden="true"><defs><path id="{sid}" d="M100,100 m-74,0 a74,74 0 1,1 148,0 a74,74 0 1,1 -148,0"/></defs>
  <circle cx="100" cy="100" r="98" fill="#d0342c"/><circle cx="100" cy="100" r="91" fill="none" stroke="#fff" stroke-width="2"/><circle cx="100" cy="100" r="58" fill="none" stroke="#fff" stroke-width="1.5"/>
  <text font-family="Montserrat, sans-serif" font-weight="700" font-size="11" fill="#fff"><textPath href="#{sid}" textLength="462" lengthAdjust="spacing">{ring}</textPath></text>
  <text x="100" y="97" text-anchor="middle" font-family="Anton, sans-serif" font-size="30" fill="#fff">{top}</text>
  <text x="100" y="128" text-anchor="middle" font-family="Anton, sans-serif" font-size="30" fill="#fff">{bottom}</text></svg>'''


def facts_strip(P):
    return f'''<ul class="meds2" data-rv aria-label="Datos de la agencia" data-aria-en="Agency facts">
  <li class="md2 md2--red"><strong>{L(SITE["rating"], SITE["rating_en"])}</strong><span>{L(f"en Google · {SITE['reviews_count']} reseñas", f"on Google · {SITE['reviews_count']} reviews")}</span></li>
  <li class="md2 md2--cream"><strong>{L("10:00", "10am")}</strong><span>{L("salida todos los días", "departure every day")}</span></li>
  <li class="md2 md2--blue"><strong>16</strong><span>{L("pasajeros máx. por van", "passengers max. per van")}</span></li>
  <li class="md2 md2--sand"><strong>{L("Castro", "Castro")}</strong><span>{L("frente a la Plaza de Armas", "facing the main square")}</span></li>
</ul>'''


def home():
    P = '/'
    COPY.append((P, 'Tours en Chiloé desde Castro', 'título de interfaz', None))
    content = f'''
<section class="hero" data-hero>{WAVE}
  <a class="hero__seal" href="#tours" aria-label="Ver los tours" data-aria-en="See the tours"><span data-l="es">{seal("TOURS", "DIARIOS", "DESDE CASTRO ★ CHILOÉ MÁGICO ★ 10:00 A 19:00 ★ ")}</span><span data-l="en">{seal("DAILY", "TOURS", "FROM CASTRO ★ CHILOÉ MÁGICO ★ 10AM TO 7PM ★ ", "sr-en")}</span></a>
  <div class="hero__media" data-parallax-hero>{img("huillinco-columpio", "100vw", "", True)}</div>
  <div class="hero__shade" aria-hidden="true"></div>
  <div class="hero__in">
    <h1 class="hero__t" data-lines><span class="line"><span>{L("Tours en Chiloé", "Chiloé tours")}</span></span><span class="line"><span>{L("desde Castro", "from Castro")}</span></span></h1>
    <p class="hero__sub" lang="es">{q(Q("Nuestro archipiélago es mágico. ¡Ven a descubrirlo!", "[BIO]", fix="se agrega el punto antes de ¡"), P)}</p>
    <div class="hero__ctas">{btn(L("Ver los tours", "See the tours"), "#tours", "btn btn--light")}{btn(L("Cotizar por WhatsApp", "Get a quote on WhatsApp"), wa_link("¡Hola! Quiero cotizar un tour."), "btn btn--red", True)}</div>
  </div>
</section>



<section class="tsec" id="tours" aria-labelledby="tours-t">{WAVE}
  <header class="tsec__head" data-rv>
    <h2 class="h2" id="tours-t">{L("Elige <em>tu</em> tour", "Choose <em>your</em> tour")}</h2>
    <p class="tsec__lead">{L("Tours de día completo desde Castro.", "Full-day tours from Castro.")} {L("Todos incluyen traslado, guía, almuerzo y bebestibles.", "All include transport, guide, lunch and drinks.")}</p>
  </header>
  {facts_strip(P)}
  {tour_list(P, D.TOURS)}
</section>

<section class="pksec pksec--home" aria-labelledby="pkh-t">{WAVE}
  <header class="tsec__head" data-rv>
    <h2 class="h2" id="pkh-t">{L("Paquetes", "Packages")}</h2>
    <p class="tsec__lead" lang="es">{qx(SITE["privados"], "Servicio de turismo, traslado y viajes privados", P, fix="recorte; mayúscula inicial")}</p>
  </header>
  <ul class="pks pks--mini">{''.join(pkg_card(p, P, mini=True) for p in D.PAQUETES)}</ul>
  <p class="pksec__cta">{btn(f'{L("Ver paquetes", "See packages")} <span aria-hidden="true">→</span>', "/paquetes/", "btn btn--light")}</p>
</section>

<section class="isla" aria-labelledby="isla-t" data-isla>{WAVE}
  <div class="isla__stick">
    <div class="isla__blur" aria-hidden="true"><video class="isla__vbg" muted playsinline loop preload="none" data-lazy-video aria-hidden="true" tabindex="-1"><source data-src="/assets/video/isla.webm" type="video/webm"><source data-src="/assets/video/isla.mp4" type="video/mp4"></video></div>
    <video class="isla__v" muted playsinline loop preload="none" data-lazy-video data-poster="/assets/video/isla-poster.jpg" aria-label="{e(META['_videos']['isla']['alt'])}" data-aria-en="{e(ALT_EN['vid:isla'])}">
      <source data-src="/assets/video/isla.webm" type="video/webm"><source data-src="/assets/video/isla.mp4" type="video/mp4">
    </video>
    <div class="isla__cover" aria-hidden="true"></div>
    <div class="isla__shade" aria-hidden="true"></div>
    <div class="isla__t" data-isla-t>
      <h2 class="isla__h" id="isla-t" lang="es">{q(Q("¿Vamos a navegar? 🌊", "[IG-015]", fix="se agrega el signo de apertura ¿"), P)}</h2>
      <p class="isla__q">{L("Entre los islotes de Puñihuil, donde anidan los pingüinos.", "Among the Puñihuil islets, where the penguins nest.")} <a href="{tour_href(TOURS["pinguineras-punihuil"])}">{L("Ver el tour", "See the tour")} →</a></p>
    </div>
  </div>
</section>

<section class="abh" aria-labelledby="abh-t">{WAVE}
  <div class="bcta__pols abh__pols" aria-hidden="true"><div class="pol2 pol2--a">{bimg("nicolas-enrique", "(max-width:760px) 60vw, 26vw")}</div><div class="pol2 pol2--b">{bimg("grupo-van", "(max-width:760px) 50vw, 22vw")}</div><div class="pol2 pol2--c">{bimg("brujos-vuelo", "(max-width:760px) 44vw, 18vw")}</div></div>
  <div class="abh__txt" data-rv>
    <h2 class="h2" id="abh-t" lang="es">{qx(SITE["somos"], "Somos Chiloé Mágico", P, em="Mágico")}</h2>
    <p class="abh__p" lang="es">{qx(SITE["anos"], "Somos una empresa dedicada al rubro turístico, con más de 20 años de servicio", P)}</p>
    <p class="abh__cta">{btn(f'{L("Conócenos", "About us")} <span aria-hidden="true">→</span>', "/nosotros/", "btn btn--red")}</p>
  </div>
</section>

{reviews_solid(P, D.REVIEWS)}

{closing(P, "¡Hola! Quiero cotizar un tour.")}
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
    content = f'''<section class="phead2">
  <div class="phead2__in">
    <h1 class="h1">{L("Nuestros tours", "Our tours")}</h1>
    <p class="phead2__p">{L("Elige uno y cotízalo por WhatsApp. Todos incluyen traslado desde Castro, guía, almuerzo y bebestibles.", "Pick one and get a quote on WhatsApp. All include transport from Castro, guide, lunch and drinks.")}</p>
  </div>
</section>
<section class="tsec tsec--page" aria-label="Todos los tours" data-aria-en="All tours">{WAVE}
  {facts_strip(P)}
  {tour_list(P, D.TOURS, h='h2')}
</section>
{closing(P, "¡Hola! Quiero cotizar un tour.")}'''
    page(P, 'Tours en Chiloé desde Castro · Turismo Chiloé Mágico', 'Chiloé tours from Castro · Turismo Chiloé Mágico',
         'Tours de día completo desde Castro con traslado, guiado, almuerzo y bebestibles.',
         'Full-day tours from Castro with transport, guiding, lunch and drinks.', content)


def tour_page(t):
    """La ficha explica el tour completo y termina ofreciendo 3 tours afines y la lista entera."""
    P = tour_href(t); d = det(t)
    ld = {"@context": "https://schema.org", "@type": "TouristTrip", "name": t['short'], "touristType": "Grupos",
          "description": d['que'].es, "image": f"{DOMAIN}/assets/img/{t['hero']}-800.webp", "url": DOMAIN + P,
          "provider": {"@type": "TravelAgency", "name": SITE['name'], "telephone": '+' + SITE['wa'], "url": DOMAIN + '/'}}
    if t.get('price_from'):
        ld['offers'] = {"@type": "Offer", "price": t['price_from'], "priceCurrency": "CLP"}
    wa_t = f'¡Hola! Quiero cotizar el {t["short"]}.'
    a, s, b = t['title']
    COPY.append((P, f'{a} {s} {b}', t['afiche'] + ' título del afiche', None))
    sub = f'{s} {b}'.strip()
    title = (f'<h1 class="tt" lang="es"><span class="tt__a">{e(a.title() if a.isupper() else a)}</span>'
             f'{f"<span class=tt__b> {e(sub[0].upper() + sub[1:].lower() if sub.isupper() else sub)}</span>" if sub else ""}</h1>')
    title = f'<h1 class="tt" lang="es">{e(t["short"])}</h1>'
    if t['stops']:
        COPY.append((P, ' · '.join(t['stops']), t['afiche'] + ' rótulos de paradas', None))
    pts = ''.join(f'<li>{L(x)}</li>' for x in d['pts'])
    stops = ''.join(f'<li><span lang="es">{e(x)}</span></li>' for x in t['stops'])
    no = ''.join(f'<li>{L(x)}</li>' for x in d['no'])
    photos = [k for k in t['gallery'] if k != t['hero']][:6]
    gallery = ''.join(f'<div class="swiper-slide tf">{bimg(k, "(max-width:760px) 80vw, 30vw")}</div>' for k in photos)
    revs = [r for r in D.REVIEWS if r.get('tour') == t['slug']][:2]
    rel = [TOURS[x] for x in d['rel']]
    lead = f'<figure class="tw__quote"><blockquote lang="es">“{q(t["lead"], P)}”</blockquote><figcaption>{L("Chiloé Mágico en Instagram", "Chiloé Mágico on Instagram")}</figcaption></figure>' if t.get('lead') else ''
    season = f'<p class="note">{L(d["season"])}</p>' if d.get('season') else ''
    guide = [g for g in D.GUIA if g['slug'] in d.get('guia', [])]
    guide_html = ''.join(f'<li><a class="u-link" href="/guia/{g["slug"]}/">{L(g["title"])}</a></li>' for g in guide)
    content = f'''<section class="th th--split" data-hero>{WAVE}
  <div class="th__media" data-parallax-hero>{bimg(t["hero"], "100vw", True)}</div>{credit(t["hero"])}
  <div class="th__shade" aria-hidden="true"></div>
  <a class="back" href="/tours/"><span aria-hidden="true">←</span> {L("Todos los tours", "All tours")}</a>
  <div class="th__in">
    {title}
    <p class="th__que">{L(d["que"])}</p>
    <div class="th__ctas">{btn(L("Cotizar este tour", "Get a quote"), "#cotizar", "btn btn--red")}<a class="th__more" href="#detalle">{L("Ver qué harás", "See what you'll do")} <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="M8 3v10M3.5 8.5 8 13l4.5-4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></a></div>
  </div>
</section>

<section class="tq" id="detalle" aria-label="Datos del tour" data-aria-en="Tour facts">{WAVE}
  <dl class="tq__dl" data-rv>
    <div><dt>{L("Duración", "Duration")}</dt><dd>{L("Día completo, 10:00 a 19:00 aprox.", "Full day, 10am to 7pm approx.")}</dd></div>
    <div><dt>{L("Salida", "Departure")}</dt><dd>{L("Agencia frente a la Plaza de Armas de Castro", "Agency facing Castro's main square")}</dd></div>
    <div><dt>{L("Almuerzo", "Lunch")}</dt><dd class="u-cap">{L(d["lunch"])}</dd></div>
    <div><dt>{L("Precio", "Price")}</dt><dd>{price_short(t)}</dd></div>
  </dl>
</section>

<section class="tw" aria-labelledby="tw-t">{WAVE}
  <div class="tw__in">
    <div class="tw__main">
      <h2 class="h2" id="tw-t">{L("Lo que <em>harás</em>", "What you'll <em>do</em>")}</h2>
      <ul class="tw__list" data-rv>{pts}</ul>
      {lead}
      <h2 class="h2 tw__h2" id="tin-t">{L("Qué <em>incluye</em>", "What\'s <em>included</em>")}</h2>
      <div class="tin__grid" data-rv>
      <div><h3 class="h4">{L("Incluye", "Included")}</h3><ul class="inclist"><li>{L("Traslado en van desde Castro, ida y vuelta", "Round-trip van transport from Castro")}</li><li>{L("Guía durante todo el día", "Guide for the whole day")}</li><li>{L("Almuerzo y bebestibles", "Lunch and drinks")}</li></ul></div>
      <div>{f'<h3 class="h4">{L("No incluye", "Not included")}</h3><ul class="nolist">{no}</ul>' if no else ''}
      {season}
      {f'<h3 class="h4">{L("Para saber más", "Learn more")}</h3><ul class="guidelist">{guide_html}</ul>' if guide_html else ''}
      <p class="note">{L("Mínimo de pasajeros, niños y cancelación: pregúntanos por WhatsApp.", "Minimum group, children and cancellation: ask us on WhatsApp.")}</p></div>
      </div>
    </div>
    <aside class="tbox" aria-label="Cotizar" data-aria-en="Get a quote">
      <div class="tbox__in">
        <p class="tbox__name" lang="es">{e(t["short"])}</p>
        <p class="tbox__price">{price_short(t)}</p>
        <ul class="tbox__list"><li>{L("Día completo, 10:00 a 19:00", "Full day, 10am to 7pm")}</li><li>{L("Traslado, guía, almuerzo y bebestibles", "Transport, guide, lunch and drinks")}</li><li>{L("Sale frente a la Plaza de Armas de Castro", "Leaves from Castro's main square")}</li></ul>
        {btn(L("Cotizar este tour", "Get a quote"), "#cotizar", "btn btn--red btn--full")}
        <p class="tbox__alt"><a class="u-link" href="{wa_link(wa_t)}" target="_blank" rel="noopener">{L("¿Dudas? Escríbenos por WhatsApp", "Questions? Message us on WhatsApp")}</a></p>
      </div>
    </aside>
  </div>
</section>

{f"""<section class="tfotos" aria-labelledby="tf-t">{WAVE}
  <header class="tfotos__head" data-rv><h2 class="h2 h2--light" id="tf-t">{L("Así se <em>vive</em>", "What it <em>looks</em> like")}</h2><p>{L("Fotos de la agencia en este tour. Desliza para ver más.", "Our photos from this tour.")}</p></header>
  <div class="swiper tfsw" data-swiper="gallery" data-drag><div class="swiper-wrapper">{gallery}</div></div>
  <div class="snav snav--light"><button class="arrow arrow--light" type="button" data-prev aria-label="Foto anterior" data-aria-en="Previous photo">←</button><button class="arrow arrow--light" type="button" data-next aria-label="Foto siguiente" data-aria-en="Next photo">→</button></div>
</section>""" if photos else ''}



<section class="meet" aria-labelledby="meet-t">{WAVE}
  <div class="meet__txt" data-rv>
    <h2 class="h2" id="meet-t">{L("Punto de <em>encuentro</em>", "Meeting <em>point</em>")}</h2>
    <p lang="es">{q(SITE["address_short"], P)}</p>
    <p lang="es">{q(SITE["salida"], P)}.</p>
    <a class="u-link" href="https://www.google.com/maps/dir/?api=1&amp;destination=-42.4816941,-73.7642726" target="_blank" rel="noopener">{L("Cómo llegar en Google Maps", "Directions on Google Maps")}</a>
  </div>
  {map_block(P)}
</section>

{f"""<section class="trev" aria-labelledby="trev-t">{WAVE}<div class="trev__in"><h2 class="h2" id="trev-t">{L("Lo que <em>cuentan</em> de este tour", "What travellers <em>say</em>")}</h2><div class="trev__grid" data-rv>""" + ''.join(f'<figure class="rev"><div class="rev__stars" role="img" aria-label="5 de 5 estrellas" data-aria-en="5 out of 5 stars">{STARS}</div><blockquote lang="{r["lang"]}">“{q(r["text"], P)}”</blockquote><figcaption><strong>{e(r["name"])}</strong> · {L("vía Google", "via Google")}</figcaption></figure>' for r in revs) + "</div></div></section>" if revs else ''}

<section class="tcot" id="cotizar" aria-labelledby="cot-t">{WAVE}
  <div class="tcot__in" data-rv>
    <h2 class="h2" id="cot-t">{L("Cotiza <em>este</em> tour", "Get a <em>quote</em>")}</h2>
    <p class="tcot__sub">{L("Elige fecha y cuántas personas. Se abre WhatsApp con tu mensaje listo y te respondemos ahí.", "Choose a date and the number of people. WhatsApp opens with your message ready and we reply there.")}</p>
    <form class="tcot__f" data-wa-form data-tour="{e(t["short"])}">
      <label>{L("Fecha", "Date")}<input type="date" name="fecha" required></label>{f'<p class="tcot__warn">{L(d["season"])}</p>' if d.get('season') else ''}
      <label>{L("Personas", "People")}<input type="number" name="personas" min="1" max="16" value="2" required></label>
      <button class="btn btn--red" type="submit"><span class="btn__in">{L("Cotizar por WhatsApp", "Get a quote on WhatsApp")}</span></button>
    </form>
    <p class="tcot__alt">{L("¿Prefieres hablar?", "Rather talk?")} <a href="{wa_link(wa_t)}" target="_blank" rel="noopener" class="u-link">{L("Escríbenos directo por WhatsApp", "Message us directly on WhatsApp")}</a></p>
  </div>
</section>

<section class="other" aria-labelledby="other-t">
  <div class="other__in" data-rv>
    <h2 class="h2" id="other-t">{L("¿Buscas <em>otro</em> tour?", "Looking for <em>another</em> tour?")}</h2>
    <p class="other__p">{L("Estos se parecen a este. También puedes ver los 8.", "Similar tours, or browse all 8.")}</p>
    {tour_list(P, rel, "tl--mini")}
    <p class="other__all">{btn(L("Ver los 8 tours", "See all 8 tours"), "/tours/", "btn btn--ink")}</p>
  </div>
</section>
<div class="mbar" data-mbar><span class="mbar__t">{price_short(t)}</span>{btn(L("Cotizar", "Quote"), "#cotizar", "btn btn--red btn--sm")}</div>'''
    page(P, f'{t["short"]} desde Castro · Turismo Chiloé Mágico', f'{EN.get(t["short"], t["short"])} from Castro · Turismo Chiloé Mágico',
         f'{t["short"]}: {d["que"].es} Día completo desde Castro con traslado, guiado, almuerzo y bebestibles.',
         f'{EN.get(t["short"], t["short"])}: {d["que"].en} Full day from Castro with transport, guiding, lunch and drinks.', content, 'tour', wa_t, ld, preload_img(t['hero']))


def faq_items(P, items):
    out = ''
    for qq, answers in items:
        parts = ''
        for a in answers:
            if a == '__pending__': parts += pending(P)
            elif a == '__pending_prices__': parts += f'<p>{L("Los demás tours: precio por confirmar con la agencia.", "Other tours: price to be confirmed with the agency.")}</p>'
            elif a == '__costa__': parts += f'<p><a href="/tours/la-costa-curanto/">{L("Tour La Costa", "La Costa Tour")}</a>:</p>'
            elif a == '__es_only__': parts += f'<p>{L("Español.", "Spanish.")}</p>'
            elif a == '__wa__': parts += f'<p>WhatsApp <a href="{wa_link("¡Hola! Quiero reservar un tour")}" target="_blank" rel="noopener">{SITE["wa_display"]}</a> · <a href="tel:+56998833946">{SITE["phone2"]}</a></p>'
            elif "RESEÑA" in getattr(a, "src", ""):
                parts += f'<p><span lang="{"en" if a.isascii() else "es"}">“{q(a, P)}”</span> <small class="u-muted">{L("Reseña en Google", "Google review")}</small></p>'
            else: parts += f'<p lang="es">{q(a, P)}</p>'
        out += f'<details class="faq"><summary>{L(qq)}</summary><div class="faq__a">{parts}</div></details>'
    return out


# ------------------------------------------------------------------ DESTINOS / EXPERIENCIAS
def destinos():
    P = '/destinos/'
    tiles = ''.join(f'<li>{tile(d["img"], dest_href(d), f"<span lang=es>{e(d["name"])}</span>", f"<span lang=es>{q(d["intro"], P)}</span>")}</li>' for d in D.DESTINOS)
    content = f'''{bleed_hero("aucar-isla", h1_lines((L("Explora por", "Explore by"), False), (L("destino", "destination"), True)), L("Destinos", "Destinations"), f'<p lang="es">{q(SITE["diarias"], P)}</p>')}
<section class="tgrid"><ul class="tiles2">{tiles}</ul></section>{booking_cta(P, "¡Hola! Quiero cotizar un tour.", "punihuil-bahia")}'''
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
{booking_cta(P, f"¡Hola! Quiero conocer {d['name']}", d["imgs"][-1])}'''
        page(P, f'{d["name"]} · Turismo Chiloé Mágico', f'{d["name"]} · Turismo Chiloé Mágico',
             f'Qué hacer en {d["name"]}, Chiloé: {", ".join(d["must"])}. Tours desde Castro.', f'Things to do in {DEST_EN.get(d["name"], d["name"])}, Chiloé. Tours from Castro.',
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
{booking_cta(P, "¡Hola! Quiero cotizar un tour.", ts[0]["hero"] if ts else "punihuil-bahia")}'''
        page(P, f'{x["name"].es} en Chiloé · Turismo Chiloé Mágico', f'{x["name"].en} in Chiloé · Turismo Chiloé Mágico',
             f'{x["name"].es}: tours de día completo desde Castro.', f'{x["name"].en}: full-day tours from Castro.', content, preload=preload_img(x['img']))


# ------------------------------------------------------------------ PAQUETES, SERVICIOS, NOSOTROS, GUÍA, FAQ, CONTACTO
def _norm(t):
    return re.sub(r'\s+', ' ', noemoji(str(t))).strip().lower()


def qx(src, part, P, em=None, fix='recorte del texto original'):
    """Recorte literal de un texto de la marca: debe estar contenido tal cual en la fuente."""
    if _norm(part).strip(' .!¡?¿') not in _norm(src):
        raise SystemExit(f'qx: «{part}» no está en la fuente {src.src}')
    COPY.append((P, part, src.src, fix))
    h = e(part)
    if em:
        h = h.replace(e(em), f'<em>{e(em)}</em>', 1)
    if part not in TR_EN:
        raise SystemExit(f'qx: falta la traducción al inglés de «{part}»')
    en, en_em = TR_EN[part]
    he = e(en)
    if en_em:
        he = he.replace(e(en_em), f'<em>{e(en_em)}</em>', 1)
    return f'<span data-l="es" lang="es">{h}</span><span data-l="en" lang="en">{he}</span>'


# Traducción fiel de los recortes de la agencia (mismo sentido, sin agregar nada).
TR_EN = {
    'Servicio de turismo, traslado y viajes privados': ('Tourism, transfer and private trip services', None),
    'Otra salida marcada por innumerable recuerdos': ('Another trip full of countless memories', None),
    'La nieve, paisajes hermosos y todo lo que San Carlos de Bariloche puede ofrecer': ('The snow, beautiful landscapes and everything San Carlos de Bariloche has to offer', None),
    'Somos Chiloé Mágico': ('We are Chiloé Mágico', 'Mágico'),
    'Somos una empresa dedicada al rubro turístico, con más de 20 años de servicio': ('We are a tourism company with more than 20 years of service', None),
    'Una empresa dedicada a entregarte la mejor experiencia en nuestro archipiélago.': ('A company devoted to giving you the best experience in our archipelago.', None),
    'Magia también es ver la sonrisa de nuestros amigos turistas': ('Magic is also seeing the smiles of our traveller friends', 'smiles'),
    'No sólo nos referimos a las mil y un historias que se cuentan sobre mitos, leyendas y brujería': ("We don't just mean the thousand and one stories told about myths, legends and witchcraft", None),
    'Conductores que además de profesionales son wena onda!': ('Drivers who, besides being professionals, are great fun!', 'great fun'),
    'Un máximo de 16 pasajeros y su propio guía': ('A maximum of 16 passengers and their own guide', None),
    'Con aire acondicionado': ('Air-conditioned', None),
    'Asientos reclinables para la siesta post almuerzo': ('Reclining seats for the after-lunch nap', None),
    'Transmite el amor por la tierra y la cultura chilota': ('Conveys a love for the land and Chilote culture', 'Chilote culture'),
    'Nuestro marketing y publicidad más grande son nuestros turistas': ('Our travellers are our best advertising', 'travellers'),
    'Servicios privados': ('Private services', 'services'),
    'Para consultas y programaciones pueden hablarnos a nuestro WhatsApp': ('For questions and bookings, message us on WhatsApp', None),
}


PKG_VIEW = {
    'valdivia-niebla': dict(img='valdivia', inset='valdivia-2',
        quote=('Otra salida marcada por innumerable recuerdos', None),
        chips=[U('4 días · 3 noches', '4 days · 3 nights')]),
    'nieve-volcan-osorno': dict(img='osorno', inset=None,
        quote=('Recorrido de Castro al volcán Osorno, visitando Salto de Petrohué y el Lago Todos los Santos', 'mayúsculas y tilde en nombres propios; sin emoji'),
        chips=[U('Salto de Petrohué', 'Petrohué Falls'), U('Lago Todos los Santos', 'Todos los Santos Lake')]),
    'bariloche': dict(img='nieve', inset='nieve-2',
        quote=('La nieve, paisajes hermosos y todo lo que San Carlos de Bariloche puede ofrecer', None),
        chips=[U('Nieve', 'Snow'), U('Argentina', 'Argentina')]),
}


def pkg_card(p, P, mini=False):
    v = PKG_VIEW[p['slug']]
    txt, fix = v['quote']
    if fix:
        COPY.append((P, txt, {'nieve-volcan-osorno': '[IG-031]'}[p['slug']], fix))
        quote = (f'<span data-l="es" lang="es">{e(txt)}</span><span data-l="en" lang="en">'
                 'A trip from Castro to Osorno Volcano, visiting Petrohué Falls and Todos los Santos Lake</span>')
    else:
        quote = qx(p['text'], txt, P)
    inset = f'<div class="pk__inset" aria-hidden="true">{img(v["inset"], "160px")}</div>' if v['inset'] and not mini else ''
    chips = ''.join(f'<li>{L(c)}</li>' for c in v['chips'])
    if mini:
        return f'''<li class="pk pk--mini" data-rv><a class="pk__a" href="/paquetes/#{p["slug"]}">
  <div class="pk__img">{bimg(v["img"], "(max-width:760px) 92vw, 30vw")}</div>
  <div class="pk__txt"><h3 class="pk__t" lang="es">{e(p["name"])}</h3><ul class="pk__chips">{chips}</ul>
  <p class="pk__q" lang="es">{quote}</p>
  <span class="pk__go">{L("Ver paquete", "See package")} <span aria-hidden="true">→</span></span></div>
</a></li>'''
    return f'''<li class="pk" id="{p["slug"]}" data-rv>
  <div class="pk__img">{bimg(v["img"], "(max-width:760px) 92vw, 31vw")}{inset}{credit(v["img"])}</div>
  <div class="pk__txt">
    <h2 class="pk__t" lang="es">{e(p["name"])}</h2>
    <ul class="pk__chips">{chips}</ul>
    <p class="pk__q" lang="es">{quote}</p>
    <p class="pk__note">{L("Itinerario y precio por WhatsApp", "Itinerary and price on WhatsApp")}</p>
    {btn(f'{L("Cotizar", "Get a quote")} <span aria-hidden="true">→</span>', wa_link(f"¡Hola! Quiero cotizar el viaje {p['name']}"), "btn btn--red pk__btn", True)}
  </div>
</li>'''


def polaroids(keys, cls='pstrip'):
    return f'<ul class="{cls}" aria-hidden="true">' + ''.join(f'<li class="pol3">{img(k, "(max-width:760px) 44vw, 22vw")}</li>' for k in keys) + '</ul>'


def wa_form(P, kind):
    return f'''<form class="form" data-wa-form data-kind="{kind}">
  <label>{L("Nombre", "Name")}<input name="nombre" autocomplete="name" required></label>
  <label>{L("Fechas aproximadas", "Approximate dates")}<input name="fecha" placeholder="Ej.: segunda semana de enero" data-ph-en="E.g. second week of January"></label>
  <label>{L("Personas", "People")}<input type="number" name="personas" min="1" value="2"></label>
  <label class="form__wide">{L("¿Qué te gustaría conocer?", "What would you like to see?")}<textarea name="mensaje" rows="3"></textarea></label>
  <button class="btn btn--red" type="submit"><span class="btn__in">{L("Cotizar por WhatsApp", "Get a quote on WhatsApp")}</span></button>
  <p class="form__note">{L("Se abre WhatsApp con tu mensaje listo; no guardamos datos.", "WhatsApp opens with your message ready; we store no data.")}</p>
</form>'''


def paquetes():
    P = '/paquetes/'
    COPY.append((P, 'Paquetes', 'título de interfaz (nombre del menú)', None))
    cards = ''.join(pkg_card(p, P) for p in D.PAQUETES)
    content = f'''<section class="phead2 phead2--pk">
  <div class="phead2__in">
    <h1 class="h1">{L("Paquetes", "Packages")}</h1>
    <p class="phead2__p" lang="es">{qx(SITE["privados"], "Servicio de turismo, traslado y viajes privados", P, fix="recorte; mayúscula inicial")}</p>
  </div>
</section>
<section class="pksec" aria-label="Paquetes" data-aria-en="Packages">{WAVE}
  <ul class="pks">{cards}</ul>
  <p class="pksec__note">{L("Viajes que ya hemos realizado. Próximas salidas y valores: por confirmar.", "Trips we have already run. Next departures and prices: to be confirmed.")}</p>
</section>
<section class="medida2" id="a-medida" aria-labelledby="medida-t">
  {GULL}
  <div class="medida2__txt" data-rv>
    <h2 class="h2" id="medida-t" lang="es">{qx(Q("Servicios privados", "[BIO]"), "Servicios privados", P, em="privados", fix=None)}</h2>
    <p class="medida2__p" lang="es">{qx(SITE["diarias"], "Para consultas y programaciones pueden hablarnos a nuestro WhatsApp", P, fix="recorte; mayúscula inicial")}</p>
  </div>
  <div class="medida2__f" data-rv>{wa_form(P, "a medida")}</div>
</section>'''
    page(P, 'Paquetes y viajes de varios días · Turismo Chiloé Mágico', 'Multi-day packages · Turismo Chiloé Mágico',
         'Excursión Valdivia y Niebla 4 días, circuito a la nieve al Volcán Osorno, Bariloche y viajes privados desde Castro.',
         'Valdivia and Niebla 4-day trip, snow circuit to Osorno Volcano, Bariloche and private trips from Castro.', content)


def servicios():
    P = '/servicios/'
    cards = [
        (U('Viajes privados', 'Private trips'), Q('Servicios privados', '[BIO]'), 'grupo-van'),
        (U('Traslados', 'Transfers'), Q('servicio de turismo, traslado y viajes privados', '[IG-016]'), 'vans'),
        (U('Grupos', 'Groups'), Q('Tremendo grupo nos tocó … que disfrutaron el Tour de La Costa🤩', '[IG-006]', fix='se omite «ayer»'), 'grupo-columpios'),
    ]
    tiles = [tile(k, wa_link("¡Hola! Quiero cotizar: " + t.es), L(t), f'<span lang="es">{q(x, P)}</span> · {L("Cotizar", "Get a quote")}', '', '', '(max-width:760px) 100vw, 34vw', 'target="_blank" rel="noopener"') for t, x, k in cards]
    content = f'''{bleed_hero("vans", h1_lines((L("Traslados, privados", "Transfers, private trips"), False), (L("y grupos", "and groups"), True)), L("Servicios", "Services"), f'<p lang="es">{q(SITE["vans"], P)}</p>')}
{trio(tiles, "trio--tall")}
<section class="sec narrow"><p class="note">{L("Recorridos, vehículos y tarifas de cada servicio: por confirmar con la agencia.", "Routes, vehicles and rates for each service: to be confirmed with the agency.")}</p></section>
{booking_cta(P, "¡Hola! Quiero cotizar un servicio privado", "muelle-luz-grupo")}'''
    page(P, 'Servicios privados y traslados · Turismo Chiloé Mágico', 'Private services and transfers · Turismo Chiloé Mágico',
         'Viajes privados, traslados y grupos en vans con aire acondicionado desde Castro.', 'Private trips, transfers and groups in air-conditioned vans from Castro.', content, preload=preload_img('vans'))


def nosotros():
    P = '/nosotros/'
    team = ''.join(f'<li><span class="team2__n" lang="es">{e(m["name"])}</span><span class="team2__r">{L(m["role"])}</span></li>' for m in D.TEAM)
    COPY.append((P, ', '.join(m['name'] for m in D.TEAM), 'nombres en posts y reseñas: ' + ' '.join(m['src'] for m in D.TEAM), None))
    andrea = next(r for r in D.REVIEWS if r['name'] == 'Andrea')
    meds = f'''<ul class="meds2 meds2--ab" data-rv aria-label="Datos de la agencia" data-aria-en="Agency facts">
  <li class="md2 md2--cream"><strong>+20</strong><span>{L("años de servicio", "years in service")}</span></li>
  <li class="md2 md2--sand"><strong>16</strong><span>{L("pasajeros máx. por van", "passengers max. per van")}</span></li>
  <li class="md2 md2--blue"><strong>{L(SITE["rating"], SITE["rating_en"])}</strong><span>{L(f"en Google · {SITE['reviews_count']} reseñas", f"on Google · {SITE['reviews_count']} reviews")}</span></li>
</ul>'''
    COPY.append((P, '+20 años de servicio', SITE['anos'].src, 'cifra tomada de «con más de 20 años de servicio»'))
    vid = f'''<video class="flota__v" muted playsinline loop preload="none" data-lazy-video data-poster="/assets/video/vans-poster.jpg" aria-label="{e(META['_videos']['vans']['alt'])}" data-aria-en="{e(ALT_EN['vid:vans'])}">
      <source data-src="/assets/video/vans.webm" type="video/webm"><source data-src="/assets/video/vans.mp4" type="video/mp4"></video>'''
    head = f'''<h2 class="h2 h2--light" id="rsec-t" lang="es">{qx(SITE["marketing"], "Nuestro marketing y publicidad más grande son nuestros turistas", P, em="turistas", fix="recorte; mayúscula inicial")}</h2>
    <p class="rsec__sub">{STARS} {L(f"{SITE['rating']} en Google · {SITE['reviews_count']} reseñas. Las citas van en su idioma original.", f"{SITE['rating_en']} on Google · {SITE['reviews_count']} reviews. Reviews written in Spanish are translated.")}</p>'''
    content = f'''<section class="ab1" aria-labelledby="ab1-t">{WAVE}
  <div class="ab1__in">
    <div class="ab1__txt">
      <h1 class="h1" id="ab1-t" lang="es">{qx(SITE["somos"], "Somos Chiloé Mágico", P, em="Mágico")}</h1>
      <p class="ab1__p" lang="es">{qx(SITE["somos"], "Una empresa dedicada a entregarte la mejor experiencia en nuestro archipiélago.", P)}</p>
      {meds}
    </div>
    <div class="bcta__pols ab1__pols" aria-hidden="true"><div class="pol2 pol2--a">{bimg("nicolas-enrique", "(max-width:760px) 60vw, 26vw")}</div><div class="pol2 pol2--b">{bimg("grupo-van", "(max-width:760px) 50vw, 22vw")}</div><div class="pol2 pol2--c">{bimg("enrique", "(max-width:760px) 44vw, 18vw")}</div></div>
  </div>
</section>
<section class="ab2" aria-labelledby="ab2-t">{WAVE}
  <header class="ab2__head" data-rv>
    <h2 class="h2" id="ab2-t" lang="es">{qx(SITE["magia2"], "Magia también es ver la sonrisa de nuestros amigos turistas", P, em="sonrisa")}</h2>
    <p class="ab2__p" lang="es">{qx(SITE["magia"], "No sólo nos referimos a las mil y un historias que se cuentan sobre mitos, leyendas y brujería", P, fix="recorte; mayúscula inicial; sin emoji")}</p>
  </header>
  {polaroids(["brujos-vuelo", "grupo-almuerzo", "almas-grupo", "yayanes-cascada"])}
</section>
<section class="ab3" aria-labelledby="ab3-t">{WAVE}
  <div class="ab3__in">
    <div class="ab3__media" data-rv><div class="ab3__phone">{vid}</div><div class="pol3 ab3__pol" aria-hidden="true">{img("vans", "(max-width:760px) 40vw, 18vw")}</div></div>
    <div class="ab3__txt" data-rv>
      <h2 class="h2" id="ab3-t" lang="es">{qx(SITE["vans"], "Conductores que además de profesionales son wena onda!", P, em="wena onda", fix="recorte; mayúscula inicial")}</h2>
      <ul class="ab3__list" lang="es">
        <li>{qx(SITE["van16"], "Un máximo de 16 pasajeros y su propio guía", P)}</li>
        <li>{qx(SITE["vans"], "Con aire acondicionado", P)}</li>
        <li>{qx(SITE["vans"], "Asientos reclinables para la siesta post almuerzo", P, fix="recorte; mayúscula inicial")}</li>
      </ul>
    </div>
  </div>
</section>
<section class="ab4" aria-labelledby="ab4-t">{WAVE}
  <header class="ab4__head" data-rv>
    <h2 class="h2" id="ab4-t" lang="es">{qx(Q(andrea["text"], "[RESEÑA]"), "Transmite el amor por la tierra y la cultura chilota", P, em="cultura chilota", fix="recorte de reseña de Google")}</h2>
    <p class="ab4__by">{L("Andrea, sobre su guía Alberto · vía Google", "Andrea, about her guide Alberto · via Google")}</p>
  </header>
  <ul class="team2" data-rv>{team}</ul>
</section>
{reviews_solid(P, D.REVIEWS[:6], head)}'''
    page(P, 'Nosotros · Turismo Chiloé Mágico', 'About us · Turismo Chiloé Mágico',
         'Agencia local de turismo en Castro, Chiloé: más de 20 años de servicio, guías, conductores y vans para recorrer el archipiélago.', 'Local travel agency in Castro, Chiloé.', content, preload=preload_img('nicolas-enrique'))


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
        inner = ''.join(q(p, P, 'p') for p in g["paras"]) + f'<p class="note">{L("Fuente: publicaciones de @chiloemagicotour.", "Source: posts by @chiloemagicotour.")}</p>'
        content = f'''{bleed_hero(g["img"], h1_lines((L(g["title"]), False)), L("Guía de Chiloé", "Chiloé guide"), '', crumbs, "tall")}
<article class="art"><div class="art__body narrow">{inner}</div></article>
{f'<section class="related"><header class="pkgs__head"><p class="kicker">{L("Vívelo en", "Experience it on")}</p></header>' + trio([tour_tile(t, P, sizes="(max-width:760px) 100vw, 34vw") for t in ts]) + '</section>' if ts else ''}'''
        page(P, f'{g["title"].es} · Guía de Chiloé', f'{g["title"].en} · Chiloé guide', f'{g["title"].es}: guía de Chiloé de Turismo Chiloé Mágico.',
             f'{g["title"].en}{" " if g["title"].en.endswith("?") else ": "}Chiloé guide by Turismo Chiloé Mágico.', content, preload=preload_img(g['img']))


def faq():
    P = '/preguntas-frecuentes/'
    content = f'''{bleed_hero("huillinco-pareja", h1_lines((L("Preguntas", "Frequently asked"), False), (L("frecuentes", "questions"), True)), "FAQ", '', '', "tall")}
<section class="sec narrow">{faq_items(P, D.FAQ)}</section>{booking_cta(P, "¡Hola! Tengo una consulta", "muelle-luz-oceano")}'''
    page(P, 'Preguntas frecuentes · Turismo Chiloé Mágico', 'FAQ · Turismo Chiloé Mágico',
         'Salidas, horarios, qué incluye, idioma, grupos y reservas de los tours de Turismo Chiloé Mágico.', 'Departures, times, inclusions, language, groups and bookings.', content, preload=preload_img('huillinco-pareja'))


def contacto():
    P = '/contacto/'
    content = f'''{bleed_hero("chonchi", f'<h1 class="h1 h1--light" data-lines><span class="line"><span>{L("Cotiza tu tour", "Get a quote")}</span></span></h1>', L("Contacto", "Contact"), f'<p>{L("Escríbenos por WhatsApp:", "Message us on WhatsApp:")} {SITE["wa_display"]}</p>', '', "tall")}
<section class="sec split">
  <div class="contact__list">
    <p><span class="kicker">WhatsApp</span><a class="big-link" href="{wa_link('¡Hola! Quiero cotizar un tour.')}" target="_blank" rel="noopener">{SITE["wa_display"]}</a></p>
    <p><span class="kicker">{L("Teléfono", "Phone")}</span><a class="big-link" href="tel:+56998833946">{SITE["phone2"]}</a></p>
    <p><span class="kicker">{L("Correo", "Email")}</span><a class="big-link" href="mailto:{SITE["email"]}">{SITE["email"]}</a></p>
    <p><span class="kicker">{L("Dirección", "Address")}</span><span lang="es">{q(SITE["address"], P)}</span></p>
    <p><span class="kicker">{L("Horario", "Hours")}</span><span lang="es">{q(SITE["hours"], P)}</span></p>
  </div>
  {wa_form(P, "contacto")}
</section>
<section class="visit visit--full">{map_block(P)}</section>'''
    page(P, 'Cotiza tu tour · Turismo Chiloé Mágico', 'Get a quote · Turismo Chiloé Mágico',
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
    # Las páginas de destinos, experiencias y guía salen del menú, pero Google las sigue encontrando aquí.
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{DOMAIN}{p}</loc></url>\n' for p in PAGES) + '</urlset>\n')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')
    if MISSING_ALT:
        sys.exit('ERROR: falta texto alternativo en inglés para: ' + ', '.join(sorted(set(MISSING_ALT))))
    print(f'{len(PAGES)} páginas · {len(COPY)} textos con fuente')
