import io, json
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"


def sub(f, old, new, count=1):
    s = io.open(L + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(L + f, "w", encoding="utf-8", newline="\n").write(s)


sub("import_assets.py", '''exec(open(ROOT + "/Scripts/level/import_surfaces.py", encoding="utf-8").read())''',
    '''exec(open(ROOT + "/Scripts/level/import_surfaces.py", encoding="utf-8").read())
exec(open(ROOT + "/Scripts/level/import_variants.py", encoding="utf-8").read())''')
sub("import_assets.py", '''("extra", step_extra_mats), ("mega", step_mega)):''', '''("extra", step_extra_mats), ("mega", step_mega), ("variants", step_variants)):''')
sub("import_assets.py", '''"kit,her,mats,audio,tex,props,decals,extra,mega"''', '''"kit,her,mats,audio,tex,props,decals,extra,mega,variants"''')

# no more pink / purple / toy-bright kit colours: every such slot goes to a textured, aged material
o = json.load(open(L + "overrides.json"))
o.update({
    "M_LeatherPurple": "MI_LeatherRed", "M_LeatherGreen": "MI_LeatherGreen", "M_Purple": "MI_FabricDark", "M_Red": "MI_LeatherRed", "M_Green": "MI_LeatherGreen",
    "M_Orange": "MI_LeatherTan", "M_Yellow": "MI_PaperOld", "M_SkinPink": "MI_Porcelain", "M_Toy": "MI_ToyRed", "M_ToyBlue": "MI_ToyBlue",
    "M_PlasticBlue": "MI_ToyBlue", "M_PlasticGreen": "MI_LeatherGreen", "M_PlasticOrange": "MI_ToyRed", "M_PlasticYellow": "MI_ToyYellow", "M_PlasticWhite": "MI_Porcelain",
    "M_CurtainGreen": "MI_FabricGreen", "M_Felt": "MI_FabricGreen", "M_EnamelGreen": "MI_Porcelain", "M_CanvasDark": "MI_FabricDark", "M_Burlap": "MI_Sheet",
    "M_WaxPurple": "KIT:MI_Wax", "M_WaxRed": "KIT:MI_Wax", "M_GlowPurple": "KIT:MI_GlowWarm", "M_LiquidPurple": "KIT:MI_LiquidMurky", "M_LiquidGreen": "KIT:MI_LiquidMurky",
    "M_GlassPotionPurple": "KIT:MI_GlassBrown", "M_GlassPotionGreen": "KIT:MI_GlassBrown", "M_MushroomPurple": "KIT:MI_MushroomPale", "M_GlowSickly": "KIT:MI_GlowWarm",
    "M_Padding": "MI_Mattress", "M_PaddingStain": "MI_Mattress", "M_Stuffing": "MI_Sheet", "M_Concrete": "MI_CellarStone", "M_Slate": "MI_CellarStone",
    "M_WoodLight": "MI_WoodBleached", "M_Clay": "MI_Brick", "M_Rope": "MI_Sheet", "M_Hay": "MI_PaperOld",
})
json.dump(o, open(L + "overrides.json", "w"), indent=1)
sub("build_house.py", '''    p = f"{G}/Materials/{mi}"
    if eal.does_asset_exist(p):
        OVERRIDES[slot] = asset(p)''', '''    p = f"{KIT}/Materials/{mi[4:]}" if mi.startswith("KIT:") else f"{G}/Materials/{mi}"
    if eal.does_asset_exist(p):
        OVERRIDES[slot] = asset(p)''')
print("ok")
