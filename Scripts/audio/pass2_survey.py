"""Audio pass 2: print what is inside each library recording (length, level, where the hits are)."""
import sys
import numpy as np
import pass2_lib as L
import pass2_sources as S

keys = sys.argv[1:] or (list(S.SONNISS) + list(S.OTHER))
for k in keys:
    try:
        p = S.path(k)
        x = L.load(p, 0, 90)
        ev = L.events(x, -26, 0.25, 0.04)
        m = x.mean(axis=1)
        spec = np.abs(np.fft.rfft(m[: L.SR * 20])) ** 2
        fr = np.fft.rfftfreq(len(m[: L.SR * 20]), 1 / L.SR)
        cen = (spec * fr).sum() / (spec.sum() + 1e-20)
        print(f"{k:16s} {len(x)/L.SR:6.1f}s pk {L.peak(x):6.1f} mom {L.loud(x):6.1f} low {L.low_share(x):5.1f}% cen {cen:5.0f}  ev{len(ev):3d}: " +
              " ".join(f"{a:.2f}-{b:.2f}({pk:.0f})" for a, b, pk in ev[:14]))
    except Exception as exc:
        print(f"{k:16s} FAILED {exc}")
