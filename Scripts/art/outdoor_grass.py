"""Blender: clumps of dead November grass, built blade by blade (Cheyenne, 2026-11-28: "the grass needs to be revamped and
actually look like grass").  Each blade is a tapered, bowed strip leaning out of the crown; some are broken over.
Colour is painted on the vertices (rotted brown at the crown, olive up the blade, bleached straw at the tip, about half the
blades dead to the base), so no texture is needed.  Vertex alpha = how much that point may sway in the wind (0 at the root).
Normals point mostly up so a clump is lit as one soft mass, not as hundreds of little mirrors.

  blender -b --factory-startup -P outdoor_grass.py -- <out_dir> [--preview]
    <out_dir>/SM_Grass_<T1..F2>.fbx      fifteen clumps; one material slot "GrassBlades"; metres here = centimetres in Unreal
Scripts/level/outdoor_plant.py decides where they grow, Scripts/level/import_outdoors.py imports them and makes the
material, Scripts/level/polish_outdoors.py plants them on the map as instances."""
import bpy, math, os, random, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
PREVIEW = "--preview" in argv
os.makedirs(OUT, exist_ok=True)
PI = math.pi


def lerp3(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def blades(buf, n, h, spread, seed, lean, short=0.4, heads=0, dry=0.55, at=(0.0, 0.0, 0.0), yaw=0.0, size=1.0, flip=False):
    """Write one clump into buf = (verts, faces, cols, normals), at a place, turned and scaled.  flip mirrors Y (for
    meshes built in level coordinates: the FBX import mirrors it back)."""
    rr = random.Random(seed)
    verts, faces, cols, nrm = [], [], [], []
    crown = (0.020, 0.015, 0.008)

    def blade(bx, by, L, w, ha, ln, colour, tip, kink, segs=4):
        tw = ha + PI / 2 + rr.uniform(-0.7, 0.7)
        base = len(verts)
        for s in range(segs + 1):
            t = s / segs
            out = ln * L * t ** 1.8
            z = L * (t - 0.22 * min(ln, 1.2) * t ** 3)
            if kink and t > 0.5:
                out += L * (t - 0.5) * 0.9
                z -= L * (t - 0.5) * 1.3
            cx, cy = bx + out * math.cos(ha), by + out * math.sin(ha)
            ww = w * (1.0 - t ** 1.7) + 0.00025
            z = max(z, 0.003)
            c = lerp3(crown, colour, min(1.0, t / 0.22)) if t < 0.22 else lerp3(colour, tip, ((t - 0.22) / 0.78) ** 1.6)
            sway = t ** 1.5
            for sgn in (-1, 1):
                verts.append((cx + sgn * ww * math.cos(tw), cy + sgn * ww * math.sin(tw), z))
                cols.append((c[0], c[1], c[2], sway))
                nrm.append(Vector((cx * 2.2, cy * 2.2, 1.0)).normalized())
        for s in range(segs):
            q = base + 2 * s
            faces.append((q, q + 1, q + 3, q + 2))

    for b in range(n):
        a = rr.uniform(0, 2 * PI)
        d = spread * rr.random() ** 0.7
        g = rr.random()
        olive = lerp3((0.040, 0.058, 0.018), (0.105, 0.118, 0.044), g)
        straw = lerp3((0.230, 0.185, 0.085), (0.400, 0.345, 0.180), rr.random())
        dead = rr.random() < dry
        colour = lerp3(straw, (0.12, 0.085, 0.04), rr.random() * 0.5) if dead else olive
        tip = straw if (dead or rr.random() < 0.7) else lerp3(olive, straw, 0.4)
        blade(d * math.cos(a), d * math.sin(a), h * rr.uniform(short, 1.0), rr.uniform(0.0022, 0.0046), a + rr.uniform(-1.0, 1.0),
              lean * rr.uniform(0.2, 1.4) * (0.45 + 0.9 * d / spread), colour, tip, rr.random() < 0.14)
    for k in range(heads):                                                   # seeding stalks standing above the clump
        a = rr.uniform(0, 2 * PI)
        d = spread * 0.5 * rr.random()
        L = h * rr.uniform(1.2, 1.7)
        ha, ln = rr.uniform(0, 2 * PI), rr.uniform(0.05, 0.22)
        stalk = lerp3((0.20, 0.16, 0.075), (0.33, 0.28, 0.14), rr.random())
        bx, by = d * math.cos(a), d * math.sin(a)
        blade(bx, by, L, 0.0011, ha, ln, stalk, stalk, False, 5)
        # the head: a spindle of four small leaves at the top of the stalk
        tx, ty, tz = bx + ln * L * math.cos(ha), by + ln * L * math.sin(ha), L * (1.0 - 0.22 * ln)
        hc = lerp3((0.060, 0.042, 0.020), (0.125, 0.092, 0.042), rr.random())
        hl = rr.uniform(0.03, 0.06)
        for j in range(4):
            aa = j * PI / 4
            base = len(verts)
            pts = [(0.0, -hl * 0.15), (0.0022, hl * 0.3), (0.0, hl), (-0.0022, hl * 0.3)]
            for px, pz in pts:
                verts.append((tx + px * math.cos(aa), ty + px * math.sin(aa), tz + pz))
                cols.append((hc[0], hc[1], hc[2], 1.0))
                nrm.append(Vector((tx * 2.2, ty * 2.2, 1.0)).normalized())
            faces.append((base, base + 1, base + 2, base + 3))
    V, F, C, N = buf
    off = len(V)
    ca, sa = math.cos(yaw), math.sin(yaw)
    ys = -1.0 if flip else 1.0
    for (x, y, z), nn in zip(verts, nrm):
        V.append((at[0] + (x * ca - y * sa) * size, at[1] + ys * (x * sa + y * ca) * size, at[2] + z * size))
        N.append((nn.x * ca - nn.y * sa, ys * (nn.x * sa + nn.y * ca), nn.z))
    C += cols
    F += [tuple(off + i for i in f) for f in faces]


def to_object(name, buf):
    verts, faces, cols, nrm = buf
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ca = me.color_attributes.new("Col", "FLOAT_COLOR", "POINT")
    for i, c in enumerate(cols):
        ca.data[i].color = c
    me.color_attributes.active_color = ca
    try:
        me.color_attributes.render_color_index = 0
    except Exception:
        pass
    for p in me.polygons:
        p.use_smooth = True
    try:
        me.normals_split_custom_set_from_vertices([tuple(v) for v in nrm])
    except Exception as exc:
        print("GRASS normals:", exc)
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    m = bpy.data.materials.get("GrassBlades") or bpy.data.materials.new("GrassBlades")
    m.use_nodes = True
    nt = m.node_tree
    if not any(n.type == "VERTEX_COLOR" for n in nt.nodes):
        vc = nt.nodes.new("ShaderNodeVertexColor")
        vc.layer_name = "Col"
        b = next(x for x in nt.nodes if x.type == "BSDF_PRINCIPLED")
        nt.links.new(vc.outputs["Color"], b.inputs["Base Color"])
        b.inputs["Roughness"].default_value = 0.75
    m.use_backface_culling = False
    me.materials.append(m)
    return ob


def clump(name, **kw):
    buf = ([], [], [], [])
    blades(buf, **kw)
    print(f"GRASS {name}: {len(buf[1]) * 2} triangles, {max(v[2] for v in buf[0]) * 100:.0f} cm tall")
    return to_object(name, buf)


def export(ob, path):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, mesh_smooth_type="OFF",
                             add_leaf_bones=False, bake_anim=False, apply_scale_options="FBX_SCALE_NONE", colors_type="LINEAR")


