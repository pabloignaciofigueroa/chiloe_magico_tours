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


def q(text, page, tag=None, cls='', lang='es'):
    """Texto de la marca (literal). Registra su fuente para copy.md."""
    if isinstance(text, Q):
        COPY.append((page, str(text), text.src, text.fix))
    s = e(str(text))
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
    rep = {'title': e(title), 'title_en': e(title_en), 'desc': e(desc), 'desc_en': e(desc_en), 'url': url, 'domain': DOMAIN,
           'jsonld': json.dumps(ld or ld_business(), ensure_ascii=False).replace('</', '<\\/'), 'body_class': body_class,
           'header': header(path, wa_text), 'footer': footer(path), 'wa': wa_float(wa_text), 'content': content, 'preload': preload}
    for k, v in rep.items():
        out = out.replace('{{' + k + '}}', v)
    dest = ROOT / (path.strip('/') + '/index.html' if path != '/' else 'index.html')
    dest.parent.mkdir(parents=True, exist_ok=True)
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


def reviews_block(page, items, title=True):
    slides = ''
    for r in items:
        frm = f' · <span lang="es">desde {e(r["from"])}</span>' if r.get('from') else ''
        tour = f' · <a href="{tour_href(TOURS[r["tour"]])}">{e(TOURS[r["tour"]]["short"])}</a>' if r.get('tour') else ''
        slides += (f'<figure class="rev swiper-slide"><div class="rev__stars" role="img" aria-label="5 de 5 estrellas" data-aria-en="5 out of 5 stars">★★★★★</div>'
                   f'<blockquote lang="{r["lang"]}">“{q(r["text"], page)}”</blockquote>'
                   f'<figcaption><strong>{e(r["name"])}</strong>{frm} · {L("vía Google", "via Google")}{tour}</figcaption></figure>')
    head = (f'<header class="sec__head"><p class="kicker">{L("Testimonios", "Reviews")}</p>'
            f'<h2 class="h2" data-lines><span class="line"><span>{SITE["rating"]} ★ </span></span><span class="line"><span>{L("en Google", "on Google")}</span></span></h2>'
            f'<p class="lead">{L(f"{SITE["reviews_count"]} reseñas leídas el 19 de octubre de 2026. Las citas van en su idioma original.", f"{SITE["reviews_count"]} reviews read on 19 October 2026. Quotes are shown in their original language.")}</p></header>') if title else ''
    return f'''<section class="sec reviews" aria-label="Testimonios" data-aria-en="Reviews">
  {head}
  <div class="swiper reviews__sw" data-swiper="reviews"><div class="swiper-wrapper">{slides}</div></div>
  <div class="reviews__nav"><button class="arrow" type="button" data-prev aria-label="Reseña anterior" data-aria-en="Previous review">←</button><button class="arrow" type="button" data-next aria-label="Reseña siguiente" data-aria-en="Next review">→</button>
  <a class="u-link" href="https://www.google.com/maps/place/Turismo+Chilo%C3%A9+M%C3%A1gico/@-42.4816941,-73.7642726,17z" target="_blank" rel="noopener">{L("Ver todas en Google Maps", "See all on Google Maps")}</a></div>
</section>'''


def medallion(name, key, i, size='m'):
    inner = img(key, '220px') if key else f'<span class="med__n" aria-hidden="true">{i:02d}</span>'
    pid = f'arc{abs(hash(name)) % 10**7}'
    return (f'<li lang="es" class="med med--{size}{"" if key else " med--empty"}"><div class="med__ring">{inner}</div>'
            f'<svg class="med__label" viewBox="0 0 200 200" aria-hidden="true"><defs><path id="{pid}" d="M6,100 a94,94 0 0,0 188,0"/></defs>'
            f'<text><textPath href="#{pid}" startOffset="50%" text-anchor="middle">{e(name.upper())}</textPath></text></svg>'
            f'<span class="sr">{e(name)}</span></li>')


