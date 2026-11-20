"""Split the original surface study and author material-response maps and jar labels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
p=Path(__file__).resolve().parents[2]/'SourceArt/Textures/Harrow'
im=Image.open(p/'FridgeSurfaceStudy.png').convert('RGB');w,h=im.size
for i,name in enumerate(('Enamel','Fruit','Wrapper','Preserve')):
    x=i%2*w//2;y=i//2*h//2
    tile=im.crop((x+2,y+2,x+w//2-2,y+h//2-2)).resize((1024,1024),Image.Resampling.LANCZOS)
    tile.save(p/('T_Harrow'+name+'.png'))
    rgb=np.asarray(tile).astype(float)/255
    v=rgb.mean(axis=2)
    if i==0:rough=.27+.63*(1-v)**1.7
    elif i==1:rough=.27+.6*(rgb[:,:,2]/(rgb[:,:,0]+.1)).clip(0,1)
    elif i==2:rough=.55+.32*v
    else:rough=.16+.59*v
    Image.fromarray(np.uint8(rough*255)).save(p/('T_Harrow'+name+'_R.png'))
    smooth=np.asarray(tile.convert('L').filter(ImageFilter.GaussianBlur(1.25))).astype(float)/255
    dx=np.gradient(smooth,axis=1);dy=np.gradient(smooth,axis=0)
    vec=np.stack((-dx*1.6,dy*1.6,np.ones_like(dx)),2);vec/=np.linalg.norm(vec,axis=2,keepdims=True)
    Image.fromarray(np.uint8((vec*.5+.5)*255)).save(p/('T_Harrow'+name+'_N.png'))
for name,line1,line2,line3 in [('PearLabel','HARROW ORCHARD','SPICED PEARS','September 1974'),('PlumLabel','E. HARROW','PLUM BUTTER','Batch 6   /   1981')]:
    ink=(67,45,28);bg=Image.open(p/'T_HarrowWrapper.png').resize((1024,512))
    d=ImageDraw.Draw(bg)
    d.rounded_rectangle((14,12,1010,500),20,outline=ink,width=6);d.rectangle((28,26,996,486),outline=ink,width=2)
    for txt,y,size,font in [(line1,110,54,'georgiab'),(line2,225,85,'georgiab'),(line3,360,49,'georgiai')]:
        try:f=ImageFont.truetype('C:/Windows/Fonts/'+font+'.ttf',size)
        except OSError:f=ImageFont.load_default()
        d.text((512,y),txt,font=f,fill=ink,anchor='mm')
    bg.save(p/('T_Harrow'+name+'.png'))
