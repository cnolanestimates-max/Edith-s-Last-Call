"""Blender: the tiling textures for the gravel road round the house (Cheyenne, 2026-11-21: "it's got no detail whatsoever
and needs hella detail").

A 1.2 m square of real gravel, rendered straight down: about seven thousand loose stones (forty shapes, 3 to 35 mm, sunk
into packed dirt at random depths, a few big ones), wrapped across the edges so the square tiles with no seam.  Renders:
  T_RoadGravel_C.png    base colour (Cycles diffuse colour pass, darkened in the crevices by an occlusion pass)
  T_RoadGravel_N.png    tangent-space normal from the height (Z pass), +Y up
  T_RoadGravel_R.png    roughness (stones a little smoother than the dirt between them)
  T_RoadGravel_H.png    height, 0 at the dirt, 1 at the top of the tallest stone
blender -b --factory-startup -P road_textures.py -- <out_dir> [--size 2048]"""
import bpy, bmesh, math, os, random, sys
import numpy as np
from mathutils import Vector, noise

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
SIZE = int(argv[argv.index("--size") + 1]) if "--size" in argv else 2048
os.makedirs(OUT, exist_ok=True)
T = 1.2                                                     # the tile, in metres
random.seed(1993)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(name, col, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 4.0
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (col[0] * 0.7, col[1] * 0.7, col[2] * 0.7, 1)
    ramp.color_ramp.elements[1].color = (col[0] * 1.25, col[1] * 1.25, col[2] * 1.25, 1)
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    return m


# stone colours of a county road: limestone, grey granite, brown river gravel, a little dark shale, rust-stained chert
STONE_COLS = [(0.30, 0.29, 0.27), (0.22, 0.21, 0.20), (0.26, 0.22, 0.17), (0.14, 0.13, 0.12), (0.33, 0.30, 0.25), (0.24, 0.17, 0.11), (0.18, 0.18, 0.18)]
stone_mats = [mat(f"S{i}", c, 0.62) for i, c in enumerate(STONE_COLS)]

# the dirt between them: a lumpy, rutted ground plane
bpy.ops.mesh.primitive_grid_add(x_subdivisions=240, y_subdivisions=240, size=T * 1.5)
ground = bpy.context.object
for v in ground.data.vertices:
    p = v.co
    # periodic noise on the tile, so the dirt tiles too
    a, b = 2 * math.pi * p.x / T, 2 * math.pi * p.y / T
    q1 = Vector((math.cos(a), math.sin(a), 0.37)); q2 = Vector((0.71, math.cos(b), math.sin(b)))
    v.co.z = 0.0025 * (noise.noise(q1 * 2.0 + q2 * 2.0)) + 0.0012 * noise.noise(q1 * 7.0 + q2 * 7.0)
dirt = bpy.data.materials.new("Dirt")
dirt.use_nodes = True
db = dirt.node_tree.nodes["Principled BSDF"]
db.inputs["Base Color"].default_value = (0.075, 0.06, 0.045, 1)
db.inputs["Roughness"].default_value = 0.92
ground.data.materials.append(dirt)

# forty stone shapes: crushed rock is angular, river stones round
shapes = []
for i in range(40):
    round_ = i % 3 == 0
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2 if round_ else 1, radius=1.0)
    ob = bpy.context.object
    sx, sy, sz = random.uniform(0.7, 1.3), random.uniform(0.6, 1.2), random.uniform(0.35, 0.75)
    for v in ob.data.vertices:
        d = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
        d *= 1.0 + (0.12 if round_ else 0.28) * noise.noise(v.co * 2.3 + Vector((i, i * 2, i * 3)))
        v.co = d
    if not round_:
        for f in ob.data.polygons:
            f.use_smooth = False
    else:
        for f in ob.data.polygons:
            f.use_smooth = True
    ob.data.materials.append(stone_mats[i % len(stone_mats)])
    ob.hide_render = True
    ob.location = (100 + i * 3, 0, 0)
    shapes.append(ob)

col = bpy.data.collections.new("Stones")
sc.collection.children.link(col)
count = 0


def put(shape, x, y, r, sink, rot):
    global count
    for dx in (-T, 0, T):
        for dy in (-T, 0, T):
            px, py = x + dx, y + dy
            if abs(px) > T / 2 + r or abs(py) > T / 2 + r:
                continue
            o = bpy.data.objects.new("s", shape.data)
            o.location = (px, py, r * (shape.dimensions.z / 2.0) * (1.0 - sink))
            o.rotation_euler = rot
            o.scale = (r, r, r)
            col.objects.link(o)
            count += 1


# a dense bed of small chips, a layer of mid-size gravel over it, and a scatter of big stones
for n, (rmin, rmax), (s0, s1) in ((16000, (0.0024, 0.0055), (0.15, 0.6)), (5200, (0.0055, 0.011), (0.2, 0.55)), (260, (0.011, 0.021), (0.25, 0.5))):
    for i in range(n):
        x, y = random.uniform(-T / 2, T / 2), random.uniform(-T / 2, T / 2)
        # where the dirt shows through: fewer stones in patches (periodic, so it tiles)
        a, b = 2 * math.pi * x / T, 2 * math.pi * y / T
        q = Vector((math.cos(a), math.sin(a), math.cos(b))) + Vector((0, 0, math.sin(b)))
        if noise.noise(q * 1.7) > 0.32 and random.random() < 0.55:
            continue
        put(random.choice(shapes), x, y, random.uniform(rmin, rmax), random.uniform(s0, s1),
            (random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4), random.uniform(0, 2 * math.pi)))
