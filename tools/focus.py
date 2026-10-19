"""Encuadre automático: busca rostros (OpenCV) y, si no hay, la zona más llamativa (saliencia).
Guarda en assets/img/meta.json el punto focal 'pos' de cada imagen para object-position."""
import json, pathlib, cv2, numpy as np
cv2.setLogLevel(0) if hasattr(cv2, 'setLogLevel') else None
ROOT = pathlib.Path(__file__).resolve().parent.parent
M = json.loads((ROOT / 'assets/img/meta.json').read_text())
YUNET = str(ROOT / 'tools/models/yunet.onnx')
def saliency(im):
    g = cv2.cvtColor(cv2.resize(im, (64, 64)), cv2.COLOR_BGR2GRAY).astype(float)
    f = np.fft.fft2(g); la = np.log(np.abs(f) + 1e-9); ph = np.angle(f)
    sr = la - cv2.blur(la, (3, 3))
    s = np.abs(np.fft.ifft2(np.exp(sr + 1j * ph))) ** 2
    s = cv2.GaussianBlur(s, (0, 0), 3)
    return cv2.resize(s / s.max(), (im.shape[1], im.shape[0]))
for k, m in M.items():
    if k.startswith('_'): continue
    im = cv2.imread(str(ROOT / f'assets/img/{k}-800.webp'))
    if im is None: continue
    h, w = im.shape[:2]
    det = cv2.FaceDetectorYN.create(YUNET, '', (w, h), 0.75, 0.3, 5000)
    _, faces = det.detect(im)
    boxes = [] if faces is None else [f[:4].astype(int) for f in faces if f[2] > w * .02]
    kind = 'rostros'
    if len(boxes):
        b = np.array(boxes); x0, y0 = b[:, 0].min(), b[:, 1].min(); x1, y1 = (b[:, 0] + b[:, 2]).max(), (b[:, 1] + b[:, 3]).max()
        cx = (x0 + x1) / 2 / w
        # ventana horizontal típica muestra ~la mitad de la foto: arrancarla un poco sobre las cabezas
        cy = min(max(2 * (y0 / h - .07), 0), 1)
    else:
        cx, cy = .5, .42; kind = 'centro'
    cx = min(max(cx, .12), .88)
    m['pos'] = f'{cx*100:.0f}% {cy*100:.0f}%'; m['pos_src'] = kind
(ROOT / 'assets/img/meta.json').write_text(json.dumps(M, ensure_ascii=False, indent=1))
print({k: (m.get('pos'), m.get('pos_src')) for k, m in M.items() if not k.startswith('_')})
