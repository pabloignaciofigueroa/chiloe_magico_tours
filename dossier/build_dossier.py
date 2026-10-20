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
N_NOMBRE = has(['nicol', 'alberto', 'enrique', 'sandra', 'meli', 'rodolfo', 'beto'])
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
RECORRIDO = ['Portada', 'Vamos a navegar', 'Elige tu tour', 'Reseñas', 'Cierre', 'Pie',
             'Catálogo de tours', 'Ficha de tour', 'Destinos', 'Experiencias', 'Paquetes',
             'Servicios privados', 'Nosotros', 'Guía de Chiloé', 'Preguntas frecuentes', 'Contacto']
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
    li = ''.join(f'<li class="{"on" if r == cur else ""}">{E(r)}</li>' for r in RECORRIDO)
    return f'<ol class="rec">{li}</ol>'
PIE = lambda n: f'<footer class="pf"><span>Chiloé Mágico · Decisiones de diseño del sitio</span><span>{COORDS}</span><span>{n:02d}</span></footer>'

C = dict(niebla='#f2f1ec', bruma='#dfe4e6', tinta='#1d2421', musgo='#46473b', tierra='#a69775', mar='#1a8fc4',
         marh='#126a96', isla='#0e766c', chiloe='#17853f', chiloeh='#106530', turismo='#d0342c', turismoh='#b02a23')
def P(*names):
    nom = {'niebla': 'Niebla de Castro', 'bruma': 'Bruma', 'tinta': 'Tinta de alerce', 'musgo': 'Musgo',
           'tierra': 'Tierra chilota', 'mar': 'Mar del logo', 'marh': 'Mar hondo', 'isla': 'Isla Grande',
           'chiloe': 'Verde Chiloé', 'chiloeh': 'Verde hondo', 'turismo': 'Rojo Turismo', 'turismoh': 'Rojo banda'}
    return chips([(nom[n], C[n]) for n in names])

