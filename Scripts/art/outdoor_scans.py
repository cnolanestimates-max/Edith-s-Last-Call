"""Blender: prepare the photo-scanned Fab assets for the yard (Cheyenne, 2026-11-28: "AAA quality please").

Sources are her own Fab library downloads, unpacked under SourceArt/Fab/<name>/x (Fab Standard License: commercial use,
no credit needed):
  Quixel Megascans "Urban Australian Desolation Wheelbarrow Metal Rusty" (photogrammetry), "Mossy Rock",
  "Forest pine boulder", "mossy rocks from forest lidar scan", "Grass Vegitation Mix".

  blender -b --factory-startup -P outdoor_scans.py -- inspect            what is in each file (size, triangles, materials)
  blender -b --factory-startup -P outdoor_scans.py -- build [names]      SourceArt/Outdoors/scans/SM_Scan_<Name>.fbx + textures
Each scan is set upright on the ground with its pivot at the middle of its footprint, scaled to real size in metres
(= centimetres in Unreal), cleaned of loose scraps, reduced to a sane triangle count, and given one material slot."""
import bpy, bmesh, json, math, os, sys
from mathutils import Vector, Matrix

ROOT = "C:/GameDev/Unreal/WellnessCheck"
FAB = ROOT + "/SourceArt/Fab"
OUT = ROOT + "/SourceArt/Outdoors/scans"
argv = sys.argv[sys.argv.index("--") + 1:]
MODE = argv[0] if argv else "inspect"
ONLY = argv[1:]
os.makedirs(OUT, exist_ok=True)

SCANS = {
    "Wheelbarrow": dict(fbx="urban_australian_desolation_wheelbarrow_metal_rusty_yjvbcgl_high/x/Urban_Australian_Desolation_Wheelbarrow_Metal_Rusty_yjvbcgl_High.fbx"),
    "MossyRock": dict(fbx="mossy-rock/x/source/x/mossy_rock.fbx"),
    "PineBoulder": dict(fbx="forest_pine_boulder/x/source/x/pine-stone.fbx"),
    "LidarRocks": dict(fbx="mossy-rocks-from-forest-lidar-scan/x/source/forest_mossy_rocks.fbx"),
    "GrassMix": dict(fbx="grass-vegitation-mix/x/source/Grass Vegitation mix.fbx"),
}


def import_fbx(path):
    before = set(bpy.data.objects)
    try:
        bpy.ops.wm.fbx_import(filepath=path)
    except Exception:
        bpy.ops.import_scene.fbx(filepath=path)
    return [o for o in bpy.data.objects if o not in before]


def world_bounds(obs):
    lo = Vector((1e9, 1e9, 1e9)); hi = Vector((-1e9, -1e9, -1e9))
    for o in obs:
        if o.type != "MESH":
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
            hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    return lo, hi


