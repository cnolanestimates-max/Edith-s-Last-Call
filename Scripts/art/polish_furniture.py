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


# ---------------------------------------------------------------------------------------------------- round two: home pieces
# for the hospital kit (Cheyenne, 2026-11-22: "most of that other stuff I want done for sure").  Pivot at the middle of
# the floor under the piece, front +Y, back at y = -D/2; the level seats each back against its wall.
PORC, ENAMEL, CHROME, RUST = "MI_Porcelain", "M_HarrowEnamel", "M_ItemSteel", "MI_Rust"


def rounded_basin(cx, cy, z_rim, w, d, depth, m, wall=1.2, r=6.0, seg=10):
    """An open rectangular basin with rounded corners: outer skin, rolled rim and inner skin, as one lofted shell."""
    def ring(hw, hd, rr, z):
        pts = []
        for k, (sx, sy) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
            a0 = k * math.pi / 2
            ccx, ccy = cx + sx * (hw - rr), cy + sy * (hd - rr)
            for i in range(seg + 1):
                a = a0 + (math.pi / 2) * i / seg
                pts.append((ccx + rr * math.cos(a), ccy + rr * math.sin(a), z))
        return pts
    rows = [ring(w / 2 - 3.0, d / 2 - 3.0, r - 2.0, z_rim - depth - 2.0), ring(w / 2, d / 2, r, z_rim - 4.0), ring(w / 2 + 0.6, d / 2 + 0.6, r + 0.6, z_rim - 0.6),
            ring(w / 2, d / 2, r, z_rim), ring(w / 2 - wall, d / 2 - wall, r - wall, z_rim - 0.4),
            ring(w / 2 - wall - 0.5, d / 2 - wall - 0.5, r - wall - 0.5, z_rim - depth + 2.5), ring(w / 2 - wall - 4.0, d / 2 - wall - 4.0, max(1.0, r - wall - 4.0), z_rim - depth)]
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    vr = [[bm.verts.new(V(*p)) for p in row] for row in rows]
    n = len(rows[0])
    for k in range(len(vr) - 1):
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((vr[k][i], vr[k][j], vr[k + 1][j], vr[k + 1][i]))
            for lp in f.loops:
                lp[uv].uv = (lp.vert.co.x * 3.0 + lp.vert.co.y * 3.0, lp.vert.co.z * 3.0)
    for ring_ in (vr[0], vr[-1]):
        c = bm.verts.new(V(cx, cy, rows[0][0][2] if ring_ is vr[0] else rows[-1][0][2]))
        for i in range(n):
            try:
                bm.faces.new((c, ring_[i], ring_[(i + 1) % n]))
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(bm, m)


def tap(x, y, z, m=CHROME, spout=12.0, yaw=0.0):
    """A wall or deck mounted faucet: body, swan spout bent over the basin, a cross handle each side."""
    lathe([(0, 0), (2.4, 0), (2.4, 1.0), (1.4, 1.6), (1.4, 6.0), (0, 6.6)], m, (x, y, z), 20, yaw)
    tube([xform(p, (x, y, z), yaw) for p in ((0, 0, 5.5), (0, 0, 9.5), (0, spout * 0.35, 11.5), (0, spout * 0.75, 10.8), (0, spout, 8.0))], 0.95, m)
    for s_ in (-1, 1):
        hx = x + s_ * 9.0
        lathe([(0, 0), (1.6, 0), (1.6, 1.0), (0.9, 1.4), (0.9, 4.0), (0, 4.0)], m, (hx, y, z), 16, yaw)
        for a in (0, 90):
            box((5.2, 0.8, 0.8), (hx, y, z + 4.0), PORC, yaw + a + 45, bevel=0.2)


def kitchen_sink():
    """A cast-iron enamelled farmhouse sink with a drainboard, on a painted base cabinet, splashback and wall taps,
    a few dishes left in it, rust bled down from the taps."""
    random.seed(1955)
    W, D, H = 92.0, 54.0, 90.0
    B = -D / 2
    P = "MI_WoodPainted"
    box((W - 4.0, D - 6.0, 8.0), (0.0, B + (D - 6.0) / 2, 0.0), "MI_WoodDark", bevel=0.3)
    for sx in (-1, 1):
        box((2.0, D - 2.0, H - 18.0), (sx * (W / 2 - 1.0), B + (D - 2.0) / 2, 8.0), P, bevel=0.3)
    box((W, 1.0, H - 18.0), (0.0, B + 0.5, 8.0), P, bevel=0.0)
    for x0, x1 in ((-W / 2 + 2.0, -0.3), (0.3, W / 2 - 2.0)):
        door_panel(x0, x1, 9.0, H - 21.0, B + D - 2.0, P, rail=6.5)
    knob(-3.0, H - 32.0, B + D - 2.0, "M_PhoneIvory")
    knob(3.0, H - 32.0, B + D - 2.0, "M_PhoneIvory")
    box((W, D - 2.0, 3.0), (0.0, B + (D - 2.0) / 2, H - 21.0), P, bevel=0.4)                               # top frame
    # the iron sink: an apron front, the bowl on the right, a ribbed drainboard on the left, a high splashback
    box((W + 1.0, 2.6, 18.0), (0.0, B + D - 1.0, H - 18.0), ENAMEL, bevel=1.0)                                # apron
    box((W + 1.0, D - 2.0, 2.0), (0.0, B + (D - 2.0) / 2, H - 2.0), ENAMEL, bevel=0.8)                        # deck
    rounded_basin(16.0, 2.0, H + 0.3, 44.0, 36.0, 19.0, ENAMEL)
    for i in range(9):
        box((30.0, 1.2, 0.5), (-24.0, B + 10.0 + i * 3.6, H), ENAMEL, bevel=0.2)                              # drainboard ribs
    box((W + 1.0, 3.0, 26.0), (0.0, B + 1.5, H), ENAMEL, bevel=1.0)                                          # splashback
    tap(16.0, B + 3.2, H + 14.0, spout=10.0)
    lathe([(0, 0), (3.4, 0), (3.4, 0.3), (0, 0.3)], CHROME, (16.0, 2.0, H - 18.6), 20)                         # drain
    # left behind: a stack of plates in the bowl, a cup, a pot on the drainboard
    for i in range(4):
        plate((15.0, 2.0, H - 18.3 + i * 1.05), 10.5, i * 21.0, tilt=(6.0, 0.0), rim=False)
    cup((26.0, -6.0, H - 18.3), 200.0, tilt=(0.0, 0.0))
    lathe([(0, 0), (9.0, 0), (9.5, 1.0), (9.5, 11.0), (9.9, 11.5), (9.2, 11.5), (8.9, 1.0), (0, 1.0)], ENAMEL, (-24.0, 4.0, H + 0.6), 32)
    tube([(-24.0 - 9.6 - t * 14.0, 4.0, H + 9.0) for t in (0.0, 0.5, 1.0)], 1.0, "M_PhoneBakelite")
    export("SM_PolishKitchenSink")


