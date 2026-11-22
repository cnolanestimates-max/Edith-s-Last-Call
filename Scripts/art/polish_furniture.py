"""Blender: what the empty glass cabinets in the house hold (Cheyenne, 2026-11-21: "tall what look like they are supposed
to be book shelves or wardrobes ... turn them into something that actually makes sense and looks good").

Each set is one mesh in the local space of the cabinet it goes in (Unreal cm: X across, +Y out through the doors, Z up),
built from the house's own materials by slot name (/Game/WC/Materials/<slot>), so the level only drops it in at the
cabinet's transform:
  SM_PolishChinaSet     the dining-room china cabinet (OldWest SM_Cabinet_02a): two shelves, Edith's good china (dinner
                        plates stood up and stacked, cups on saucers, a tureen, bowls, a gravy boat, a jug), the crystal
                        on top, one cup knocked on its side and a plate dropped askew
  SM_PolishDenSet       the same cabinet in Walter's den: shelves of books, a decoy duck, a cigar box, shell boxes, a
                        bottle of whiskey and two glasses
  SM_PolishKitchenSet   the kitchen's glass-fronted cabinet (kit SM_Cabinet_Medicine_Glass_Open, its own medicine
                        hidden): canned goods, plates and bowls, mugs and glasses, jars of preserves, a cereal box
  SM_PolishMedicineSet  the same cabinet in the sickroom: amber medicine bottles, pill tins, bandage rolls, a kidney
                        dish, a hot-water bottle, boxes of gauze and a bedpan
and two pieces of furniture that replace kit ones outright (pivot at the middle of the floor, back where the kit back was):
  SM_PolishDanielWardrobe   Danny's walnut wardrobe (for the plain kit Wardrobe_Tall), his army duffel on top
  SM_PolishPantryCupboard   a painted pantry cupboard with glazed doors (for the hospital Cabinet_Steel_Tall)
blender -b --factory-startup -P polish_furniture.py -- [names...]"""
import bpy, bmesh, math, random, sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "SourceArt/Props/Polish"
OUT.mkdir(parents=True, exist_ok=True)
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
TAU = math.tau

CER, GOLD, GLASS, WOOD, TRIM, BRASS = "M_ItemCeramic", "M_ItemGold", "M_JarGlass", "MI_WoodDark", "MI_WoodTrim", "MI_Brass"
STEEL, CARD, PAPER, SHEET = "M_ItemSteel", "MI_Cardboard", "MI_PaperOld", "MI_Sheet"
BOOKS = ["MI_LeatherRed", "MI_LeatherGreen", "MI_LeatherTan", "MI_LeatherBlue", "MI_Leather", "MI_FabricBlue", "MI_FabricDark",
         "MI_FabricGreen", "MI_FabricRed"]
parts = []


def V(x, y, z):
    """Unreal cm to Blender metres; Y is mirrored because the FBX import mirrors it back."""
    return (x / 100.0, -y / 100.0, z / 100.0)


def mat(name):
    return bpy.data.materials.get(name) or bpy.data.materials.new(name)


def obj(bm, m, smooth=True):
    me = bpy.data.meshes.new("p")
    bm.to_mesh(me)
    bm.free()
    for f in me.polygons:
        f.use_smooth = smooth
    o = bpy.data.objects.new("p", me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(m))
    if not o.data.uv_layers:
        o.data.uv_layers.new(name="UVMap")
    parts.append(o)
    return o


def xform(co, at, yaw=0.0, tilt=(0.0, 0.0)):
    """Local cm point -> placed cm point: tilt (about X, then Y, degrees), yaw about Z, then move to at."""
    x, y, z = co
    ax, ay = math.radians(tilt[0]), math.radians(tilt[1])
    y, z = y * math.cos(ax) - z * math.sin(ax), y * math.sin(ax) + z * math.cos(ax)
    x, z = x * math.cos(ay) + z * math.sin(ay), -x * math.sin(ay) + z * math.cos(ay)
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    return (at[0] + x * c - y * s, at[1] + x * s + y * c, at[2] + z)


