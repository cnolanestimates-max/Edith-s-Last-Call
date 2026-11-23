"""Camera option A on the saved House map (Cheyenne, 2026-11-23): the grades' motion blur from 0 to 0.5 (max 3), so fast
turns smear a little.  The walk itself is in WCCharacter.cpp (wc.CameraFeel 2.5).  lighting.py builds it this way now.
apply_polish.py step "camera_a"."""
import unreal as u


def dress():
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    n = 0
    for a in sub.get_all_level_actors():
        if isinstance(a, u.PostProcessVolume) and a.get_actor_label() in ("Grade_Night", "Grade_Dawn"):
            st = a.settings
            for prop, val in (("motion_blur_amount", 0.5), ("motion_blur_max", 3.0)):
                st.set_editor_property("override_" + prop, True)
                st.set_editor_property(prop, val)
            a.set_editor_property("settings", st)
            n += 1
    u.log_warning(f"WC_POLISH camera A: motion blur on {n} grades")
