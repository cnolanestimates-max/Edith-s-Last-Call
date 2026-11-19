# Her drawings, the Company's silhouette, and the three memories shown when she has hold of you.
# exec'd by build_house.py after watchers.py (shares its helpers).
MF = "Memory"
HER_SK = asset(G + "/Her/SK_Her", must=False)
VOID = asset(G + "/Materials/M_Void", must=False)


# ---------------------------------------------------------------- drawings (PIL-made, imported by step "drawings")
def drawing(n, x, y, z, face=None, w=30.0, h=38.0, yaw=0.0):
    p = f"{G}/Drawings/MI_Draw_{n}"
    if not eal.does_asset_exist(p):
        return None
    if face is None:      # lying on the floor
        a = box(f"Drawing_{n}_{int(x)}_{int(y)}", x - w / 2, x + w / 2, y - h / 2, y + h / 2, z, z + 0.3, "WC:M_Paper", "Dressing/Drawings", collide=False, shadow=False, yaw=yaw)
    else:
        dx, dy = {"x+": (1, 0), "x-": (-1, 0), "y+": (0, 1), "y-": (0, -1)}[face]
        if dx:
            a = box(f"Drawing_{n}_{int(x)}_{int(y)}", min(x, x + dx * 0.4), max(x, x + dx * 0.4), y - w / 2, y + w / 2, z - h / 2, z + h / 2, "WC:M_Paper", "Dressing/Drawings", collide=False, shadow=False, roll=yaw)
        else:
            a = box(f"Drawing_{n}_{int(x)}_{int(y)}", x - w / 2, x + w / 2, min(y, y + dy * 0.4), max(y, y + dy * 0.4), z - h / 2, z + h / 2, "WC:M_Paper", "Dressing/Drawings", collide=False, shadow=False, pitch=yaw)
    a.static_mesh_component.set_material(0, asset(p))
    return a


for i, n in enumerate((1, 2, 3, 4, 5, 6)):                         # the wall of her sitting room
    drawing(n, 816.5, -548 + i * 46, GZ + (138 if i % 2 == 0 else 186), "x+", yaw=(-4, 3, 5, -2, 4, -5)[i])
drawing(3, 300, 583.5, GZ + 150, "y-", yaw=3)                      # dining room: SUPPER FOR 2
drawing(5, 2480, 583.5, GZ + 170, "y-", yaw=-4)                    # over the sickroom bed: HE NEVER LEVES
drawing(4, 2420, 583.5, GZ + 160, "y-", yaw=5)
drawing(2, 2200, -183.5, UZ + 140, "y+", yaw=-3)                   # upstairs rear hall
drawing(1, 470, -330, UZ + 0.6, None, yaw=25)                      # on Ruth's floor
drawing(6, 1080, 470, UZ + 0.6, None, yaw=-40)                     # on the prayer-room floor
drawing(1, 1305, 520, GZ + 96, None, w=22, h=28, yaw=15)           # on the kitchen table


# ---------------------------------------------------------------- the Company: a black shape, seen a few times after the first sight of her
for wid, x, y, z, yaw in (("company_uprear", 2745, 0, UZ, 180), ("company_attic", 1480, -470, AZ, 150), ("company_cellar", 720, -520, CZ, 110), ("company_sick", 2745, 555, GZ, 215)):
    watcher(wid, x, y, z, yaw, 0.0, 2, 5.2)


# ---------------------------------------------------------------- memories (hidden until a grab shows one)
def figure(name, x, y, z, yaw, scale, clip, group, void=False, at=1.0):
    """A person in a memory: her own model at human size (or a black outline of it), held in one pose."""
    if not HER_SK:
        return None
    a = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(x, y, z), R(yaw - 90.0))
    a.set_actor_label(name)
    c = a.skeletal_mesh_component
    c.set_skeletal_mesh_asset(HER_SK)
    a.set_actor_scale3d(V(scale, scale, scale))
    seq = asset(f"{G}/Her/A_Her_{clip}", must=False)
    if seq:
        c.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        ad = unreal.SingleAnimationPlayData()
        ad.set_editor_property("anim_to_play", seq)
        ad.set_editor_property("saved_position", at)
        ad.set_editor_property("saved_play_rate", 0.0)
        ad.set_editor_property("saved_playing", False)
        c.set_editor_property("animation_data", ad)
    if void and VOID:
        for i in range(len(c.get_materials())):
            c.set_material(i, VOID)
    c.set_collision_profile_name("NoCollision")
    c.set_editor_property("lighting_channels", LC_IN)
    a.set_actor_hidden_in_game(True)
    tag(a, [group])
    a.set_folder_path("House/" + MF)
    return a