def lathe(prof, m, at, seg=32, yaw=0.0, tilt=(0.0, 0.0), sx=1.0, sy=1.0, smooth=True):
    """Spin a (radius, height) profile round Z, in cm.  A radius of 0 closes the end to a point."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    rings = []
    for r, z in prof:
        if r < 1e-4:
            rings.append([bm.verts.new(V(*xform((0, 0, z), at, yaw, tilt)))])
        else:
            rings.append([bm.verts.new(V(*xform((r * math.cos(TAU * i / seg) * sx, r * math.sin(TAU * i / seg) * sy, z), at, yaw, tilt))) for i in range(seg)])
    L = 0.0
    lens = [0.0]
    for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
        L += math.hypot(r1 - r0, z1 - z0)
        lens.append(L)
    for k in range(len(rings) - 1):
        a, b = rings[k], rings[k + 1]
        for i in range(seg):
            j = (i + 1) % seg
            if len(a) == 1 and len(b) == 1:
                continue
            if len(a) == 1:
                vs = (a[0], b[j], b[i])
            elif len(b) == 1:
                vs = (a[i], a[j], b[0])
            else:
                vs = (a[i], a[j], b[j], b[i])
            try:
                f = bm.faces.new(vs)
            except ValueError:
                continue
            for lp in f.loops:
                ring_k = k if lp.vert in a else k + 1
                idx = (a if lp.vert in a else b).index(lp.vert)
                lp[uv].uv = (idx / seg * 2.0, lens[ring_k] / 12.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(bm, m, smooth)


def box(size, at, m, yaw=0.0, tilt=(0.0, 0.0), bevel=0.15):
    sx, sy, sz = size
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = V(*xform((v.co.x * sx, v.co.y * sy, v.co.z * sz + sz / 2), at, yaw, tilt))
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        n = f.normal
        for lp in f.loops:
            c = lp.vert.co
            a_, b_ = (c.y if abs(n.x) > 0.5 else c.x) * 4.0, (c.y if abs(n.z) > 0.5 else c.z) * 4.0
            # the walnut veneer: its figure runs up the doors and sides, about 60 cm to a repeat, like Edith's armoire
            lp[uv].uv = (b_ * 0.42, a_ * 0.42) if m == "M_HarrowWalnut" else (a_, b_)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel / 100.0, segments=1, affect="EDGES", clamp_overlap=True)
    return obj(bm, m, smooth=False)


def tube(pts, r, m, seg=8):
    """A round rod through cm points (handles, rims)."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    rings = []
    for k, p in enumerate(pts):
        a, b = pts[max(0, k - 1)], pts[min(len(pts) - 1, k + 1)]
        d = [b[i] - a[i] for i in range(3)]
        L = math.sqrt(sum(c * c for c in d)) or 1.0
        d = [c / L for c in d]
        up = (0, 0, 1) if abs(d[2]) < 0.9 else (1, 0, 0)
        n1 = [d[1] * up[2] - d[2] * up[1], d[2] * up[0] - d[0] * up[2], d[0] * up[1] - d[1] * up[0]]
        l1 = math.sqrt(sum(c * c for c in n1))
        n1 = [c / l1 for c in n1]
        n2 = [d[1] * n1[2] - d[2] * n1[1], d[2] * n1[0] - d[0] * n1[2], d[0] * n1[1] - d[1] * n1[0]]
        rings.append([bm.verts.new(V(*[p[i] + r * (math.cos(TAU * j / seg) * n1[i] + math.sin(TAU * j / seg) * n2[i]) for i in range(3)])) for j in range(seg)])
    for k in range(len(rings) - 1):
        for j in range(seg):
            f = bm.faces.new((rings[k][j], rings[k][(j + 1) % seg], rings[k + 1][(j + 1) % seg], rings[k + 1][j]))
            for lp in f.loops:
                lp[uv].uv = (j / seg, k / len(rings))
    return obj(bm, m)