def pedestal_sink():
    """A porcelain pedestal basin with two taps, the bowl crazed, a dried cake of soap and a toothbrush glass."""
    random.seed(1963)
    H = 84.0
    lathe([(0, 0), (11.0, 0), (11.5, 1.0), (9.0, 3.0), (7.0, 14.0), (6.0, 40.0), (6.5, 60.0), (8.0, 66.0), (0, 66.0)], PORC, (0.0, -6.0, 0.0), 32, sx=1.25, sy=1.0)
    rounded_basin(0.0, -1.0, H, 56.0, 42.0, 14.0, PORC, wall=2.0, r=12.0)
    box((56.0, 3.0, 12.0), (0.0, -21.0, H - 1.0), PORC, bevel=1.2)                                           # back ledge
    tap(0.0, -18.5, H + 0.5, spout=7.0)                                                                       # one spout, hot and cold
    lathe([(0, 0), (3.0, 0), (3.0, 0.3), (0, 0.3)], CHROME, (0.0, -1.0, H - 14.0), 20)
    box((8.0, 5.0, 2.2), (-18.0, -17.0, H + 10.9), "M_PhoneIvory", 8.0, bevel=0.8)                           # soap
    tumbler((18.0, -17.5, H + 10.9), 9.0, 3.0)
    tube([(17.5, -17.0, H + 12.0), (19.0, -18.5, H + 24.0)], 0.45, "MI_ToyRed")                               # toothbrush
    export("SM_PolishPedestalSink")


def hamper():
    """A wicker laundry hamper, its lid knocked askew, the washing nobody did spilling over the top and onto the floor."""
    random.seed(1984)
    R, H = 22.0, 58.0
    W_ = "MI_WoodBleached"
    lathe([(0, 0), (R - 2.0, 0), (R, 2.0), (R + 1.5, H - 3.0), (R + 2.2, H), (R + 0.6, H), (R - 0.2, H - 3.0), (R - 1.8, 2.0), (0, 2.0)], W_, (0, 0, 0), 48, sx=1.3)
    for i in range(24):                                                                                        # woven uprights
        a = TAU * i / 24
        x0, y0 = math.cos(a) * (R + 0.4) * 1.3, math.sin(a) * (R + 0.4)
        x1, y1 = math.cos(a) * (R + 2.0) * 1.3, math.sin(a) * (R + 2.0)
        tube([(x0, y0, 2.0), (x1, y1, H - 2.0)], 0.5, W_, 6)
    for k in range(9):                                                                                         # weave bands
        z = 6.0 + k * 5.8
        rr = R + 0.6 + 1.5 * z / H
        tube([(math.cos(TAU * i / 48) * rr * 1.3, math.sin(TAU * i / 48) * rr, z) for i in range(49)], 0.55, W_, 6)
    lathe([(0, 0), (R + 2.5, 0), (R + 2.5, 1.6), (0, 2.4)], W_, (7.0, 4.0, H + 2.0), 48, 20.0, tilt=(8.0, -6.0), sx=1.3)  # the lid, askew
    # clothes: a towel over the rim, a shirt half out, socks on the floor
    for (cx, cy, cz, sx, sy, m) in ((-10.0, -6.0, H - 2.0, 18.0, 11.0, "MI_FabricBlue"), (6.0, -8.0, H + 1.0, 12.0, 10.0, "M_HarrowGingham"),
                                    (-30.0, 10.0, 0.6, 14.0, 8.0, "MI_Sheet"), (-40.0, -8.0, 0.4, 7.0, 4.0, "MI_FabricDark")):
        lathe([(0, 0), (1.0, 0.0), (0.9, 2.2), (0.5, 3.2), (0, 3.4)], m, (cx, cy, cz), 24, random.uniform(0, 180), sx=sx, sy=sy)
    tube([(-24.0, -2.0, H - 1.0), (-30.0, -2.0, H - 12.0), (-33.0, 0.0, H - 30.0), (-34.0, 2.0, 8.0), (-36.0, 4.0, 1.0)], 2.2, "MI_Sheet", 10)  # a towel trailing down
    export("SM_PolishHamper")


