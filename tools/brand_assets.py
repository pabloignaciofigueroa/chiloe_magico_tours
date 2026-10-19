"""Arma las variantes del logo desde el trazado (brand/logo/_trace.json) — fase 5."""
import json, re, pathlib
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
T = json.load(open('brand/logo/_trace.json')); W, H = T['W'], T['H']
OUT = pathlib.Path('brand/logo'); OUT.mkdir(parents=True, exist_ok=True)
COL = {'mar': '#1a8fc4', 'verde': '#17853f', 'rojo': '#d0342c', 'isla': '#0e766c', 'gaviota': '#0e5f63'}

def contours(d):
    return [c.strip() for c in re.findall(r'M[^M]*', d)]

def bbox(c):
    n = list(map(float, re.findall(r'-?\d+\.?\d*', c)))
    xs, ys = n[0::2], n[1::2]
    return min(xs), min(ys), max(xs), max(ys)

# limpiar fragmentos fuera del logo (borde del círculo de foto bajo el logo)
P = {}
for k, d in T['paths'].items():
    keep = [c for c in contours(d) if bbox(c)[1] < H * 0.86 and (bbox(c)[2]-bbox(c)[0])*(bbox(c)[3]-bbox(c)[1]) > 900]
    P[k] = ' '.join(keep)

# bounding box real
allb = [bbox(c) for d in P.values() for c in contours(d)]
X0 = min(b[0] for b in allb); Y0 = min(b[1] for b in allb); X1 = max(b[2] for b in allb); Y1 = max(b[3] for b in allb)

# gaviota reconstruida (línea simple, medida sobre el afiche): caja local 100x100
GULL_BOX = (1290, 380, 1690, 760)
def gull(stroke, fill, sw=2.6):
    x0, y0, x1, y1 = GULL_BOX; sx = (x1 - x0) / 100; sy = (y1 - y0) / 100
    body = ('M4,4 C22,16 42,36 56,55 C62,53 70,52 78,53 C82,53.5 85,55 86,57 C83,59 79,60 75,61 '
            'C82,72 90,85 97,98 C86,88 75,76 66,65 C58,66 50,67 44,69 C47,66 50,63 52,61 C40,42 22,20 4,4 Z')
    head = 'M78,53 C81,52 84.5,53.5 86,57 C83,58.5 80,59 77,58.5 Z'
    return (f'<g transform="translate({x0} {y0}) scale({sx:.3f} {sy:.3f})">'
            f'<path d="{body}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
            f'<path d="{head}" fill="{stroke}"/></g>')

pad = 40
VB = f'{X0 - pad:.0f} {Y0 - pad:.0f} {X1 - X0 + 2 * pad:.0f} {Y1 - Y0 + 2 * pad:.0f}'

