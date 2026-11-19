"""Pass 106b: the first previews of the stronger skin were smeared by the denoiser and the close-up was out of focus.
Sharper previews (more samples, no denoising, no shallow focus) and the extra layers rebalanced: less darkening, more relief."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
p = "C:/GameDev/Unreal/WellnessCheck/Scripts/her/her_look.py"
edit(p, [
    ('"darkwet2": ((0.012, 0.010, 0.009), (0.052, 0.039, 0.031), 0.55, 0.80, 0.25, 1.15, 0.6),', '"darkwet2": ((0.012, 0.010, 0.009), (0.056, 0.042, 0.033), 0.55, 0.80, 0.25, 1.40, 0.6),'),
    ('"darkwet3": ((0.011, 0.009, 0.008), (0.055, 0.040, 0.031), 0.65, 0.90, 0.25, 1.30, 1.0),', '"darkwet3": ((0.012, 0.010, 0.009), (0.060, 0.044, 0.034), 0.65, 0.90, 0.25, 1.70, 1.0),'),
    ('math_("MULTIPLY", bruise, 0.40 * extra))', 'math_("MULTIPLY", bruise, 0.22 * extra))'),
    ('math_("MULTIPLY", math_("SUBTRACT", 1.0, micro), 0.55 * extra))', 'math_("MULTIPLY", math_("SUBTRACT", 1.0, micro), 0.30 * extra))'),
    ('    sc.cycles.samples = 28\n    sc.render.resolution_x = 640; sc.render.resolution_y = 720',
     '    SHARP = any(len(LOOKS.get(n_, ())) > 6 for n_ in NAMES)          # the detailed looks: nothing may smear the detail\n'
     '    sc.cycles.samples = 72 if SHARP else 28\n    sc.cycles.use_denoising = not SHARP\n    sc.render.threads = 6 if SHARP else 4\n'
     '    sc.render.resolution_x = 800 if SHARP else 640; sc.render.resolution_y = 900 if SHARP else 720'),
    ('        for pose, sv in (("rest", 0.0), ("scream", 1.0)):', '        for pose, sv in ((("rest", 0.0),) if SHARP else (("rest", 0.0), ("scream", 1.0))):'),
    ('                cam.data.dof.focus_distance = (tgt - loc).length', '                cam.data.dof.focus_distance = (tgt - loc).length\n                cam.data.dof.use_dof = not SHARP'),
])
print("pass 106b applied")
