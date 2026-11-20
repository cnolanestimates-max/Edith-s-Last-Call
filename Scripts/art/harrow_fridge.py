"""A mid-century enamel icebox, a separately hinged door and spoiled pantry food."""
from pathlib import Path
import sys, math, random
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from harrow_mesh import box,rod,finish,xyz,export
from harrow_mesh import path,ellipsoid

rng=random.Random(1974)
enamel='M_HarrowEnamel';brass='M_PhoneBrass';steel='M_ItemSteel';iron='MI_Iron'
tar='M_HarrowPreserve';fruit='M_HarrowFruit';paper='M_HarrowWrapper'
def panel(at,size,mat,bevel=1):
    o=box(at,size,mat,bevel)
    # Use the whole scan on a broad pressed-steel face; preserve per-face orientation.
    uv=o.data.uv_layers.active
    for face in o.data.polygons:
        if face.area < .002:continue
        k=max(range(3),key=lambda i:abs(face.normal[i]));axes=[i for i in range(3) if i!=k]
        if k==0:axes=[1,2]
        for li in face.loop_indices:
            co=o.data.vertices[o.data.loops[li].vertex_index].co
            uv.data[li].uv=(.5+co[axes[0]]/(size[axes[0]]/100),.5+co[axes[1]]/(size[axes[1]]/100))
    return o

def revolve(x,y,z,profile,mat,scale_y=1,jitter=0,seed=1,n=48):
    verts=[];faces=[];uvs=[];r=random.Random(seed);a0=r.uniform(0,6)
    for j,(height,rad) in enumerate(profile):
        for i in range(n):
            a=math.tau*i/n
            wave=1+jitter*(.6*math.sin(5*a+a0+.3*j)+.4*math.cos(7*a+j*.15))
            verts.append(xyz((x+rad*wave*math.cos(a),y+rad*scale_y*wave*math.sin(a),z+height+jitter*.8*math.sin(a*4))))
    for j in range(len(profile)-1):
        for i in range(n):
            nxt=(i+1)%n
            faces.append((j*n+i,(j+1)*n+i,(j+1)*n+nxt,j*n+nxt))
            uvs.extend(((i/n,profile[j][0]/max(1,profile[-1][0])),(i/n,profile[j+1][0]/max(1,profile[-1][0])),((i+1)/n,profile[j+1][0]/max(1,profile[-1][0])),((i+1)/n,profile[j][0]/max(1,profile[-1][0]))))
    m=bpy.data.meshes.new('Turned profile');m.from_pydata(verts,[],faces);m.update()
    tex=m.uv_layers.new()
    for dst,src in zip(tex.data,uvs):dst.uv=src
    o=bpy.data.objects.new('Turned profile',m);bpy.context.collection.objects.link(o);finish(o,mat)
    for f in m.polygons:f.use_smooth=True

def label(x,y,z,radius,h,mat):
    vs=[];fs=[];uv=[]
    for j in (0,1):
        for i in range(33):
            a=-1.10+2.2*i/32
            vs.append(xyz((x+radius*math.cos(a),y+radius*math.sin(a),z+j*h-.12*math.cos(6*a))))
    for i in range(32):
        fs.append((i,33+i,34+i,i+1));uv.extend(((i/32,0),(i/32,1),((i+1)/32,1),((i+1)/32,0)))
    m=bpy.data.meshes.new('Water stained paper label');m.from_pydata(vs,[],fs);m.update();tex=m.uv_layers.new()
    for dst,src in zip(tex.data,uv):dst.uv=src
    o=bpy.data.objects.new('Jar label',m);bpy.context.collection.objects.link(o);finish(o,mat)