def lamina_seccion(n, nombre, titulo, lead, desk, mob, bloques, nota_izq='', desk2=None):
    left_extra = f'<img class="desk2" src="{shot(desk2)}" alt="">' if desk2 else ''
    if desk2: mob = None
    mob_html = f'<img class="mob" src="{shot(mob, 520)}" alt="">' if mob else ''
    return f'''<article class="lam">
  <div class="L {'two' if desk2 else ''}">
    <p class="lab">Sitio · computador</p>
    <img class="desk" src="{shot(desk)}" alt="">{left_extra}
    <div class="Lrow">
      {f'<div class="mobw"><p class="lab">Celular</p>{mob_html}</div>' if mob else ''}
      <div class="Linfo"><p class="lab">Lugar en el recorrido</p>{recorrido(nombre)}
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
def S(nombre, titulo, lead, desk, mob, bloques, nota='', desk2=None):
    L.append(lamina_seccion(nx(), nombre, titulo, lead, desk, mob, bloques, nota, desk2))

# ======================= 01 PORTADA =======================
L.append(lamina_libre(nx(),
  f'<img class="bleed" src="{raw("huillinco-columpio")}" style="object-position:50% 60%" alt="">',
  f'''<div class="center cover-in">
    <img class="cover-logo" src="{png_file("brand/logo/logo-color.png", 900)}" alt="Turismo Chiloé Mágico">
    <p class="sub">Decisiones de diseño del sitio web</p>
    <p class="for">Preparado para Chiloé Mágico</p>
    <p class="meta">Castro, Chiloé · octubre 2026</p>
    <p class="coords">{COORDS}</p>
    <p class="url">chiloemagicotour.pages.dev</p></div>''', 'full', 'cover'))

# ======================= 02 CARTA =======================
L.append(lamina_libre(nx(),
  f'<img class="bleed" src="{raw("nicolas-enrique")}" style="object-position:50% 40%" alt="">',
  f'''<p class="kick">Antes de empezar</p><h2>Un sitio hecho con lo que ustedes ya dijeron</h2>
  <div class="letter">
  <p>Equipo de Chiloé Mágico:</p>
  <p>Este sitio nació de mirar con atención lo que Chiloé Mágico ya publica. No hay frases inventadas ni promesas de agencia: cada título y cada párrafo sale de sus posts de Instagram, de sus historias destacadas, de sus afiches de tours, de su bio o de lo que sus viajeros escribieron en Google. Lo que hicimos fue ordenarlo, darle aire y ponerlo en movimiento.</p>
  <p>Tampoco hay fotos de banco de imágenes. De las {N_FOTOS} fotos del sitio, {N_PROPIAS} y los 3 videos son de Chiloé Mágico. La única excepción es la del volcán Osorno, de libre uso y con su autor citado, porque aún no han publicado una propia de ese viaje. La letra, los colores y el logo se reconstruyeron a partir de sus propias piezas gráficas.</p>
  <p>Este documento explica, sección por sección, qué se decidió y por qué. En cada lámina, a la izquierda está la sección tal como se ve en el sitio, en computador y en celular. A la derecha, de dónde salió cada texto e imagen, qué letra y qué color se usó, cómo se compuso y por qué va en ese lugar del recorrido.</p>
  <p>Es un regalo. Ojalá lo disfruten tanto como nosotros disfrutamos haciéndolo.</p>
  <p class="sign">Pablo Figueroa G.<br>Director de estudio</p></div>''', 'full'))

# ======================= 03 DE DÓNDE VIENE TODO =======================
grid_keys = ['huillinco-columpio', 'curanto-destape', 'brujos-columpio-2', 'almas-pareja', 'muelle-luz-mirador',
             'caleuche', 'punihuil-bahia', 'pasarela-aucar', 'tenaun', 'palafitos',
             'nicolas-enrique', 'vans', 'yayanes-puente', 'curaco-2', 'mechuque']
igrid = ''.join(f'<img src="{src(k, 300)}" alt="">' for k in grid_keys)
vids = ''.join(f'<img src="{b64img(Image.open(ROOT / "assets/video" / f"{v}-poster.jpg"), 400, 76)}" alt="">' for v in ['isla', 'vuelo', 'vans'])
L.append(lamina_libre(nx(),
  f'''<p class="lab">15 de las {N_PROPIAS} fotos elegidas de su Instagram</p><div class="igrid">{igrid}</div>
  <p class="lab" style="margin-top:.1in">Los 3 videos del sitio, también suyos</p><div class="vgrid">{vids}</div>''',
  f'''<p class="kick">De dónde viene todo</p><h2>Todo esto ya era suyo</h2>
  <p class="lead">Antes de diseñar, leímos y ordenamos todo lo que Chiloé Mágico tiene publicado.</p>
  <div class="grid">
  {block("Instagram", f"<p><b>{N_POSTS} publicaciones</b> leídas una por una: {N_PROPIOS} de ustedes y {N_POSTS - N_PROPIOS} de viajeros que los etiquetaron. Las de viajeros se leyeron, pero no se usan como voz de la marca.</p><p><b>7 historias destacadas</b> y la bio, con su horario, su dirección y su WhatsApp.</p>")}
  {block("Afiches", "<p>Los <b>7 afiches de tours</b> de la destacada «Tours»: de ahí salen los títulos de cada tour, las paradas, la letra y el rojo de la banda.</p>")}
  {block("Google", f"<p><b>{N_REV} reseñas</b> con nota <b>{NOTA}</b>: {N5} de cinco estrellas y {N2} de dos. Se leyeron todas, en su idioma original, para saber qué valoran y qué les falta a sus viajeros.</p>")}
  {block("Fotos y videos", f"<p>De sus publicaciones se eligieron <b>{N_PROPIAS} fotos</b> de {N_POSTS_FOTOS} posts distintos y <b>3 videos</b>. Sin piezas con texto encima ni fotos de cuentas ajenas.</p>")}
  {block("La regla", "<p>Cada texto del sitio tiene su origen identificado: qué post, qué destacada, qué afiche o qué reseña. Si un dato no estaba publicado (precios de la mayoría de los tours, formas de pago, políticas), el sitio lo dice: <b>«por confirmar con la agencia»</b>.</p>", "wide")}
  </div>'''))

# ======================= 04 LA VOZ =======================
L.append(lamina_libre(nx(),
  f'''<div class="voice">
    <p class="vbig">¡NO DEJES QUE TE LO CUENTEN, VEN A DISFRUTAR DE ESTA MÁGICA ISLA JUNTO A NOSOTROS!</p>
    <p class="vsrc">{IG("007")} · y en muchos posts más</p></div>
  <div class="pair"><img src="{src("brujos-vuelo", 700)}" alt=""><img src="{src("curanto-papas", 500)}" alt=""></div>
  <p class="lnote">Viajeros «volando» en el Muelle de los Brujos ({IGD["070"]}) y el curanto ({IGD["086"]}).</p>''',
  f'''<p class="kick">La voz</p><h2>Cercana, alegre y con un remate fijo</h2>
  <p class="lead">Chiloé Mágico escribe como habla un buen guía: tutea, se ríe, usa la mitología como invitación y agradece siempre.</p>
  <div class="grid">
  {block("Tutea y se entusiasma", quote("UN CURANTITO?", IG("010")) + quote("VAMOS A VOLAR UN RATITO?", IG("012")) + "<p class='small'>En el sitio se quitaron los emojis; las preguntas y las mayúsculas se dejaron tal cual.</p>")}
  {block("Mitos como invitación", quote("Cuando hablamos de Chiloé Mágico, no sólo nos referimos a las mil y un historias que se cuentan sobre mitos, leyendas y brujería", IG("042")))}
  {block("Agradece a sus viajeros", quote("nuestro marketing y publicidad más grande son nuestros turistas que cuentan sus experiencias con nosotros", IG("002")))}
  {block("Su firma", "<p>Dos frases que se repiten en sus posts y afiches cierran el sitio: el remate de la izquierda y «Chiloé Mágico te espera, Ven a descubrirlo!», del pie de sus afiches. El sitio escribe con la voz que la marca ya construyó; no agrega superlativos propios.</p>")}
  </div>'''))

# ======================= 05 TIPOGRAFÍA =======================
L.append(lamina_libre(nx(),
  f'''<p class="lab">Cómo se ven juntas en el sitio</p>
  <div class="spec">
    <p class="sp0">Tours de día completo desde Castro</p>
    <p class="sp1">TOUR LA COSTA</p><p class="sp1s">con</p><p class="sp1">CURANTO EN HOYO</p>
    <p class="sp2">Todos nuestros tours incluyen traslado, guiado, almuerzo y bebestibles, y visitas a distintos atractivos turísticos</p>
    <p class="cap">Anton · títulos — Montserrat · textos, rótulos y botones</p></div>
  <img class="desk" style="margin-top:.14in" src="{shot("d-ficha", 1300)}" alt="">''',
  f'''<p class="kick">Tipografía</p><h2>La letra de sus afiches, con aire</h2>
  <p class="lead">Ustedes no tenían sitio, pero sí una gramática clara en sus afiches. La buscamos ahí.</p>
  <div class="grid">
  {block("Anton · títulos", "<p>En sus afiches los títulos van en una letra de palo pesada y angosta, en mayúsculas («TOUR / LA COSTA / CURANTO EN HOYO»). Anton es su equivalente libre: enorme en portadas y nombres de tour, siempre en mayúsculas.</p>")}
  {block("Montserrat · todo lo demás", "<p>Su pieza «Visita CHILOÉ con nuestros TOURS DE DÍA COMPLETO» usa una letra redonda y geométrica. Montserrat la reemplaza en textos, botones y en los rótulos pequeños, muy espaciados.</p>")}
  {block("La palabra de enlace", "<p>Sus afiches unen dos líneas con una palabra suelta («con», «de la», «Isla»). El sitio respeta ese gesto: «TOUR LA COSTA / <i>con</i> / CURANTO EN HOYO». En el afiche esa palabra va en letra manuscrita; en el sitio va en Montserrat gruesa, a veces en rojo, para que el título se lea de un vistazo.</p>")}
  {block("El logo, aparte", "<p>Las letras irregulares del logo no se usan como letra de textos: el logo se redibujó a partir del original y aparece solo como logo.</p>")}
  </div>'''))

# ======================= 06 PALETA =======================
pal_src = ['punihuil-bahia', 'yayanes-puente', 'palafitos', 'almas-camino', 'hueñay-playa', 'ancud-atardecer']
pgrid = ''.join(f'<img src="{src(k, 320)}" alt="">' for k in pal_src)
sw = [('niebla', 'Niebla de Castro', '#1d2421'), ('bruma', 'Bruma', '#1d2421'), ('tierra', 'Tierra chilota', '#1d2421'),
      ('tinta', 'Tinta de alerce', '#f2f1ec'), ('musgo', 'Musgo', '#f2f1ec'), ('isla', 'Isla Grande', '#f2f1ec'),
      ('mar', 'Mar del logo', '#fff'), ('chiloe', 'Verde Chiloé', '#fff'), ('turismo', 'Rojo Turismo', '#fff')]
swh = ''.join(f'<span style="background:{C[k]};color:{fg}">{nm}<br>{C[k]}</span>' for k, nm, fg in sw)
L.append(lamina_libre(nx(),
  f'''<p class="lab">Fotos de ustedes de donde salen los tonos</p><div class="pgrid">{pgrid}</div>
  <div class="swatches">{swh}</div>''',
  f'''<p class="kick">Paleta</p><h2>El cielo de sus fotos y los colores de su logo</h2>
  <p class="lead">Medimos los tonos que más se repiten en sus fotos, en sus afiches y en su logo. La paleta tiene dos familias.</p>
  <div class="grid">
  {block("Base · el territorio", "<p>Los cielos nublados de Chiloé, aclarados, dan el fondo: <b>Niebla de Castro</b> y <b>Bruma</b>. Las sombras del bosque y de la madera dan el oscuro: <b>Tinta de alerce</b> y <b>Musgo</b>. <b>Tierra chilota</b> acompaña.</p>" + P("niebla", "bruma", "tinta", "musgo", "tierra"))}
  {block("Acento · el logo", "<p>Los colores del logo se usan tal cual: el azul de la «C» y la «M», el verde azulado de la isla, el verde de «Chiloé» y el <b>rojo de «TURISMO»</b>, que es también la banda roja de sus afiches.</p>" + P("mar", "isla", "chiloe", "turismo"))}
  {block("Rojo = reservar", "<p>El rojo se reserva para lo que lleva a reservar: el botón «Reservar», «Cotizar por WhatsApp» y el pie. Así el ojo aprende rápido dónde se actúa.</p>" + P("turismoh"))}
  {block("Legibilidad", "<p>Para textos chicos se usan versiones más hondas del azul, el verde y el rojo. Todo se lee con holgura, incluso con poca vista o con sol sobre la pantalla del celular, que es como se leerá en plena excursión.</p>" + P("marh", "chiloeh"))}
  </div>'''))

# ======================= 07 LOGO =======================
L.append(lamina_libre(nx(),
  f'''<div class="logos">
    <div class="lg light"><img src="{png_file("brand/logo/logo-color.png", 700)}" alt=""></div>
    <div class="lg dark"><img src="{png_file("brand/logo/logo-white.png", 700)}" alt=""></div>
    <div class="lg photo" style="background-image:url({src("huillinco-columpio", 800)})"><img src="{png_file("brand/logo/logo-sticker.png", 700)}" alt=""></div>
    <div class="lg light"><img src="{png_file("brand/logo/isotipo-color.png", 500)}" alt=""></div>
    <div class="lg light wide"><img src="{png_file("brand/logo/logotipo-h-color.png", 1100)}" alt=""></div></div>''',
  f'''<p class="kick">Logo</p><h2>Ven a descubrirlo!</h2>
  <p class="lead">El logo de su foto de perfil (la isla, «TURISMO» en rojo, «Chiloé Mágico» y su eslogan) se redibujó para que sea nítido a cualquier tamaño.</p>
  <div class="grid">
  {block("Cómo se redibujó", "<p>Se calcó sobre el original, respetando la silueta de la isla, el orden de las palabras y sus colores. No se cambió nada del diseño: solo dejó de verse borroso al agrandarlo.</p>")}
  {block("Variantes", "<p>A color sobre fondo claro, en blanco sobre fondo oscuro, una versión «adhesivo» con borde blanco para ponerla sobre fotos, la isla sola como ícono y una versión horizontal para la barra de arriba.</p>")}
  {block("Dónde aparece", "<p>La versión adhesivo en la portada y en el pie; la horizontal en la barra de arriba; la isla sola en el ícono de la pestaña del navegador y en la imagen que aparece al compartir el enlace por WhatsApp.</p>")}
  {block("La isla, también ventana", "<p>La silueta de Chiloé del logo se usa una vez más en la portada: es la ventana por la que se ve el video de la navegación en Puñihuil (lámina 10).</p>")}
  </div>'''))

# ======================= 08 RECORRIDO =======================
strip = [('d-hero', 'Portada'), ('d-isla-b', 'Vamos a navegar'), ('d-tours', 'Elige tu tour'),
         ('d-reviews', 'Reseñas'), ('d-bcta', 'Cierre'), ('d-ficha', 'Ficha de tour'),
         ('d-destinos', 'Destinos'), ('d-nosotros', 'Nosotros'), ('d-contacto', 'Contacto')]
sh = ''.join(f'<figure><img src="{shot(k, 640)}" alt=""><figcaption>{c}</figcaption></figure>' for k, c in strip)
L.append(lamina_libre(nx(), f'<p class="lab">El recorrido</p><div class="strip">{sh}</div>',
  f'''<p class="kick">Recorrido</p><h2>Un día de tour, en cuatro actos</h2>
  <p class="lead">La portada se recorre como una excursión: llegar, elegir, confiar y reservar. Las demás páginas profundizan en cada paso.</p>
  <div class="grid">
  {block("1 · Llegar", "<p>La portada con el columpio del lago Huillinco y la frase de su bio. Enseguida, la navegación en Puñihuil dentro de la silueta de la isla.</p>")}
  {block("2 · Elegir", "<p>Los 8 tours como sus afiches, uno al lado del otro. Cada uno abre su ficha: paradas, qué incluye, horario y fotos. Destinos y experiencias ofrecen otras dos formas de buscar.</p>")}
  {block("3 · Confiar", f"<p>{N_REV} reseñas con nota {NOTA}, el equipo con sus nombres (guías y conductores), las vans y los más de 20 años de servicio.</p>")}
  {block("4 · Reservar", "<p>Su remate «¡NO DEJES QUE TE LO CUENTEN…!» y WhatsApp siempre a un toque: en la barra de arriba, en cada ficha y en el botón verde que acompaña toda la visita.</p>")}
  {block("Ritmo", "<p>Se alternan fondos claros (Niebla) y oscuros (Tinta de alerce) con fotos a pantalla completa, para que el recorrido respire como una salida al aire libre y termine en la banda roja de sus afiches.</p>", "wide")}
  </div>'''))

# ======================= SECCIONES DE LA PORTADA =======================
S('Portada', 'Nuestro archipiélago es mágico',
  'La primera pantalla: una foto suya a pantalla completa, su logo, la frase de su bio y dos caminos, ver los tours o escribir por WhatsApp.',
  'd-hero', 'm-hero', [
    block('Textos', quote('Nuestro archipiélago es mágico ¡Ven a descubrirlo!', 'Bio de Instagram') + quote('¡Tours todos los días! - Servicios privados', 'Bio de Instagram')),
    block('Imagen', thumbs([('huillinco-columpio', 'Columpio del lago Huillinco · ' + ORIG('huillinco-columpio'))]) + '<p>Agua quieta, cerros y un columpio: Chiloé en calma, sin texto encima.</p>'),
    block('Datos de confianza', f'<p>Al pie, cuatro datos verificables: <b>{NOTA} ★ en Google · {N_REV} reseñas</b>, tours de lunes a domingo, máximo 16 pasajeros por van y salida a las 10:00 frente a la Plaza de Armas. En celular quedan los dos primeros.</p>'),
    block('Por qué así', f'<p>Lo primero que hace un viajero es comparar agencias. La nota de Google y el tamaño de los grupos responden esa duda antes de bajar. Una viajera lo escribió así:</p>' + quote('El transporte es en vehículos pequeños pero cómodos, lo cual hace que la experiencia sea muy personalizada.', 'Gabriela · Google')),
  ])

S('Vamos a navegar', 'Vamos a navegar?',
  'La isla de su logo se vuelve una ventana. Al bajar por la página, la silueta crece hasta que el video de la navegación en Puñihuil ocupa toda la pantalla.',
  'd-isla-a', None, [
    block('Textos', quote('Vamos a navegar?', IG('015')) + '<p>Bajada: «Entre los islotes de Puñihuil, con los pingüinos».</p>'),
    block('Video', thumbs([('punihuil-navega', 'Navegación en Puñihuil · ' + IG('015'))]) + f'<p>Un tramo de su video del {IGD["013"]}, aligerado para que cargue rápido incluso con poca señal.</p>'),
    block('Movimiento', '<p>Es el único momento «de efecto» del sitio: la isla crece suave mientras se baja y el velo oscuro desaparece. Si alguien prefiere menos movimiento en su teléfono, la isla aparece ya abierta.</p>'),
    block('Por qué aquí', quote('La experiencia de ver los pingüinos que ofrece la caleta Puñihuil es de otro nivel', IG('057')) + '<p>Su logo ya es la isla. Antes de ver la lista de tours, el viajero entra «dentro» de Chiloé por la ventana de su propia marca.</p>'),
  ], nota='Arriba, la isla recién abriéndose; abajo, a pantalla completa.', desk2='d-isla-b')

S('Elige tu tour', 'Elige tu tour',
  'Los 8 tours, uno al lado del otro, como si estuvieran sus afiches colgados en la vitrina de la agencia. Se deslizan con el dedo o con las flechas.',
  'd-tours', 'm-tours', [
    block('Textos', quote('Todos nuestros tours incluyen traslado, guiado, almuerzo y bebestibles, y visitas a distintos atractivos turísticos', IG('007')) + '<p>Bajo cada nombre, una frase suya del post de ese tour: «UN CURANTITO?», «Caminar entre bosque y mar es lo mágico de Chiloé».</p>'),
    block('Imágenes', thumbs([('curanto-destape', 'Destape del curanto · ' + ORIG('curanto-destape')), ('brujos-columpio-2', 'Muelle de los Brujos · ' + ORIG('brujos-columpio-2')), ('almas-pareja', 'Muelle de las Almas · ' + ORIG('almas-pareja')), ('caleuche', 'Muelle del Caleuche · ' + ORIG('caleuche'))])),
    block('Composición', '<p>Tarjetas altas, foto arriba y nombre en Anton abajo, con un rótulo verde que dice lo distintivo («Con curanto en hoyo», «Con asado al palo»). En computador se ven cuatro y media, para que se note que hay más; en celular, una y un borde de la siguiente.</p>'),
    block('Por qué así', f'<p>{N_COMIDA} de las {N_REV} reseñas hablan de la comida: el curanto, el asado de cordero, el almuerzo. Por eso el rótulo de cada tour nombra primero lo que se come o lo que se vive, antes que la lista de lugares.</p>'),
  ])

S('Reseñas', f'{NOTA} ★ en Google',
  f'Trece reseñas reales, en el idioma en que se escribieron, sobre fondo oscuro. Se deslizan igual que los tours y terminan en un enlace a su ficha de Google Maps.',
  'd-reviews', 'm-reviews', [
    block('Textos', quote('Alberto, el guía lo da todo, explica y atiende cada pregunta, está atento a todo. Transmite el amor por la tierra y la cultura chilota.', 'Andrea · Google') + quote('A sympathetic guide tour who made us laugh a lot with a million stories.', 'elia · Google · en su idioma original', 'en')),
    block('Datos', f'<p><b>{NOTA} ★ · {N_REV} reseñas</b>, leído en Google Maps el 19 de octubre de 2026. Solo nombre de pila y «vía Google»; el país, solo si la persona lo dice («desde Iquique»).</p>'),
    block('Lo que se decidió no mostrar', f'<p>Las {N2} reseñas de dos estrellas se leyeron pero no se publican. Una de ellas sí dejó una enseñanza: el sitio explica que los tours son guiados en español (lámina 24).</p>'),
    block('Por qué así', f'<p><b>{N_GUIA} de las {N_REV} reseñas</b> hablan del guía y <b>{N_NOMBRE}</b> nombran a alguien del equipo: Nicolás, Alberto, Sandra, don Enrique. Por eso se eligieron reseñas que dicen nombres; son la mejor carta de presentación de la agencia.</p>'),
  ])

S('Cierre', '¡No dejes que te lo cuenten!',
  'Antes del pie, el remate que ustedes repiten en sus posts, enorme sobre la bahía de Puñihuil, con un solo botón: cotizar por WhatsApp.',
  'd-bcta', 'm-bcta', [
    block('Textos', quote('¡NO DEJES QUE TE LO CUENTEN, VEN A DISFRUTAR DE ESTA MÁGICA ISLA JUNTO A NOSOTROS!', IG('007')) + quote('Gamboa 351, Local Interior 116 (Frente a Plaza de Armas Castro)', AFICHES)),
    block('Imagen', thumbs([('punihuil-bahia', 'Bahía de Puñihuil · ' + ORIG('punihuil-bahia'))])),
    block('Letra / Color', '<p>La frase completa en Anton, blanca y en mayúsculas, como en sus posts. Un velo oscuro sobre la foto asegura que se lea. El botón, en el rojo de la banda de sus afiches.</p>' + P('turismoh', 'niebla')),
    block('Por qué aquí', '<p>Es su frase de cierre de siempre; en el sitio cumple el mismo papel. Al final de la portada no se ofrece nada nuevo: solo una invitación y la dirección «frente a la Plaza de Armas», tal como dicen sus afiches.</p>'),
  ])

S('Pie', 'Chiloé Mágico te espera',
  'El pie es la banda roja con la gaviota de sus afiches: logo, su eslogan, el mapa del sitio y todos los datos de contacto.',
  'd-foot', 'm-foot', [
    block('Textos', quote('Chiloé Mágico te espera, Ven a descubrirlo!', AFICHES) + quote('Av. Gamboa 351, Galería Alonso de Ercilla, Local Interior 116, Castro, Chile · Lu a Do | 9:00 a 19:30', 'Bio de Instagram')),
    block('Composición', '<p>Una ola suave separa la página del pie. Logo adhesivo a la izquierda, dos columnas («Sitio» y «Visítanos») y, al final, una línea pequeña con lo que falta confirmar.</p>' + P('turismo', 'niebla')),
    block('Datos', '<p>WhatsApp +56 9 7890 2625 (el de su bio), teléfono +56 9 9883 3946 y correo chiloemagicocontacto@gmail.com, publicados en el portal de turismo de Castro, e Instagram @chiloemagicotour.</p>'),
    block('Por qué así', '<p>La banda roja con la gaviota es el pie de todos sus afiches; ahora también es el pie del sitio. La línea «Pagos, sellos y políticas: por confirmar con la agencia» es honesta: no se inventa lo que no está publicado.</p>'),
  ])

# ======================= PÁGINAS INTERNAS =======================
S('Catálogo de tours', 'Nuestros tours disponibles',
  'La página «Tours» reúne los 8 recorridos en una grilla, con el horario común de todos arriba. Desde aquí se entra a cada ficha.',
  'd-tlist', None, [
    block('Textos', quote('NUESTROS TOURS disponibles', AFICHES + ' · portada') + quote('Todos son tours de día completo (salida a las 10am y retorno a las 7pm aprox)', IG('006')) + '<p class="small">«disponibles» se pasó a una segunda línea, como palabra de enlace.</p>'),
    block('Imagen', thumbs([('muelle-luz-oceano', 'Muelle de la Luz · ' + ORIG('muelle-luz-oceano'))])),
    block('Composición', '<p>Portada con el océano frente al Muelle de la Luz y, debajo, las mismas tarjetas de la portada, ahora en grilla de tres para verlas todas de una vez.</p>'),
    block('Por qué así', '<p>Quien llega directo desde Google buscando «tours en Chiloé» necesita ver la oferta completa sin deslizar. El título es el de la portada de su propia destacada «Tours».</p>'),
  ], desk2='d-tlist2')

S('Ficha de tour', 'Tour La Costa con curanto en hoyo',
  'Cada tour tiene su página, armada como uno de sus afiches. Aquí, el Tour La Costa: el título del afiche sobre la pasarela de la Isla Aucar.',
  'd-ficha', 'm-ficha', [
    block('Textos', quote('TOUR LA COSTA con CURANTO EN HOYO', AFICHES) + quote('UN CURANTITO?', IG('010'))),
    block('Imágenes', thumbs([('pasarela-aucar', 'Pasarela de Aucar · ' + ORIG('pasarela-aucar')), ('curanto-hoyo', 'Curanto · ' + ORIG('curanto-hoyo')), ('tenaun', 'Tenaún · ' + ORIG('tenaun'))])),
    block('Composición', '<p>Título en tres líneas, con «con» como palabra de enlace, igual que en el afiche. Debajo, la frase de su post y un único botón rojo. Las 8 fichas comparten esta misma estructura.</p>'),
    block('Por qué así', '<p>Sus afiches ya resolvían cómo presentar un tour: nombre grande, el plato estrella y las paradas. La ficha traslada eso a la pantalla, para que el viajero reconozca el mismo tour que vio en Instagram.</p>'),
  ])

S('Ficha de tour', 'El tour en 3 puntos',
  'Bajo la portada de cada ficha: qué recorres, qué incluye, horario y precio. Luego, sus fotos de ese tour y un formulario corto que termina en WhatsApp.',
  'd-ficha-info', None, [
    block('Textos', quote('Feria Artesanal Dalcahue · Iglesia Patrimonio Tenaún · Almuerzo en agroturismo · Cascadas de Tocoihue · Isla Aucar', AFICHES + ' · paradas del afiche') + quote('Consulta por cupos, no te quedes sin el tuyo', IG('006'))),
    block('Datos', '<p><b>$35.000 por persona</b> (con almuerzo) + <b>$3.000</b> de entrada a las cascadas, según su post del 7 de febrero de 2025. Es el único tour con precio publicado; en los demás, el sitio dice «por confirmar».</p><p class="small">Conviene confirmar si este valor sigue vigente.</p>'),
    block('Interacción', '<p>El formulario pide solo fecha y número de personas, y abre WhatsApp con el mensaje ya escrito. En celular, una barra fija abajo muestra el precio y el botón «Cotizar» durante toda la lectura.</p>'),
    block('Por qué así', quote('El tour fue preciso, teníamos tiempo para recorrer libremente y solo acordábamos la hora de reunión…', 'Ximena · Google') + '<p>Los viajeros valoran saber qué pasa en el día. Por eso la ficha pone las paradas y el horario antes que cualquier otra cosa.</p>'),
  ], desk2='d-ficha-cot')

S('Destinos', 'Explora por destino',
  'Una segunda forma de buscar: por lugar. Cinco zonas del archipiélago, cada una con su página y los tours que pasan por ahí.',
  'd-destinos', None, [
    block('Textos', quote('Contamos con salidas diarias a distintos paramos de este fantástico archipiélago, para consultas y programaciones pueden hablarnos a nuestro WhatsApp', IG('033')) + quote('En el mapudungun de Chiloé Dalkawe significa lugar de dalcas…', IG('087'))),
    block('Imágenes', thumbs([('palafitos', 'Palafitos de Castro · ' + ORIG('palafitos')), ('aucar-isla', 'Isla Aucar · ' + ORIG('aucar-isla')), ('almas-camino', 'Muelle de las Almas · ' + ORIG('almas-camino'))])),
    block('Composición', '<p>Castro, Ancud y Puñihuil, Dalcahue y Quinchao, Chonchi y Lemuy, Cucao y el Parque. Fotos de distinto tamaño, como un mosaico, con el nombre del lugar en Anton.</p>'),
    block('Por qué así', '<p>Muchos viajeros llegan sabiendo a dónde quieren ir, no qué tour tomar. Ustedes ya explican cada lugar en sus posts (qué significa Dalcahue, por qué Aucar es la isla de las almas navegantes); esas explicaciones son el texto de cada destino.</p>'),
  ], desk2='d-destinos2')

S('Experiencias', 'Explora por experiencia',
  'La tercera forma de buscar: por lo que se quiere vivir. Patrimonio e iglesias, naturaleza, navegación, gastronomía y mitos.',
  'd-experiencias', None, [
    block('Textos', quote('Cuando hablamos de Chiloé Mágico, no sólo nos referimos a las mil y un historias que se cuentan sobre mitos, leyendas y brujería', IG('042')) + quote('¡Llegó la hora del destape! #curantoalhoyo', IG('086'))),
    block('Imágenes', thumbs([('brujos-vuelo', 'Muelle de los Brujos · ' + ORIG('brujos-vuelo')), ('yayanes-puente', 'Parque Yayanes · ' + ORIG('yayanes-puente')), ('tenaun', 'Iglesia de Tenaún · ' + ORIG('tenaun'))])),
    block('Composición', '<p>Cinco bloques con foto, cada uno lleva a su página con los tours que la incluyen. El título de cada experiencia sale del post donde ustedes la cuentan.</p>'),
    block('Por qué así', quote('I enjoyed the myths of brujería and the taste of chiloe with Nicolas.', 'elia · Google', 'en') + '<p>Sus viajeros recuerdan los mitos y la comida tanto como los paisajes. Por eso «Mitos» y «Gastronomía» están al mismo nivel que «Patrimonio».</p>'),
  ], desk2='d-experiencias2')

S('Paquetes', 'Viajes de varios días',
  'Los viajes largos que ustedes ya han hecho fuera de Chiloé: Valdivia y Niebla, el volcán Osorno y Bariloche.',
  'd-paquetes', None, [
    block('Textos', quote('Otra salida marcada por innumerable recuerdos, una agradecimiento a nuestros amigos por contar con nosotros, excursión Valdivia y Niebla 4 días - 3 noches', IG('016')) + quote('recorrido de castro al volcán Osorno, visitando salto de petrohue y el lago todos los santos…', IG('031'))),
    block('Imágenes', thumbs([('valdivia', 'Valdivia y Niebla · ' + ORIG('valdivia')), ('nieve', 'Bariloche · ' + ORIG('nieve')), ('osorno', 'Volcán Osorno · foto de libre uso, autor citado')])),
    block('Composición', '<p>Cada viaje es una franja con foto a un lado y texto al otro, alternando lados. La duración va arriba en rótulo pequeño («4 días · 3 noches»); itinerario, alojamiento y precio, «por confirmar».</p>'),
    block('Por qué así', '<p>Son viajes que ustedes publicaron entre 2023 y 2024. Como no hay fechas vigentes publicadas, el sitio los muestra como lo que ofrecen hacer, no como salidas confirmadas. La foto del Osorno es la única que no es suya, y lleva el crédito de su autor.</p>'),
  ], desk2='d-paquetes2')

S('Servicios privados', 'Traslados, privados y grupos',
  'Una página para lo que su bio llama «Servicios privados»: las vans, los traslados y los grupos armados a medida.',
  'd-servicios', 'm-servicios', [
    block('Textos', quote('Es por esto que diariamente nos trasladamos en modernas y cómodas vans Con aire acondicionado (para que ni el frio ni el calor nos detengan!), asientos reclinables para la siesta post almuerzo, y conductores que además de profesionales son wena onda!', IG('007'))),
    block('Imágenes', thumbs([('vans', 'Las vans · ' + ORIG('vans')), ('grupo-van', 'Grupo del Tour La Costa · ' + ORIG('grupo-van')), ('grupo-columpios', 'Grupo en los columpios · ' + ORIG('grupo-columpios'))])),
    block('Letra / Color', '<p>La portada usa la foto de sus tres vans junto al mar. «TRASLADOS, PRIVADOS» en Anton y «y grupos» como palabra de enlace.</p>' + P('tinta', 'niebla')),
    block('Por qué así', '<p>Su post de las vans es de los más completos que han escrito: dice cómo viajan, cuántos van y quién maneja. Se dejó entero, con su «wena onda», porque es justo lo que alguien busca al contratar un traslado privado.</p>'),
  ])

S('Nosotros', 'Somos Chiloé Mágico',
  'Quiénes son: su presentación, sus más de 20 años y, sobre todo, su equipo con nombre, tal como aparece en sus posts y en las reseñas.',
  'd-nosotros', None, [
    block('Textos', quote('Somos Chiloé Mágico! Una empresa dedicada a entregarte la mejor experiencia en nuestro archipiélago. Ven a conocer esta majestuosa zona insular junto a nosotros!', IG('017')) + quote('Somos una empresa dedicada al rubro turístico, con más de 20 años de servicio…', IG('032'))),
    block('Imágenes', thumbs([('nicolas-enrique', 'Nicolás y don Enrique · ' + ORIG('nicolas-enrique')), ('muelle-luz-grupo', 'Grupo en el Muelle de la Luz · ' + ORIG('muelle-luz-grupo'))])),
    block('El equipo', '<p>Guías: Nicolás, Alberto, Meli, Sandra y Rodolfo. Conductores: don Enrique, Marcelo y Marco. Cada nombre aparece en sus posts o en reseñas de Google.</p>' + quote('Nuestro guía Nicolás junto a don Enrique siempre enfocados en brindarle la mejor experiencia a nuestros turistas!', IG('023'))),
    block('Por qué así', f'<p>{N_NOMBRE} reseñas nombran a alguien del equipo. Lo que distingue a Chiloé Mágico no es un paisaje (esos los muestran todas las agencias), sino las personas. Por eso «Nosotros» muestra caras y nombres, y cierra con sus propias reseñas.</p>'),
  ], desk2='d-nosotros2')

S('Guía de Chiloé', 'Historias del archipiélago',
  'Cinco artículos cortos con lo que ustedes ya han explicado en Instagram: el curanto, las iglesias, los brujos y las almas, la minga y los pingüinos.',
  'd-guia', None, [
    block('Textos', quote('Te estarás preguntando ¿que es el curanto?', IG('034')) + quote('Con viento y lluvia, se vive la magia y aventura de Chiloé.', IG('137'))),
    block('Imágenes', thumbs([('curanto-fuego', 'Curanto · ' + ORIG('curanto-fuego')), ('nercon', 'Iglesia de Nercón · ' + ORIG('nercon')), ('minga', 'Minga · ' + ORIG('minga'))])),
    block('Lo que se decidió', '<p>La minga de febrero de 2025 ya pasó: se cuenta como tradición que ustedes acompañaron, no como una actividad para reservar. Cada artículo termina en el tour donde se vive.</p>'),
    block('Por qué así', '<p>Sus posts explicativos (qué es el curanto, de qué madera son las iglesias, qué cuentan los mitos) son muy buenos, pero en Instagram se pierden con el tiempo. Reunidos en una guía, ayudan a que los encuentren en Google quienes están planificando su viaje.</p>'),
  ], desk2='d-guia-art')

S('Preguntas frecuentes', '¿En qué idioma es el guiado?',
  'Las dudas típicas antes de reservar, respondidas con sus propias palabras. Cada respuesta se abre con un toque.',
  'd-faq', 'm-faq', [
    block('Textos', quote('Salidas desde nuestra agencia, ubicada frente a la plaza de armas, a un costado de la Iglesia de Castro', IG('006')) + quote('FYI the tour is not available in english.', 'Maja · Google', 'en')),
    block('Datos', '<p>14 preguntas: salida, horario, qué incluye, tamaño del grupo, días, idioma, lluvia, comida vegetariana, precio, reserva, cancelación, pago, niños y horario de la agencia. Las que ustedes no han respondido en público dicen «Por confirmar con la agencia».</p>'),
    block('Por qué así', '<p>Tres reseñas en inglés mencionan que el tour es en español; una de ellas, de dos estrellas, es de alguien que esperaba explicaciones en inglés. Decirlo antes evita esa sorpresa y cuida la nota de Google.</p>'),
    block('Por qué también', quote('They were able to add vegetarian meals at the restaurant.', 'Zarana · Google', 'en') + '<p>Las respuestas de los propios viajeros también sirven: la opción vegetariana existe porque una viajera lo contó.</p>'),
  ])

S('Contacto', 'Reserva ahora',
  'Todos los caminos para escribirles, la dirección frente a la Plaza de Armas y un formulario corto que llega a su WhatsApp.',
  'd-contacto', None, [
    block('Textos', quote('RESERVA AHORA', 'Pieza «Visita CHILOÉ» · ' + IG('017')) + quote('Informaciones y reservas', IG('006'))),
    block('Imágenes', thumbs([('chonchi', 'Chonchi · ' + ORIG('chonchi')), ('palafitos', 'Palafitos de Castro · ' + ORIG('palafitos'))])),
    block('Interacción', '<p>Nombre, fechas aproximadas, personas y qué les gustaría conocer. Al enviar, se abre WhatsApp con todo escrito. No hay correo intermedio ni datos guardados en otra parte.</p>'),
    block('Por qué así', '<p>Su bio dice «Escríbenos» con el enlace de WhatsApp, y sus afiches llevan ese mismo número: ese es su canal real. El sitio no crea uno nuevo; ordena la primera conversación para que llegue con fecha y número de personas.</p><p class="small">En la bio y en el portal municipal aparecen dos números distintos; ambos están en el sitio hasta que ustedes confirmen cuál usar.</p>'),
  ], desk2='d-contacto2')

# ======================= DETALLES =======================
mrow = ''.join(f'<img src="{shot(k, 360)}" alt="">' for k in ['m-hero', 'm-tours', 'm-ficha-info', 'm-nosotros', 'm-contacto'])
L.append(lamina_libre(nx(),
  f'''<p class="lab">Menú abierto</p><img class="desk" style="width:66%" src="{shot("d-menu", 1100)}" alt="">
  <p class="lab" style="margin-top:.06in">En inglés</p><img class="desk" style="width:50%" src="{shot("d-en", 900)}" alt="">
  <p class="lab" style="margin-top:.06in">Celular</p><div class="mrow">{mrow}</div>''',
  f'''<p class="kick">Detalles en todo el sitio</p><h2>Lo que no se ve, pero se siente</h2>
  <p class="lead">Decisiones que acompañan toda la visita, en todas las páginas.</p>
  <div class="grid">
  {block("Menú", "<p>Cuatro capítulos grandes (Tours, Paquetes, Nosotros, Contacto). Al pasar sobre cada uno aparece una foto suya de ese tema.</p>")}
  {block("Español e inglés", "<p>Un botón ES · EN traduce todo lo que guía la visita: menús, botones, rótulos. Sus textos y las reseñas quedan en su idioma original, para no poner palabras en su boca.</p>")}
  {block("WhatsApp siempre a mano", "<p>Un botón verde acompaña cada página. En las fichas, una barra con el precio y «Cotizar» se queda abajo mientras se lee.</p>")}
  {block("Pensado para celular", "<p>Cada página se ordena distinto en el teléfono: una columna, botones grandes y WhatsApp a un toque. Las fotos se aligeraron y se descargan a medida que se baja, para que funcione incluso con poca señal en ruta.</p>")}
  {block("Sin tropiezos", "<p>Las fotos reservan su espacio antes de cargar, así la página no salta mientras se lee. Se puede recorrer completo con el teclado, y cada foto tiene su descripción en español e inglés para quien usa lector de pantalla.</p>", "wide")}
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
.sp1{{font-family:"Anton";font-size:34pt;line-height:1;text-transform:uppercase}}
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
