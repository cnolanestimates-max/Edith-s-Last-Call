"""Unreal (headless, read-only): list every actor in the House map with its mesh, place, size and collision, to
Saved/Outdoors/survey.json.  Used by the outdoor polish pass to see what is in the yard and the forest."""
import json
import unreal as u

le = u.get_editor_subsystem(u.LevelEditorSubsystem)
if not le.load_level("/Game/WC/Maps/House"):
    raise RuntimeError("could not open the House map")
sub = u.get_editor_subsystem(u.EditorActorSubsystem)
sm = u.get_editor_subsystem(u.StaticMeshEditorSubsystem)
rows = []
for a in sub.get_all_level_actors():
    r = {"label": a.get_actor_label(), "cls": a.get_class().get_name(), "folder": str(a.get_folder_path()),
         "tags": [str(t) for t in a.tags]}
    l = a.get_actor_location(); s = a.get_actor_scale3d(); ro = a.get_actor_rotation()
    r["loc"] = [round(l.x, 1), round(l.y, 1), round(l.z, 1)]
    r["scale"] = [round(s.x, 3), round(s.y, 3), round(s.z, 3)]
    r["rot"] = [round(ro.roll, 1), round(ro.pitch, 1), round(ro.yaw, 1)]
    o, e = a.get_actor_bounds(False)
    r["ext"] = [round(e.x, 1), round(e.y, 1), round(e.z, 1)]
    r["org"] = [round(o.x, 1), round(o.y, 1), round(o.z, 1)]
    r["hidden"] = bool(a.is_hidden_ed()) or bool(a.get_editor_property("hidden"))
    if isinstance(a, u.StaticMeshActor):
        c = a.static_mesh_component
        m = c.static_mesh
        r["mesh"] = m.get_path_name() if m else ""
        r["coll"] = str(c.get_collision_profile_name())
        r["mats"] = [x.get_name() if x else "" for x in c.get_materials()]
        if m:
            bs = m.get_editor_property("body_setup")
            try:
                r["simple"] = u.EditorStaticMeshLibrary.get_simple_collision_count(m)
            except Exception:
                r["simple"] = -1
            try:
                r["tris"] = m.get_num_triangles(0)
            except Exception:
                pass
            r["trace"] = str(bs.get_editor_property("collision_trace_flag")) if bs else ""
    elif isinstance(a, u.SkeletalMeshActor):
        m = a.skeletal_mesh_component.skeletal_mesh_asset
        r["mesh"] = m.get_path_name() if m else ""
    else:
        ism = a.get_components_by_class(u.InstancedStaticMeshComponent)
        if ism:
            r["ism"] = [[c.static_mesh.get_path_name() if c.static_mesh else "", c.get_instance_count(), str(c.get_collision_profile_name())] for c in ism]
    rows.append(r)
json.dump(rows, open("C:/GameDev/Unreal/WellnessCheck/Saved/Outdoors/survey.json", "w"))
u.log_warning(f"WC_SURVEY {len(rows)} actors")
