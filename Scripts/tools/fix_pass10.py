import io
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"


def sub(f, old, new, count=1):
    s = io.open(L + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(L + f, "w", encoding="utf-8", newline="\n").write(s)


# prop master: default textures must match their sampler types, so use the cruiser's own (imported first)
sub("import_more.py", '''    tn.set_editor_property("texture", unreal.load_object(None, "/Engine/EngineMaterials/DefaultNormal.DefaultNormal"))''',
    '''    tn.set_editor_property("texture", eal.load_asset(G + "/Props/T_Cruiser_Normal"))''')
sub("import_more.py", '''    tr.set_editor_property("texture", unreal.load_object(None, "/Engine/EngineResources/WhiteSquareTexture.WhiteSquareTexture"))''',
    '''    tr.set_editor_property("texture", eal.load_asset(G + "/Props/T_Cruiser_MR"))''')
sub("import_more.py", '''    tb.set_editor_property("parameter_name", "BaseColor")''', '''    tb.set_editor_property("parameter_name", "BaseColor")
    tb.set_editor_property("texture", eal.load_asset(G + "/Props/T_Cruiser_BaseColor"))''')
sub("import_more.py", '''    master = build_prop_master()
    for f in sorted(os.listdir(d)):''', '''    # textures first (the master material takes its defaults from the cruiser's)
    alltex = [f"{d}/{f}" for f in sorted(os.listdir(d)) if f.lower().endswith(".png")]
    import_files(alltex, P)
    for f in alltex:
        nm_ = os.path.basename(f)[:-4]
        tex_settings(f"{P}/{nm_}", nm_.endswith("_BaseColor"), normal=nm_.endswith("_Normal"))
    master = build_prop_master()
    for f in sorted(os.listdir(d)):''')
# Edith: the iris is a faint ring, not a headlight; skin a touch warmer and dirtier
sub("import_assets.py", '''    flat_material("M_EyeIris", (0.55, 0.62, 0.66), 0.25, emissive=0.35)''', '''    flat_material("M_EyeIris", (0.30, 0.36, 0.40), 0.3, emissive=0.06)''')
sub("import_assets.py", '''    tint = vparam(m, "Tint", (0.46, 0.47, 0.5, 1), -700, -420)''', '''    tint = vparam(m, "Tint", (0.50, 0.46, 0.41, 1), -700, -420)''')
print("ok")
