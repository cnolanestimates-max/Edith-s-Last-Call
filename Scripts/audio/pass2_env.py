"""Audio pass 2: print the loudness shape of files over time (dB per step) in three bands: under 200 Hz / 200-2k / over 2k."""
import sys, os
import numpy as np
import pass2_lib as L
import pass2_sources as S
step = 0.25
args = sys.argv[1:]
if args and args[0].startswith("--step="):
    step = float(args[0][7:]); args = args[1:]
for a in args:
    lim = None
    if "@" in a:
        a, lim = a.split("@"); lim = [float(v) for v in lim.split(",")]
    p = a if os.path.exists(a) else (S.ROOT + "/SourceArt/Audio/" + a if os.path.exists(S.ROOT + "/SourceArt/Audio/" + a) else S.path(a))
    x = L.load(p, lim[0] if lim else 0, lim[1] if lim else 30)
    n = L.secs(step)
    bands = (L.lp(x, 200, 4), L.bp(x, 200, 2000, 2), L.hp(x, 2000, 4))
    print(f"== {a}  {len(x)/L.SR:.2f}s  step {step}s")
    for nm, b in zip(("low", "mid", "hi "), bands):
        v = [L.db(np.sqrt((b[i:i + n] ** 2).mean())) for i in range(0, len(b) - n // 2, n)]
        print(f"  {nm} " + " ".join(f"{max(q, -99):4.0f}" for q in v[:60]))
