"""Cheyenne 21:13-21:15: (1) the stairs were solid kit wedges stacked in one tower, so the flight above showed as a flat floor
over the flight below: build real open flights (treads, risers, stringers, a sloped soffit).  (2) No window may look lit from
outside: every window gets dark glass in front of its moon lamp; one upstairs window keeps a warm lamp that dies when he knocks."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "build_house.py", [
    ('''for i, z0 in enumerate((CZ, GZ, UZ)):
    place("Stairs_Straight_Storey", 600, -88, z0, STAIR_YAW, "Shell/Stairs", name=f"Stairs_{i}", collide=False)
    a = actors.spawn_actor_from_class(unreal.StaticMeshActor, V(600, -88, z0 + RISE / 2 - 4), R(0, RANG, 0))''',
     '''M_TREAD = surf("WoodDark", "MI_WoodDark")
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
    a = actors.spawn_actor_from_class(unreal.StaticMeshActor, V(600, -88, z0 + RISE / 2 - 4), R(0, RANG, 0))'''),
])
edit(L + "exterior.py", [
    ('''    piece("WinJambR_" + key, 60, 72, 93, 262, 7, M_TRIM)''', '''piece("WinJambR_" + key, 60, 72, 93, 262, 7, M_TRIM)
    if not (face == "-x" and y == 400 and z == UZ):
        # dark glass: nothing behind a window shows from the yard (the one exception is the lamp she leaves burning)
        piece("WinGlass_" + key, -61, 61, 92, 263, 2.2, "WC:M_Black", d0=5.5)'''),
    ('''# boards nailed over two upstairs windows from outside, long ago''', '''# the two windows without casings (behind the turret, beside the bay) get their dark glass too
for (gx, gy, gz) in ((200, -600, UZ),):
    box(f"WinGlassX_{gx}_{int(gz)}", gx - 61, gx + 61, gy - 52, gy - 49.5, gz + 92, gz + 263, "WC:M_Black", EX + "/Windows", collide=False, shadow=False)
# boards nailed over two upstairs windows from outside, long ago'''),
    ('''ext("Window_Boarded_Cross", -48, 400, UZ + 95, 90, collide=False)''', '''ext("Window_Boarded_Cross", -54, -400, UZ + 95, 90, collide=False)'''),
])
edit(L + "lighting.py", [
    ('''for z, f in ((GZ, "G"), (UZ, "U")):
    shaft(f"W_{f}_living", -120, -400, z + 250, 0)
    shaft(f"W_{f}_dining", -120, 400, z + 250, 0)''', '''for z, f in ((GZ, "G"), (UZ, "U")):
    shaft(f"W_{f}_living", -120, -400, z + 250, 0)
    if z == GZ:
        shaft(f"W_{f}_dining", -120, 400, z + 250, 0)
# the one lit window: a lamp in the master bedroom that goes out when he knocks
light_point("Lamp_Welcome", 62, 400, UZ + 175, 150, (1.0, 0.62, 0.3), 520, "Lights/Lamps", tags=["Flicker", "L_Welcome", "Hide_dawn"], shadows=True, vol=1.6, source=3.0)'''),
])
print("ok")
