"""Blender joinery and relief carving for the Harrow family's walnut armoire, in cm."""
import math
import bmesh
import bpy
from mathutils import Vector

from harrow_mesh import box, brass, finish, xyz

WALNUT = 'M_HarrowWalnut'
BURR = 'M_HarrowBurr'
TAU = math.tau


def front(x, y, z):
    return x, y, z


def door(side):
    angle = math.radians(side*92)
    def transform(x, y, z):
        return (26 + x*math.cos(angle) - y*math.sin(angle),
                side*86 + x*math.sin(angle) + y*math.cos(angle), z)
    return transform


def cubic(start, control1, control2, end, steps=18):
    a, b, c, d = map(Vector, (start, control1, control2, end))
    return [a*(1-t)**3 + 3*b*t*(1-t)**2 + 3*c*t*t*(1-t) + d*t**3
            for t in (i/steps for i in range(steps+1))]


class Carving:
    """Keep the small carved details in a few mesh sections, with explicit veneer UVs."""
    def __init__(self):
        self.sections = {}

    def loft(self, material, transform, rows, uv=None, smooth=True):
        verts, faces, coords, shading = self.sections.setdefault(material, ([], [], [], []))
        offset, n = len(verts), len(rows[0])
        for row in rows:
            for x, y, z in row:
                verts.append(xyz(transform(x, y, z)))
                coords.append(uv(x,y,z) if uv else ((y+x*.61)/54, z/81))
        for j in range(len(rows)-1):
            for k in range(n):
                h = (k+1)%n
                a = offset + j*n
                faces.append((a+k, a+h, a+n+h, a+n+k))
                shading.append(smooth)
        faces.extend((tuple(offset+i for i in reversed(range(n))),
                      tuple(offset+(len(rows)-1)*n+i for i in range(n))))
        shading.extend((False, False))

    def finish(self):
        for material, (verts, faces, coords, shading) in self.sections.items():
            mesh = bpy.data.meshes.new('Armoire joinery')
            mesh.from_pydata(verts, [], faces)
            mesh.update()
            uv = mesh.uv_layers.new(name='UVMap')
            for loop in mesh.loops:
                uv.data[loop.index].uv = coords[loop.vertex_index]
            for face, smooth in zip(mesh.polygons, shading):
                face.use_smooth = smooth
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            # Triangulate the curved shell ends and concave ogees in Blender, where
            # the veneer UVs are defined. The FBX runtime cannot tessellate them.
            bmesh.ops.triangulate(bm, faces=list(bm.faces))
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_area()<1e-13], context='FACES')
            bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces], context='EDGES')
            bm.to_mesh(mesh)
            bm.free()
            obj = bpy.data.objects.new('Hand carved '+material, mesh)
            bpy.context.collection.objects.link(obj)
            finish(obj, material)

    def fillet(self, points, x, width, depth, material=WALNUT, transform=front, taper=None):
        # Oval cross section, swept along the line of the cut in the face of the timber.
        rows = []
        points = [Vector(p) for p in points]
        for i, p in enumerate(points):
            t = i/(len(points)-1)
            dy, dz = (points[min(i+1,len(points)-1)] - points[max(i-1,0)]).normalized()
            w = taper(t) if taper else 1
            rows.append([(x + depth*w*math.cos(j*TAU/10),
                          p.x - dz*width*w*math.sin(j*TAU/10),
                          p.y + dy*width*w*math.sin(j*TAU/10)) for j in range(10)])
        self.loft(material, transform, rows)

    def relief(self, contour, profiles, transform, material):
        ys, zs = zip(*contour)
        cy, cz = (max(ys)+min(ys))/2, (max(zs)+min(zs))/2
        w, h = max(ys)-min(ys), max(zs)-min(zs)
        rows = [[(x, cy+(y-cy)*sy, cz+(z-cz)*sz) for y,z in contour] for x,sy,sz in profiles]
        self.loft(material, transform, rows, lambda x,y,z: (.5+(y-cy)/w, .5+(z-cz)/h), smooth=False)

    def turning(self, x, y, profile, material=WALNUT, twist=False):
        rows = []
        for z,r in profile:
            row = []
            for i in range(32):
                angle = i*TAU/32
                radius = r*(1 + .12*math.cos(4*angle - z*.14)) if twist else r
                row.append((x+radius*math.cos(angle), y+radius*math.sin(angle), z))
            rows.append(row)
        self.loft(material, front, rows, lambda x,y,z: ((y+.58*x)/19, z/72))

    def leaf(self, start, c1, c2, tip, x, width, transform=front, material=BURR):
        self.fillet(cubic(start,c1,c2,tip,12),x,width,width*.58,material,transform,
                    lambda t: .055 + .95*math.sin(math.pi*t)**.88*(1.15-.33*t))

    def flower(self, y, z, x, radius, transform=front):
        for i in range(8):
            a = TAU*i/8
            p = lambda r, da=0: (y+r*math.cos(a+da), z+r*math.sin(a+da))
            self.leaf(p(.1*radius),p(.35*radius,.42),p(.72*radius,.3),p(radius),x,radius*.21,transform)
        circle = [(y+radius*.19*math.cos(i*TAU/16),z+radius*.19*math.sin(i*TAU/16)) for i in range(16)]
        self.relief(circle,[(x-.3,1,1),(x+1,1,1),(x+1.4,.7,.7)],transform,brass)