def map_block(page):
    return f'''<div class="map" data-map>
  <a class="map__fallback" href="https://www.google.com/maps/place/Turismo+Chilo%C3%A9+M%C3%A1gico/@-42.4816941,-73.7642726,17z" target="_blank" rel="noopener">
    {img("palafitos", "(max-width: 760px) 100vw, 50vw")}
    <span class="map__cta">{L("Abrir mapa · Gamboa 351, Castro", "Open map · Gamboa 351, Castro")}</span>
  </a>
  <iframe title="Mapa: Gamboa 351, Castro" data-title-en="Map: Gamboa 351, Castro" data-src="https://www.openstreetmap.org/export/embed.html?bbox=-73.7702%2C-42.4846%2C-73.7582%2C-42.4786&amp;layer=mapnik&amp;marker=-42.4816941%2C-73.7642726" loading="lazy" referrerpolicy="no-referrer"></iframe>
</div>'''


def booking_cta(page, text):
    return f'''<section class="sec cta" aria-label="Reservar" data-aria-en="Book">
  <p class="cta__big" lang="es" data-lines><span class="line"><span>{q(SITE["cierre"], page)}</span></span></p>
  <div class="cta__row">{btn(L("Reservar por WhatsApp", "Book on WhatsApp"), wa_link(text), "btn btn--red", True)}
  <a class="u-link" href="tel:+{SITE["wa"]}">{SITE["wa_display"]}</a></div>
  <p class="cta__note" lang="es">{q(SITE["cupos"], page)}</p>
</section>'''