SPECS = [  # tall tussocks
         ("SM_Grass_T1", dict(n=78, h=0.50, spread=0.085, seed=1, lean=0.34, heads=3)),
         ("SM_Grass_T2", dict(n=66, h=0.42, spread=0.09, seed=11, lean=0.40)),
         ("SM_Grass_T3", dict(n=86, h=0.56, spread=0.10, seed=12, lean=0.30, heads=2)),
         # gone to seed
         ("SM_Grass_S1", dict(n=46, h=0.62, spread=0.06, seed=4, lean=0.24, heads=9, dry=0.75)),
         ("SM_Grass_S2", dict(n=38, h=0.52, spread=0.065, seed=14, lean=0.28, heads=6, dry=0.8)),
         # the common clump
         ("SM_Grass_C1", dict(n=76, h=0.33, spread=0.11, seed=2, lean=0.48)),
         ("SM_Grass_C2", dict(n=60, h=0.27, spread=0.10, seed=21, lean=0.55)),
         ("SM_Grass_C3", dict(n=70, h=0.37, spread=0.12, seed=22, lean=0.45, dry=0.4)),
         ("SM_Grass_C4", dict(n=56, h=0.30, spread=0.13, seed=23, lean=0.60)),
         # beaten down by rain
         ("SM_Grass_B1", dict(n=64, h=0.40, spread=0.10, seed=5, lean=0.95, dry=0.7)),
         ("SM_Grass_B2", dict(n=52, h=0.34, spread=0.11, seed=51, lean=1.05, dry=0.75)),
         # low turf
         ("SM_Grass_L1", dict(n=96, h=0.17, spread=0.20, seed=3, lean=0.70, short=0.5, dry=0.45)),
         ("SM_Grass_L2", dict(n=74, h=0.14, spread=0.17, seed=31, lean=0.80, short=0.5, dry=0.5)),
         # sprouts between the clumps and in the crown of the road
         ("SM_Grass_F1", dict(n=44, h=0.10, spread=0.15, seed=6, lean=0.6, short=0.5, dry=0.35)),
         ("SM_Grass_F2", dict(n=30, h=0.08, spread=0.12, seed=61, lean=0.6, short=0.5, dry=0.35))]

