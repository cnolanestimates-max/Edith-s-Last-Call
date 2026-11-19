# Lighting, atmosphere and post for the House map.  exec'd by build_house.py (shares its helpers).
#
# The rule: the power was cut off a year ago, and the lights burn anyway (switches.py), dim and yellow and not for long.  What you see by is (1) your flashlight, (2) thin blades of moonlight through
# the boarded windows, (3) the cruiser's lights on the front of the house, (4) a few candles that should not be lit.
# Exposure is fixed so darkness stays dark instead of the camera "helping".
ENV = "Environment"

# ---------------------------------------------------------------- sky, moon, dawn sun
atm = actors.spawn_actor_from_class(unreal.SkyAtmosphere, V(0, 0, 0), R())
atm.set_actor_label("SkyAtmosphere")
atm.set_folder_path("House/" + ENV)

moon = actors.spawn_actor_from_class(unreal.DirectionalLight, V(0, 0, 2000), R(205, -38))
moon.set_actor_label("Moon")
mc = moon.light_component
mc.set_mobility(unreal.ComponentMobility.MOVABLE)
mc.set_intensity(float(os.environ.get("WC_MOON", "2.4")))
mc.set_light_color(unreal.LinearColor(0.52, 0.64, 1.0, 1.0))
mc.set_editor_property("atmosphere_sun_light", True)
mc.set_editor_property("volumetric_scattering_intensity", 1.6)
mc.set_cast_shadows(True)
tag(moon, ["Hide_dawn"])
moon.set_folder_path("House/" + ENV)

sun = actors.spawn_actor_from_class(unreal.DirectionalLight, V(0, 0, 2100), R(8, -7))
sun.set_actor_label("DawnSun")
sc = sun.light_component
sc.set_mobility(unreal.ComponentMobility.MOVABLE)
sc.set_intensity(170.0)
sc.set_light_color(unreal.LinearColor(0.78, 0.74, 0.84, 1.0))
sc.set_editor_property("atmosphere_sun_light", True)
sc.set_editor_property("volumetric_scattering_intensity", 0.8)
tag(sun, ["Show_dawn"])
sun.set_folder_path("House/" + ENV)

sky = actors.spawn_actor_from_class(unreal.SkyLight, V(0, 0, 1500), R())
sky.set_actor_label("SkyLight")
sk = sky.light_component
sk.set_mobility(unreal.ComponentMobility.MOVABLE)
sk.set_editor_property("real_time_capture", True)
sk.set_intensity(float(os.environ.get("WC_SKY", "1.7")))
sky.set_folder_path("House/" + ENV)

fog = actors.spawn_actor_from_class(unreal.ExponentialHeightFog, V(0, 0, -40), R())
fog.set_actor_label("Fog")
fog.set_folder_path("House/" + ENV)
fc = fog.component
for setter, val in (("set_fog_density", 0.028), ("set_fog_height_falloff", 0.06),
                    ("set_fog_inscattering_color", unreal.LinearColor(0.02, 0.026, 0.036, 1.0)),
                    ("set_volumetric_fog", True), ("set_start_distance", 0.0)):
    try:
        getattr(fc, setter)(val)
    except Exception as exc:
        log(f"fog {setter}: {exc}")
for prop, val in (("volumetric_fog_scattering_distribution", 0.6), ("volumetric_fog_extinction_scale", 1.6),
                  ("volumetric_fog_albedo", unreal.Color(214, 218, 226, 255)), ("volumetric_fog_distance", 5000.0),
                  ("volumetric_fog_start_distance", 0.0), ("volumetric_fog_near_fade_in_distance", 0.0),
                  ("fog_max_opacity", 0.96)):
    try:
        fc.set_editor_property(prop, val)
    except Exception as exc:
        log(f"fog {prop}: {exc}")