def tex_material(name, base, normal=None, rough=None, metal=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = next(x for x in nt.nodes if x.type == "BSDF_PRINCIPLED")

    def img(path, non_color=False):
        n = nt.nodes.new("ShaderNodeTexImage")
        n.image = bpy.data.images.load(path, check_existing=True)
        if non_color:
            n.image.colorspace_settings.name = "Non-Color"
        return n
    nt.links.new(img(base).outputs[0], b.inputs["Base Color"])
    if rough:
        nt.links.new(img(rough, True).outputs[0], b.inputs["Roughness"])
    if metal:
        nt.links.new(img(metal, True).outputs[0], b.inputs["Metallic"])
    if normal:
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(img(normal, True).outputs[0], nm.inputs["Color"])
        nt.links.new(nm.outputs[0], b.inputs["Normal"])
    return m


def look_at(ob, target):
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()


def render_views(tag, lo, hi, views=((0.9, -1.5, 0.9), (0.0, -0.3, 2.2))):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 24
    try:
        sc.cycles.use_denoising = True
    except Exception:
        pass
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.35, 0.38, 0.42, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    c = (lo + hi) / 2
    size = max((hi - lo).x, (hi - lo).y, (hi - lo).z)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 40; cam.data.clip_start = size * 0.01; cam.data.clip_end = size * 50
    sc.render.resolution_x = 800; sc.render.resolution_y = 600
    sc.view_settings.view_transform = "Standard"
    outs = []
    for i, v in enumerate(views):
        cam.location = c + Vector(v).normalized() * size * 1.9
        look_at(cam, c)
        sc.render.filepath = f"{OUT}/preview_{tag}_{i}.png"
        bpy.ops.render.render(write_still=True)
        outs.append(sc.render.filepath)
    return outs


if MODE == "preview":
    for name, s in SCANS.items():
        if ONLY and name not in ONLY:
            continue
        bpy.ops.wm.read_factory_settings(use_empty=True)
        obs = [o for o in import_fbx(FAB + "/" + s["fbx"]) if o.type == "MESH"]
        if name == "Wheelbarrow":
            d = os.path.dirname(FAB + "/" + s["fbx"])
            pre = d + "/Urban_Australian_Desolation_Wheelbarrow_Metal_Rusty_yjvbcgl_High_4K_"
            m = tex_material("Scan", pre + "BaseColor.jpg", pre + "Normal.jpg", pre + "Roughness.jpg", pre + "Metalness.jpg")
            for o in obs:
                o.data.materials.clear(); o.data.materials.append(m)
        if name == "LidarRocks":
            for o in obs:
                lo, hi = world_bounds([o])
                for q in obs:
                    q.hide_render = q is not o
                render_views(f"{name}_{o.name[-1]}", lo, hi)
            continue
        lo, hi = world_bounds(obs)
        render_views(name, lo, hi)
    print("SCAN preview done")

if MODE == "inspect":
    for name, s in SCANS.items():
        if ONLY and name not in ONLY:
            continue
        bpy.ops.wm.read_factory_settings(use_empty=True)
        obs = import_fbx(FAB + "/" + s["fbx"])
        lo, hi = world_bounds(obs)
        print(f"SCAN {name}: {len(obs)} objects, size {hi.x - lo.x:.2f} x {hi.y - lo.y:.2f} x {hi.z - lo.z:.2f} m, lowest z {lo.z:.2f}")
        for o in obs:
            if o.type != "MESH":
                print(f"SCAN   {o.type} {o.name}")
                continue
            me = o.data
            tris = sum(len(p.vertices) - 2 for p in me.polygons)
            mats = [m.name if m else "-" for m in me.materials]
            imgs = []
            for m in me.materials:
                if m and m.use_nodes:
                    imgs += [n.image.name for n in m.node_tree.nodes if n.type == "TEX_IMAGE" and n.image]
            print(f"SCAN   mesh {o.name}: {len(me.vertices)} verts, {tris} tris, dims {o.dimensions.x:.2f} x {o.dimensions.y:.2f} x {o.dimensions.z:.2f}, "
                  f"scale {tuple(round(v, 3) for v in o.scale)}, uv {[u.name for u in me.uv_layers]}, mats {mats}, images {imgs[:6]}, vcol {[c.name for c in me.color_attributes]}")
    print("SCAN inspect done")


# ================================================================================================ build
def joined(fbx, pick=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    obs = [o for o in import_fbx(FAB + "/" + fbx) if o.type == "MESH"]
    if pick:
        obs = [o for o in obs if pick(o)][:1]
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")      # some packs hang everything under a scaled empty
    if len(obs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return ob


def trim_below(ob, z):
    """Cut away everything under a height (the scanned ground round a rock), then keep only the biggest piece."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    gone = [f for f in bm.faces if max(v.co.z for v in f.verts) < z]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    seen, best = set(), []
    for f0 in bm.faces:
        if f0 in seen:
            continue
        stack, isl = [f0], []
        seen.add(f0)
        while stack:
            f = stack.pop()
            isl.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g not in seen:
                        seen.add(g)
                        stack.append(g)
        if len(isl) > len(best):
            best = isl
    keep = set(best)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f not in keep], context="FACES")
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def decimate(ob, tris):
    n = sum(len(pl.vertices) - 2 for pl in ob.data.polygons)
    if n <= tris:
        return n
    md = ob.modifiers.new("d", "DECIMATE")
    md.ratio = tris / n
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier="d")
    return sum(len(pl.vertices) - 2 for pl in ob.data.polygons)


def settle(ob, scale=1.0, sink=0.0, yaw=0.0):
    """Real size, pivot at the middle of the footprint, standing on z = 0 (sunk a little so no edge shows)."""
    import numpy as np
    me = ob.data
    co = np.empty(len(me.vertices) * 3, dtype=np.float32)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3) * scale
    if yaw:
        c, s_ = math.cos(yaw), math.sin(yaw)
        x, y = co[:, 0].copy(), co[:, 1].copy()
        co[:, 0], co[:, 1] = x * c - y * s_, x * s_ + y * c
    co[:, 0] -= (co[:, 0].min() + co[:, 0].max()) / 2
    co[:, 1] -= (co[:, 1].min() + co[:, 1].max()) / 2
    co[:, 2] -= co[:, 2].min() + sink
    me.vertices.foreach_set("co", co.reshape(-1))
    me.update()
    for pl in me.polygons:
        pl.use_smooth = True
    return (float(co[:, 0].max() - co[:, 0].min()), float(co[:, 1].max() - co[:, 1].min()), float(co[:, 2].max()))


def one_slot(ob, keep_uv=None):
    me = ob.data
    if keep_uv:
        for uv in list(me.uv_layers):
            if uv.name != keep_uv and len(me.uv_layers) > 1:
                me.uv_layers.remove(uv)
    me.materials.clear()
    me.materials.append(bpy.data.materials.new("Scan"))
    me.polygons.foreach_set("material_index", [0] * len(me.polygons))


def export(ob, name):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    ob.name = ob.data.name = "SM_Scan_" + name
    bpy.ops.export_scene.fbx(filepath=f"{OUT}/SM_Scan_{name}.fbx", use_selection=True, object_types={"MESH"}, mesh_smooth_type="FACE",
                             add_leaf_bones=False, bake_anim=False, apply_scale_options="FBX_SCALE_NONE")


def texture(src, dst, size=4096, quality=2):
    """Copy a scan texture into the project, at most `size` on a side (ffmpeg)."""
    import subprocess
    vf = f"scale='min({size},iw)':'min({size},ih)':flags=lanczos"
    cmd = ["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-vf", vf]
    cmd += ["-q:v", str(quality)] if dst.lower().endswith((".jpg", ".jpeg")) else []
    subprocess.run(cmd + [dst], check=True)


def b_wheelbarrow():
    s = SCANS["Wheelbarrow"]
    ob = joined(s["fbx"])
    dims = settle(ob, yaw=math.radians(90.0))           # the scan runs along Y, wheel at -Y: turn it to run along X, wheel at +X
    one_slot(ob)
    export(ob, "Wheelbarrow")
    pre = os.path.dirname(FAB + "/" + s["fbx"]) + "/Urban_Australian_Desolation_Wheelbarrow_Metal_Rusty_yjvbcgl_High_4K_"
    texture(pre + "BaseColor.jpg", OUT + "/T_Scan_Wheelbarrow_C.jpg")
    texture(pre + "Normal.jpg", OUT + "/T_Scan_Wheelbarrow_N.jpg", quality=1)
    import subprocess                                   # R = occlusion, G = roughness, B = metal, as the baked items have it
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", pre + "AO.jpg", "-i", pre + "Roughness.jpg", "-i", pre + "Metalness.jpg", "-filter_complex",
                    "[0:v]format=gray[a];[1:v]format=gray[r];[2:v]format=gray,scale=4096:4096[m];[a][r][m]mergeplanes=0x001020:gbrp[o];[o]shuffleplanes=1:2:0,format=rgb24",
                    "-q:v", "2", OUT + "/T_Scan_Wheelbarrow_ORM.jpg"], check=True)
    return dims, len(ob.data.polygons)


def b_mossyrock():
    ob = joined(SCANS["MossyRock"]["fbx"])
    lo, hi = world_bounds([ob])
    trim_below(ob, lo.z + 0.36)                         # the square of leaf litter it was scanned on
    dims = settle(ob, sink=0.035)
    one_slot(ob)
    export(ob, "MossyRock")
    t = FAB + "/mossy-rock/x/textures/"
    texture(t + "moss_rock_basecolor.png", OUT + "/T_Scan_MossyRock_C.jpg")
    texture(t + "mossy_rock_normal.png", OUT + "/T_Scan_MossyRock_N.jpg", quality=1)
    return dims, len(ob.data.polygons)


def b_pineboulder():
    ob = joined(SCANS["PineBoulder"]["fbx"])
    lo, hi = world_bounds([ob])
    trim_below(ob, lo.z + 1.0)
    n = decimate(ob, 110000)
    dims = settle(ob, scale=0.18, sink=0.03)             # the scan has no real scale: about two and a half metres across
    one_slot(ob)
    export(ob, "PineBoulder")
    texture(FAB + "/forest_pine_boulder/x/textures/pine-stone.jpeg", OUT + "/T_Scan_PineBoulder_C.jpg")
    return dims, n


def b_lidar():
    out = []
    for k in ("1", "2", "3"):
        ob = joined(SCANS["LidarRocks"]["fbx"], pick=lambda o, k=k: o.name.endswith(k))
        n = decimate(ob, 160000)
        dims = settle(ob, sink=0.10)
        one_slot(ob)
        export(ob, "Ledge" + k)
        texture(FAB + f"/mossy-rocks-from-forest-lidar-scan/x/textures/textured_output{k}.jpg", OUT + f"/T_Scan_Ledge{k}_C.jpg")
        out.append((dims, n))
    return out


def b_grass():
    out = []
    for nm, mat, img in (("GrassClump", "1300954650", "1300954650.png"), ("GrassSeed", "2785131480", "2785131480.png")):
        def pick(o, mat=mat):
            return o.data.materials and o.data.materials[0].name == mat and abs(o.scale.x - (1.0 if mat == "1300954650" else 0.813)) < 0.01
        ob = joined(SCANS["GrassMix"]["fbx"], pick=pick)
        uvs = [u.name for u in ob.data.uv_layers]
        dims = settle(ob)
        one_slot(ob, keep_uv=[u for u in uvs if u != "LightMapUV"][0] if len(uvs) > 1 else None)
        export(ob, nm)
        import shutil
        shutil.copyfile(FAB + "/grass-vegitation-mix/x/textures/" + img, OUT + f"/T_Scan_{nm}_C.png")
        out.append((dims, len(ob.data.polygons), uvs))
    return out


if MODE == "build":
    for name, fn in (("Wheelbarrow", b_wheelbarrow), ("MossyRock", b_mossyrock), ("PineBoulder", b_pineboulder), ("LidarRocks", b_lidar), ("GrassMix", b_grass)):
        if ONLY and name not in ONLY:
            continue
        print(f"SCAN built {name}: {fn()}")
    print("SCAN build done")

