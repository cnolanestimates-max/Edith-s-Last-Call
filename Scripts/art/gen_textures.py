"""Decay texture library for the house: generate flat material photos with Higgsfield, make them tile, derive
normal / ORM maps, and write SourceArt/Textures/<Name>/{BaseColor,Normal,ORM}.png + surfaces.json for import_assets.py.
Also makes grime decals (SourceArt/Decals/<name>.png with alpha).

  python gen_textures.py --list      what is missing (and the credit cost)
  python gen_textures.py             generate missing (no automatic retries), then process everything
  python gen_textures.py --process   only process

Run with the SF3D venv python (needs numpy, scipy, PIL).
"""
import json, os, subprocess, sys, urllib.request

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = "C:/GameDev/Unreal/WellnessCheck"
RAW = ROOT + "/SourceArt/Textures/_raw"
OUT = ROOT + "/SourceArt/Textures"
DEC = ROOT + "/SourceArt/Decals"
HF = "C:/Users/cheye/.local/share/unreal-agent-tools/node-v26.13.1-win-x64/higgsfield.cmd"
MODEL = "seedream_5_0_flash"
COST = 0.5
HEAD = "Seamless tileable PBR texture scan, perfectly flat straight-on orthographic view, even diffuse lighting, no shadows, no perspective, no objects, fills the whole frame edge to edge: "
OLD = " Two hundred years of neglect in an abandoned settler-era farmhouse: filthy, rotten, decayed, disgusting."

