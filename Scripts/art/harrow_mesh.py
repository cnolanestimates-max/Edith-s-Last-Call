"""Shared centimetre-space mesh and FBX helpers for the Harrow furniture."""
from pathlib import Path
import math
import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parents[2] / 'SourceArt/Props/HarrowFurniture'
OUT.mkdir(exist_ok=True, parents=True)
parts = []
wood, trim, dark, brass, ivory = 'MI_WoodDark','MI_WoodTrim','MI_WoodRotten','M_PhoneBrass','M_PhoneIvory'
leathers = ['MI_LeatherRed','MI_LeatherGreen','MI_LeatherTan','MI_LeatherBlue','MI_Leather']
def xyz(p):
    return (p[0]/100, -p[1]/100, p[2]/100)
def finish(o,mat):
    o.data.materials.append(bpy.data.materials.get(mat) or bpy.data.materials.new(mat))
    parts.append(o)
    return o
def box(p,size,mat,bevel=.30,yaw=0,roll=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz(p))
    o=bpy.context.object
    o.dimensions=[d/100 for d in size]
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=o.modifiers.new('Worn edge','BEVEL'); b.width=bevel/100; b.segments=2
        bpy.ops.object.modifier_apply(modifier=b.name)
    o.rotation_euler=(math.radians(roll),0,-math.radians(yaw))
    return finish(o,mat)
def rod(a,b,r,mat):
    v,w=Vector(xyz(a)),Vector(xyz(b))
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r/100,depth=(w-v).length,location=(v+w)/2)
    o=bpy.context.object;o.rotation_euler=(w-v).to_track_quat('Z','Y').to_euler()
    return finish(o,mat)
def export(name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:
        # Blender joins UVs by layer name. The game samples UV0 for every material.
        if o.data.uv_layers.active:o.data.uv_layers.active.name='UVMap'
        o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.join()
    o=bpy.context.object
    bpy.context.scene.cursor.location=(0,0,0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    o.name=name
    if name=='SM_EdithWardrobe':
        layer=o.data.uv_layers[0]
        for slot in o.material_slots:
            if not slot.name.startswith('M_Dress'):continue
            uv=[layer.data[i].uv.x for face in o.data.polygons if face.material_index==slot.slot_index for i in face.loop_indices]
            assert uv and max(uv)-min(uv)>.9, 'Missing garment photograph UVs: '+slot.name
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,
                             apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,mesh_smooth_type='FACE')
    bpy.data.objects.remove(o,do_unlink=True)
    parts.clear()
def case(width,height,depth):
    box((-depth/2+1,0,height/2),(2,width,height),dark)
    for side in (-1,1):box((0,side*(width/2-1.5),height/2),(depth,3,height),wood)
    for z in (5,height-2):
        box((0,0,z),(depth+3,width+6,5),trim,.7)
        box((0,0,z+3),(depth+1,width+3,2),wood)

def surface(label,rows,material,uvscale=35,closed=True):
    n=len(rows[0]);verts=[xyz(p) for row in rows for p in row]
    faces=[];tex=[]
    for j in range(len(rows)-1):
        for i in range(n if closed else n-1):
            nxt=(i+1)%n
            faces.append((j*n+i,(j+1)*n+i,(j+1)*n+nxt,j*n+nxt))
            tex.extend(((i/n*1.18,rows[j][i][2]/uvscale),(i/n*1.18,rows[j+1][i][2]/uvscale),
                        ((i+1)/n*1.18,rows[j+1][nxt][2]/uvscale),((i+1)/n*1.18,rows[j][nxt][2]/uvscale)))
    m=bpy.data.meshes.new(label);m.from_pydata(verts,[],faces);m.update()
    uv=m.uv_layers.new(name='Tailored fabric')
    for loop,p in zip(uv.data,tex):loop.uv=p
    obj=bpy.data.objects.new(label,m);bpy.context.collection.objects.link(obj);finish(obj,material)
    for poly in m.polygons:poly.use_smooth=True

def path(points,r,mat):
    # One bevelled curve per seam keeps the silhouette smooth without a cylinder at every stitch.
    data=bpy.data.curves.new('Tailoring',type='CURVE');data.dimensions='3D';data.resolution_u=2
    data.resolution_v=2;data.bevel_resolution=2;data.bevel_depth=r/100
    spline=data.splines.new('POLY');spline.points.add(len(points)-1)
    for point,co in zip(spline.points,points):point.co=(*xyz(co),1)
    obj=bpy.data.objects.new('Piping',data);bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.object.convert(target='MESH');finish(bpy.context.object,mat);bpy.context.object.select_set(False)

def ellipsoid(center,radii,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=xyz(center))
    o=bpy.context.object;o.scale=tuple(v/100 for v in radii)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for f in o.data.polygons:f.use_smooth=True
    finish(o,mat)