def smoke_man(name, x, y, z, yaw, tall, group):
    """The Company: black smoke in the shape of a man (AWCSmokeMan), hidden until the story shows it."""
    a = actors.spawn_actor_from_class(WC["WCSmokeMan"], V(x, y, z), R(yaw))
    a.set_actor_label(name)
    a.set_editor_property("tall", float(tall))
    a.set_actor_hidden_in_game(True)
    tag(a, [group])
    a.set_folder_path("House/" + MF)
    return a


def mem_light(name, x, y, z, lumens, group, col=(1.0, 0.78, 0.5), radius=900.0):
    a = light_point(name, x, y, z, lumens, col, radius, MF, tags=[group], shadows=True, vol=1.4, source=6.0)
    a.light_component.set_visibility(False)
    return a


def mem_cam(group, x, y, z, yaw, pitch, fov=58.0):
    c_ = actors.spawn_actor_from_class(unreal.CameraActor, V(x, y, z), R(yaw, pitch))
    c_.set_actor_label("Cam_" + group)
    tag(c_, ["Cam_" + group])
    c_.camera_component.set_editor_property("field_of_view", fov)
    c_.camera_component.set_editor_property("constrain_aspect_ratio", False)
    c_.set_folder_path("House/" + MF)


def mem_prop(mesh, x, y, z, yaw, group, **kw):
    a = place(mesh, x, y, z, yaw, MF, tags=[group], collide=False, **kw)
    a.set_actor_hidden_in_game(True)
    return a


# 1. Thanksgiving: the last time anyone came.  The front door stands open on daylight; they are already on the porch.
a = box("Mem1_Daylight", 17, 19, -62, 62, GZ, GZ + 214, "WC:M_GlowWarm", MF, collide=False, shadow=False, tags=["Mem1"])
a.set_actor_hidden_in_game(True)
figure("Mem1_Edith", 250, 10, GZ, 180, 0.60, "Idle", "Mem1", at=2.0)
figure("Mem1_Ruth", 70, -18, GZ, 180, 0.62, "Idle", "Mem1", void=True, at=4.0)
figure("Mem1_Man", 48, 26, GZ, 180, 0.66, "Idle", "Mem1", void=True, at=6.0)
mem_light("Mem1_Sun", 60, 0, GZ + 190, 11000, "Mem1", (1.0, 0.86, 0.66), 1300)
mem_light("Mem1_Fill", 520, 60, GZ + 240, 5000, "Mem1")
mem_cam("Mem1", 640, 96, GZ + 150, 186, -4)

# 2. The attic: her grandmother's book, under Danny's things.
mem_prop("Crate_Wood_Small", 905, -380, AZ, 20, "Mem2")
figure("Mem2_Edith", 905, -380, AZ + 16, 250, 0.60, "Sit", "Mem2")
mem_prop("Book_Open_Pages", 842, -402, AZ + 38, 60, "Mem2")
mem_prop("Lantern_Hurricane", 850, -330, AZ, 0, "Mem2")
mem_light("Mem2_Lantern", 850, -330, AZ + 40, 9000, "Mem2", (1.0, 0.7, 0.38), 700)
mem_cam("Mem2", 1090, -250, AZ + 118, 215, -9)

# 3. The ninth: she asks, and something comes to stand in the corner where the lamp does not reach.
mem_prop("Rocking_Chair", 1200, 400, UZ, 150, "Mem3")
figure("Mem3_Edith", 1200, 400, UZ + 14, 150, 0.60, "Sit", "Mem3")
smoke_man("Mem3_Company", 1520, 545, UZ, 205, 290, "Mem3")
mem_light("Mem3_Candles", 1200, 380, UZ + 60, 7000, "Mem3", (1.0, 0.62, 0.3), 620)
mem_cam("Mem3", 905, 265, UZ + 150, 24, -7)

# the look of a memory: warm, washed, bright, soft
grade("Grade_Memory", NIGHT_EV + 2.5, [
    ("vignette_intensity", 0.9), ("film_grain_intensity", 0.5), ("bloom_intensity", 1.6),
    ("color_saturation", unreal.Vector4(0.55, 0.5, 0.42, 1.0)), ("color_gain", unreal.Vector4(1.12, 1.0, 0.82, 1.0)),
    ("white_temp", 5200.0), ("scene_fringe_intensity", 1.2)], priority=9.0, tags=["PP_Memory"], enabled=False)

# her grandmother's book itself, where she found it: on the attic floor by the footlocker
note("note_wrenbook", "Book_Open_Pages", 842, -402, AZ + 1, 60, grab=(22, 22, 12))
log("memory: drawings, 4 silhouettes, 3 memories")
