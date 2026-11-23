"""Lighting option B on the saved House map (Cheyenne picked it, 2026-11-23: "the dimmer still"): thicker air, the moonlight
through the windows a little dimmer and barely lighting the air, a little more bounce light.  lighting.py builds it this
way now; this sets the same values (absolute, so it is safe to run again) on a map built before.  apply_polish.py step
"lighting_b"."""
import unreal as u


def dress():
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    n = 0
    for a in sub.get_all_level_actors():
        lab = a.get_actor_label()
        if isinstance(a, u.ExponentialHeightFog) and lab == "Fog":
            fc = a.component
            fc.set_editor_property("volumetric_fog_scattering_distribution", 0.9)
            fc.set_editor_property("volumetric_fog_extinction_scale", 2.0)
            n += 1
        elif isinstance(a, u.PostProcessVolume) and lab == "Grade_Night":
            st = a.settings
            for prop, val in (("indirect_lighting_intensity", 1.1), ("lumen_scene_lighting_quality", 2.0), ("lumen_final_gather_quality", 2.0),
                              ("lumen_scene_detail", 2.0), ("lumen_reflection_quality", 2.0)):
                st.set_editor_property("override_" + prop, True)
                st.set_editor_property(prop, val)
            a.set_editor_property("settings", st)
            n += 1
        elif isinstance(a, u.SpotLight) and lab.endswith("_moon") and a.actor_has_tag("Hide_dawn"):
            lc = a.spot_light_component
            if lc.intensity > 1900.0:                                  # (still at the old 2600: lower it once)
                lc.set_intensity(lc.intensity * 0.7)
            lc.set_editor_property("volumetric_scattering_intensity", 0.525)
            n += 1
    u.log_warning(f"WC_POLISH lighting B: {n} actors set")
