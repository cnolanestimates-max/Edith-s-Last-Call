# Decayed surface master + instances, exec'd by import_assets.py after import_more.py (overrides build_surface_master / step_tex).
#
# M_Surface is world-aligned (triplanar), so the same instance works on any kit piece or box.  On top of the texture set it adds:
#   - a big filth mask (the "Grime" texture) sampled at room scale: brown-black stains, drips, mold blotches
#   - dirt bands by height inside each storey: skirting-level filth and damp creeping down from the ceiling
#   - broad uneven darkening so no two metres of wall look alike


def _custom(m, code, inputs, out, x, y):
    c = mel.create_material_expression(m, unreal.MaterialExpressionCustom, x, y)
    c.set_editor_property("code", code)
    c.set_editor_property("output_type", out)
    ins = []
    for name in inputs:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", name)
        ins.append(ci)
    c.set_editor_property("inputs", ins)
    return c


def build_surface_master():
    m = new_material("M_Surface")
    F3 = unreal.CustomMaterialOutputType.CMOT_FLOAT3
    F4 = unreal.CustomMaterialOutputType.CMOT_FLOAT4
    F1 = unreal.CustomMaterialOutputType.CMOT_FLOAT1
    wp = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -2000, -100)
    vn = mel.create_material_expression(m, unreal.MaterialExpressionVertexNormalWS, -2000, 220)
    tile = sparam(m, "Tile", 200.0, -2000, 60)
    div = mel.create_material_expression(m, unreal.MaterialExpressionDivide, -1800, -60)
    mel.connect_material_expressions(wp, "", div, "A")
    mel.connect_material_expressions(tile, "", div, "B")
    gtile = sparam(m, "GrimeTile", 430.0, -2000, 420)
    gdiv = mel.create_material_expression(m, unreal.MaterialExpressionDivide, -1800, 380)
    mel.connect_material_expressions(wp, "", gdiv, "A")
    mel.connect_material_expressions(gtile, "", gdiv, "B")
    wts = _custom(m, "float3 w = pow(abs(N), 6.0); return w / (w.x + w.y + w.z);", ["N"], F3, -1750, 220)
    mel.connect_material_expressions(vn, "", wts, "N")

    def tri(param, default_tex, sampler, x, y, coords, normal=False):
        tp = mel.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, x - 300, y)
        tp.set_editor_property("parameter_name", param)
        tp.set_editor_property("sampler_type", sampler)
        if default_tex:
            tp.set_editor_property("texture", default_tex)
        if normal:
            code = ("float3 tx = UnpackNormalMap(Texture2DSample(T, TSampler, P.yz)).xyz;"
                    "float3 ty = UnpackNormalMap(Texture2DSample(T, TSampler, P.xz)).xyz;"
                    "float3 tz = UnpackNormalMap(Texture2DSample(T, TSampler, P.xy)).xyz;"
                    "float3 s = sign(N);"
                    "float3 nx = float3(tx.z * s.x, tx.x, tx.y);"
                    "float3 ny = float3(ty.x, ty.z * s.y, ty.y);"
                    "float3 nz = float3(tz.x, tz.y, tz.z * s.z);"
                    "return normalize(nx * W.x + ny * W.y + nz * W.z);")
            c = _custom(m, code, ["T", "P", "W", "N"], F3, x, y)
            mel.connect_material_expressions(vn, "", c, "N")
        else:
            c = _custom(m, "return Texture2DSample(T, TSampler, P.yz) * W.x + Texture2DSample(T, TSampler, P.xz) * W.y + Texture2DSample(T, TSampler, P.xy) * W.z;",
                        ["T", "P", "W"], F4, x, y)
        mel.connect_material_expressions(tp, "", c, "T")
        mel.connect_material_expressions(coords, "", c, "P")
        mel.connect_material_expressions(wts, "", c, "W")
        return c
    white = unreal.load_object(None, "/Engine/EngineResources/WhiteSquareTexture.WhiteSquareTexture")
    flatn = unreal.load_object(None, "/Engine/EngineMaterials/DefaultNormal.DefaultNormal")
    grime_default = eal.load_asset(G + "/Textures/Grime/BaseColor") or white
    bc = tri("BaseColor", white, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -1200, -300, div)
    orm = tri("ORM", white, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS, -1200, 0, div)
    nrm = tri("Normal", flatn, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, -1200, 300, div, normal=True)
    gr = tri("GrimeTex", grime_default, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -1200, 600, gdiv)
    tint = vparam(m, "Tint", (1, 1, 1, 1), -1200, -560)
    gtint = vparam(m, "GrimeTint", (0.16, 0.115, 0.07, 1), -1200, -760)
    grime = sparam(m, "Grime", 0.5, -1200, -900)
    skirt = sparam(m, "Skirt", 0.55, -1200, -1000)
    # filth mask 0..1 (returned in .a) and the decayed base colour (.rgb)
    decay = _custom(m,
                    "float lum = dot(G.rgb, float3(0.3, 0.59, 0.11));"
                    "float mask = saturate((0.78 - lum) * 1.9);"
                    "float n = sin(P.x * 0.0031 + sin(P.y * 0.0043) * 2.1) * sin(P.y * 0.0037 + sin(P.z * 0.0051) * 1.7) * sin(P.z * 0.0029 + 1.3);"
                    "float broad = saturate(0.5 + 0.5 * n);"
                    "float h = frac(P.z / 350.0 + 100.0) * 350.0;"
                    "float low = saturate(1.0 - h / 75.0);"
                    "float high = saturate((h - 235.0) / 95.0);"
                    "float band = saturate((low * 0.75 + high * 0.6) * Skirt * (0.55 + 0.9 * mask));"
                    "float f = saturate(mask * Grime * (0.8 + 0.6 * broad) + band);"
                    "float3 c = Base.rgb * Tint.rgb * lerp(1.0, 0.62 + 0.38 * broad, saturate(Grime));"
                    "c = lerp(c, c * GT.rgb * 2.2 + GT.rgb * 0.06, f);"
                    "return float4(c, f);",
                    ["Base", "G", "P", "Tint", "GT", "Grime", "Skirt"], F4, -700, -420)
    for src, pin in ((bc, "Base"), (gr, "G"), (wp, "P"), (tint, "Tint"), (gtint, "GT"), (grime, "Grime"), (skirt, "Skirt")):
        mel.connect_material_expressions(src, "", decay, pin)

    def chan(src, chs, x, y):
        k = mel.create_material_expression(m, unreal.MaterialExpressionComponentMask, x, y)
        for c2 in "rgba":
            k.set_editor_property(c2, c2 in chs)
        mel.connect_material_expressions(src, "", k, "")
        return k
    mel.connect_material_property(chan(decay, "rgb", -420, -420), "", unreal.MaterialProperty.MP_BASE_COLOR)
    fmask = chan(decay, "a", -420, -300)
    ao = chan(orm, "r", -900, -60)
    ro = chan(orm, "g", -900, 40)
    me = chan(orm, "b", -900, 140)
    rsc = sparam(m, "RoughScale", 1.0, -900, 240)
    rough = _custom(m, "return saturate(R * S + F * 0.18);", ["R", "S", "F"], F1, -420, 60)
    mel.connect_material_expressions(ro, "", rough, "R")
    mel.connect_material_expressions(rsc, "", rough, "S")
    mel.connect_material_expressions(fmask, "", rough, "F")
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(ao, "", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    msc = sparam(m, "Metal", 0.0, -900, 340)
    mmul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -420, 200)
    mel.connect_material_expressions(me, "", mmul, "A")
    mel.connect_material_expressions(msc, "", mmul, "B")
    mel.connect_material_property(mmul, "", unreal.MaterialProperty.MP_METALLIC)
    mel.connect_material_property(nrm, "", unreal.MaterialProperty.MP_NORMAL)
    m.set_editor_property("tangent_space_normal", False)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    return m


