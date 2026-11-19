"""Pass 103c: second look at the item models (my own notes on the first sheet): the fuse's rating window was covered by its cap,
the wedding ring's beading was coarse, the mirror in the jewelry box lid was mostly gone, the vent's rust was a speckle."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Scripts/art/build_items_fine.py", [
    # the fuse: the cap is a ring, and the card with the rating shows through it
    ('''    P.append(moved(lathe([(0.0332, 0.0124), (0.0346, 0.0124), (0.0352, 0.0118), (0.0352, 0.0098)], "Brass", 48), rot=(0, -PI / 2, 0)))        # the cap ring''',
     '''    capr = moved(lathe([(0.0332, 0.0124), (0.0346, 0.0124), (0.0353, 0.0118), (0.0353, 0.0104)], "Brass", 48), rot=(0, -PI / 2, 0))
    P.append(cut(capr, cyl(0.0100, 0.01, (0, 0, 0.0345), m="Brass", v=48)))                                    # the cap ring'''),
    # the ring: plain, with a fine line near each edge
    ('''    for z in (-0.0024, 0.0024):
        for k in range(60):
            a = 2 * PI * k / 60
            P.append(sphere(0.00028, (0.01078 * math.cos(a), 0.01078 * math.sin(a), z), "Gold", 6, 4))
    return P''', '''    for z in (-0.0023, 0.0023):
        P.append(tube(ring_pts(0.01072, 96, z=z), 0.00012, "Gold", True, 2))
    return P'''),
    ('''    c = g.mix((0.55, 0.57, 0.56), (0.05, 0.045, 0.035), g.ramp(g.noise(160.0, 5.0), 0.52, 0.66))       # the silvering has gone in spots
    g.finish(c, g.ramp(g.noise(160.0, 5.0), 0.52, 0.66, 0.04, 0.6), g.ramp(g.noise(160.0, 5.0), 0.52, 0.66, 1.0, 0.0))''',
     '''    gone = g.ramp(g.math("ADD", g.noise(70.0, 5.0), g.ramp(g.edge(0.004), 0.0, 1.0, 0.0, 0.12)), 0.63, 0.72)       # the silvering has gone in a few spots, mostly at the edges
    c = g.mix((0.50, 0.52, 0.51), (0.05, 0.045, 0.035), gone)
    g.finish(c, g.mix(0.05, 0.6, gone), g.mix(1.0, 0.0, gone))'''),
    ('''def m_steel(g):''', '''def m_castiron(g):
    """A big cast piece (the vent): rust in broad stains, not speckle."""
    worn(g, (0.060, 0.056, 0.052), 1.0, 0.55, tarnish=(0.13, 0.05, 0.02), tarn=0.8, tarn_metal=0.85, bright=(0.30, 0.29, 0.28), scratch=0.2, aod=0.008, er=0.002,
         bump=0.8, ns=110.0, tarn_lo=0.52, tarn_hi=0.70)


def m_steel(g):'''),
    ('''MATS = {"Cloth": m_cloth,''', '''MATS = {"CastIron": m_castiron, "Cloth": m_cloth,'''),
    ('''    veins = g.ramp(g.cells(230.0, vec=wob.outputs[0]), 0.0, 0.008, 1.0, 0.0)
    veins = g.math("MULTIPLY", veins, g.ramp(g.noise(150.0, 3.0), 0.50, 0.66))''',
     '''    veins = g.ramp(g.cells(230.0, vec=wob.outputs[0]), 0.0, 0.011, 1.0, 0.0)
    veins = g.math("MULTIPLY", veins, g.ramp(g.noise(150.0, 3.0), 0.44, 0.60))'''),
])
p = R + "Scripts/art/build_items_fine.py"
s = open(p, encoding="utf-8").read()
a = s.index("def vent_parts(")
b = s.index("def vent_cover_flat(")
body = s[a:b].replace('m="Iron"', 'm="CastIron"').replace('"Iron", 0.0006)', '"CastIron", 0.0006)')
s = s[:a] + body + s[b:]
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("pass 103c applied", body.count("CastIron"))
