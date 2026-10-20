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

# ======================= 01 PORTADA (doble página) =======================
nx()
L.append(f'''<article class="lam spread">
  <img class="bleed" src="{raw("huillinco-columpio", 2600)}" style="object-position:50% 62%" alt="">
  <div class="spread-tab"><img class="spread-logo" src="{png_file("brand/logo/logo-color.png", 900)}" alt="Turismo Chiloé Mágico"></div>
</article>''')

# ======================= 02 CARTA =======================
L.append(lamina_libre(nx(),
  f'<img class="bleed" src="{raw("nicolas-enrique")}" style="object-position:50% 40%" alt="">',
  f'''<p class="kick">Antes de empezar</p><h2>Un sitio hecho con lo que ustedes ya dijeron</h2>
  <div class="letter">
  <p>Equipo de Chiloé Mágico:</p>
  <p>Este sitio nació de mirar con atención lo que Chiloé Mágico ya publica. No hay frases inventadas ni promesas de agencia: cada título sale de sus posts de Instagram, de sus destacadas, de sus afiches de tours, de su bio o de lo que sus viajeros escribieron en Google. Lo que hicimos fue ordenarlo, darle aire y ponerlo en movimiento.</p>
  <p>Tampoco hay fotos de banco de imágenes. De las {N_FOTOS} fotos del sitio, {N_PROPIAS} y los 3 videos son suyos; la única excepción es una foto de libre uso del volcán Osorno, con su autor citado.</p>
  <p>En las próximas láminas, a la izquierda está el sitio tal como se ve; a la derecha, de dónde salió cada cosa y por qué está ahí.</p>
  <p>Es un regalo. Ojalá lo disfruten tanto como nosotros disfrutamos haciéndolo.</p>
  <p class="sign">Pablo Figueroa G.<br>Director de estudio</p></div>''', 'full'))

# ======================= 03 DE DÓNDE VIENE TODO =======================
grid_keys = ['huillinco-columpio', 'curanto-destape', 'brujos-columpio-2', 'almas-pareja', 'muelle-luz-mirador',
             'caleuche', 'punihuil-bahia', 'pasarela-aucar', 'tenaun', 'palafitos',
             'nicolas-enrique', 'vans', 'yayanes-puente', 'curaco-2', 'mechuque']
igrid = ''.join(f'<img src="{src(k, 300)}" alt="">' for k in grid_keys)
L.append(lamina_libre(nx(),
  f'''<p class="lab">15 de las {N_PROPIAS} fotos elegidas de su Instagram</p><div class="igrid">{igrid}</div>
  <div class="voice" style="margin-top:.16in">
    <p class="vbig vsm">¡NO DEJES QUE TE LO CUENTEN, VEN A DISFRUTAR DE ESTA MÁGICA ISLA JUNTO A NOSOTROS!</p>
    <p class="vsrc">{IG("007")} · su remate de siempre, y el cierre del sitio</p></div>''',
  f'''<p class="kick">De dónde viene todo</p><h2>Todo esto ya era suyo</h2>
  <p class="lead">Antes de diseñar, leímos todo lo que Chiloé Mágico tiene publicado.</p>
  <div class="grid">
  {block("Lo que leímos", f"<p><b>{N_POSTS} publicaciones</b> de Instagram ({N_PROPIOS} suyas), <b>7 destacadas</b>, la bio y los <b>7 afiches de tours</b>. De los afiches salen los títulos, las paradas, la letra y el rojo.</p>")}
  {block("Lo que dicen sus viajeros", f"<p><b>{N_REV} reseñas</b> de Google con nota <b>{NOTA}</b>, leídas todas en su idioma original para saber qué valoran y qué les falta.</p>")}
  {block("Su voz", "<p>Tutea, se entusiasma y usa la mitología como invitación: «UN CURANTITO?», «VAMOS A VOLAR UN RATITO?». En el sitio se quitaron los emojis; las preguntas y las mayúsculas se dejaron tal cual.</p>")}
  {block("La regla", "<p>Cada texto de la marca tiene su origen identificado. Si un dato no estaba publicado (la mayoría de los precios, pagos, políticas), el sitio dice <b>«por confirmar con la agencia»</b>.</p>")}
  </div>'''))