# ---------------------------------------------------------------- grading
def grade(name, ev, extra, priority=0.0, tags=None, enabled=True):
    ppv = actors.spawn_actor_from_class(unreal.PostProcessVolume, V(0, 0, 100), R())
    ppv.set_actor_label(name)
    ppv.set_folder_path("House/" + ENV)
    ppv.set_editor_property("unbound", True)
    ppv.set_editor_property("priority", priority)
    ppv.set_editor_property("enabled", enabled)
    st = ppv.settings
    base = [("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL), ("auto_exposure_bias", ev),
            ("auto_exposure_apply_physical_camera_exposure", False),
            ("lens_flare_intensity", 0.0), ("motion_blur_amount", 0.0)]
    for prop, val in base + extra:
        try:
            st.set_editor_property("override_" + prop, True)
            st.set_editor_property(prop, val)
        except Exception as exc:
            log(f"post {name} {prop}: {exc}")
    ppv.set_editor_property("settings", st)
    tag(ppv, tags or [])
    return ppv


NIGHT_EV = float(os.environ.get("WC_EV", "-5.0"))
grade("Grade_Night", NIGHT_EV, [
    ("vignette_intensity", 0.55), ("film_grain_intensity", 0.18), ("bloom_intensity", 0.75),
    ("scene_fringe_intensity", 0.25), ("color_saturation", unreal.Vector4(0.80, 0.84, 0.90, 1.0)),
    ("color_contrast", unreal.Vector4(1.08, 1.08, 1.08, 1.0)), ("color_gain_shadows", unreal.Vector4(0.90, 0.98, 1.08, 1.0)),
    ("color_gamma_midtones", unreal.Vector4(0.98, 1.0, 1.02, 1.0)), ("white_temp", 6800.0),
    ("ambient_occlusion_intensity", 0.7), ("local_exposure_shadow_contrast_scale", 0.9)])
grade("Grade_Dawn", NIGHT_EV + 2.4, [          # the first grey before sunrise (Cheyenne: "barely breaking morning, not bright sun")
    ("vignette_intensity", 0.45), ("film_grain_intensity", 0.15), ("bloom_intensity", 0.3),
    ("color_saturation", unreal.Vector4(0.72, 0.74, 0.8, 1.0)), ("white_temp", 6900.0)], priority=5.0, tags=["PP_Dawn"], enabled=False)

# ---------------------------------------------------------------- moonlight through the boards (and warm dawn light later)
def shaft(name, x, y, z, yaw, pitch=-15.0):
    # The lamp sits IN the window opening (not out in the yard), so the lit fog starts at the boards: from outside the
    # window stays dark, inside the light fans down through the gaps.
    x += math.cos(math.radians(yaw)) * 78.0
    y += math.sin(math.radians(yaw)) * 78.0
    z -= 42.0
    m_ = light_spot(name + "_moon", x, y, z, yaw, pitch, 9000, (0.5, 0.63, 1.0), 900, 36, 62, "Lights/Windows", tags=["Hide_dawn"], shadows=True, vol=2.0)
    m_.light_component.set_editor_property("lighting_channels", LC_SHAFT)
    light_spot(name + "_dawn", x, y, z, yaw, pitch + 4, 9000, (0.72, 0.76, 0.92), 1100, 36, 62, "Lights/Windows", tags=["Show_dawn"], shadows=True, vol=2.4)


for z, f in ((GZ, "G"), (UZ, "U")):
    shaft(f"W_{f}_living", -120, -400, z + 250, 0)
    if z == GZ:
        shaft(f"W_{f}_dining", -120, 400, z + 250, 0)
# the one lit window: a lamp in the master bedroom that goes out when he knocks
light_point("Lamp_Welcome", 62, 400, UZ + 175, 150, (1.0, 0.62, 0.3), 520, "Lights/Lamps", tags=["Flicker", "L_Welcome"], shadows=True, vol=1.6, source=3.0)
shaft("W_U_hall", -120, 0, UZ + 250, 0)
shaft("W_G_kitchen", 1000, 730, GZ + 250, -90)
shaft("W_G_sitting", 1000, -730, GZ + 250, 90)
shaft("W_U_bath", 1000, -730, UZ + 250, 90)
shaft("W_U_master", 200, 730, UZ + 250, -90)
shaft("W_G_den", 1800, -730, GZ + 250, 90)
shaft("W_G_bath", 2600, -730, GZ + 250, 90)
shaft("W_G_pantry", 1800, 730, GZ + 250, -90)
shaft("W_G_sick", 2600, 730, GZ + 250, -90)
shaft("W_U_daniel", 1800, -730, UZ + 250, 90)
shaft("W_U_sewing", 2600, -730, UZ + 250, 90)
shaft("W_U_aide", 1800, 730, UZ + 250, -90)
shaft("W_U_bath2", 2600, 730, UZ + 250, -90)
shaft("W_G_back", XB + 120, 400, GZ + 250, 180)
shaft("W_U_back", XB + 120, 0, UZ + 250, 180)

# ---------------------------------------------------------------- candles that should not be lit
def candle(name, x, y, z, lumens=28.0, radius=420.0, tags=("Flicker",)):
    light_point(name, x, y, z, lumens, (1.0, 0.56, 0.24), radius, "Lights/Candles", tags=list(tags), shadows=True, vol=1.2, source=1.5)


candle("Candle_Altar", 1150, 548, UZ + 122)
candle("Candle_Altar2", 1262, 552, UZ + 132, 18)
candle("Candle_Floor1", 1060, 300, UZ + 40, 22)
candle("Candle_Floor2", 1340, 500, UZ + 40, 22)
candle("Candle_Root", 1300, 556, CZ + 26, 16, 380)
light_point("FurnaceGlow", 600, -500, CZ + 95, 30, (1.0, 0.3, 0.08), 520, "Lights/Candles", tags=["Flicker", "Hide_dawn"], shadows=True, vol=1.5, source=8)
log("lighting done")