bpy.ops.wm.read_factory_settings(use_empty=True)
obs = []
for nm, kw in SPECS:
    ob = clump(nm, **kw)
    obs.append(ob)
    export(ob, os.path.join(OUT, nm + ".fbx"))

if PREVIEW:
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.012, 0.016, 1)
    for i, ob in enumerate(obs):
        ob.location = ((i % 5) * 0.62 - 1.24, (i // 5) * 0.7 - 0.5, 0)
    # a patch as the level will scatter it, behind the six
    rr = random.Random(7)
    for k in range(60):
        src = rr.choice(obs)
        d = bpy.data.objects.new("i", src.data)
        d.location = (rr.uniform(-1.6, 1.6), rr.uniform(1.4, 3.2), 0)
        d.rotation_euler = (0, 0, rr.uniform(0, 6.28))
        s = rr.uniform(0.8, 1.25)
        d.scale = (s, s, s)
        sc.collection.objects.link(d)
    bpy.ops.mesh.primitive_plane_add(size=30)
    fm = bpy.data.materials.new("floor"); fm.use_nodes = True
    fb = next(x for x in fm.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    fb.inputs["Base Color"].default_value = (0.02, 0.016, 0.011, 1); fb.inputs["Roughness"].default_value = 0.9
    bpy.context.object.data.materials.append(fm)
    L = bpy.data.objects.new("key", bpy.data.lights.new("key", "SPOT"))
    L.data.energy = 900; L.data.spot_size = 1.1; L.data.color = (1.0, 0.93, 0.8)
    L.location = (0.3, -2.6, 1.5)
    L.rotation_euler = (Vector((0, 1.0, 0.0)) - L.location).to_track_quat("-Z", "Y").to_euler()
    sc.collection.objects.link(L)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 28
    cam.location = (0.0, -2.9, 1.45)
    cam.rotation_euler = (Vector((0, 0.7, 0.1)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = 1280; sc.render.resolution_y = 720
    sc.view_settings.view_transform = "Standard"
    sc.render.filepath = os.path.join(OUT, "preview_grass.png")
    bpy.ops.render.render(write_still=True)

print("GRASS done")
