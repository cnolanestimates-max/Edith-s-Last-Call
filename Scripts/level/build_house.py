"""Unreal (headless): build /Game/WC/Maps/House, the whole of Wellness Check, from code.  Re-running rebuilds the map.

Coordinates (cm): +X runs from the front door into the house, +Y is to the right as you walk in.
The house is 16 m deep (X 0..1600) and 12 m wide (Y -600..600) on a 4 m grid, to suit the Horror House Kit's
modular walls.  Floors: cellar -350, ground 0, upstairs 350, attic 700.  One stair tower (X 400..800, Y -184..8)
stacks the cellar, main and attic stairs.
"""
import json
import math
import os

import unreal

MAP = "/Game/WC/Maps/House"
G = "/Game/WC"
KIT = "/Game/HorrorHouseKit"
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "C:/GameDev/Unreal/WellnessCheck/Scripts/level"

eal = unreal.EditorAssetLibrary
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level_editor = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
count = {"mesh": 0, "light": 0, "game": 0}


def log(msg):
    unreal.log_warning("WC_BUILD: " + str(msg))


def asset(path, must=True):
    a = eal.load_asset(path)
    if not a and must:
        raise RuntimeError("missing " + path)
    return a


# ------------------------------------------------------------------ kit index (name without SM_ -> asset)
KIT_INDEX = {}
for a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path(KIT + "/Meshes", recursive=True):
    KIT_INDEX[str(a.asset_name)[3:]] = str(a.package_name)
MI_CACHE = {}


def kit(name):
    if name not in KIT_INDEX:
        raise RuntimeError("no kit mesh " + name)
    return asset(KIT_INDEX[name])


def kmi(name):
    """Kit material instance by short name, e.g. 'WoodFloorDark'; or a /Game/WC material 'WC:Name'."""
    if name not in MI_CACHE:
        if name.startswith("WC:"):
            MI_CACHE[name] = asset(f"{G}/Materials/{name[3:]}")
        else:
            MI_CACHE[name] = asset(f"{KIT}/Materials/MI_{name}")
    return MI_CACHE[name]


def V(x, y, z):
    return unreal.Vector(float(x), float(y), float(z))


def R(yaw=0.0, pitch=0.0, roll=0.0):
    return unreal.Rotator(pitch=pitch, yaw=yaw, roll=roll)


def tag(a, tags):
    if tags:
        a.set_editor_property("tags", [unreal.Name(t) for t in (tags if isinstance(tags, (list, tuple)) else [tags])])


LC_IN = unreal.LightingChannels()
LC_IN.set_editor_property("channel0", True)
LC_IN.set_editor_property("channel1", True)
LC_SHAFT = unreal.LightingChannels()
LC_SHAFT.set_editor_property("channel0", False)
LC_SHAFT.set_editor_property("channel1", True)


def indoor(c, folder):
    """Indoor things also take light from the moon shafts (channel 1).  The outside of the house, the boards in the
    windows and the forest do not, so no window looks lit from the yard."""
    if not folder.startswith(("Shell/Exterior", "Shell/Windows", "Forest", "Cruiser")):
        c.set_editor_property("lighting_channels", LC_IN)


CUBE = asset("/Engine/BasicShapes/Cube.Cube")
CYL = asset("/Engine/BasicShapes/Cylinder.Cylinder")
SPHERE = asset("/Engine/BasicShapes/Sphere.Sphere")
# surface overrides: kit slot name -> our textured material, filled in when those exist (see restyle())
OVERRIDES = {}


def restyle(comp):
    if not OVERRIDES:
        return
    names = comp.get_material_slot_names()
    for i, n in enumerate(names):
        key = str(n)
        if key in OVERRIDES:
            comp.set_material(i, OVERRIDES[key])