# ------------------------------------------------------------------ HOME
def home():
    P = '/'
    tours = ''.join(f'<div class="swiper-slide">{tour_card(t, P)}</div>' for t in D.TOURS if not t.get('thin'))
    dests = ''.join(f'<li><a class="dest" href="{dest_href(d)}" data-card><div class="dest__ring">{img(d["img"], "(max-width:760px) 44vw, 18vw")}</div>'
                    f'<span class="dest__name" lang="es">{e(d["name"])}</span></a></li>' for d in D.DESTINOS)
    exps = ''.join(f'<li><a class="exp" href="{exp_href(x)}" data-hover-img="{x["img"]}"><span class="exp__n">0{i+1}</span>'
                   f'<span class="exp__name">{L(x["name"])}</span><span class="exp__q" lang="es">{q(x["quote"], P)}</span></a></li>'
                   for i, x in enumerate(D.EXPERIENCIAS))
    exp_imgs = ''.join(f'<div class="exp__img" data-hover-key="{x["img"]}">{img(x["img"], "30vw")}</div>' for x in D.EXPERIENCIAS)
    pkgs = ''.join(f'''<li class="pkg">{media(p["imgs"][0], "(max-width:760px) 90vw, 30vw", "pkg__media", ratio="4/5") if p["imgs"] else '<div class="pkg__type" aria-hidden="true">❄</div>'}
      <p class="kicker">{L(p["days"])}</p><h3 class="h4" lang="es">{e(p["name"])}</h3>
      <p class="pkg__t" lang="es">{q(p["text"], P)}</p></li>''' for p in D.PAQUETES)
    guia = ''.join(f'<li><a class="gcard" href="/guia/{g["slug"]}/" data-card>{media(g["img"], "(max-width:760px) 90vw, 30vw", "gcard__media", ratio="4/3")}'
                   f'<h3 class="h4">{L(g["title"])}</h3><span class="u-link">{L("Leer", "Read")}</span></a></li>' for g in D.GUIA[:3])
    content = f'''
<section class="hero" data-hero>
  <div class="hero__media" data-parallax-hero>{img("huillinco-columpio", "100vw", "", True)}</div>
  <div class="hero__shade" aria-hidden="true"></div>
  <div class="hero__in">
    <img class="hero__logo" src="/brand/logo/logo-sticker.svg" width="1912" height="1065" alt="Turismo Chiloé Mágico" data-alt-en="Turismo Chiloé Mágico">
    <h1 class="hero__t" lang="es" data-lines><span class="line"><span>{q(Q("Nuestro archipiélago es mágico", "[BIO]"), P)}</span></span><span class="line line--script"><span>{q(Q("¡Ven a descubrirlo!", "[BIO]"), P)}</span></span></h1>
    <p class="hero__sub" lang="es">{q(SITE["bio1"], P)}</p>
    <div class="hero__ctas">{btn(L("Ver tours", "See tours"), "/tours/", "btn btn--light")}{btn(L("Reservar por WhatsApp", "Book on WhatsApp"), wa_link("Hola! Quiero consultar por los tours"), "btn btn--red", True)}</div>
  </div>
  <p class="hero__cap" lang="es">Columpio del lago Huillinco · <span class="sr">foto</span>@chiloemagicotour</p>
</section>

<section class="trust" aria-label="Datos de confianza" data-aria-en="Trust facts">
  <ul>
    <li><strong>{SITE["rating"]} ★</strong><span>{L(f"Google · {SITE['reviews_count']} reseñas", f"Google · {SITE['reviews_count']} reviews")}</span></li>
    <li><strong>{L("Lu a Do", "Mon–Sun")}</strong><span>{L("Tours todos los días", "Tours every day")}</span></li>
    <li><strong>16</strong><span>{L("pasajeros máx. por van, con su guía", "passengers max. per van, with their guide")}</span></li>
    <li><strong>+20</strong><span>{L("años de servicio, según la agencia", "years of service, as stated by the agency")}</span></li>
    <li><strong>10:00</strong><span>{L("salida frente a la Plaza de Armas de Castro", "departure facing Castro's main square")}</span></li>
  </ul>
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

<section class="sec tours-home">
  <header class="sec__head sec__head--row">
    <div><p class="kicker">{L("Nuestros tours disponibles", "Our available tours")}</p>
    <h2 class="h2" data-lines><span class="line"><span>{L("Tours de día completo", "Full-day tours")}</span></span></h2></div>
    <p class="lead" lang="es">{q(Q("Todos nuestros tours incluyen traslado, guiado, almuerzo y bebestibles, y visitas a distintos atractivos turísticos 🌿", "[IG-007]"), P)}</p>
  </header>
  <div class="swiper tours__sw" data-swiper="cards" data-drag><div class="swiper-wrapper">{tours}</div></div>
  <div class="tours__foot">{btn(L("Ver todos los tours", "See all tours"), "/tours/", "btn btn--ink")}</div>
</section>

<section class="sec dests">
  <header class="sec__head"><p class="kicker">{L("Explora por destino", "Explore by destination")}</p>
  <h2 class="h2" data-lines><span class="line"><span>{L("El archipiélago,", "The archipelago,")}</span></span><span class="line"><span>{L("isla por isla", "island by island")}</span></span></h2></header>
  <ul class="dests__list">{dests}</ul>
</section>

<section class="sec exps" data-hover-zone>
  <header class="sec__head"><p class="kicker">{L("Explora por experiencia", "Explore by experience")}</p></header>
  <ul class="exps__list">{exps}</ul>
  <div class="exps__float" aria-hidden="true">{exp_imgs}</div>
</section>

<section class="sec why">
  <div class="why__media">
    <video class="why__v" muted playsinline loop preload="none" data-lazy-video data-poster="/assets/video/vans-poster.jpg" aria-label="{e(META['_videos']['vans']['alt'])}" data-aria-en="{e(ALT_EN['vid:vans'])}"><source data-src="/assets/video/vans.webm" type="video/webm"><source data-src="/assets/video/vans.mp4" type="video/mp4"></video>
  </div>
  <div class="why__txt">
    <p class="kicker">{L("Por qué viajar con nosotros", "Why travel with us")}</p>
    <h2 class="h3" lang="es" data-lines><span class="line"><span>{q(Q("¡NO DEJES QUE TE LO CUENTEN…!", "[IG-007]", fix="recorte del remate «¡NO DEJES QUE TE LO CUENTEN, VEN A DISFRUTAR…»"), P)}</span></span></h2>
    <p lang="es" class="why__p">{q(SITE["servicio"], P)}</p>
    <ul class="why__list">
      <li lang="es">{q(SITE["vans"], P)}</li>
      <li lang="es">{q(SITE["van16"], P)}</li>
      <li lang="es">{q(SITE["salida"], P)} ⛪️</li>
      <li lang="es">{q(SITE["horario_tour"], P)}</li>
    </ul>
  </div>
</section>

<section class="sec pkgs">
  <header class="sec__head sec__head--row"><div><p class="kicker">{L("Paquetes de varios días", "Multi-day packages")}</p>
  <h2 class="h2" data-lines><span class="line"><span>{L("Más allá de la isla", "Beyond the island")}</span></span></h2></div>
  <p class="lead" lang="es">{q(SITE["privados"], P)}</p></header>
  <ul class="pkgs__list">{pkgs}</ul>
  <div class="tours__foot">{btn(L("Arma tu viaje a medida", "Plan a custom trip"), "/paquetes/#a-medida", "btn btn--ink")}</div>
</section>

{reviews_block(P, D.REVIEWS)}

<section class="sec guia-home">
  <header class="sec__head"><p class="kicker">{L("Guía de Chiloé", "Chiloé guide")}</p>
  <h2 class="h2" data-lines><span class="line"><span>{L("Lo que cuentan", "What they tell")}</span></span><span class="line line--script"><span>{L("en el camino", "along the way")}</span></span></h2></header>
  <ul class="guia__list">{guia}</ul>
</section>

<section class="sec contact-home">
  <div class="contact__txt">
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


# ------------------------------------------------------------------ TOURS
def tours_index():
    P = '/tours/'
    filt = ''.join(f'<button type="button" class="chip" data-filter="{x["slug"]}" aria-pressed="false">{L(x["name"])}</button>' for x in D.EXPERIENCIAS)
    cards = ''.join(f'<li data-exp="{" ".join(t["exp"])}">{tour_card(t, P, "(max-width:760px) 90vw, 30vw")}</li>' for t in D.TOURS)
    content = f'''