def file_cabinet():
    """A 1960s oak four-drawer file in place of the office steel one: brass card holders and pulls, papers on top."""
    random.seed(1966)
    W, D, H = 46.0, 62.0, 132.0
    B = -D / 2
    O = "MI_WoodTrim"
    box((W - 3.0, D - 3.0, 5.0), (0.0, B + (D - 3.0) / 2, 0.0), "MI_WoodDark", bevel=0.3)
    for sx in (-1, 1):
        box((2.0, D, H - 7.0), (sx * (W / 2 - 1.0), B + D / 2, 5.0), O, bevel=0.3)
    box((W, 1.0, H - 7.0), (0.0, B + 0.5, 5.0), O, bevel=0.0)
    box((W + 1.6, D + 1.0, 2.2), (0.0, B + (D + 1.0) / 2, H - 2.2), O, bevel=0.6)
    dh = (H - 9.0) / 4
    for k in range(4):
        z = 5.5 + k * dh
        ajar = 9.0 if k == 1 else 0.0
        box((W - 4.6, 2.2, dh - 1.2), (0.0, B + D - 1.1 + ajar, z), O, bevel=0.6)
        box((W - 10.0, 0.6, dh - 8.0), (0.0, B + D + ajar, z + 4.0), O, bevel=0.4)
        box((7.0, 0.3, 3.2), (0.0, B + D + 0.4 + ajar, z + dh - 9.0), BRASS, bevel=0.1)                         # label holder
        box((5.6, 0.12, 2.2), (0.0, B + D + 0.6 + ajar, z + dh - 8.5), PAPER, bevel=0.0)
        bail(0.0, z + dh * 0.45, B + D + 0.3 + ajar, 7.0)
        if ajar:                                                                                                 # folders standing in it
            for i in range(9):
                box((W - 8.0, 0.3, 24.0), (0.0, B + D - 6.0 - i * 1.6 + ajar, z + 2.0), random.choice((CARD, PAPER, "MI_FabricGreen")), tilt=(random.uniform(-8, 8), 0.0), bevel=0.0)
    for i in range(6):                                                                                           # papers on top
        box((21.0, 28.0, 0.25), (random.uniform(-3, 3), random.uniform(-4, 4), H + 0.3 + i * 0.3), PAPER, random.uniform(-14, 14), bevel=0.0)
    box((22.0, 15.0, 6.0), (2.0, 14.0, H + 2.1), CARD, 10.0, bevel=0.2)                                         # a shoebox of receipts
    export("SM_PolishFileCabinet")


def cellar_shelves():
    """Rough cellar shelving of plank and two-by-four in place of the school lockers: paint cans, coffee cans of nails,
    old jars, a toolbox, a coil of rope, a kerosene lantern, all under dust."""
    random.seed(1949)
    W, D, H = 160.0, 46.0, 186.0
    B = -D / 2
    PL = "MI_MegaRottenWood"
    for sx in (-1, 0, 1):
        for sy in (B + 2.0, B + D - 2.0):
            box((3.8, 3.8, H), (sx * (W / 2 - 2.0), sy, 0.0), PL, random.uniform(-1, 1), bevel=0.3)
    levels = (12.0, 56.0, 102.0, 146.0, H - 3.0)
    for z in levels:
        for k in range(3):
            box((W, D / 3 - 0.5, 2.4), (0.0, B + D / 6 + k * D / 3, z), PL, tilt=(0.0, random.uniform(-0.6, 0.6)), bevel=0.3)
    def paint_can(x, y, z, H_=17.0, R_=8.5):
        lathe([(0, 0), (R_, 0), (R_, H_), (R_ - 0.8, H_ + 0.6), (0, H_ + 0.6)], CHROME, (x, y, z), 28)
        lathe([(R_ + 0.05, 2.0), (R_ + 0.05, H_ - 3.0)], PAPER, (x, y, z), 28)
        tube([(x - R_ + 0.3, y, z + H_ - 1.0), (x, y, z + H_ + 5.0), (x + R_ - 0.3, y, z + H_ - 1.0)], 0.2, CHROME, 6)
        tube([(x + R_ * 0.7, y + R_ * 0.7, z + H_), (x + R_ * 0.72, y + R_ * 0.72, z + H_ * 0.4)], 0.7, "MI_PaintDrip" if False else RUST, 6)
    for i, x in enumerate((-66.0, -48.0, -30.0)):
        paint_can(x, -4.0, levels[0] + 2.4)
    for x in (-8.0, 6.0):
        can((x, 2.0, levels[0] + 2.4), 14.0, 6.0, label=RUST)                                                 # coffee cans of nails
    box((40.0, 20.0, 18.0), (40.0, 2.0, levels[0] + 2.4), "MI_ToyRed", bevel=0.8)                            # a steel toolbox
    tube([(28.0, 2.0, levels[0] + 20.4), (40.0, 2.0, levels[0] + 26.0), (52.0, 2.0, levels[0] + 20.4)], 0.8, CHROME, 8)
    fills = ["M_PickleOchre", "M_PicklePale", "M_PickleRust", "M_JarSediment"]
    for z in (levels[1], levels[2]):
        x = -W / 2 + 9.0
        while x < W / 2 - 9.0:
            jar((x, random.uniform(-8, 2), z + 2.4), random.choice((13.0, 15.0, 18.0)), 4.6, random.choice(fills))
            x += random.uniform(10.5, 13.0)
    for k in range(6):                                                                                          # rope coil
        tube([(-40.0 + 12.0 * math.cos(TAU * i / 24), 2.0 + 12.0 * math.sin(TAU * i / 24), levels[3] + 3.4 + k * 1.6) for i in range(25)], 0.9, "MI_Cardboard", 6)
    lathe([(0, 0), (7.0, 0), (7.0, 6.0), (5.5, 8.0), (4.0, 10.0), (5.5, 22.0), (3.0, 26.0), (1.5, 28.0), (0, 28.0)], RUST, (20.0, 0.0, levels[3] + 2.4), 24)
    lathe([(0, 10.0), (5.0, 10.0), (5.4, 21.0), (0, 21.0)], GLASS, (20.0, 0.0, levels[3] + 2.4), 24)              # lantern glass
    tube([(15.0, 0.0, levels[3] + 30.0), (20.0, 0.0, levels[3] + 36.0), (25.0, 0.0, levels[3] + 30.0)], 0.3, RUST, 6)
    for x in (-60.0, 50.0):
        box((30.0, 28.0, 22.0), (x, 0.0, levels[4] + 2.4), CARD, random.uniform(-6, 6), bevel=0.3)
    export("SM_PolishCellarShelves")


SETS.update({"SM_PolishKitchenSink": kitchen_sink, "SM_PolishPedestalSink": pedestal_sink, "SM_PolishHamper": hamper,
             "SM_PolishFileCabinet": file_cabinet, "SM_PolishCellarShelves": cellar_shelves})


