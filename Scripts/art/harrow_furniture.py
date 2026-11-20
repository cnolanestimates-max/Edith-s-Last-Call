"""Build the desks, piano, books and fixtures. The wardrobe has its own Blender scene generator."""
from pathlib import Path
import random
import sys
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from harrow_mesh import box, rod, case, export, wood, trim, dark, brass, ivory, leathers, xyz, finish
import math
bpy.ops.wm.read_factory_settings(use_empty=True)
rng = random.Random(1967)

for variant in range(2):
    case(123,191,35)
    for shelf in range(5):
        base=11+shelf*34
        box((0,0,base),(36,118,2.8),trim)
        y=-56
        while y<48:
            thick=rng.uniform(3.4,7.5);h=rng.uniform(21,30);x=rng.uniform(4,7);c=rng.choice(leathers)
            box((x-3,y+thick/2,base+2+h/2),(19,thick-.5,h-.6),'MI_PaperOld',0)
            box((x+7,y+thick/2,base+2+h/2),(1.8,thick,h),c,.32)
            for off in (-1,1):box((x-2,y+thick/2+off*thick*.47,base+2+h/2),(20,.42,h),c,0)
            for rz in (.19,.80):box((x+8,y+thick/2,base+2+h*rz),(.36,thick-.45,.55),brass,.08)
            if rng.random()<.27:box((x+8,y+thick/2,base+h*.57),(.35,thick*.65,3),'MI_PaperOld',0)
            y+=thick+rng.uniform(.1,1.5)
    export('SM_DenBooks'+str(variant+1))

# Upright with an actual gap in its playable keyboard and space beneath for the drawer.
case(151,131,40)
box((18,0,103),(5,142,46),wood,.9)
for y in (-50,0,50):
    box((21,y,107),(2,43,32),trim,1)
    box((22.4,y,107),(1.4,37,26),wood,.8)
box((28,0,80),(26,146,4),trim,.55)
for y in (-71,71):
    box((29,y,83),(28,5,10),wood,.9)
    rod((35,y,10),(35,y,77),3.1,trim)
for y in (-6,0,6):box((25,y,7),(12,2.3,2),brass,.6)
for key in range(52):
    y=(key-25.5)*2.54
    if key!=25:box((32,y,84),(21,2.42,2.6),ivory,.18)
    if key%7 not in (1,4) and key<51:box((26,y+1.27,86.3),(12,1.45,2.1),'MI_Iron',.22)
box((22,0,90),(6,139,3),trim)
box((21,0,31),(4,142,38),wood)
for y in (-48,48):box((22,y,67),(6,46,15),wood,.6)
export('SM_HarrowUpright')
box((0,0,0),(21,2.42,2.6),ivory,.18)
box((-9,0,1.65),(2,2.1,.8),dark,.1)
export('SM_LoosePianoKey')
box((0,0,0),(26,40,1.8),wood)
for y in (-19,19):box((0,y,3),(26,2,6),wood)
box((-12,0,3),(2,39,6),wood)
box((12,0,4),(2.6,44,10),trim,.7)
rod((15,-5,4),(15,5,4),1,brass)
export('SM_PianoDrawer')
# Hollow rolled-rim bathtub and a separate elliptical surface which can drain away.
def ovalmesh(name,rings,material,cap=True):
    vertices=[];faces=[];n=64
    for rx,ry,z in rings:
        for i in range(n):
            angle=-2*math.pi*i/n
            vertices.append(xyz((rx*math.cos(angle),ry*math.sin(angle),z)))
    for k in range(len(rings)-1):
        for i in range(n):
            a=k*n+i;b=k*n+(i+1)%n;faces.append((a,b,b+n,a+n))
    if cap:faces.append(tuple(range(n*(len(rings)-1),n*len(rings))))
    m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],faces);m.update()
    o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);finish(o,material)
    for f in m.polygons:f.use_smooth=len(f.vertices)==4
ovalmesh('Cast iron enamel',[(59,25,11),(73,34,24),(90,43,63),(91,44,66),(87,40,68),(83,37,65),(75,33,46),(58,24,20),(51,20,17)],enamel)
for x in (-51,51):
    for y in (-22,22):rod((x,y,3),(x*.94,y*.94,18),3.5,'MI_Rust')
for y in (-8,8):
    rod((-72,y,50),(-72,y,73),1.3,brass)
    rod((-73,y-3,73),(-73,y+3,73),1.1,ivory)
rod((-72,0,65),(-58,0,65),1.6,brass)
rod((-58,0,65),(-58,0,61),1.6,brass)
export('SM_HarrowBath')
ovalmesh('Stagnant water',[(77,34,0),(77,34,.6)],'M_KitchenTar')
export('SM_BathWater')
# Kneehole writing desk. The centre drawer is a separate prop.
box((0,0,74),(71,140,4),trim,1)
box((-27,0,62),(3,128,18),wood)
for y in (-53,53):
    for x in (-25,25):box((x,y,34),(6,6,64),wood,1)
    box((0,y,62),(58,34,21),wood)
    box((30,y,63),(3,31,16),trim,.55)
    rod((33,y-3,64),(33,y+3,64),.8,brass)
box((4,0,54),(48,52,2),dark)
export('SM_HarrowDesk')
