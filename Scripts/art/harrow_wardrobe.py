"""A carved wardrobe with four individually patterned, tailored garments on wooden hangers."""
from pathlib import Path
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from harrow_mesh import rod, export, ellipsoid, brass
from harrow_cabinet import build_case

def wardrobe():
    from harrow_dress_mesh import garment
    build_case()
    rod((6,-85,175),(6,85,175),1.05,brass)
    for y in (-85,85):ellipsoid((6,y,175),(2.4,1.5,2.4),brass)
    garment('Dogwood','M_HarrowCalico',-64,63,166,43,-6,0)
    garment('Sunday','M_HarrowBurgundy',-22,53,165,39,8,1)
    garment('Wedding','M_HarrowBrocade',21,29,166,45,-4,2)
    garment('Poppy','M_HarrowGingham',64,70,164,42,7,3)
    export('SM_EdithWardrobe')

if __name__=='__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True)
    wardrobe()