<section class="phead">
  <p class="kicker">{L("Tours", "Tours")}</p>
  <h1 class="h1" lang="es" data-lines><span class="line"><span>NUESTROS TOURS</span></span><span class="line line--script"><span>disponibles</span></span></h1>
  <p class="lead" lang="es">{q(SITE["horario_tour"], P)}</p>
  <p class="lead" lang="es">{q(SITE["cupos"], P)} 😉</p>
</section>
<section class="sec tours-grid">
  <h2 class="sr">{L("Todos los tours", "All tours")}</h2>
  <div class="chips" role="group" aria-label="Filtrar por experiencia" data-aria-en="Filter by experience"><button type="button" class="chip" data-filter="all" aria-pressed="true">{L("Todos", "All")}</button>{filt}</div>
  <ul class="grid3" data-filter-grid>{cards}</ul>
</section>
{booking_cta(P, "Hola! Quiero consultar por los tours")}'''
    COPY.append((P, 'NUESTROS TOURS disponibles', '[DEST-H7_001] "NUESTROS TOURS DISPONIBLES"', 'Se separa "disponibles" en cursiva'))
    page(P, 'Tours en Chiloé desde Castro · Turismo Chiloé Mágico', 'Chiloé tours from Castro · Turismo Chiloé Mágico',
         'Siete tours de día completo desde Castro con traslado, guiado, almuerzo y bebestibles.',
         'Seven full-day tours from Castro with transport, guiding, lunch and drinks.', content)


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
    for s in t['stops']:
        pass
    body = ''.join(q(b, P, 'p') for b in t['body'])
    gallery = ''.join(f'<div class="swiper-slide gal__s">{img(k, "(max-width:760px) 80vw, 40vw")}</div>' for k in t['gallery'])
    extras = ''.join(f'<li lang="es">{q(x, P)}</li>' for x in t.get('extras', []))
    season = (f'<p lang="es">{L("Temporada:", "Season:")} {q(t["season"], P)} · {L("meses exactos por confirmar.", "exact months to be confirmed.")}</p>' if t.get('season') else '')
    content = f'''
<nav class="crumbs" aria-label="Migas de pan" data-aria-en="Breadcrumbs"><a href="/">{L("Inicio", "Home")}</a> › <a href="/tours/">Tours</a> › <span aria-current="page" lang="es">{e(t["short"])}</span></nav>
<section class="thero">
  <div class="thero__txt">
    <p class="kicker">{L(t["tag"])} · <span class="stars">★ {SITE["rating"]}</span> <span class="muted">({L(f"{SITE['reviews_count']} reseñas de la agencia", f"{SITE['reviews_count']} agency reviews")})</span></p>
    {title_afiche(t["title"], P)}
    <p class="thero__hook" lang="es">{q(t["hook"], P)}</p>
  </div>
  {media(t["hero"], "(max-width:760px) 100vw, 46vw", "thero__media", True, "4/5", True)}
</section>

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
    <h2 class="h4">{L("Mapa del punto de salida", "Departure point map")}</h2>{map_block(P)}
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

{f'<section class="sec gal"><div class="swiper gal__sw" data-swiper="gallery" data-drag><div class="swiper-wrapper">{gallery}</div></div></section>' if t["gallery"] else ''}
{reviews_block(P, revs, False) if revs else ''}
<section class="sec faq-mini">
  <h2 class="h3">{L("Preguntas frecuentes", "Frequently asked questions")}</h2>
  {faq_items(P, [D.FAQ[i] for i in (5, 6, 7, 10)])}
  <a class="u-link" href="/preguntas-frecuentes/">{L("Ver todas", "See all")}</a>
