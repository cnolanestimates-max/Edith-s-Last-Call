"""Read-only: list what blocks the player around the six snag spots from the 2026-11-23 bot playthrough.
UnrealEditor-Cmd WellnessCheck.uproject -run=pythonscript -script=<this> -unattended -nosplash  (prints WC_SNAG lines)"""
import unreal as u

REGIONS = {   # name: (x0, x1, y0, y1, z0, z1)
    "bath_g": (2400, 2800, -600, -140, -20, 250),
    "up_bath": (1150, 1500, -600, -250, 330, 600),
    "piano": (0, 320, -560, -250, -20, 250),
    "master_bedside": (380, 820, 180, 620, 330, 600),
    "attic_trunk": (560, 1000, -560, -100, 680, 950),
    "sewing": (2400, 3400, -620, -140, 330, 600),
}

le = u.get_editor_subsystem(u.LevelEditorSubsystem)
if not le.load_level("/Game/WC/Maps/House"):
    raise RuntimeError("could not open the House map")
sub = u.get_editor_subsystem(u.EditorActorSubsystem)
for a in sub.get_all_level_actors():
    o, e = a.get_actor_bounds(True)
    if e.x > 2000 or e.y > 2000:
        continue
    for name, (x0, x1, y0, y1, z0, z1) in REGIONS.items():
        if x0 <= o.x <= x1 and y0 <= o.y <= y1 and z0 <= o.z <= z1:
            comps = a.get_components_by_class(u.PrimitiveComponent)
            blocks = [c for c in comps if c.get_collision_enabled() != u.CollisionEnabled.NO_COLLISION
                      and c.get_collision_response_to_channel(u.CollisionChannel.ECC_PAWN) == u.CollisionResponseType.ECR_BLOCK]
            if not blocks:
                continue
            mesh = ""
            if isinstance(a, u.StaticMeshActor) and a.static_mesh_component.static_mesh:
                mesh = a.static_mesh_component.static_mesh.get_name()
            r = a.get_actor_rotation()
            u.log_warning(f"WC_SNAG {name} | {a.get_actor_label()} | {mesh} | loc ({a.get_actor_location().x:.0f},{a.get_actor_location().y:.0f},{a.get_actor_location().z:.0f}) yaw {r.yaw:.0f} "
                          f"| box x {o.x - e.x:.0f}..{o.x + e.x:.0f} y {o.y - e.y:.0f}..{o.y + e.y:.0f} z {o.z - e.z:.0f}..{o.z + e.z:.0f} | tags {[str(t) for t in a.tags]}")
u.log_warning("WC_SNAG done")