print("ROAD stones", count)

# camera straight down, orthographic, exactly the tile
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.type = "ORTHO"
cam.data.ortho_scale = T
cam.location = (0, 0, 1.0)
cam.data.clip_start = 0.5
cam.data.clip_end = 2.0
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 16
sc.render.resolution_x = sc.render.resolution_y = SIZE
sc.render.film_transparent = False
sc.world = bpy.data.worlds.new("w")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "None"
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_depth = "16"
sc.render.image_settings.color_mode = "RGB"
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
sc.world.light_settings.distance = 0.02


def emit_all(kind):
    """Point every material's output at one signal, as pure emission: 'col' base colour, 'z' height, 'ao' occlusion."""
    for m in bpy.data.materials:
        nt = m.node_tree
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        em = nt.nodes.get("WCEmit") or nt.nodes.new("ShaderNodeEmission")
        em.name = "WCEmit"
        for l in list(em.inputs["Color"].links):
            nt.links.remove(l)
        if kind == "col":
            src = bsdf.inputs["Base Color"]
            if src.is_linked:
                nt.links.new(src.links[0].from_socket, em.inputs["Color"])
            else:
                em.inputs["Color"].default_value = src.default_value
        elif kind == "z":
            geo = nt.nodes.get("WCGeo") or nt.nodes.new("ShaderNodeNewGeometry")
            geo.name = "WCGeo"
            sep = nt.nodes.get("WCSep") or nt.nodes.new("ShaderNodeSeparateXYZ")
            sep.name = "WCSep"
            mr = nt.nodes.get("WCMap") or nt.nodes.new("ShaderNodeMapRange")
            mr.name = "WCMap"
            mr.inputs["From Min"].default_value = -0.006
            mr.inputs["From Max"].default_value = 0.030
            nt.links.new(geo.outputs["Position"], sep.inputs[0])
            nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
            nt.links.new(mr.outputs["Result"], em.inputs["Color"])
        else:
            aon = nt.nodes.get("WCAO") or nt.nodes.new("ShaderNodeAmbientOcclusion")
            aon.name = "WCAO"
            aon.inputs["Distance"].default_value = 0.012
            aon.samples = 16
            nt.links.new(aon.outputs["AO"], em.inputs["Color"])
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])


def shoot(kind):
    emit_all(kind)
    sc.render.filepath = f"{OUT}/_{kind}.png"
    bpy.ops.render.render(write_still=True)
    im = bpy.data.images.load(sc.render.filepath, check_existing=False)
    im.colorspace_settings.name = "Non-Color"
    a = np.array(im.pixels[:], dtype=np.float32).reshape(SIZE, SIZE, 4)[:, :, :3]
    return a


sc.cycles.samples = 8
col_ = shoot("col")                                         # linear base colour (Standard view, Non-Color read)
z = shoot("z")[:, :, 0]
sc.cycles.samples = 24
ao = shoot("ao")[:, :, 0]
h = np.clip((z - np.percentile(z, 2)) / max(1e-4, np.percentile(z, 99.8) - np.percentile(z, 2)), 0, 1)
albedo = col_ * (0.55 + 0.45 * np.clip(ao, 0, 1))[:, :, None]
albedo = np.clip(albedo, 0, 1)                               # already display-encoded by the Standard transform
# normal from height (tile-wrapping gradient); the height range is ~20 mm across 1.2 m
px = T / SIZE
hm = h * 0.02
gx = (np.roll(hm, -1, 1) - np.roll(hm, 1, 1)) / (2 * px)
gy = (np.roll(hm, -1, 0) - np.roll(hm, 1, 0)) / (2 * px)
nz = 1.0 / np.sqrt(gx * gx + gy * gy + 1.0)
nrm = np.stack([-gx * nz, gy * nz, nz], -1) * 0.5 + 0.5        # image rows run top to bottom: +Y up
rough = np.clip(0.93 - 0.30 * h - 0.05 * (1 - ao), 0.45, 0.97)


def save(name, arr):
    im = bpy.data.images.new(name, SIZE, SIZE, alpha=False, float_buffer=False)
    if arr.ndim == 2:
        arr = np.stack([arr, arr, arr], -1)
    rgba = np.concatenate([arr, np.ones((SIZE, SIZE, 1), np.float32)], -1)
    im.pixels[:] = rgba.astype(np.float32).ravel()
    im.filepath_raw = f"{OUT}/{name}.png"
    im.file_format = "PNG"
    im.save()


save("T_RoadGravel_C", albedo)
save("T_RoadGravel_N", nrm)
save("T_RoadGravel_R", rough)
save("T_RoadGravel_H", h)
print("ROAD textures written", OUT)