# ======================= 04 LA MARCA =======================
sw = [('niebla', 'Niebla de Castro', '#1d2421'), ('bruma', 'Bruma', '#1d2421'), ('tierra', 'Tierra chilota', '#1d2421'),
      ('tinta', 'Tinta de alerce', '#f2f1ec'), ('musgo', 'Musgo', '#f2f1ec'), ('isla', 'Isla Grande', '#f2f1ec'),
      ('mar', 'Mar del logo', '#fff'), ('chiloe', 'Verde Chiloé', '#fff'), ('turismo', 'Rojo Turismo', '#fff')]
swh = ''.join(f'<span style="background:{C[k]};color:{fg}">{nm}<br>{C[k]}</span>' for k, nm, fg in sw)
L.append(lamina_libre(nx(),
  f'''<div class="spec">
    <img class="spec-logo" src="{png_file("brand/logo/logo-color.png", 600)}" alt="">
    <p class="sp0">Tours de día completo desde Castro</p>
    <p class="sp1">TOUR LA COSTA</p><p class="sp1s">con</p><p class="sp1">CURANTO EN HOYO</p>
    <p class="sp2">Todos nuestros tours incluyen traslado, guiado, almuerzo y bebestibles, y visitas a distintos atractivos turísticos</p>
    <p class="cap">Anton · títulos — Montserrat · textos, rótulos y botones</p></div>
  <div class="swatches">{swh}</div>''',
  f'''<p class="kick">La marca</p><h2>La letra de sus afiches y los colores de su logo</h2>
  <p class="lead">Ustedes no tenían sitio, pero sí una gramática clara en sus afiches y en su logo. La buscamos ahí.</p>
  <div class="grid">
  {block("Letra", "<p>Los títulos de sus afiches van en una letra de palo pesada y angosta, en mayúsculas; <b>Anton</b> es su equivalente libre. Para todo lo demás, <b>Montserrat</b>, la letra redonda de su pieza «Visita CHILOÉ». La palabra suelta que une dos líneas en sus afiches («con») se mantiene, en Montserrat gruesa.</p>")}
  {block("Color", "<p>Medimos los tonos que más se repiten en sus fotos: los cielos nublados dan el fondo (<b>Niebla de Castro</b>) y el bosque y la madera, el oscuro (<b>Tinta de alerce</b>). Los acentos son los colores de su logo, tal cual.</p>")}
  {block("Rojo = reservar", "<p>El <b>rojo de «TURISMO»</b>, que es también la banda de sus afiches, se usa solo en lo que lleva a reservar: «Reservar», «Cotizar por WhatsApp» y el pie. Todo se lee con holgura, incluso con sol sobre la pantalla del celular.</p>" + P("turismoh"))}
  {block("Logo", "<p>El logo de su foto de perfil se redibujó sobre el original, sin cambiar nada, para que sea nítido a cualquier tamaño: a color, en blanco, en versión adhesivo para fotos y horizontal para la barra de arriba. La isla del logo reaparece como ventana en la portada.</p>")}
  </div>'''))

# ======================= 05 RECORRIDO =======================
strip = [('d-hero', 'Portada'), ('d-isla-b', 'Vamos a navegar'), ('d-tours', 'Elige tu tour'),
         ('d-ficha', 'Ficha de tour'), ('d-reviews', 'Reseñas'), ('d-nosotros', 'Nosotros'),
         ('d-destinos', 'Destinos'), ('d-bcta', 'Cierre'), ('d-contacto', 'Contacto')]
sh = ''.join(f'<figure><img src="{shot(k, 640)}" alt=""><figcaption>{c}</figcaption></figure>' for k, c in strip)
L.append(lamina_libre(nx(), f'<p class="lab">El recorrido</p><div class="strip">{sh}</div>',
  f'''<p class="kick">Recorrido</p><h2>Un día de tour, en cuatro actos</h2>
  <p class="lead">El sitio se recorre como una excursión: llegar, elegir, confiar y reservar.</p>
  <div class="grid">
  {block("1 · Llegar", "<p>El columpio del lago Huillinco con la frase de su bio. Enseguida, la navegación en Puñihuil dentro de la silueta de la isla.</p>")}
  {block("2 · Elegir", "<p>Los 8 tours como sus afiches, cada uno con su ficha. Destinos y experiencias ofrecen otras dos formas de buscar.</p>")}
  {block("3 · Confiar", f"<p>{N_REV} reseñas con nota {NOTA}, el equipo con sus nombres, las vans y los más de 20 años de servicio.</p>")}
  {block("4 · Reservar", "<p>Su remate «¡NO DEJES QUE TE LO CUENTEN…!» y WhatsApp siempre a un toque, en cada página.</p>")}
  </div>'''))

