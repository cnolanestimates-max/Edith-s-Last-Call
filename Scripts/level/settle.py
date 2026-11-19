# Settle pass: every small prop, note and pick-up that is meant to rest ON furniture is dropped onto whatever is
# actually under it (Cheyenne: "a lot of the items are not sitting on top of what they're supposed to be").
# exec'd by build_house.py after all dressing.  Wall-hung things, cords and fixtures are left alone.
SKIP_WORDS = ("Portrait", "Mirror", "Cobweb", "Curtain", "Medicine_Cabinet", "Cross", "Chain", "Ceiling", "Bunting", "Jar_Herbs", "Hook", "Bulb", "Cord", "Socket",
              "Switch", "Fuse", "Knot", "Window", "Lantern", "Decal", "Look_", "Trigger", "T_", "Door_", "Wall", "Stairs", "Rail", "Shutter", "Win", "Swing",
              "Gutter", "Pane", "Trim", "Beam", "Roof", "Gable", "Post", "Brace", "Cap", "Line", "Flies", "Her", "Tour", "Nav", "A_", "Light", "note_calendar", "Mem",
              "Picture", "Sconce", "Rack", "Wreath", "Doll_Voodoo", "Effigy_Twig_Hanging", "Oil_Lamp_Wall", "Oil_Lamp_Hanging", "Blanket", "Dress", "Rag", "Mattress")
_w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
moved, checked, fell = 0, 0, 0
for a in actors.get_all_level_actors():
    folder = str(a.get_folder_path())
    if not (folder.startswith("House/Dressing") or folder.startswith("House/Decay/Kitchen") or folder.startswith("House/Decay/Dining") or folder.startswith("House/Interact")):
        continue
    label = a.get_actor_label()
    if any(wd in label for wd in SKIP_WORDS):
        continue
    if any(str(t).startswith(("Show_", "Hide_")) for t in a.tags) and not any(str(t) == "Show_jewel" for t in a.tags):
        continue
    _rot = a.get_actor_rotation()
    if abs(_rot.roll) > 45 or abs(_rot.pitch) > 45:
        continue                                           # pinned to a wall
    comps = [c_ for c_ in a.get_components_by_class(unreal.StaticMeshComponent) if c_.static_mesh]
    if not comps:
        continue                                           # a bare "use" spot (light switch, knot): nothing to rest
    origin, extent, _r = unreal.SystemLibrary.get_component_bounds(comps[0])
    if max(extent.x, extent.y) > 48 or extent.z > 45 or (extent.x + extent.y + extent.z) < 0.5:
        continue                                           # furniture, or nothing to see
    if label.startswith("Drawing_") and extent.z > 3:
        continue                                           # a drawing on a wall (the flat ones on floors and tables do settle)
    bottom = origin.z - extent.z
    floor = math.floor((bottom + 12.0) / 350.0) * 350.0
    if bottom - floor < 14.0:
        continue                                           # on the floor already
    loc = a.get_actor_location()
    checked += 1
    try:
        hit = unreal.SystemLibrary.line_trace_single(_w, V(origin.x, origin.y, bottom + 36.0), V(origin.x, origin.y, bottom - 46.0), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                     True, [a], unreal.DrawDebugTrace.NONE, True)
    except Exception:
        hit = None
    if not hit or not hit.to_tuple()[0]:
        # nothing under it within reach: it was hanging in the air beside the furniture.  Let it fall to whatever is below.
        try:
            hit = unreal.SystemLibrary.line_trace_single(_w, V(origin.x, origin.y, bottom + 4.0), V(origin.x, origin.y, bottom - 340.0), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                         True, [a], unreal.DrawDebugTrace.NONE, True)
        except Exception:
            hit = None
        if not hit or not hit.to_tuple()[0]:
            continue
        fell += 1
    t = hit.to_tuple()
    dz = (t[5].z + 0.25) - bottom
    if abs(dz) > 0.6:
        a.set_actor_location(V(loc.x, loc.y, loc.z + dz), False, False)
        moved += 1
log(f"settle: {moved} of {checked} resting props moved onto the surface under them ({fell} had nothing under them and fell)")

# her glass eye lies on the lining of the open jewelry box, wherever the box came to rest
_jb = next((a for a in actors.get_all_level_actors() if a.get_actor_label() == "JewelBoxOpen"), None)
_je = next((a for a in actors.get_all_level_actors() if a.get_actor_label() == "Pickup_pick_keep_eye"), None)
if _jb and _je:
    _l = _jb.get_actor_location()
    _je.set_actor_location(V(_l.x, _l.y, _l.z + 3.0), False, False)
    log(f"glass eye set in the jewelry box at z {_l.z + 3.0:.1f}")
