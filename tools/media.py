"""Fase 7: genera WebP 800/1800 + LQIP (assets/img/meta.json) y videos MP4/WebM + póster."""
import json, base64, io, subprocess, pathlib
from PIL import Image, ImageOps
ROOT = pathlib.Path(__file__).resolve().parent.parent
M = json.load(open(ROOT / 'content/media.json'))
RAW = ROOT / 'assets/raw/ig'; IMG = ROOT / 'assets/img'; VID = ROOT / 'assets/video'
IMG.mkdir(parents=True, exist_ok=True); VID.mkdir(parents=True, exist_ok=True)
meta = {}
for key, (fname, alt) in M['images'].items():
    im = ImageOps.exif_transpose(Image.open(RAW / fname)).convert('RGB')
    w, h = im.size
    for size in (800, 1800):
        out = IMG / f'{key}-{size}.webp'
        if size == 1800 and max(w, h) < 1100:
            continue
        c = im.copy(); c.thumbnail((size, size), Image.LANCZOS)
        c.save(out, 'WEBP', quality=78 if size == 1800 else 74, method=6)
    lq = im.copy(); lq.thumbnail((24, 24)); b = io.BytesIO(); lq.save(b, 'WEBP', quality=40)
    big = (IMG / f'{key}-1800.webp').exists()
    t = im.copy(); t.thumbnail((1800 if big else 800,) * 2)
    meta[key] = {'w': t.width, 'h': t.height, 'big': big, 'alt': alt, 'src': fname,
                 'lqip': 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()}
json.dump(meta, open(IMG / 'meta.json', 'w'), ensure_ascii=False, indent=1)
for key, (fname, start, end, alt) in M['videos'].items():
    src = str(RAW / fname); dur = str(end - start)
    vf = 'scale=600:-2,fps=30'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start), '-t', dur, '-i', src, '-an', '-vf', vf, '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-crf', '29', '-preset', 'slow', '-movflags', '+faststart', str(VID / f'{key}.mp4')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start), '-t', dur, '-i', src, '-an', '-vf', vf, '-c:v', 'libvpx-vp9', '-b:v', '0', '-crf', '43', '-row-mt', '1', '-deadline', 'good', str(VID / f'{key}.webm')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(start + 0.5), '-i', src, '-frames:v', '1', '-vf', 'scale=720:-2', '-q:v', '4', str(VID / f'{key}-poster.jpg')], check=True)
    meta.setdefault('_videos', {})[key] = {'alt': alt}
json.dump(meta, open(IMG / 'meta.json', 'w'), ensure_ascii=False, indent=1)
print(len(meta) - 1, 'imágenes')
