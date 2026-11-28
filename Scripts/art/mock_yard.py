"""Blender: the yard-ground mock-up (Cheyenne, 2026-11-22: before and after pictures, keep or trash).  The yard round the
house is one flat dark dirt texture; this scatters what a neglected farmhouse yard has on it, in world space so it can keep
off the footpath, the house and the oil spill: fallen leaves, pine needles and twigs, stones and the odd fallen branch.
(Its clumps of flat grass blades were replaced on 2026-11-28 by the planted grass of Scripts/art/outdoor_grass.py.)  Six-metre chunks, pivot at the middle on the ground.
Materials by slot: RoadGrass (vertex colour, two-sided), RoadStone (vertex colour grey), Bark.
  SourceArt/Mock/SM_MockYard_<nn>.fbx, SourceArt/Mock/mock_yard.json
blender -b --factory-startup -P mock_yard.py"""
import bpy, bmesh, json, math, os, random
from mathutils import Vector, noise

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "SourceArt", "Mock")
os.makedirs(OUT, exist_ok=True)
random.seed(2026)
GRASS = os.environ.get("WC_MOCK_GRASS", "0") == "1"       # 2026-11-28: off; set WC_MOCK_GRASS=1 for the old flat blades
GROUND = -40.0
CH = 600.0
X0, X1, Y0, Y1 = -1150.0, 3900.0, -1650.0, 1650.0
HOUSE = (-30.0, 2894.0, -694.0, 694.0)
PATHS = [[(-710, 0), (-649, -340), (-536, -654), (-216, -1000), (53, -1184), (463, -1184), (760, -1000), (1410, -845), (2695, -836), (3230, -755), (3556, -745)],
         [(-710, 0), (-595, 400), (-507, 685), (-431, 911), (-325, 993), (825, 993), (1100, 875), (2610, 802), (3130, 760), (3335, 480), (3345, -482), (3230, -755)]]
KEEP_OFF = [((3100, -520), 170.0), ((3189, -488), 140.0)]       # the oil drum and its spill


def seg_dist(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / (ax * ax + ay * ay or 1.0)))
    return math.hypot(p[0] - a[0] - t * ax, p[1] - a[1] - t * ay)


def clear(x, y, margin=0.0):
    if HOUSE[0] - margin < x < HOUSE[1] + margin and HOUSE[2] - margin < y < HOUSE[3] + margin:
        return False
    for poly in PATHS:
        for a, b in zip(poly, poly[1:]):
            if seg_dist((x, y), a, b) < 118.0 + margin:
                return False
    return all(math.hypot(x - c[0], y - c[1]) > r for c, r in KEEP_OFF)


def n2(x, y, s):
    return noise.noise(Vector((x * s, y * s, 0.37)))