# ---------------------------------------------------------------------------------------------------- round two: wardrobes
# What the kit's open wardrobe (HorrorHouseKit SM_Wardrobe_Open_Clothes, its own rag of a garment hidden) holds.  Its inside:
# x -66..53, y -54..2 (the door swings open beyond +Y), floor z 46, ceiling z 194.
WX0, WX1, WY0, WY1, WZ0, WZ1 = -64.0, 51.0, -52.0, 0.0, 46.0, 192.0
RAIL_Z, RAIL_Y = 182.0, -27.0
FABRICS = ["MI_FabricBlue", "MI_FabricDark", "MI_FabricGreen", "MI_FabricRed", "M_HarrowCalico", "M_HarrowGingham", "M_HarrowBrocade",
           "M_HarrowBurgundy", "MI_Sheet"]


def rail():
    tube([(WX0 - 1.0, RAIL_Y, RAIL_Z), (WX1 + 1.0, RAIL_Y, RAIL_Z)], 1.1, BRASS, 12)


def garment(x, length, m, width=44.0, sleeves=False, seed=0.0, sway=0.0):
    """A garment on a wooden hanger on the rail, hanging edge-on to the front like it would: shoulders to hem lofted as a
    thin closed sleeve of cloth with folds that deepen toward the hem."""
    yc = RAIL_Y
    top = RAIL_Z - 4.5
    hw0 = width / 2 * 0.92
    tube([(x, yc - hw0, top - 3.0), (x, yc - hw0 * 0.5, top - 1.0), (x, yc, top), (x, yc + hw0 * 0.5, top - 1.0), (x, yc + hw0, top - 3.0)], 0.7, "MI_WoodDark", 8)
    tube([(x, yc, top), (x, yc, RAIL_Z + 1.0), (x, yc - 1.6, RAIL_Z + 2.6), (x, yc - 2.6, RAIL_Z + 1.4)], 0.22, CHROME, 6)
    N, M = 14, 28
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    rows = []
    for k in range(N + 1):
        t = k / N
        z = top - 1.5 - t * length
        hw = width / 2 * (0.42 + 0.58 * min(1.0, t * 7.0)) * (1.0 + 0.14 * t)
        th = 1.6 + 2.8 * t
        row = []
        for i in range(M):
            a = TAU * i / M
            fold = (0.6 + 2.0 * t) * math.sin(5.0 * a + seed + t * 2.0)
            px = x + sway * t * t + (th + fold) * math.cos(a)
            py = yc + hw * math.sin(a)
            row.append(bm.verts.new(V(px, py, z)))
        rows.append(row)
    for k in range(N):
        for i in range(M):
            j = (i + 1) % M
            f = bm.faces.new((rows[k][i], rows[k][j], rows[k + 1][j], rows[k + 1][i]))
            for lp in f.loops:
                kk = k if lp.vert in rows[k] else k + 1
                ii = (rows[kk].index(lp.vert))
                lp[uv].uv = (ii / M * 1.6, kk / N * length / 40.0)
    c = bm.verts.new(V(x, yc, top - 1.5 - length))
    for i in range(M):
        bm.faces.new((rows[-1][(i + 1) % M], rows[-1][i], c))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj(bm, m)
    if sleeves:
        for s_ in (-1, 1):
            tube([(x + 0.5, yc + s_ * hw0 * 0.9, top - 4.0), (x + 1.0, yc + s_ * hw0 * 1.02, top - 22.0), (x + 1.8 + sway * 0.2, yc + s_ * hw0 * 0.96, top - 44.0)], 3.0, m, 10)


def shoes(x, y, m, yaw=0.0):
    for s_ in (-1, 1):
        cx, cy = x + s_ * 5.0 * math.cos(math.radians(yaw + 90)), y + s_ * 5.0 * math.sin(math.radians(yaw + 90))
        lathe([(0, 0), (4.0, 0.0), (4.4, 2.0), (4.0, 4.5), (2.6, 6.5), (0, 7.0)], m, (cx, cy, WZ0), 20, yaw + random.uniform(-8, 8), sx=2.6, sy=1.0)


def folded(x, y, z, w, d, n, mats):
    zz = z
    for i in range(n):
        h = random.uniform(2.6, 4.2)
        box((w + random.uniform(-2, 2), d + random.uniform(-2, 2), h), (x + random.uniform(-1.2, 1.2), y + random.uniform(-1.2, 1.2), zz), random.choice(mats), random.uniform(-6, 6), bevel=1.0)
        zz += h
    return zz


def aide_wardrobe():
    """Mrs. Pruitt's things, the aide who lived in: her white uniform dresses, a cardigan, a raincoat, Sunday blouse; her
    shoes in pairs underneath, sweaters folded on the floor of it and a hat box."""
    random.seed(1991)
    rail()
    # (the left door stays shut, so most of it hangs in the open right half, +X, where it can be seen)
    plan = [(-40.0, 112.0, "MI_FabricDark", True), (-28.0, 90.0, "M_HarrowBurgundy", False), (4.0, 104.0, "MI_Sheet", False), (11.0, 104.0, "MI_Sheet", False),
            (19.0, 72.0, "MI_FabricBlue", True), (27.0, 64.0, "M_HarrowGingham", True), (35.0, 66.0, "MI_FabricGreen", True)]
    for i, (x, L, m, sl) in enumerate(plan):
        garment(x, L, m, 44.0 if L < 100 else 40.0, sl, seed=i * 1.7, sway=random.uniform(-2, 2))
    for i in range(4):                                                                                            # empty hangers
        x = 41.0 + i * 3.0
        tube([(x, RAIL_Y - 19.0, RAIL_Z - 7.5), (x, RAIL_Y - 9.0, RAIL_Z - 5.5), (x, RAIL_Y, RAIL_Z - 4.5), (x, RAIL_Y + 9.0, RAIL_Z - 5.5), (x, RAIL_Y + 19.0, RAIL_Z - 7.5)],
             0.7, "MI_WoodDark", 8)
        tube([(x, RAIL_Y, RAIL_Z - 4.5), (x, RAIL_Y, RAIL_Z + 1.0), (x, RAIL_Y - 1.6, RAIL_Z + 2.6)], 0.22, CHROME, 6)
    shoes(8.0, -12.0, "M_PhoneIvory", 95.0)                                                                       # white work shoes
    shoes(22.0, -12.0, "MI_Leather", 88.0)
    shoes(-30.0, -14.0, "MI_LeatherTan", 85.0)
    zz = folded(38.0, -30.0, WZ0, 22.0, 30.0, 6, ["MI_FabricBlue", "MI_FabricGreen", "MI_Sheet", "MI_FabricDark"])
    lathe([(0, 0), (12.0, 0), (12.0, 11.0), (12.6, 11.0), (12.6, 14.0), (0, 14.0)], "M_HarrowCalico", (38.0, -30.0, zz), 40)
    export("SM_PolishAideWardrobe")


