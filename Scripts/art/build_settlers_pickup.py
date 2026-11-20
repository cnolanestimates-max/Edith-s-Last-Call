"""Blender authoring source. Coordinates are game centimetres: +X to the top of the book, +Y to its fore edge."""
import math
from pathlib import Path
import bpy
from mathutils import Vector, Matrix

root=Path(__file__).resolve().parents[2]
out=root/'SourceArt/Props/HarrowFurniture'
bpy.ops.wm.read_factory_settings(use_empty=True)

def pt(x,y,z): return Vector((x,-y,z))*.01
def material(obj,name):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    obj.data.materials.append(mat)

def board(center,dimensions,finish,rounding=.12):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pt(*center))
    obj=bpy.context.object
    obj.dimensions=Vector(dimensions)*.01
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bevel=obj.modifiers.new('Rounded edges','BEVEL')
    bevel.width=rounding*.01
    bevel.segments=3
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    obj.modifiers.new('Face normals','WEIGHTED_NORMAL')
    material(obj,finish)
    return obj

def lettering(words,x,y,z,size,finish):
    bpy.ops.object.text_add(location=pt(x,y,z), rotation=(0,0,-math.pi/2))
    obj=bpy.context.object
    obj.data.body=words
    obj.data.align_x=obj.data.align_y='CENTER'
    obj.data.size=size*.01
    obj.data.extrude=.00014
    material(obj,finish)
    bpy.ops.object.convert(target='MESH')

def printed_leaf(x0,x1,y0,y1,z,inside_cover=False):
    corners=[(x0,y0),(x0,y1),(x1,y1),(x1,y0)]
    if inside_cover: corners.reverse()
    mesh=bpy.data.meshes.new('Printed leaf')
    mesh.from_pydata([pt(x,y,z) for x,y in corners],[],[(0,1,2,3)])
    uv=mesh.uv_layers.new()
    for i,(x,y) in enumerate(corners):
        u=(15.36-y)/15. if inside_cover else 1.+(y+7.6)/15.2
        uv.data[i].uv=(u*.5,(x+11.15)/22.30)
    obj=bpy.data.objects.new('Print',mesh)
    bpy.context.collection.objects.link(obj)
    material(obj,'M_SettlersLeaves')