# ======================= SECCIONES =======================
S('Portada', 'Nuestro archipiélago es mágico',
  'Una foto suya a pantalla completa, su logo, la frase de su bio y dos caminos: ver los tours o escribir por WhatsApp.',
  'd-hero', 'm-hero', [
    block('Textos', quote('Nuestro archipiélago es mágico ¡Ven a descubrirlo!', 'Bio de Instagram') + quote('¡Tours todos los días! - Servicios privados', 'Bio de Instagram')),
    block('Datos de confianza', f'<p>Al pie, cuatro datos verificables: <b>{NOTA} ★ en Google · {N_REV} reseñas</b>, tours de lunes a domingo, máximo 16 pasajeros por van y salida a las 10:00 frente a la Plaza de Armas.</p>'),
    block('Por qué así', '<p>Lo primero que hace un viajero es comparar agencias. La nota de Google y el tamaño de los grupos responden esa duda antes de bajar.</p>' + quote('El transporte es en vehículos pequeños pero cómodos, lo cual hace que la experiencia sea muy personalizada.', 'Gabriela · Google'), 'wide'),
  ])

S('Vamos a navegar', 'Vamos a navegar?',
  'La isla de su logo se vuelve una ventana: al bajar por la página, la silueta crece hasta que el video de Puñihuil ocupa toda la pantalla.',
  'd-isla-a', None, [
    block('Textos', quote('Vamos a navegar?', IG('015')) + f'<p>Video: un tramo de su publicación del {IGD["013"]}.</p>'),
    block('Movimiento', '<p>Es el único momento «de efecto» del sitio. Si alguien prefiere menos movimiento en su teléfono, la isla aparece ya abierta.</p>'),
    block('Por qué aquí', quote('La experiencia de ver los pingüinos que ofrece la caleta Puñihuil es de otro nivel', IG('057')) + '<p>Su logo ya es la isla. Antes de ver los tours, el viajero entra «dentro» de Chiloé por la ventana de su propia marca.</p>', 'wide'),
  ], nota='Arriba, la isla abriéndose; abajo, a pantalla completa.', desk2='d-isla-b')

S('Elige tu tour', 'Elige tu tour',
  'Los 8 tours uno al lado del otro, como sus afiches en la vitrina de la agencia. Se deslizan con el dedo o con las flechas; la página «Tours» los muestra todos en grilla.',
  'd-tours', 'm-tours', [
    block('Textos', quote('Todos nuestros tours incluyen traslado, guiado, almuerzo y bebestibles, y visitas a distintos atractivos turísticos', IG('007')) + '<p>Bajo cada nombre, una frase suya del post de ese tour: «UN CURANTITO?».</p>'),
    block('Imágenes', thumbs([('curanto-destape', 'Curanto · ' + ORIG('curanto-destape')), ('brujos-columpio-2', 'Muelle de los Brujos · ' + ORIG('brujos-columpio-2')), ('almas-pareja', 'Muelle de las Almas · ' + ORIG('almas-pareja'))])),
    block('Por qué así', f'<p>{N_COMIDA} de las {N_REV} reseñas hablan de la comida. Por eso el rótulo de cada tour nombra primero lo que se come o se vive («Con curanto en hoyo», «Con asado al palo»), antes que la lista de lugares.</p>', 'wide'),
  ], hl=('Elige tu tour',))