</section>
<section class="sec related">
  <header class="sec__head"><p class="kicker">{L("Tours relacionados", "Related tours")}</p></header>
  <ul class="grid3">{''.join(f"<li>{tour_card(x, P)}</li>" for x in rel)}</ul>
</section>
{booking_cta(P, wa_t)}'''
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
    items = ''.join(f'<li><a class="bigcard" href="{dest_href(d)}" data-card>{media(d["img"], "(max-width:760px) 90vw, 45vw", "bigcard__media", ratio="4/3")}'
                    f'<h2 class="h3" lang="es">{e(d["name"])}</h2><p lang="es">{q(d["intro"], P)}</p></a></li>' for d in D.DESTINOS)
    content = f'''<section class="phead"><p class="kicker">{L("Destinos", "Destinations")}</p>
<h1 class="h1" data-lines><span class="line"><span>{L("Explora por", "Explore by")}</span></span><span class="line line--script"><span>{L("destino", "destination")}</span></span></h1>
<p class="lead" lang="es">{q(SITE["diarias"], P)}</p></section>
<section class="sec"><ul class="grid2">{items}</ul></section>{booking_cta(P, "Hola! Quiero consultar por los tours")}'''
    page(P, 'Destinos en Chiloé · Turismo Chiloé Mágico', 'Destinations in Chiloé · Turismo Chiloé Mágico',
         'Castro, Ancud y Puñihuil, Dalcahue y Quinchao, Chonchi e Isla Lemuy, Cucao y el Parque Nacional Chiloé.',
         'Castro, Ancud and Puñihuil, Dalcahue and Quinchao, Chonchi and Lemuy Island, Cucao and Chiloé National Park.', content)
    for d in D.DESTINOS:
        P = dest_href(d)
        ts = [t for t in D.TOURS if d['slug'] in t['dest']]
        must = ''.join(f'<li lang="es">{e(m)}</li>' for m in d['must'])
        COPY.append((P, ' / '.join(d['must']), 'nombres de lugares de los afiches [DEST-H7] y posts', None))
        content = f'''<nav class="crumbs" aria-label="Migas de pan" data-aria-en="Breadcrumbs"><a href="/">{L("Inicio", "Home")}</a> › <a href="/destinos/">{L("Destinos", "Destinations")}</a> › <span aria-current="page" lang="es">{e(d["name"])}</span></nav>
<section class="dhero">{media(d["img"], "100vw", "dhero__media", True, None, True)}<div class="dhero__in"><h1 class="h1 h1--light" lang="es" data-lines><span class="line"><span>{e(d["name"].upper())}</span></span></h1></div></section>
<section class="sec split">
  <div><p class="lead" lang="es">{q(d["intro"], P)}</p>{''.join(q(b, P, 'p') for b in d["body"])}
  <h2 class="h4">{L("Imperdibles", "Must-sees")}</h2><ul class="must">{must}</ul>
  <h2 class="h4">{L("Cómo llegar desde Castro · mejor época", "Getting there from Castro · best season")}</h2>
  <p lang="es">{q(SITE["salida"], P)}</p>{pending(P)}</div>
  <div class="split__imgs">{''.join(media(k, "(max-width:760px) 90vw, 35vw", "", ratio="4/5", parallax=True) for k in d["imgs"])}</div>
</section>
<section class="sec"><header class="sec__head"><p class="kicker">{L("Tours que pasan por aquí", "Tours that stop here")}</p></header><ul class="grid3">{''.join(f"<li>{tour_card(t, P)}</li>" for t in ts)}</ul></section>
{booking_cta(P, f"Hola! Quiero conocer {d['name']}")}'''
        page(P, f'{d["name"]} · Turismo Chiloé Mágico', f'{d["name"]} · Turismo Chiloé Mágico',
             f'Qué hacer en {d["name"]}, Chiloé: {", ".join(d["must"])}. Tours desde Castro.', f'Things to do in {d["name"]}, Chiloé. Tours from Castro.',
             content, preload=preload_img(d['img']))


def experiencias():
    P = '/experiencias/'
    items = ''.join(f'<li><a class="bigcard" href="{exp_href(x)}" data-card>{media(x["img"], "(max-width:760px) 90vw, 30vw", "bigcard__media", ratio="1/1")}'
                    f'<h2 class="h3">{L(x["name"])}</h2><p lang="es">{q(x["quote"], P)}</p></a></li>' for x in D.EXPERIENCIAS)
    content = f'''<section class="phead"><p class="kicker">{L("Experiencias", "Experiences")}</p>
