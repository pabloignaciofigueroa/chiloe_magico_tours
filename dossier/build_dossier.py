# Dossier de decisiones de diseño · Turismo Chiloé Mágico
# Genera dossier/chiloemagico-dossier-diseno.html (autocontenido). Adaptado del caso RILÁN.
import base64, html, io, json, pathlib, re
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / 'dossier'
SH = D / 'shots'
IMG = ROOT / 'assets/img'
E = html.escape

# ---------- fuentes citables (desde los archivos, no de memoria) ----------
MESES = 'ene feb mar abr may jun jul ago sep oct nov dic'.split()
IGD = {}
for l in (ROOT / 'content/ig_posts.md').read_text(encoding='utf-8').splitlines():
    m = re.match(r'### \[IG-(\d+)\] (\d{4})-(\d\d)-(\d\d) ', l)
    if m:
        IGD[m.group(1)] = f'{int(m.group(4))} {MESES[int(m.group(3)) - 1]} {m.group(2)}'
def IG(n): return f'Instagram · {IGD[n]}'
MEDIA = json.loads((ROOT / 'content/media.json').read_text(encoding='utf-8'))['images']
def ORIG(key):
    f = MEDIA[key][0]
    return IG(f[:3]) if f[:3].isdigit() else 'Foto de libre uso, con su autor citado'
REV = json.loads((ROOT / 'content/google_reviews.json').read_text(encoding='utf-8'))
N_REV = REV['count']; NOTA = str(REV['rating']).replace('.', ',')
rv = REV['reviews']
has = lambda ws: sum(any(w in (x.get('txt') or '').lower() for w in ws) for x in rv)
N_GUIA = has(['guía', 'guia', 'guide'])
N_NOMBRE = sum(bool(re.search(r'\b(nicol[aá]s|nico|alberto|beto|enrique|sandra|meli|rodolfo|marcelo|marco)\b', (x.get('txt') or '').lower())) for x in rv)
N_COMIDA = has(['comida', 'curanto', 'asado', 'almuerzo', 'food', 'lunch', 'cordero'])
N5 = sum(x['stars'].startswith('5') for x in rv); N2 = N_REV - N5
posts = re.findall(r'^### \[IG-\d+\] \S+ · \S+ · autor: (\S+)', (ROOT / 'content/ig_posts.md').read_text(encoding='utf-8'), re.M)
N_POSTS = len(posts); N_PROPIOS = posts.count('chiloemagicotour')
N_FOTOS = len(MEDIA); N_PROPIAS = sum(v[0][:3].isdigit() for v in MEDIA.values())
N_POSTS_FOTOS = len({v[0][:3] for v in MEDIA.values() if v[0][:3].isdigit()})

