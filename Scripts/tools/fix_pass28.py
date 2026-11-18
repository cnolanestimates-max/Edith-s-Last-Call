"""Her scream (Cheyenne: 'I want her mouth to be like hella big, like elongated mouth scream').
Blender side: a 'Scream' shape key that drops the whole jaw 11 cm from the lip line and hollows the gap, and the lip
line painted black in the texture so the stretched gap is a black hole.  Unreal side: import the morph target."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
P = "C:/GameDev/Unreal/WellnessCheck/Scripts/her/build_her.py"
s = io.open(P, encoding="utf-8").read()
marker = "# ------------------------------------------------------------------ textures\n"
assert marker in s and "SCREAM" not in s
block = r'''# ------------------------------------------------------------------ SCREAM: an unhinged, elongated open mouth
# Measured on the model (mouth_probe.py): lip line z = 234.0, mouth centre x = 0.3, about 8.5 cm wide, lips at y = -26.8.
LIP_Z, MOUTH_X, MOUTH_HALF, JAW_DROP = 234.0, 0.3, 4.4, 11.5
me_ = mesh.data
if not me_.shape_keys:
    mesh.shape_key_add(name="Basis", from_mix=False)
sk_scream = mesh.shape_key_add(name="Scream", from_mix=False)
inv_ = mesh.matrix_world.inverted()
n_jaw = n_gap = 0


def sstep(a, b, v):
    t = min(1.0, max(0.0, (v - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


gap_verts = set()
for i, p in enumerate(co):
    x, y, z = float(p[0]), float(p[1]), float(p[2])
    if z > LIP_Z + 0.9 or z < LIP_Z - 26.0 or y > -9.0:
        continue
    dx = abs(x - MOUTH_X)
    side = 1.0 - sstep(MOUTH_HALF * 0.75, MOUTH_HALF * 2.1, dx)          # the corners of the mouth are pinned
    depth = 1.0 - sstep(-17.0, -10.5, y)                                 # only the front of the face, not the neck
    below = sstep(0.0, 1.3, LIP_Z - z)                                   # everything under the lip line goes with the jaw
    low = 1.0 - sstep(15.0, 26.0, LIP_Z - z)                             # fades out down the throat
    w_ = side * depth * below * low
    dz_ = -JAW_DROP * w_
    dy_ = 0.0
    dxs = 0.0
    if dx < MOUTH_HALF and abs(z - LIP_Z) < 0.75 and y < -21.0:
        # the lip line itself becomes the inside of the mouth: stretched, and pushed back into the head
        k = 1.0 - sstep(MOUTH_HALF * 0.55, MOUTH_HALF, dx)
        dy_ = 4.2 * k
        dz_ = -JAW_DROP * 0.5 * k
        gap_verts.add(i)
        n_gap += 1
    elif w_ > 0.02:
        # the open jaw narrows a little toward the chin: a long O, not a square
        dxs = -(x - MOUTH_X) * 0.10 * w_
        n_jaw += 1
    if dz_ or dy_:
        v_ = sk_scream.data[i]
        wp_ = Vector((x + dxs, y + dy_, z + dz_))
        v_.co = inv_ @ wp_
print("HER scream: jaw verts", n_jaw, "gap verts", n_gap)
# black inside: paint every face on the lip line black in the base colour (it is a hair-thin line until she screams)
_bsdf = next(n for n in me_.materials[0].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
_node = _bsdf.inputs["Base Color"].links[0].from_node
while _node.type != "TEX_IMAGE":
    _node = next(i.links[0].from_node for i in _node.inputs if i.is_linked)
_img = _node.image
_W, _H = _img.size
_px = np.array(_img.pixels[:], dtype=np.float32).reshape(_H, _W, 4)
_uv = me_.uv_layers.active.data
n_tri = 0
for poly in me_.polygons:
    if sum(1 for vi in poly.vertices if vi in gap_verts) < 2:
        continue
    uvs = [(_uv[li].uv.x % 1.0 * _W, _uv[li].uv.y % 1.0 * _H) for li in poly.loop_indices]
    for t in range(1, len(uvs) - 1):
        (x0, y0), (x1, y1), (x2, y2) = uvs[0], uvs[t], uvs[t + 1]
        xa, xb = int(max(0, min(x0, x1, x2) - 1)), int(min(_W - 1, max(x0, x1, x2) + 1))
        ya, yb = int(max(0, min(y0, y1, y2) - 1)), int(min(_H - 1, max(y0, y1, y2) + 1))
        if xb - xa > 200 or yb - ya > 200:
            continue                                    # a face that wraps a UV seam
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9:
            _px[ya:yb + 1, xa:xb + 1, :3] = 0.004
            continue
        ys, xs = np.mgrid[ya:yb + 1, xa:xb + 1]
        a_ = ((y1 - y2) * (xs + 0.5 - x2) + (x2 - x1) * (ys + 0.5 - y2)) / den
        b_ = ((y2 - y0) * (xs + 0.5 - x2) + (x0 - x2) * (ys + 0.5 - y2)) / den
        inside = (a_ >= -0.12) & (b_ >= -0.12) & (a_ + b_ <= 1.12)
        sub = _px[ya:yb + 1, xa:xb + 1, :3]
        sub[inside] = 0.004
        n_tri += 1
_img.pixels[:] = _px.ravel()
_img.update()
print("HER scream: painted", n_tri, "lip-line triangles black")
info["mouth"] = [MOUTH_X, -26.8, LIP_Z]

'''
s = s.replace(marker, block + marker, 1)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
compile(s, P, "exec")
# Unreal: bring the morph target in with the mesh
edit("C:/GameDev/Unreal/WellnessCheck/Scripts/level/import_assets.py", [
    ('''        sd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
    else:''', '''sd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
        sd.set_editor_property("import_morph_targets", True)
    else:'''),
])
print("ok")