<h1 class="h1" data-lines><span class="line"><span>{L("Explora por", "Explore by")}</span></span><span class="line line--script"><span>{L("experiencia", "experience")}</span></span></h1>
<p class="lead" lang="es">{q(SITE["magia"], P)}</p></section><section class="sec"><ul class="grid3">{items}</ul></section>'''
    page(P, 'Experiencias en Chiloé · Turismo Chiloé Mágico', 'Experiences in Chiloé · Turismo Chiloé Mágico',
         'Patrimonio e iglesias, naturaleza, navegación, gastronomía chilota y mitos de Chiloé.', 'Heritage churches, nature, boat trips, Chilote food and myths of Chiloé.', content)
    for x in D.EXPERIENCIAS:
        P = exp_href(x)
        ts = [t for t in D.TOURS if x['slug'] in t['exp']]
        content = f'''<nav class="crumbs" aria-label="Migas de pan" data-aria-en="Breadcrumbs"><a href="/">{L("Inicio", "Home")}</a> › <a href="/experiencias/">{L("Experiencias", "Experiences")}</a> › <span aria-current="page">{L(x["name"])}</span></nav>
<section class="dhero">{media(x["img"], "100vw", "dhero__media", True, None, True)}<div class="dhero__in"><h1 class="h1 h1--light" data-lines><span class="line"><span>{L(x["name"])}</span></span></h1></div></section>
<section class="sec narrow"><p class="lead" lang="es">{q(x["quote"], P)}</p><p lang="es">{q(x["more"], P)}</p></section>
<section class="sec"><header class="sec__head"><p class="kicker">{L("Tours con esta experiencia", "Tours with this experience")}</p></header><ul class="grid3">{''.join(f"<li>{tour_card(t, P)}</li>" for t in ts)}</ul></section>
{booking_cta(P, "Hola! Quiero consultar por los tours")}'''
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
        imgs = ''.join(media(k, "(max-width:760px) 90vw, 30vw", "", ratio="4/5") for k in p['imgs']) or f'<div class="pkg__type pkg__type--big" aria-hidden="true">❄</div>'
        extra = q(p['extra'], P, 'p') if p.get('extra') else ''
        items += f'''<article class="pkgrow"><div class="pkgrow__imgs">{imgs}</div><div class="pkgrow__t"><p class="kicker">{L(p["days"])}</p>
<h2 class="h3" lang="es">{e(p["name"])}</h2>{q(p["text"], P, "p")}{extra}
<h3 class="h5">{L("Itinerario día a día, alojamiento, comidas y precio en base doble", "Day-by-day itinerary, lodging, meals and price per person (double)")}</h3>{pending(P)}
{btn(L("Cotizar", "Get a quote"), wa_link(f"Hola! Quiero cotizar el viaje {p['name']}"), "btn btn--ink", True)}</div></article>'''
    content = f'''<section class="phead"><p class="kicker">{L("Paquetes", "Packages")}</p>