def jar(x,y,z,r,h,kind,opened=False):
    revolve(x,y,z,[(0,.2),(0,r*.76),(.7,r*.96),(2,r),(h*.76,r),(h*.86,r*.82),(h*.95,r*.82),(h,r*.91),(h+.5,r*.87),(h+.5,r*.74)],'M_JarGlass')
    revolve(x,y,z+.55,[(0,.1),(.1,r*.78),(1,r*.93),(h*.63,r*.93),(h*.72,r*.83),(h*.71,.1)],tar)
    for k in range(3):revolve(x,y,z+h-2+k*.8,[(0,r*.81),(.23,r*.86),(.39,r*.82)],steel)
    if not opened:
        revolve(x,y,z+h+.4,[(0,r*.88),(.3,r*.94),(1.3,r*.94),(1.7,r*.78),(1.7,.03)],'MI_Rust')
    label(x,y,z+h*.22,r+.1,h*.33,'M_Harrow'+kind)
def bad_pear(x,y,z,s,k):
    revolve(x,y,z,[(0,.2),(.6*s,2.7*s),(3*s,4.4*s),(5*s,4.0*s),(7*s,2.9*s),(9*s,1.6*s),(9.8*s,.4*s)],fruit,.84,.12,k)
    rod((x,y,z+9.4*s),(x+.7*s,y+.25*s,z+11.5*s),.26*s,'MI_WoodRotten')
    for j in range(3):
        ellipsoid((x+2.8*s,y+(j-1)*1.4*s,z+(3.5+.5*j)*s),(1.5*s,1.4*s,.7*s), 'M_HarrowFruit')
def parcel(x,y,z,s):
    panel((x,y,z+3.3*s),(18*s,24*s,6.4*s),paper,1.5*s)
    for k in (-1,1):
        path([(x-8*s,y+k*8*s,z+5*s),(x-1*s,y+k*11*s,z+7*s),(x+8*s,y+k*7*s,z+5.7*s)],.24*s,'MI_LeatherTan')
    for k in (-1,1):path([(x-8.5*s,y+k*5*s,z+s),(x-8.9*s,y+k*5*s,z+5.6*s),(x-7*s,y+k*5*s,z+6.8*s),(x+8*s,y+k*5*s,z+6.7*s),(x+8.8*s,y+k*5*s,z+s)],.16*s,'MI_LeatherTan')
def cabbage(x,y,z):
    # Nested individual leaves curl away from the rotten core of last winter's cabbage.
    ellipsoid((x,y,z+5),(8.1,8.,5.5),fruit)
    for k in range(17):
        phi=k*2.39996;span=.95 if k<10 else .78
        rows=[]
        for j in range(12):
            u=j/11;row=[]
            for i in range(24):
                v=i/23*2-1;theta=phi+v*span*(.45+.55*u)
                rad=(4.8 if k<10 else 3.)+(5.5 if k<10 else 4.5)*math.sin(u*1.85)+.7*math.cos(7*v+k)*u*u
                height=z+1+u*(8 if k<10 else 11)-2.1*v*v*u+u*u*math.sin(10*v+k)
                row.append((x+rad*math.cos(theta),y+rad*math.sin(theta),height))
            rows.append(row)
        from harrow_mesh import surface
        surface('Rot curled leaf',rows,fruit,uvscale=17,closed=False)
        path([row[12] for row in rows],.14,'M_HarrowWrapper')
    for k in range(17):
        t=rng.uniform(0,6.28);rr=rng.uniform(1,6)
        ellipsoid((x+rr*math.cos(t),y+rr*math.sin(t),z+9+rng.uniform(-.9,.3)),(.62,.53,.35),'MI_PaperOld')
def wire(z):
    for y in range(-34,36,4):rod((-24,y,z),(24,y,z),.31,steel)
    for x in (-24,0,24):rod((x,-36,z-.5),(x,36,z-.5),.53,'MI_Rust')
    for y in (-37,37):rod((-25,y,z),(25,y,z),.65,steel)