# name: (prompt, tile_cm, grime, rough_scale, bump, size)
TEX = {
    "WallpaperGreen": ("ancient faded green floral wallpaper, peeling and torn in strips showing rotten lath and crumbling plaster underneath, brown water stains running down, black mold blooms, nicotine yellowing." + OLD, 260, 0.55, 1.0, 1.4, 2048),
    "WallpaperRed": ("ancient faded dark red damask wallpaper, peeling and torn in strips showing crumbling plaster underneath, brown water stains running down, black and green mold, grime." + OLD, 260, 0.55, 1.0, 1.4, 2048),
    "WallpaperPurple": ("ancient faded mauve striped wallpaper, bubbling and peeling away from the wall, torn strips, brown damp stains, black mold spots, cobweb dust." + OLD, 260, 0.55, 1.0, 1.4, 2048),
    "WallpaperGrey": ("old bare lime plaster wall, cracked and crumbling with patches fallen away showing wooden lath, brown water stains, grey and black mold, smeared filth." + OLD, 280, 0.6, 1.0, 1.6, 2048),
    "PlasterCeiling": ("old ceiling plaster, sagging and cracked, large brown water rings and stains, black mold colonies, flaking paint, cobweb dust." + OLD, 300, 0.55, 1.0, 1.3, 2048),
    "FloorBoards": ("very old wide pine floorboards running vertically, warped, rotten, splintered, dark gaps between boards, caked dirt, mouse droppings, dark stains, dust." + OLD, 240, 0.5, 1.0, 2.0, 2048),
    "AtticBoards": ("rough sawn unpainted attic floorboards, grey with thick dust, rotten patches, old nail heads, gaps, dirt." + OLD, 240, 0.5, 1.0, 2.0, 1024),
    "WoodTrim": ("old dark brown painted wood panelling, paint cracked and flaking off, greasy grime, scratches, water damage." + OLD, 160, 0.5, 0.9, 1.2, 1024),
    "WoodDark": ("old dark walnut furniture wood, finish worn away and flaking, scratched, water rings, dirt in the grain, woodworm holes." + OLD, 110, 0.45, 0.85, 1.0, 1024),
    "WoodRotten": ("rotten wet black wood, soft and crumbling, fungus, splitting grain." + OLD, 120, 0.4, 1.0, 1.8, 1024),
    "WoodBleached": ("weathered grey sun-bleached old boards, cracked, splintered, grey lichen, dirt." + OLD, 140, 0.4, 1.0, 1.6, 1024),
    "WoodPainted": ("old boards with thick white paint peeling off in curls and flakes, grey wood beneath, dirt and mildew." + OLD, 140, 0.45, 1.0, 1.5, 1024),
    "PorchBoards": ("old exterior porch floorboards running vertically, grey and weathered, peeling grey paint, rot, gaps, dead leaves fragments, dirt.", 220, 0.4, 1.0, 1.8, 1024),
    "Siding": ("old horizontal wooden clapboard siding, white paint almost entirely peeled away, grey rotting wood, dark streaks, mildew, cracked boards.", 300, 0.5, 1.0, 2.2, 2048),
    "RoofShingle": ("old wooden roof shingles in rows, rotten, mossy, curled, some missing, black streaks.", 300, 0.4, 1.0, 2.0, 1024),
    "CellarStone": ("old rough fieldstone cellar wall with crumbling lime mortar, damp, dark, white salt deposits, green and black mold, dirt.", 260, 0.45, 1.0, 2.6, 2048),
    "CellarFloor": ("damp packed dirt cellar floor, dark mud, small stones, puddle stains, mold, debris.", 260, 0.4, 0.95, 1.4, 1024),
    "Brick": ("old crumbling soot-blackened red brick wall with eroded mortar, damp stains, white efflorescence.", 240, 0.45, 1.0, 2.2, 1024),
    "YardGround": ("dead matted brown grass and dark mud, patchy, wet, small twigs and dead leaves, night ground.", 500, 0.3, 1.0, 1.4, 2048),
    "Gravel": ("old dirty grey gravel driveway with mud and weeds, small stones.", 320, 0.3, 1.0, 1.8, 1024),
    "Rust": ("heavily rusted flaking iron sheet, orange and dark brown rust, pitting, scale.", 100, 0.3, 1.0, 1.4, 1024),
    "Iron": ("old black cast iron, pitted, rust blooming through, greasy dirt.", 90, 0.3, 0.8, 1.0, 1024),
    "Brass": ("old tarnished brass, brown and green verdigris tarnish, scratches, dull.", 60, 0.3, 0.6, 0.6, 512),
    "FabricRed": ("old dark red velvet upholstery fabric, threadbare, faded, torn patches showing stuffing, stains, mold spots, thick dust." + OLD, 110, 0.5, 1.0, 1.0, 1024),
    "FabricDark": ("old dark brown-black woollen upholstery fabric, moth-eaten holes, threadbare, stains, mildew, thick dust." + OLD, 110, 0.5, 1.0, 1.0, 1024),
    "Sheet": ("old yellowed cotton bed sheet fabric, brown stains, mildew spots, dust, small holes, grime." + OLD, 130, 0.5, 1.0, 0.7, 1024),
    "Mattress": ("disgusting old striped mattress ticking, large brown and yellow stains, mold, tears showing horsehair, filth." + OLD, 130, 0.5, 1.0, 0.9, 1024),
    "Leather": ("old cracked dry dark brown leather, peeling, split, mouldy, dusty.", 80, 0.4, 0.85, 1.0, 1024),
    "Porcelain": ("old white enamel bathroom surface, crazed and chipped, brown rust streaks, black mold in cracks, yellow stains, filth." + OLD, 120, 0.55, 0.7, 0.8, 1024),
    "PaperOld": ("old yellowed brittle paper, foxing spots, water stains, creases, torn edges, faint faded handwriting impossible to read.", 60, 0.35, 1.0, 0.5, 1024),
    "Cardboard": ("old damp brown cardboard, water stained, mouldy, torn, sagging.", 90, 0.4, 1.0, 0.8, 512),
    "Bark": ("dead tree bark, grey-black, deeply cracked, peeling, dry.", 140, 0.2, 1.0, 2.4, 1024),
    "Soot": ("thick black soot and char on a surface, matte, flaky.", 100, 0.2, 1.0, 1.0, 512),
    "RoofTin": ("old corrugated tin roofing sheets with vertical ridges, heavily rusted orange-brown with patches of grey galvanised metal, streaks, holes, rust stains.", 300, 0.4, 0.85, 1.8, 1024),
    "Grime": ("abstract grunge dirt mask: dark brown filth, drips, smears and mold blotches on a pale off-white surface, high contrast, organic stains running downward.", 400, 0.0, 1.0, 1.0, 1024),
}
DHEAD = "A single isolated stain photographed flat and straight-on, centred, on a pure white background, with soft irregular edges that fade into the white, nothing else in the image: "
DECALS = {
    "mold_01": "a large black and dark green mold colony, blotchy, speckled",
    "mold_02": "spreading black mold spots and fuzzy grey mildew patches",
    "water_01": "a brown water stain with dark tide-line edges and long drips running straight down",
    "water_02": "a wide yellow-brown damp stain with several concentric rings",
    "filth_01": "a smeared dark brown filthy hand-smear stain, streaky, disgusting",
    "filth_02": "a dark brown splattered and dripping filth stain running downward",
    "rust_01": "long orange-brown rust streaks running straight down from a point",
    "dirt_01": "a scattered patch of dark dirt, dust, dead leaves fragments and small debris seen from above",
    "dirt_02": "a dark greasy trodden-in dirt patch with scuff marks seen from above",
    "crack_01": "a branching black crack in plaster with small missing chips",
    "blood_old": "an old dried dark brown-black blood stain, soaked in, cracked at the edges",
    "puddle_01": "an irregular puddle of dark dirty water seen from directly above, pure black shape",
    "puddle_02": "a long irregular spill of dark liquid with small satellite drops seen from directly above, pure black shape",
    "filth_03": "a wide dark brown smeared and dripping filth stain as if wiped by hands, with fingermark streaks",
    "mold_03": "a very large spreading patch of black, grey and dark green mold with fuzzy speckled edges",
    "scratches": "deep parallel fingernail scratch marks gouged into a pale surface, dark grooves",
}