S('Ficha de tour', 'Tour La Costa con curanto en hoyo',
  'Cada tour tiene su página, armada como su afiche: el título, el plato estrella, las paradas, qué incluye, horario y precio, sus fotos y un formulario que termina en WhatsApp.',
  'd-ficha', None, [
    block('Textos', quote('TOUR LA COSTA con CURANTO EN HOYO', AFICHES) + quote('Feria Artesanal Dalcahue · Iglesia Patrimonio Tenaún · Almuerzo en agroturismo · Cascadas de Tocoihue · Isla Aucar', AFICHES + ' · paradas')),
    block('Datos', '<p><b>$35.000 por persona</b> (con almuerzo) + <b>$3.000</b> de entrada a las cascadas, según su post del 7 de febrero de 2025. Es el único tour con precio publicado; en los demás dice «por confirmar».</p><p class="small">Conviene confirmar si este valor sigue vigente.</p>'),
    block('Interacción', '<p>El formulario pide solo fecha y número de personas, y abre WhatsApp con el mensaje escrito. En celular, una barra con «Cotizar» se queda abajo durante la lectura.</p>'),
    block('Por qué así', quote('El tour fue preciso, teníamos tiempo para recorrer libremente y solo acordábamos la hora de reunión…', 'Ximena · Google') + '<p>Los viajeros valoran saber qué pasa en el día: por eso las paradas y el horario van primero.</p>'),
  ], desk2='d-ficha-info')

S('Reseñas', 'Las personas son la marca',
  f'Trece reseñas reales en su idioma original, y una página «Nosotros» con el equipo por su nombre, sus más de 20 años y sus propias palabras.',
  'd-reviews', None, [
    block('Textos', quote('Alberto, el guía lo da todo, explica y atiende cada pregunta, está atento a todo.', 'Andrea · Google') + quote('nuestro marketing y publicidad más grande son nuestros turistas que cuentan sus experiencias con nosotros', IG('002'))),
    block('El equipo', '<p>Guías: Nicolás, Alberto, Meli, Sandra y Rodolfo. Conductores: don Enrique, Marcelo y Marco. Cada nombre aparece en sus posts o en reseñas de Google.</p>'),
    block('Lo que se decidió no mostrar', f'<p>Las {N2} reseñas de dos estrellas se leyeron, pero no se publican. Una sí dejó una enseñanza: las preguntas frecuentes aclaran que el guiado es en español.</p>'),
    block('Por qué así', f'<p><b>{N_GUIA} de las {N_REV} reseñas</b> hablan del guía y <b>{N_NOMBRE}</b> nombran a alguien del equipo. Paisajes muestran todas las agencias; lo que distingue a Chiloé Mágico son las personas.</p>'),
  ], desk2='d-nosotros2', hl=('Reseñas', 'Nosotros'))

S('Destinos', 'Otras formas de buscar',
  'Por lugar (cinco zonas del archipiélago), por experiencia (patrimonio, naturaleza, navegación, gastronomía y mitos) y una guía con sus propias explicaciones.',
  'd-destinos', None, [
    block('Textos', quote('En el mapudungun de Chiloé Dalkawe significa lugar de dalcas…', IG('087')) + quote('Te estarás preguntando ¿que es el curanto?', IG('034'))),
    block('También', '<p><b>Paquetes:</b> Valdivia y Niebla, el volcán Osorno y Bariloche, sin fechas, con detalles «por confirmar». <b>Servicios privados:</b> sus vans y traslados, con su post entero, «wena onda» incluido.</p>'),
    block('Por qué así', quote('I enjoyed the myths of brujería and the taste of chiloe with Nicolas.', 'elia · Google', 'en') + '<p>Muchos llegan sabiendo a dónde quieren ir o qué quieren vivir, no qué tour tomar. Y sus posts explicativos, que en Instagram se pierden con el tiempo, aquí ayudan a que los encuentren en Google.</p>', 'wide'),
  ], desk2='d-experiencias', hl=('Destinos', 'Experiencias', 'Guía de Chiloé', 'Paquetes', 'Servicios privados'))