def export(name):
    meshes=[obj for obj in bpy.context.scene.objects if obj.type=='MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes: obj.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0]
    bpy.ops.object.join()
    obj=bpy.context.object
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    obj.name='SM_Settlers'+name
    bpy.ops.export_scene.fbx(filepath=str(out/(obj.name+'.fbx')),use_selection=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,mesh_smooth_type='FACE')
    bpy.data.objects.remove(obj,do_unlink=True)

leather='MI_LeatherOld'
paper='MI_PaperOld'
gilt='MI_BrassOld'
board((0,0,.28),(23,16,.56),leather)
# A hollow cut through the block of pages, with uneven signatures visible at the fore edge.
board((0,0,.63),(22.25,15.25,.35),'MI_Parchment')
for i in range(9):
    z=.83+i*.38
    w=15.2+.14*math.sin(i*2.4)
    for x in (-8.65,8.65): board((x,0,z),(5.0,w,.39),paper,.055)
    for y in (-5.4,5.4): board((0,y,z),(12.4,4.48,.39),paper,.055)
board((0,-7.78,2.22),(23,.67,4.2),leather,.24)
for x in (-9,-6.8,6.8,9): board((x,-7.95,2.18),(.64,.64,4.32),leather,.22)
for a,b in [(-11.05,-6.26),(6.26,11.05)]:
    printed_leaf(a,b,-7.49,7.49,4.075)
for a,b in [(-7.49,-3.25),(3.25,7.49)]:
    printed_leaf(-6.26,6.26,a,b,4.075)
export('Pages')
# The cover mesh is authored about its long hinge, not its centre.
board((0,7.86,.23),(23,16,.53),leather)
board((0,7.86,-.06),(22.3,15.0,.10),'MI_Parchment')
printed_leaf(-11.06,11.06,.45,15.27,-.12,True)
for off in (.78,1.02):
    for y in (off,15.72-off): board((0,y,.511),(22.2-2*off,.055,.035),gilt,.012)
    for x in (-11.1+off,11.1-off): board((x,7.86,.511),(.055,15.72-2*off,.035),gilt,.012)
for words,x,size in [('CUSTOMS',3.5,1.85),('OF THE',1.6,.80),('FIRST SETTLERS',-.2,1.28),('COUNTY HISTORIES',-6.6,.63)]:
    lettering(words,x,7.86,.52,size,gilt)
export('Cover')

# Smooth ring lofts follow the knuckles and the cuff. A narrow, curved thumb rests on top of the book;
# all four fingers wrap the fore edge below it.
def loft(path,finish):
    points=[pt(*p[:3]) for p in path]
    vertices=[]; faces=[]; sides=12
    width=Vector((0,1,0))
    for i,(row,p) in enumerate(zip(path,points)):
        tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
        # Parallel transport the cross section so curled fingertips keep a continuous silhouette.
        width=(width-tangent*width.dot(tangent)).normalized()
        if width.length<.5: width=tangent.cross(Vector((0,0,1))).normalized()
        height=tangent.cross(width).normalized()
        for j in range(sides):
            angle=2*math.pi*j/sides
            vertices.append(p+.01*(row[3]*math.cos(angle)*width+row[4]*math.sin(angle)*height))
        if i:
            for j in range(sides):
                a=(i-1)*sides+j;b=(i-1)*sides+(j+1)%sides
                faces.append((a,b,b+sides,a+sides))
    faces.append(tuple(reversed(range(sides))))
    faces.append(tuple(range(len(vertices)-sides,len(vertices))))
    mesh=bpy.data.meshes.new('Leather panels'); mesh.from_pydata(vertices,[],faces)
    obj=bpy.data.objects.new('Panel',mesh); bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('Soft contours','SUBSURF');mod.levels=2
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for face in obj.data.polygons: face.use_smooth=True
    material(obj,finish)

loft([(-52,34,13,5.8,5.3),(-49,32,13,5.8,5.3),(-37,24,11.5,5.6,5.1),(-31,20,9.5,5.6,4.8),(-30,19.8,9.4,5.85,5),(-28.7,19,9,5.35,4.65),(-19,14,6.8,4.0,3.65),(-17,13,6,4,3.6)],'MI_ClothDark')
loft([(-20,14.5,7.2,4.5,4),(-19.6,14.2,7,4.65,4.1),(-17.6,13,6.1,4.45,3.8),(-17.1,12.7,6,4.15,3.65)],leather)
black='MI_LeatherBlack'
loft([(-19,14.1,7,3.7,3.1),(-16,12.7,5.8,3.6,3.0),(-13,12.0,4.6,4.0,2.7),(-9,12.1,3.3,4.5,2.1),(-6.4,11.8,2.8,4.2,1.8),(-5.2,11.5,2.5,3.6,1.45)],black)
# Slightly different lengths and flexion for each finger.
for n in range(4):
    d=n*1.86
    x=-5.0-n*.70
    y=9.05+d
    reach=4.1-.48*abs(n-1)
    thick=1.02-.095*n
    loft([(x-2,y,3.2,thick,thick),(x,y,2.7,thick,thick),(x+2,y+.15,2.2,thick,thick),
          (x+reach,y-.6,1.0,thick*.91,thick*.91),(x+reach+.55,y-2.4,.35,thick*.84,thick*.84),
          (x+reach+.2,y-3.5,.55,thick*.68,thick*.72),(x+reach,y-4,.67,.25,.25)],black)
loft([(-13,10,5.3,1.9,1.6),(-10.8,8.7,5.6,1.75,1.5),(-8.4,7.25,5.8,1.40,1.28),
      (-6.2,6.35,5.65,1.22,1.18),(-4.45,5.8,5.1,1.18,.90),(-3.7,5.6,4.9,.76,.60),(-3.45,5.6,4.9,.23,.25)],black)
export('Glove')
