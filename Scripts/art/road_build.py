"""Blender: the gravel footpath that goes round the house, as real geometry (Cheyenne, 2026-11-21: "there is a gravel road
that goes around the outside of the house; this needs work, it's got no detail whatsoever and needs hella detail"; 2026-11-22:
"it's not really a road, it's a path ... it's already there, just needs detail").

Follows the two routes of Scripts/level/yard_access.py (LEFT and RIGHT) at the width of the old flat path, rounded at the
bends, and builds each as a run of five-metre chunks.  Each chunk: the bed of the path (a shallow trodden line wandering down
the middle where years of feet packed the gravel into the dirt, loose gravel thicker towards the edges, the edges ragged
where they sink into the yard), loose stones kicked to the sides, a few fist-sized rocks, dead grass and plantain weeds
creeping in from the verges, pine needles, twigs and dead leaves, and rain standing in the low places of the trodden line.
Units are metres (1 m = 100 cm in Unreal); chunk pivots are at their middle on the ground.
Vertex colour on the bed: R trodden, G verge (dirt and moss), B damp.
  <out_dir>/SM_Road_<L|R>_<nn>.fbx, <out_dir>/road_chunks.json (pivot of each chunk in Unreal cm), preview/road_*.png
blender -b --factory-startup -P road_build.py -- <out_dir> [--preview]"""
import bpy, bmesh, json, math, os, random, sys
from mathutils import Vector, noise

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
PREVIEW = "--preview" in argv
os.makedirs(OUT, exist_ok=True)
random.seed(1987)
GROUND = -40.0                                              # the yard's ground, Unreal cm

LEFT = [(-710, 0), (-649, -340), (-536, -654), (-216, -1000), (53, -1184), (463, -1184), (760, -1000), (1410, -845), (2695, -836), (3230, -755), (3556, -745)]
RIGHT = [(-710, 0), (-595, 400), (-507, 685), (-431, 911), (-325, 993), (825, 993), (1100, 875), (2610, 802), (3130, 760), (3335, 480), (3345, -482), (3230, -755)]


def chaikin(pts, n=4):
    for _ in range(n):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out += [(a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25), (a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75)]
        out.append(pts[-1])
        pts = out
    return pts


def resample(pts, step):
    out = [pts[0]]
    carry = 0.0
    for a, b in zip(pts, pts[1:]):
        seg = math.dist(a, b)
        t = step - carry
        while t <= seg:
            out.append((a[0] + (b[0] - a[0]) * t / seg, a[1] + (b[1] - a[1]) * t / seg))
            t += step
        carry = seg - (t - step)
    if math.dist(out[-1], pts[-1]) > step * 0.3:
        out.append(pts[-1])
    return out


def n1(x, s=0.0):
    return noise.noise(Vector((x, s, 0.31)))