def sewing_wardrobe():
    """Edith's sewing store: dresses half made, pinned and tacked, on the rail; bolts of cloth stood on end, folded lengths,
    pattern envelopes, a tin of notions and a tape measure hanging off the rail."""
    random.seed(1957)
    rail()
    plan = [(-40.0, 96.0, "M_HarrowCalico", False), (-28.0, 88.0, "M_HarrowGingham", True), (2.0, 102.0, "M_HarrowBrocade", False),
            (10.0, 60.0, "MI_Sheet", True), (18.0, 92.0, "MI_FabricRed", False), (26.0, 80.0, "M_HarrowBurgundy", True)]
    for i, (x, L, m, sl) in enumerate(plan):
        garment(x, L, m, 42.0, sl, seed=i * 2.3, sway=random.uniform(-2.5, 2.5))
    tube([(34.0, RAIL_Y + 2.0, RAIL_Z + 1.2), (34.6, RAIL_Y + 4.0, RAIL_Z - 30.0), (35.0, RAIL_Y + 5.0, RAIL_Z - 62.0)], 0.35, "M_PhoneIvory", 4)   # tape measure
    tube([(36.0, RAIL_Y - 2.0, RAIL_Z + 1.2), (36.4, RAIL_Y - 4.0, RAIL_Z - 26.0), (37.0, RAIL_Y - 5.0, RAIL_Z - 48.0)], 0.35, "M_PhoneIvory", 4)
    for i in range(5):                                                                                            # bolts on end
        x = 22.0 + i * 6.5
        box((3.5, 26.0, 62.0 + random.uniform(-6, 6)), (x, -28.0, WZ0), random.choice(FABRICS), tilt=(0.0, random.uniform(-10, 4)), bevel=1.2)
    zz = folded(6.0, -24.0, WZ0, 24.0, 30.0, 7, FABRICS)
    for i in range(5):                                                                                            # pattern envelopes
        box((16.0, 23.0, 0.4), (6.0 + random.uniform(-2, 2), -24.0 + random.uniform(-2, 2), zz + i * 0.45), PAPER, random.uniform(-20, 20), bevel=0.0)
    box((24.0, 15.0, 9.0), (-30.0, -30.0, WZ0), "M_HarrowEnamel", 6.0, bevel=0.8)                               # the notions tin
    box((24.6, 15.6, 1.2), (-30.0, -30.0, WZ0 + 9.0), "M_HarrowEnamel", 6.0, bevel=0.5)
    for i in range(6):                                                                                            # cotton reels on its lid
        lathe([(0, 0), (1.4, 0), (1.4, 0.5), (1.1, 0.6), (1.1, 3.2), (1.4, 3.3), (1.4, 3.8), (0, 3.8)], random.choice(FABRICS), (-38.0 + i * 3.4, -30.0, WZ0 + 10.2), 12)
    export("SM_PolishSewingWardrobe")


def present(x, y, z, w, d, h, paper, ribbon, yaw=0.0):
    """A wrapped box, ribboned both ways with a bow on top and a paper tag."""
    box((w, d, h), (x, y, z), paper, yaw, bevel=0.35)
    box((w + 0.3, 1.6, h + 0.3), (x, y, z - 0.15), ribbon, yaw, bevel=0.1)
    box((1.6, d + 0.3, h + 0.3), (x, y, z - 0.15), ribbon, yaw, bevel=0.1)
    s = min(w, d) * 0.18 + 1.5
    for a in (35.0, 215.0, 125.0):
        ca, sa = math.cos(math.radians(a + yaw)), math.sin(math.radians(a + yaw))
        tube([(x, y, z + h + 0.3), (x + ca * s * 0.6, y + sa * s * 0.6, z + h + s * 0.55), (x + ca * s, y + sa * s, z + h + 0.6), (x + ca * s * 0.35, y + sa * s * 0.35, z + h + 0.5)], 0.6, ribbon, 6)
    box((4.0, 0.15, 2.6), xform((w / 2 * 0.6, d / 2 + 0.3, h * 0.5), (x, y, z), yaw), "M_ItemCard", yaw, tilt=(-10.0, 0.0), bevel=0.0)


PAPERS = ["MI_FabricRed", "MI_FabricGreen", "M_HarrowGingham", "M_HarrowCalico", "M_HarrowBrocade", "MI_FabricBlue", "M_HarrowWrapper", "MI_ToyRed", "MI_ToyBlue"]
RIBBONS = ["M_ItemRibbon", "M_ItemGold", "MI_Sheet", "MI_FabricRed"]