<h1 class="h1" data-lines><span class="line"><span>{L("Viajes de", "Trips of")}</span></span><span class="line line--script"><span>{L("varios días", "several days")}</span></span></h1>
<p class="lead" lang="es">{q(SITE["privados"], P)}</p>
<p class="note">{L("Viajes que la agencia ya ha realizado según sus publicaciones. Próximas salidas y valores: por confirmar.", "Trips the agency has already run, according to its posts. Next departures and prices: to be confirmed.")}</p></section>
<section class="sec">{items}</section>
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
    items = ''.join(f'<li class="srv">{media(k, "(max-width:760px) 90vw, 30vw", "", ratio="4/3")}<h2 class="h3">{L(t)}</h2><p lang="es">{q(x, P)}</p>'
                    f'<p class="note">{L("Recorridos, vehículos y tarifas: por confirmar con la agencia.", "Routes, vehicles and rates: to be confirmed with the agency.")}</p>'
                    f'{btn(L("Cotizar", "Get a quote"), wa_link("Hola! Quiero cotizar: " + t.es), "btn btn--ink btn--sm", True)}</li>' for t, x, k in cards)
    content = f'''<section class="phead"><p class="kicker">{L("Servicios", "Services")}</p>
<h1 class="h1" data-lines><span class="line"><span>{L("Traslados, privados", "Transfers, private")}</span></span><span class="line line--script"><span>{L("y grupos", "and groups")}</span></span></h1>
<p class="lead" lang="es">{q(SITE["vans"], P)}</p></section>
<section class="sec"><ul class="grid3">{items}</ul></section>{booking_cta(P, "Hola! Quiero cotizar un servicio privado")}'''
    page(P, 'Servicios privados y traslados · Turismo Chiloé Mágico', 'Private services and transfers · Turismo Chiloé Mágico',
         'Viajes privados, traslados y grupos en vans con aire acondicionado desde Castro.', 'Private trips, transfers and groups in air-conditioned vans from Castro.', content)


def nosotros():
    P = '/nosotros/'
    team = ''.join(f'<li><span class="team__n" lang="es">{e(m["name"])}</span><span class="team__r">{L(m["role"])}</span></li>' for m in D.TEAM)
    COPY.append((P, ', '.join(m['name'] for m in D.TEAM), 'nombres en posts y reseñas: ' + ' '.join(m['src'] for m in D.TEAM), None))
    content = f'''<section class="phead"><p class="kicker">{L("Nosotros", "About us")}</p>
<h1 class="h1" lang="es" data-lines><span class="line"><span>SOMOS</span></span><span class="line line--script"><span>Chiloé Mágico</span></span></h1>
<p class="lead" lang="es">{q(SITE["somos"], P)}</p></section>
<section class="sec split">
  <div><p lang="es">{q(SITE["anos"], P)}</p><p lang="es">{q(SITE["magia"], P)}</p><p lang="es">{q(SITE["magia2"], P)}</p>
  <blockquote class="pull" lang="es">“{q(SITE["marketing"], P)}”</blockquote><p lang="es">{q(SITE["irrepetible"], P)}</p></div>
  <div class="split__imgs">{media("nicolas-enrique", "(max-width:760px) 90vw, 35vw", "", ratio="1/1", parallax=True)}{media("vans", "(max-width:760px) 90vw, 35vw", "", ratio="4/3", parallax=True)}</div>
</section>
<section class="sec team"><header class="sec__head"><p class="kicker">{L("Equipo", "Team")}</p><h2 class="h2">{L("Guías y conductores", "Guides and drivers")}</h2>
<p class="lead">{L("Nombres tal como aparecen en sus publicaciones y en las reseñas de Google. Fotos del equipo: por confirmar.", "Names as they appear in the agency's posts and Google reviews. Team photos: to be confirmed.")}</p></header>
<ul class="team__list">{team}</ul>
<figure class="team__fig">{media("nicolas-enrique", "(max-width:760px) 90vw, 40vw", "", ratio="4/3")}<figcaption lang="es">{q(Q("Nuestro guía Nicolás junto a don Enrique siempre enfocados en brindarle la mejor experiencia a nuestros turistas!", "[IG-023]"), P)}</figcaption></figure></section>
<section class="sec narrow"><h2 class="h3">{L("Flota", "Fleet")}</h2><p lang="es">{q(SITE["van16"], P)}</p>
<h2 class="h3">{L("Registro Sernatur y sellos", "Sernatur registry and certifications")}</h2>
<p>{L("Número de registro Sernatur, razón social y sellos:", "Sernatur registry number, legal name and seals:")}</p>{pending(P)}</section>
{reviews_block(P, D.REVIEWS[:6])}'''
    page(P, 'Nosotros · Turismo Chiloé Mágico', 'About us · Turismo Chiloé Mágico',
         'Agencia local de turismo en Castro, Chiloé: guías, conductores y vans para recorrer el archipiélago.', 'Local travel agency in Castro, Chiloé.', content)


