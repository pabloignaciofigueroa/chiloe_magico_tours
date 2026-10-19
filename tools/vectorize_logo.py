"""Traza el logo de Chiloé Mágico desde su afiche [DEST-H7_002] por capas de color → SVG."""
import numpy as np, potrace
from PIL import Image, ImageFilter
from skimage import color, morphology
SRC='assets/raw/ig/hl/H7_002.jpg'; BOX=(36,150,418,412); S=5
im=Image.open(SRC).convert('RGB').crop(BOX); im=im.resize((im.width*S,im.height*S),Image.LANCZOS).filter(ImageFilter.MedianFilter(5))
a=np.asarray(im)/255.0; lab=color.rgb2lab(a)
refs={'mar':(0x18,0x8f,0xc0),'verde':(0x16,0x82,0x56),'rojo':(0xc8,0x36,0x2f),'isla':(0x0e,0x76,0x6c)}
L=lab[...,0]; C=np.hypot(lab[...,1],lab[...,2])
labs={k:color.rgb2lab(np.array([[v]])/255.0)[0,0] for k,v in refs.items()}
d=np.stack([np.linalg.norm(lab-labs[k],axis=-1) for k in refs],-1)
lbl=d.argmin(-1); ok=(d.min(-1)<28)&(C>18)
masks={}
for i,k in enumerate(refs):
    m=ok&(lbl==i); m=morphology.remove_small_objects(m,max_size=60*S); m=morphology.binary_closing(m,morphology.disk(2))
    masks[k]=m
def trace(m):
    bm=potrace.Bitmap(~m); p=bm.trace(turdsize=40,alphamax=1.0,opttolerance=0.4)
    out=[]
    for c in p:
        s=c.start_point; seg=[f'M{s.x:.1f},{s.y:.1f}']
        for x in c.segments:
            if x.is_corner: seg.append(f'L{x.c.x:.1f},{x.c.y:.1f}L{x.end_point.x:.1f},{x.end_point.y:.1f}')
            else: seg.append(f'C{x.c1.x:.1f},{x.c1.y:.1f} {x.c2.x:.1f},{x.c2.y:.1f} {x.end_point.x:.1f},{x.end_point.y:.1f}')
        out.append(''.join(seg)+'Z')
    return ' '.join(out)
W,H=im.size
fills={'mar':'#1a8fc4','verde':'#17853f','rojo':'#d0342c','isla':'#0e766c'}
paths={k:trace(m) for k,m in masks.items()}
import json; json.dump({'W':W,'H':H,'paths':paths},open('brand/logo/_trace.json','w'))
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">']+[f'<path fill="{fills[k]}" fill-rule="evenodd" d="{paths[k]}"/>' for k in fills]+['</svg>']
open('brand/logo/_trace_full.svg','w').write('\n'.join(svg))
print(W,H,{k:int(m.sum()) for k,m in masks.items()})
