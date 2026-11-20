"""Model the mask from the approved B portrait, preserving its inverted face and pointed cheeks."""
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from harrow_mesh import xyz, finish, export

ROOT = Path(__file__).resolve().parents[2]
# Pixel coordinates in the approved comparison plate, relative to (960, 80).
PROFILE = [(203,84),(231,85),(248,95),(264,111),(289,143),(314,172),(333,205),
           (343,240),(355,263),(391,300),(343,282),(337,319),(331,350),(316,378),
           (295,400),(265,422),(239,431),(208,432),(179,425),(151,414),(129,395),
           (112,369),(104,341),(99,312),(98,282),(46,301),(76,274),(88,251),
           (90,221),(99,201),(115,181),(131,160),(145,135),(159,111),(181,91)]
CENTER = Vector((213,252))
RINGS = 22


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Use the existing plate verbatim as a UV atlas. The mesh ends at the chin and cheeks.
    boundary = []
    for i, p in enumerate(PROFILE):
        a, b = Vector(p), Vector(PROFILE[(i+1)%len(PROFILE)])
        boundary.extend(a.lerp(b,j/4) for j in range(4))
    n = len(boundary)
    vertices, tex, faces = [], [], []
    def add(point,t):
        u,v = point
        def bump(cx,cy,w,h):
            return math.exp(-((u-cx)/w)**2-((v-cy)/h)**2)
        depth = 1.5 + 7.0*math.sqrt(max(0,1-t*t)) + 4.0*bump(211,230,19,38)
        depth += 1.4*bump(211,172,57,12) - 2.5*(bump(159,274,28,13)+bump(269,274,28,13))
        vertices.append(xyz((depth, (u-218)*.094, (251-v)*.099)))
        tex.append(((960+u)/1680,1-(80+v)/840))
    add(CENTER,0)
    for ring in range(1,RINGS+1):
        t = ring/RINGS
        for point in boundary:
            add(CENTER.lerp(point,t),t)
        for j in range(n):
            a,b = 1+(ring-1)*n+j,1+(ring-1)*n+(j+1)%n
            faces.append((0,a,b) if ring==1 else (a-n,a,b,b-n))
    m = bpy.data.meshes.new('Inverted ash mask')
    m.from_pydata(vertices,[],faces)
    m.update()
    uv = m.uv_layers.new(name='UVMap')
    for p in m.polygons:
        p.use_smooth = True
        for li in p.loop_indices:
            uv.data[li].uv = tex[m.loops[li].vertex_index]
    obj = bpy.data.objects.new('Company mask',m)
    bpy.context.collection.objects.link(obj)
    finish(obj,'M_CompanyMask')
    export('SM_CompanyMask')


if __name__=='__main__':
    build()
