"""Pass 106: Edith's skin, look C (dark and wet), pushed further (Cheyenne 2026-11-19: "I like C, dark and wet, but can we get it
any better? Can we do more texture on her?").  Two stronger versions of it to choose from: darkwet2 and darkwet3.
More layers on the same skin: a second, finer set of wrinkles; real pores; raised veins; bruising; scabbed patches; skin
lifting at the edges of them; wet running down in streaks."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

p = "C:/GameDev/Unreal/WellnessCheck/Scripts/her/her_look.py"
edit(p, [
    ('''    "corpse":  ((0.060, 0.058, 0.056), (0.210, 0.200, 0.186), 0.60, 0.40, 0.40, 1.1),
}''', '''    "corpse":  ((0.060, 0.058, 0.056), (0.210, 0.200, 0.186), 0.60, 0.40, 0.40, 1.1),
    # look C taken further (a seventh number: how much of the extra layers)
    "darkwet2": ((0.012, 0.010, 0.009), (0.052, 0.039, 0.031), 0.55, 0.80, 0.25, 1.15, 0.6),
    "darkwet3": ((0.011, 0.009, 0.008), (0.055, 0.040, 0.031), 0.65, 0.90, 0.25, 1.30, 1.0),
}'''),
    ('''    ca, cb, red, wet, sss, bump = LOOKS[name]''', '''    ca, cb, red, wet, sss, bump = LOOKS[name][:6]
    extra = LOOKS[name][6] if len(LOOKS[name]) > 6 else 0.0'''),
    ('''    c_fold = math_("SUBTRACT", 1.0, ramp(fold, 0.15, 0.75))''', '''    # ---- the extra layers (0 = none of them)
    w4 = waves(Pw, 2.7, 8.0)
    w5 = waves(Pw, 3.6, 9.0, "X")
    micro = math_("SUBTRACT", 1.0, math_("POWER", math_("MAXIMUM", w4, math_("MULTIPLY", w5, 0.75)), 2.5))          # fine wrinkles between the big ones
    vor = N.new("ShaderNodeTexVoronoi"); vor.feature = "F1"; vor.inputs["Scale"].default_value = 15.0; L.new(P, vor.inputs["Vector"])
    pit = ramp(vor.outputs["Distance"], 0.0, 0.30)                                                              # 0 in the pore, 1 on the skin
    bruise = ramp(noise(P, 0.06, 3.0).outputs["Fac"], 0.54, 0.70)
    scabn = noise(Pw, 0.85, 5.0, 0.65).outputs["Fac"]
    scab = math_("MULTIPLY", ramp(scabn, 0.675, 0.715), ramp(noise(P, 0.12, 2.0).outputs["Fac"], 0.40, 0.60))  # crusted patches, in a few regions only
    peel = math_("SUBTRACT", ramp(scabn, 0.635, 0.655), ramp(scabn, 0.670, 0.690))                              # the skin lifting round them
    drip = math_("MULTIPLY", ramp(noise(mapped((7.0, 7.0, 0.22)), 1.0, 2.0).outputs["Fac"], 0.60, 0.70), ramp(noise(P, 0.07, 2.0).outputs["Fac"], 0.42, 0.62))
    c_fold = math_("SUBTRACT", 1.0, ramp(fold, 0.15, 0.75))'''),
    ('''    h = math_("ADD", h, math_("MULTIPLY", pore, 0.05))''', '''    h = math_("ADD", h, math_("MULTIPLY", pore, 0.05))
    if extra > 0.0:
        h = math_("ADD", h, math_("MULTIPLY", micro, 0.42 * extra))
        h = math_("ADD", h, math_("MULTIPLY", ramp(fine, 0.0, 0.09), 0.22 * extra))
        h = math_("ADD", h, math_("MULTIPLY", pit, 0.16 * extra))
        h = math_("ADD", h, math_("MULTIPLY", veinsoft, 0.22 * extra))
        h = math_("ADD", h, math_("MULTIPLY", scab, 0.38 * extra))
        h = math_("ADD", h, math_("MULTIPLY", peel, 0.50 * extra))'''),
    ('''    col = mix(col, (0, 0, 0), math_("MULTIPLY", math_("SUBTRACT", 1.0, ao.outputs["AO"]), 0.75))''',
     '''    if extra > 0.0:
        col = mix(col, (0.030, 0.011, 0.028), math_("MULTIPLY", bruise, 0.40 * extra))                             # bruising under the skin
        col = mix(col, (cb[0] * 0.30, cb[1] * 0.40, cb[2] * 0.75), math_("MULTIPLY", veinsoft, 0.35 * extra))         # the veins stand out more
        col = mix(col, (ca[0] * 0.30, ca[1] * 0.26, ca[2] * 0.24), math_("MULTIPLY", math_("SUBTRACT", 1.0, micro), 0.55 * extra))
        col = mix(col, (0.004, 0.003, 0.003), math_("MULTIPLY", math_("SUBTRACT", 1.0, pit), 0.50 * extra))           # dark in the pores
        col = mix(col, (0.050, 0.008, 0.006), math_("MULTIPLY", scab, 0.85 * extra))                                  # old scabs
        col = mix(col, (cb[0] * 1.9, cb[1] * 1.8, cb[2] * 1.7), math_("MULTIPLY", peel, 0.75 * extra))                # dead skin lifting, paler
        col = mix(col, (ca[0] * 0.5, ca[1] * 0.5, ca[2] * 0.5), math_("MULTIPLY", drip, 0.45 * extra))                # wet runs darker
    col = mix(col, (0, 0, 0), math_("MULTIPLY", math_("SUBTRACT", 1.0, ao.outputs["AO"]), 0.75))'''),
    ('''    rough = math_("ADD", rough, math_("MULTIPLY", crease, 0.12), clamp=True)''',
     '''    rough = math_("ADD", rough, math_("MULTIPLY", crease, 0.12), clamp=True)
    if extra > 0.0:
        rough = math_("ADD", rough, math_("MULTIPLY", math_("MAXIMUM", scab, peel), 0.45 * extra), clamp=True)       # crust and dead skin are dry
        rough = math_("SUBTRACT", rough, math_("MULTIPLY", drip, 0.40 * extra))                                      # the runs are slick
        rough = math_("MAXIMUM", rough, 0.06)'''),
    ('''bp.inputs["Strength"].default_value = 0.75 * bump; bp.inputs["Distance"].default_value = 0.30 * K''',
     '''bp.inputs["Strength"].default_value = 0.75 * bump; bp.inputs["Distance"].default_value = (0.30 + 0.16 * extra) * K'''),
    ('''    views = {"face": (cm(10, -92, 233), cm(1.5, -22, 237), 62),''', '''    views = {"close": (cm(7, -62, 240), cm(2.5, -22, 240), 85), "arm": (cm(-70, -120, 150), cm(-38, -8, 150), 70), "face": (cm(10, -92, 233), cm(1.5, -22, 237), 62),'''),
    ('''            for vname in (("face",) if pose == "rest" else ("face",)):''', '''            for vname in (("face", "close") if pose == "rest" else ("face",)):'''),
])
print("pass 106 applied")
