"""Print the two facing leaves of Walter's hollow book as one texture atlas."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

root=Path(__file__).resolve().parents[2]
rng=np.random.default_rng(1893)
size=1024
h,w=size,size
y,x=np.mgrid[0:h,0:w]
u=(x%(w//2))/(w//2-1)
v=y/(h-1)
def noise(cols,rows):
    tile=Image.fromarray(rng.uniform(0,255,(rows,cols)).astype('uint8')).resize((w,h),Image.Resampling.BICUBIC)
    return np.asarray(tile)/255-.5
edge=np.minimum(np.minimum(u,1-u),np.minimum(v,1-v))
wear=27*np.exp(-13*edge)+12*np.exp(-36*edge)
grain=13*noise(16,14)+18*noise(5,5)+8*noise(80,65)+rng.normal(0,2,(h,w))
for _ in range(40):
    cx,cy=rng.uniform(0,w),rng.uniform(0,h)
    radius=rng.uniform(6,40)
    grain-=rng.uniform(3,18)*np.exp(-((x-cx)**2+(y-cy)**2)/(radius**2))
base=np.array([202.,183.,143.])+grain[:,:,None]-wear[:,:,None]*[.7,.92,1.00]
atlas=Image.fromarray(np.uint8(np.clip(base,0,255)))
draw=ImageDraw.Draw(atlas)
fontpath=Path('C:/Windows/Fonts')
def text(pos,words,px=20,face='GARA.TTF',anchor='mm',color=(68,51,31)):
    draw.text(pos,words,font=ImageFont.truetype(str(fontpath/face),px),fill=color,anchor=anchor)
# The inside front board carries an engraved private-library plate.
for box in [(82,276,430,625),(88,282,424,619),(95,289,417,612)]:
    draw.rectangle(box,outline=(113,86,52),width=2)
text((256,335),'EX   LIBRIS',30)
draw.line((146,365,366,365), fill=(105,80,49),width=2)
text((256,427),'Walter Harrow',43,'GARAIT.TTF')
text((256,495),'Harrow Family Library',23)
text((256,558),'County Histories',20,'GARAIT.TTF')
# Printed matter across the facing leaf is physically cut away at the key recess.
text((768,104),'CHAPTER   XIV',20)
text((768,158),'Household Customs',36,'GARAIT.TTF')
draw.line((597,197,938,197), fill=(99,76,44),width=2)
lines=['In the first houses of the settlement it was','the custom to leave a lamp by the window',
       'until the last traveller had come in. In winter','a fire was kept upon the hearth, and the',
       'family would gather round it after supper.','The road lay well below the old house,',
       'where the sound of wheels carried far at','night. So it was written in the household',
       'accounts, in a hand now scarcely legible.']
for i in range(22):
    text((561,241+i*29),lines[i%len(lines)],23,anchor='lm')
text((768,932),'—  147  —',21)
atlas.save(root/'SourceArt/Props/HarrowFurniture/T_SettlersLeaves.png')
