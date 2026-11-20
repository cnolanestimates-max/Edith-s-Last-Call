"""Split the existing bathroom chair at its measured axles. Run in Blender after export_source()."""
from collections import defaultdict
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

root = Path(__file__).resolve().parents[2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(root/'Saved/BathChairSource.fbx'))
chair = next(obj for obj in bpy.context.scene.objects if obj.type=='MESH')
mesh = chair.data
positions = [tuple(round(v*100,3) for v in chair.matrix_world @ vert.co) for vert in mesh.vertices]

# UV and normal seams split vertices. Join matching positions within a material for classification only.
parents = {}
def root_of(v):
    while parents[v]!=v:
        parents[v]=parents[parents[v]]
        v=parents[v]
    return v

for face in mesh.polygons:
    keys=[(positions[i],face.material_index) for i in face.vertices]
    for k in keys: parents.setdefault(k,k)
    for k in keys[1:]: parents[root_of(k)]=root_of(keys[0])
islands=defaultdict(list)
for face in mesh.polygons:
    islands[root_of((positions[face.vertices[0]],face.material_index))].append(face)

parts=defaultdict(set)
for group in islands.values():
    points=[positions[i] for face in group for i in face.vertices]
    xs,ys,zs=zip(*points)
    slot=chair.material_slots[group[0].material_index].name
    if max(zs)<12 and min(xs)>28 and slot in ('MI_Rubber','MI_IronBlack'):
        part='Caster' if max(ys)<0 else 'OtherCaster'
    elif max(zs)<65 and (min(ys)>=26.9 or max(ys)<=-26.9) and slot in ('MI_Rubber','MI_Steel','MI_MetalDark'):
        part='RightWheel' if max(ys)<0 else 'LeftWheel'
    else:
        part='Frame'
    parts[part].update(face.index for face in group)
assert all(parts[key] for key in ('Frame','RightWheel','LeftWheel','Caster','OtherCaster'))
assert sum(map(len,parts.values()))==len(mesh.polygons)

output=root/'SourceArt/Props/HarrowFurniture'
for part,pivot in [('Frame',(0,0,0)),('RightWheel',(.5,-30,31.8)),('LeftWheel',(.5,30,31.8)),('Caster',(30.5,-25,6.8))]:
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index not in parts[part]],context='FACES')
    for vert in bm.verts:
        vert.co=chair.matrix_world @ vert.co-Vector(pivot)*.01
    name='SM_BathChair'+part
    data=mesh.copy()
    bm.to_mesh(data)
    bm.free()
    data.update()
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active=obj
    obj.select_set(True)
    bpy.ops.object.material_slot_remove_unused()
    bpy.ops.export_scene.fbx(filepath=str(output/(name+'.fbx')),use_selection=True,
                             apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,mesh_smooth_type='FACE')
    bpy.data.objects.remove(obj,do_unlink=True)
