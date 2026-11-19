"""List the sudden loud events in a sound file (to find a thump hiding in a loop).  python find_hits.py <wav> [...]"""
import sys, wave
import numpy as np

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
for path in ARGS:
    w = wave.open(path, "rb")
    n, ch, sr, sw = w.getnframes(), w.getnchannels(), w.getframerate(), w.getsampwidth()
    a = np.frombuffer(w.readframes(n), dtype={1: np.int8, 2: np.int16, 4: np.int32}[sw]).astype(np.float64)
    a = a.reshape(-1, ch).mean(axis=1) / float(2 ** (8 * sw - 1))
    win = int(sr * 0.05)
    m = len(a) // win
    rms = np.sqrt((a[:m * win].reshape(m, win) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    # low band only (thumps): a crude one-pole low-pass at about 150 Hz
    k = np.exp(-2 * np.pi * 150 / sr)
    lo = np.zeros_like(a)
    acc = 0.0
    step = max(1, sr // 4000)
    ad = a[::step]
    kd = np.exp(-2 * np.pi * 150 / (sr / step))
    lod = np.zeros_like(ad)
    for i, v in enumerate(ad):
        acc = acc * kd + v * (1 - kd)
        lod[i] = acc
    wl = int((sr / step) * 0.05)
    ml = len(lod) // wl
    dbl = 20 * np.log10(np.sqrt((lod[:ml * wl].reshape(ml, wl) ** 2).mean(axis=1) + 1e-12))
    hits = []
    for name, d in (("all", db), ("low", dbl)):
        for i in range(8, len(d)):
            base = np.median(d[max(0, i - 40):i])
            if d[i] - base > 6 and (not hits or i * 0.05 - hits[-1][0] > 0.6):
                hits.append((round(i * 0.05, 2), name, round(d[i] - base, 1), round(d[i], 1)))
    hits.sort()
    print(f"{path.split('/')[-1]}: {n / sr:.1f} s, mean {db.mean():.1f} dB, max window {db.max():.1f} dB, {len(hits)} sudden events")
    print("   ", ", ".join(f"{t}s(+{g}dB {nm})" for t, nm, g, lv in hits[:40]))
