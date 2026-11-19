"""Fit the approved C portrait to Edith's existing UVs. Run with the SF3D Python and a Blender executable as the sole argument."""
from pathlib import Path
import sys
import tempfile
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
EXPORT = ROOT / "SourceArt/Her/export"
LOOK = ROOT / "SourceArt/Her/look_c"


def export_projection(destination):
    import bpy
    from mathutils import Vector

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(EXPORT / "SK_Her.fbx"))
    actor = max((o for o in bpy.context.scene.objects if o.type == "MESH"), key=lambda o: len(o.data.vertices))
    mesh = actor.data
    mesh.calc_loop_triangles()
    corners = [actor.matrix_world @ Vector(v) for v in actor.bound_box]
    base_z = min(v.z for v in corners)
    unit = (max(v.z for v in corners) - base_z) / 270

    def cm(x, y, z):
        return Vector((x * unit, y * unit, base_z + z * unit))

    # Same camera as the approved rest-face study in her_look.py.
    camera = bpy.data.objects.new("Portrait", bpy.data.cameras.new("Portrait"))
    bpy.context.scene.collection.objects.link(camera)
    camera.location = cm(10, -92, 233)
    camera.rotation_euler = (cm(1.5, -22, 237) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 62
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    matrix = camera.calc_matrix_camera(deps, x=640, y=720) @ camera.matrix_world.inverted() @ actor.matrix_world
    vertices = np.array([v.co[:] for v in mesh.vertices])
    clip = np.column_stack((vertices, np.ones(len(vertices)))) @ np.array(matrix).T
    depth = clip[:, 3]
    norm = clip[:, :2] / np.maximum(depth[:, None], 0.00001)
    screen = np.column_stack(((norm[:, 0] + 1) * 0.5, (1 - norm[:, 1]) * 0.5))
    uvs = np.array([u.uv[:] for u in mesh.uv_layers.active.data])
    uvs[:, 1] = 1 - uvs[:, 1]
    indices = np.array([t.vertices[:] for t in mesh.loop_triangles])
    loops = np.array([t.loops[:] for t in mesh.loop_triangles])
    front = (depth[indices].min(axis=1) > 0) & (screen[indices].min(axis=1) < 1.01).all(axis=1) & (screen[indices].max(axis=1) > -0.01).all(axis=1)
    np.savez(destination, screen=screen[indices[front]], depth=depth[indices[front]], uv=uvs[loops[front]])


def raster(triangles, depths, projected, depth_buffer, coordinates, write_depth):
    """First rasterize the nearest surface in portrait space, then transfer visible texels in atlas space."""
    height, width = depth_buffer.shape if write_depth else coordinates.shape[:2]
    for i in range(len(triangles)):
        xy = triangles[i]
        x0, y0 = xy[0]
        ax, ay = xy[1] - xy[0]
        bx, by = xy[2] - xy[0]
        det = ax * by - ay * bx
        if abs(det) < 1e-10:
            continue
        for y in range(max(0, int(np.ceil(xy[:, 1].min()))), min(height, 1 + int(np.floor(xy[:, 1].max())))):
            for x in range(max(0, int(np.ceil(xy[:, 0].min()))), min(width, 1 + int(np.floor(xy[:, 0].max())))):
                w1 = ((x-x0)*by - (y-y0)*bx) / det
                w2 = (ax*(y-y0) - ay*(x-x0)) / det
                w0 = 1.0-w1-w2
                if min(w0, w1, w2) < -0.00001:
                    continue
                z = depths[i]
                if write_depth:
                    pixel_z = 1.0 / (w0/z[0] + w1/z[1] + w2/z[2])
                    depth_buffer[y,x] = min(depth_buffer[y,x], pixel_z)
                else:
                    pixel_z = w0*z[0] + w1*z[1] + w2*z[2]
                    q = projected[i]
                    sx = (w0*q[0,0]*z[0] + w1*q[1,0]*z[1] + w2*q[2,0]*z[2]) / pixel_z
                    sy = (w0*q[0,1]*z[0] + w1*q[1,1]*z[1] + w2*q[2,1]*z[2]) / pixel_z
                    ix, iy = int(round(sx)), int(round(sy))
                    if 0 <= ix < depth_buffer.shape[1] and 0 <= iy < depth_buffer.shape[0] and abs(pixel_z-depth_buffer[iy,ix]) < 0.0035:
                        coordinates[y,x,0], coordinates[y,x,1] = sx,sy


def fit(data):
    import cv2
    from numba import njit

    portrait = cv2.imread(str(LOOK / "Edith_C_reference.png"))
    h, w = portrait.shape[:2]
    pixels = data["screen"] * np.array([w,h]) - 0.5
    zbuffer = np.full((h,w), np.inf, dtype=np.float32)
    size = 4096
    coords = np.full((size,size,2), -1, dtype=np.float32)
    draw = njit(raster)
    draw(pixels, data["depth"], pixels, zbuffer, coords, True)
    draw(data["uv"]*size-0.5, data["depth"], pixels, zbuffer, coords, False)

    # Masks are in the baseline's 640 x 720 camera frame. Keep the animated eyeball,
    # lip opening and curtain of hair out of the face projection.
    mask = np.zeros((720,640), np.uint8)
    patches = [
        [(308,0),(443,0),(475,65),(488,138),(491,208),(495,274),(485,354),(464,422),(444,466),(405,505),(347,528),(281,529),(274,474),(277,404),(271,349),(254,326),(262,279),(274,244),(282,160),(294,96)],
        [(281,510),(347,520),(403,493),(416,482),(397,549),(394,594),(421,650),(463,686),(446,720),(280,720),(279,604)],
    ]
    for patch in patches:
        cv2.fillPoly(mask,[np.array(patch)],255)
    cv2.fillPoly(mask,[np.array([(337,203),(344,156),(359,130),(384,116),(417,118),(446,132),(468,155),(476,187),(471,211),(458,235),(434,246),(390,243),(357,234),(337,223)])],0)
    cv2.fillPoly(mask,[np.array([(275,411),(299,404),(329,406),(367,414),(371,426),(306,426),(274,426)])],0)
    mask = cv2.resize(cv2.GaussianBlur(mask,(0,0),4.5),(w,h)).astype(np.float32)/255
    weights = cv2.remap(mask,coords,None,cv2.INTER_LINEAR)
    used = weights > 0.01
    if used.sum() < 12000:
        raise RuntimeError(f"Face coverage too small: {used.sum()} texels")
    # Extend the paint around UV-island edges for bilinear filtering and mipmaps.
    dist, labels = cv2.distanceTransformWithLabels((~used).astype('uint8'),cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
    pad = (~used) & (dist < 6)
    neighbor = labels[pad]-1
    coords[pad] = coords[used][neighbor]
    weights[pad] = weights[used][neighbor]
    active = used | pad
    yy,xx = np.nonzero(active)
    sample = coords[yy,xx]
    # Sparse gather avoids allocating full-size floating-point RGB atlases.
    sx = np.clip(np.rint(sample[:,0]).astype(int),0,w-1)
    sy = np.clip(np.rint(sample[:,1]).astype(int),0,h-1)
    alpha = weights[yy,xx,None]
    rgb = portrait.astype(np.float32) / 255
    luminance = cv2.cvtColor(rgb,cv2.COLOR_BGR2GRAY)
    broad = cv2.GaussianBlur(luminance,(0,0),32)
    # Reduce broad studio lighting before the game flashlight relights the paint.
    pigment = np.clip(rgb * (1.26 / np.maximum(broad,0.12)**0.19)[:,:,None],0,1)
    redness = np.clip((rgb[:,:,2] - rgb[:,:,0] - 0.035)*7,0,1)
    detail = (luminance - cv2.GaussianBlur(luminance,(0,0),3))
    rough = np.clip(0.65 - 0.30*redness + 1.25*detail,0.23,0.80)
    relief = np.zeros((size,size),np.float32)
    relief[yy,xx] = np.clip(detail[sy,sx]*1.6,-0.18,0.18)
    dy,dx = np.gradient(relief)
    for channel in ("BaseColor","Roughness","Normal"):
        filename = f"T_Her_{channel}.png"
        original = cv2.imread(str(EXPORT / filename),cv2.IMREAD_COLOR)
        atlas = cv2.resize(original,(size,size),interpolation=cv2.INTER_CUBIC)
        base = atlas[yy,xx].astype(np.float32)/255
        if channel == "BaseColor":
            changed = pigment[sy,sx]
        elif channel == "Roughness":
            changed = rough[sy,sx,None]
        else:
            normal = base*2-1
            normal[:,2] -= np.clip(dx[yy,xx]*2.3,-0.38,0.38)
            normal[:,1] -= np.clip(dy[yy,xx]*2.3,-0.38,0.38)
            normal /= np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),0.001)
            changed = normal*0.5+0.5
        atlas[yy,xx] = np.clip(255*(base*(1-alpha)+changed*alpha),0,255).astype('uint8')
        if not cv2.imwrite(str(LOOK / filename),atlas):
            raise OSError(filename)
    print(f"C face fitted over {used.sum():,} visible atlas texels")


if __name__ == "__main__":
    if "--" in sys.argv:
        export_projection(sys.argv[-1])
    else:
        with tempfile.TemporaryDirectory() as scratch:
            geometry = str(Path(scratch)/"projection.npz")
            subprocess.run([sys.argv[1],"-b","--factory-startup","--python-exit-code","1","-P",__file__,"--",geometry],check=True)
            with np.load(geometry) as geometry_data:
                fit(geometry_data)