meta = {}
idx = 0
cx = X0
while cx < X1:
    cy = Y0
    while cy < Y1:
        mx, my = cx + CH / 2, cy + CH / 2
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bm = bmesh.new()
        col = bm.loops.layers.color.new("Col")
        uvl = bm.loops.layers.uv.new("UVMap")

        def L(x, y, z):
            return Vector(((x - mx) / 100.0, -(y - my) / 100.0, z / 100.0))       # Y mirrored for the FBX import

        def face(vs, mi, cols):
            try:
                f = bm.faces.new(vs)
            except ValueError:
                return
            f.material_index = mi
            f.smooth = True
            for lp, c in zip(f.loops, cols):
                lp[col] = (c[0], c[1], c[2], 1.0)
                lp[uvl].uv = (0.0, 0.0)

        def tuft(x, y, n, hmin, hmax, dry):
            for b in range(n):
                a = random.uniform(0, 2 * math.pi)
                r0 = random.uniform(0, 5.0)
                bx, by = x + math.cos(a) * r0, y + math.sin(a) * r0
                h = random.uniform(hmin, hmax)
                lean = random.uniform(0.1, 0.6)
                la = a + random.uniform(-0.6, 0.6)
                w = random.uniform(0.5, 1.1)
                sx, sy = -math.sin(a) * w / 2, math.cos(a) * w / 2
                tx, ty = bx + math.cos(la) * h * lean, by + math.sin(la) * h * lean
                mx_, my_ = bx + math.cos(la) * h * lean * 0.4, by + math.sin(la) * h * lean * 0.4
                g = random.uniform(0.0, 1.0)
                if not GRASS:                    # the clumps are planted as real grass now (Scripts/art/outdoor_grass.py); the dice are
                    continue                     # still thrown so the leaves, needles and stones land where they did before
                v = [bm.verts.new(L(bx - sx, by - sy, -0.5)), bm.verts.new(L(bx + sx, by + sy, -0.5)), bm.verts.new(L(mx_ + sx * 0.6, my_ + sy * 0.6, h * 0.55)),
                     bm.verts.new(L(mx_ - sx * 0.6, my_ - sy * 0.6, h * 0.55)), bm.verts.new(L(tx, ty, h * (1 - lean * 0.4)))]
                straw = (0.30 + 0.08 * g, 0.23 + 0.06 * g, 0.11 + 0.03 * g)
                olive = (0.07 + 0.03 * g, 0.08 + 0.04 * g, 0.03 + 0.01 * g)
                cc = tuple(straw[i] * dry + olive[i] * (1 - dry) for i in range(3))
                dk = tuple(c * 0.4 for c in cc)
                face((v[0], v[1], v[2], v[3]), 0, (dk, dk, cc, cc))
                face((v[3], v[2], v[4]), 0, (cc, cc, tuple(min(1, c * 1.2) for c in cc)))

        n_t = n_l = n_s = 0
        # dead grass and weeds: clumps, far thicker in patches and near the house walls and fence lines
        for k in range(int(CH * CH / 10000.0 * 11.0)):
            x, y = random.uniform(cx, cx + CH), random.uniform(cy, cy + CH)
            dens = 0.5 + 0.5 * n2(x, y, 0.004) + (0.35 if clear(x, y) and not clear(x, y, 90.0) else 0.0)     # thicker along walls and the path
            if random.random() > dens or not clear(x, y):
                continue
            tuft(x, y, random.randint(10, 26), 8.0, 42.0 if dens > 0.7 else 26.0, random.uniform(0.6, 1.0))
            n_t += 1
        # leaves: oak and maple, brown, rust, near-black where they have rotted
        for k in range(int(CH * CH / 10000.0 * 16.0)):
            x, y = random.uniform(cx, cx + CH), random.uniform(cy, cy + CH)
            if not clear(x, y, -40.0):
                continue
            Lf, Wl, a = random.uniform(4.0, 9.0), random.uniform(2.4, 5.0), random.uniform(0, 2 * math.pi)
            ca, sa = math.cos(a), math.sin(a)
            ring = []
            for i in range(8):
                t = 2 * math.pi * i / 8
                lx, ly = math.cos(t) * Lf / 2, math.sin(t) * Wl / 2 * (1.0 - 0.3 * math.cos(t))
                ring.append(bm.verts.new(L(x + ca * lx - sa * ly, y + sa * lx + ca * ly, 0.3 + 0.3 * abs(math.sin(t)) ** 2 + random.uniform(0, 0.2))))
            lc = random.choice([(0.26, 0.12, 0.04), (0.18, 0.09, 0.035), (0.08, 0.05, 0.025), (0.32, 0.18, 0.06), (0.14, 0.10, 0.05), (0.22, 0.16, 0.08)])
            face(ring, 0, [lc] * 8)
            n_l += 1
        # needles and twigs
        for k in range(int(CH * CH / 10000.0 * 3.0)):
            x, y = random.uniform(cx, cx + CH), random.uniform(cy, cy + CH)
            if not clear(x, y, -40.0):
                continue
            a = random.uniform(0, 2 * math.pi)
            ln = random.uniform(3.0, 7.0) if random.random() < 0.8 else random.uniform(10.0, 26.0)
            th = 0.12 if ln < 8 else 0.4
            p0 = L(x, y, 0.4)
            dv = Vector((math.cos(a) * ln / 100.0, -math.sin(a) * ln / 100.0, 0.0))
            sv = Vector((math.sin(a) * th / 100.0, math.cos(a) * th / 100.0, 0.0))
            cc = (0.13, 0.075, 0.035) if ln < 8 else (0.07, 0.055, 0.04)
            face([bm.verts.new(p0 - sv), bm.verts.new(p0 + sv), bm.verts.new(p0 + dv + sv), bm.verts.new(p0 + dv - sv)], 0, [cc] * 4)
        # stones, half sunk
        for k in range(int(CH * CH / 10000.0 * 0.35)):
            x, y = random.uniform(cx, cx + CH), random.uniform(cy, cy + CH)
            if not clear(x, y, -20.0):
                continue
            r = random.uniform(2.0, 9.0)
            ret = bmesh.ops.create_icosphere(bm, subdivisions=2 if r > 5 else 1, radius=r / 100.0)
            sz = random.uniform(0.35, 0.6)
            tone = random.choice((0.12, 0.16, 0.2, 0.24))
            for v in ret["verts"]:
                c = v.co
                c.z *= sz
                c *= 1.0 + 0.25 * noise.noise(c * 60.0 + Vector((k, 1, 2)))
                v.co = c + L(x, y, -r * 0.2)
            for f in {f for v in ret["verts"] for f in v.link_faces}:
                f.material_index = 1
                for lp in f.loops:
                    lp[col] = (tone, tone * 0.97, tone * 0.92, 1.0)
            n_s += 1
        # a fallen branch now and then
        if random.random() < 0.6:
            x, y = random.uniform(cx, cx + CH), random.uniform(cy, cy + CH)
            if clear(x, y, 80.0):
                a = random.uniform(0, 2 * math.pi)
                Lb = random.uniform(80, 220)
                pts = [L(x + math.cos(a) * Lb * t + 6 * math.sin(t * 7), y + math.sin(a) * Lb * t, 3.0 + 4.0 * math.sin(t * 3.1)) for t in [i / 8 for i in range(9)]]
                rings = []
                for i, p in enumerate(pts):
                    rr = (3.2 - 2.4 * i / 8) / 100.0
                    d = (pts[min(8, i + 1)] - pts[max(0, i - 1)]).normalized()
                    n1 = d.cross(Vector((0, 0, 1))).normalized()
                    n2_ = d.cross(n1)
                    rings.append([bm.verts.new(p + rr * (math.cos(2 * math.pi * j / 8) * n1 + math.sin(2 * math.pi * j / 8) * n2_)) for j in range(8)])
                bf = []
                for i in range(8):
                    for j in range(8):
                        f = bm.faces.new((rings[i][j], rings[i][(j + 1) % 8], rings[i + 1][(j + 1) % 8], rings[i + 1][j]))
                        f.material_index = 2
                        bf.append(f)
                        for lp in f.loops:
                            lp[col] = (0.2, 0.2, 0.2, 1.0)
                            lp[uvl].uv = (j / 8, i / 2)
                bmesh.ops.reverse_faces(bm, faces=bf)                    # (built through the Y mirror, so turned inside out)
        if len(bm.faces) < 50:
            bm.free()
            cy += CH
            continue
        name = f"SM_MockYard_{idx:02d}"
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(ob)
        for m in ("RoadGrass", "RoadStone", "Bark"):
            ob.data.materials.append(bpy.data.materials.new(m))
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + ".fbx"), use_selection=True, object_types={"MESH"}, mesh_smooth_type="FACE",
                                 add_leaf_bones=False, bake_anim=False, apply_scale_options="FBX_SCALE_NONE", colors_type="LINEAR")
        meta[name] = [mx, my, GROUND]
        print(f"MOCKYARD {name}: {len(me.vertices)} verts, {n_t} clumps, {n_l} leaves, {n_s} stones")
        idx += 1
        cy += CH
    cx += CH
json.dump(meta, open(os.path.join(OUT, "mock_yard.json"), "w"), indent=1)
print("MOCKYARD done", len(meta))
