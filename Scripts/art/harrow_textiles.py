"""Paint four tileable period fabric prints and their common woven normal map."""
from pathlib import Path
import math
import random
import numpy as np
from PIL import Image, ImageDraw

out=Path(__file__).resolve().parents[2]/'SourceArt/Textures/Harrow'
out.mkdir(parents=True,exist_ok=True)
s=1024
y,x=np.mgrid[:s,:s]
rng=np.random.default_rng(1967)
# Warp and weft cross under one another on alternate intersections.
h=(np.sin(2*np.pi*x/8)*.56+np.sin(2*np.pi*y/8)*.37+
   .31*np.sin(2*np.pi*x/16)*np.sin(2*np.pi*y/16))
dx=(np.roll(h,-1,1)-np.roll(h,1,1))*.22
dy=(np.roll(h,-1,0)-np.roll(h,1,0))*.22
normal=np.stack((-dx,dy,np.ones_like(dx)),2)
normal/=np.linalg.norm(normal,axis=2,keepdims=True)
Image.fromarray(np.uint8((normal*.5+.5)*255)).save(out/'T_HarrowWeave_N.png')
def petal(draw,cx,cy,r,angle,color):
    a=math.radians(angle);points=[]
    for k in range(28):
        t=k*math.tau/28
        lx=r*(1+math.cos(t))/2;ly=r*.29*math.sin(t)*(1+.4*math.cos(t))
        points.append((cx+lx*math.cos(a)-ly*math.sin(a),cy+lx*math.sin(a)+ly*math.cos(a)))
    draw.polygon(points, fill=color)
def flower(d,cx,cy,r,dark,light):
    for k in range(5):petal(d,cx,cy,r,72*k-80,dark)
    for k in range(5):petal(d,cx,cy,r*.61,72*k-74,light)
    d.ellipse((cx-3,cy-3,cx+3,cy+3),fill=(170,142,80))
for kind,bg in [('Calico',(62,90,109)),('Burgundy',(113,50,62)),('Brocade',(193,178,140)),('Gingham',(123,148,130))]:
    im=Image.new('RGB',(s,s),bg);d=ImageDraw.Draw(im);r=random.Random(1954)
    if kind=='Calico':
        for j in range(-1,9):
            for i in range(-1,9):
                cx=i*128+(j%2)*64+25;cy=j*128+48
                d.line([(cx-14,cy+26),(cx-4,cy+6),(cx+12,cy-21)],fill=(94,116,92),width=3)
                petal(d,cx-5,cy+12,15,190,(147,154,116));petal(d,cx+6,cy-9,15,-4,(139,150,110))
                flower(d,cx,cy,17,(171,146,117),(194,175,144));flower(d,cx+15,cy-22,9,(176,124,109),(191,153,131))
    elif kind in ('Burgundy','Brocade'):
        ink=(134,65,72) if kind=='Burgundy' else (213,200,162)
        shadow=(93,40,54) if kind=='Burgundy' else (172,153,118)
        for j in range(-1,9):
            for i in range(-1,9):
                cx=i*128+64*(j%2);cy=j*128
                for side in (-1,1):
                    pts=[(cx+side*(k*.39+6*math.sin(k*.08)),cy+k-42) for k in range(85)]
                    d.line(pts,fill=shadow,width=2)
                    for off in (0,13,27):petal(d,cx+side*(9+off*.34),cy+off,18,(-40 if side==1 else 220),ink)
                petal(d,cx,cy-5,19,-90,ink)
    else:
        pix=np.array(im).astype(float)
        warp=((x//28)%2+(y//28)%2)*14+((x%28<3)|(y%28<3))*8
        pix-=warp[:,:,None];im=Image.fromarray(np.uint8(pix))
    a=np.array(im).astype(float)
    slub=1+.045*h+.019*np.sin(y*math.tau/s*8)+.014*np.cos((x+y)*math.tau/s*5)
    a=a*slub[:,:,None]+rng.normal(0,1.7,(s,s,1))
    Image.fromarray(np.uint8(np.clip(a,0,255))).save(out/('T_Harrow'+kind+'.png'),optimize=True)