def export(name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts:
        o.data.uv_layers.active.name = "UVMap"
        o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    bpy.ops.export_scene.fbx(filepath=str(OUT / (name + ".fbx")), use_selection=True, object_types={"MESH"}, mesh_smooth_type="FACE",
                             add_leaf_bones=False, bake_anim=False, apply_scale_options="FBX_SCALE_NONE")
    print("POLISH", name, len(o.data.vertices), "verts")
    bpy.data.objects.remove(o, do_unlink=True)
    parts.clear()


# ---------------------------------------------------------------------------------------------------- tableware
def plate(at, R=12.5, yaw=0.0, tilt=(0.0, 0.0), rim=True):
    k = R / 12.5
    prof = [(0, 0.0), (7.5 * k, 0.0), (8.0 * k, 0.35), (10.0 * k, 1.05), (12.2 * k, 1.75), (R, 1.95), (12.25 * k, 2.15), (11.8 * k, 2.0),
            (9.8 * k, 1.3), (8.3 * k, 0.75), (0, 0.72)]
    lathe(prof, CER, at, 40, yaw, tilt)
    if rim:
        lathe([(11.0 * k, 1.78), (11.35 * k, 1.9), (11.35 * k, 1.93), (11.0 * k, 1.81)], GOLD, at, 40, yaw, tilt)


def bowl(at, R=8.0, H=5.0, yaw=0.0, tilt=(0.0, 0.0), m=CER):
    lathe([(0, 0), (R * 0.45, 0), (R * 0.5, 0.5), (R * 0.85, H * 0.45), (R, H), (R - 0.35, H), (R * 0.82, H * 0.5), (R * 0.45, 0.8), (0, 0.8)], m, at, 36, yaw, tilt)


def cup(at, yaw=0.0, tilt=(0.0, 0.0), R=4.2, H=6.6, m=CER, handle=True):
    lathe([(0, 0), (2.4, 0), (2.6, 0.5), (R * 0.85, H * 0.55), (R, H), (R - 0.3, H), (R * 0.82, H * 0.55), (2.2, 0.9), (0, 0.9)], m, at, 32, yaw, tilt)
    if handle:
        pts = []
        for i in range(10):
            t = i / 9
            a = -1.2 + 2.4 * t
            pts.append(xform((R * 0.93 + 1.9 * math.cos(a * 0.9) - 0.2, 0.0, H * 0.5 + 2.1 * math.sin(a)), at, yaw, tilt))
        tube(pts, 0.36, m)


def saucer(at, yaw=0.0):
    lathe([(0, 0), (3.6, 0), (4.0, 0.3), (6.6, 1.0), (7.0, 1.2), (6.7, 1.35), (4.0, 0.75), (2.6, 0.7), (2.6, 0.9), (0, 0.9)], CER, at, 36, yaw)
    lathe([(6.0, 1.08), (6.3, 1.18), (6.3, 1.2), (6.0, 1.12)], GOLD, at, 36, yaw)


def tureen(at):
    lathe([(0, 0), (6.0, 0), (6.4, 0.8), (5.0, 1.6), (9.5, 5.0), (11.0, 9.5), (10.6, 11.0), (10.2, 11.0), (10.3, 9.6), (9.0, 5.5), (4.5, 2.2), (0, 2.2)], CER, at, 40)
    lathe([(0, 15.6), (1.0, 15.6), (1.4, 14.6), (0.9, 13.8), (3.0, 13.4), (8.0, 12.4), (10.4, 11.2), (10.4, 10.8), (0, 10.8)], CER, at, 40)
    for s in (-1, 1):
        tube([(at[0] + s * 10.4, at[1] + y, at[2] + 9.0 + 1.6 * math.sin(math.pi * (y + 2.5) / 5.0)) for y in (-2.5, -1.25, 0, 1.25, 2.5)], 0.6, CER)


def gravy_boat(at, yaw=0.0):
    lathe([(0, 0), (3.0, 0), (3.2, 0.5), (2.4, 1.0), (5.2, 3.0), (6.0, 6.0), (5.7, 6.0), (4.9, 3.3), (2.5, 1.6), (0, 1.6)], CER, at, 32, yaw, sx=1.45, sy=0.85)
    tube([xform((-8.0 + 1.5 * math.cos(a), 0, 4.0 + 2.4 * math.sin(a)), at, yaw) for a in [math.radians(x) for x in range(-80, 120, 20)]], 0.42, CER)


def jug(at, yaw=0.0):
    lathe([(0, 0), (3.4, 0), (3.6, 0.5), (4.6, 4.0), (4.3, 8.5), (3.5, 11.0), (3.8, 12.5), (3.5, 12.5), (3.2, 11.0), (4.0, 8.5), (4.2, 4.0), (3.2, 0.9), (0, 0.9)], CER, at, 32, yaw)
    tube([xform((4.1 + 2.0 * math.cos(a), 0, 7.0 + 3.0 * math.sin(a)), at, yaw) for a in [math.radians(x) for x in range(-80, 100, 20)]], 0.45, CER)


def wine_glass(at, H=15.5, yaw=0.0, tilt=(0.0, 0.0)):
    lathe([(0, 0), (3.2, 0), (3.25, 0.25), (0.6, 0.6), (0.35, 1.5), (0.35, H * 0.42), (1.2, H * 0.5), (3.2, H * 0.72), (3.4, H), (3.25, H), (3.05, H * 0.73),
           (1.1, H * 0.53), (0, H * 0.5)], GLASS, at, 32, yaw, tilt)


def tumbler(at, H=9.0, R=3.6, fill=None):
    lathe([(0, 0), (R - 0.3, 0), (R - 0.1, 0.4), (R, H), (R - 0.25, H), (R - 0.35, 1.0), (0, 1.0)], GLASS, at, 32)
    if fill:
        lathe([(0, 1.05), (R - 0.4, 1.05), (R - 0.37, fill), (0, fill)], "M_PickleOchre", at, 24)


def bottle(at, H=28.0, R=4.2, neck=1.3, m=GLASS, fill=None, fill_m="M_PickleOchre", cap=None, label=None, sx=1.0, sy=1.0):
    prof = [(0, 0), (R - 0.4, 0), (R, 0.6), (R, H * 0.62), (R * 0.7, H * 0.74), (neck, H * 0.84), (neck, H * 0.97), (neck + 0.25, H), (neck - 0.3, H),
            (neck - 0.3, H * 0.84), (R * 0.68, H * 0.73), (R - 0.3, H * 0.62), (R - 0.3, 0.8), (0, 0.8)]
    lathe(prof, m, at, 32, sx=sx, sy=sy)
    if fill:
        lathe([(0, 0.85), (R - 0.35, 0.85), (R - 0.35, min(fill, H * 0.6)), (0, min(fill, H * 0.6))], fill_m, at, 24, sx=sx, sy=sy)
    if cap:
        lathe([(0, H - 0.2), (neck + 0.35, H - 0.2), (neck + 0.4, H + 1.6), (0, H + 1.6)], cap, at, 24)
    if label:
        lathe([(R + 0.03, H * 0.2), (R + 0.03, H * 0.52)], label, at, 32, sx=sx, sy=sy, smooth=True)


def can(at, H=11.5, R=3.8, label=PAPER):
    lathe([(0, 0), (R - 0.2, 0), (R, 0.3), (R, H - 0.3), (R - 0.2, H), (0, H - 0.2)], STEEL, at, 32)
    lathe([(R + 0.04, 0.8), (R + 0.04, H - 0.8)], label, at, 32)


def jar(at, H=15.0, R=4.6, fill="M_PickleOchre", lid=BRASS):
    lathe([(0, 0), (R - 0.4, 0), (R, 0.6), (R, H * 0.8), (R * 0.82, H * 0.9), (R * 0.82, H), (R * 0.78, H), (R * 0.78, H * 0.9), (R - 0.3, H * 0.8),
           (R - 0.3, 0.8), (0, 0.8)], GLASS, at, 32)
    lathe([(0, 0.85), (R - 0.35, 0.85), (R - 0.35, H * 0.74), (0, H * 0.74)], fill, at, 24)
    lathe([(0, H + 1.0), (R * 0.84, H + 1.0), (R * 0.88, H - 0.6), (R * 0.82, H - 0.6), (0, H + 0.6)], lid, at, 32)


def book(at, w, h, d, m, yaw=0.0, lean=0.0, lie=False):
    """A hardback: cover box (spine out toward +Y), the page block showing at the top and on the side faces."""
    tilt = (0.0, lean)
    if lie:
        box((h, d, w), at, m, yaw, (0.0, 0.0), bevel=0.25)
        box((h - 0.6, d - 0.8, w - 0.5), (at[0], at[1] - 0.45, at[2] + 0.25), PAPER, yaw, bevel=0.0)
        return
    box((w, d, h), at, m, yaw, tilt, bevel=0.25)
    box((w - 0.5, d - 0.8, h - 0.4), xform((0, -0.45, 0.2), at, yaw, tilt), PAPER, yaw, tilt, bevel=0.0)
    if random.random() < 0.5:
        for zz in (h * 0.12, h * 0.82):
            box((w + 0.06, 0.15, 0.5), xform((0, d / 2, zz), at, yaw, tilt), GOLD, yaw, tilt, bevel=0.0)


def book_row(x0, x1, y, z, depth=(15, 21), height=(19, 27), lean_end=True):
    x = x0
    while x < x1 - 2.0:
        w = random.uniform(2.0, 4.6)
        if x + w > x1:
            break
        h, d = random.uniform(*height), random.uniform(*depth)
        book((x + w / 2, y + d / 2, z), w, h, d, random.choice(BOOKS))
        x += w + random.uniform(0.05, 0.25)
    if lean_end and x1 - x > 6:
        w, h, d = 3.2, random.uniform(*height), random.uniform(*depth)
        book((x + 1.8 + 0.42 * h, y + d / 2, z), w, h, d, random.choice(BOOKS), lean=-24.0)    # fallen against the row


# ---------------------------------------------------------------------------------------------------- the sets
def shelves_02a():
    """Two shelves for the OldWest cabinet (its inside is one empty box from z 52 to 210)."""
    for z in (102.0, 155.0):
        box((110.0, 40.0, 1.8), (0.0, 0.5, z), TRIM, bevel=0.3)
        box((110.0, 0.9, 1.4), (0.0, -14.0, z + 1.8), TRIM, bevel=0.1)              # plate groove
    return (52.0, 103.8, 156.8)


def china_set():
    random.seed(1962)
    z0, z1, z2 = shelves_02a()
    # bottom: plates stacked, the tureen, bowls nested, the gravy boat, and a plate broken in two
    for i in range(9):
        plate((-36.0, 2.0, z0 + i * 1.05), 12.5, i * 17.0, rim=True)
    for i in range(6):
        plate((-36.0 + 26.0, 4.0, z0 + i * 1.05), 10.0, i * 23.0)
    tureen((14.0, 1.0, z0))
    for i in range(4):
        bowl((40.0, 2.0, z0 + i * 1.2), 8.0 - i * 0.05, 5.0)
    gravy_boat((38.0, 14.0, z0), 20.0)
    plate((-12.0, 14.0, z0 + 0.6), 12.5, 30.0, tilt=(4.0, -3.0))                   # put back in a hurry, askew
    # middle: dinner plates stood up in the groove against the back, cups on saucers in front
    for i, x in enumerate((-44.0, -30.0, -16.0, -2.0, 12.0, 26.0, 40.0)):
        if i == 5:
            continue                                                                  # a gap where one has gone
        plate((x, -17.5, z1 + 12.8), 12.5, 0.0, tilt=(-78.0, 0.0))
    for i, x in enumerate((-40.0, -22.0, -4.0, 14.0, 32.0)):
        saucer((x, 8.0, z1), i * 31.0)
        if i == 3:
            cup((x + 9.0, 12.0, z1 + 4.2), 110.0, tilt=(0.0, 90.0))                  # knocked over, lying on its side
        else:
            cup((x, 8.0, z1 + 0.9), random.uniform(-40, 40))
    jug((46.0, 6.0, z1), 200.0)
    # top: the crystal
    for i, x in enumerate((-44.0, -34.0, -24.0, -14.0, -4.0, 6.0)):
        wine_glass((x, -8.0 if i % 2 else -2.0, z2), 15.5 + (i % 3) * 0.6)
    for x in (18.0, 27.0, 36.0):
        tumbler((x, 2.0, z2), 9.0)
    bottle((46.0, -6.0, z2), 26.0, 4.6, 1.2, GLASS, cap=GLASS)                         # a decanter, stopper in
    export("SM_PolishChinaSet")


def den_set():
    random.seed(1958)
    z0, z1, z2 = shelves_02a()
    book_row(-53.0, 20.0, -19.0, z0)
    for i in range(5):                                                                 # a stack lying flat
        book((36.0, 0.0, z0 + i * 3.6), 3.5, random.uniform(22, 28), random.uniform(15, 18), random.choice(BOOKS), yaw=random.uniform(-6, 6), lie=True)
    book_row(-53.0, 53.0, -19.0, z1, height=(18, 24))
    # top: decoy, cigar box, shell boxes, whiskey and two glasses
    lathe([(0, 0), (6.5, 0.0), (8.0, 3.0), (7.2, 7.0), (4.0, 9.0), (0, 9.2)], "MI_WoodPainted", (-36.0, -2.0, z2), 24, 15.0, sx=2.0, sy=1.0)
    lathe([(0, 0), (2.6, 0.0), (3.0, 3.0), (2.8, 5.6), (1.2, 7.0), (0, 7.1)], "MI_WoodPainted", (-36.0 + 13.0 * math.cos(math.radians(15)), -2.0 + 13.0 * math.sin(math.radians(15)), z2 + 7.5), 20, 15.0, sx=1.4)
    box((22.0, 14.0, 5.5), (-8.0, 2.0, z2), "MI_WoodDark", 8.0, bevel=0.3)
    box((22.4, 14.4, 0.8), (-8.0, 2.0, z2 + 5.5), "MI_WoodDark", 8.0, bevel=0.2)
    for i in range(3):
        box((11.0, 6.5, 4.2), (14.0, 4.0, z2 + i * 4.25), CARD, random.uniform(-8, 8), bevel=0.1)
    bottle((34.0, -4.0, z2), 26.0, 4.4, 1.3, GLASS, fill=12.0, cap="M_PhoneBakelite", label=PAPER, sx=1.0, sy=0.72)
    tumbler((44.0, 6.0, z2), 8.5, 3.6, fill=2.2)
    tumbler((47.0, -6.0, z2), 8.5, 3.6)
    export("SM_PolishDenSet")


MED_X0, MED_X1 = -42.0, 29.0
MED_SHELVES = (10.0, 54.0, 96.0, 139.0)


def kitchen_set():
    random.seed(1971)
    s0, s1, s2, s3 = MED_SHELVES
    x = MED_X0 + 4.0
    for row_y in (-12.0, -2.0):                                                        # canned goods, two rows
        x = MED_X0 + 4.5
        while x < MED_X1 - 4.0:
            can((x, row_y + random.uniform(-0.5, 0.5), s0), random.choice((11.5, 11.5, 10.0, 14.0)), 3.8)
            x += 8.3
    box((16.0, 7.0, 26.0), (MED_X1 - 10.0, 8.0, s0), CARD, -6.0, bevel=0.15)            # a box of oats in front
    for i in range(7):
        plate((-28.0, -2.0, s1 + i * 1.05), 12.5, i * 19.0)
    for i in range(3):
        bowl((-4.0, -2.0, s1 + i * 1.3), 8.2, 5.2)
    for i in range(5):
        plate((15.0, -2.0, s1 + i * 1.0), 10.0, i * 23.0, rim=False)
    for i, xx in enumerate((-36.0, -26.0, -16.0, -6.0, 4.0)):
        cup((xx, -6.0, s2), 200.0 + random.uniform(-20, 20), R=4.0, H=8.6, m="M_HarrowEnamel" if i % 2 else CER)
    for xx in (14.0, 22.0):
        tumbler((xx, -4.0, s2), 10.0, 3.4)
    tumbler((18.0, 6.0, s2), 10.0, 3.4)
    for i, (xx, f) in enumerate(((-36.0, "M_PickleOchre"), (-26.0, "M_PicklePale"), (-16.0, "M_PickleRust"), (-6.0, "M_PickleOchre"), (4.0, "M_PicklePale"))):
        jar((xx, -6.0, s3), 15.0 if i % 2 else 13.0, 4.5, f)
    box((19.0, 7.0, 28.0), (18.0, -4.0, s3), CARD, 4.0, bevel=0.15)                    # cereal, its top torn open
    export("SM_PolishKitchenSet")


def medicine_set():
    random.seed(1989)
    s0, s1, s2, s3 = MED_SHELVES
    # amber bottles of every size along the top two shelves
    for zz, n in ((s3, 7), (s2, 6)):
        x = MED_X0 + 4.0
        for i in range(n):
            H = random.choice((9.0, 11.0, 13.0, 16.0))
            R = H * 0.26
            bottle((x, random.uniform(-10, 4), zz), H, R, R * 0.42, GLASS, fill=H * random.uniform(0.1, 0.45), fill_m="M_PickleRust",
                   cap=random.choice(("M_PhoneBakelite", STEEL)), label=PAPER if random.random() < 0.8 else None)
            x += R * 2 + random.uniform(1.6, 3.4)
            if x > MED_X1 - 4:
                break
    for i in range(4):                                                                 # pill tins in a stack
        lathe([(0, 0), (3.6, 0), (3.7, 1.6), (0, 1.6)], STEEL, (MED_X1 - 6.0, 6.0, s2 + i * 1.65), 28)
    # bandage rolls and gauze boxes, the hot-water bottle
    for i, xx in enumerate((-36.0, -28.5, -21.0)):
        lathe([(0, 0), (3.4, 0), (3.5, 6.5), (0, 6.5)], SHEET, (xx, -8.0, s1), 28)
    lathe([(0, 0), (3.4, 0), (3.5, 6.5), (0, 6.5)], SHEET, (-32.0, 4.0, s1 + 3.5), 28, tilt=(90.0, 0.0))
    for i in range(3):
        box((12.0, 8.0, 6.5), (0.0, -4.0, s1 + i * 6.6), CARD if i != 1 else PAPER, random.uniform(-6, 6), bevel=0.1)
    lathe([(0, 0), (9.0, 0.0), (10.0, 2.0), (9.0, 3.0), (0, 3.2)], "M_PhoneRubber", (18.0, -2.0, s1), 28, 12.0, sx=1.0, sy=0.7)
    # kidney dish and the bedpan
    lathe([(0, 0), (8.0, 0.0), (9.0, 2.6), (9.3, 3.0), (8.9, 3.0), (7.6, 0.8), (0, 0.8)], STEEL, (-24.0, -2.0, s0), 36, 0.0, sx=1.3, sy=0.6)
    lathe([(0, 0), (11.0, 0.0), (12.0, 4.5), (12.4, 5.0), (12.0, 5.0), (10.6, 0.8), (0, 0.8)], "M_HarrowEnamel", (8.0, -2.0, s0), 40, 0.0, sx=1.25, sy=0.95)
    export("SM_PolishMedicineSet")


SETS = {"SM_PolishChinaSet": china_set, "SM_PolishDenSet": den_set, "SM_PolishKitchenSet": kitchen_set, "SM_PolishMedicineSet": medicine_set}


# ---------------------------------------------------------------------------------------------------- furniture
WALNUT = "M_HarrowWalnut"


def door_panel(x0, x1, z0, z1, yf, m, rail=8.0, t=2.2):
    """A frame-and-panel door face standing at yf (its front): stiles and rails, a sunk panel with a raised field and a bead."""
    w, h = x1 - x0, z1 - z0
    cx = (x0 + x1) / 2
    box((w, t, rail), (cx, yf - t / 2, z0), m, bevel=0.25)                                   # bottom rail
    box((w, t, rail), (cx, yf - t / 2, z1 - rail), m, bevel=0.25)                            # top rail
    for sx in (x0 + rail / 2, x1 - rail / 2):
        box((rail, t, h - 2 * rail), (sx, yf - t / 2, z0 + rail), m, bevel=0.25)            # stiles
    box((w - 2 * rail, 1.0, h - 2 * rail), (cx, yf - t + 0.3, z0 + rail), m, bevel=0.1)      # the sunk panel
    box((w - 2 * rail - 5.0, 1.4, h - 2 * rail - 5.0), (cx, yf - t + 0.9, z0 + rail + 2.5), m, bevel=0.6)   # raised field
    for zz in (z0 + rail, z1 - rail - 0.6):
        box((w - 2 * rail, 0.6, 0.6), (cx, yf - 0.3, zz), m, bevel=0.1)                      # bead round the panel
    for xx in (x0 + rail, x1 - rail):
        box((0.6, 0.6, h - 2 * rail), (xx, yf - 0.3, z0 + rail), m, bevel=0.1)


def bail(x, z, yf, w=9.0):
    """A brass bail pull: back plate, two posts and the handle hanging down."""
    box((w + 3.0, 0.3, 2.6), (x, yf + 0.15, z - 1.3), BRASS, bevel=0.1)
    for sx in (-w / 2, w / 2):
        lathe([(0, 0), (0.45, 0), (0.45, 1.4), (0, 1.4)], BRASS, (x + sx, yf, z), 10, tilt=(-90.0, 0.0))
    tube([(x + w / 2 * math.cos(a), yf + 1.2, z - 2.6 * math.sin(a) - 0.2) for a in [math.radians(v) for v in range(0, 181, 15)]], 0.28, BRASS)


def keyhole(x, z, yf):
    lathe([(0, 0), (1.3, 0), (1.3, 0.25), (0, 0.25)], BRASS, (x, yf, z), 20, tilt=(-90.0, 0.0), sx=0.7, sy=1.0)
    box((0.35, 0.1, 1.0), (x, yf + 0.3, z - 0.7), "M_Black", bevel=0.0)


COURSES = ((1.0, 3.0), (2.4, 2.2), (3.6, 4.0))


def cornice(w, d_back, d_front, z, m):
    """Stepped moulding round the top: three courses, each a little prouder than the last."""
    zz = z
    for stick, hh in COURSES:
        box((w + 2 * stick, d_front - d_back + stick, hh), (0.0, (d_back + d_front + stick) / 2, zz), m, bevel=0.5)
        zz += hh


def knob(x, z, yf, m):
    lathe([(0, 0), (0.6, 0), (0.6, 1.0), (1.6, 1.6), (1.5, 2.6), (0, 2.8)], m, (x, yf, z), 16, tilt=(-90.0, 0.0))


def daniel_wardrobe():
    """Danny's wardrobe: a 1950s walnut two-door with two drawers under, kept dusted for forty years (Wardrobe_Tall's
    footprint, its back on the same wall).  His army duffel, a hat box and a shoe box on top."""
    random.seed(1968)
    W, B, F, H = 140.0, -35.0, 26.0, 200.0
    D = F - B
    box((W - 4.0, D - 3.0, 8.0), (0.0, B + (D - 3.0) / 2, 0.0), "MI_WoodDark", bevel=0.3)                 # plinth, set back
    box((W + 1.0, D + 0.6, 2.0), (0.0, B + (D + 0.6) / 2, 8.0), WALNUT, bevel=0.5)                         # base moulding
    for sx in (-1, 1):
        box((2.4, D, H - 10.0), (sx * (W / 2 - 1.2), B + D / 2, 10.0), WALNUT, bevel=0.3)                  # sides
    box((W, 1.2, H - 10.0), (0.0, B + 0.6, 10.0), "MI_WoodDark", bevel=0.0)                                # back
    box((W, D, 2.0), (0.0, B + D / 2, H - 2.0), WALNUT, bevel=0.3)                                         # top
    for x in (-W / 4 - 0.4, W / 4 + 0.4):                                                                  # two drawers
        box((W / 2 - 4.6, 2.2, 28.0), (x, F - 1.1, 11.0), WALNUT, bevel=0.6)
        box((W / 2 - 9.6, 0.5, 23.0), (x, F + 0.2, 13.5), WALNUT, bevel=0.3)
        bail(x, 27.0, F + 0.4)
        keyhole(x, 33.0, F + 0.4)
    box((W - 2.0, 2.0, 1.4), (0.0, F - 1.0, 40.0), WALNUT, bevel=0.2)                                      # rail
    for k, (x0, x1) in enumerate(((-W / 2 + 2.6, -0.3), (0.3, W / 2 - 2.6))):                              # two doors
        door_panel(x0, x1, 42.0, H - 9.0, F + (0.8 if k == 0 else 0.0), WALNUT, rail=9.5)                  # left one not quite shut
    keyhole(-2.6, 118.0, F + 0.8)
    knob(-3.6, 108.0, F + 0.8, BRASS)
    knob(3.6, 108.0, F, BRASS)
    cornice(W, B, F, H - 9.0, WALNUT)
    top = H - 9.0 + sum(h for _, h in COURSES)
    # on top: his olive-drab duffel lying along it with its strap, a round hat box and a shoe box
    lathe([(0, 0), (6.0, 1.0), (11.0, 6.0), (12.5, 18.0), (12.5, 52.0), (11.0, 64.0), (6.0, 69.0), (0, 70.0)], "MI_FabricGreen",
          (-64.0, -6.0, top + 9.8), 24, 0.0, tilt=(0.0, 90.0), sx=0.78, sy=1.0)
    tube([(-60.0 + t * 62.0, -6.0, top + 19.0 + 4.0 * math.sin(t * math.pi)) for t in [i / 10 for i in range(11)]], 0.9, "MI_Leather")
    lathe([(0, 0), (16.0, 0), (16.0, 14.0), (16.6, 14.0), (16.6, 18.0), (0, 18.0)], CARD, (38.0, -12.0, top), 40)
    box((30.0, 18.0, 11.0), (34.0, 15.0, top), CARD, -6.0, bevel=0.2)
    export("SM_PolishDanielWardrobe")


def pantry_cupboard():
    """A painted wooden pantry cupboard in place of the hospital steel cabinet: panelled doors below, a ledge, glazed doors
    above with jars and tins showing through (Cabinet_Steel_Tall's footprint, its back on the same wall)."""
    random.seed(1977)
    P = "MI_WoodPainted"
    W, B, F, H = 88.0, -24.5, 19.5, 188.0
    D = F - B
    box((W - 3.0, D - 3.0, 7.0), (0.0, B + (D - 3.0) / 2, 0.0), "MI_WoodDark", bevel=0.3)
    for sx in (-1, 1):
        box((2.0, D, H - 7.0), (sx * (W / 2 - 1.0), B + D / 2, 7.0), P, bevel=0.3)
    box((W, 1.0, H - 7.0), (0.0, B + 0.5, 7.0), P, bevel=0.0)
    box((W, D, 1.8), (0.0, B + D / 2, H - 1.8), P, bevel=0.3)
    for x0, x1 in ((-W / 2 + 2.2, -0.3), (0.3, W / 2 - 2.2)):                                             # lower doors
        door_panel(x0, x1, 8.0, 80.0, F, P, rail=7.0)
    knob(-3.2, 52.0, F, "M_PhoneIvory")
    knob(3.2, 52.0, F, "M_PhoneIvory")
    box((W + 3.0, D + 4.0, 2.4), (0.0, B + (D + 4.0) / 2, 81.0), P, bevel=0.4)                            # the ledge
    for zz in (122.0, 152.0):                                                                             # shelves behind the glass
        box((W - 4.0, D - 3.0, 1.6), (0.0, B + 1.0 + (D - 3.0) / 2, zz - 1.6), P, bevel=0.1)
    fills = ["M_PickleOchre", "M_PicklePale", "M_PickleRust"]
    for zz, kind in ((83.4, "can"), (122.0, "jar"), (152.0, "jar")):
        x = -W / 2 + 8.0
        while x < W / 2 - 8.0:
            if kind == "can":
                can((x, -6.0, zz), random.choice((11.5, 10.0)), 3.8)
                x += 8.4
            else:
                jar((x, -6.0, zz), random.choice((13.0, 15.0)), 4.4, random.choice(fills))
                x += 10.2
    for x0, x1 in ((-W / 2 + 2.2, -0.3), (0.3, W / 2 - 2.2)):                                             # glazed upper doors
        cx, w = (x0 + x1) / 2, x1 - x0
        z0, z1 = 86.0, H - 9.0
        box((w, 2.0, 5.0), (cx, F - 1.0, z0), P, bevel=0.3)
        box((w, 2.0, 5.0), (cx, F - 1.0, z1 - 5.0), P, bevel=0.3)
        for sx in (x0 + 2.5, x1 - 2.5):
            box((5.0, 2.0, z1 - z0 - 10.0), (sx, F - 1.0, z0 + 5.0), P, bevel=0.3)
        box((1.6, 1.6, z1 - z0 - 10.0), (cx, F - 1.0, z0 + 5.0), P, bevel=0.2)                               # muntins
        for k in (1, 2):
            box((w - 10.0, 1.6, 1.6), (cx, F - 1.0, z0 + 5.0 + k * (z1 - z0 - 10.0) / 3 - 0.8), P, bevel=0.2)
        box((w - 9.0, 0.3, z1 - z0 - 9.0), (cx, F - 1.2, z0 + 4.5), GLASS, bevel=0.0)                       # the glass
    knob(-3.2, 112.0, F, "M_PhoneIvory")
    knob(3.2, 112.0, F, "M_PhoneIvory")
    cornice(W, B, F, H - 9.0, P)
    export("SM_PolishPantryCupboard")


SETS.update({"SM_PolishDanielWardrobe": daniel_wardrobe, "SM_PolishPantryCupboard": pantry_cupboard})


for name, fn in SETS.items():
    if argv and name not in argv:
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fn()
print("POLISH done")