S('Contacto', '¡No dejes que te lo cuenten!',
  'El final de cada página es su remate de siempre y un solo botón. Las preguntas frecuentes y el contacto terminan, igual, en su WhatsApp.',
  'd-bcta', None, [
    block('Textos', quote('¡NO DEJES QUE TE LO CUENTEN, VEN A DISFRUTAR DE ESTA MÁGICA ISLA JUNTO A NOSOTROS!', IG('007')) + quote('FYI the tour is not available in english.', 'Maja · Google', 'en')),
    block('Preguntas frecuentes', '<p>14 dudas típicas respondidas con sus palabras. Las que no han respondido en público dicen «Por confirmar con la agencia». El idioma se aclara antes de reservar: tres reseñas en inglés lo mencionan.</p>'),
    block('Por qué así', '<p>Su bio dice «Escríbenos» con el enlace de WhatsApp: ese es su canal real. El sitio no crea uno nuevo; ordena la primera conversación para que llegue con fecha y número de personas.</p><p class="small">En la bio y en el portal municipal aparecen dos números distintos; ambos están en el sitio hasta que ustedes confirmen cuál usar.</p>', 'wide'),
  ], desk2='d-contacto2', hl=('Preguntas frecuentes', 'Contacto'))

# ======================= DETALLES =======================
mrow = ''.join(f'<img src="{shot(k, 360)}" alt="">' for k in ['m-hero', 'm-tours', 'm-ficha-info', 'm-nosotros', 'm-contacto'])
L.append(lamina_libre(nx(),
  f'''<p class="lab">Menú abierto</p><img class="desk" style="width:72%" src="{shot("d-menu", 1100)}" alt="">
  <p class="lab" style="margin-top:.08in">Celular</p><div class="mrow">{mrow}</div>''',
  f'''<p class="kick">Detalles en todo el sitio</p><h2>Lo que no se ve, pero se siente</h2>
  <p class="lead">Decisiones que acompañan toda la visita.</p>
  <div class="grid">
  {block("Menú", "<p>Cuatro capítulos grandes. Al pasar sobre cada uno aparece una foto suya de ese tema.</p>")}
  {block("Español e inglés", "<p>Un botón ES · EN traduce lo que guía la visita. Sus textos y las reseñas quedan en su idioma original, para no poner palabras en su boca.</p>")}
  {block("Pensado para celular", "<p>Una columna, botones grandes y WhatsApp a un toque. Las fotos se aligeraron y se descargan a medida que se baja, para que funcione con poca señal en ruta.</p>")}
  {block("Sin tropiezos", "<p>La página no salta mientras carga, se puede recorrer con el teclado y cada foto tiene su descripción en español e inglés.</p>")}
  </div>'''))

# ======================= CIERRE =======================
L.append(lamina_libre(nx(),
  f'<img class="bleed" src="{raw("tenaun")}" style="object-position:50% 40%" alt="">',
  f'''<div class="close">{MARK}
  <p class="kick">Lo que sigue</p><h2>Hacerlo suyo</h2>
  <p class="lead">Este sitio se hizo solo con lo que ya estaba publicado. Con un par de conversaciones podría ir mucho más lejos:</p>
  <ul class="next"><li>Fotografía y video propios de cada tour, del equipo y de las vans</li>
    <li>Precios, temporadas y políticas confirmados por ustedes, en vez de «por confirmar»</li>
    <li>Dominio propio .cl y alojamiento a nombre de Chiloé Mágico</li>
    <li>Reservas que lleguen a su WhatsApp ordenadas por fecha, tour y cupos</li></ul>
  <p class="invite">Cuando quieran, lo conversamos.</p>
  <p class="who">Pablo Figueroa G.</p>
  <p class="role">Director de estudio</p>
  <p class="contact"><a href="mailto:pablo@bergerac.cl">pablo@bergerac.cl</a> · <a href="tel:+56975892096">+56 9 7589 2096</a></p>
  <p class="link"><a href="https://bergerac.cl">Bergerac.cl</a></p>
  <p class="coords">{COORDS}</p></div>''', 'full'))

