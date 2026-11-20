"""Model the pierced, eight-sided brass shade in centimetres, with its origin at the hook."""
from pathlib import Path
from math import sin, cos, pi, floor
import bpy
from mathutils import Vector

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
vertices, faces, slots = [], [], []
BRASS, PATINA, IRON, BULB = range(4)


def grid(rings, slot):
    start = len(vertices)
    count = len(rings[0])
    for ring in rings:
        vertices.extend(tuple(v * .01) for v in map(Vector, ring))
    for j in range(len(rings)-1):
        for i in range(count):
            a = start + j*count+i
            b = start + j*count+(i+1)%count
            faces.append((a,b,b+count,a+count))
            slots.append(slot)


def tube(points, radius, slot, sides=5):
    pts = list(map(Vector,points))
    loops = []
    for i,p in enumerate(pts):
        axis = (pts[min(i+1,len(pts)-1)] - pts[max(0,i-1)]).normalized()
        guide = Vector((0,0,1)) if abs(axis.z)<.9 else Vector((1,0,0))
        a = axis.cross(guide).normalized()
        b = axis.cross(a)
        loops.append([p + radius*(a*cos(2*pi*k/sides)+b*sin(2*pi*k/sides)) for k in range(sides)])
    grid(loops,slot)


def lathe(profile, slot, sides=32):
    grid([[(r*cos(2*pi*i/sides),r*sin(2*pi*i/sides),z) for i in range(sides)] for z,r in profile],slot)


# Woven flex, turned fittings, suspension ring and socket.
lathe([(0,.48),(-47,.48),(-48,1.4),(-51,1.1)],IRON)
for z in (-47,-51,-60,-61):
    lathe([(z+.6,.2),(z+.45,1.8),(z-.35,1.8),(z-.6,.2)],BRASS)
tube([(0,2.4*cos(i*pi/16),-55+3.7*sin(i*pi/16)) for i in range(33)],.45,BRASS,8)
profile=[(-60,1.4),(-64,4.6),(-67,8.0),(-75,13.5),(-84,17.7),(-95,18.4),(-106,15.8),(-113,10.5),(-117,5.2),(-120,1.5)]
def panel(k,u,v):
    s=min(len(profile)-1.00001,max(0,v*(len(profile)-1)))
    n=floor(s)
    z=profile[n][0]+(profile[n+1][0]-profile[n][0])*(s-n)
    r=profile[n][1]+(profile[n+1][1]-profile[n][1])*(s-n)
    a,b=k*pi/4,(k+1)*pi/4
    return Vector((r*((1-u)*cos(a)+u*cos(b)),r*((1-u)*sin(a)+u*sin(b)),z))
for k in range(8):
    tube([panel(k,0,i/36) for i in range(37)],.57,BRASS,7)
    for v in (.18,.32,.69,.84):
        tube([panel(k,u/8,v) for u in range(9)],.36,BRASS)
    # Each cell is open. Interwoven lancets and the raised central rosette catch light in silhouette.
    for row in range(9):
        low=.10+row*.092
        for col in range(3):
            mid=(col+.5)/3
            tube([panel(k,mid+.152*sin(t*pi/12),low+.046*(1-cos(t*pi/12))) for t in range(25)],.18,PATINA)
    for side in (-1,1):
        tube([panel(k,.5+side*.45*sin(pi*t/40),.23+.55*t/40) for t in range(41)],.34,BRASS)
    for petal in range(6):
        a=petal*pi/3
        tube([panel(k,.5+.117*cos(a)+.115*cos(t*pi/12),.51+.034*sin(a)+.031*sin(t*pi/12)) for t in range(25)],.27,BRASS)
lathe([(-59,.15),(-60.7,2.7),(-64,4.85),(-65,4.5)],BRASS)
lathe([(-116,5.6),(-118.5,4.8),(-119.5,2.2),(-121,1.3),(-123,2.0),(-125,.2)],BRASS)
lathe([(-66,1.1),(-80,1.1),(-82,2.5),(-84,2.4)],IRON)
lathe([(-83,1.2),(-85,2.2),(-88,3.25),(-91,3.1),(-94,1.9),(-95,.1)],BULB)
mesh=bpy.data.meshes.new('Pierced brass and woven cord')
mesh.from_pydata(vertices,[],faces)
mesh.update()
obj=bpy.data.objects.new('SM_HallPendant',mesh)
bpy.context.collection.objects.link(obj)
for name in ('M_PhoneBrass','M_BrassOld','M_Black','M_GlowBulb'):
    mesh.materials.append(bpy.data.materials.new(name))
for face,slot in zip(mesh.polygons,slots):
    face.material_index=slot
    face.use_smooth=True
obj.select_set(True)
bpy.context.view_layer.objects.active=obj
out=Path(__file__).resolve().parents[2]/'SourceArt/Props/HarrowFurniture/SM_HallPendant.fbx'
bpy.ops.export_scene.fbx(filepath=str(out),use_selection=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,mesh_smooth_type='FACE')
