"""Build the low-poly housefly used by the instanced swarms. Blender, metres."""
import bpy, math
from pathlib import Path
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
parts = []
def ellipsoid(name, center, radius, material, yaw=0, tilt=0):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=5, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = radius
    obj.rotation_euler = (tilt, 0, yaw)
    obj.data.materials.append(material)
    for face in obj.data.polygons: face.use_smooth = True
    parts.append(obj)
def surface(name, rgb):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*rgb,1)
    return m
body=surface("FlyBody",(.042,.035,.028))
wing=surface("FlyWing",(.36,.31,.24))
eye=surface("FlyEye",(.105,.030,.019))
ellipsoid("Thorax",(0,0,0),(.032,.025,.023),body)
ellipsoid("Abdomen",(-.047,0,-.003),(.042,.023,.020),body)
ellipsoid("Head",(.037,0,.002),(.023,.022,.020),body)
for side in [-1,1]:
    ellipsoid("Eye",(.043,.016*side,.006),(.015,.010,.014),eye)
    ellipsoid("Wing",(-.027,.050*side,.016),(.062,.022,.003),wing,-side*.72,side*.19)
    for x in [-.032,0,.026]:
        ellipsoid("Leg",(x-.005,.027*side,-.016),(.006,.023,.003),body,side*(x*11),-side*.52)
bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.join()
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.context.object.name='SM_HouseFly'
path=Path(__file__).resolve().parents[2]/'SourceArt/Props/SM_HouseFly.fbx'
bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,add_leaf_bones=False,axis_forward='-Y',axis_up='Z',mesh_smooth_type='FACE')
