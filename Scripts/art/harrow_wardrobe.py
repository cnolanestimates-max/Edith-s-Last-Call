"""A carved wardrobe with four individually patterned, tailored garments on wooden hangers."""
from pathlib import Path
import math
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from harrow_mesh import box, rod, case, export, ellipsoid, wood, trim, brass

def wardrobe():
    from harrow_dress_mesh import garment
    case(177,212,53)
    for z in (9,195,201,207):
        box((0,0,z),(58 if z<200 else 62,182 if z<200 else 186,2.1),trim,.72)
    for y in (-86,86):
        box((26,y,104),(6,7.5,184),trim,.8)
        for off in (-1.8,0,1.8):rod((29.2,y+off,19),(29.2,y+off,188),.52,wood)
    rod((6,-85,175),(6,85,175),1.05,brass)
    for y in (-85,85):ellipsoid((6,y,175),(2.4,1.5,2.4),brass)
    for side in (-1,1):
        yaw=side*72;t=math.radians(yaw)
        def d(x,y,z):return (26+x*math.cos(t)-y*math.sin(t),side*86+x*math.sin(t)+y*math.cos(t),z)
        def dp(x,y,z,dims,material,bevel=.6):box(d(x,y,z),dims,material,bevel,yaw)
        dp(0,-side*37,104,(4,74,185),wood)
        for z,hh in ((55,72),(146,81)):
            dp(2.3,-side*37,z,(1.5,60,hh),trim)
            dp(3.4,-side*37,z,(1.3,54,hh-6),wood)
            for off in (-1,1):
                dp(4.2,-side*37+off*25,z,(1,1.3,hh-8),trim,.35)
        dp(3,-side*66,103,(1.4,4.8,13),brass)
        ellipsoid(d(5,-side*66,105),(2.5,1.4,2.4),brass)
        for z in (37,104,175):dp(0,0,z,(5,3.3,9),brass)
    garment('Dogwood','M_HarrowCalico',-64,63,166,43,-6,0)
    garment('Sunday','M_HarrowBurgundy',-22,53,165,39,8,1)
    garment('Wedding','M_HarrowBrocade',21,29,166,45,-4,2)
    garment('Poppy','M_HarrowGingham',64,70,164,42,7,3)
    export('SM_EdithWardrobe')

if __name__=='__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True)
    wardrobe()
