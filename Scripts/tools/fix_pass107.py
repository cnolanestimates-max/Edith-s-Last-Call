"""Pass 107: age the items properly (Cheyenne 2026-11-19 16:34 UTC: "they all look good, just make sure to age them
appropriately").  These things have lain in a rotting house for a year or more, and most are forty to a hundred years old:
  - dust settled on whatever faced up, and packed into the recesses
  - brass gone brown with green in the crevices, bright only where fingers and pockets rub it
  - steel spotted with rust; the wedding ring stays gold but dull and scratched
  - paper and card foxed and water-stained (already), cloth grubby (already)"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
p = "C:/GameDev/Unreal/WellnessCheck/Scripts/art/build_items_fine.py"
edit(p, [
    ('''         bright=None, edges=0.7, scratch=0.3, aod=0.003, er=0.0006, bump=0.35, col=None, tarn_lo=0.50, tarn_hi=0.64):''',
     '''         bright=None, edges=0.7, scratch=0.3, aod=0.003, er=0.0006, bump=0.35, col=None, tarn_lo=0.50, tarn_hi=0.64, dust=0.45, verdigris=0.0):'''),
    ('''    r = g.math("ADD", rough, g.math("MULTIPLY", t, 0.25))''', '''    # age: green in the crevices of brass; dust on what faced up and in the recesses
    vd = None
    if verdigris > 0.0:
        vd = g.math("MULTIPLY", g.ramp(g.noise(ns * 0.55, 4.0, vec=g.mapping(loc=(0.91, 0.17, 0.43))), 0.50, 0.64), g.ramp(a, 0.97, 0.62))
        vd = g.math("MULTIPLY", vd, verdigris)
        c = g.mix(c, g.mix((0.050, 0.130, 0.100), (0.110, 0.200, 0.150), fine), vd)
    dm = None
    if dust > 0.0:
        geo = g.N.new("ShaderNodeNewGeometry")
        sn = g.N.new("ShaderNodeSeparateXYZ")
        g.L.new(geo.outputs["Normal"], sn.inputs[0])
        up = g.math("MULTIPLY", g.ramp(sn.outputs[2], 0.30, 0.92), g.ramp(g.noise(ns * 0.45, 4.0, vec=g.mapping(loc=(0.71, 0.23, 0.87))), 0.28, 0.72))
        dm = g.math("MULTIPLY", g.math("MAXIMUM", up, g.math("MULTIPLY", g.ramp(a, 0.90, 0.50), 0.8)), dust, clamp=True)
        c = g.mix(c, g.mix((0.150, 0.128, 0.098), (0.105, 0.088, 0.066), fine2), g.math("MULTIPLY", dm, 0.85))
    r = g.math("ADD", rough, g.math("MULTIPLY", t, 0.25))'''),
    ('''    m = g.math("MULTIPLY", m, g.math("SUBTRACT", 1.0, g.math("MULTIPLY", t, tarn_metal)), clamp=True)''',
     '''    m = g.math("MULTIPLY", m, g.math("SUBTRACT", 1.0, g.math("MULTIPLY", t, tarn_metal)), clamp=True)
    if vd is not None:
        r = g.math("ADD", r, g.math("MULTIPLY", vd, 0.5), clamp=True)
        m = g.math("MULTIPLY", m, g.math("SUBTRACT", 1.0, vd), clamp=True)
    if dm is not None:
        r = g.math("ADD", r, g.math("MULTIPLY", dm, 0.45), clamp=True)
        m = g.math("MULTIPLY", m, g.math("SUBTRACT", 1.0, g.math("MULTIPLY", dm, 0.9)), clamp=True)'''),
    # brass: browner, less of it bright, green in the recesses
    ('''worn(g, (0.44, 0.29, 0.09), 1.0, 0.36, tarnish=(0.060, 0.045, 0.022), tarn=0.92, tarn_metal=0.55, bright=(0.80, 0.60, 0.25), scratch=0.45, aod=0.002, bump=0.55, tarn_lo=0.43, tarn_hi=0.58)''',
     '''worn(g, (0.36, 0.235, 0.075), 1.0, 0.40, tarnish=(0.048, 0.034, 0.017), tarn=0.95, tarn_metal=0.65, bright=(0.74, 0.55, 0.22), edges=0.6, scratch=0.45, aod=0.002, bump=0.6,
         tarn_lo=0.36, tarn_hi=0.54, verdigris=0.75, dust=0.4)'''),
    # steel: rust spots, duller
    ('''worn(g, (0.40, 0.40, 0.39), 1.0, 0.28, tarnish=(0.10, 0.085, 0.07), tarn=0.45, tarn_metal=0.5, bright=(0.66, 0.66, 0.65), scratch=0.55, aod=0.002)''',
     '''worn(g, (0.30, 0.30, 0.29), 1.0, 0.36, tarnish=(0.125, 0.052, 0.020), tarn=0.80, tarn_metal=0.85, bright=(0.60, 0.60, 0.59), edges=0.55, scratch=0.6, aod=0.002, bump=0.55,
         tarn_lo=0.47, tarn_hi=0.60, dust=0.4)'''),
    # gold does not tarnish; it goes dull and fine-scratched, with dirt in the line by each edge
    ('''worn(g, (0.78, 0.54, 0.17), 1.0, 0.20, tarnish=(0.42, 0.27, 0.08), tarn=0.35, tarn_metal=0.0, bright=(0.92, 0.72, 0.30), scratch=0.7, dirty=0.5, aod=0.0015, ns=900.0)''',
     '''worn(g, (0.66, 0.45, 0.14), 1.0, 0.30, tarnish=(0.36, 0.23, 0.07), tarn=0.5, tarn_metal=0.0, bright=(0.90, 0.70, 0.28), scratch=0.85, dirty=0.8, aod=0.0015, ns=900.0, dust=0.25)'''),
])
print("pass 107 applied")