def step_tex():
    base = SRC + "/Textures"
    if not os.path.isdir(base):
        log("no textures folder yet")
        return
    spec = json.load(open(base + "/surfaces.json")) if os.path.exists(base + "/surfaces.json") else {}
    eal.make_directory(G + "/Textures")
    names = [n for n in sorted(os.listdir(base)) if os.path.isdir(base + "/" + n) and not n.startswith("_") and os.path.exists(f"{base}/{n}/BaseColor.png")]
    # textures first (the master's default grime texture must exist before it is built)
    for name in names:
        d = base + "/" + name
        files = [f"{d}/{k}.png" for k in ("BaseColor", "ORM", "Normal") if os.path.exists(f"{d}/{k}.png")]
        import_files(files, f"{G}/Textures/{name}")
        tex_settings(f"{G}/Textures/{name}/BaseColor", True)
        tex_settings(f"{G}/Textures/{name}/ORM", False)
        tex_settings(f"{G}/Textures/{name}/Normal", False, normal=True)
    master = build_surface_master()
    grime_tex = eal.load_asset(G + "/Textures/Grime/BaseColor")
    for name in names:
        if name == "Grime":
            continue
        dest = f"{G}/Textures/{name}"
        mi_path = f"{G}/Materials/MI_{name}"
        if eal.does_asset_exist(mi_path):
            eal.delete_asset(mi_path)
        mi = tools.create_asset("MI_" + name, G + "/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, master)
        for key in ("BaseColor", "ORM", "Normal"):
            t = eal.load_asset(f"{dest}/{key}")
            if t:
                mel.set_material_instance_texture_parameter_value(mi, key, t)
        if grime_tex:
            mel.set_material_instance_texture_parameter_value(mi, "GrimeTex", grime_tex)
        s = spec.get(name, {})
        mel.set_material_instance_scalar_parameter_value(mi, "Tile", float(s.get("tile", 200.0)))
        mel.set_material_instance_scalar_parameter_value(mi, "Grime", float(s.get("grime", 0.5)) * 1.5)
        mel.set_material_instance_scalar_parameter_value(mi, "RoughScale", float(s.get("rough", 1.0)))
        mel.set_material_instance_scalar_parameter_value(mi, "Metal", float(s.get("metal", 0.0)))
        tile = float(s.get("tile", 200.0))
        mel.set_material_instance_scalar_parameter_value(mi, "Skirt", 0.6 if tile >= 200 else 0.25)
        mel.set_material_instance_scalar_parameter_value(mi, "GrimeTile", 430.0 if tile >= 200 else 170.0)
        eal.save_loaded_asset(mi, False)
        log(f"surface MI_{name}")