def arched_panel(carving, transform, cy, bottom, height, breadth):
    # French-arch field cut from a bookmatched leaf, with stepped ogee surrounds.
    w = breadth/2
    spring = bottom + height - 12
    points = [(cy-w+3,bottom),(cy+w-3,bottom),(cy+w,bottom+3),(cy+w,spring)]
    for start,c1,c2,end in [
        ((w,spring),(w-9,spring),(w-7,spring+12),(0,spring+12)),
        ((0,spring+12),(-w+7,spring+12),(-w+9,spring),(-w,spring))]:
        points += [(cy+p.x,p.y) for p in cubic(start,c1,c2,end,15)[1:]]
    points.append((cy-w,bottom+3))
    carving.relief(points,[(2.1,1,1),(2.9,1,1),(3.1,.97,.98),(4.4,.93,.95),(4.7,.89,.93),
                           (3.8,.85,.90)],transform,WALNUT)
    carving.relief(points,[(3.75,.852,.902),(4.4,.81,.88)],transform,BURR)
    for sign in (-1,1):
        carving.leaf((cy,spring-8),(cy+sign*4,spring-2),(cy+sign*12,spring-7),
                     (cy+sign*14,spring-12),4.6,1.35,transform)


def cabinet_doors(carving):
    for side in (-1,1):
        transform = door(side)
        center = -side*37
        box(transform(0,center,107),(4.4,74,180),WALNUT,.6,side*92)
        for face in (-1,1):
            def face_transform(x,y,z):
                return transform(face*x,y,z)
            for z,h in ((23,58),(93,98)):
                arched_panel(carving,face_transform,center,z,h,62)
            carving.flower(center,87,2.35,4.4,face_transform)
            y = -side*67
            plate = [(y-2,95),(y-1.5,92),(y,90),(y+1.5,92),(y+2,95),(y+1.5,101),
                     (y+2.3,104),(y,107),(y-2.3,104),(y-1.5,101)]
            carving.relief(plate,[(2.3,1,1),(2.9,1,1),(3.05,.82,.94)],face_transform,brass)
            ring = [(y+2.05*math.sin(a*TAU/24),99+2.9*math.cos(a*TAU/24)) for a in range(25)]
            carving.fillet(ring,4,.47,.52,brass,face_transform)
        for z in (34,109,175):
            box(transform(0,0,z),(5.1,3.4,8.8),brass,.6,side*92)