def make():
    # Recessed liner, kick grille, adjustable wire racks and an ice compartment.
    panel((-31,0,85),(6,86,164),enamel,2.0)
    for side in (-1,1):panel((0,side*41,85),(65,5,164),enamel,2.2)
    panel((0,0,10),(66,86,9),enamel,2.2);panel((0,0,162),(66,86,8),enamel,2.3)
    panel((28,0,7),(4,74,10),iron,1.1)
    for y in range(-32,33,4):panel((30.3,y,7),(1.5,1.3,6.2),'MI_Rust',.5)
    for side in (-1,1):
        panel((-9,side*37.6,84),(6,1.8,115),iron)
        for z in range(35,141,9):panel((-9,side*36.6,z),(3,.7,3),'MI_Rust',.25)
    for z in (39,75,110):wire(z)
    panel((-11,-6,143),(34,63,23),enamel,1.6)
    ellipsoid((-6,34,120),(3.2,2.8,5.2),'M_PhoneIvory')
    for z in (116,119,122):rod((-7,31,z),(-2,31,z),.45,steel)
    panel((7,-6,142),(2,57,17),steel,1.1)
    panel((8.5,12,141),(2,9,2.5),iron)
    for j in range(4):rod((8.5,-27,138+j*2.6),(8.5,-18,138+j*2.6),.31,iron)
    # Sour fruit on a chipped oval dish. Escaped syrup runs through the wire.
    revolve(4,-12,75.8,[(0,.2),(0,10),(1.1,16),(2.3,19),(2.8,19),(2.1,16),(1.3,.1)],enamel,.73)
    for x,y,z,s,k in [(2,-21,77,.98,2),(9,-11,77,1.12,3),(-2,-7,77,.87,4),(3,-12,80,1.06,5)]:
        bad_pear(x,y,z,s,k)
    jar(-2,22,76,6.9,19,'PearLabel')
    jar(9,-19,111,7.4,17,'PlumLabel',True);jar(-10,9,111,6.4,19,'PearLabel')
    # Molded puddle and stringy drips below the open jar.
    revolve(8,-17,110.2,[(0,.08),(.15,10),(.6,8.5),(.8,.05)],tar,.85,.21)
    for yy,drop in [(-21,9),(-17,5),(-11,13)]:
        path([(15,yy,111),(18,yy-.6,109),(18,yy,106),(17.8,yy+.3,111-drop)],.37,tar)
        ellipsoid((17.8,yy+.3,111-drop),(.6,.56,.87),tar)
    parcel(7,11,39.5,1.1);cabbage(7,-19,39.6)
    panel((9,2,20),(33,61,12),'MI_Porcelain',2.4)
    panel((26,2,23),(2.4,59,15),enamel,1.7)
    rod((29,-9,23),(29,10,23),.95,steel)
    export('SM_HarrowFridge')
    # Door pivot is at its hinge. All interior bins and the bottles swing with it.
    panel((2,-41,84),(8,86,162),enamel,3.6)
    panel((-2,-41,85),(2,81,154),'MI_FabricDark',2.2)
    panel((-3.4,-41,85),(2.2,77,149),enamel,2.0)
    for z in (35,78):
        panel((-9,-42,z),(13,62,2.4),enamel,.9)
        for y in (-72,-12):rod((-4,y,z+8),(-15,y,z+8),.56,steel)
        rod((-15,-72,z+8),(-15,-12,z+8),.68,steel)
    jar(-9,-43,36.3,4.4,15,'PlumLabel')
    for y in (-56,-64,-35):
        ellipsoid((-9,y,82),(3.1,2.7,4.3),'M_HarrowEnamel')
    # Thumb release and bowed chrome handle, an enamel badge and exposed hinge caps.
    for z in (90,111):panel((7.8,-72,z),(5.2,4.3,4.7),steel,1.15)
    path([(8,-72,89),(11,-72.4,92),(12.5,-72.6,100),(12.4,-72.5,108),(9,-72,113)],1.38,steel)
    panel((9,-72,114),(5,3.8,2.1),iron,.6)
    panel((6.5,-23,137),(1.3,16,4.4),steel,.8)
    for y in (-28,-24,-20):panel((7.3,y,137),(.6,1.5,2),brass,.25)
    for z in (21,143):rod((1,.2,z),(1,.2,z+8),1.7,steel)
    export('SM_HarrowFridgeDoor')
if __name__=='__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True);make()
