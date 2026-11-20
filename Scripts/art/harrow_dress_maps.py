"""Prepare the four 2.6 garment scans for UV projection and real-time cloth shading."""
from pathlib import Path
import numpy as np
from scipy import ndimage as nd
from PIL import Image
root=Path(__file__).resolve().parents[2]/'SourceArt/Textures/Harrow'
plate=Image.open(root/'EdithDressPlate.png').convert('RGBA')
names=('Dogwood','Sunday','Wedding','Poppy')
for i,name in enumerate(names):
    x=i%2*1024;y=i//2*1024
    cell=np.array(plate.crop((x,y,x+1024,y+1024)))
    mask=cell[:,:,3]>135
    ids,count=nd.label(mask);area=np.bincount(ids.ravel());area[0]=0;mask=ids==area.argmax()
    # Keep the neckline and the separation beneath the sleeves; remove tiny alpha pinholes.
    holes=nd.binary_fill_holes(mask)&~mask
    groups,ng=nd.label(holes)
    for g in range(1,ng+1):
        if np.sum(groups==g)<42:mask[groups==g]=True
    ys,xs=np.where(mask);box=(slice(max(0,ys.min()-3),min(1024,ys.max()+4)),slice(max(0,xs.min()-3),min(1024,xs.max()+4)))
    mask=mask[box];rgb=cell[box][:,:,:3]
    outside=~mask;near=nd.distance_transform_edt(outside,return_distances=False,return_indices=True)
    rgb=rgb[near[0],near[1]]
    # Keep the source ratio in the silhouette image. Texture UVs span the normalized crop.
    raw=Image.fromarray(np.dstack((rgb,np.uint8(mask)*255)))
    raw.save(root/('Shape_'+name+'.png'))
    color=Image.fromarray(rgb).resize((512,1024),Image.Resampling.LANCZOS)
    color.save(root/('T_Dress'+name+'.png'))
    lum=np.asarray(color.convert('L'),dtype=float)/255
    fine=nd.gaussian_filter(lum,.8)-nd.gaussian_filter(lum,6.)
    dy,dx=np.gradient(fine)
    yy,xx=np.mgrid[:1024,:512]
    normal=np.stack((-dx*1.4+.024*np.sin(xx*2.1),dy*1.4+.021*np.cos(yy*2.3),np.ones_like(dx)),2)
    normal/=np.linalg.norm(normal,axis=2,keepdims=True)
    Image.fromarray(np.uint8((normal*.5+.5)*255)).save(root/('T_Dress'+name+'_N.png'))
    rough=np.clip((.69 if i==1 else .81)-fine*.30,.43,.93)
    Image.fromarray(np.uint8(rough*255)).save(root/('T_Dress'+name+'_R.png'))
    print(name,raw.size)
