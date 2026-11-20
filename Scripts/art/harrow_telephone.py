"""Retopologize the SF3D phone shell and rebuild small functional details lost in reconstruction.
Run in Blender background with this script. Source and exports live in SourceArt/Phone.
"""
import math
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector, geometry
from mathutils.bvhtree import BVHTree

OUT = Path(__file__).resolve().parents[2] / 'SourceArt/Phone'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/'Reconstruction.glb'))
scan = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
scan.data.calc_loop_triangles()
triangles = list(scan.data.loop_triangles)
points = [scan.matrix_world @ v.co for v in scan.data.vertices]
lo = Vector(tuple(min(v[i] for v in points) for i in range(3)))
hi = Vector(tuple(max(v[i] for v in points) for i in range(3)))
mid = (hi + lo) / 2
# Construction space is cm, with the dial facing -Y. Flatten the photographed tilt at the sole.
points = [Vector((mid.x-v.x, mid.y-v.y, v.z-lo.z))*15.5/(hi.z-lo.z) for v in points]
tree = BVHTree.FromPolygons(points,[t.vertices[:] for t in triangles],all_triangles=True)
uv = scan.data.uv_layers.active.data
tex = next(n for n in scan.data.materials[0].node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].links[0].from_node.image
pixels=np.empty(len(tex.pixels),dtype=np.float32)
tex.pixels.foreach_get(pixels)
pixels=pixels.reshape(tex.size[1],tex.size[0],4)


def scan_tone(location):
    near,_,idx,_=tree.find_nearest(location)
    t=triangles[idx]
    a,b,c=[points[j] for j in t.vertices]
    coords=[Vector((*uv[j].uv,0)) for j in t.loops]
    if (b-a).cross(c-a).length_squared<1e-10:return .24
    uvw=geometry.barycentric_transform(near,a,b,c,*coords)
    col=pixels[min(tex.size[1]-1,max(0,int(uvw.y*tex.size[1]))),min(tex.size[0]-1,max(0,int(uvw.x*tex.size[0])))]
    return min(.85, .10+float(np.sqrt(max(0,col[:3].mean())))*.82)

objects=[]
TAU=math.tau

