# The small carried things (Scripts/art/build_items.py): static meshes + plain metal / glass materials.
# exec'd by import_assets.py; step name "items".
def item_material(name, rgb, rough, metallic):
    m = new_material(name)
    mel.connect_material_property(const3(m, rgb, -400, 0), "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(const1(m, rough, -400, 200), "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(const1(m, metallic, -400, 320), "", unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    return m


def step_items():
    d = SRC + "/Props/items"
    if not os.path.isdir(d):
        log("no item models yet (run Scripts/art/build_items.py)")
        return
    P = G + "/Props"
    mats = {
        "Brass": item_material("M_ItemBrass", (0.50, 0.34, 0.11), 0.42, 1.0),
        "Iron": item_material("M_ItemIron", (0.10, 0.09, 0.085), 0.55, 1.0),
        "Gold": item_material("M_ItemGold", (0.86, 0.62, 0.22), 0.28, 1.0),
        "Steel": item_material("M_ItemSteel", (0.48, 0.48, 0.47), 0.38, 1.0),
        "Glass": item_material("M_ItemGlass", (0.50, 0.62, 0.60), 0.08, 0.0),
        "Ceramic": item_material("M_ItemCeramic", (0.74, 0.70, 0.62), 0.5, 0.0),
        "Ribbon": item_material("M_ItemRibbon", (0.26, 0.03, 0.04), 0.9, 0.0),
        "Polymer": item_material("M_ItemPolymer", (0.025, 0.025, 0.028), 0.55, 0.0),
        "Gunmetal": item_material("M_ItemGunmetal", (0.075, 0.075, 0.08), 0.36, 1.0),
    }
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".fbx"):
            continue
        name = f[:-4]
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", f"{d}/{f}")
        t.set_editor_property("destination_path", P)
        t.set_editor_property("destination_name", name)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("automated", True)
        t.set_editor_property("save", True)
        ui = unreal.FbxImportUI()
        ui.set_editor_property("automated_import_should_detect_type", False)
        ui.set_editor_property("import_mesh", True)
        ui.set_editor_property("import_as_skeletal", False)
        ui.set_editor_property("import_animations", False)
        ui.set_editor_property("import_materials", False)
        ui.set_editor_property("import_textures", False)
        ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
        sd = ui.get_editor_property("static_mesh_import_data")
        sd.set_editor_property("combine_meshes", True)
        sd.set_editor_property("auto_generate_collision", True)
        sd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
        t.set_editor_property("options", ui)
        tools.import_asset_tasks([t])
        sm = eal.load_asset(f"{P}/{name}")
        if not sm:
            log(f"item {name}: FAILED to import")
            continue
        slots = []
        for i, sm_mat in enumerate(sm.static_materials):
            slot = str(sm_mat.material_slot_name)
            key = next((k for k in mats if slot.lower().startswith(k.lower())), None)
            if key:
                sm.set_material(i, mats[key])
            slots.append(f"{slot}->{key}")
        eal.save_loaded_asset(sm, False)
        b = sm.get_bounds().box_extent
        log(f"item {name}: {', '.join(slots)}; half size {b.x:.1f} x {b.y:.1f} x {b.z:.1f} cm")