def svg(body, vb=VB, title='Turismo Chiloé Mágico'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{title}"><title>{title}</title>{body}</svg>\n'

def layers(colors, gull_stroke, gull_fill, sticker=None):
    st = f' stroke="{sticker}" stroke-width="34" stroke-linejoin="round" paint-order="stroke"' if sticker else ''
    out = ''
    if sticker:  # base blanca tipo adhesivo, como en sus afiches
        out += f'<g fill="{sticker}" stroke="{sticker}" stroke-width="70" stroke-linejoin="round">' + ''.join(f'<path d="{P[k]}"/>' for k in P) + '</g>'
        out += gull(sticker, sticker, 40).replace('vector-effect="non-scaling-stroke"', '')
    for k in ['mar', 'isla', 'verde', 'rojo']:
        out += f'<path fill="{colors[k]}" fill-rule="evenodd" d="{P[k]}"/>'
    out += gull(gull_stroke, gull_fill)
    return out

full = layers(COL, COL['gaviota'], '#ffffff')
(OUT / 'logo-color.svg').write_text(svg(full))
(OUT / 'logo-sticker.svg').write_text(svg(layers(COL, COL['gaviota'], '#ffffff', sticker='#ffffff'), vb=f'{X0-90:.0f} {Y0-90:.0f} {X1-X0+180:.0f} {Y1-Y0+180:.0f}'))
mono = lambda c: {k: c for k in COL}
(OUT / 'logo-white.svg').write_text(svg(layers(mono('#ffffff'), '#ffffff', 'none')))
(OUT / 'logo-ink.svg').write_text(svg(layers(mono('#1d2421'), '#1d2421', 'none')))

# isotipo: la C (mar) + isla. La C es el contorno "mar" más a la izquierda.
mar = contours(P['mar']); c_shape = min(mar, key=lambda c: bbox(c)[0])
bx = bbox(c_shape); ib = [bbox(c) for c in contours(P['isla'])]
ix1 = max(bx[2], max(b[2] for b in ib)); side = max(ix1 - bx[0], bx[3] - bx[1]) + 60
cx = (bx[0] + ix1) / 2; cy = (bx[1] + bx[3]) / 2
VBI = f'{cx - side/2:.0f} {cy - side/2:.0f} {side:.0f} {side:.0f}'
iso = lambda cm, ci: f'<path fill="{cm}" d="{c_shape}"/><path fill="{ci}" fill-rule="evenodd" d="{P["isla"]}"/>'
(OUT / 'isotipo-color.svg').write_text(svg(iso(COL['mar'], COL['isla']), VBI, 'Chiloé Mágico'))
(OUT / 'isotipo-white.svg').write_text(svg(iso('#ffffff', '#ffffff'), VBI, 'Chiloé Mágico'))
(OUT / 'isotipo-ink.svg').write_text(svg(iso('#1d2421', '#1d2421'), VBI, 'Chiloé Mágico'))
# favicon: isotipo sobre círculo blanco
fav = f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{side/2:.0f}" fill="#ffffff"/>' + iso(COL['mar'], COL['isla'])
(OUT / 'favicon.svg').write_text(svg(fav, VBI, 'Chiloé Mágico'))

# logotipo horizontal: isotipo + "Chiloé Mágico" (Delius → trazos) + TURISMO (Montserrat 700)
def text_path(fontfile, text, size, x, y, tracking=0):
    f = TTFont(fontfile); gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f['head'].unitsPerEm; hm = f['hmtx']
    s = size / upm; out = []; pen_x = x
    for ch in text:
        g = cmap.get(ord(ch));
        if not g: continue
        sp = SVGPathPen(gs); tp = TransformPen(sp, (s, 0, 0, -s, pen_x, y)); gs[g].draw(tp); out.append(sp.getCommands())
        pen_x += hm[g][0] * s + tracking
    return ' '.join(out), pen_x - x
FD = '/home/claude/fonts/node_modules/@fontsource'
def woff2ttf(path, out):
    t = TTFont(path); t.flavor = None; t.save(out); return out
delius = woff2ttf(f'{FD}/delius/files/delius-latin-400-normal.woff', '/tmp/delius.ttf')
mont = woff2ttf(f'{FD}/montserrat/files/montserrat-latin-700-normal.woff', '/tmp/mont700.ttf')
dw, wlen = text_path(delius, 'Chiloé Mágico', 200, 0, 0)
tw, tlen = text_path(mont, 'TURISMO', 64, 4, -190, tracking=14)
iso_h = 330
_v = list(map(float, VBI.split())); _sc = iso_h / _v[2]
grp = (f'<g transform="translate(0 -255) scale({_sc:.5f}) translate({-_v[0]:.1f} {-_v[1]:.1f})">' + iso('{M}', '{I}') + '</g>')
def horiz(cm, ci, cv, cr):
    g = grp.replace('{M}', cm).replace('{I}', ci)
    return (g + f'<g transform="translate({iso_h + 30} 0)"><path fill="{cv}" d="{dw}"/><path fill="{cr}" d="{tw}"/></g>')
hvb = f'-10 -270 {iso_h + 30 + wlen + 20:.0f} 340'
(OUT / 'logotipo-h-color.svg').write_text(svg(horiz(COL['mar'], COL['isla'], COL['verde'], COL['rojo']), hvb))
(OUT / 'logotipo-h-white.svg').write_text(svg(horiz('#fff', '#fff', '#fff', '#fff'), hvb))
(OUT / 'logotipo-h-ink.svg').write_text(svg(horiz('#1d2421', '#1d2421', '#1d2421', '#d0342c'), hvb))
print('ok', VB, VBI, hvb)