# ---------- imágenes ----------
def b64img(img, w, q=80):
    img = img.convert('RGB')
    if img.width > w:
        img = img.resize((w, round(img.height * w / img.width)), Image.LANCZOS)
    buf = io.BytesIO(); img.save(buf, 'JPEG', quality=q, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
def shot(name, w=1500):
    p = SH / f'{name}.jpg'
    return b64img(Image.open(p), w) if p.exists() else ''
def src(key, w=420):
    return b64img(Image.open(IMG / f'{key}-800.webp'), w, 76)
def raw(key, w=1950):
    p = IMG / f'{key}-1800.webp'
    return b64img(Image.open(p if p.exists() else IMG / f'{key}-800.webp'), w, 82)
def font(name):
    return 'data:font/woff2;base64,' + base64.b64encode((ROOT / 'assets/fonts' / f'{name}.woff2').read_bytes()).decode()
def png_file(rel, w=900):
    im = Image.open(ROOT / rel).convert('RGBA')
    if im.width > w:
        im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()

COORDS = '42° 28′ 54″ S · 73° 45′ 51″ O'
MARK = f'<img class="mk" src="{png_file("brand/logo/isotipo-color.png", 300)}" alt="">'
RECORRIDO = ['Portada', 'Vamos a navegar', 'Elige tu tour', 'Ficha de tour', 'Reseñas', 'Nosotros',
             'Destinos', 'Experiencias', 'Guía de Chiloé', 'Paquetes', 'Servicios privados', 'Preguntas frecuentes', 'Contacto']
AFICHES = 'Destacada «Tours» · afiches de 2023'

def quote(text, source, lang=''):
    la = f' lang="{lang}"' if lang else ''
    return f'<blockquote class="q"{la}><p>{text}</p><cite>{E(source)}</cite></blockquote>'
def thumbs(items):
    out = [f'<figure class="th"><img src="{src(k)}" alt=""><figcaption>{E(cap)}</figcaption></figure>' for k, cap in items]
    return f'<div class="ths">{"".join(out)}</div>'
def chips(items):
    return '<div class="chips">' + ''.join(
        f'<span class="chip"><i style="background:{hx}"></i><b>{E(n)}</b> {hx}</span>' for n, hx in items) + '</div>'
def block(title, body, cls=''):
    return f'<section class="bk {cls}"><h4>{title}</h4>{body}</section>'
def recorrido(cur):
    cur = cur if isinstance(cur, tuple) else (cur,)
    li = ''.join(f'<li class="{"on" if r in cur else ""}">{E(r)}</li>' for r in RECORRIDO)
    return f'<ol class="rec">{li}</ol>'
PIE = lambda n: f'<footer class="pf"><span>Chiloé Mágico · Decisiones de diseño del sitio</span><span>{COORDS}</span><span>{n:02d}</span></footer>'

C = dict(niebla='#f2f1ec', bruma='#dfe4e6', tinta='#1d2421', musgo='#46473b', tierra='#a69775', mar='#1a8fc4',
         marh='#126a96', isla='#0e766c', chiloe='#17853f', chiloeh='#106530', turismo='#d0342c', turismoh='#b02a23')
def P(*names):
    nom = {'niebla': 'Niebla de Castro', 'bruma': 'Bruma', 'tinta': 'Tinta de alerce', 'musgo': 'Musgo',
           'tierra': 'Tierra chilota', 'mar': 'Mar del logo', 'marh': 'Mar hondo', 'isla': 'Isla Grande',
           'chiloe': 'Verde Chiloé', 'chiloeh': 'Verde hondo', 'turismo': 'Rojo Turismo', 'turismoh': 'Rojo banda'}
    return chips([(nom[n], C[n]) for n in names])

def lamina_seccion(n, nombre, titulo, lead, desk, mob, bloques, nota_izq='', desk2=None, hl=None):
    left_extra = f'<img class="desk2" src="{shot(desk2)}" alt="">' if desk2 else ''
    if desk2: mob = None
    mob_html = f'<img class="mob" src="{shot(mob, 520)}" alt="">' if mob else ''
    return f'''<article class="lam">
  <div class="L {'two' if desk2 else ''}">
    <p class="lab">Sitio · computador</p>
    <img class="desk" src="{shot(desk)}" alt="">{left_extra}
    <div class="Lrow">
      {f'<div class="mobw"><p class="lab">Celular</p>{mob_html}</div>' if mob else ''}
      <div class="Linfo"><p class="lab">Lugar en el recorrido</p>{recorrido(hl or nombre)}
        {f'<p class="lnote">{nota_izq}</p>' if nota_izq else ''}</div>
    </div>
  </div>
  <div class="R"><p class="kick">{n:02d} · {E(nombre)}</p><h2>{titulo}</h2><p class="lead">{lead}</p>
    <div class="grid">{''.join(bloques)}</div>{PIE(n)}</div>
</article>'''
def lamina_libre(n, left_html, right_html, left_cls='', right_cls=''):
    return f'''<article class="lam"><div class="L {left_cls}">{left_html}</div>
  <div class="R {right_cls}">{right_html}{PIE(n)}</div></article>'''

L, n = [], 0
def nx():
    global n; n += 1; return n
def S(nombre, titulo, lead, desk, mob, bloques, nota='', desk2=None, hl=None):
    L.append(lamina_seccion(nx(), nombre, titulo, lead, desk, mob, bloques, nota, desk2, hl))

# ======================= LÁMINAS (diseño libre, colores alternados) =======================
GULL = '<svg viewBox="0 0 100 100" class="gull" style="{st}"><path d="M4,4 C22,16 42,36 56,55 C62,53 70,52 78,53 C82,53.5 85,55 86,57 C83,59 79,60 75,61 C82,72 90,85 97,98 C86,88 75,76 66,65 C58,66 50,67 44,69 C47,66 50,63 52,61 C40,42 22,20 4,4 Z" fill="{c}"/></svg>'
def gull(x, y, w, c, rot=0, flip=False):
    sx = -1 if flip else 1
    return GULL.format(st=f'left:{x}in;top:{y}in;width:{w}in;transform:rotate({rot}deg) scaleX({sx})', c=c)
def wave(c, h=.8, top=None, flip=False):
    pos = f'top:{top}in' if top is not None else 'bottom:0'
    tr = 'transform:scaleY(-1);' if flip else ''
    return f'<svg class="wave" viewBox="0 0 1440 120" preserveAspectRatio="none" style="{pos};height:{h}in;{tr}"><path d="M0,120 L0,70 C360,10 820,0 1440,58 L1440,120 Z" fill="{c}"/></svg>'
def fr(name, x, y, w, rot=0, z=2):
    return f'<div class="fr" style="left:{x}in;top:{y}in;width:{w}in;transform:rotate({rot}deg);z-index:{z}"><img src="{shot(name, 1400)}" alt=""></div>'
def ph(name, x, y, w, rot=0, z=3):
    return f'<div class="ph" style="left:{x}in;top:{y}in;width:{w}in;transform:rotate({rot}deg);z-index:{z}"><img src="{shot(name, 560)}" alt=""></div>'
def medal(x, y, d, bg, fg, html_, rot=0, fs=11, z=4):
    return f'<div class="md" style="left:{x}in;top:{y}in;width:{d}in;height:{d}in;background:{bg};color:{fg};transform:rotate({rot}deg);font-size:{fs}pt;z-index:{z}"><div>{html_}</div></div>'
def box(x, y, w, inner, cls='', st=''):
    return f'<div class="tx {cls}" style="left:{x}in;top:{y}in;width:{w}in;{st}">{inner}</div>'
def pill(t, bg, fg='#fff'):
    return f'<span class="pill" style="background:{bg};color:{fg}">{E(t)}</span>'
def Q(text, source, lang='', cls=''):
    la = f' lang="{lang}"' if lang else ''
    return f'<blockquote class="q2 {cls}"{la}><p>“{text}”</p><cite>{E(source)}</cite></blockquote>'
def lam(bg, inner, nc='rgba(29,36,33,.45)', cls=''):
    k = nx()
    return f'<article class="lam free {cls}" style="background:{bg}">{inner}<span class="no" style="color:{nc}">{k:02d}</span></article>'
def photo(key, x, y, w, h, r=.28, pos='50% 50%', z=1, rot=0, border=''):
    return f'<div class="pic" style="left:{x}in;top:{y}in;width:{w}in;height:{h}in;border-radius:{r}in;transform:rotate({rot}deg);z-index:{z};{border}"><img src="{raw(key, 1500)}" style="object-position:{pos}" alt=""></div>'

NI, BR, TI, MU, TE = C['niebla'], C['bruma'], C['tinta'], C['musgo'], C['tierra']
MAR, MARH, ISLA, VER, ROJO, ROJOH = C['mar'], C['marh'], C['isla'], C['chiloe'], C['turismo'], C['turismoh']

# 01 · PORTADA
nx()
L.append(f'''<article class="lam spread">
  <img class="bleed" src="{raw("huillinco-columpio", 2600)}" style="object-position:50% 62%" alt="">
  <div class="spread-tab"><img class="spread-logo" src="{png_file("brand/logo/logo-color.png", 900)}" alt="Turismo Chiloé Mágico"></div>
</article>''')

# 02 · CARTA · niebla, foto redondeada, ola azul, medallón rojo
L.append(lam(NI,
  photo('nicolas-enrique', .45, .45, 5.6, 7.3, pos='50% 40%', z=2) +
  medal(8.7, 4.75, 1.75, ROJO, '#fff', 'UN REGALO<br>PARA<br>CHILOÉ<br>MÁGICO', rot=-8, fs=16) +
  box(6.65, .75, 5.85, f'''<p class="k" style="color:{ISLA}">Antes de empezar</p>
  <h2 class="t" style="color:{TI}">Un sitio hecho <em style="color:{ROJO}">con</em> lo que ustedes ya dijeron</h2>
  <div class="letter2">
  <p>Equipo de Chiloé Mágico:</p>
  <p>Este sitio nació de mirar con atención lo que ustedes ya publican. No hay frases inventadas ni promesas de agencia: cada título sale de sus posts, sus destacadas, sus afiches, su bio o de lo que sus viajeros escribieron en Google. Lo que hicimos fue ordenarlo, darle aire y ponerlo en movimiento.</p>
  <p>Tampoco hay fotos de banco: de las {N_FOTOS} fotos del sitio, {N_PROPIAS} y los 3 videos son suyos. La única excepción es una foto de libre uso del volcán Osorno, con su autor citado.</p>
  <p>Es un regalo. Ojalá lo disfruten tanto como nosotros disfrutamos haciéndolo.</p>
  <p class="sign2">Pablo Figueroa G. · Director de estudio</p></div>''')))

# 03 · DE DÓNDE VIENE TODO · rojo, polaroids, cifras gigantes
pol = [('caleuche', .55, .7, -8), ('curanto-destape', 2.55, .45, 5), ('tenaun', 4.35, .9, -3),
       ('brujos-columpio-2', .8, 3.15, 4), ('palafitos', 2.85, 2.95, -6), ('vans', 4.55, 3.35, 7),
       ('almas-pareja', 1.0, 5.55, -4), ('pasarela-aucar', 3.1, 5.4, 3)]
polh = ''.join(f'<div class="pol" style="left:{x}in;top:{y}in;transform:rotate({r}deg)"><img src="{src(k, 420)}" alt=""></div>' for k, x, y, r in pol)
def big(nm, cap): return f'<div class="bign"><b>{nm}</b><span>{cap}</span></div>'
L.append(lam(ROJOH, polh + gull(11.6, .45, .8, 'rgba(255,255,255,.9)', -8) +
  box(6.85, .7, 5.7, f'''<p class="k" style="color:rgba(255,255,255,.85)">De dónde viene todo</p>
  <h2 class="t" style="color:#fff">Todo esto <em style="color:{TI}">ya</em> era suyo</h2>
  <div class="bigs">{big(N_POSTS, "publicaciones de Instagram, leídas una por una")}{big(N_REV, f"reseñas de Google, nota {NOTA}, en su idioma original")}{big(7, "afiches de tours: títulos, paradas, letra y rojo")}{big(N_PROPIAS, f"fotos suyas, de {N_POSTS_FOTOS} posts distintos")}</div>
  <p class="p" style="color:#fff">Cada texto de la marca tiene su origen identificado. Lo que no estaba publicado (la mayoría de los precios, pagos, políticas) dice <b>«por confirmar con la agencia»</b>.</p>'''),
  nc='rgba(255,255,255,.7)'))

# 04 · LA MARCA · niebla, franjas de color verticales
stripes = [('niebla', 'Niebla de Castro', TI), ('bruma', 'Bruma', TI), ('tierra', 'Tierra chilota', TI), ('musgo', 'Musgo', NI),
           ('tinta', 'Tinta de alerce', NI), ('isla', 'Isla Grande', '#fff'), ('mar', 'Mar del logo', '#fff'),
           ('chiloe', 'Verde Chiloé', '#fff'), ('turismo', 'Rojo Turismo', '#fff')]
sth = ''.join(f'<div class="stripe" style="background:{C[k]};color:{fg}"><span class="sn">{nm}</span><span class="sh">{C[k]}</span></div>' for k, nm, fg in stripes)
L.append(lam(NI, f'<div class="stripes">{sth}</div>' +
  f'<img class="abs" src="{png_file("brand/logo/logo-color.png", 600)}" style="left:.55in;top:.5in;width:1.7in" alt="">' +
  box(.55, 1.75, 6.6, f'''<p class="k" style="color:{ISLA}">La marca · letra y color</p>
  <p class="spa">TOUR LA COSTA</p><p class="spb">con</p><p class="spa">CURANTO EN HOYO</p>
  <p class="cap2">Anton para títulos, como sus afiches · Montserrat para todo lo demás</p>''') +
  box(.55, 5.3, 6.6, f'''<div class="cols3">
  <div><h4 style="color:{ROJOH}">Letra</h4><p>La letra pesada y angosta de sus afiches, en mayúsculas, y la palabra suelta que une dos líneas («con»).</p></div>
  <div><h4 style="color:{ISLA}">Color</h4><p>El fondo y el oscuro salen del cielo nublado y del bosque de sus fotos; los acentos, de su logo, tal cual.</p></div>
  <div><h4 style="color:{ROJOH}">Rojo = reservar</h4><p>El rojo de «TURISMO» solo va en lo que lleva a reservar: así el ojo aprende dónde se actúa.</p></div></div>''')))

# 05 · RECORRIDO · isla, 4 actos con medallones
actos = [('d-hero', 'Llegar', 'El columpio de Huillinco y la navegación en Puñihuil, dentro de la isla del logo.', -3),
         ('d-tours', 'Elegir', 'Los 8 tours como sus afiches, cada uno con su ficha.', 2),
         ('d-reviews', 'Confiar', f'{N_REV} reseñas, el equipo con sus nombres y más de 20 años.', -2),
         ('d-bcta', 'Reservar', 'Su remate de siempre y WhatsApp a un toque, en cada página.', 3)]
ah = ''
for i, (s_, t_, p_, r_) in enumerate(actos):
    x = .5 + i * 3.1
    ah += fr(s_, x, 3.2, 2.85, r_) + medal(x + 2.15, 2.75, .95, NI, ISLA, f'<b class="mdn">{i + 1}</b>', rot=-r_ * 2, z=5)
    ah += box(x, 5.45, 2.8, f'<h3 class="t3" style="color:#fff">{t_}</h3><p class="p" style="color:rgba(255,255,255,.88)">{p_}</p>')
L.append(lam(ISLA, wave('rgba(255,255,255,.08)', 1.4) +
  box(.5, .6, 9, f'''<p class="k" style="color:rgba(255,255,255,.8)">El recorrido</p>
  <h2 class="t" style="color:#fff">Un día de tour, <em style="color:{NI}">en</em> cuatro actos</h2>''') + ah,
  nc='rgba(255,255,255,.7)'))

# 06 · PORTADA DEL SITIO · azul hondo, navegador + celular
L.append(lam(MARH, gull(.55, 6.6, .7, 'rgba(255,255,255,.35)', 12) +
  box(.55, .7, 3.95, f'''<p class="k" style="color:rgba(255,255,255,.8)">La portada</p>
  <h2 class="t" style="color:#fff">Nuestro archipiélago <em style="color:{TE}">es</em> mágico</h2>
  <p class="p" style="color:rgba(255,255,255,.9)">La frase de su bio sobre su foto del lago, y dos caminos: ver los tours o escribir por WhatsApp. Al pie, cuatro datos que un viajero quiere saber antes de comparar agencias.</p>''') +
  box(.55, 5.0, 3.75, Q('El transporte es en vehículos pequeños pero cómodos, lo cual hace que la experiencia sea muy personalizada.', 'Gabriela · Google'), 'card', f'background:{NI};') +
  fr('d-hero', 5.3, .65, 7.25, 1.5) + ph('m-hero', 4.65, 3.75, 1.65, -5) +
  box(6.75, 5.5, 5.8, f'<div class="pills">{pill(f"{NOTA} ★ · {N_REV} reseñas", ROJO)}{pill("Lu a Do", NI, TI)}{pill("16 por van", ISLA)}{pill("10:00 · Plaza de Armas", NI, TI)}</div>'),
  nc='rgba(255,255,255,.7)'))

# 07 · VAMOS A NAVEGAR · captura a sangre, tarjeta flotante
L.append(f'<article class="lam free" style="background:{TI}"><img class="bleed abs0" src="{shot("d-isla-b", 2400)}" style="object-position:50% 70%" alt="">' +
  box(7.55, 1.15, 5.0, f'''<p class="k" style="color:{ISLA}">Vamos a navegar</p>
  <h2 class="t" style="color:{TI}">La isla <em style="color:{ROJO}">de su logo,</em> hecha ventana</h2>
  <p class="p">Al bajar por la página, la silueta de Chiloé crece hasta que el video de Puñihuil llena la pantalla. Es el único momento «de efecto» del sitio.</p>
  {Q("La experiencia de ver los pingüinos que ofrece la caleta Puñihuil es de otro nivel", IG("057"))}''', 'card', f'background:{NI};') +
  fr('d-isla-a', 9.3, 5.25, 3.2, 4) + medal(8.55, 4.95, 1.05, ROJO, '#fff', 'Así<br>empieza', rot=-12, fs=10, z=6) +
  f'<span class="no" style="color:rgba(255,255,255,.7)">{nx():02d}</span></article>')

# 08 · ELIGE TU TOUR · niebla con banda roja y afiches en abanico
fan = [('curanto-destape', 8.45, 1.75, -7, 'Con curanto en hoyo'), ('brujos-columpio-2', 9.85, 1.6, 2, 'Con asado al palo'), ('almas-pareja', 11.2, 1.8, 8, 'Mitos y acantilados')]
fanh = ''.join(f'<div class="card-t" style="left:{x}in;top:{y}in;transform:rotate({r}deg)"><img src="{src(k, 420)}" alt=""><span>{t}</span></div>' for k, x, y, r, t in fan)
L.append(lam(NI, f'<div class="band" style="background:{ROJOH}"></div>' + gull(11.75, .2, .75, '#fff', -6) +
  box(.55, .3, 11, f'<p class="k" style="color:rgba(255,255,255,.85)">Elige tu tour</p><h2 class="t tline" style="color:#fff">Los 8 tours, <em style="color:{TI}">como</em> sus afiches</h2>') +
  fr('d-tours', .55, 1.75, 7.3, -1) + ph('m-tours', 6.75, 4.55, 1.45, 5) + fanh +
  box(8.45, 4.75, 4.1, f'''<p class="p">Se deslizan con el dedo, como si estuvieran colgados en la vitrina de la agencia. Bajo cada nombre, una frase suya: «UN CURANTITO?».</p>
  <p class="p"><b style="color:{ROJOH}">{N_COMIDA} de las {N_REV} reseñas</b> hablan de la comida. Por eso cada tour se presenta primero por lo que se come o se vive.</p>''')))

# 09 · FICHA DE TOUR · verde, título de afiche, paradas en círculos
paradas = ['Feria Artesanal Dalcahue', 'Iglesia Patrimonio Tenaún', 'Almuerzo en agroturismo', 'Cascadas de Tocoihue', 'Isla Aucar']
parh = ''.join(medal(.55 + i * 1.18, 3.55, 1.08, NI if i % 2 == 0 else '#fff', VER, f'<span class="mds">{E(p_)}</span>', rot=(-6, 5, -3, 7, -5)[i], fs=7.4) for i, p_ in enumerate(paradas))
L.append(lam(VER,
  box(.55, .55, 6.2, f'''<p class="k" style="color:rgba(255,255,255,.85)">Ficha de tour · como su afiche</p>
  <p class="spa" style="color:#fff">TOUR LA COSTA</p><p class="spb" style="color:{NI}">con</p><p class="spa" style="color:#fff">CURANTO EN HOYO</p>''') + parh +
  box(.55, 4.95, 2.95, f'<p class="pr">$35.000</p><p class="p">por persona, con almuerzo, + $3.000 a las cascadas. Su post del 7 feb 2025: conviene confirmar si sigue vigente.</p>', 'card', f'background:{NI};') +
  box(3.75, 4.95, 2.85, Q('El tour fue preciso, teníamos tiempo para recorrer libremente…', 'Ximena · Google', cls='light') + '<p class="p" style="color:rgba(255,255,255,.9)">Por eso las paradas y el horario van primero, y el formulario termina en su WhatsApp.</p>') +
  fr('d-ficha', 6.95, .6, 5.6, 2.5) + fr('d-ficha-info', 6.7, 4.3, 5.6, -2) +
  medal(11.7, 3.65, 1.0, ROJO, '#fff', 'Cotizar<br><small>por WhatsApp</small>', rot=10, fs=10, z=6),
  nc='rgba(255,255,255,.7)'))

# 10 · LAS PERSONAS · tinta, comillas gigantes, nombres en cápsulas
names = [('Nicolás', MAR), ('Alberto', ISLA), ('Meli', ROJO), ('Sandra', VER), ('Rodolfo', TE), ('don Enrique', MAR), ('Marcelo', ISLA), ('Marco', ROJO)]
L.append(lam(TI, '<p class="qq" style="left:.4in;top:.15in">“</p>' +
  box(.6, 1.45, 5.9, f'''<p class="qbig">Alberto, el guía lo da todo, explica y atiende cada pregunta, está atento a todo.</p>
  <p class="k" style="color:rgba(255,255,255,.6);margin-top:.12in">Andrea · Google</p>''') +
  box(.6, 3.55, 5.9, f'''<div class="stats"><div><b style="color:{ROJO}">{N_GUIA}</b><span>de {N_REV} reseñas hablan del guía</span></div><div><b style="color:{MAR}">{N_NOMBRE}</b><span>nombran a alguien del equipo</span></div></div>
  <div class="pills" style="margin-top:.2in">{"".join(pill(n_, c_) for n_, c_ in names)}</div>
  <p class="p" style="color:rgba(255,255,255,.75);margin-top:.18in">Paisajes muestran todas las agencias; lo que distingue a Chiloé Mágico son las personas. Por eso las reseñas elegidas dicen nombres, y «Nosotros» muestra caras. Las {N2} reseñas de dos estrellas se leyeron, pero no se publican.</p>''') +
  fr('d-reviews', 7.0, .6, 5.55, -2.5) + fr('d-nosotros2', 6.75, 4.25, 5.55, 2),
  nc='rgba(255,255,255,.6)'))

# 11 · OTRAS FORMAS DE BUSCAR · bruma, tres capturas con medallones
trio = [('d-destinos', 'Por<br>lugar', MAR, -2.5), ('d-experiencias', 'Por<br>experiencia', VER, 1.5), ('d-guia', 'Por<br>historia', ROJO, -1.5)]
th_ = ''.join(fr(s_, .55 + i * 4.1, 2.15, 3.85, r_) + medal(.2 + i * 4.1 + 3.4, 1.65, 1.15, c_, '#fff', t_, rot=(-10, 8, -6)[i], fs=12, z=5) for i, (s_, t_, c_, r_) in enumerate(trio))
L.append(lam(BR, gull(11.7, .45, .7, MARH, -10, True) +
  box(.55, .55, 9, f'<p class="k" style="color:{ISLA}">Otras formas de buscar</p><h2 class="t" style="color:{TI}">Por dónde, <em style="color:{ROJO}">qué y</em> por qué</h2>') + th_ +
  box(.55, 5.15, 3.85, Q('En el mapudungun de Chiloé Dalkawe significa lugar de dalcas…', IG('087')) + '<p class="p">Cinco destinos, cada uno explicado con sus posts.</p>') +
  box(4.65, 5.15, 3.85, Q('I enjoyed the myths of brujería and the taste of chiloe with Nicolas.', 'elia · Google', 'en') + '<p class="p">Mitos y comida, al mismo nivel que el patrimonio.</p>') +
  box(8.75, 5.15, 3.8, f'<p class="p">Sus posts explicativos (el curanto, las iglesias, los brujos) se pierden en Instagram con el tiempo; reunidos en una guía, ayudan a que los encuentren en Google.</p><p class="p"><b>Paquetes</b> y <b>servicios privados</b> tienen su página, con lo no publicado «por confirmar».</p>')))

# 12 · RESERVAR · rojo, el remate gigante
L.append(lam(ROJO, wave(ROJOH, 1.3) + gull(5.2, 4.15, .85, '#fff', -12) +
  box(.55, .55, 6.7, f'''<p class="k" style="color:rgba(255,255,255,.85)">Reservar · el final de cada página</p>
  <p class="remate">¡NO DEJES QUE TE LO CUENTEN, VEN A DISFRUTAR DE ESTA MÁGICA ISLA JUNTO A NOSOTROS!</p>
  <p class="k" style="color:rgba(255,255,255,.75)">{IG("007")} · su remate de siempre</p>''') +
  box(.55, 5.35, 6.2, f'''<p class="p">Su bio dice «Escríbenos» con el enlace de WhatsApp: ese es su canal real. El contacto y las 14 preguntas frecuentes terminan ahí, con fecha y personas ya escritas. Antes de reservar se aclara que el guiado es en español.</p>
  <p class="p sm">En la bio y en el portal municipal aparecen dos números distintos; ambos están en el sitio hasta que confirmen cuál usar.</p>''', 'card', f'background:{NI};') +
  fr('d-contacto2', 7.25, .65, 5.3, 3) + fr('d-faq', 7.6, 4.2, 4.95, -2.5) + ph('m-contacto', 6.85, 3.3, 1.35, -6),
  nc='rgba(255,255,255,.7)'))

# 13 · DETALLES · niebla, cinco celulares
phs = ''.join(ph(k, .65 + i * 2.45, .5 + (0, .3, 0, .3, 0)[i], 2.05, (-4, 3, -2, 4, -3)[i]) for i, k in enumerate(['m-hero', 'm-tours', 'm-ficha-info', 'm-nosotros', 'm-contacto']))
dots = ''.join(f'<div class="dot" style="left:{.45 + i * 2.45}in;top:{1.4 + (0, .3, 0, .3, 0)[i]}in;background:{c_}"></div>' for i, c_ in enumerate([MAR, VER, ROJO, ISLA, TE]))
det = [('Celular primero', 'Una columna, botones grandes y WhatsApp a un toque. Las fotos se aligeraron para funcionar con poca señal en ruta.', MAR),
       ('Español e inglés', 'Un botón ES · EN traduce lo que guía la visita; sus textos y las reseñas quedan en su idioma original.', VER),
       ('Menú con fotos', 'Cuatro capítulos grandes; al pasar sobre cada uno aparece una foto suya de ese tema.', ROJO),
       ('Sin tropiezos', 'La página no salta mientras carga y cada foto tiene su descripción en español e inglés.', ISLA)]
deth = ''.join(box(.55 + i * 3.1, 5.75, 2.85, f'<div class="bar" style="background:{c_}"></div><h3 class="t4">{t_}</h3><p class="p">{p_}</p>') for i, (t_, p_, c_) in enumerate(det))
L.append(lam(NI, dots + phs + deth))

# 14 · CIERRE · foto a sangre y tarjeta
L.append(f'<article class="lam free" style="background:{TI}"><img class="bleed abs0" src="{raw("tenaun", 2600)}" style="object-position:50% 40%" alt="">' +
  box(6.75, .5, 5.75, f'''{MARK}
  <p class="k" style="color:{ISLA}">Lo que sigue</p><h2 class="t" style="color:{TI}">Hacerlo <em style="color:{ROJO}">suyo</em></h2>
  <p class="p">Este sitio se hizo solo con lo que ya estaba publicado. Con un par de conversaciones podría ir mucho más lejos:</p>
  <ul class="next2"><li>Fotografía y video propios de cada tour, del equipo y de las vans</li>
    <li>Precios, temporadas y políticas confirmados por ustedes</li>
    <li>Dominio propio .cl y alojamiento a nombre de Chiloé Mágico</li>
    <li>Reservas que lleguen a su WhatsApp ordenadas por fecha, tour y cupos</li></ul>
  <p class="invite2">Cuando quieran, lo conversamos.</p>
  <p class="who2">Pablo Figueroa G.</p><p class="role2">Director de estudio</p>
  <p class="contact2"><a href="mailto:pablo@bergerac.cl">pablo@bergerac.cl</a> · <a href="tel:+56975892096">+56 9 7589 2096</a></p>
  <p class="link2"><a href="https://bergerac.cl">Bergerac.cl</a></p>''', 'card', f'background:{NI};padding:.45in .5in;') +
  f'<span class="no" style="color:rgba(255,255,255,.7)">{nx():02d}</span></article>')

# ======================= CSS =======================
CSS = f'''
@font-face{{font-family:"Anton";src:url({font("anton-latin-400-normal")}) format("woff2")}}
@font-face{{font-family:"Montserrat";font-weight:400;src:url({font("montserrat-latin-400-normal")}) format("woff2")}}
@font-face{{font-family:"Montserrat";font-weight:400;font-style:italic;src:url({font("montserrat-latin-400-italic")}) format("woff2")}}
@font-face{{font-family:"Montserrat";font-weight:500;src:url({font("montserrat-latin-500-normal")}) format("woff2")}}
@font-face{{font-family:"Montserrat";font-weight:600;src:url({font("montserrat-latin-600-normal")}) format("woff2")}}
@font-face{{font-family:"Montserrat";font-weight:700;src:url({font("montserrat-latin-700-normal")}) format("woff2")}}
@page{{size:13in 8.5in;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#8b8f8a}}
body{{font-family:"Montserrat",Arial,sans-serif;color:{TI};-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.lam{{width:13in;height:8.5in;overflow:hidden;margin:0 auto .3in;position:relative;page-break-after:always;break-after:page}}
@media print{{html,body{{background:none}}.lam{{margin:0}}}}
.bleed{{width:100%;height:100%;object-fit:cover;display:block}}
.abs0{{position:absolute;inset:0}}
.abs{{position:absolute;display:block}}
.spread .bleed{{position:absolute;inset:0}}
.spread-tab{{position:absolute;left:0;top:.45in;background:#fff;opacity:.75;padding:.17in .32in .17in .5in;border-radius:0 .18in .18in 0}}
.spread-logo{{width:1.9in;display:block}}
.no{{position:absolute;right:.4in;bottom:.28in;font-weight:600;font-size:7pt;letter-spacing:.2em;z-index:20}}
.tx{{position:absolute;z-index:4}}
.card{{border-radius:.22in;padding:.3in .34in;box-shadow:0 10pt 30pt rgba(0,0,0,.18)}}
.k{{font-weight:600;font-size:7.4pt;letter-spacing:.24em;text-transform:uppercase;margin-bottom:.1in}}
.t{{font-family:"Anton";font-weight:400;font-size:36pt;line-height:1;text-transform:uppercase;margin-bottom:.18in}}
.t em{{font-style:normal}}
.tline{{font-size:34pt;white-space:nowrap}}
.t3{{font-family:"Anton";font-weight:400;font-size:24pt;text-transform:uppercase;margin-bottom:.06in}}
.t4{{font-family:"Anton";font-weight:400;font-size:17pt;text-transform:uppercase;margin:.1in 0 .05in}}
.p{{font-size:9.6pt;line-height:1.5;margin-bottom:.08in}}
.p.sm{{font-size:7.6pt;color:{MU}}}
.q2{{margin:.04in 0 .1in}}
.q2 p{{font-style:italic;font-size:10.4pt;line-height:1.42;margin-bottom:3pt}}
.q2 cite{{font-style:normal;font-weight:600;font-size:6.4pt;letter-spacing:.16em;text-transform:uppercase;color:{MU}}}
.q2.light p{{color:#fff}}.q2.light cite{{color:rgba(255,255,255,.75)}}
.letter2 p{{font-size:10.2pt;line-height:1.58;margin-bottom:.1in}}
.sign2{{font-style:italic;color:{MU}}}
.wave{{position:absolute;left:0;width:100%;display:block;z-index:0}}
.gull{{position:absolute;z-index:3}}
.pic{{position:absolute;overflow:hidden;box-shadow:0 12pt 34pt rgba(0,0,0,.22)}}
.pic img{{width:100%;height:100%;object-fit:cover;display:block}}
.fr{{position:absolute;border-radius:8pt;overflow:hidden;box-shadow:0 14pt 34pt rgba(0,0,0,.3);background:#fff}}
.fr img{{width:100%;display:block}}
.ph{{position:absolute;border-radius:16pt;overflow:hidden;border:4pt solid #111;box-shadow:0 14pt 30pt rgba(0,0,0,.32);background:#111}}
.ph img{{width:100%;display:block;border-radius:12pt}}
.md{{position:absolute;border-radius:50%;display:flex;align-items:center;justify-content:center;text-align:center;font-family:"Anton";text-transform:uppercase;line-height:1.02;padding:.1in;box-shadow:0 8pt 20pt rgba(0,0,0,.22)}}
.md small{{font-size:.7em}}
.mdn{{font-size:30pt;font-weight:400}}
.mds{{font-family:"Montserrat";font-weight:700;text-transform:uppercase;letter-spacing:.04em;line-height:1.25}}
.pol{{position:absolute;width:1.85in;background:#fff;padding:.08in .08in .3in;box-shadow:0 10pt 24pt rgba(0,0,0,.3)}}
.pol img{{width:100%;aspect-ratio:1;object-fit:cover;display:block}}
.bigs{{display:grid;grid-template-columns:1fr 1fr;gap:.12in .3in;margin:.06in 0 .22in}}
.bign b{{display:block;font-family:"Anton";font-weight:400;font-size:52pt;line-height:1;color:{NI}}}
.bign span{{display:block;font-size:8.6pt;line-height:1.35;color:#fff;margin-top:.02in}}
.stripes{{position:absolute;right:0;top:0;bottom:0;width:5.3in;display:flex}}
.stripe{{flex:1;position:relative}}
.stripe .sn{{position:absolute;left:50%;top:.55in;transform:translateX(-50%) rotate(180deg);writing-mode:vertical-rl;font-weight:700;font-size:8pt;letter-spacing:.2em;text-transform:uppercase;white-space:nowrap}}
.stripe .sh{{position:absolute;left:0;right:0;bottom:.55in;text-align:center;font-weight:600;font-size:6.2pt;letter-spacing:.06em;writing-mode:vertical-rl;transform:rotate(180deg);margin:0 auto;width:100%;display:flex;align-items:center}}
.spa{{font-family:"Anton";font-size:58pt;line-height:.98;text-transform:uppercase;color:{TI}}}
.spb{{font-family:"Anton";font-size:30pt;line-height:1;text-transform:uppercase;color:{ROJO};margin:.02in 0}}
.cap2{{font-weight:600;font-size:7pt;letter-spacing:.18em;text-transform:uppercase;color:{MU};margin-top:.16in}}
.cols3{{display:grid;grid-template-columns:repeat(3,1fr);gap:.28in}}
.cols3 h4{{font-family:"Anton";font-weight:400;font-size:16pt;text-transform:uppercase;margin-bottom:.06in}}
.cols3 p{{font-size:9.2pt;line-height:1.5}}
.pills{{display:flex;flex-wrap:wrap;gap:6pt}}
.pill{{display:inline-block;padding:5pt 11pt;border-radius:999px;font-weight:600;font-size:8.4pt}}
.band{{position:absolute;left:0;right:0;top:0;height:1.35in}}
.card-t{{position:absolute;width:1.4in;background:#fff;padding:.07in .07in .1in;border-radius:6pt;box-shadow:0 10pt 24pt rgba(0,0,0,.22)}}
.card-t img{{width:100%;height:1.75in;object-fit:cover;display:block;border-radius:3pt}}
.card-t span{{display:block;font-weight:700;font-size:6.6pt;letter-spacing:.12em;text-transform:uppercase;color:{ISLA};margin-top:.06in}}
.pr{{font-family:"Anton";font-size:38pt;line-height:1;color:{VER};margin-bottom:.04in}}
.qq{{position:absolute;font-family:"Anton";font-size:180pt;line-height:1;color:{ROJO};z-index:1}}
.qbig{{font-style:italic;font-size:21pt;line-height:1.32;color:{NI}}}
.stats{{display:flex;gap:.45in}}
.stats b{{display:block;font-family:"Anton";font-weight:400;font-size:60pt;line-height:1}}
.stats span{{display:block;font-size:9pt;color:rgba(255,255,255,.85);max-width:1.8in}}
.remate{{font-family:"Anton";font-size:40pt;line-height:1.02;color:#fff;margin:.04in 0 .16in}}
.dot{{position:absolute;width:2.6in;height:2.6in;border-radius:50%;opacity:.9;z-index:1}}
.bar{{width:.6in;height:4pt;border-radius:2pt}}
.mk{{width:.55in;display:block;margin-bottom:.12in}}
.next2{{list-style:none;margin:.04in 0 .18in}}
.next2 li{{font-size:9.6pt;line-height:1.45;padding:5pt 0;border-bottom:.5pt solid #cfd3cf}}
.invite2{{font-size:13pt;font-style:italic;margin-bottom:.06in}}
.who2{{font-family:"Anton";font-size:11pt;letter-spacing:.14em;text-transform:uppercase}}
.role2{{font-size:9pt}}
.contact2{{font-size:8.2pt;color:{MU}}}
.card a{{color:inherit;text-decoration:none}}
.link2{{font-family:"Anton";font-size:16pt;letter-spacing:.16em;text-transform:uppercase;color:{ROJO};margin-top:.1in}}
'''

DOC = f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chiloé Mágico · Decisiones de diseño del sitio web</title><style>{CSS}</style></head>
<body>{''.join(L)}</body></html>'''
(D / 'chiloemagico-dossier-diseno.html').write_text(DOC, encoding='utf-8')
print('láminas', n, 'MB', round(len(DOC) / 1e6, 1))