def mat(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    return m


BED_Z = 3.4                                                 # loose gravel built up on the yard, cm
TROD_Z = 0.9                                                # how far feet have pressed the middle down


def build_side(tag, poly, width_at, zoff):
    # centre line in Unreal cm, every 12 cm, with the arc length and the direction at each sample
    pts = resample(chaikin(poly, 4), 12.0)
    s_acc, rows = 0.0, []
    for i, p in enumerate(pts):
        if i:
            s_acc += math.dist(pts[i - 1], p)
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        d = (b[0] - a[0], b[1] - a[1])
        L = math.hypot(*d) or 1.0
        rows.append((p, s_acc, (d[0] / L, d[1] / L)))
    total = rows[-1][1]
    nchunks = max(1, round(total / 500.0))
    chunks = []
    for ci in range(nchunks):
        s0, s1 = total * ci / nchunks, total * (ci + 1) / nchunks
        sel = [r for r in rows if s0 - 13 <= r[1] <= s1 + 13]
        if len(sel) < 2:
            continue
        mid = sel[len(sel) // 2][0]
        chunks.append((ci, sel, mid))
    meta = {}
    for ci, sel, mid in chunks:
        name = f"SM_Road_{tag}_{ci:02d}"
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bm = bmesh.new()
        col = bm.loops.layers.color.new("Col")
        uvl = bm.loops.layers.uv.new("UVMap")

        def local(x, y, z):
            return ((x - mid[0]) / 100.0, (y - mid[1]) / 100.0, z / 100.0)

        # ------------------------------------------------------------ puddles: where the trodden line dips
        puddles = []
        for i in range(3, len(sel), 7):
            p, s, d = sel[i]
            dip = n1(s * 0.0045, 9.0)
            if dip < 0.25 or random.random() < 0.35:
                continue
            nx, ny = -d[1], d[0]
            w = width_at(p[0], p[1]) / 2
            uo = 0.14 * n1(s * 0.011, 6.0) + random.uniform(-0.10, 0.10)
            puddles.append((p[0] + nx * uo * w, p[1] + ny * uo * w, d, random.uniform(55, 95), random.uniform(32, 50), 1.2 + 1.0 * dip))
        if len(puddles) > 2:
            puddles = random.sample(puddles, 2)

        def pud(x, y):
            """How far the bed is pressed down by the puddles here (cm), and how wet it is round them (0..1)."""
            dz, wet = 0.0, 0.0
            for (cx, cy, d, L, Wd, depth) in puddles:
                lx, ly = (x - cx) * d[0] + (y - cy) * d[1], -(x - cx) * d[1] + (y - cy) * d[0]
                q = (lx / (L * 0.62)) ** 2 + (ly / (Wd * 0.62)) ** 2
                dz += depth * math.exp(-q)
                wet = max(wet, math.exp(-q * 0.3))
            return dz, wet

        # ------------------------------------------------------------ the bed
        NU = 32
        grid = []
        for (p, s, d) in sel:
            nx, ny = -d[1], d[0]                                     # to the left of the direction of travel
            w = width_at(p[0], p[1])
            hw_l = w / 2 * (0.93 + 0.05 * n1(s * 0.004, 1.0) + 0.05 * n1(s * 0.035, 2.0) + 0.035 * n1(s * 0.16, 12.0))
            hw_r = w / 2 * (0.93 + 0.05 * n1(s * 0.004, 3.0) + 0.05 * n1(s * 0.035, 4.0) + 0.035 * n1(s * 0.16, 13.0))
            walk = 0.14 * n1(s * 0.011, 6.0)                         # where feet go wanders from side to side
            tw = 0.36 + 0.07 * n1(s * 0.02, 8.0)
            row = []
            for j in range(NU + 1):
                u = -1.0 + 2.0 * j / NU
                hw = hw_l if u < 0 else hw_r
                off = u * hw
                x, y = p[0] + nx * off, p[1] + ny * off
                au = abs(u)
                trod = math.exp(-((u - walk) / tw) ** 2) * (0.75 + 0.25 * n1(x * 0.02, y * 0.02 + 3.0))
                z = BED_Z
                z -= TROD_Z * trod
                z += 0.6 * max(0.0, au - 0.45)                                        # gravel kicked up towards the sides
                z -= 6.0 * max(0.0, (au - 0.72) / 0.28) ** 1.7                        # the edges go down under the grass
                z += 0.30 * n1(x * 0.06, y * 0.06) + 0.12 * n1(x * 0.25, y * 0.25)
                pz, pw = pud(x, y)
                z -= pz
                verge = min(1.0, max(0.0, (au - 0.40) / 0.32)) ** 1.1 * (0.8 + 0.2 * n1(x * 0.05, y * 0.05 + 7.0))
                verge = max(verge, 0.6 * min(1.0, max(0.0, n1(x * 0.013, y * 0.013 + 11.0) - 0.2) * 2.0) * min(1.0, au * 1.6))   # moss and dirt patches
                damp = min(1.0, max(pw, 0.6 * min(1.0, max(0.0, n1(x * 0.009, y * 0.009 + 21.0) - 0.15) * 2.0)))
                v = bm.verts.new(local(x, y, z + zoff))
                row.append((v, (min(1.0, trod * 1.2), min(1.0, verge), damp), (x / 120.0, y / 120.0)))
            grid.append(row)
        bm.verts.ensure_lookup_table()
        for i in range(len(grid) - 1):
            for j in range(NU):
                quad = [grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]]
                f = bm.faces.new([q[0] for q in quad])
                f.material_index = 0
                f.smooth = True
                for loop, q in zip(f.loops, quad):
                    loop[col] = (q[1][0], q[1][1], q[1][2], 1.0)
                    loop[uvl].uv = q[2]
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        # ------------------------------------------------------------ loose stones
        def stone(x, y, r, zb, tone, warm, k, sink=0.25):
            ret = bmesh.ops.create_icosphere(bm, subdivisions=1 if r < 2.5 else 2, radius=r / 100.0)
            ang = random.uniform(0, 2 * math.pi)
            sx, sy, sz = random.uniform(0.8, 1.3), random.uniform(0.6, 1.0), random.uniform(0.35, 0.65)
            base = zb / 100.0
            for v in ret["verts"]:
                c = v.co
                c.x, c.y, c.z = c.x * sx, c.y * sy, c.z * sz
                c *= 1.0 + 0.25 * noise.noise(c * 90.0 + Vector((k, k * 0.3, 1)))
                cx, cy = c.x * math.cos(ang) - c.y * math.sin(ang), c.x * math.sin(ang) + c.y * math.cos(ang)
                v.co = Vector(((x - mid[0]) / 100.0 + cx, (y - mid[1]) / 100.0 + cy, base + c.z + r / 100.0 * sz * sink))
            for f in {f for v in ret["verts"] for f in v.link_faces}:
                f.material_index = 1
                f.smooth = r > 2.5
                for loop in f.loops:
                    sh = 0.7 if loop.vert.co.z < base + r / 100.0 * 0.1 else 1.0          # dirt-darkened underneath
                    loop[col] = ((tone + warm) * sh, tone * sh, (tone - warm) * sh, 1.0)
                    loop[uvl].uv = ((x + loop.vert.co.x * 100) / 120.0, (y + loop.vert.co.y * 100) / 120.0)

        # kicked out of the trodden line towards the sides and off into the verge; only a few left in the middle
        for k in range(int(len(sel) * 3.6)):
            rp, s, d = random.choice(sel)
            band = random.random()
            if band < 0.55:
                u, zb = random.choice([-1, 1]) * random.uniform(0.55, 0.95), BED_Z - 0.4 + zoff
            elif band < 0.85:
                u, zb = random.choice([-1, 1]) * random.uniform(0.95, 1.25), -0.4 + zoff
            else:
                u, zb = random.uniform(-0.55, 0.55), BED_Z - TROD_Z + zoff
            nx, ny = -d[1], d[0]
            w = width_at(rp[0], rp[1]) / 2
            x, y = rp[0] + nx * u * w + d[0] * random.uniform(-6, 6), rp[1] + ny * u * w + d[1] * random.uniform(-6, 6)
            if pud(x, y)[0] > 0.4:
                continue
            stone(x, y, random.uniform(0.9, 2.8) if random.random() < 0.8 else random.uniform(2.8, 4.2), zb, random.choice([0.16, 0.20, 0.24, 0.28, 0.33]), random.uniform(-0.03, 0.04), k)
        # a few fist-sized rocks half sunk at the edges
        for k in range(max(1, len(sel) // 14)):
            rp, s, d = random.choice(sel)
            nx, ny = -d[1], d[0]
            w = width_at(rp[0], rp[1]) / 2
            u = random.choice([-1, 1]) * random.uniform(0.85, 1.25)
            stone(rp[0] + nx * u * w, rp[1] + ny * u * w, random.uniform(4.0, 7.5), -1.5 + zoff, random.choice([0.14, 0.18, 0.22]),
                  random.uniform(-0.02, 0.03), 500 + k, sink=-0.1)

        # ------------------------------------------------------------ dead grass and weeds creeping in from the verges
        def tuft(x, y, z, n, hmin, hmax, dry):
            for b in range(n):
                a = random.uniform(0, 2 * math.pi)
                r0 = random.uniform(0, 4.0)
                bx, by = x + math.cos(a) * r0, y + math.sin(a) * r0
                h = random.uniform(hmin, hmax)
                lean = random.uniform(0.1, 0.55)
                la = a + random.uniform(-0.6, 0.6)
                wdt = random.uniform(0.5, 1.0)
                base_l = Vector(((bx - mid[0] - math.sin(a) * wdt / 2) / 100.0, (by - mid[1] + math.cos(a) * wdt / 2) / 100.0, z / 100.0))
                base_r = Vector(((bx - mid[0] + math.sin(a) * wdt / 2) / 100.0, (by - mid[1] - math.cos(a) * wdt / 2) / 100.0, z / 100.0))
                midp = Vector(((bx - mid[0] + math.cos(la) * h * lean * 0.4) / 100.0, (by - mid[1] + math.sin(la) * h * lean * 0.4) / 100.0, (z + h * 0.55) / 100.0))
                tip = Vector(((bx - mid[0] + math.cos(la) * h * lean) / 100.0, (by - mid[1] + math.sin(la) * h * lean) / 100.0, (z + h * (1 - lean * 0.4)) / 100.0))
                vs = [bm.verts.new(base_l), bm.verts.new(base_r), bm.verts.new(midp + Vector((math.sin(a) * wdt * 0.3 / 100, -math.cos(a) * wdt * 0.3 / 100, 0))),
                      bm.verts.new(midp - Vector((math.sin(a) * wdt * 0.3 / 100, -math.cos(a) * wdt * 0.3 / 100, 0))), bm.verts.new(tip)]
                g = random.uniform(0.0, 1.0)
                straw = (0.20 + 0.06 * g, 0.15 + 0.05 * g, 0.07 + 0.02 * g)
                olive = (0.07 + 0.03 * g, 0.08 + 0.04 * g, 0.03 + 0.01 * g)
                cc = tuple(straw[i] * dry + olive[i] * (1 - dry) for i in range(3))
                dark = tuple(c * 0.45 for c in cc)
                for fv, shade in (((vs[0], vs[1], vs[2], vs[3]), (dark, dark, cc, cc)), ((vs[3], vs[2], vs[4]), (cc, cc, tuple(min(1, c * 1.2) for c in cc)))):
                    try:
                        f = bm.faces.new(fv)
                    except ValueError:
                        continue
                    f.material_index = 2
                    f.smooth = True
                    for loop, sh in zip(f.loops, shade):
                        loop[col] = (sh[0], sh[1], sh[2], 1.0)
                        loop[uvl].uv = (0.0, 0.0)

        def rosette(x, y, z, size):
            """A broadleaf plantain, flat to the ground: five to eight oval leaves round a centre."""
            n = random.randint(5, 8)
            c0 = bm.verts.new(local(x, y, z + 0.4))
            g = random.uniform(0.0, 1.0)
            dry = random.uniform(0.0, 0.5)
            green = (0.045 + 0.03 * g, 0.06 + 0.035 * g, 0.022 + 0.01 * g)
            leafc = tuple(green[i] * (1 - dry) + (0.12, 0.09, 0.04)[i] * dry for i in range(3))
            for i in range(n):
                a = 2 * math.pi * i / n + random.uniform(-0.25, 0.25)
                L = size * random.uniform(0.7, 1.1)
                Wl = L * 0.32
                ca, sa = math.cos(a), math.sin(a)
                vs = [c0]
                for (lx, ly) in ((L * 0.55, Wl), (L, 0.0), (L * 0.55, -Wl)):
                    vs.append(bm.verts.new(local(x + ca * lx - sa * ly, y + sa * lx + ca * ly, z + 0.4 + 0.10 * lx)))
                for tri in ((vs[0], vs[1], vs[2]), (vs[0], vs[2], vs[3])):
                    try:
                        f = bm.faces.new(tri)
                    except ValueError:
                        continue
                    f.material_index = 2
                    f.smooth = True
                    for loop in f.loops:
                        sh = 0.55 if loop.vert is c0 else 1.0
                        loop[col] = (leafc[0] * sh, leafc[1] * sh, leafc[2] * sh, 1.0)
                        loop[uvl].uv = (0.0, 0.0)

        for (p, s, d) in sel[::2]:
            nx, ny = -d[1], d[0]
            w = width_at(p[0], p[1]) / 2
            for side in (-1, 1):
                # both verges, thick and tall, half in the yard
                for k in range(3):
                    off = side * w * random.uniform(0.85, 1.15)
                    tuft(p[0] + nx * off + d[0] * random.uniform(-6, 6), p[1] + ny * off + d[1] * random.uniform(-6, 6), -0.5 + zoff,
                         random.randint(12, 26), 6.0, 24.0, random.uniform(0.6, 1.0))
                # short grass creeping onto the gravel at the edge
                if random.random() < 0.55:
                    off = side * w * random.uniform(0.62, 0.82)
                    tuft(p[0] + nx * off + d[0] * random.uniform(-6, 6), p[1] + ny * off + d[1] * random.uniform(-6, 6), BED_Z - 0.8 + zoff,
                         random.randint(5, 12), 2.5, 9.0, random.uniform(0.4, 0.9))
            # a lone weed in the loose gravel now and then, never in the trodden line
            if random.random() < 0.10:
                off = random.choice([-1, 1]) * w * random.uniform(0.40, 0.65)
                tuft(p[0] + nx * off, p[1] + ny * off, BED_Z - 0.6 + zoff, random.randint(4, 9), 2.0, 8.0, random.uniform(0.3, 0.8))
            if random.random() < 0.16:
                off = random.choice([-1, 1]) * w * random.uniform(0.45, 0.80)
                rosette(p[0] + nx * off, p[1] + ny * off, BED_Z - 0.5 + zoff, random.uniform(4.0, 8.0))

        # ------------------------------------------------------------ pine needles and twigs, thicker at the sides
        for k in range(len(sel) * 2):
            rp, s, d = random.choice(sel)
            nx, ny = -d[1], d[0]
            w = width_at(rp[0], rp[1]) / 2
            u = random.choice([-1, 1]) * random.uniform(0.55, 1.0) if random.random() < 0.7 else random.uniform(-0.6, 0.6)
            x, y = rp[0] + nx * u * w + random.uniform(-6, 6), rp[1] + ny * u * w + random.uniform(-6, 6)
            if pud(x, y)[0] > 0.4:
                continue
            a = random.uniform(0, 2 * math.pi)
            ln = random.uniform(2.5, 6.0) if random.random() < 0.85 else random.uniform(8.0, 20.0)
            th = 0.12 if ln < 7 else 0.35
            p0 = Vector(local(x, y, BED_Z + 0.2 + zoff))
            dv = Vector((math.cos(a) * ln / 100.0, math.sin(a) * ln / 100.0, 0.0))
            sv = Vector((-math.sin(a) * th / 100.0, math.cos(a) * th / 100.0, 0.0))
            vs = [bm.verts.new(p0 - sv), bm.verts.new(p0 + sv), bm.verts.new(p0 + dv + sv), bm.verts.new(p0 + dv - sv)]
            f = bm.faces.new(vs)
            f.material_index = 2
            cc = (0.13, 0.075, 0.035) if ln < 7 else (0.08, 0.06, 0.045)
            for loop in f.loops:
                loop[col] = (cc[0], cc[1], cc[2], 1.0)
                loop[uvl].uv = (0.0, 0.0)

        # ------------------------------------------------------------ dead leaves blown onto the path
        for k in range(len(sel) // 3):
            rp, s, d = random.choice(sel)
            nx, ny = -d[1], d[0]
            w = width_at(rp[0], rp[1]) / 2
            u = random.uniform(-1.0, 1.0)
            x, y = rp[0] + nx * u * w, rp[1] + ny * u * w
            if pud(x, y)[0] > 0.4:
                continue
            L, Wl, a = random.uniform(3.5, 7.0), random.uniform(1.6, 3.0), random.uniform(0, 2 * math.pi)
            ca, sa = math.cos(a), math.sin(a)
            ring = []
            for i in range(8):
                t = 2 * math.pi * i / 8
                lx, ly = math.cos(t) * L / 2, math.sin(t) * Wl / 2 * (1.0 - 0.3 * math.cos(t))
                curl = 0.25 * (abs(math.sin(t)) ** 2)
                ring.append(bm.verts.new(local(x + ca * lx - sa * ly, y + sa * lx + ca * ly, BED_Z + 0.3 + zoff + curl)))
            f = bm.faces.new(ring)
            f.material_index = 2
            lc = random.choice([(0.16, 0.075, 0.03), (0.11, 0.06, 0.03), (0.07, 0.045, 0.025), (0.20, 0.12, 0.04)])
            for loop in f.loops:
                loop[col] = (lc[0], lc[1], lc[2], 1.0)
                loop[uvl].uv = (0.0, 0.0)

        # ------------------------------------------------------------ standing rain in the pressed-down places
        for (cx, cy, d, L, Wd, depth) in puddles:
            nx, ny = -d[1], d[0]
            zc = BED_Z - TROD_Z - depth * 0.62 + zoff
            segs = 40
            centre = bm.verts.new(local(cx, cy, zc))
            ring = []
            for k in range(segs):
                a = 2 * math.pi * k / segs
                e = 0.80 + 0.20 * n1(math.cos(a) * 1.5 + cx * 0.01, math.sin(a) * 1.5 + cy * 0.01)
                lx, ly = math.cos(a) * L / 2 * e, math.sin(a) * Wd / 2 * e
                ring.append(bm.verts.new(local(cx + d[0] * lx + nx * ly, cy + d[1] * lx + ny * ly, zc)))
            for k in range(segs):
                f = bm.faces.new((centre, ring[k], ring[(k + 1) % segs]))
                f.material_index = 3
                f.smooth = True
                for loop in f.loops:
                    loop[col] = (0.0, 0.0, 0.0, 1.0)
                    loop[uvl].uv = ((mid[0] + loop.vert.co.x * 100) / 120.0, (mid[1] + loop.vert.co.y * 100) / 120.0)
            # a dead leaf or two and some needles floating on it
            for k in range(random.randint(1, 3)):
                a, rr = random.uniform(0, 2 * math.pi), random.uniform(0.0, 0.3)
                x, y = cx + math.cos(a) * L * rr, cy + math.sin(a) * Wd * rr
                Ll, Wl, ang = random.uniform(3.5, 6.5), random.uniform(1.6, 2.8), random.uniform(0, 2 * math.pi)
                ring = [bm.verts.new(local(x + math.cos(ang) * math.cos(t) * Ll / 2 - math.sin(ang) * math.sin(t) * Wl / 2,
                                           y + math.sin(ang) * math.cos(t) * Ll / 2 + math.cos(ang) * math.sin(t) * Wl / 2, zc + 0.06))
                        for t in [2 * math.pi * i / 8 for i in range(8)]]
                f = bm.faces.new(ring)
                f.material_index = 2
                lc = random.choice([(0.12, 0.06, 0.025), (0.07, 0.045, 0.025)])
                for loop in f.loops:
                    loop[col] = (lc[0], lc[1], lc[2], 1.0)
                    loop[uvl].uv = (0.0, 0.0)

        # Unreal's FBX import mirrors Y (Blender is right-handed, Unreal left-handed): mirror here so it lands the right way round
        for v in bm.verts:
            v.co.y = -v.co.y
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(ob)
        for m in ("Road", "RoadStone", "RoadGrass", "RoadWater"):
            ob.data.materials.append(mat(m))
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + ".fbx"), use_selection=True, object_types={"MESH"}, mesh_smooth_type="FACE",
                                 add_leaf_bones=False, bake_anim=False, apply_scale_options="FBX_SCALE_NONE", colors_type="LINEAR")
        meta[name] = [round(mid[0], 1), round(mid[1], 1), GROUND]
        print(f"ROAD {name}: {len(me.vertices)} verts, {len(puddles)} puddles")
        if PREVIEW and ci in (0, len(chunks) // 2):
            preview(ob, name)
    return meta


def preview(ob, name):
    sc = bpy.context.scene
    for m in ob.data.materials:
        m.use_nodes = True
        nt = m.node_tree
        b = nt.nodes["Principled BSDF"]
        a = nt.nodes.new("ShaderNodeVertexColor")
        a.layer_name = "Col"
        if m.name == "Road":
            mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
            mix.inputs[6].default_value = (0.20, 0.18, 0.15, 1); mix.inputs[7].default_value = (0.05, 0.035, 0.025, 1)
            sep = nt.nodes.new("ShaderNodeSeparateColor")
            nt.links.new(a.outputs["Color"], sep.inputs[0])
            nt.links.new(sep.outputs["Green"], mix.inputs["Factor"])
            nt.links.new(mix.outputs[2], b.inputs["Base Color"])
            b.inputs["Roughness"].default_value = 0.8
        elif m.name == "RoadWater":
            b.inputs["Base Color"].default_value = (0.01, 0.012, 0.012, 1); b.inputs["Roughness"].default_value = 0.03
        else:
            nt.links.new(a.outputs["Color"], b.inputs["Base Color"])
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.location = (0.0, -3.2, 1.6)
    cam.rotation_euler = (math.radians(62), 0, 0)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    sc.collection.objects.link(sun)
    sc.world = bpy.data.worlds.new("w")
    sc.world.use_nodes = True
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.25, 0.27, 1)
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 1200, 700
    os.makedirs(os.path.join(OUT, "preview"), exist_ok=True)
    sc.render.filepath = os.path.join(OUT, "preview", name + ".png")
    bpy.ops.render.render(write_still=True)


# the width of the old flat path (YardTrail planes), kept so the path stays where it was and as wide
def width_left(x, y):
    return 184.0


def width_right(x, y):
    return 146.0 if -510 < x < 840 else 184.0


meta = {}
meta.update(build_side("L", LEFT, width_left, 0.0))
meta.update(build_side("R", RIGHT, width_right, 0.3))
json.dump(meta, open(os.path.join(OUT, "road_chunks.json"), "w"), indent=1)
print("ROAD done", len(meta), "chunks")
