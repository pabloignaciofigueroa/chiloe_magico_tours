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


def clp(n):
    return '$' + f'{n:,}'.replace(',', '.')


def tour_href(t): return f'/tours/{t["slug"]}/'
def dest_href(d): return f'/destinos/{d["slug"]}/'
def exp_href(x): return f'/experiencias/{x["slug"]}/'


NAV = [
    ('/tours/', U('Tours', 'Tours'), 'punihuil-bahia'),
    ('/paquetes/', U('Paquetes', 'Packages'), 'valdivia'),
    ('/nosotros/', U('Nosotros', 'About us'), 'nicolas-enrique'),
    ('/contacto/', U('Contacto', 'Contact'), 'palafitos'),
]


def header(current, wa_text):
    links = ''.join(f'<li><a href="{h}"{" aria-current=page" if current.startswith(h) else ""}>{L(lbl)}</a></li>' for h, lbl, _ in NAV)
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
    <a href="{wa_link('Hola! Quiero consultar por los tours')}" target="_blank" rel="noopener">WhatsApp {SITE["wa_display"]}</a>
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
      <p class="ftr__slogan" lang="es">{q(SITE["slogan"], page)}</p>
    </div>
    <div class="ftr__act">
      {btn(L("Cotizar por WhatsApp", "Get a quote on WhatsApp"), wa_link('Hola! Quiero cotizar un tour'), "btn btn--light ftr__wa", True)}
      <p class="ftr__addr" lang="es">{q(SITE["address_short"], page)}<br>{q(SITE["hours"], page)}</p>
    </div>
  </div>
  <nav class="ftr__nav" aria-label="Pie de página" data-aria-en="Footer"><ul>{nav}<li><a href="/preguntas-frecuentes/">{L("Preguntas frecuentes", "FAQ")}</a></li><li><a href="{SITE["instagram"]}" target="_blank" rel="noopener">Instagram</a></li></ul></nav>
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
    'brujos-columpio': '68% 18%', 'brujos-columpio-2': '50% 30%', 'almas': '50% 35%', 'parque-bosque': '50% 40%',
    'curanto-destape': '50% 45%', 'tocoihue': '50% 40%', 'caleuche': '50% 55%', 'curaco': '50% 60%', 'curaco-2': '50% 50%',
    'mechuque': '50% 55%', 'palafitos': '50% 78%', 'punihuil-navega': '50% 40%', 'tenaun': '50% 35%', 'brujos-vuelo': '50% 45%',
    'yayanes-puente': '50% 45%', 'huillinco-columpio': '50% 40%', 'aucar-isla': '50% 55%', 'curanto-fuego': '50% 50%',
    'nercon': '50% 40%', 'brujos-alas': '50% 40%', 'punihuil-islote': '50% 50%', 'minga': '50% 55%',
    'palafitos': '50% 78%', 'vans': '50% 70%', 'muelle-luz-grupo': '60% 40%', 'parque-muelle': '50% 55%',
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
        return f'{clp(t["price_from"])} CLP'
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
        slides += (f'<figure class="rev swiper-slide"><div class="rev__stars" role="img" aria-label="5 de 5 estrellas" data-aria-en="5 out of 5 stars">{STARS}</div>'
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
  <div class="ssplit__txt" data-rv>{inner_html}</div>
</section>{more}'''


# ------------------------------------------------------------------ v5: cada tour se explica solo
STARS = '<svg class="stars5" viewBox="0 0 100 18" aria-hidden="true"><path d="M9 1l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L9 13.4 4 16.2l1.2-5.6L1 6.8l5.6-.6zM29 1l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L29 13.4 24 16.2l1.2-5.6L21 6.8l5.6-.6zM49 1l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L49 13.4 44 16.2l1.2-5.6L41 6.8l5.6-.6zM69 1l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L69 13.4 64 16.2l1.2-5.6L61 6.8l5.6-.6zM89 1l2.4 5.2 5.6.6-4.2 3.8 1.2 5.6L89 13.4 84 16.2l1.2-5.6L81 6.8l5.6-.6z"/></svg>'

def det(t): return D.DETAIL[t['slug']]


def price_short(t):
    return (f'<strong>{clp(t["price_from"])}</strong> <span class="u-small">{L("por persona", "per person")}</span>'
            if t.get('price_from') else f'<span class="u-muted">{L("Precio a cotizar", "Price on request")}</span>')


def trow(t, P, sizes='(max-width:560px) 132px, (max-width:1099px) 46vw, 25vw', h='h3'):
    """Fila de tour: foto + qué es + horario/almuerzo + precio. Toda la fila es el enlace."""
    d = det(t)
    return f'''<li class="tr" data-rv><a class="tr__a" href="{tour_href(t)}">
  <div class="tr__img">{bimg(t["card"], sizes)}</div>
  <div class="tr__txt">
    <{h} class="tr__t" lang="es">{e(t["short"])}</{h}>
    <p class="tr__que">{L(d["corto"])}</p>
    <ul class="tr__tags">{''.join(f'<li>{L(x)}</li>' for x in d["tags"])}</ul>
    <p class="tr__meta">{L("Almuerzo:", "Lunch:")} {L(d["lunch"])}</p>
    <p class="tr__foot"><span class="tr__price">{price_short(t)}</span><span class="tr__go">{L("Ver tour", "See tour")} <span aria-hidden="true">→</span></span></p>
  </div>
</a></li>'''


def tour_list(P, items, cls='', h='h3'):
    return f'<ul class="tl {cls}">' + ''.join(trow(t, P, h=h) for t in items) + '</ul>'


def reviews_solid(page, items):
    slides = ''
    for r in items:
        frm = f' · <span lang="es">desde {e(r["from"])}</span>' if r.get('from') else ''
        tour = f' · <a href="{tour_href(TOURS[r["tour"]])}">{e(TOURS[r["tour"]]["short"])}</a>' if r.get('tour') else ''
        slides += (f'<figure class="rev swiper-slide"><div class="rev__stars" role="img" aria-label="5 de 5 estrellas" data-aria-en="5 out of 5 stars">{STARS}</div>'
                   f'<blockquote lang="{r["lang"]}">“{q(r["text"], page)}”</blockquote>'
                   f'<figcaption><strong>{e(r["name"])}</strong>{frm} · {L("vía Google", "via Google")}{tour}</figcaption></figure>')
    return f'''<section class="rsec" aria-labelledby="rsec-t">
  <header class="rsec__head" data-rv>
    <h2 class="h2 h2--light" id="rsec-t">{L(f"{SITE['rating']} en Google", f"{SITE['rating_en']} on Google")}</h2>
    <p class="rsec__sub">{STARS} {L(f"{SITE['reviews_count']} reseñas de viajeros. Las citas van en su idioma original.", f"{SITE['reviews_count']} traveller reviews. Quotes in their original language.")}</p>
  </header>
  <div class="swiper rsec__sw" data-swiper="reviews" data-drag><div class="swiper-wrapper">{slides}</div></div>
  <div class="snav snav--light"><button class="arrow arrow--light" type="button" data-prev aria-label="Reseña anterior" data-aria-en="Previous review">←</button><button class="arrow arrow--light" type="button" data-next aria-label="Reseña siguiente" data-aria-en="Next review">→</button>
  <a class="u-link u-link--light" href="https://www.google.com/maps/place/Turismo+Chilo%C3%A9+M%C3%A1gico/@-42.4816941,-73.7642726,17z" target="_blank" rel="noopener">{L("Leer todas en Google Maps", "Read them all on Google Maps")}</a></div>
</section>'''


def closing(page, text, key='punihuil-bahia'):
    """Cierre: una foto, una frase corta, WhatsApp y dónde estamos."""
    COPY.append((page, '¡No dejes que te lo cuenten! / Ven a disfrutar de esta mágica isla junto a nosotros', '[IG-007]', 'remate partido en dos: título y frase'))
    return f'''<section class="bcta" aria-labelledby="bcta-t">
  <div class="bcta__media" data-parallax>{bimg(key)}</div>
  <div class="bcta__shade" aria-hidden="true"></div>
  <div class="bcta__in">
    <h2 class="bcta__big" id="bcta-t" lang="es">¡No dejes que te lo cuenten!</h2>
    <p class="bcta__p" lang="es">Ven a disfrutar de esta mágica isla junto a nosotros.</p>
    <div class="cta__row">{btn(L("Cotizar por WhatsApp", "Get a quote on WhatsApp"), wa_link(text), "btn btn--red", True)}</div>
    <p class="bcta__addr" lang="es">{q(SITE["address_short"], page)} · {q(SITE["hours"], page)}</p>
  </div>
</section>'''


def facts_strip(P):
    return f'''<ul class="facts2" data-rv aria-label="Datos de la agencia" data-aria-en="Agency facts">
  <li><strong>{SITE["rating"]} / 5</strong> {L(f"en Google ({SITE['reviews_count']} reseñas)", f"on Google ({SITE['reviews_count']} reviews)")}</li>
  <li><strong>{L("Todos los días", "Every day")}</strong> {L("salida 10:00, regreso 19:00 aprox.", "leave 10am, back 7pm approx.")}</li>
  <li><strong>{L("Desde Castro", "From Castro")}</strong> {L("frente a la Plaza de Armas", "facing the main square")}</li>
  <li><strong>{L("Máx. 16", "Max. 16")}</strong> {L("pasajeros por van, con guía", "passengers per van, with guide")}</li>
</ul>'''


def home():
    P = '/'
    COPY.append((P, 'Tours en Chiloé desde Castro', 'título de interfaz', None))
    content = f'''
<section class="hero" data-hero>
  <div class="hero__media" data-parallax-hero>{img("huillinco-columpio", "100vw", "", True)}</div>
  <div class="hero__shade" aria-hidden="true"></div>
  <div class="hero__in">
    <h1 class="hero__t" data-lines><span class="line"><span>{L("Tours en Chiloé", "Chiloé tours")}</span></span><span class="line"><span>{L("desde Castro", "from Castro")}</span></span></h1>
    <p class="hero__sub" lang="es">{q(Q("Nuestro archipiélago es mágico ¡Ven a descubrirlo!", "[BIO]"), P)}</p>
    <div class="hero__ctas">{btn(L("Ver los tours", "See the tours"), "#tours", "btn btn--light")}{btn(L("Cotizar por WhatsApp", "Get a quote on WhatsApp"), wa_link("Hola! Quiero cotizar un tour"), "btn btn--red", True)}</div>
  </div>
</section>



<section class="tsec" id="tours" aria-labelledby="tours-t">
  <header class="tsec__head" data-rv>
    <h2 class="h2" id="tours-t">{L("Elige tu tour", "Choose your tour")}</h2>
    <p class="tsec__lead">{L("Tours de día completo desde Castro.", "Full-day tours from Castro.")} <span lang="es">{q(Q("Todos nuestros tours incluyen traslado, guiado, almuerzo y bebestibles, y visitas a distintos atractivos turísticos 🌿", "[IG-007]"), P)}</span></p>
  </header>
  {facts_strip(P)}
  {tour_list(P, D.TOURS)}
</section>

<section class="isla" aria-labelledby="isla-t" data-isla>
  <div class="isla__stick">
    <div class="isla__blur" aria-hidden="true"></div>
    <video class="isla__v" muted playsinline loop preload="none" data-lazy-video data-poster="/assets/video/isla-poster.jpg" aria-label="{e(META['_videos']['isla']['alt'])}" data-aria-en="{e(ALT_EN['vid:isla'])}">
      <source data-src="/assets/video/isla.webm" type="video/webm"><source data-src="/assets/video/isla.mp4" type="video/mp4">
    </video>
    <div class="isla__cover" aria-hidden="true"></div>
    <div class="isla__shade" aria-hidden="true"></div>
    <div class="isla__t" data-isla-t>
      <h2 class="isla__h" id="isla-t" lang="es">{q(Q("¿Vamos a navegar? 🌊", "[IG-015]", fix="se agrega el signo de apertura ¿"), P)}</h2>
      <p class="isla__q">{L("Entre los islotes de Puñihuil, con los pingüinos.", "Among the Puñihuil islets, with the penguins.")} <a href="{tour_href(TOURS["pinguineras-punihuil"])}">{L("Ver el tour", "See the tour")} →</a></p>
    </div>
  </div>
</section>

{reviews_solid(P, D.REVIEWS)}

{closing(P, "Hola! Quiero consultar por los tours")}
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
<section class="tsec tsec--page" aria-label="Todos los tours" data-aria-en="All tours">
  {facts_strip(P)}
  {tour_list(P, D.TOURS, h='h2')}
</section>
{closing(P, "Hola! Quiero consultar por los tours", "ancud-atardecer")}'''
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
    wa_t = f'Hola! Quiero cotizar el {t["short"]}. Fecha: ___ Personas: ___'
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
    content = f'''<section class="th{" th--split" if not wide(t["hero"]) else ""}" data-hero>
  <div class="th__media" data-parallax-hero>{bimg(t["hero"], "100vw", True)}</div>{credit(t["hero"])}
  <div class="th__shade" aria-hidden="true"></div>
  <a class="back" href="/tours/"><span aria-hidden="true">←</span> {L("Todos los tours", "All tours")}</a>
  <div class="th__in">
    {title}
    <p class="th__que">{L(d["que"])}</p>
    <div class="th__ctas">{btn(L("Cotizar este tour", "Get a quote"), "#cotizar", "btn btn--red")}<a class="th__more" href="#detalle">{L("Ver el detalle", "See the details")} <span aria-hidden="true">↓</span></a></div>
  </div>
</section>

<section class="tq" id="detalle" aria-label="Datos del tour" data-aria-en="Tour facts">
  <dl class="tq__dl" data-rv>
    <div><dt>{L("Duración", "Duration")}</dt><dd>{L("Día completo, 10:00 a 19:00 aprox.", "Full day, 10am to 7pm approx.")}</dd></div>
    <div><dt>{L("Salida", "Departure")}</dt><dd>{L("Agencia frente a la Plaza de Armas de Castro", "Agency facing Castro's main square")}</dd></div>
    <div><dt>{L("Almuerzo", "Lunch")}</dt><dd class="u-cap">{L(d["lunch"])}</dd></div>
    <div><dt>{L("Precio", "Price")}</dt><dd>{price_short(t)}</dd></div>
  </dl>
</section>

<section class="tw" aria-labelledby="tw-t">
  <div class="tw__in">
    <div class="tw__l" data-rv>
      <h2 class="h2" id="tw-t">{L("Lo que harás", "What you'll do")}</h2>
      {lead}
    </div>
    <ul class="tw__list" data-rv>{pts}</ul>
  </div>
</section>

{f"""<section class="tfotos" aria-labelledby="tf-t">
  <header class="tfotos__head" data-rv><h2 class="h2 h2--light" id="tf-t">{L("Así se vive", "What it looks like")}</h2><p>{L("Fotos de la agencia en este tour. Desliza para ver más.", "The agency's photos on this tour. Swipe for more.")}</p></header>
  <div class="swiper tfsw" data-swiper="gallery" data-drag><div class="swiper-wrapper">{gallery}</div></div>
  <div class="snav snav--light"><button class="arrow arrow--light" type="button" data-prev aria-label="Foto anterior" data-aria-en="Previous photo">←</button><button class="arrow arrow--light" type="button" data-next aria-label="Foto siguiente" data-aria-en="Next photo">→</button></div>
</section>""" if photos else ''}

<section class="tin" aria-labelledby="tin-t">
  <div class="tin__in">
    <h2 class="h2" id="tin-t">{L("Qué incluye", "What's included")}</h2>
    <div class="tin__grid" data-rv>
      <div><h3 class="h4">{L("Incluye", "Included")}</h3><ul class="inclist"><li>{L("Traslado en van desde Castro, ida y vuelta", "Return van transport from Castro")}</li><li>{L("Guía durante todo el día", "Guide for the whole day")}</li><li>{L("Almuerzo y bebestibles", "Lunch and drinks")}</li></ul>
      <h3 class="h4">{L("No incluye", "Not included")}</h3>{f'<ul class="nolist">{no}</ul>' if no else f'<p>{L("Por confirmar: pregúntanos por WhatsApp.", "To be confirmed: ask us on WhatsApp.")}</p>'}
      {season}
      <p class="note">{L("Mínimo de pasajeros, niños y cancelación: pregúntanos por WhatsApp.", "Minimum group, children and cancellation: ask us on WhatsApp.")}</p></div>
    </div>
  </div>
</section>

<section class="meet" aria-labelledby="meet-t">
  <div class="meet__txt" data-rv>
    <h2 class="h2" id="meet-t">{L("Punto de encuentro", "Meeting point")}</h2>
    <p lang="es">{q(SITE["address_short"], P)}</p>
    <p lang="es">{q(SITE["salida"], P)}.</p>
    <a class="u-link" href="https://www.google.com/maps/dir/?api=1&amp;destination=-42.4816941,-73.7642726" target="_blank" rel="noopener">{L("Cómo llegar en Google Maps", "Directions on Google Maps")}</a>
  </div>
  {map_block(P)}
</section>

{f"""<section class="trev" aria-labelledby="trev-t"><div class="trev__in"><h2 class="h2" id="trev-t">{L("Lo que cuentan de este tour", "What travellers say about this tour")}</h2><div class="trev__grid" data-rv>""" + ''.join(f'<figure class="rev"><div class="rev__stars" role="img" aria-label="5 de 5 estrellas" data-aria-en="5 out of 5 stars">{STARS}</div><blockquote lang="{r["lang"]}">“{q(r["text"], P)}”</blockquote><figcaption><strong>{e(r["name"])}</strong> · {L("vía Google", "via Google")}</figcaption></figure>' for r in revs) + "</div></div></section>" if revs else ''}

<section class="tcot" id="cotizar" aria-labelledby="cot-t">
  <div class="tcot__in" data-rv>
    <h2 class="h2" id="cot-t">{L("Cotiza este tour", "Get a quote")}</h2>
    <p class="tcot__sub">{L("Elige fecha y cuántas personas. Se abre WhatsApp con tu mensaje listo y te respondemos ahí.", "Pick a date and how many people. WhatsApp opens with your message ready and we reply there.")}</p>
    <form class="tcot__f" data-wa-form data-tour="{e(t["short"])}">
      <label>{L("Fecha", "Date")}<input type="date" name="fecha" required></label>
      <label>{L("Personas", "People")}<input type="number" name="personas" min="1" max="16" value="2" required></label>
      <button class="btn btn--red" type="submit"><span class="btn__in">{L("Cotizar por WhatsApp", "Get a quote on WhatsApp")}</span></button>
    </form>
    <p class="tcot__alt">{L("¿Prefieres hablar?", "Rather talk?")} <a href="{wa_link(wa_t)}" target="_blank" rel="noopener" class="u-link">WhatsApp {SITE["wa_display"]}</a></p>
  </div>
</section>

<section class="other" aria-labelledby="other-t">
  <div class="other__in" data-rv>
    <h2 class="h2" id="other-t">{L("¿Buscas otro tour?", "Looking for another tour?")}</h2>
    <p class="other__p">{L("Estos se parecen a este. También puedes ver los 8.", "These are similar to this one. You can also see all 8.")}</p>
    {tour_list(P, rel, "tl--mini")}
    <p class="other__all">{btn(L("Ver los 8 tours", "See all 8 tours"), "/tours/", "btn btn--ink")}</p>
  </div>
</section>
<div class="mbar" data-mbar><span class="mbar__t">{price_short(t)}</span>{btn(L("Cotizar", "Quote"), "#cotizar", "btn btn--red btn--sm")}</div>'''
    page(P, f'{t["short"]} desde Castro · Turismo Chiloé Mágico', f'{t["short"]} from Castro · Turismo Chiloé Mágico',
         f'{t["short"]}: {d["que"].es} Día completo desde Castro con traslado, guiado, almuerzo y bebestibles.',
         f'{t["short"]}: {d["que"].en} Full day from Castro with transport, guiding, lunch and drinks.', content, 'tour', wa_t, ld, preload_img(t['hero']))


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
  <label>{L("Fechas aproximadas", "Approximate dates")}<input name="fecha" placeholder="Ej.: segunda semana de enero" data-ph-en="E.g. second week of January"></label>
  <label>{L("Personas", "People")}<input type="number" name="personas" min="1" value="2"></label>
  <label class="form__wide">{L("¿Qué te gustaría conocer?", "What would you like to see?")}<textarea name="mensaje" rows="3"></textarea></label>
  <button class="btn btn--red" type="submit"><span class="btn__in">{L("Cotizar por WhatsApp", "Get a quote on WhatsApp")}</span></button>
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
            items += sticky_split(p['imgs'][0], inner, 'right' if items.count('ssplit--') % 2 == 0 else 'left')
        else:
            items += f'<section class="ssplit ssplit--flat"><div class="ssplit__media ssplit__media--flat" aria-hidden="true"><span>❄</span></div><div class="ssplit__txt">{inner}</div></section>'
    content = f'''{bleed_hero("valdivia-2" if META["valdivia-2"]["w"] > 1200 else "ancud-atardecer", h1_lines((L("Viajes de varios días", "Multi-day trips"), False)), L("Paquetes", "Packages"),
        f'<p lang="es">{q(SITE["privados"], P)}</p><p class="note note--light">{L("Viajes que ya hemos realizado. Próximas salidas y valores: por confirmar.", "Trips we have already run. Next departures and prices: to be confirmed.")}</p>')}
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
{reviews_solid(P, D.REVIEWS[:6])}'''
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
    # Las páginas de destinos, experiencias y guía salen del menú, pero Google las sigue encontrando aquí.
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{DOMAIN}{p}</loc></url>\n' for p in PAGES) + '</urlset>\n')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n')
    if MISSING_ALT:
        sys.exit('ERROR: falta texto alternativo en inglés para: ' + ', '.join(sorted(set(MISSING_ALT))))
    print(f'{len(PAGES)} páginas · {len(COPY)} textos con fuente')
