#!/usr/bin/env python3
"""Regenera public/: la carpeta que se publica en Cloudflare Pages.

Copia solo lo que el sitio usa (index.html, las carpetas de páginas, css, js, vendor, assets, brand),
deja fuera todo lo interno y escribe public/_headers con la política de caché.

Falla (código 1, sin dejar un public/ a medias) si:
  - se cuela algo interno (.md, .py, .csv, .json, assets/raw, nombres con "_"),
  - falta un archivo que index.html, css o js referencian,
  - algún archivo pesa más de 25 MB (límite por archivo de Cloudflare Pages).

Uso: python3 tools/publish.py
"""
import pathlib, re, shutil, sys, tempfile
from urllib.parse import unquote

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'public'

INCLUDE_FILES = ['index.html']
PAGE_DIRS = ['tours', 'destinos', 'experiencias', 'paquetes', 'servicios', 'nosotros', 'guia', 'preguntas-frecuentes', 'contacto']
INCLUDE_DIRS = ['css', 'js', 'vendor', 'assets', 'brand'] + PAGE_DIRS

BLOCKED_EXT = {'.md', '.py', '.csv', '.json', '.pyc', '.sh', '.ipynb'}
BLOCKED_DIRS = {'assets/raw'}
BLOCKED_NAMES = {'.DS_Store', 'Thumbs.db', '__pycache__', 'node_modules', '.git'}
MAX_BYTES = 25 * 1024 * 1024

# Caché (antes en vercel.json). Cloudflare Pages lee public/_headers.
HEADERS = """\
/assets/*
  Cache-Control: public, max-age=604800, stale-while-revalidate=86400

/vendor/*
  Cache-Control: public, max-age=2592000, immutable

/brand/*
  Cache-Control: public, max-age=604800

/css/*
  Cache-Control: public, max-age=31536000, immutable

/js/*
  Cache-Control: public, max-age=31536000, immutable
"""


def is_internal(rel: pathlib.PurePosixPath) -> str | None:
    """Devuelve el motivo si la ruta es interna; None si es publicable."""
    s = rel.as_posix()
    if any(s == d or s.startswith(d + '/') for d in BLOCKED_DIRS):
        return 'carpeta interna'
    for part in rel.parts:
        if part in BLOCKED_NAMES:
            return f'nombre bloqueado ({part})'
        if part.startswith('_') and s != '_headers':
            return f'nombre interno ({part})'
        if part.startswith('.'):
            return f'archivo oculto ({part})'
    if rel.suffix.lower() in BLOCKED_EXT:
        return f'extensión interna ({rel.suffix})'
    return None


def copy_tree(stage: pathlib.Path) -> list[str]:
    skipped = []
    for f in INCLUDE_FILES:
        src = ROOT / f
        if not src.is_file():
            sys.exit(f'ERROR: falta {f}')
        shutil.copy2(src, stage / f)
    for d in INCLUDE_DIRS:
        base = ROOT / d
        if not base.is_dir():
            sys.exit(f'ERROR: falta la carpeta {d}/')
        for src in sorted(base.rglob('*')):
            if not src.is_file():
                continue
            rel = pathlib.PurePosixPath(src.relative_to(ROOT).as_posix())
            if is_internal(rel):
                if not rel.as_posix().startswith('assets/raw/'):
                    skipped.append(rel.as_posix())
                continue
            dst = stage / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    (stage / '_headers').write_text(HEADERS)
    return skipped


REF_PATTERNS = [
    re.compile(r'''(?:src|href|poster|data-[\w-]+)\s*=\s*["']([^"']+)["']'''),
    re.compile(r'''srcset\s*=\s*["']([^"']+)["']'''),
    re.compile(r'''url\(\s*["']?([^"')]+)["']?\s*\)'''),
    re.compile(r'''["'`]((?:\.{0,2}/)?(?:assets|brand|css|js|vendor)/[^"'`\s]+?)["'`]'''),
]


def references(text: str, base: pathlib.PurePosixPath) -> set[str]:
    refs = set()
    for pat in REF_PATTERNS:
        for m in pat.finditer(text):
            for piece in m.group(1).split(','):
                url = piece.strip().split(' ')[0].split('#')[0].split('?')[0]
                if not url or re.match(r'^([a-z]+:|//|#|\{|\$)', url, re.I) or '${' in url:
                    continue
                if not re.search(r'\.[a-z][a-z0-9]{1,4}$', url, re.I):
                    continue
                p = (base / unquote(url)).as_posix() if not url.startswith('/') else url.lstrip('/')
                parts = []
                for seg in p.split('/'):
                    if seg in ('', '.'):
                        continue
                    if seg == '..':
                        if parts:
                            parts.pop()
                        continue
                    parts.append(seg)
                refs.add('/'.join(parts))
    return refs


def check(stage: pathlib.Path) -> list[str]:
    errors = []
    files = [p for p in stage.rglob('*') if p.is_file()]
    for p in files:
        rel = pathlib.PurePosixPath(p.relative_to(stage).as_posix())
        why = is_internal(rel)
        if why:
            errors.append(f'interno: {rel} ({why})')
        if p.stat().st_size > MAX_BYTES:
            errors.append(f'pesa más de 25 MB: {rel} ({p.stat().st_size / 1048576:.1f} MB)')
    sources = list(stage.rglob('*.html')) + list((stage / 'css').rglob('*.css')) + list((stage / 'js').rglob('*.js'))
    missing = set()
    for src in sources:
        rel_dir = pathlib.PurePosixPath(src.relative_to(stage).as_posix()).parent
        # en JS las rutas son relativas al documento, no al archivo .js
        base = pathlib.PurePosixPath('.') if src.suffix == '.js' else rel_dir
        if src.suffix == '.html':
            # enlaces a carpetas de páginas (/tours/x/) deben tener su index.html
            for href in re.findall(r'href="(/[^"#?]*/)"', src.read_text(errors='ignore')):
                if not (stage / href.strip('/') / 'index.html').is_file():
                    missing.add(f'falta la página: {href} (enlazada en {src.relative_to(stage)})')
        for ref in references(src.read_text(errors='ignore'), base):
            if not (stage / ref).is_file():
                missing.add(f'falta: {ref} (referenciado en {src.relative_to(stage)})')
    return errors + sorted(missing)


def main():
    with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
        stage = pathlib.Path(tmp) / 'public'
        stage.mkdir()
        skipped = copy_tree(stage)
        errors = check(stage)
        if errors:
            print('publish.py: ERROR, public/ no se modificó', file=sys.stderr)
            for e in errors:
                print('  ' + e, file=sys.stderr)
            sys.exit(1)
        if OUT.exists():
            shutil.rmtree(OUT)
        shutil.move(str(stage), OUT)
    files = [p for p in OUT.rglob('*') if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    big = max(files, key=lambda p: p.stat().st_size)
    print(f'public/ listo: {len(files)} archivos, {total / 1048576:.1f} MB '
          f'(el mayor: {big.relative_to(OUT)}, {big.stat().st_size / 1048576:.1f} MB)')
    print(f'omitidos por internos: {len(skipped)} (más assets/raw completo)')
    for s in skipped:
        print('  - ' + s)


if __name__ == '__main__':
    main()