def attic_presents():
    """Every Christmas since 1969, a present for Danny and one for Ruth, wrapped and tagged and never opened: packed into
    the attic wardrobe to the top and spilling out onto the boards in front of it."""
    random.seed(1969)
    # inside, stacked in rough columns from the floor of the wardrobe to near its top
    x = WX0 + 2.0
    while x < WX1 - 8.0:
        w = random.uniform(16, 30)
        if x + w > WX1:
            w = WX1 - x
        z = WZ0
        while z < WZ1 - 24.0:
            h = random.uniform(7, 22)
            d = random.uniform(20, 44)
            present(x + w / 2 + random.uniform(-1, 1), WY0 + d / 2 + random.uniform(0, 4), z, w - 1.0, d, h, random.choice(PAPERS), random.choice(RIBBONS), random.uniform(-5, 5))
            z += h + 0.3
        x += w + 0.4
    # spilled out in front
    floor = []
    for i in range(6):
        w, d, h = random.uniform(18, 34), random.uniform(18, 34), random.uniform(8, 20)
        px, py = -58.0 + i * 15.0 + random.uniform(-3, 3), random.uniform(20, 58)
        present(px, py, 0.0, w, d, h, random.choice(PAPERS), random.choice(RIBBONS), random.uniform(-25, 25))
        floor.append((px, py, h, min(w, d)))
    for (px, py, h, s_) in floor[::2]:                                                                          # a smaller one on top
        present(px + random.uniform(-2, 2), py + random.uniform(-2, 2), h + 0.35, s_ * 0.6, s_ * 0.55, random.uniform(5, 10), random.choice(PAPERS),
                random.choice(RIBBONS), random.uniform(0, 90))
    export("SM_PolishAtticPresents")


SETS.update({"SM_PolishAideWardrobe": aide_wardrobe, "SM_PolishSewingWardrobe": sewing_wardrobe, "SM_PolishAtticPresents": attic_presents})


# ---------------------------------------------------------------------------------------------------- mock-ups: clutter
# Lived-in clutter for two bare tops, pivot at the middle of the top surface (z 0 is the top), front +Y.  Mock-ups for
# Cheyenne to keep or trash (2026-11-22).
def frame(x, y, w, h, yaw, m="MI_WoodDark", pic="MI_PortraitFace"):
    box((w, 1.2, h), (x, y, 0.0), m, yaw, tilt=(-14.0, 0.0), bevel=0.3)
    box((w - 3.0, 0.2, h - 3.0), xform((0, 0.7, 1.5), (x, y, 0.0), yaw, (-14.0, 0.0)), pic, yaw, tilt=(-14.0, 0.0), bevel=0.0)
    box((w - 2.6, 0.1, h - 2.6), xform((0, 0.9, 1.3), (x, y, 0.0), yaw, (-14.0, 0.0)), GLASS, yaw, tilt=(-14.0, 0.0), bevel=0.0)
    box((1.0, 7.0, 0.8), xform((0, -4.5, 0.0), (x, y, 0.0), yaw), m, yaw, tilt=(30.0, 0.0), bevel=0.1)       # the stand at the back


def doily(x, y, R, yaw=0.0):
    pts = [(0, 0.05)]
    lathe([(0, 0.0), (R, 0.0), (R, 0.12), (0, 0.12)], "MI_Sheet", (x, y, 0.0), 48, yaw)
    for i in range(16):
        a = TAU * i / 16
        lathe([(0, 0.0), (2.0, 0.0), (2.0, 0.1), (0, 0.1)], "MI_Sheet", (x + math.cos(a) * R, y + math.sin(a) * R, 0.01), 12)


def mail(x, y, n, yaw):
    z = 0.0
    for i in range(n):
        box((16.0, 9.5, 0.35), (x + random.uniform(-1.2, 1.2), y + random.uniform(-1, 1), z), random.choice((PAPER, PAPER, "M_ItemCard")), yaw + random.uniform(-10, 10), bevel=0.0)
        z += 0.38
    tube([(x - 8.5, y - 3.0, z * 0.5), (x - 8.5, y + 3.0, z * 0.5)], 0.25, "MI_ToyRed", 6)                    # rubber band
    return z


def glasses(x, y, yaw):
    for s_ in (-1, 1):
        c = xform((s_ * 3.0, 0, 1.6), (x, y, 0.0), yaw, (70.0, 0.0))
        tube([xform((s_ * 3.0 + 1.9 * math.cos(TAU * i / 16), 0, 1.6 + 1.5 * math.sin(TAU * i / 16)), (x, y, 0.0), yaw, (70.0, 0.0)) for i in range(17)], 0.12, "M_PhoneBakelite", 5)
        lathe([(0, 0), (1.8, 0), (1.8, 0.1), (0, 0.1)], GLASS, c, 16, yaw, tilt=(-20.0, 0.0), sx=1.05, sy=0.8)
        tube([xform((s_ * 5.0, 0, 1.8), (x, y, 0.0), yaw, (70.0, 0.0)), xform((s_ * 5.6, -12.0, 0.4), (x, y, 0.0), yaw)], 0.12, "M_PhoneBakelite", 5)


def dead_flowers(x, y):
    lathe([(0, 0), (3.0, 0), (3.4, 1.0), (4.6, 8.0), (3.0, 15.0), (2.0, 18.0), (2.6, 20.0), (2.3, 20.0), (1.6, 18.0), (2.6, 15.0), (4.2, 8.0), (2.6, 1.0), (0, 1.0)],
          "M_HarrowEnamel", (x, y, 0.0), 28)
    for i in range(9):
        a, r = random.uniform(0, TAU), random.uniform(0.0, 1.2)
        top = (x + math.cos(a) * (3 + 9 * r), y + math.sin(a) * (3 + 7 * r), 26.0 + random.uniform(0, 14) - 6 * r)
        mid = (x + math.cos(a) * (1.5 + 3 * r), y + math.sin(a) * (1.5 + 3 * r), 21.0)
        tube([(x, y, 12.0), mid, top, (top[0] + math.cos(a) * 3, top[1] + math.sin(a) * 3, top[2] - random.uniform(2, 8))], 0.16, "MI_FabricGreen", 5)
        lathe([(0, 0), (1.4, 0.4), (1.6, 1.6), (0.6, 2.4), (0, 2.5)], random.choice(("MI_FabricDark", "MI_LeatherTan", "MI_Cardboard")),
              (top[0] + math.cos(a) * 3, top[1] + math.sin(a) * 3, top[2] - 3.0), 10, tilt=(random.uniform(60, 160), random.uniform(-30, 30)))
    for i in range(5):                                                                                          # petals dropped
        box((1.6, 1.0, 0.1), (x + random.uniform(-14, 14), y + random.uniform(-10, 10), 0.0), "MI_FabricDark", random.uniform(0, 180), bevel=0.0)


