"""Level fixes after the first tour of the big house: no lit windows from outside (moon shafts only light the inside),
a little more moon outside, tour points out of the furniture, furnace, cobweb, textures on a few bare boxes, the body faces the door."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"

edit(L + "build_house.py", [
    # lighting channels: everything indoors is on channels 0+1; the moon shafts light channel 1 only
    ('''CUBE = asset("/Engine/BasicShapes/Cube.Cube")''', '''LC_IN = unreal.LightingChannels()
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


CUBE = asset("/Engine/BasicShapes/Cube.Cube")'''),
    ('''    tag(a, tags)
    a.set_folder_path("House/" + folder)
    count["mesh"] += 1
    return a


def place(''', '''    tag(a, tags)
    indoor(c, folder)
    a.set_folder_path("House/" + folder)
    count["mesh"] += 1
    return a


def place('''),
    ('''    c.set_editor_property("can_ever_affect_navigation", collide and scale == 1.0 and "Hide_" not in str(tags) and "Show_" not in str(tags))
    tag(a, tags)''', '''    c.set_editor_property("can_ever_affect_navigation", collide and scale == 1.0 and "Hide_" not in str(tags) and "Show_" not in str(tags))
    indoor(c, folder)
    tag(a, tags)'''),
    ('''    mc.set_relative_location(V(56.5, 0, 0), False, False)
    restyle(mc)''', '''    mc.set_relative_location(V(56.5, 0, 0), False, False)
    mc.set_editor_property("lighting_channels", LC_IN)
    restyle(mc)'''),
    ('''    mc = a.get_editor_property("mesh")
    if mesh is not None:''', '''    mc = a.get_editor_property("mesh")
    mc.set_editor_property("lighting_channels", LC_IN)
    if mesh is not None:'''),
    ('''M_PORCH = surf("WoodBleached", "MI_PorchBoards")''', '''M_PORCH = surf("WoodBleached", "MI_PorchBoards")
M_WOODV = surf("WoodVictorian", "MI_WoodTrim")
M_WOODR = surf("WoodRotten", "MI_WoodRotten")'''),
    ('''box("TowerLintelG", 392, 408, -200, 16, 250, 330, "WoodVictorian", "Shell/Ground")''', '''box("TowerLintelG", 392, 408, -200, 16, 250, 330, M_WOODV, "Shell/Ground")'''),
    ('''box("TowerLintelU", 792, 808, -200, 16, UZ + 250, UZ + 330, "WoodVictorian", "Shell/Upper")''', '''box("TowerLintelU", 792, 808, -200, 16, UZ + 250, UZ + 330, M_WOODV, "Shell/Upper")'''),
    ('''box("AtticStairRailA", SX0, SX1, SY1, SY1 + 10, AZ, AZ + 100, "WoodVictorian", "Shell/Attic")''', '''box("AtticStairRailA", SX0, SX1, SY1, SY1 + 10, AZ, AZ + 100, M_WOODV, "Shell/Attic")'''),
    ('''box("AtticStairRailB", SX0 - 10, SX0, SY0 - 16, SY1 + 10, AZ, AZ + 100, "WoodVictorian", "Shell/Attic")''', '''box("AtticStairRailB", SX0 - 10, SX0, SY0 - 16, SY1 + 10, AZ, AZ + 100, M_WOODV, "Shell/Attic")'''),
    ('''box(f"CellarPost_{x}", x - 9, x + 9, 100, 118, CZ, GZ - 20, "WoodRotten", C)''', '''box(f"CellarPost_{x}", x - 9, x + 9, 100, 118, CZ, GZ - 20, M_WOODR, C)'''),
    ('''for x, y, yaw in ((700, -590, 0), (900, 590, 180), (800, 0, 0)):''', '''for x, y, yaw in ((700, -590, 0), (900, 590, 180)):'''),
    ('''place("Fire_Barrel", 600, -500, CZ, 0, CE, name="Furnace")''', '''_furn = None
for _a in unreal.AssetRegistryHelpers.get_asset_registry().get_assets_by_path("/Game/Fab/Urban_Australian_Desolation_Fireplace_Metal_Rusty", recursive=True):
    if str(_a.asset_class_path.asset_name) == "StaticMesh":
        _furn = _a.get_asset()
place(_furn or "Barrel_Old", 600, -545, CZ, 0, CE, name="Furnace", scale=1.5 if _furn else 1.0)'''),
    ('''b = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(1400, 556, CZ), R(0))''', '''b = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(1400, 540, CZ), R(180))'''),
    ('''("den", 1640, -240, 92, -40), ("den2", 2360, -560, 92, 140),''', '''("den", 1720, -250, 92, -35), ("den2", 2290, -470, 92, 150),'''),
    ('''("hall_rear", 2760, 100, 92, 180),''', '''("hall_rear", 2700, 40, 92, 180),'''),
    ('''("daniel", 1640, -240, UZ + 92, -40), ("daniel2", 2360, -560, UZ + 92, 140),''', '''("daniel", 1760, -250, UZ + 92, -40), ("daniel2", 2300, -300, UZ + 92, 200),'''),
    ('''("aide", 1640, 240, UZ + 92, 40), ("bath2", 2440, 240, UZ + 92, 45),''', '''("aide", 1700, 300, UZ + 92, 30), ("bath2", 2450, 250, UZ + 92, 45),'''),
])
edit(L + "ell.py", [
    ('''place("Laundry_Cart", 2470, 260, UZ, 20, B2)''', '''place("Laundry_Cart", 2740, 540, UZ, 20, B2)'''),
])
edit(L + "exterior.py", [
    ('''box("AtticKneeFront", 0, 14, -600, 600, AZ, AZ + 12, "WoodVictorian", EX, collide=False)''', '''box("AtticKneeFront", 0, 14, -600, 600, AZ, AZ + 12, M_TRIM, EX, collide=False)'''),
])
edit(L + "lighting.py", [
    ('''mc.set_intensity(0.9)''', '''mc.set_intensity(float(os.environ.get("WC_MOON", "2.4")))'''),
    ('''sk.set_intensity(1.0)''', '''sk.set_intensity(float(os.environ.get("WC_SKY", "1.7")))'''),
    ('''    light_spot(name + "_moon", x, y, z, yaw, pitch, 1900, (0.5, 0.63, 1.0), 950, 10, 26, "Lights/Windows", tags=["Hide_dawn"], shadows=True, vol=2.2)''',
     '''    m_ = light_spot(name + "_moon", x, y, z, yaw, pitch, 1900, (0.5, 0.63, 1.0), 950, 10, 26, "Lights/Windows", tags=["Hide_dawn"], shadows=True, vol=2.2)
    m_.light_component.set_editor_property("lighting_channels", LC_SHAFT)'''),
])
print("ok")