def box(name, x0, x1, y0, y1, z0, z1, mat, folder, collide=True, tags=(), hidden=False, shadow=True, yaw=0.0, pitch=0.0, roll=0.0):
    a = actors.spawn_actor_from_class(unreal.StaticMeshActor, V((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), R(yaw, pitch, roll))
    a.set_actor_label(name)
    c = a.static_mesh_component
    c.set_static_mesh(CUBE)
    c.set_material(0, kmi(mat))
    a.set_actor_scale3d(V((x1 - x0) / 100.0, (y1 - y0) / 100.0, (z1 - z0) / 100.0))
    if not collide:
        c.set_collision_profile_name("NoCollision")
    if hidden:
        a.set_actor_hidden_in_game(True)
        c.set_editor_property("cast_shadow", False)
    if not shadow:
        c.set_editor_property("cast_shadow", False)
    tag(a, tags)
    indoor(c, folder)
    a.set_folder_path("House/" + folder)
    count["mesh"] += 1
    return a


def place(mesh, x, y, z, yaw=0.0, folder="Props", name=None, tags=(), pitch=0.0, roll=0.0, scale=1.0, collide=True, shadow=True, mats=None):
    m = kit(mesh) if isinstance(mesh, str) else mesh
    a = actors.spawn_actor_from_class(unreal.StaticMeshActor, V(x, y, z), R(yaw, pitch, roll))
    a.set_actor_label(name or (mesh if isinstance(mesh, str) else m.get_name()))
    c = a.static_mesh_component
    c.set_static_mesh(m)
    if scale != 1.0:
        s = scale if isinstance(scale, (tuple, list)) else (scale, scale, scale)
        a.set_actor_scale3d(V(*s))
    if not collide:
        c.set_collision_profile_name("NoCollision")
    if not shadow:
        c.set_editor_property("cast_shadow", False)
    restyle(c)
    if mats:
        for i, mname in mats.items():
            c.set_material(i, kmi(mname))
    c.set_editor_property("can_ever_affect_navigation", collide and scale == 1.0 and "Hide_" not in str(tags) and "Show_" not in str(tags))
    indoor(c, folder)
    tag(a, tags)
    a.set_folder_path("House/" + folder)
    count["mesh"] += 1
    return a


def wall(piece, cx, cy, z, axis, folder, flip=False, tags=()):
    """A 4 m (or 2 m) kit wall centred at (cx, cy). axis 'x' = runs along X, 'y' = runs along Y."""
    yaw = (0.0 if axis == "x" else 90.0) + (180.0 if flip else 0.0)
    return place(piece, cx, cy, z, yaw, folder, tags=tags)


def light_point(name, x, y, z, lumens, color, radius, folder="Lights", tags=(), shadows=False, vol=1.0, source=4.0):
    a = actors.spawn_actor_from_class(unreal.PointLight, V(x, y, z), R())
    a.set_actor_label(name)
    c = a.light_component
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    c.set_intensity(lumens)
    c.set_light_color(unreal.LinearColor(*color, 1.0))
    c.set_attenuation_radius(radius)
    c.set_cast_shadows(shadows)
    c.set_editor_property("source_radius", source)
    c.set_editor_property("volumetric_scattering_intensity", vol)
    tag(a, tags)
    a.set_folder_path("House/" + folder)
    count["light"] += 1
    return a


def light_spot(name, x, y, z, yaw, pitch, lumens, color, radius, inner, outer, folder="Lights", tags=(), shadows=True, vol=1.0):
    a = actors.spawn_actor_from_class(unreal.SpotLight, V(x, y, z), R(yaw, pitch))
    a.set_actor_label(name)
    c = a.light_component
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    c.set_intensity(lumens)
    c.set_light_color(unreal.LinearColor(*color, 1.0))
    c.set_attenuation_radius(radius)
    c.set_inner_cone_angle(inner)
    c.set_outer_cone_angle(outer)
    c.set_cast_shadows(shadows)
    c.set_editor_property("volumetric_scattering_intensity", vol)
    tag(a, tags)
    a.set_folder_path("House/" + folder)
    count["light"] += 1
    return a


def point(name, x, y, z, yaw=0.0, tags=None, folder="Points"):
    a = actors.spawn_actor_from_class(unreal.TargetPoint, V(x, y, z), R(yaw))
    a.set_actor_label(name)
    tag(a, tags or [name])
    a.set_folder_path("House/" + folder)
    return a


WC = {}
for cls in ("WCDoor", "WCNote", "WCPickup", "WCUsable", "WCTrigger", "WCEntity", "WCLook", "WCWatcher", "WCSmokeMan"):
    WC[cls] = unreal.load_class(None, "/Script/WellnessCheck." + cls)


def trigger(wid, x0, x1, y0, y1, z0, z1):
    a = actors.spawn_actor_from_class(WC["WCTrigger"], V((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), R())
    a.set_actor_label("T_" + wid)
    a.set_editor_property("wc_id", unreal.Name(wid))
    a.get_editor_property("box").set_box_extent(V((x1 - x0) / 2, (y1 - y0) / 2, (z1 - z0) / 2))
    a.set_folder_path("House/Triggers")
    count["game"] += 1
    return a


def door(wid, hx, hy, z, yaw, open_angle, locked=False, key=None, start_open=False, mesh="Door_Victorian_Closed", prompt=None, swing=1.6, tags=()):
    """Hinged door. (hx, hy) is the hinge; the leaf runs 113 cm along the actor's +X."""
    a = actors.spawn_actor_from_class(WC["WCDoor"], V(hx, hy, z), R(yaw))
    a.set_actor_label("Door_" + wid)
    a.set_editor_property("wc_id", unreal.Name(wid))
    a.set_editor_property("locked", locked)
    if key:
        a.set_editor_property("key_id", unreal.Name(key))
    a.set_editor_property("open_angle", float(open_angle))
    a.set_editor_property("start_open", start_open)
    a.set_editor_property("swing_seconds", swing)
    mc = a.get_editor_property("mesh")
    mc.set_static_mesh(kit(mesh))
    mc.set_relative_location(V(56.5, 0, 0), False, False)
    mc.set_editor_property("lighting_channels", LC_IN)
    restyle(mc)
    tag(a, tags)
    a.set_folder_path("House/Doors")
    count["game"] += 1
    return a


def interact(cls, wid, mesh, x, y, z, yaw=0.0, prompt=None, grab=(14, 14, 10), grab_off=(0, 0, 6), scale=1.0, tags=(), label=None, mats=None, pitch=0.0, roll=0.0, enabled=True):
    a = actors.spawn_actor_from_class(WC[cls], V(x, y, z), R(yaw, pitch, roll))
    a.set_actor_label(label or (cls[2:] + "_" + wid))
    a.set_editor_property("wc_id", unreal.Name(wid))
    if prompt:
        a.set_editor_property("prompt", prompt)
    a.set_editor_property("grab_extent", V(*grab))
    a.set_editor_property("grab_offset", V(*grab_off))
    a.set_editor_property("enabled", enabled)
    mc = a.get_editor_property("mesh")
    mc.set_editor_property("lighting_channels", LC_IN)
    if mesh is not None:
        mc.set_static_mesh(kit(mesh) if isinstance(mesh, str) else mesh)
        if scale != 1.0:
            s = scale if isinstance(scale, (tuple, list)) else (scale, scale, scale)
            mc.set_relative_scale3d(V(*s))
        restyle(mc)
        if mats:
            for i, mname in mats.items():
                mc.set_material(i, kmi(mname))
    tag(a, tags)
    a.set_folder_path("House/Interact")
    count["game"] += 1
    return a


NOTES = json.load(open(os.path.join(HERE, "notes.json"), encoding="utf-8"))


def ow(name, fallback):
    """Old West furniture (Fab) by short name, e.g. 'Bed_01f'; the kit piece `fallback` if that pack is not installed."""
    p = f"/Game/OldWest/VOL1/Meshes/SM_{name}"
    return asset(p) if eal.does_asset_exist(p) else fallback


OW_YAW = float(os.environ.get("WC_OW_YAW", "0"))
TABLE = ow("Table_Small_01a", "Table_Side_Round")     # a plain small table (the kit's pedestal stand read as "not a table")          # added to every Old West piece if the pack faces another way


def note(wid, mesh, x, y, z, yaw=0.0, scale=1.0, grab=(18, 18, 8), tags=(), pitch=0.0, roll=0.0):
    n = NOTES[wid]
    if mesh == "Letters_Scattered" and scale == 1.0:
        scale = 0.5                      # a fan of loose sheets wider than the table they are on looks like it is floating
    a = interact("WCNote", wid, mesh, x, y, z, yaw, "Read", grab, (0, 0, 4), scale, tags, pitch=pitch, roll=roll)
    a.set_editor_property("title", n.get("title", ""))
    a.set_editor_property("body", n["body"])
    a.set_editor_property("style", int(n.get("style", 1)))
    return a


def ITEM(name, fallback=None):
    """One of the small carried models (Scripts/art/build_items.py), or the plain shape it replaces if it is not imported yet."""
    p = f"{G}/Props/SM_Item_{name}"
    return asset(p) if eal.does_asset_exist(p) else fallback


def pickup(wid, item, display, mesh, x, y, z, yaw=0.0, scale=1.0, grab=(12, 12, 8), tags=(), mats=None):
    if isinstance(mesh, tuple):          # (item model name, plain fallback mesh, fallback scale, fallback mats)
        real = ITEM(mesh[0])
        mesh, scale, mats = (real, 1.0, None) if real else (mesh[1], mesh[2], mesh[3])
    a = interact("WCPickup", wid, mesh, x, y, z, yaw, "Take", grab, (0, 0, 4), scale, tags, mats=mats)
    a.set_editor_property("item_id", unreal.Name(item))
    a.set_editor_property("display_name", display)
    return a


# ------------------------------------------------------------------ open / reset the map
eal.make_directory(G + "/Maps")
if eal.does_asset_exist(MAP):
    if not level_editor.load_level(MAP):
        raise RuntimeError("could not open " + MAP)
    old = actors.get_all_level_actors()
    actors.destroy_actors([a for a in old if not isinstance(a, unreal.WorldSettings)])
elif not level_editor.new_level(MAP):
    raise RuntimeError("could not create " + MAP)

# textured surfaces, when they have been imported (import_assets.py step "tex")
for slot, mi in json.load(open(os.path.join(HERE, "overrides.json"))).items():
    p = f"{KIT}/Materials/{mi[4:]}" if mi.startswith("KIT:") else f"{G}/Materials/{mi}"
    if eal.does_asset_exist(p):
        OVERRIDES[slot] = asset(p)
log(f"{len(OVERRIDES)} surface overrides")


def surf(kit_name, wc_name):
    """Our textured material if it exists, else the kit's flat one."""
    return "WC:" + wc_name if eal.does_asset_exist(f"{G}/Materials/{wc_name}") else kit_name


M_FLOOR = surf("WoodFloorDark", "MI_FloorBoards")
M_CEIL = surf("PlasterOld", "MI_PlasterCeiling")
M_STONE = surf("StoneGraveDark", "MI_CellarStone")
M_DIRT = surf("GraveDirtDark", "MI_CellarFloor")
M_ROOF = surf("Rust", "MI_RoofTin")
M_SIDING = surf("SidingDark", "MI_Siding")
M_GROUND = surf("GraveDirt", "MI_YardGround")
M_GRAVEL = surf("Sand", "MI_Gravel")
M_ATTIC = surf("WoodRotten", "MI_AtticBoards")
M_PORCH = surf("WoodBleached", "MI_PorchBoards")
M_WOODV = surf("WoodVictorian", "MI_WoodTrim")
M_WOODR = surf("WoodRotten", "MI_WoodRotten")

GZ, UZ, AZ, CZ = 0.0, 350.0, 700.0, -350.0
SX0, SX1, SY0, SY1 = 400.0, 800.0, -184.0, 8.0          # stair tower footprint (inner)
XB = 2800.0                                              # back wall of the house (the rear wing runs X 1600..2800)

# ================================================================== FLOORS / CEILINGS (boxes, with the stair hole)
# places where a floor has rotted through: (x0, x1, y0, y1) per level
HOLES = {GZ: [(470, 620, -560, -440)], UZ: [(1290, 1440, -430, -310), (2480, 2600, 330, 450)], AZ: [(1280, 1400, 300, 420)]}
HOLE_LIST = []      # (x0, x1, y0, y1, z of this floor, z of the floor below) for decay.py


def cut(rects, hole):
    hx0, hx1, hy0, hy1 = hole
    out = []
    for (x0, x1, y0, y1) in rects:
        if hx1 <= x0 or hx0 >= x1 or hy1 <= y0 or hy0 >= y1:
            out.append((x0, x1, y0, y1))
            continue
        if hx0 > x0:
            out.append((x0, hx0, y0, y1))
        if hx1 < x1:
            out.append((hx1, x1, y0, y1))
        mx0, mx1 = max(x0, hx0), min(x1, hx1)
        if hy0 > y0:
            out.append((mx0, mx1, y0, hy0))
        if hy1 < y1:
            out.append((mx0, mx1, hy1, y1))
    return out


def slab(name, z_top, mat, folder, surface, thick=20.0, ceil_mat=None):
    parts = [(0, SX0, -600, 600), (SX1, XB, -600, 600), (SX0, SX1, -600, SY0), (SX0, SX1, SY1 + 16, 600)]
    for h in HOLES.get(z_top, []):
        parts = cut(parts, h)
        HOLE_LIST.append((h[0], h[1], h[2], h[3], z_top, z_top - 350.0))
    for i, (x0, x1, y0, y1) in enumerate(parts):
        box(f"{name}_{i}", x0, x1, y0, y1, z_top - thick, z_top, mat, folder, tags=["Floor_" + surface])
        if ceil_mat:
            box(f"{name}_ceil_{i}", x0, x1, y0, y1, z_top - thick - 3, z_top - thick, ceil_mat, folder, collide=False)


slab("GroundFloor", GZ, M_FLOOR, "Shell/Ground", "Wood")
slab("UpperFloor", UZ, M_FLOOR, "Shell/Upper", "Wood", ceil_mat=M_CEIL)
slab("AtticFloor", AZ, M_ATTIC, "Shell/Attic", "Wood", ceil_mat=M_CEIL)
box("CellarFloor", -20, 1620, -620, 620, CZ - 20, CZ, M_DIRT, "Shell/Cellar", tags=["Floor_Stone"])
for _i, (_x0, _x1, _y0, _y1) in enumerate(cut([(0, SX0, -600, 600)], HOLES[GZ][0]) if False else [(0, SX0, -600, 600)]):
    box(f"CellarCeil_{_i}", _x0, _x1, _y0, _y1, GZ - 26, GZ - 20, M_ATTIC, "Shell/Cellar", collide=False)
box("CellarCeil2", SX1, 1600, -600, 600, GZ - 26, GZ - 20, M_ATTIC, "Shell/Cellar", collide=False)
box("CellarCeil3", SX0, SX1, SY1 + 16, 600, GZ - 26, GZ - 20, M_ATTIC, "Shell/Cellar", collide=False)
for _i, (_x0, _x1, _y0, _y1) in enumerate(cut([(SX0, SX1, -600, SY0)], HOLES[GZ][0])):
    box(f"CellarCeil4_{_i}", _x0, _x1, _y0, _y1, GZ - 26, GZ - 20, M_ATTIC, "Shell/Cellar", collide=False)

# ================================================================== STAIRS (kit mesh for looks, a hidden ramp to walk on)
RISE, RUN = 350.0, 400.0
RLEN = math.hypot(RISE, RUN)
RANG = math.degrees(math.atan2(RISE, RUN))
STAIR_YAW = float(os.environ.get("WC_STAIR_YAW", "0"))
M_TREAD = surf("WoodDark", "MI_WoodDark")
M_STRING = surf("WoodVictorian", "MI_WoodTrim")


def sloped(name, y0, y1, dz, thick, mat, z0):
    """A board lying along the flight: from the foot (X 400) to the head (X 800), dz above the nosing line."""
    b = actors.spawn_actor_from_class(unreal.StaticMeshActor, V(600, (y0 + y1) / 2.0, z0 + RISE / 2 + dz), R(0, RANG, 0))
    b.set_actor_label(name)
    bc_ = b.static_mesh_component
    bc_.set_static_mesh(CUBE)
    bc_.set_material(0, kmi(mat))
    b.set_actor_scale3d(V(RLEN / 100.0, (y1 - y0) / 100.0, thick / 100.0))
    bc_.set_collision_profile_name("NoCollision")
    bc_.set_editor_property("lighting_channels", LC_IN)
    b.set_folder_path("House/Shell/Stairs")
    count["mesh"] += 1
    return b


NSTEP = 16
for i, z0 in enumerate((CZ, GZ, UZ)):
    # a real flight: treads and risers between two stringers, with a boarded soffit underneath.  (The kit stair is a solid
    # wedge; three of them stacked put a flat "floor" over each flight below.)
    for k in range(NSTEP):
        xt = SX0 + k * RUN / NSTEP
        zt = z0 + (k + 1) * RISE / NSTEP
        box(f"Tread_{i}_{k}", xt - 3, xt + RUN / NSTEP, SY0 + 4, SY1 - 4, zt - 4, zt, M_TREAD, "Shell/Stairs", collide=False)
        if i > 0 or k % 3 != 1:          # the cellar flight has lost some risers
            box(f"Riser_{i}_{k}", xt, xt + 2, SY0 + 4, SY1 - 4, zt - RISE / NSTEP, zt - 4, M_TREAD, "Shell/Stairs", collide=False)
    sloped(f"StringerL_{i}", SY0, SY0 + 5, 4.0, 34.0, M_STRING, z0)
    sloped(f"StringerR_{i}", SY1 - 5, SY1, 4.0, 34.0, M_STRING, z0)
    sloped(f"Soffit_{i}", SY0, SY1, -22.0, 3.0, M_CEIL if i > 0 else M_ATTIC, z0)
    a = actors.spawn_actor_from_class(unreal.StaticMeshActor, V(600, -88, z0 + RISE / 2 - 4), R(0, RANG, 0))
    a.set_actor_label(f"StairRamp_{i}")
    a.static_mesh_component.set_static_mesh(CUBE)
    a.static_mesh_component.set_material(0, kmi("WC:M_Collision"))
    a.set_actor_scale3d(V(RLEN / 100.0, 1.84, 0.08))
    a.set_actor_hidden_in_game(True)
    a.static_mesh_component.set_editor_property("cast_shadow", False)
    tag(a, ["Floor_Stairs"])
    a.set_folder_path("House/Shell/Stairs")
# tower side wall (hall side) on the three levels, and the end walls with their doors
for z, f in ((GZ, "Ground"), (UZ, "Upper")):
    wall("Wall_Plain_Simple", 600, SY1 + 8, z, "x", "Shell/" + f)
wall("Wall_Doorway_2m", 800, -88, GZ, "y", "Shell/Ground")            # cellar door, under the main stairs' top
wall("Wall_Doorway_2m", 400, -88, UZ, "y", "Shell/Upper")             # attic door, at the foot of the attic stairs
box("TowerLintelG", 392, 408, -200, 16, 250, 330, M_WOODV, "Shell/Ground")     # header over the main stair entrance
box("TowerLintelU", 792, 808, -200, 16, UZ + 250, UZ + 330, M_WOODV, "Shell/Upper")
box("CellarStairWall", SX0, SX1, SY1, SY1 + 16, CZ, GZ - 20, M_STONE, "Shell/Cellar")
box("CellarStairBack", 800, 816, -200, SY1 + 16, CZ, GZ - 20, M_STONE, "Shell/Cellar")
box("AtticStairRailA", SX0, SX1, SY1, SY1 + 10, AZ, AZ + 100, M_WOODV, "Shell/Attic")
box("AtticStairRailB", SX0 - 10, SX0, SY0 - 16, SY1 + 10, AZ, AZ + 100, M_WOODV, "Shell/Attic")

# ================================================================== WALLS: ground and upper floors
# (piece per 4 m segment; None = open)
def run_x(y, z, pieces, folder, x_start=200):
    for i, p in enumerate(pieces):
        if p:
            wall(p, x_start + i * 400, y, z, "x", folder)


def run_y(x, z, pieces, folder, y_start=-400):
    for i, p in enumerate(pieces):
        if p:
            wall(p, x, y_start + i * 400, z, "y", folder)


PLAIN, WAIN, DOORW, WIN = "Wall_Plain_Simple", "Wall_Wainscot_Green", "Wall_Doorway", "Wall_Window"
PEEL = "Wall_Peeling"
# ---- ground: front block (living, dining, kitchen, her sitting room) + rear wing (den, bath, pantry, sickroom)
run_y(0, GZ, [WIN, DOORW, WIN], "Shell/Ground")                                   # front
run_y(1600, GZ, [PLAIN, "Wall_Doorway_Arched", DOORW], "Shell/Ground")            # old back wall: hall arch, kitchen -> pantry
run_y(XB, GZ, [WIN, DOORW, WIN], "Shell/Ground")                                  # back
run_x(-600, GZ, [PEEL, "Wall_Fireplace_Breast", WIN, "Wall_Wainscot_Grey", WIN, "Wall_Fireplace_Breast", WIN], "Shell/Ground")
run_x(600, GZ, [WIN, PEEL, WIN, "Wall_Exposed_Brick", WIN, PEEL, WIN], "Shell/Ground")
run_x(-200, GZ, ["Wall_Doorway_Double", "Wall_Wainscot_Red", "Wall_Wainscot_Grey", DOORW, DOORW, "Wall_Wainscot_Red", DOORW], "Shell/Ground")   # hall | living, sitting, den, bath
run_x(200, GZ, ["Wall_Doorway_Arched", WAIN, DOORW, PLAIN, WAIN, DOORW, "Wall_Wainscot_Grey"], "Shell/Ground")                               # hall | dining, kitchen, pantry, sickroom
wall("Wall_Wainscot_Red", 800, -400, GZ, "y", "Shell/Ground")                     # living | sitting
wall(DOORW, 800, 400, GZ, "y", "Shell/Ground")                                    # dining | kitchen
wall("Wall_Wainscot_Grey", 2400, -400, GZ, "y", "Shell/Ground")                   # den | bath
wall(PEEL, 2000, 400, GZ, "y", "Shell/Ground")                                    # pantry | sickroom
# ---- upper: master, Ruth's room, bath, prayer room + rear wing (Daniel's room, sewing room, the aide's room, second bath)
run_y(0, UZ, [WIN, WIN, WIN], "Shell/Upper")
run_y(1600, UZ, ["Wall_Striped_Green", DOORW, "Wall_Striped_Purple"], "Shell/Upper")
run_y(XB, UZ, [PLAIN, WIN, PLAIN], "Shell/Upper")
run_x(-600, UZ, [WIN, PEEL, WIN, "Wall_Exposed_Brick", WIN, PEEL, WIN], "Shell/Upper")
run_x(600, UZ, [WIN, PEEL, "Wall_Striped_Purple", PEEL, WIN, PEEL, WIN], "Shell/Upper")
run_x(-200, UZ, [DOORW, "Wall_Striped_Green", DOORW, PLAIN, DOORW, "Wall_Striped_Green", DOORW], "Shell/Upper")               # hall | Ruth's, bath, Daniel's, sewing
run_x(200, UZ, [DOORW, "Wall_Wainscot_Purple", DOORW, "Wall_Striped_Purple", DOORW, "Wall_Wainscot_Purple", DOORW], "Shell/Upper")   # hall | master, prayer, aide's, bath 2
wall("Wall_Striped_Green", 800, -400, UZ, "y", "Shell/Upper")
wall("Wall_Wainscot_Purple", 800, 400, UZ, "y", "Shell/Upper")
wall("Wall_Striped_Green", 2400, -400, UZ, "y", "Shell/Upper")
wall(PEEL, 2400, 400, UZ, "y", "Shell/Upper")
# corner posts hide the seams
for z, f in ((GZ, "Ground"), (UZ, "Upper")):
    for x in (0, 800, 1600, 2400, 2800):
        for y in (-600, -200, 200, 600):
            if (x, y) in ((800, -200),):
                continue
            place("Wall_Corner_Post", x, y, z, 0, "Shell/" + f, collide=False)
    place("Wall_Corner_Post", 2000, 200, GZ, 0, "Shell/Ground", collide=False)
    place("Wall_Corner_Post", 2000, 600, GZ, 0, "Shell/Ground", collide=False)

exec(open(os.path.join(HERE, "exterior.py"), encoding="utf-8").read())
log("shell done")

# ================================================================== WINDOWS (boarded from the inside), fake doors
WZ = 95.0
def window_y(x, y, z, facing):       # in a wall that runs along Y
    place("Window_Boarded", x + facing * 4, y, z + WZ, 90, "Shell/Windows")


def window_x(x, y, z, facing):
    place("Window_Boarded", x, y + facing * 4, z + WZ, 0, "Shell/Windows")


for z in (GZ, UZ):
    for y in (-400, 400):
        window_y(0, y, z, 1)
    window_x(200, 600, z, -1)
    window_x(200 if z == UZ else 1000, -600, z, 1)
    for x in (1800, 2600):
        window_x(x, -600, z, 1)
window_y(0, 0, UZ, 1); window_y(XB, 0, UZ, -1)
window_y(XB, -400, GZ, -1); window_y(XB, 400, GZ, -1)
window_x(1000, 600, GZ, -1); window_x(1000, -600, UZ, 1)
window_x(1800, 600, GZ, -1); window_x(2600, 600, GZ, -1); window_x(1800, 600, UZ, -1); window_x(2600, 600, UZ, -1)

# ================================================================== DOORS
door("front", 0, -56.5, GZ, 90, -100, locked=True, swing=2.2)
door("back", XB, -56.5, GZ, 90, 95, locked=True, mesh="Door_Boarded")
door("pantry", 1600, 343.5, GZ, 90, -95)
door("den", 1743.5, -200, GZ, 0, -95)
door("bath_g", 2543.5, -200, GZ, 0, -95, start_open=True)
door("sickroom", 2143.5, 200, GZ, 0, 95)
door("up_ell", 1600, -56.5, UZ, 90, 95, locked=True, key="key_ell")
door("up_daniel", 1743.5, -200, UZ, 0, -95)
door("up_sewing", 2543.5, -200, UZ, 0, -95)
door("up_aide", 1743.5, 200, UZ, 0, 95)
door("up_bath2", 2543.5, 200, UZ, 0, 95, start_open=True)
door("kitchen", 943.5, 200, GZ, 0, 95, start_open=True)
door("sitting", 1343.5, -200, GZ, 0, -95, locked=True, key="key_sitting")
door("cellar", 800, -144.5, GZ, 90, -100, locked=True, key="key_cellar")
door("up_master", 143.5, 200, UZ, 0, 100, start_open=True)
door("up_kids", 143.5, -200, UZ, 0, -95, locked=True)
door("up_bath", 943.5, -200, UZ, 0, -95)
door("up_prayer", 943.5, 200, UZ, 0, 95, locked=True, key="key_prayer")
door("up_attic", 400, -144.5, UZ, 90, 100, locked=True, key="key_attic")

# ================================================================== CELLAR WALLS (stone boxes)
C = "Shell/Cellar"
box("CW_Front", -20, 0, -620, 620, CZ, GZ - 20, M_STONE, C)
box("CW_Back", 1600, 1620, -620, 620, CZ, GZ - 20, M_STONE, C)
box("CW_Left", 0, 1600, -620, -600, CZ, GZ - 20, M_STONE, C)
box("CW_Right", 0, 1600, 600, 620, CZ, GZ - 20, M_STONE, C)
box("CW_HallL_a", 800, 1600, -216, -200, CZ, GZ - 20, M_STONE, C)          # left wing only under the living room
box("CW_HallL_b", 0, 130, -216, -200, CZ, GZ - 20, M_STONE, C)
box("CW_HallL_c", 290, 400, -216, -200, CZ, GZ - 20, M_STONE, C)
box("CW_HallL_d", 400, 800, -216, -200, CZ, GZ - 20, M_STONE, C)
box("CW_HallL_lintel", 130, 290, -216, -200, CZ + 220, GZ - 20, M_STONE, C)
box("CW_WingBack", 800, 816, -600, -200, CZ, GZ - 20, M_STONE, C)
box("CW_HallR_a", 0, 1330, 200, 216, CZ, GZ - 20, M_STONE, C)             # right side solid, except the root cellar mouth
box("CW_HallR_b", 1470, 1600, 200, 216, CZ, GZ - 20, M_STONE, C)
box("CW_HallR_lintel", 1330, 1470, 200, 216, CZ + 215, GZ - 20, M_STONE, C)
box("CW_RootSide", 1184, 1200, 216, 600, CZ, GZ - 20, M_STONE, C)
box("CW_FillRight", 0, 1184, 216, 600, CZ, GZ - 20, M_STONE, C)            # solid earth under the dining room side
for x in (300, 1050, 1450):
    box(f"CellarPost_{x}", x - 9, x + 9, 100, 118, CZ, GZ - 20, M_WOODR, C)
for _n, (_x0, _x1, _y0, _y1, _z) in {"KitchenTiles": (816, 1584, 216, 584, GZ), "BathTiles": (816, 1584, -584, -216, UZ), "PantryTiles": (1616, 1984, 216, 584, GZ),
                                      "BathGTiles": (2416, 2784, -584, -216, GZ), "Bath2Tiles": (2416, 2784, 216, 584, UZ)}.items():
    _rects = [(_x0, _x1, _y0, _y1)]
    for _h in HOLES.get(_z, []):
        _rects = cut(_rects, _h)
    for _i, (_a, _b, _c, _d) in enumerate(_rects):
        box(f"{_n}_{_i}", _a, _b, _c, _d, _z, _z + 1.2, surf("TileDark", "MI_MegaTilesOld" if _n in ("KitchenTiles", "PantryTiles") else "MI_MegaTilesStained"), "Shell/Tiles", tags=["Floor_Stone"])
log("walls, doors, cellar done")

# ================================================================== DRESSING
D = "Dressing/"
# ---- foyer / hall
place("Rug_Persian_Worn", 200, 0, GZ, 90, D + "Hall", collide=False)
place("Coat_Rack", 60, 150, GZ, 0, D + "Hall")
place("Umbrella_Stand_Umbrellas", 55, -150, GZ, 0, D + "Hall")
place(TABLE, 300, 150, GZ, 0, D + "Hall")
place("Clock_Grandfather", 1100, -168, GZ, 0, D + "Hall")
place("Portrait_Large", 1400, 181, GZ + 130, 180, D + "Hall", collide=False)        # was at x 1000: the middle of the kitchen doorway
place("Portrait_Oval", 600, 181, GZ + 150, 180, D + "Hall", collide=False)
place("Portrait_Slashed", 1250, -181, GZ + 140, 0, D + "Hall", collide=False)
place("Mirror_Covered_Sheet", 2730, 120, GZ, 250, D + "Hall")
place("Bust_Pedestal", 1540, -150, GZ, 110, D + "Hall")
place("Cobweb_Corner", 20, -180, GZ + 250, 0, D + "Hall", collide=False)
place("Newspaper_Pile", 120, -120, GZ, 30, D + "Hall", collide=False)
note("note_mail", "Letters_Scattered", 300, 150, GZ + 99, 20)
# ---- living room (front left)
L = D + "Living"
place("Rug_Persian_Worn", 420, -400, GZ, 0, L, collide=False)
place("Sofa_Sagging_Broken", 430, -335, GZ, 180, L)          # in the middle of the room, facing the television on the south wall
place("Armchair_Wingback_Torn", 545, -265, GZ, 205, L)
place("Armchair_Tipped", 615, -415, GZ, 120, L)
place("Fireplace_Wood_Overmantel", 600, -562, GZ, 0, L)
place("Mantel_Clock", 600, -548, GZ + 132, 0, L, collide=False)
place("Piano_Upright", 90, -420, GZ, 90, L)
place("Piano_Stool", 170, -420, GZ, 0, L)
place(TABLE, 720, -250, GZ, 0, L)
place("Rocking_Chair_Shawl", 690, -500, GZ, 150, L, tags=["RockingChair"])
place("Portrait_Slashed", 250, -581, GZ + 165, 0, L, collide=False)
place("Portrait_Small", 470, -581, GZ + 175, 0, L, collide=False)
# the television: against the south wall between the portraits, facing the hall doors
if ITEM("TV"):
    interact("WCUsable", "tv", ITEM("TV"), 360, -548, GZ, float(os.environ.get("WC_TV_YAW", "0")), "Look at the television", (48, 28, 44), (0, 0, 52))
    point("Her_TVFar", 200, -110, GZ, -60)          # in the hall doorway, behind anyone at the set
place("Portrait_Oval", 783, -420, GZ + 150, 270, L, collide=False)
place("Portrait_Small", 783, -300, GZ + 160, 270, L, collide=False)
place("Plant_Stand_Dead_Fern", 60, -250, GZ, 0, L)
place("Curtains_Torn_Window", 22, -400, GZ + 20, 90, L, collide=False)
place("Cobweb_Wall_Large", 780, -560, GZ + 200, 270, L, collide=False)
note("note_letter1", "Letters_Scattered", 720, -250, GZ + 99, 40)
# ---- dining room (front right): the table set for four
DI = D + "Dining"
place("Rug_Persian_Worn", 420, 400, GZ, 0, DI, collide=False)
place("Table_Dining_Long", 420, 400, GZ, 0, DI)
for x, y, yaw in ((330, 330, 180), (510, 330, 180), (330, 470, 0), (510, 470, 0)):
    place("Chair_Dining_HighBack", x, y, GZ, yaw, DI)
place("Plates_Stack_Dusty", 300, 400, GZ + 80, 0, DI, collide=False)
place("Candelabra_5", 420, 400, GZ + 80, 0, DI, collide=False)
place("Teapot_Old", 520, 410, GZ + 80, 40, DI, collide=False)
place("Dresser_Drawers", 420, 560, GZ, 180, DI)
place(ow("Cabinet_02a", "Bookshelf_Tall"), 700, 558, GZ, 180 + OW_YAW, DI, name="ChinaCabinet")
place("Chandelier_Fallen", 600, 300, GZ, 30, DI, collide=False)
place("Portrait_Large", 783, 250, GZ + 130, 90, DI, collide=False)
place("Clock_Grandfather_Broken", 60, 560, GZ, 0, DI)
place("Curtains_Torn_Window", 22, 400, GZ + 20, 90, DI, collide=False)
place("Chair_Dining_Broken", 690, 440, GZ, 30, DI)
# ---- kitchen (back right)
K = D + "Kitchen"
place("Table_Seance_Round", 1250, 420, GZ, 0, K)
# (no chair on the hall side of the table: that is the way through to the pantry)
place("Chair_Dining_HighBack", 1160, 420, GZ, 270, K)
place("Chair_Dining_HighBack", 1340, 430, GZ, 80, K, tags=["KitchenChair"])
place("Cabinet_Steel_Low_Drawers", 900, 560, GZ, 180, K)
place("Sink_Hospital", 1050, 570, GZ, 180, K)
place("Cabinet_Medicine_Glass_Open", 1400, 560, GZ, 180, K)
place("Dresser_Drawers", 1560, 300, GZ, 270, K, tags=["Hide_drawer"])
place("Dresser_Drawers_Open", 1548, 300, GZ, 270, K, tags=["Show_drawer"])
place("Radiator_Cast_Iron", 1320, 578, GZ, 180, K)
place("Plates_Stack_Dusty", 1250, 400, GZ + 89, 0, K, collide=False)
place("Tin_Cans_Rusty", 920, 560, GZ + 95, 0, K, collide=False)
place("Bottles_Empty_Group", 1500, 560, GZ, 0, K, collide=False)
place(TABLE, 868, 536, GZ, 0, K)
interact("WCUsable", "phone", "Telephone_Rotary", 868, 536, GZ + 98, 20, "Pick up the phone", (18, 18, 14))
point("PhonePoint", 868, 536, GZ + 110)
note("note_calendar", "Newspaper_Single", 1100, 219, GZ + 150, 0, pitch=0, roll=90, grab=(22, 6, 22))
note("note_grocery", "Clipboard_Chart", 1480, 150, GZ + 4, 30)
pickup("pick_key_sitting", "key_sitting", "Small brass key", ("Key", CUBE, (0.07, 0.022, 0.006), {0: "BrassOld"}), 1530, 300, GZ + 97, 20, tags=["Show_drawer"])
# ---- sitting room (back left, locked): her room
S = D + "Sitting"
place("Rug_Persian_Worn", 1200, -400, GZ, 90, S, collide=False)
place("Rocking_Chair", 1150, -470, GZ, 30, S)
place("Desk_Writing", 1500, -420, GZ, 270, S)
place("Chair_Dining_HighBack", 1430, -420, GZ, 90, S)
interact("WCUsable", "phonograph", "Phonograph", 880, -540, GZ, 20, "Look at the phonograph", (32, 32, 46), (0, 0, 62))
point("Her_RecordDoor", 1392, -188, GZ, -144)
place("Wardrobe_Mirror_Cracked", 1300, -560, GZ, 0, S)
place("Folding_Screen_Victorian", 900, -280, GZ, 60, S)
place("Candle_Melted_Puddle", 1500, -470, GZ + 101, 0, S, collide=False)
# (her drawings on this wall are real drawings now: memory.py)
note("note_diary2", "Book_Open_Pages", 1500, -416, GZ + 101, 100, grab=(14, 14, 6))
note("note_ruth", "Letters_Scattered", 1490, -340, GZ + 101, 60, scale=0.7, grab=(12, 12, 6))
pickup("pick_key_prayer", "key_prayer", "Iron key on a ribbon", ("KeyIron", CUBE, (0.08, 0.024, 0.006), {0: "Iron"}), 1508, -457, GZ + 102, 70, grab=(10, 10, 7))
note("note_deskkey", "Letters_Scattered", 1492, -377, GZ + 101.5, 20, scale=0.45, grab=(10, 10, 5))
# ---- upstairs hall
UH = D + "UpperHall"
place("Rug_Persian_Worn", 1150, 0, UZ, 90, UH, collide=False)
place(TABLE, 1520, 140, UZ, 0, UH)
place("Plant_Stand_Dead_Fern", 60, 140, UZ, 0, UH)
place("Portrait_Large", 600, 181, UZ + 130, 180, UH, collide=False)
place("Portrait_Glowing_Eyes", 1300, -181, UZ + 140, 0, UH, collide=False)
place("Chair_Dining_Broken", 1450, -120, UZ, 200, UH)
place("Cobweb_Doorway", 60, 0, UZ + 240, 90, UH, collide=False)
# ---- master bedroom (front right)
MB = D + "Master"
place(ow("Bed_01f", "Bed_FourPoster_Broken"), 560, 455, UZ, 0 + OW_YAW, MB, name="MasterBed")
place(TABLE, 700, 300, UZ, 0, MB)
place("Vanity_Dresser_Smashed", 420, 565, UZ, 180, MB)
place("Wardrobe_Open_Clothes", 60, 500, UZ, 90, MB)
place("Rocking_Chair", 120, 300, UZ, 300, MB, tags=["MasterRocker"])
place("Rug_Persian_Worn", 380, 380, UZ, 0, MB, collide=False)
place("Chest_Trunk", 400, 440, UZ, 90, MB)
place("Curtains_Torn_Window", 22, 400, UZ + 20, 90, MB, collide=False)
place("Oil_Lamp_Broken_Unlit", 700, 300, UZ + 98, 0, MB, collide=False)
note("note_diary1", "Book_Open_Pages", 690, 310, UZ + 99, 30)
note("note_walter", "Newspaper_Single", 420, 548, UZ + 100, 10)
# ---- children's room (front left)
KD = D + "Kids"
_rb = place(ow("Bed_02g", "Bed_Hospital_Sheet"), 640, -470, UZ, 180 + OW_YAW, KD, tags=["RuthBed"], name="RuthBed")
_rbo, _rbe = _rb.get_actor_bounds(False)
RB_X, RB_EDGE = (_rbo.x, _rbo.y + _rbe.y) if 20 < _rbe.y < 160 else (640.0, -400.0)
log(f"RuthBed centre ({_rbo.x:.0f},{_rbo.y:.0f}) half ({_rbe.x:.0f},{_rbe.y:.0f},{_rbe.z:.0f}) open edge y={RB_EDGE:.0f}")
place(ow("Bed_02c", "Bed_Hospital_Rusty"), 250, -470, UZ, 180 + OW_YAW, KD, name="DannyOldBed")
place("Cradle_Rocking", 80, -300, UZ, 90, KD)
place("Rocking_Horse_Broken", 440, -500, UZ, 200, KD)
place("Dollhouse_Victorian", 730, -290, UZ, 270, KD)
place("Toy_Blocks_Scattered", 500, -380, UZ, 0, KD, collide=False)
place("Teddy_Bear_One_Eye", 640, -480, UZ + 62, 20, KD, collide=False)
place("Rag_Doll_Torn_One_Eye", 240, -500, UZ + 50, 0, KD, collide=False)
place("Jack_In_The_Box", 390, -560, UZ, 40, KD, collide=False)
place("Toy_Train_Wind_Up", 500, -545, UZ, 130, KD, collide=False)
place("Rug_Persian_Worn", 420, -400, UZ, 0, KD, collide=False, scale=0.8)
place("Curtains_Torn_Window", 22, -400, UZ + 20, 90, KD, collide=False)
note("note_kids", "Letters_Scattered", 360, -330, UZ + 1, 70, scale=0.8)
pickup("pick_keep_ruth", "keep_ruth", "Ruth's music box", "Music_Box_Closed", RB_X, RB_EDGE + 52, UZ + 1, 30, grab=(16, 16, 12))
point("MusicBoxPoint", RB_X, RB_EDGE + 52, UZ + 20)
# ---- bathroom + linen (back left)
B = D + "Bath"
place("Mirror_Wall_Oval", 1250, -582, UZ + 150, 0, B, collide=False)
place("Medicine_Cabinet_Wall_Open", 1100, -580, UZ + 140, 0, B, collide=False)
place("Laundry_Cart", 1500, -300, UZ, 30, B)
place("Privacy_Screen_Torn", 880, -330, UZ, 70, B)
# ---- prayer room (back right, locked): the keeping
PR = D + "Prayer"
place("Ritual_Circle_Floor", 1200, 400, UZ, 0, PR, collide=False)
place("Desk_Writing", 1200, 560, UZ, 180, PR, name="Altar")
place("Candle_Short_Cluster", 1150, 560, UZ + 101, 0, PR, collide=False)
place("Candle_Red_Trio", 1260, 565, UZ + 101, 0, PR, collide=False)
place("Candle_Cluster_Floor", 1060, 300, UZ, 0, PR, collide=False)
place("Candle_Cluster_Floor", 1340, 500, UZ, 120, PR, collide=False)
place("Candle_Ring_Purple", 1200, 400, UZ, 0, PR, collide=False)
place("Tome_Grimoire_Eye", 1200, 545, UZ + 101, 10, PR, collide=False)
place("Book_Lectern_Open", 1450, 320, UZ, 250, PR)
place("Skull_Goat_Horned", 1200, 583, UZ + 180, 0, PR, collide=False)
def hair_cord(x, y, z_top, length, folder, tags=(), name="HairCord"):
    """A hanging cord of grey hair with a fat knot in it."""
    place(CYL, x, y, z_top - length / 2, 0, folder, name=name, tags=tags, collide=False, scale=(0.014, 0.014, length / 100.0), mats={0: surf("Rope", "MI_Sheet")})
    place(SPHERE, x, y, z_top - length * 0.62, 0, folder, name=name + "_knot", tags=tags, collide=False, scale=(0.06, 0.06, 0.085), mats={0: surf("Rope", "MI_Sheet")})
    place(SPHERE, x, y, z_top - length, 0, folder, name=name + "_end", tags=tags, collide=False, scale=(0.035, 0.035, 0.12), mats={0: surf("Rope", "MI_Sheet")})


for i, (x, y) in enumerate(((1100, 380), (1200, 300), (1300, 380))):
    hair_cord(x, y, UZ + 328, 150 + i * 14, PR, name=f"PrayerCord_{i}")
place("Mirror_Standing_Cheval", 900, 520, UZ, 40, PR)
place("Chain_Hanging", 1500, 560, UZ + 140, 0, PR, collide=False)
note("note_prayer", "Scroll_Open", 1450, 320, UZ + 112, 250, grab=(22, 22, 14))
pickup("pick_keep_walter", "keep_walter", "Walter's wedding ring", ("Ring", CYL, (0.022, 0.022, 0.006), {0: "Gold"}), 1180, 535, UZ + 102, 0)
# ---- attic
AT = D + "Attic"
interact("WCUsable", "trunk", "Chest_Trunk", 760, -430, AZ, 90, "Open the footlocker", (50, 30, 36), (0, 0, 36))
place("Crate_Wood_Large", 520, -520, AZ, 20, AT)
place("Crate_Wood_Small", 620, -540, AZ, 70, AT)
place("Box_Cardboard_Stack", 1000, -480, AZ, 10, AT)
place("Suitcase_Old", 900, -400, AZ, 130, AT)
place("Armchair_Sheet_Covered", 1050, 150, AZ, 220, AT)
place("Sofa_Sheet_Covered", 560, 300, AZ, 90, AT)
place("Mirror_Covered_Sheet", 1100, -200, AZ, 140, AT)
place("Rocking_Horse_Broken", 600, 80, AZ, 300, AT)
place("Portrait_Easel", 1000, 420, AZ, 200, AT)
place("Book_Pile_Fallen", 880, 250, AZ, 0, AT, collide=False)
place("Wardrobe_Leaning", 780, 560, AZ, 180, AT)
place("Box_Cardboard_Open", 500, -250, AZ, 40, AT)
place("Hatbox_Round", 700, -300, AZ, 0, AT, collide=False)
for x, y, yaw in ((700, -590, 0), (900, 590, 180)):
    place("Cobweb_Wall_Large", x, y, AZ + 180, yaw, AT, collide=False)
note("note_telegram", "Newspaper_Single", 700, -380, AZ + 1, 50)
# ---- cellar
CE = D + "Cellar"
place("Barrel_Old", 100, 120, CZ, 0, CE)
place("Barrel_Tipped_Spilled", 200, -120, CZ, 60, CE)
place("Crate_Wood_Large", 950, 130, CZ, 10, CE)
place("Crate_Wood_Broken", 1560, -120, CZ, 80, CE)
place("Specimen_Jar_Shelf", 1150, 185, CZ, 180, CE)
place("Specimen_Jar_Shelf", 700, 185, CZ, 180, CE)
place("Chain_Hanging", 1000, -100, CZ + 141, 0, CE, collide=False)
place("Rat_Group", 1300, -150, CZ, 20, CE, collide=False)
place("Bucket_Rusty", 880, -150, CZ, 0, CE)
_furn = None
for _a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path("/Game/Fab/Urban_Australian_Desolation_Fireplace_Metal_Rusty", recursive=True):
    if str(_a.asset_class_path.asset_name) == "StaticMesh":
        _furn = _a.get_asset()
place(_furn or "Barrel_Old", 600, -545, CZ, 0, CE, name="Furnace", scale=1.5 if _furn else 1.0)
place("Lockers_Row_4_Dented", 300, -580, CZ, 0, CE)
place("Planks_Pile", 100, -400, CZ, 40, CE)
place("Cobweb_Wall_Large", 20, 0, CZ + 180, 90, CE, collide=False)
interact("WCUsable", "shelf", "Bookshelf_Tall", 1400, 182, CZ, 180, "Drag the shelf aside", (60, 22, 100), (0, 0, 110), scale=(1.22, 1.0, 1.0))
point("ShelfOpen", 1250, 170, CZ)
note("note_cellar", "Letters_Scattered", 950, 130, CZ + 81, 10, scale=0.8)
# ---- root cellar: where she is
RC = D + "Root"
place("Rocking_Chair", 1400, 520, CZ, 180, RC)
place("Candle_Melted_Puddle", 1300, 560, CZ, 0, RC, collide=False)
place("Barrel_Old", 1250, 560, CZ, 0, RC)
place("Chain_Pile", 1540, 560, CZ, 0, RC, collide=False)
interact("WCUsable", "place", None, 1400, 430, CZ + 4, 0, "Lay the keepsakes at her feet", (34, 26, 10), (0, 0, 8))
place("Music_Box_Closed", 1385, 430, CZ, 20, RC, tags=["Show_placed"], collide=False)
place(CYL, 1420, 425, CZ + 1, 0, RC, tags=["Show_placed"], collide=False, scale=(0.022, 0.022, 0.006), mats={0: "Gold"}, name="RingPlaced")
place("Chain_Pile", 1410, 450, CZ, 0, RC, tags=["Show_placed"], collide=False, scale=0.16, name="TagsPlaced")
for i, (x, y) in enumerate(((1330, 470), (1400, 455), (1470, 470))):
    interact("WCUsable", f"knot{i + 1}", None, x, y, CZ + 205, i * 80, "Cut the knot", (14, 14, 50), (0, 0, -45), tags=[f"Show_knot{i + 1}"])
    hair_cord(x, y, CZ + 328, 190 + i * 10, RC, tags=[f"Show_knot{i + 1}"], name=f"Knot_{i + 1}")
# her reminders to herself, from when she could still write them
note("note_rem1", "Newspaper_Single", 19, 110, GZ + 150, 0, scale=0.5, roll=90, grab=(6, 20, 22))
note("note_rem2", "Newspaper_Single", 1240, 583, GZ + 150, 0, scale=0.5, pitch=0, roll=90, grab=(20, 6, 22))
note("note_rem3", "Letters_Scattered", 420, 555, GZ + 96, 30, scale=0.6)
note("note_rem4", "Letters_Scattered", 1520, 150, UZ + 99, 80, scale=0.6)
note("note_rem5", "Newspaper_Single", 1250, -581, UZ + 120, 0, scale=0.45, roll=90, grab=(20, 6, 22))
log("dressing done")

# ================================================================== HER + her body
her_mesh = asset(G + "/Her/SK_Her", must=False)
info = json.load(open("C:/GameDev/Unreal/WellnessCheck/SourceArt/Her/export/her_info.json"))
if her_mesh:
    h = actors.spawn_actor_from_class(WC["WCEntity"], V(600, 0, -2000), R())
    h.set_actor_label("Her")
    body = h.get_editor_property("body")
    body.set_skeletal_mesh_asset(her_mesh)
    anims, speeds = {}, {}
    for c, d in info["clips"].items():
        a = asset(f"{G}/Her/A_Her_{c}", must=False)
        if a:
            anims[unreal.Name(c)] = a
            speeds[unreal.Name(c)] = float(d["speed"])
    h.set_editor_property("anims", anims)
    h.set_editor_property("anim_speeds", speeds)
    h.set_folder_path("House/Her")
    # the body in the root cellar: the same woman, long dead, in her chair
    b = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(1400, 540, CZ), R(180))
    b.set_actor_label("HerBody")
    bc = b.skeletal_mesh_component
    bc.set_skeletal_mesh_asset(her_mesh)
    bc.set_editor_property("lighting_channels", LC_IN)
    sit = asset(f"{G}/Her/A_Her_Sit", must=False)
    if sit:
        bc.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        ad = unreal.SingleAnimationPlayData()
        ad.set_editor_property("anim_to_play", sit)
        ad.set_editor_property("saved_position", 1.0)
        ad.set_editor_property("saved_play_rate", 0.0)
        ad.set_editor_property("saved_playing", False)
        ad.set_editor_property("saved_looping", False)
        bc.set_editor_property("animation_data", ad)
    dead = asset(G + "/Her/MI_HerDead", must=False)
    if dead:
        bc.set_material(0, dead)
    b.set_folder_path("House/Her")
else:
    log("WARNING: no SK_Her; she is not in the level")

# where she appears
point("Her_Peek", 215, 190, UZ, 0)
point("Her_PeekBack", 215, 345, UZ, 0)
point("Her_Hall0", 150, 60, GZ, 0)
point("Her_KitchenSeat", 1340, 430, GZ, 190)
point("Her_UpFar", 90, 100, UZ, 0)
point("Her_UpBack", 60, 100, UZ, 0)
point("Her_Under", RB_X, RB_EDGE - 60, UZ, 90)
point("Her_AtticFar", 800, 520, AZ, -90)
point("Her_SprintStart", 80, 110, GZ, 0)
point("Her_Fin0", 150, 60, CZ, 0)
point("Her_Fin1", 1050, 60, CZ, 0)
point("Her_Fin2", 1400, 250, CZ, 90)
point("P_CellarBottom", 300, -60, CZ + 92, 180)
point("FrontDoorPoint", -20, 0, GZ + 120)
point("Snd_UpstairsThump", 400, 400, UZ + 20)

# ================================================================== TRIGGERS
trigger("t_yard_edge", -2440, -2330, -1080, 1080, -40, 300)
trigger("t_foyer", 30, 330, -180, 180, GZ, GZ + 250)
trigger("t_living", 60, 760, -580, -230, GZ, GZ + 250)
trigger("t_dining", 60, 760, 230, 580, GZ, GZ + 250)
trigger("t_kitchen", 840, 1560, 230, 580, GZ, GZ + 250)
trigger("t_up_landing", 820, 1150, -180, 180, UZ, UZ + 250)
trigger("t_master", 60, 760, 240, 580, UZ, UZ + 250)
trigger("t_kids", 60, 760, -580, -240, UZ, UZ + 250)
trigger("t_cellar_shelf", 1250, 1560, -100, 180, CZ, CZ + 250)
trigger("t_root", 1230, 1570, 240, 580, CZ, CZ + 250)
trigger("t_cruiser", -1700, -1250, 40, 520, -40, 250)
trigger("t_up_corridor", 420, 700, 24, 184, UZ, UZ + 250)
trigger("t_sitting", 816, 1584, -584, -216, GZ, GZ + 250)
trigger("t_backhall", 2000, 2780, -180, 180, GZ, GZ + 250)
trigger("t_den", 1620, 2380, -580, -220, GZ, GZ + 250)
trigger("t_sickroom", 2020, 2780, 220, 580, GZ, GZ + 250)
trigger("t_pantry", 1620, 1980, 220, 580, GZ, GZ + 250)
trigger("t_bath_g", 2420, 2780, -580, -220, GZ, GZ + 250)
trigger("t_daniel", 1620, 2380, -580, -220, UZ, UZ + 250)
trigger("t_sewing", 2420, 2780, -580, -220, UZ, UZ + 250)
trigger("t_aide", 1620, 2380, 220, 580, UZ, UZ + 250)
trigger("t_bath2", 2420, 2780, 220, 580, UZ, UZ + 250)
trigger("t_up_ell", 1620, 2780, -180, 180, UZ, UZ + 250)
trigger("t_attic", 420, 1560, -560, 560, AZ, AZ + 250)
trigger("t_hall_mid", 900, 1500, -180, 180, GZ, GZ + 250)

# ================================================================== AUTO-PLAY / TOUR POINTS
for n, x, y, z, yaw in (("A_Porch", -150, 0, GZ, 0), ("A_Foyer", 220, 60, GZ, 0), ("A_Living", 250, -430, GZ, 300), ("A_Dining", 300, 300, GZ, 30),
                        ("A_Kitchen", 1000, 380, GZ, 20), ("A_BackDoor", 2700, 0, GZ, 0), ("A_Den", 2000, -380, GZ, 250), ("A_Sickroom", 2400, 380, GZ, 60), ("A_Pantry", 1800, 400, GZ, 60), ("A_BathG", 2600, -380, GZ, 250),
                        ("A_Daniel", 2000, -380, UZ, 250), ("A_Sewing", 2600, -380, UZ, 250), ("A_Aide", 2000, 380, UZ, 60), ("A_Bath2", 2600, 380, UZ, 60), ("A_UpEll", 1750, 0, UZ, 0), ("A_Sitting", 1250, -350, GZ, 200),
                        ("A_StairsTop", 900, 60, UZ, 160), ("A_Master", 380, 330, UZ, 30), ("A_Kids", 420, -330, UZ, 250),
                        ("A_Prayer", 1150, 330, UZ, 60), ("A_Attic", 760, -250, AZ, 250), ("A_CellarShelf", 1380, 60, CZ, 90),
                        ("A_Root", 1400, 330, CZ, 90), ("A_Cruiser", -1450, 260, -40, 180)):
    point(n, x, y, z, yaw, folder="Auto")
TOUR = [("road", -9000, 300, 60, 0), ("gate", -3300, 320, 60, -5), ("yard", -1900, -200, 52, 8), ("yard_side", -1200, -1500, 52, 50), ("yard_back", 3900, 1300, 52, 200),
        ("den", 1720, -250, 92, -35), ("den2", 2290, -470, 92, 150), ("bath_g", 2440, -240, 92, -50), ("pantry", 1640, 240, 92, 45), ("sickroom", 2040, 240, 92, 40), ("sickroom2", 2760, 560, 92, 220),
        ("hall_rear", 2700, 40, 92, 180), ("up_ell", 1640, 100, UZ + 92, 0), ("daniel", 1760, -250, UZ + 92, -40), ("daniel2", 2300, -300, UZ + 92, 200), ("sewing", 2440, -240, UZ + 92, -50),
        ("aide", 1700, 300, UZ + 92, 30), ("bath2", 2450, 250, UZ + 92, 45), ("yard_near", -900, 300, 52, -10), ("porch", -260, 100, 92, -20), ("foyer", 60, 100, 92, -5), ("hall_back", 1500, 100, 92, 180),
        ("living", 120, -260, 92, -50), ("living2", 720, -540, 92, 120), ("dining", 100, 260, 92, 40), ("kitchen", 880, 300, 92, 30), ("kitchen2", 1500, 520, 92, 215),
        ("sitting", 1000, -400, 92, -20), ("stairs_foot", 300, -88, 92, 0), ("up_landing", 900, 60, UZ + 92, 170), ("up_hall_front", 80, 100, UZ + 92, 0),
        ("master", 100, 260, UZ + 92, 40), ("kids", 100, -260, UZ + 92, -40), ("bath", 1350, -250, UZ + 92, -140), ("prayer", 880, 260, UZ + 92, 40),
        ("attic", 800, -100, AZ + 92, 90), ("attic2", 800, 100, AZ + 92, -90), ("cellar", 300, 0, CZ + 92, 0), ("cellar_wing", 200, -300, CZ + 92, -60),
        ("root", 1400, 280, CZ + 92, 90)]
for i, (n, x, y, z, yaw) in enumerate(TOUR):
    point(f"Tour_{i:02d}_{n}", x, y, z, yaw, tags=[f"Tour_{i:02d}_{n}", "Tour"], folder="Tour")

# ================================================================== PLAYER START, NAV, MENU CAMERA
ps = actors.spawn_actor_from_class(unreal.PlayerStart, V(-1440, 120, 60), R(0))
ps.set_actor_label("PlayerStart")
ps.set_folder_path("House/Gameplay")
nav = actors.spawn_actor_from_class(unreal.NavMeshBoundsVolume, V(-400, 0, 200), R())
nav.set_actor_scale3d(V(36.0, 13.0, 7.0))
nav.set_actor_label("NavBounds")
nav.set_folder_path("House/Gameplay")
cam = actors.spawn_actor_from_class(unreal.CameraActor, V(-2150, -620, 110), R(16, 9))
cam.set_actor_label("MenuCam")
tag(cam, ["MenuCam"])
cam.camera_component.set_editor_property("field_of_view", 62.0)
cam.set_folder_path("House/Gameplay")

exec(open(os.path.join(HERE, "nav.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "decay.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "ell.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "looks.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "watchers.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "settle.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "lighting.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "memory.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "switches.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "forest.py"), encoding="utf-8").read())

if not level_editor.save_current_level():
    raise RuntimeError("could not save " + MAP)
log(f"DONE {count} -> {MAP}")
