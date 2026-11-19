# Float sweep (Cheyenne 2026-11-19: "a lot of props are literally in midair still ... bottles in the kitchen that are just
# hanging in the air by the sink").  Runs last in the level build.  Every small loose thing is checked against what is really
# under it, at five points of its footprint; anything hanging more than 3 cm above its support is dropped onto it.  Things that
# are meant to hang (pictures, cobwebs, lamps on walls and so on) are left alone, and whatever else is found in the air but is
# not on the list of loose things is reported, not moved.
import math as _m
_fw = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
_HANG = ("Portrait", "Mirror", "Cobweb", "Curtain", "Medicine_Cabinet", "Cross", "Chain", "Ceiling", "Bunting", "Jar_Herbs", "Hook", "Bulb", "Cord", "Socket", "Switch",
         "Fuse", "Knot", "Window", "Lantern", "Decal", "Wall", "Stairs", "Rail", "Shutter", "Gutter", "Pane", "Trim", "Beam", "Roof", "Gable", "Post", "Brace", "Sconce",
         "Rack", "Wreath", "Voodoo", "Hanging", "Blanket", "Dress", "Rag", "Chandelier", "Vent", "Shelf", "Drawing_", "Frame", "Clock_Wall", "Antler", "Eye", "Hole", "Rake",
         "Nail", "Gap", "Door", "Lintel", "Board", "Skull_Goat", "Shed", "BookCase", "Book_", "DenBook", "ShelfBook", "Settlers", "Curtains", "Plank")
_LOOSE = ("Bottle", "Tin_Cans", "Jar", "Candle", "Plates", "Teapot", "Bucket", "Crate", "Box_", "Newspaper", "Doll", "Toy", "Pill", "Lamp", "Radio", "Typewriter",
          "Telephone", "Cup", "Suitcase", "Hatbox", "Barrel", "Basket", "Paint_Can", "Letters", "Clipboard", "Music_Box", "Flashlight", "Tome", "Pickup_", "Note_",
          "Mantel_Clock", "Trash", "Stack", "Pile", "Bust", "Vase", "Bowl", "Pot", "Pan", "Kettle", "Glass", "Mug", "Ink", "Quill", "Photo")
_dropped, _left, _seen = 0, [], 0
for _a in actors.get_all_level_actors():
    _folder = str(_a.get_folder_path())
    if not _folder.startswith("House/") or _folder.startswith(("House/Shell", "House/Nav", "House/Points", "House/Auto", "House/Environment", "House/Exterior/Forest")):
        continue
    _label = _a.get_actor_label()
    if any(_w in _label for _w in _HANG):
        continue
    if any(str(_t).startswith(("Show_", "Hide_")) for _t in _a.tags):
        continue
    _rot = _a.get_actor_rotation()
    if abs(_rot.roll) > 45 or abs(_rot.pitch) > 45:
        continue
    _comps = [_c for _c in _a.get_components_by_class(unreal.StaticMeshComponent) if _c.static_mesh]
    if not _comps:
        continue
    _o, _e, _r = unreal.SystemLibrary.get_component_bounds(_comps[0])
    if max(_e.x, _e.y) > 70 or _e.z > 60 or (_e.x + _e.y + _e.z) < 0.5:
        continue
    _seen += 1
    _bottom = _o.z - _e.z
    _best = None
    for _dx, _dy in ((0, 0), (0.5, 0), (-0.5, 0), (0, 0.5), (0, -0.5)):
        try:
            _h = unreal.SystemLibrary.line_trace_single(_fw, V(_o.x + _dx * _e.x, _o.y + _dy * _e.y, _bottom + 6.0), V(_o.x + _dx * _e.x, _o.y + _dy * _e.y, _bottom - 400.0),
                                                        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [_a], unreal.DrawDebugTrace.NONE, True)
        except Exception:
            _h = None
        if _h and _h.to_tuple()[0]:
            _z = _h.to_tuple()[5].z
            _best = _z if _best is None else max(_best, _z)
    if _best is None:
        continue
    _gap = _bottom - _best
    if _gap <= 3.0:
        continue
    # only a short fall is put right: a long one means whatever it stands on has no solid top (a bed, a counter) or it is
    # part of something built in the air on purpose (the cruiser's cabin), and those are reported, not moved
    if _gap <= 40.0 and _o.x > -900.0 and any(_w in _label for _w in _LOOSE):
        _l = _a.get_actor_location()
        _a.set_actor_location(V(_l.x, _l.y, _l.z - _gap + 0.3), False, False)
        _dropped += 1
        log(f"float: {_label} at ({_l.x:.0f},{_l.y:.0f},{_l.z:.0f}) hung {_gap:.0f} cm in the air: dropped")
    else:
        _left.append(f"{_label} ({_o.x:.0f},{_o.y:.0f},{_bottom:.0f}) {_gap:.0f} cm")
log(f"float sweep: {_seen} small things checked, {_dropped} dropped onto what is under them, {len(_left)} others are off their support and were left: " + "; ".join(_left[:60]))
