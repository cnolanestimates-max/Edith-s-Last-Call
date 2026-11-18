# Tinted children of the textured surfaces: house paint, trim, shutters, book leathers, faded toy paint.
# exec'd by import_assets.py (step "variants").  Run after "tex".
VARIANTS = {
    # name: (parent, tint rgb, grime or None)
    "SidingPaint": ("MI_Siding", (1.30, 1.16, 0.80), None),        # faded butter-yellow clapboard
    "SidingPaintDark": ("MI_Siding", (0.95, 0.86, 0.62), None),
    "TrimPaint": ("MI_WoodPainted", (1.25, 1.2, 1.08), None),      # what is left of the white trim
    "ShutterPaint": ("MI_WoodPainted", (0.22, 0.40, 0.33), None),  # dark green shutters and door
    "PorchPaint": ("MI_PorchBoards", (0.80, 0.84, 0.86), None),
    "ShingleRed": ("MI_RoofShingle", (0.75, 0.42, 0.36), None),
    "LeatherRed": ("MI_Leather", (0.85, 0.30, 0.24), None),
    "LeatherGreen": ("MI_Leather", (0.42, 0.62, 0.40), None),
    "LeatherBlue": ("MI_Leather", (0.40, 0.50, 0.72), None),
    "LeatherTan": ("MI_Leather", (1.25, 1.0, 0.7), None),
    "ToyRed": ("MI_WoodPainted", (0.70, 0.30, 0.25), None),
    "ToyBlue": ("MI_WoodPainted", (0.36, 0.48, 0.60), None),
    "ToyYellow": ("MI_WoodPainted", (0.85, 0.72, 0.38), None),
    "FabricGreen": ("MI_FabricDark", (0.75, 1.0, 0.70), None),
    "FabricBlue": ("MI_FabricDark", (0.75, 0.85, 1.15), None),
    "DirtRoad": ("MI_YardGround", (0.80, 0.70, 0.56), None),
    "ForestFloor": ("MI_YardGround", (0.55, 0.60, 0.42), None),
}


def step_variants():
    n = 0
    for name, (parent, tint, grime) in VARIANTS.items():
        par = eal.load_asset(f"{G}/Materials/{parent}")
        if not par:
            log(f"variant {name}: no parent {parent}")
            continue
        p = f"{G}/Materials/MI_{name}"
        if eal.does_asset_exist(p):
            eal.delete_asset(p)
        mi = tools.create_asset("MI_" + name, G + "/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, par)
        mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(tint[0], tint[1], tint[2], 1))
        if grime is not None:
            mel.set_material_instance_scalar_parameter_value(mi, "Grime", grime)
        eal.save_loaded_asset(mi, False)
        n += 1
    log(f"variants: {n}")