def guia():
    P = '/guia/'
    items = ''.join(f'<li><a class="gcard" href="/guia/{g["slug"]}/" data-card>{media(g["img"], "(max-width:760px) 90vw, 30vw", "gcard__media", ratio="4/3")}<h2 class="h4">{L(g["title"])}</h2></a></li>' for g in D.GUIA)
    content = f'''<section class="phead"><p class="kicker">{L("Guía de Chiloé", "Chiloé guide")}</p>
<h1 class="h1" data-lines><span class="line"><span>{L("Historias del", "Stories of the")}</span></span><span class="line line--script"><span>{L("archipiélago", "archipelago")}</span></span></h1>
<p class="lead">{L("Textos publicados por la agencia en su Instagram.", "Texts published by the agency on its Instagram.")}</p></section>
<section class="sec"><ul class="grid3">{items}</ul>
<div class="narrow"><h2 class="h3">{L("Cuándo viajar, clima y cómo llegar a Chiloé", "When to travel, weather and how to reach Chiloé")}</h2><p lang="es">{q(SITE["clima"], P)}</p>{pending(P)}</div></section>'''
    page(P, 'Guía de Chiloé · Turismo Chiloé Mágico', 'Chiloé guide · Turismo Chiloé Mágico',
         'Curanto, iglesias patrimonio, brujos y almas, la minga y los pingüinos de Puñihuil.', 'Curanto, heritage churches, myths, the minga and Puñihuil penguins.', content)
    for g in D.GUIA:
        P = f'/guia/{g["slug"]}/'
        ts = [TOURS[s] for s in g['tours']]
        content = f'''<nav class="crumbs" aria-label="Migas de pan" data-aria-en="Breadcrumbs"><a href="/">{L("Inicio", "Home")}</a> › <a href="/guia/">{L("Guía", "Guide")}</a> › <span aria-current="page">{L(g["title"])}</span></nav>
<article class="art"><header class="art__head"><h1 class="h1" data-lines><span class="line"><span>{L(g["title"])}</span></span></h1></header>
{media(g["img"], "(max-width:760px) 100vw, 60vw", "art__media", True, "16/10", True)}
<div class="art__body narrow">{''.join(q(p, P, 'p') for p in g["paras"])}<p class="note">{L("Fuente: publicaciones de @chiloemagicotour.", "Source: @chiloemagicotour posts.")}</p></div></article>
{f'<section class="sec"><header class="sec__head"><p class="kicker">{L("Vívelo en", "Experience it on")}</p></header><ul class="grid3">' + ''.join(f"<li>{tour_card(t, P)}</li>" for t in ts) + '</ul></section>' if ts else ''}'''
        page(P, f'{g["title"].es} · Guía de Chiloé', f'{g["title"].en} · Chiloé guide', f'{g["title"].es}: guía de Chiloé de Turismo Chiloé Mágico.',
             f'{g["title"].en}: Chiloé guide by Turismo Chiloé Mágico.', content, preload=preload_img(g['img']))


def faq():
    P = '/preguntas-frecuentes/'
    content = f'''<section class="phead"><p class="kicker">FAQ</p><h1 class="h1" data-lines><span class="line"><span>{L("Preguntas", "Frequently asked")}</span></span><span class="line line--script"><span>{L("frecuentes", "questions")}</span></span></h1></section>
<section class="sec narrow">{faq_items(P, D.FAQ)}</section>{booking_cta(P, "Hola! Tengo una consulta")}'''
    page(P, 'Preguntas frecuentes · Turismo Chiloé Mágico', 'FAQ · Turismo Chiloé Mágico',
         'Salidas, horarios, qué incluye, idioma, grupos y reservas de los tours de Turismo Chiloé Mágico.', 'Departures, times, inclusions, language, groups and bookings.', content)


def contacto():
    P = '/contacto/'
    content = f'''<section class="phead"><p class="kicker">{L("Contacto", "Contact")}</p><h1 class="h1" lang="es" data-lines><span class="line"><span>{q(Q("RESERVA AHORA", "[PIEZA IG-017]"), P)}</span></span></h1>
<p class="lead" lang="es">{q(SITE["reservas"], P)}: 📲 {SITE["wa_display"]}</p></section>
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
<section class="sec">{map_block(P)}</section>'''
    page(P, 'Contacto y reservas · Turismo Chiloé Mágico', 'Contact and bookings · Turismo Chiloé Mágico',
         'WhatsApp +56 9 7890 2625, Gamboa 351, Local Interior 116, frente a la Plaza de Armas de Castro. Lunes a domingo 9:00 a 19:30.',
         'WhatsApp +56 9 7890 2625, Gamboa 351, Castro. Mon–Sun 9:00–19:30.', content)


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
