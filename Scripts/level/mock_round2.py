"""Round two of the polish pass, shown to Cheyenne as mock-ups (2026-11-22) and kept (A kitchen, B floors with the white
kept, C clutter, D yard; E puddles trashed).  At the end of the level build, or on the saved map with apply_polish.py step
"mock_round2"; with WC_MOCK_UNDO=1 it takes them out again.
  - kitchen: 1950s paper on its walls (the wallpaper slot of each wall piece round the kitchen) and checker linoleum on
    its floor (KitchenTiles_0)
  - clutter: the dining-room dresser and the living-room side table dressed (Scripts/art/polish_furniture.py Mock sets)
  - yard: dead grass, leaves, needles, stones and branches over the yard ground, off the path and the house
  - floors: see below"""
import json, os
import unreal as u

K = (816.0, 1584.0, 216.0, 584.0)
eal = u.EditorAssetLibrary


def dress():
    undo = os.environ.get("WC_MOCK_UNDO") == "1"
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = list(sub.get_all_level_actors())
    by = {a.get_actor_label(): a for a in actors}
    paper = eal.load_asset("/Game/WC/Mock/MI_MockKitchenPaper")
    lino = eal.load_asset("/Game/WC/Mock/MI_MockLinoleum")
    n = 0
    # ---- kitchen walls and floor
    for a in actors:
        if not isinstance(a, u.StaticMeshActor) or not a.static_mesh_component.static_mesh:
            continue
        c = a.static_mesh_component
        o, e = a.get_actor_bounds(False)
        if not (K[0] - 40 < o.x < K[1] + 40 and K[2] - 40 < o.y < K[3] + 40 and -10 < o.z < 340):
            continue
        thin = min(e.x, e.y) < 45 and max(e.x, e.y) > 60 and e.z > 100
        for i, m in enumerate(c.get_materials()):
            nm = m.get_name() if m else ""
            if thin and (nm.startswith("MI_Wallpaper") or nm == "MI_MockKitchenPaper"):
                if undo:
                    orig = [t for t in a.tags if str(t).startswith("MockOrig_")]
                    if orig:
                        c.set_material(i, eal.load_asset("/Game/WC/Materials/" + str(orig[0])[9:]))
                else:
                    if nm != "MI_MockKitchenPaper":
                        a.set_editor_property("tags", list(a.tags) + [u.Name("MockOrig_" + nm)])
                    c.set_material(i, paper)
                n += 1
    tiles = by.get("KitchenTiles_0")
    if tiles:
        tiles.static_mesh_component.set_material(0, eal.load_asset("/Game/WC/Materials/MI_MegaTilesOld") if undo else lino)
        n += 1
    # ---- the floors: the three trim bands of the outside (water table, band board, frieze) were laid as slabs right
    # through the house, and indoors their painted tops are the white boards you see, 2-8 cm above the real floor, so the
    # feet of every piece of furniture sank into them.  Cheyenne kept the white (2026-11-22): the slabs indoors are dropped
    # to 3 mm above the floor, the outside keeps its full-height trim as strips round the walls, and the other tile layers
    # (never seen before) stay out of sight so only the kitchen's linoleum shows through.
    LEVELS = {"WaterTable": (-6.0, 8.0, 0.3), "BandBoard": (328.0, 352.0, 350.3), "Frieze": (662.0, 702.0, 700.3)}
    bands = {}
    for a in actors:
        lab = a.get_actor_label()
        for nm in LEVELS:
            if lab.startswith(nm + "_"):
                bands.setdefault(nm, []).append(a)
    for nm, parts in bands.items():
        lo, hi, low_top = LEVELS[nm]
        for a in parts:
            a.set_actor_hidden_in_game(False)
            a.static_mesh_component.set_visibility(True)
            o, e = a.get_actor_bounds(False)
            top = hi if undo else low_top
            sc = a.get_actor_scale3d()
            a.set_actor_scale3d(u.Vector(sc.x, sc.y, sc.z * (top - lo) / max(0.01, 2 * e.z)))
            o2, e2 = a.get_actor_bounds(False)
            loc = a.get_actor_location()
            a.set_actor_location(u.Vector(loc.x, loc.y, loc.z + (lo - (o2.z - e2.z))), False, True)
        for k in range(4):
            if undo and by.get(f"Mock_{nm}Strip_{k}"):
                sub.destroy_actor(by[f"Mock_{nm}Strip_{k}"])
        if undo:
            continue
        bb = [a.get_actor_bounds(False) for a in parts]
        x0, x1 = min(o.x - e.x for o, e in bb), max(o.x + e.x for o, e in bb)
        y0, y1 = min(o.y - e.y for o, e in bb), max(o.y + e.y for o, e in bb)
        z0, z1 = lo, hi
        m = {"WaterTable": 64.0, "BandBoard": 58.0, "Frieze": 60.0}[nm] + 2.0
        src = parts[0].static_mesh_component
        strips = [(x0, x1, y0, y0 + m), (x0, x1, y1 - m, y1), (x0, x0 + m, y0 + m, y1 - m), (x1 - m, x1, y0 + m, y1 - m)]
        if nm == "BandBoard" and not undo:
            # the band was cut round the old hole in the back bathroom: stretch the piece beside it back over the gap
            if by.get("Mock_BandBoardStrip_4"):
                sub.destroy_actor(by["Mock_BandBoardStrip_4"])
            for a in parts:
                o, e = a.get_actor_bounds(False)
                if abs(o.x - e.x - 2480) < 2 and abs(o.x + e.x - 2600) < 2 and abs(o.y + e.y - 330) < 2:
                    sc = a.get_actor_scale3d()
                    a.set_actor_scale3d(u.Vector(sc.x, sc.y * (2 * e.y + 120.0) / (2 * e.y), sc.z))
                    o2, e2 = a.get_actor_bounds(False)
                    loc = a.get_actor_location()
                    a.set_actor_location(u.Vector(loc.x, loc.y + ((o.y - e.y) - (o2.y - e2.y)), loc.z), False, True)
        for k, (a0, a1, b0, b1) in enumerate(strips):
            zz1 = low_top if k == 4 else z1
            lab = f"Mock_{nm}Strip_{k}"
            st = by.get(lab) or sub.spawn_actor_from_class(u.StaticMeshActor, u.Vector(0, 0, 0), u.Rotator(0, 0, 0))
            st.set_actor_label(lab)
            st.set_folder_path("House/Mock/Trim")
            c = st.static_mesh_component
            c.set_static_mesh(src.static_mesh)
            c.set_material(0, src.get_materials()[0])
            c.set_collision_profile_name("NoCollision")
            st.set_actor_scale3d(u.Vector((a1 - a0) / 100.0, (b1 - b0) / 100.0, (zz1 - z0) / 100.0))
            want = u.Vector((a0 + a1) / 2, (b0 + b1) / 2, (z0 + zz1) / 2)
            st.set_actor_location(want, False, True)
            o_, e_ = st.get_actor_bounds(False)                                   # whatever the cube's pivot, centre it
            st.set_actor_location(want + (want - o_), False, True)
        n += 1
    # the boards laid over the old hole in the back bathroom take the same white top, level with the rest
    pb = by.get("UpperFloor_Bath2Patch")
    if pb and not undo:
        pb.static_mesh_component.set_material(0, eal.load_asset("/Game/WC/Materials/MI_TrimPaint"))
        o, e = pb.get_actor_bounds(False)
        sc = pb.get_actor_scale3d()
        pb.set_actor_scale3d(u.Vector(sc.x, sc.y, sc.z * (350.3 - 330.0) / max(0.01, 2 * e.z)))
        o2, e2 = pb.get_actor_bounds(False)
        loc = pb.get_actor_location()
        pb.set_actor_location(u.Vector(loc.x, loc.y, loc.z + (330.0 - (o2.z - e2.z))), False, True)
    for i in range(3):                                                        # the grime laid over the patched boards
        if not undo and by.get(f"Decal_Bath2Patch_{i}"):
            sub.destroy_actor(by[f"Decal_Bath2Patch_{i}"])
    if by.get("Mock_Bath2TilesPatch"):
        sub.destroy_actor(by["Mock_Bath2TilesPatch"])
    for a in actors:
        lab = a.get_actor_label()
        if any(lab.startswith(t) for t in ("BathTiles_", "BathGTiles_", "PantryTiles_", "Bath2Tiles_")):
            a.set_actor_hidden_in_game(not undo)
            a.static_mesh_component.set_visibility(undo)
    # ---- clutter on the bare tops
    for label, folder, mesh in (("Dresser_Drawers", "/Dining", "SM_MockClutterDresser"), ("SM_Table_Small_01a", "/Living", "SM_MockClutterTable")):
        top = next((a for a in actors if a.get_actor_label() == label and str(a.get_folder_path()).endswith(folder)), None)
        lab = "Mock_" + mesh[7:]
        if undo:
            if by.get(lab):
                sub.destroy_actor(by[lab])
            continue
        if not top:
            continue
        o, e = top.get_actor_bounds(False)
        a = by.get(lab) or sub.spawn_actor_from_class(u.StaticMeshActor, u.Vector(o.x, o.y, o.z + e.z), top.get_actor_rotation())
        a.set_actor_label(lab)
        a.set_folder_path("House/Mock")
        a.set_actor_location_and_rotation(u.Vector(o.x, o.y, o.z + e.z), top.get_actor_rotation(), False, True)
        a.static_mesh_component.set_static_mesh(eal.load_asset("/Game/WC/Props/Polish/" + mesh))
        a.static_mesh_component.set_collision_profile_name("NoCollision")
        n += 1
    # ---- the yard
    meta = json.load(open("C:/GameDev/Unreal/WellnessCheck/SourceArt/Mock/mock_yard.json"))
    for name, (x, y, z) in sorted(meta.items()):
        lab = name.replace("SM_", "")
        if undo:
            if by.get(lab):
                sub.destroy_actor(by[lab])
            continue
        mesh = eal.load_asset("/Game/WC/Mock/" + name)
        if not mesh:
            continue
        a = by.get(lab) or sub.spawn_actor_from_class(u.StaticMeshActor, u.Vector(x, y, z), u.Rotator(0, 0, 0))
        a.set_actor_label(lab)
        a.set_folder_path("House/Mock/Yard")
        a.set_actor_location(u.Vector(x, y, z), False, True)
        c = a.static_mesh_component
        c.set_static_mesh(mesh)
        c.set_collision_profile_name("NoCollision")
        c.set_cast_shadow(False)
        n += 1
    u.log_warning(f"WC_POLISH mock round two {'taken out' if undo else 'put in'}: {n} changes")