def candle(x, y, H=7.0):
    lathe([(0, 0), (5.0, 0), (5.2, 0.6), (1.6, 1.2), (1.4, 4.0), (2.4, 4.6), (2.4, 5.2), (0, 5.2)], BRASS, (x, y, 0.0), 24)
    lathe([(0, 5.2), (1.9, 5.2), (2.0, 5.2 + H), (0.4, 5.2 + H + 0.4), (0, 5.2 + H + 0.4)], "M_PhoneIvory", (x, y, 0.0), 16)
    tube([(x, y, 5.2 + H + 0.3), (x, y, 5.2 + H + 1.4)], 0.1, "M_Black", 4)
    for a in (0.6, 2.4, 4.2):                                                                                   # wax run down it
        tube([(x + 2.0 * math.cos(a), y + 2.0 * math.sin(a), 5.2 + H), (x + 2.1 * math.cos(a), y + 2.1 * math.sin(a), 5.2 + H * 0.5), (x + 2.6 * math.cos(a), y + 2.6 * math.sin(a), 5.0)], 0.35, "M_PhoneIvory", 6)


def mock_clutter_dresser():
    """The dining-room dresser: family photographs, a doily under a dish of old candies, the mail she stopped opening, her
    pill organiser, her reading glasses, a vase of flowers long dead, a burned-down candle."""
    random.seed(1993)
    doily(-6.0, -2.0, 15.0)
    for (x, y, w, h, yaw) in ((-44.0, -16.0, 14.0, 19.0, 8.0), (-28.0, -18.0, 18.0, 23.0, -4.0), (34.0, -17.0, 13.0, 17.0, -10.0)):
        frame(x, y, w, h, yaw)
    lathe([(0, 0), (3.5, 0), (3.6, 0.5), (1.4, 1.2), (1.3, 3.5), (6.5, 5.0), (9.0, 8.5), (8.6, 8.5), (6.2, 5.6), (0, 4.0)], GLASS, (-6.0, -2.0, 0.12), 32)
    for i in range(14):
        a, r = random.uniform(0, TAU), random.uniform(0, 5.5)
        lathe([(0, 0), (1.0, 0.3), (1.0, 0.9), (0, 1.2)], random.choice(("MI_ToyRed", "MI_ToyYellow", "MI_FabricGreen", "M_PhoneIvory")),
              (-6.0 + math.cos(a) * r, -2.0 + math.sin(a) * r, 4.3 + r * 0.35 + random.uniform(0, 1.2)), 8, random.uniform(0, 180), sx=1.6)
    mail(18.0, 10.0, 9, -12.0)
    box((19.0, 5.0, 2.2), (-32.0, 12.0, 0.0), "M_HarrowEnamel", 6.0, bevel=0.4)                                  # pill organiser
    for i in range(7):
        box((2.3, 4.2, 0.6), (-32.0 - 8.1 + i * 2.7, 12.0, 2.2), random.choice(("M_HarrowEnamel", "MI_ToyBlue", "MI_ToyYellow")), 6.0, bevel=0.1)
    glasses(2.0, 16.0, 20.0)
    dead_flowers(46.0, -8.0)
    candle(20.0, -12.0)
    export("SM_MockClutterDresser")


