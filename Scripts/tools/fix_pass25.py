"""Edith's material: the hem of the nightgown and her feet and hands are filthy (darker, rougher toward the floor)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "import_assets.py", [
    ('''    mel.connect_material_expressions(tb, "RGB", mul, "A")
    mel.connect_material_expressions(tint, "", mul, "B")
    mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
    tn = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 60)
    tn.set_editor_property("texture", nm)''', '''mel.connect_material_expressions(tb, "RGB", mul, "A")
    mel.connect_material_expressions(tint, "", mul, "B")
    # filth: darker and browner from the knees down, as if she has been walking a wet cellar for months
    wp_ = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1000, -700)
    op_ = mel.create_material_expression(m, unreal.MaterialExpressionObjectPositionWS, -1000, -600)
    dirt = _custom(m, "float h = saturate((WP.z - OP.z) / 135.0); float k = h * h * (3.0 - 2.0 * h); return lerp(float3(0.30, 0.24, 0.17), float3(1.0, 1.0, 1.0), k);",
                   ["WP", "OP"], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -700, -650)
    mel.connect_material_expressions(wp_, "", dirt, "WP")
    mel.connect_material_expressions(op_, "", dirt, "OP")
    mul2 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -200, -300)
    mel.connect_material_expressions(mul, "", mul2, "A")
    mel.connect_material_expressions(dirt, "", mul2, "B")
    mel.connect_material_property(mul2, "", unreal.MaterialProperty.MP_BASE_COLOR)
    tn = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 60)
    tn.set_editor_property("texture", nm)'''),
])
print("ok")
