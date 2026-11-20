"""Folded bath letter. The wax, flap and address are modelled on the pickup."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import harrow_mesh as m

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
paper='MI_PaperOld'
m.box((0,0,.10),(18,10,.20),paper,.07)
for a,b in [((-8.7,-4.6,.22),(0,1.8,.22)),((0,1.8,.22),(8.7,-4.6,.22))]:
    m.rod(a,b,.055,'MI_LeatherTan')
m.ellipsoid((0,1.55,.3),(1.0,.84,.30),'MI_LeatherRed')
# A short address on the folded flap, legible as handwriting close to the paper.
font=bpy.data.curves.new('Address','FONT')
font.body='Walter';font.size=.021;font.shear=.21
o=bpy.data.objects.new('Address',font)
bpy.context.collection.objects.link(o)
o.location=m.xyz((-3,2.5,.23))
bpy.context.view_layer.objects.active=o
o.select_set(True)
bpy.ops.object.convert(target='MESH')
m.finish(bpy.context.object,'MI_WoodDark')
m.export('SM_BathLetter')