def finish(name, verts, faces, material, smooth=True):
    data=bpy.data.meshes.new(name);data.from_pydata([Vector(p)*.01 for p in verts],[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    data.materials.append(bpy.data.materials.get(material) or bpy.data.materials.new(material))
    for p in data.polygons:p.use_smooth=smooth
    if material=='PhoneBakelite':
        colors=data.color_attributes.new(name='ScanTone',type='FLOAT_COLOR',domain='POINT')
        for vert in data.vertices:
            tone=scan_tone(vert.co*100)
            colors.data[vert.index].color=(tone,tone,tone,1)
    objects.append(obj)
    return obj

def skin(name, rings, mat):
    n=len(rings[0])
    faces=[tuple(reversed(range(n)))]
    for j in range(len(rings)-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n
            faces.append((a,b,b+n,a+n))
    faces.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
    return finish(name,[p for ring in rings for p in ring],faces,mat)

def ellipse(rx, ry, power=1, count=80):
    def powerof(v):return math.copysign(abs(v)**power,v)
    return [(rx*powerof(math.cos(TAU*j/count)),ry*powerof(math.sin(TAU*j/count))) for j in range(count)]

half=(max(p.x for p in points)-min(p.x for p in points))/2
depth=(max(p.y for p in points)-min(p.y for p in points))/2
shell=[(half*.84,depth*.98,-.2,.36,0),(half*.87,depth,-.2,.52,0),
       (half*.87,depth,-.2,1.58,0),(half*.86,depth*.99,-.2,1.95,0),
       (half*.84,depth*.95,-.12,2.35,.04),(half*.62,depth*.79,.65,7.02,.52),
       (half*.59,depth*.70,.80,7.98,.55),(half*.55,depth*.65,.80,8.18,.55)]
skin('Moulded housing', [[(x,y+cy,z+y*slope) for x,y in ellipse(rx,ry,.27)] for rx,ry,cy,z,slope in shell],'PhoneBakelite')
skin('Bottom seam', [[(x,y-.2,z) for x,y in ellipse(half*.868,depth*.999,.26)] for z in [.49,.64]],'PhoneRubber')

def round_axis(name, center, normal, profile, mat, sides=64):
    n=Vector(normal).normalized()
    right=Vector((1,0,0))
    if abs(right.dot(n))>.95:right=Vector((0,1,0))
    right=(right-n*n.dot(right)).normalized();up=n.cross(right)
    rings=[[Vector(center)+n*t+right*x+up*y for x,y in ellipse(r,r,count=sides)] for t,r in profile]
    return skin(name,rings,mat)

for x in [-7.5,7.5]:
    for y in [-6,6]:
        round_axis('Rubber foot',(x,y,0),(0,0,1),[(0,.76),(.11,.98),(.48,1)],'PhoneRubber',24)
for x in [-5.4,5.4]:
    for y in [1.1,5.1]:
        skin('Cradle horn',[[(x+a,y+b,z) for a,b in ellipse(r,.75*r,.62,28)] for z,r in [(7.2,1.5),(10.4,1.25),(12.6,.82),(13,.62)]],'PhoneBakelite')
# Continuous bowed handset. Its central underside clears the cradle.
grip=[]
for i in range(65):
    t=i/64;x=-10.0+20*t
    arch=math.sin(math.pi*t)**.85
    z=11.85+2.34*arch
    grip.append([(x,3.6+dy,z+dz) for dy,dz in ellipse(1.45+.45*(1-arch),1.22+.32*(1-arch),.75,40)])
skin('Receiver bridge',grip,'PhoneBakelite')
for sign in [-1,1]:
    normal=(sign*.40,-.33,-.85)
    end=(sign*9.2,3.45,12.25)
    round_axis('Receiver bell',end,normal,[(-.85,.82),(-.62,1.55),(-.13,2.15),(.7,2.54),(1.64,2.68),(2.03,2.67),(2.22,2.57)],'PhoneBakelite')
    round_axis('Receiver screw seam',end,normal,[(1.48,2.69),(1.55,2.72),(1.65,2.70)],'PhoneRubber')
    round_axis('Mouthpiece cap',end,normal,[(2.21,2.55),(2.32,2.38),(2.37,2.08)],'PhoneBakelite')
# Number plate and finger wheel follow the sloping front panel.
angle=math.radians(43);axis=Vector((0,-math.sin(angle),math.cos(angle)))
up=Vector((0,math.cos(angle),math.sin(angle)));right=Vector((1,0,0))
center=Vector((0,-3.00,6.85))
def dial(x,y,z):return center+right*x+up*y+axis*z
def disc(name,profile,mat):
    return round_axis(name,center,axis,profile,mat,96)
disc('Dial mount',[(-1.08,5.60),(-.4,5.84),(-.1,5.73),(.05,5.61)],'PhoneBakelite')
disc('Brass edge',[(.03,5.57),(.10,5.58),(.16,5.51)],'PhoneBrass')
disc('Ivory number plate',[(.15,5.42),(.19,5.40)],'PhoneIvory')
disc('Dark dial backing',[(.19,4.05),(.26,4.03)],'PhoneRubber')
# Manifold ring with ten real finger holes, bevelled on their inner and outer rims.
wheel=disc('Finger wheel',[(.26,3.91),(.31,4.07),(.67,4.07),(.72,3.96)],'PhoneDial')
angles=[math.radians(43+29*i) for i in range(10)]
for a in angles:
    loc=dial(3.1*math.cos(a),3.1*math.sin(a),.46)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.0072,depth=.013,location=loc*.01)
    cutter=bpy.context.object;cutter.rotation_euler=axis.to_track_quat('Z','Y').to_euler()
    bpy.context.view_layer.objects.active=wheel
    mod=wheel.modifiers.new('Finger socket','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
for p in wheel.data.polygons:p.use_smooth=False
disc('Card bezel',[(.70,2.12),(.79,2.17),(.85,2.06)],'PhoneBrass')
disc('Exchange card',[(.82,1.97),(.86,1.95)],'PhonePaper')

def lettering(value,x,y,h,z,mat):
    curve=bpy.data.curves.new('Engraved type','FONT');curve.body=value;curve.align_x='CENTER';curve.align_y='CENTER';curve.size=h*.01;curve.resolution_u=3
    o=bpy.data.objects.new('Dial marking',curve);bpy.context.collection.objects.link(o);o.location=dial(x,y,z)*.01;o.rotation_euler.x=angle
    curve.materials.append(bpy.data.materials[mat])
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
    objects.append(o)
for i,a in enumerate(angles):
    lettering(str((i+1)%10),4.76*math.cos(a),4.76*math.sin(a),.94,.205,'PhoneRubber')
lettering('HARROW',0,.40,.69,.875,'PhoneRubber');lettering('2  -  4 1 7',0,-.57,.52,.875,'PhoneRubber')
# A tapered finger stop sits at the end of travel.
a=math.radians(-40);c,s=math.cos(a),math.sin(a)
stop=[]
for h,w,r in [(.25,.53,5.32),(.43,.54,5.22),(.78,.43,4.04),(.94,.28,3.47)]:
    stop.append([dial((r+xx)*c-yy*s,(r+xx)*s+yy*c,h) for xx,yy in ellipse(.33,w,.5,20)])
skin('Nickel finger stop',stop,'PhoneBrass')
# Helical receiver cord rests on the table and rises to the left earpiece.
def cablepoint(t):
    return Vector((-8.65-2.94*math.sin(t*math.pi)**.65,-6.25+9.25*t,.62+10.35*t**2.2))
def tube(name, path, radius, mat):
    rings=[]
    for i,p in enumerate(path):
        tangent=(path[min(i+1,len(path)-1)]-path[max(0,i-1)]).normalized()
        local=tangent.cross(Vector((0,0,1)))
        if local.length<.01:local=tangent.cross(right)
        local.normalize();local2=tangent.cross(local)
        rings.append([p+local*x+local2*y for x,y in ellipse(radius,radius,count=8)])
    return skin(name,rings,mat)
cord=[]
for i in range(520):
    t=i/519;p=cablepoint(t);tan=(cablepoint(min(1,t+.001))-cablepoint(max(0,t-.001))).normalized()
    h=tan.cross(right).normalized();v=tan.cross(h)
    cord.append(p+.47*(h*math.cos(TAU*23*t)+v*math.sin(TAU*23*t)))
tube('Coiled lead',cord,.18,'PhoneRubber')
tube('Cord to base',[cord[0],Vector((-8.5,-6.4,.76)),Vector((-8.2,-6.35,1.09))],.20,'PhoneRubber')
# Bake the projected scan tones onto the retopologized parts. Projecting a whole new polygon
# through a single tiny SF3D triangle stretches atlas seams into conspicuous triangular chips.
bpy.ops.object.select_all(action='DESELECT')
shell_parts=[o for o in objects if o.data.materials[0].name=='PhoneBakelite']
objects=[o for o in objects if o not in shell_parts]
for o in shell_parts:o.select_set(True)
bpy.context.view_layer.objects.active=shell_parts[0]
bpy.ops.object.join()
housing=bpy.context.object
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(island_margin=.012)
bpy.ops.object.mode_set(mode='OBJECT')
bake_mat=housing.data.materials[0]
nodes=bake_mat.node_tree.nodes
nodes.clear()
tone=nodes.new('ShaderNodeVertexColor');tone.layer_name='ScanTone'
emit=nodes.new('ShaderNodeEmission');out=nodes.new('ShaderNodeOutputMaterial')
bake_mat.node_tree.links.new(tone.outputs['Color'],emit.inputs['Color'])
bake_mat.node_tree.links.new(emit.outputs[0],out.inputs['Surface'])
target=nodes.new('ShaderNodeTexImage');target.image=bpy.data.images.new('PhonePatina',512,512,alpha=False)
nodes.active=target
bpy.context.scene.render.engine='CYCLES'
bpy.context.scene.cycles.samples=1
bpy.ops.object.bake(type='EMIT',margin=5)
target.image.filepath_raw=str(OUT/'T_PhonePatina.png');target.image.file_format='PNG';target.image.save()
nodes.clear()
objects.insert(0,housing)
bpy.data.objects.remove(scan,do_unlink=True)
# FBX keeps material sections and UVs in one draw mesh; origin is the foot plane.
bpy.ops.object.select_all(action='DESELECT')
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
body=bpy.context.object;body.name='SM_HarrowTelephone'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
bpy.ops.export_scene.fbx(filepath=str(OUT/'SM_HarrowTelephone.fbx'),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,mesh_smooth_type='FACE')
print('WC_PHONE_MODEL',body.dimensions[:],len(body.data.polygons))