def mock_clutter_table():
    """The side table by the sofa: an ashtray full, a pack of cigarettes and a lighter, the TV Guide, a coffee mug with a
    dried ring in it, the television's remote."""
    random.seed(1994)
    lathe([(0, 0), (6.5, 0), (7.0, 0.5), (7.0, 2.6), (6.2, 2.8), (5.4, 1.0), (0, 1.0)], GLASS, (-16.0, -8.0, 0.0), 32)
    for i in range(7):
        a = random.uniform(0, TAU)
        p0 = (-16.0 + math.cos(a) * random.uniform(0, 3), -8.0 + math.sin(a) * random.uniform(0, 3), 1.2)
        p1 = (p0[0] + math.cos(a) * 3.0, p0[1] + math.sin(a) * 3.0, 1.5 + random.uniform(0, 1.4))
        tube([p0, p1], 0.4, random.choice(("M_PhoneIvory", "MI_Cardboard")), 6)
    lathe([(0, 0), (6.2, 0), (6.2, 1.1), (0, 1.1)], "M_Black", (-16.0, -8.0, 0.0), 32)                          # ash in the bottom
    box((5.6, 2.2, 8.6), (2.0, -12.0, 0.0), "MI_ToyRed", 14.0, tilt=(0.0, 90.0), bevel=0.2)                     # cigarettes, on its side
    box((2.4, 1.2, 7.2), (6.0, -4.0, 0.0), "MI_ToyBlue", -30.0, tilt=(0.0, 90.0), bevel=0.3)                    # lighter
    box((13.5, 19.0, 0.6), (14.0, 6.0, 0.0), "M_HarrowWrapper", -8.0, bevel=0.1)                                 # TV Guide
    cup((-18.0, 12.0, 0.0), 210.0, R=4.2, H=9.2, m="M_HarrowEnamel")
    lathe([(0, 0.95), (3.7, 0.95), (3.7, 1.3), (0, 1.3)], "M_KitchenTar", (-18.0, 12.0, 0.0), 24)                 # dried coffee
    box((5.0, 17.0, 2.0), (30.0, -2.0, 0.0), "M_PhoneBakelite", 12.0, bevel=0.6)                                 # the remote
    for i in range(12):
        box((0.9, 0.9, 0.4), xform((-1.3 + (i % 3) * 1.3, -5.0 + (i // 3) * 2.2, 2.0), (30.0, -2.0, 0.0), 12.0), random.choice(("M_PhoneIvory", "MI_ToyRed")), 12.0, bevel=0.1)
    export("SM_MockClutterTable")


SETS.update({"SM_MockClutterDresser": mock_clutter_dresser, "SM_MockClutterTable": mock_clutter_table})


def alcove_metronome():
    """Walnut case with inset face, graduated scale, pendulum and winding key."""
    box((15.5, 10, 1.4), (0, 0, 0), "M_HarrowWalnut", bevel=.45)
    box((14, 8.8, 1.1), (0, 0, 1.4), TRIM, bevel=.25)
    # Stepped feet are hidden underneath the bevel of the case.
    for x in (-5, 5):
        for y in (-3, 3):
            box((2.5, 2.5, .45), (x, y, 0), TRIM, bevel=.14)
    bm = bmesh.new()
    rings = []
    for width, depth, z in ((13, 8, 2), (12, 7.7, 4), (5.3, 5.0, 24), (4.5, 4.2, 25.8)):
        rings.append([bm.verts.new(V(x*width/2, y*depth/2, z))
                      for x,y in ((-1,-1),(1,-1),(1,1),(-1,1))])
    for a, b in zip(rings, rings[1:]):
        for i in range(4):
            j = (i+1) % 4
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new(rings[0]); bm.faces.new(rings[-1])
    bm.normal_update()
    uv = bm.loops.layers.uv.new("UVMap")
    for face in bm.faces:
        for l in face.loops:
            p = l.vert.co
            l[uv].uv = ((p.y if abs(face.normal.x) > .5 else p.x)*5+.5, p.z*4)
    bmesh.ops.bevel(bm, geom=list(bm.edges), offset=.0019, segments=2, affect="EDGES", clamp_overlap=True)
    obj(bm, "M_HarrowWalnut", False)
    box((2.3, .5, 19.2), (0, 4.0, 4.5), BRASS, tilt=(3.8,0), bevel=.12)
    for i in range(14):
        z = 6 + i*1.1
        box((1.35 if i % 3 == 0 else .82, .08, .12), (0, 4.36-(z-4.5)*.067,z), "M_Black", bevel=0)
    tube([(0.1,4.7,6),(1.7,4.0,21.0)], .14, STEEL, 8)
    box((1.5, 1.0, 2.0), (1.17,4.25,15.25), BRASS, tilt=(0,6), bevel=.16)
    tube([(5.7,0,7),(8.6,0,7)], .35, BRASS, 10)
    tube([(8.6,-1.5,7),(8.6,0,8.1),(8.6,1.5,7),(8.6,0,5.9),(8.6,-1.5,7)], .21, BRASS, 8)
    export("SM_AlcoveMetronomeSet")


def scullery_washboard():
    """Corrugated zinc washboard resting in a shallow enamel tray."""
    lathe([(0,0), (18.5,0), (20.4,.9), (22.8,9.3), (22.8,10.0),
           (21.9,10.1), (20.9,8.6), (18.3,.9), (0,.9)],
          "M_HarrowEnamel", (0,0,0), 48, sx=1.25, sy=.72)
    for x in (-28.4,28.4):
        tube([(x*.88,-4,8),(x,-5,9.5),(x,-5,11.5),(x,4,11.5),(x,4,9.4),(x*.88,4,8)], .53, STEEL, 10)
    for x in (-12.,12.):
        box((2.7, 2.6, 36), (x,-5.,2), WOOD, tilt=(19.,0.), bevel=.37)
    box((24, 2.1, 4.3), (0,-15.25,32.0), WOOD, tilt=(19.,0.), bevel=.4)
    for z in range(7,31):
        y = -5.0 - (z-2)*.344
        tube([(-10.9,y,z),(10.9,y,z)], .63, STEEL, 10)
    box((8.2,5.3,2.5), (13,4.5,1), "M_PhoneIvory", yaw=11, bevel=.67)
    export("SM_SculleryWashSet")


def folded_linen():
    for i,(width, depth, shade, yaw) in enumerate(((27,21,SHEET,2),(27,20,SHEET,-5),(23,18,"MI_FabricGreen",4),
                                                   (23,17,SHEET,-4),(19,15,SHEET,4))):
        z=i*2.4
        box((width,depth,2.65), (1,(-1)**i*.45,z), shade,yaw,bevel=.85)
        # Two rounded woven hems follow the folded front edge.
        for trimz in (.54,1.21):
            tube([xform((x,depth*.475,z+trimz),(1,0,0),yaw) for x in (-width*.40,0,width*.4)], .13, shade, 8)
    export("SM_LinenStackSet")


def wrapped_patterns():
    for i,(x,y,w,d,yaw) in enumerate(((-11,0,22,28,-8),(9,-2,22,26,13),(6,5,18,21,-7))):
        z = 4.0 if i==2 else 0.
        box((w,d,4.2), (x,y,z), PAPER, yaw, bevel=.6)
        for u_,v_ in ((.24,0),(-.22,0)):
            at = (x,y,z)
            tube([xform((u_*w,h,4.24),at,yaw) for h in (-d/2,0,d/2)],.16,BRASS,8)
        tube([xform((k,v_,4.26),(x,y,z),yaw) for k in (-w/2,0,w/2)], .17, BRASS, 8)
        box((7,5,.12), xform((2,4,4.3),(x,y,z),yaw), "M_PhoneIvory", yaw, bevel=.05)
    export("SM_BoxRoomPatternSet")


SETS.update({"SM_AlcoveMetronomeSet": alcove_metronome, "SM_SculleryWashSet": scullery_washboard,
             "SM_LinenStackSet": folded_linen, "SM_BoxRoomPatternSet": wrapped_patterns})


for name, fn in SETS.items():
    if argv and name not in argv:
        continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fn()
print("POLISH done")