def pediment(carving):
    for side in (-1,1):
        # Sawn swan-neck crest rails turn back into a spiral above the shell.
        stem = cubic((88,208),(58,209),(54,239),(28,239),24)
        curl = []
        for i in range(1,48):
            t = i/47
            a = math.pi/2 + t*1.58*math.pi
            r = 11*(1-.87*t)
            curl.append((28+r*math.cos(a),228+r*math.sin(a)))
        line = [(side*y,z) for y,z in [*stem,*curl]]
        def width(t):
            return 1 if t<.35 else max(.13,1-(t-.35)*1.3)
        # The first sweep supplies the silhouette. The smaller sweeps cut beads and quirks into it.
        carving.fillet(line,20,4.6,4.0,WALNUT,taper=width)
        carving.fillet([(y,z+1.5*width(i/(len(line)-1))) for i,(y,z) in enumerate(line)],
                       23.1,.95,.92,BURR,taper=width)
        for delta in (0,12,24):
            y = 75-delta
            z = 208.8+delta*.33
            carving.leaf((side*(y+6),z-1),(side*(y+1),z+5),(side*(y-6),z+5),
                         (side*(y-14),z+11),23,2.35)
        # Acanthus sprays fan out below the central scallop.
        for end_y,end_z,mid in ((34,222,213),(48,217,207),(29,230,220)):
            carving.leaf((side*4,205),(side*11,mid),(side*(end_y-7),end_z-5),
                         (side*end_y,end_z),22.6,3.45)
        carving.flower(side*84,197.5,29,5)
    # A solid scallop with alternating recessed and projecting flutes and a scalloped rim.
    rows = []
    divisions = 68
    for radius in (.045,.16,.35,.57,.78,1):
        edge = []
        for j in range(divisions+1):
            a = math.radians(-64+128*j/divisions)
            flute = .5 + .5*math.cos(TAU*8*j/divisions)
            length = radius*(28 + 3.3*flute)
            y, z = .85*length*math.sin(a), 207+length*math.cos(a)
            edge.append((21+radius*2.8 + math.sin(radius*math.pi)*2 + radius*2.2*flute,y,z))
        rows.append(edge + [(18,y,z) for x,y,z in reversed(edge)])
    carving.loft(BURR,front,rows)
    carving.flower(0,207,26,4.5)
    for side in (-1,1):
        carving.turning(1,side*82,[(210,3.1),(212,4),(214,2.3),(216,1.9),(217,2.7),
                                   (220,3.3),(223,2.1),(226,.35)])


def build_case():
    carving = Carving()
    # The lower apron floats above four turned feet. The doors frame the existing rail.
    for side in (-1,1):
        for x in (-19,19):
            carving.turning(x,side*80,[(.4,3.5),(1.4,5),(3,5.5),(4,4),(6,6.1),(8,6.4),(10,4.2)])
        box((-1,side*86,108),(50,4,194),WALNUT,.6)
    box((-24,0,110),(3.2,171,196),WALNUT,.35)
    for z,depth,width,height,mat in [(10.4,56,179,3,WALNUT),(13.2,54,177,3.4,BURR),(16,58,181,3.5,WALNUT),
                                      (192,56,178,3,WALNUT),(197,57,180,8,BURR),(202,59,183,3,WALNUT),
                                      (205,61,185,3,BURR),(208.5,64,189,4.2,WALNUT)]:
        box((0,0,z),(depth,width,height),mat,min(1.1,height*.28))
    for side in (-1,1):
        y = side*81.4
        carving.turning(27,y,[(16,4.2),(18,5),(20.3,5),(21.4,3.5),(23.4,4.5),(25,4.8),
                              (28,3.4),(30,3.1),(31.5,4.1)])
        shaft = [(31.5+i*2.2,3.05+.65*math.sin(math.pi*i/67)) for i in range(68)]
        carving.turning(27,y,shaft,twist=True)
        carving.turning(27,y,[(178.9,3.6),(180,4.6),(182,4.5),(183,3.4),(185,4.1),
                              (188,5.1),(189.3,4.7),(190,5.4),(192,5.4)])
        # Petite carved relief on the frieze echoes the dress panels.
        for y0 in (18,47):
            carving.leaf((side*(y0-10),196),(side*(y0-3),202),(side*y0,197),
                         (side*(y0+13),198),28.9,1.6)
    # The drawer front follows the plinth and carries two brass bail pulls.
    box((26.7,0,12.2),(2.7,144,6.8),BURR,.7)
    for y in (-47,47):
        for s in (-1,1):
            circle = [(y+s*4+.98*math.cos(i*TAU/14),13+.98*math.sin(i*TAU/14)) for i in range(14)]
            carving.relief(circle,[(28.2,1,1),(29,1,1)],front,brass)
        carving.fillet(cubic((y-4,13),(y-4,8.8),(y+4,8.8),(y+4,13)),29.1,.55,.61,brass)
    cabinet_doors(carving)
    pediment(carving)
    carving.finish()
