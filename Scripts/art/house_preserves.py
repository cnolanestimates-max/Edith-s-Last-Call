"""Build low-poly pantry preserves and spilled tar in shelf-local centimetres with Blender."""
import math
import random
import runpy
from pathlib import Path
import bpy

OUT = Path(__file__).resolve().parents[2] / "SourceArt/Props"
TAU = math.tau


def start():
    global verts, faces, materials, slots
    verts, faces, materials, slots = [], [], [], []


def rings(rows, material):
    if material not in slots:
        slots.append(material)
    idx = len(verts)
    count = len(rows[0])
    for row in rows:
        verts.extend((x / 100, -y / 100, z / 100) for x, y, z in row)
    polys = [tuple(range(idx, idx + count))]
    for j in range(len(rows) - 1):
        for k in range(count):
            a = idx + j * count + k
            b = idx + j * count + (k + 1) % count
            polys.append((a, a + count, b + count, b))
    end = idx + (len(rows) - 1) * count
    polys.append(tuple(reversed(range(end, end + count))))
    faces.extend(polys)
    materials.extend([slots.index(material)] * len(polys))


def rounded(x,y,z,rx,ry,rz,material,seed,irregular=.18):
    rows = []
    for j in range(11):
        lat = -.99 * math.pi/2 + .99 * math.pi*j/10
        ring = []
        for i in range(20):
            t = TAU*i/20
            r = math.cos(lat) * (1 + irregular * math.sin(3*t+seed+2*lat) * math.cos(lat) + .06*math.cos(5*t-2*lat+seed))
            ring.append((x+rx*r*math.cos(t)+rx*.15*math.sin(lat+seed),y+ry*r*math.sin(t),z+rz*math.sin(lat)))
        rows.append(ring)
    rings(rows,material)


def jars(herbs):
    rng = random.Random(613 if herbs else 215)
    for row,bottom in enumerate([2.5] if herbs else [2.5,47.,89.]):
        for col,x in enumerate([-22,-7,8,23] if herbs else [-36,-12,12,36]):
            r, y = (5.5,0.) if herbs else (6.95,1.)
            height = (14 if col%2==0 else 18) if herbs else (20 if (col+row)%2==0 else 28)
            h=height*rng.uniform(.56,.79)
            def circle(z,rad):
                return [(x+rad*math.cos(TAU*i/24),y+rad*math.sin(TAU*i/24),bottom+z) for i in range(24)]
            rings([circle(.65,r*.82),circle(1.55,r*.96),circle(h-.40,r*.96),circle(h,r*.92)],'PickleBrine')
            rounded(x,y,bottom+1.6,r*.84,r*.76,1.1,'JarSediment',col)
            for i in range(3):
                ang=TAU*i/3+rng.uniform(-.4,.4)
                cx=x+math.cos(ang)*r*.36
                cy=y+math.sin(ang)*r*.36
                hh=h*(.26+.07*i)
                rounded(cx,cy,bottom+hh+1.5,r*.34,r*.32,hh,('PickleOchre','PicklePale','PickleRust')[(i+row+col)%3],rng.random()*8,.27)
            for i in range(2):
                rows=[]
                for k in range(15):
                    t=k/14
                    a=i*2.8+t*4.8+col
                    px=x+r*.57*math.cos(a);py=y+r*.57*math.sin(a)
                    thick=r*(.085-.055*t)
                    rows.append([(px+thick*math.cos(TAU*s/7),py+thick*math.sin(TAU*s/7),bottom+2+t*h*.87) for s in range(7)])
                rings(rows,'PickleRust' if col%2 else 'PicklePale')


def tar():
    # A low uneven puddle, a sagging clot on the brass saucer, and three runs joining it.
    rounded(0,0,.55,11.5,8.7,.64,'KitchenTar',2,.22)
    rounded(-.4,.3,4.35,6.4,5.5,4.5,'KitchenTar',1,.25)
    for x,y,dx,dy in [(-4,3,-5,4),(4,-2,5,-4),(2,4,2,4)]:
        rows=[]
        for j in range(11):
            t=j/10; radius=1.15*(1-.72*t)
            rows.append([(x+dx*t+radius*math.cos(TAU*k/12),y+dy*t+radius*math.sin(TAU*k/12),.65+4.6*(1-t)**2+.36*math.sin(TAU*k/12)) for k in range(12)])
        rings(rows,'KitchenTar')


def chipped_plaster():
    contour=runpy.run_path(str(Path(__file__).with_name('stair_opening.py')))['OUTLINE']
    # The two exposed plaster edges and the lath inside share an open bore.
    rng=random.Random(46)
    slots.extend(['BrokenPlaster','ExposedLath'])
    for side in [-1,1]:
        offsets=[rng.uniform(1.22,1.49) for pt in contour]
        rows=[]
        for i,(x,z) in enumerate(contour):
            rows.append([(x*offsets[i],10.26*side,z*offsets[i]),
                         (x*1.08,(10.6+rng.uniform(0,.45))*side,z*1.08),
                         (x*.91,9.7*side,z*.91),
                         (x*.90,0,z*.90)])
        first=len(verts)
        for row in rows:verts.extend((x/100,-y/100,z/100) for x,y,z in row)
        for i in range(len(rows)):
            for j in range(3):
                a=first+4*i+j;b=first+4*((i+1)%len(rows))+j
                face=(a,b,b+1,a+1)
                faces.append(face if side==1 else face[::-1])
                materials.append(int(j==2))


def export(name):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    for s in slots:mesh.materials.append(bpy.data.materials.get(s) or bpy.data.materials.new(s))
    for face,m in zip(mesh.polygons,materials):face.material_index=m;face.use_smooth=len(face.vertices)==4
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},bake_anim=False,add_leaf_bones=False,mesh_smooth_type='FACE',apply_scale_options='FBX_SCALE_NONE')


if __name__=='__main__':
    for name,build in [('SM_PantrySpecimens',lambda:jars(False)),('SM_PantryPreserves',lambda:jars(True)),('SM_KitchenTar',tar),('SM_BrokenPlasterEdge',chipped_plaster)]:
        start();build();export(name)