def gen(prompt, dst, aspect="1:1"):
    r = subprocess.run(["cmd", "/c", HF, "generate", "create", MODEL, "--prompt", prompt, "--aspect_ratio", aspect, "--wait", "--json"],
                       capture_output=True, text=True, timeout=600)
    out = r.stdout.strip()
    try:
        j = json.loads(out)
        url = j[0]["result_url"]
    except Exception:
        raise RuntimeError((out or r.stderr)[:200])
    urllib.request.urlretrieve(url, dst)
    return j[0]["id"]


def make_tile(a, border=0.16):
    """Make an image wrap: blend each edge band with the opposite edge (after a half-offset the seams sit in the middle)."""
    h, w = a.shape[:2]
    out = a.astype(np.float32).copy()
    bw, bh = int(w * border), int(h * border)
    ramp = np.linspace(0, 1, bw, dtype=np.float32)
    ramp = ramp * ramp * (3 - 2 * ramp)
    left = out[:, :bw].copy(); right = out[:, w - bw:].copy()
    # the right band fades into what lies just left of the left edge once wrapped, i.e. the left band mirrored in time
    out[:, w - bw:] = right * (1 - ramp)[None, :, None] + left[:, ::-1] * ramp[None, :, None] * 0 + (left * 0)
    out[:, w - bw:] = right * (1 - ramp)[None, :, None] + np.roll(a.astype(np.float32), bw, axis=1)[:, w - bw:] * 0 + left[:, :bw][:, ::1] * 0 + right * 0
    # simple, robust variant: cross-dissolve a wrapped copy
    sh = np.roll(np.roll(a.astype(np.float32), w // 2, axis=1), h // 2, axis=0)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = np.minimum(xx, w - 1 - xx) / (w * border)
    dy = np.minimum(yy, h - 1 - yy) / (h * border)
    m = np.clip(np.minimum(dx, dy), 0, 1)
    m = (m * m * (3 - 2 * m))[..., None]
    return np.clip(a.astype(np.float32) * m + sh * (1 - m), 0, 255).astype(np.uint8)


def maps(name, spec):
    prompt, tile, grime, rough, bump, size = spec
    src = Image.open(f"{RAW}/{name}.png").convert("RGB")
    s = min(src.size)
    src = src.crop(((src.width - s) // 2, (src.height - s) // 2, (src.width + s) // 2, (src.height + s) // 2)).resize((size, size), Image.LANCZOS)
    a = make_tile(np.asarray(src))
    d = f"{OUT}/{name}"
    os.makedirs(d, exist_ok=True)
    # darken and desaturate a little: generated scans come out too bright and clean for this house
    f = a.astype(np.float32) / 255.0
    lum = f @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    f = f * 0.86 + lum[..., None] * 0.14
    f = np.clip(f ** 1.12, 0, 1)
    Image.fromarray((f * 255).astype(np.uint8)).save(d + "/BaseColor.png")
    # height from luminance (dark = low: gaps, cracks, stains read as recessed)
    hgt = ndimage.gaussian_filter(lum, 0.8, mode="wrap")
    fine = hgt - ndimage.gaussian_filter(hgt, 6, mode="wrap")
    broad = ndimage.gaussian_filter(hgt, 3, mode="wrap") - ndimage.gaussian_filter(hgt, 28, mode="wrap")
    hh = fine * 1.0 + broad * 0.7
    gx = ndimage.sobel(hh, axis=1, mode="wrap")
    gy = ndimage.sobel(hh, axis=0, mode="wrap")
    k = bump * 2.2 * (size / 1024.0)
    n = np.dstack([-gx * k, gy * k, np.ones_like(hh)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save(d + "/Normal.png")
    cav = np.clip((ndimage.gaussian_filter(hgt, 10, mode="wrap") - hgt) * 6.0, 0, 1)
    ao = np.clip(1.0 - cav * 0.75, 0.3, 1.0)
    r = np.clip(0.92 - (lum - lum.mean()) * 0.7, 0.35, 1.0)
    Image.fromarray((np.dstack([ao, r, np.zeros_like(r)]) * 255).astype(np.uint8)).save(d + "/ORM.png")
    return {"tile": tile, "grime": grime, "rough": rough}


def decal(name):
    src = Image.open(f"{DEC}/_raw/{name}.png").convert("RGB").resize((1024, 1024), Image.LANCZOS)
    f = np.asarray(src).astype(np.float32) / 255.0
    lum = f @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    sat = f.max(axis=2) - f.min(axis=2)
    alpha = np.clip((1.0 - lum) * 1.5 + sat * 1.2 - 0.12, 0, 1)
    yy, xx = np.mgrid[0:1024, 0:1024].astype(np.float32)
    r = np.sqrt(((xx - 511.5) / 512) ** 2 + ((yy - 511.5) / 512) ** 2)
    alpha *= np.clip((1.0 - r) / 0.18, 0, 1)                      # never touch the border
    alpha = ndimage.gaussian_filter(alpha, 1.2)
    rgb = np.clip(f * 0.9, 0, 1)
    out = np.dstack([rgb, alpha])
    Image.fromarray((out * 255).astype(np.uint8), "RGBA").save(f"{DEC}/{name}.png")


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(DEC + "/_raw", exist_ok=True)
    todo_t = [n for n in TEX if not os.path.exists(f"{RAW}/{n}.png")]
    todo_d = [n for n in DECALS if not os.path.exists(f"{DEC}/_raw/{n}.png")]
    print(f"textures missing {len(todo_t)}, decals missing {len(todo_d)}: {(len(todo_t) + len(todo_d)) * COST:.1f} credits")
    if "--list" in sys.argv:
        return
    failed = []
    if "--process" not in sys.argv:
        for i, n in enumerate(todo_t):
            try:
                gen(HEAD + TEX[n][0], f"{RAW}/{n}.png"); print(f"  tex [{i + 1}/{len(todo_t)}] {n}", flush=True)
            except Exception as exc:
                failed.append(n); print(f"  tex {n} FAILED (not retried): {exc}", flush=True)
        for i, n in enumerate(todo_d):
            try:
                gen(DHEAD + DECALS[n] + ".", f"{DEC}/_raw/{n}.png"); print(f"  decal [{i + 1}/{len(todo_d)}] {n}", flush=True)
            except Exception as exc:
                failed.append(n); print(f"  decal {n} FAILED (not retried): {exc}", flush=True)
    spec = {}
    for n in TEX:
        if os.path.exists(f"{RAW}/{n}.png"):
            spec[n] = maps(n, TEX[n])
    json.dump(spec, open(OUT + "/surfaces.json", "w"), indent=1)
    for n in DECALS:
        if os.path.exists(f"{DEC}/_raw/{n}.png"):
            decal(n)
    print(f"processed {len(spec)} surfaces; failed: {failed}")


main()
