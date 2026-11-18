import io
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"


def sub(f, old, new, count=1):
    s = io.open(L + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(L + f, "w", encoding="utf-8", newline="\n").write(s)


# her material must be allowed on a skeletal mesh (it was falling back to the gray default)
sub("import_assets.py", '''    m.set_editor_property("two_sided", True)
    tb = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, -200)''', '''    m.set_editor_property("two_sided", True)
    usage(m, "SKELETAL_MESH")
    tb = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, -200)''')
sub("import_assets.py", '''def step_her():''', '''def usage(m, what):
    try:
        mel.set_material_usage(m, getattr(unreal.MaterialUsage, "MATUSAGE_" + what))
    except Exception as exc:
        log(f"usage {what}: {exc}")


def step_her():''')
sub("import_assets.py", '''    m.set_editor_property("two_sided", two_sided)
    mel.recompile_material(m)''', '''    m.set_editor_property("two_sided", two_sided)
    usage(m, "INSTANCED_STATIC_MESHES")
    mel.recompile_material(m)''')
sub("import_assets.py", '''    flat_material("M_Paper", (0.62, 0.58, 0.48), 0.9)''', '''    flat_material("M_Paper", (0.62, 0.58, 0.48), 0.9)
    flat_material("M_EyeBlack", (0.002, 0.002, 0.002), 0.05)
    flat_material("M_EyeIris", (0.55, 0.62, 0.66), 0.25, emissive=0.35)
    flat_material("M_GlowBulb", (1.0, 0.62, 0.22), 0.5, emissive=14.0)
    flat_material("M_BulbOff", (0.09, 0.08, 0.06), 0.3)
    flat_material("M_Dash", (0.012, 0.012, 0.013), 0.55)
    flat_material("M_DashGlow", (0.25, 0.85, 0.55), 0.5, emissive=3.0)''')
# prop master: the MR textures are compressed as masks, so the sampler has to be a masks sampler
sub("import_more.py", '''    tr.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    rs = sparam(m, "RoughScale", 1.0, -700, 560)''', '''    tr.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    rs = sparam(m, "RoughScale", 1.0, -700, 560)''')
print("ok")