# ======================= CSS =======================
CSS = f'''
@font-face{{font-family:"Anton";src:url({font("anton-latin-400-normal")}) format("woff2")}}
@font-face{{font-family:"Montserrat";font-weight:400;src:url({font("montserrat-latin-400-normal")}) format("woff2")}}
@font-face{{font-family:"Montserrat";font-weight:400;font-style:italic;src:url({font("montserrat-latin-400-italic")}) format("woff2")}}
@font-face{{font-family:"Montserrat";font-weight:500;src:url({font("montserrat-latin-500-normal")}) format("woff2")}}
@font-face{{font-family:"Montserrat";font-weight:600;src:url({font("montserrat-latin-600-normal")}) format("woff2")}}
@font-face{{font-family:"Montserrat";font-weight:700;src:url({font("montserrat-latin-700-normal")}) format("woff2")}}
@page{{size:13in 8.5in;margin:0}}
:root{{--niebla:#f2f1ec;--bruma:#dfe4e6;--tinta:#1d2421;--musgo:#46473b;--tierra:#a69775;--isla:#0e766c;--rojo:#d0342c;--rojoh:#b02a23;--gris:#6b6f68}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:#8b8f8a}}
body{{font-family:"Montserrat",Arial,sans-serif;color:var(--tinta);-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.lam{{width:13in;height:8.5in;display:grid;grid-template-columns:6.5in 6.5in;overflow:hidden;margin:0 auto .3in;background:var(--niebla);page-break-after:always;break-after:page;position:relative}}
@media print{{html,body{{background:none}}.lam{{margin:0}}}}
.L{{background:var(--tinta);color:var(--niebla);padding:.42in .4in .38in;display:flex;flex-direction:column;gap:.1in;overflow:hidden}}
.L.full{{padding:0}}
.bleed{{width:100%;height:100%;object-fit:cover;display:block}}
.R{{position:relative;padding:.48in .52in .7in;display:flex;flex-direction:column;overflow:hidden}}
.lab{{font-weight:600;font-size:6.4pt;letter-spacing:.22em;text-transform:uppercase;opacity:.8}}
.desk,.desk2{{width:100%;display:block;outline:.5pt solid rgba(242,241,236,.22)}}
.L.two .desk,.L.two .desk2{{width:88%}}
.L.two .rec{{columns:4;font-size:5.4pt;line-height:1.7}}
.Lrow{{display:flex;gap:.22in;align-items:flex-start;margin-top:.04in;min-height:0;flex:1}}
.mobw{{display:flex;flex-direction:column;gap:.08in}}
.mob{{width:1.35in;display:block;outline:.5pt solid rgba(242,241,236,.22)}}
.Linfo{{flex:1;display:flex;flex-direction:column;gap:.08in}}
.rec{{list-style:none;columns:2;column-gap:.14in;font-weight:600;font-size:6pt;letter-spacing:.12em;text-transform:uppercase;line-height:1.85}}
.rec li{{opacity:.42;break-inside:avoid}}
.rec li.on{{opacity:1;color:#fff}}
.rec li.on::before{{content:"";display:inline-block;width:5pt;height:5pt;background:var(--rojo);margin-right:4pt;vertical-align:.5pt}}
.lnote{{font-size:7.4pt;font-style:italic;opacity:.75;line-height:1.4;margin-top:.02in}}
.kick{{font-weight:600;font-size:6.8pt;letter-spacing:.26em;text-transform:uppercase;color:var(--isla);margin-bottom:.1in}}
h2{{font-family:"Anton";font-weight:400;font-size:26pt;line-height:1.02;text-transform:uppercase;margin-bottom:.12in;color:var(--tinta);letter-spacing:.005em}}
.lead{{font-size:10.6pt;line-height:1.45;margin-bottom:.2in;max-width:5.4in;color:var(--musgo)}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:.18in .28in;align-content:start}}
.bk h4{{font-weight:600;font-size:6.6pt;letter-spacing:.2em;text-transform:uppercase;color:var(--rojoh);padding-bottom:4pt;border-bottom:.5pt solid #cfd3cf;margin-bottom:6pt}}
.bk p{{font-size:9pt;line-height:1.45;margin-bottom:5pt}}
.bk p.small{{font-size:7.2pt;color:var(--gris)}}
.bk.wide{{grid-column:1/-1}}
.q{{margin:0 0 6pt}}
.q p{{font-size:9.2pt;font-style:italic;line-height:1.38;margin-bottom:1.5pt}}
.q p::before{{content:"“"}}.q p::after{{content:"”"}}
.q cite{{display:block;font-style:normal;font-weight:600;font-size:5.9pt;letter-spacing:.14em;text-transform:uppercase;color:var(--gris)}}
.ths{{display:flex;gap:5pt;flex-wrap:wrap;margin-bottom:4pt}}
.th{{width:calc(33.3% - 4pt);min-width:.5in}}
.ths .th:only-child{{width:1.4in}}
.ths .th:first-child:nth-last-child(4),.ths .th:first-child:nth-last-child(4)~.th{{width:calc(25% - 4pt)}}
.th img{{width:100%;height:.9in;object-fit:cover;display:block}}
.th figcaption{{font-size:5.9pt;line-height:1.25;color:var(--gris);margin-top:2pt}}
.chips{{display:flex;flex-wrap:wrap;gap:4pt 8pt;margin-bottom:4pt}}
.chip{{display:inline-flex;align-items:center;gap:4pt;font-size:6.6pt}}
.chip i{{width:11pt;height:11pt;display:inline-block;outline:.5pt solid rgba(29,36,33,.3)}}
.chip b{{font-weight:600;letter-spacing:.06em;text-transform:uppercase;font-size:5.8pt}}
.pf{{position:absolute;left:.52in;right:.52in;bottom:.3in;display:flex;justify-content:space-between;font-weight:600;font-size:5.6pt;letter-spacing:.2em;text-transform:uppercase;color:var(--gris);border-top:.5pt solid #cfd3cf;padding-top:6pt}}
.mk{{width:.55in;display:block}}
/* portada */
.cover{{background:var(--niebla)}}
.cover-in{{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;height:100%;gap:.14in}}
.cover-logo{{width:3.4in;margin-bottom:.15in}}
.cover .sub{{font-family:"Anton";font-size:22pt;text-transform:uppercase;line-height:1.05;max-width:4.6in}}
.cover .for{{font-size:12pt;font-style:italic;margin-top:.15in;color:var(--musgo)}}
.cover .meta{{font-size:8.6pt;color:var(--gris)}}
.coords{{font-weight:600;font-size:6.6pt;letter-spacing:.24em;color:var(--gris);margin-top:.24in}}
.url{{font-weight:600;font-size:7.4pt;letter-spacing:.14em;color:var(--rojoh);margin-top:.05in}}
/* carta */
.letter p{{font-size:9.8pt;line-height:1.55;margin-bottom:7pt;max-width:5.3in}}
.sign{{font-style:italic;margin-top:6pt}}
/* fuentes y fotos */
.igrid{{display:grid;grid-template-columns:repeat(5,1fr);gap:4pt}}
.igrid img{{width:100%;aspect-ratio:1;object-fit:cover;display:block}}
.vgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:4pt}}
.vgrid img{{width:100%;aspect-ratio:16/10;object-fit:cover;display:block}}
.voice{{background:var(--rojoh);padding:.32in .3in}}
.vbig{{font-family:"Anton";font-size:27pt;line-height:1.02;color:#fff}}
.vsrc{{font-weight:600;font-size:6pt;letter-spacing:.18em;text-transform:uppercase;color:rgba(255,255,255,.8);margin-top:.12in}}
.pair{{display:grid;grid-template-columns:1fr .7fr;gap:6pt}}
.pair img{{width:100%;height:2.25in;object-fit:cover;display:block}}
.spec{{background:var(--niebla);color:var(--tinta);padding:.26in .28in}}
.sp0{{font-weight:600;font-size:7pt;letter-spacing:.24em;text-transform:uppercase;color:var(--isla);margin-bottom:.08in}}
.sp1{{font-family:"Anton";font-size:30pt;line-height:1;text-transform:uppercase}}
.sp1s{{font-weight:600;font-size:13pt;color:var(--rojo);margin:.02in 0 .02in .05in}}
.sp2{{font-size:10pt;line-height:1.45;margin-top:.14in;color:var(--musgo)}}
.spec .cap{{font-weight:600;font-size:5.8pt;letter-spacing:.16em;text-transform:uppercase;color:var(--gris);margin-top:.12in}}
.pgrid{{display:grid;grid-template-columns:repeat(3,1fr);gap:4pt}}
.pgrid img{{width:100%;aspect-ratio:1;object-fit:cover;display:block}}
.swatches{{display:grid;grid-template-columns:repeat(3,1fr);gap:4pt;margin-top:.1in}}
.swatches span{{height:.62in;padding:6pt;font-weight:600;font-size:6pt;letter-spacing:.12em;text-transform:uppercase;display:flex;align-items:flex-end;line-height:1.5;outline:.5pt solid rgba(242,241,236,.2)}}
.logos{{display:grid;grid-template-columns:1fr 1fr;gap:6pt;padding:.42in .4in;height:100%;align-content:center}}
.lg{{display:grid;place-items:center;height:1.75in;padding:.22in;background-size:cover;background-position:center}}
.lg.light{{background-color:var(--niebla)}}.lg.dark{{background-color:#121614}}
.lg.wide{{grid-column:1/-1;height:1.05in}}
.lg img{{max-width:100%;max-height:1.25in;width:auto;height:auto;display:block}}
.lg.wide img{{max-height:.5in}}
.strip{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:7pt}}
.strip figure img{{width:100%;aspect-ratio:16/10;object-fit:cover;object-position:top;display:block}}
.strip figcaption{{font-weight:600;font-size:5.6pt;letter-spacing:.16em;text-transform:uppercase;margin-top:3pt;margin-bottom:5pt;opacity:.8}}
.mrow{{display:grid;grid-template-columns:repeat(5,1fr);gap:5pt}}
.mrow img{{width:100%;height:1.75in;object-fit:cover;object-position:top;display:block;outline:.5pt solid rgba(242,241,236,.22)}}
/* portada a doble página */
.lam.spread{{display:block}}
.spread .bleed{{position:absolute;inset:0}}
.spread-shade{{display:none}}
.spread-in{{position:absolute;left:8.35in;right:.4in;top:.45in;bottom:.45in;padding:.32in;background:rgba(29,36,33,var(--masa,.8));border-radius:.24in;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;gap:.12in;color:#fff}}
.spread-tab{{position:absolute;left:0;top:.45in;background:rgba(255,255,255,.75);padding:.17in .32in .17in .5in;border-radius:0 .18in .18in 0}}
.spread-logo{{width:1.9in;display:block}}
.spread .sub{{font-family:"Anton";font-size:26pt;text-transform:uppercase;line-height:1.05;text-shadow:0 2px 14px rgba(0,0,0,.45)}}
.spread .for{{font-size:13pt;font-style:italic;margin-top:.1in;text-shadow:0 1px 8px rgba(0,0,0,.5)}}
.spread .meta{{font-size:9pt;opacity:.9}}
.spread .url{{font-weight:600;font-size:8pt;letter-spacing:.16em;color:#fff;margin-top:.06in}}
.spread-coords{{position:absolute;left:.5in;bottom:.35in;font-weight:600;font-size:6.6pt;letter-spacing:.24em;color:rgba(255,255,255,.85)}}
.spec-logo{{width:1.5in;margin-bottom:.14in;display:block}}
.vsm{{font-size:19pt}}
/* cierre */
.close{{display:flex;flex-direction:column;align-items:flex-start;justify-content:center;height:100%;gap:.08in}}
.close .mk{{margin-bottom:.12in}}
.next{{list-style:none;margin:.02in 0 .18in;width:100%}}
.next li{{font-size:10pt;line-height:1.45;padding:5pt 0;border-bottom:.5pt solid #cfd3cf}}
.close a{{color:inherit;text-decoration:none}}
.close .invite{{font-size:13pt;font-style:italic;margin-bottom:.05in}}
.close .who{{font-family:"Anton";font-size:11pt;letter-spacing:.14em;text-transform:uppercase}}
.close .role{{font-size:9pt;margin-top:-3pt}}
.close .contact{{font-size:8.2pt;color:var(--gris)}}
.close .link{{font-family:"Anton";font-size:15pt;letter-spacing:.16em;text-transform:uppercase;color:var(--rojo);margin-top:.1in}}
.close .coords{{margin-top:.12in}}
'''

DOC = f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Chiloé Mágico · Decisiones de diseño del sitio web</title><style>{CSS}</style></head>
<body>{''.join(L)}</body></html>'''
(D / 'chiloemagico-dossier-diseno.html').write_text(DOC, encoding='utf-8')
print('láminas', n, 'MB', round(len(DOC) / 1e6, 1))
