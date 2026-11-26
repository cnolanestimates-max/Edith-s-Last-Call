"""Measure every wav in a folder: length, peak, loudness, crest and how much of it a laptop speaker can play.

  <python with numpy+scipy> audit_levels.py [folder] [--csv out.csv]

Loudness is the loudest 400 ms window after K-weighting (BS.1770 momentary max), which is fairer to short one-shots
than an integrated figure.  "low%" is the share of energy under 200 Hz: Cheyenne's laptop speakers play none of it.
Needs numpy and scipy (C:/Users/cheye/Documents/LocalAI/SF3D/.venv/Scripts/python.exe has both).
"""
import os, sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter, butter, sosfilt

ROOT = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio"


def read(path):
    sr, x = wavfile.read(path)
    if x.dtype == np.int16:
        x = x / 32768.0
    elif x.dtype == np.int32:
        x = x / 2147483648.0
    elif x.dtype == np.uint8:
        x = (x - 128) / 128.0
    x = x.astype(np.float64)
    if x.ndim == 1:
        x = x[:, None]
    return sr, x


def kweight(x, sr):
    # BS.1770 pre-filter, coefficients re-derived for the sample rate
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = np.tan(np.pi * f0 / sr); Vh = 10 ** (G / 20); Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    b = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]
    a = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    y = lfilter(b, a, x, axis=0)
    f0, Q = 38.13547087602444, 0.5003270373238773
    K = np.tan(np.pi * f0 / sr)
    a0 = 1 + K / Q + K * K
    b = [1, -2, 1]
    a = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    return lfilter(b, a, y, axis=0)


def momentary_max(x, sr):
    y = kweight(x, sr)
    p = (y ** 2).sum(axis=1)                       # channels summed (weights 1.0 for L, R and mono)
    n = int(0.4 * sr)
    if len(p) <= n:
        m = p.mean() * len(p) / n if len(p) else 0  # short sound: energy as if padded to 400 ms
        m = max(m, 1e-12)
        return -0.691 + 10 * np.log10(m)
    c = np.concatenate(([0.0], np.cumsum(p)))
    hop = max(1, n // 4)
    w = (c[n::hop] - c[:-n:hop]) / n
    return -0.691 + 10 * np.log10(max(w.max(), 1e-12))


def integrated(x, sr):
    y = kweight(x, sr)
    p = (y ** 2).sum(axis=1)
    n = int(0.4 * sr)
    if len(p) <= n:
        return -0.691 + 10 * np.log10(max(p.mean(), 1e-12))
    c = np.concatenate(([0.0], np.cumsum(p)))
    hop = n // 4
    w = (c[n::hop] - c[:-n:hop]) / n
    l = -0.691 + 10 * np.log10(np.maximum(w, 1e-12))
    g = w[l > -70]
    if not len(g):
        return -70.0
    rel = -0.691 + 10 * np.log10(g.mean()) - 10
    g2 = w[l > rel]
    return -0.691 + 10 * np.log10(max(g2.mean() if len(g2) else g.mean(), 1e-12))


def measure(path):
    sr, x = read(path)
    mono = x.mean(axis=1)
    peak = np.abs(x).max() if len(x) else 0
    rms = np.sqrt((mono ** 2).mean()) if len(mono) else 0
    lo = sosfilt(butter(4, 200, "low", fs=sr, output="sos"), mono)
    e = (mono ** 2).sum() + 1e-20
    spec = np.abs(np.fft.rfft(mono[: sr * 20])) ** 2
    fr = np.fft.rfftfreq(len(mono[: sr * 20]), 1 / sr)
    cen = (spec * fr).sum() / (spec.sum() + 1e-20)
    return dict(sr=sr, ch=x.shape[1], dur=len(x) / sr, peak=20 * np.log10(max(peak, 1e-9)),
                rms=20 * np.log10(max(rms, 1e-9)), mom=momentary_max(x, sr), lufs=integrated(x, sr),
                low=100 * (lo ** 2).sum() / e, cen=cen)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    folder = args[0] if args else ROOT
    rows = []
    for f in sorted(os.listdir(folder)):
        if f.lower().endswith(".wav"):
            try:
                rows.append((f, measure(folder + "/" + f)))
            except Exception as exc:
                print(f"{f}: {exc}")
    print(f"{'file':34s} {'s':>6s} ch {'peak':>6s} {'mom':>6s} {'LUFS':>6s} {'crest':>5s} {'low%':>5s} {'cen Hz':>6s}")
    for f, m in rows:
        print(f"{f:34s} {m['dur']:6.2f} {m['ch']:2d} {m['peak']:6.1f} {m['mom']:6.1f} {m['lufs']:6.1f} {m['peak'] - m['rms']:5.1f} {m['low']:5.1f} {m['cen']:6.0f}")
    if "--csv" in sys.argv:
        out = sys.argv[sys.argv.index("--csv") + 1]
        with open(out, "w") as fh:
            fh.write("file,dur,ch,peak,mom,lufs,crest,low,cen\n")
            for f, m in rows:
                fh.write(f"{f},{m['dur']:.3f},{m['ch']},{m['peak']:.2f},{m['mom']:.2f},{m['lufs']:.2f},{m['peak'] - m['rms']:.2f},{m['low']:.2f},{m['cen']:.0f}\n")
