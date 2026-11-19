"""Pass 113: Edith's skin, look C, a different way of adding texture.  The first try (darkwet2, darkwet3) added pores and
fine wrinkles and came out as sandy glitter.  darkwet4 leaves the fine scale alone and works at the middle scale: the big
folds cut deeper, veins that can be traced, a few scabbed patches with the skin lifting round them, wet in broad streaks."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
p = "C:/GameDev/Unreal/WellnessCheck/Scripts/her/her_look.py"
edit(p, [
    ('''    "darkwet3": ((0.012, 0.010, 0.009), (0.060, 0.044, 0.034), 0.65, 0.90, 0.25, 1.70, 1.0),''',
     '''    "darkwet3": ((0.012, 0.010, 0.009), (0.060, 0.044, 0.034), 0.65, 0.90, 0.25, 1.70, 1.0),
    # an eighth number: the middle-scale layers (deeper folds, traceable veins, scabs, wet streaks), with no fine grain added
    "darkwet4": ((0.012, 0.010, 0.009), (0.062, 0.046, 0.037), 0.60, 0.80, 0.25, 1.30, 0.0, 1.0),
    "darkwet5": ((0.012, 0.010, 0.009), (0.066, 0.049, 0.039), 0.70, 0.85, 0.25, 1.55, 0.0, 1.6),'''),
    ('''    extra = LOOKS[name][6] if len(LOOKS[name]) > 6 else 0.0''', '''    extra = LOOKS[name][6] if len(LOOKS[name]) > 6 else 0.0
    mid = LOOKS[name][7] if len(LOOKS[name]) > 7 else 0.0'''),
    ('''    c_fold = math_("SUBTRACT", 1.0, ramp(fold, 0.15, 0.75))''', '''    veinw = math_("MULTIPLY", math_("SUBTRACT", 1.0, ramp(edges(mapped_w((1, 1, 1)), 0.11), 0.0, 0.06)), ramp(noise(P, 0.045, 2.0).outputs["Fac"], 0.40, 0.58))
    scabn2 = noise(Pw, 0.42, 4.0, 0.6).outputs["Fac"]
    scabm = math_("MULTIPLY", ramp(scabn2, 0.66, 0.70), ramp(noise(P, 0.09, 2.0).outputs["Fac"], 0.45, 0.62))
    peelm = math_("SUBTRACT", ramp(scabn2, 0.615, 0.635), ramp(scabn2, 0.655, 0.675))
    streak = math_("MULTIPLY", ramp(noise(mapped((3.0, 3.0, 0.10)), 1.0, 2.0).outputs["Fac"], 0.55, 0.68), ramp(noise(P, 0.05, 2.0).outputs["Fac"], 0.40, 0.60))
    c_fold = math_("SUBTRACT", 1.0, ramp(fold, 0.15, 0.75))'''),
    ('''    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.8''', '''    if mid > 0.0:
        h = math_("ADD", h, math_("MULTIPLY", fold, 0.6 * mid))                    # the big folds cut deeper
        h = math_("ADD", h, math_("MULTIPLY", fine2, 0.35 * mid))
        h = math_("ADD", h, math_("MULTIPLY", veinw, 0.30 * mid))                  # veins stand up under the skin
        h = math_("ADD", h, math_("MULTIPLY", scabm, 0.45 * mid))
        h = math_("ADD", h, math_("MULTIPLY", peelm, 0.40 * mid))
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.8'''),
    ('''    col = mix(col, (0, 0, 0), math_("MULTIPLY", math_("SUBTRACT", 1.0, ao.outputs["AO"]), 0.75))
    hairc''', '''    if mid > 0.0:
        col = mix(col, (cb[0] * 0.28, cb[1] * 0.40, cb[2] * 0.85), math_("MULTIPLY", veinw, min(1.0, 0.55 * mid)))
        col = mix(col, (0.035, 0.012, 0.030), math_("MULTIPLY", bruise, min(1.0, 0.22 * mid)))
        col = mix(col, (0.045, 0.007, 0.005), math_("MULTIPLY", scabm, min(1.0, 0.9 * mid)))
        col = mix(col, (cb[0] * 2.2, cb[1] * 2.0, cb[2] * 1.8), math_("MULTIPLY", peelm, min(1.0, 0.8 * mid)))
    col = mix(col, (0, 0, 0), math_("MULTIPLY", math_("SUBTRACT", 1.0, ao.outputs["AO"]), 0.75))
    hairc'''),
    ('''    rough = mix(mix(rough, 0.9, m_dress), 0.42, m_hair)''', '''    if mid > 0.0:
        rough = math_("ADD", rough, math_("MULTIPLY", math_("MAXIMUM", scabm, peelm), min(1.0, 0.4 * mid)), clamp=True)
        rough = math_("MAXIMUM", math_("SUBTRACT", rough, math_("MULTIPLY", streak, min(1.0, 0.38 * mid))), 0.07)
    rough = mix(mix(rough, 0.9, m_dress), 0.42, m_hair)'''),
    ('''        L.new(math_("MULTIPLY", wetmask, 0.55 * wet), b.inputs["Coat Weight"])''',
     '''        L.new(math_("MAXIMUM", math_("MULTIPLY", wetmask, 0.55 * wet), math_("MULTIPLY", streak, min(1.0, 0.8 * mid))) if mid > 0.0 else math_("MULTIPLY", wetmask, 0.55 * wet), b.inputs["Coat Weight"])'''),
])
print("pass 113 applied")
