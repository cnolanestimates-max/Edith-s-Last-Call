"""Export just Edith's left arm, in centimetres, with a finger-curl morph for Ruth's bed."""
from pathlib import Path
import bisect
import math

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "SourceArt/Her/export"
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = .01
bpy.ops.import_scene.fbx(filepath=str(OUT / "SK_Her.fbx"), use_anim=False)
mesh = next(o for o in scene.objects if o.type == "MESH")
mesh.shape_key_clear()
for mod in list(mesh.modifiers):
    mesh.modifiers.remove(mod)
mesh.parent = None
mesh.name = "BedArm"
bm = bmesh.new()
bm.from_mesh(mesh.data)
weights = bm.verts.layers.deform.active
groups = {g.index for g in mesh.vertex_groups if g.name in {"LeftArm", "LeftForeArm", "LeftHand"}}
discard = [v for v in bm.verts if v.co.z > 183 or sum(v[weights].get(i, 0.) for i in groups) < .52]
bmesh.ops.delete(bm, geom=discard, context="VERTS")
bm.to_mesh(mesh.data)
bm.free()
mesh.vertex_groups.clear()
# Lay the back of the hand uppermost. Keep the existing UVs, veins, knuckles,
# finger silhouettes and cross sections while relaxing the shoulder to floor height.
profile = [(45,80), (65,80), (75,77.7), (85,73.8), (95,72.9),
           (110,70.1), (125,62.5), (150,48.4), (170,40.4), (184,35.5)]
for v in mesh.data.vertices:
    x, y, z = v.co
    k = min(len(profile)-1, max(1, bisect.bisect_left([p[0] for p in profile], z)))
    (za, xa), (zb, xb) = profile[k-1:k+1]
    center = xa + (xb-xa)*(z-za)/(zb-za)
    reach = (101-z)*1.12
    # Keep the shoulder end well behind the skirt at maximum extension.
    reach += min(0., reach + 7.) * .58
    v.co = (reach, (y+8)*.90, (x-center)*.74 + 2*math.sin((z-46)/136*math.pi))

mesh.shape_key_add(name="Basis")
grip = mesh.shape_key_add(name="Grip")
for point in grip.data:
    x, y, z = point.co
    # Roll distal fingers down over the far lip, keeping knuckles on the lid.
    length = max(0., x-33.)
    angle = min(1.30, length/24.)
    if length:
        point.co = (33. + 24.*math.sin(angle), y*.99, z - 24.*(1.-math.cos(angle)))

# A single stationary bone lets the engine interpolate the grip on the GPU.
arm_data = bpy.data.armatures.new("BedArmRig")
arm = bpy.data.objects.new("Armature", arm_data)
scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
bone = arm_data.edit_bones.new("Root")
bone.head, bone.tail = (0,0,0), (10,0,0)
bpy.ops.object.mode_set(mode="OBJECT")
group = mesh.vertex_groups.new(name="Root")
group.add(list(range(len(mesh.data.vertices))), 1., "REPLACE")
mesh.parent = arm
mod = mesh.modifiers.new("Skin", "ARMATURE")
mod.object = arm
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
mesh.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(OUT / "SK_BedArm.fbx"), use_selection=True,
                         object_types={"ARMATURE","MESH"}, bake_anim=False, use_mesh_modifiers=False,
                         add_leaf_bones=False, mesh_smooth_type="FACE", apply_scale_options="FBX_SCALE_UNITS",
                         path_mode="STRIP", use_tspace=True)
print("Bed arm exported", len(mesh.data.vertices), "vertices")
