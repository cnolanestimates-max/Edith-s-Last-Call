"""Audio pass 2: small mastering toolkit (numpy + scipy + ffmpeg for decoding).  Signals are float64 arrays (n, 2) at 48 kHz.

Run with a Python that has numpy and scipy (C:/Users/cheye/Documents/LocalAI/SF3D/.venv/Scripts/python.exe).
The point of most of this: Cheyenne plays on laptop speakers, which reproduce nothing under about 200 Hz, so weight has
to be carried by harmonics between 200 Hz and 2 kHz, and every one-shot has to arrive at a known loudness.
"""
import os, subprocess
import numpy as np
from scipy import signal
from scipy.io import wavfile
from scipy.ndimage import minimum_filter1d, uniform_filter1d

SR = 48000
_rng = np.random.default_rng(1993)


# ------------------------------------------------------------------ in / out
_channels = {}


def channels(path):
    if path not in _channels:
        out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=channels",
                                       "-of", "csv=p=0", path])
        _channels[path] = int(out.decode().strip().split(",")[0] or 2)
    return _channels[path]


def load(path, start=0.0, dur=None):
    cmd = ["ffmpeg", "-loglevel", "error", "-nostdin"]
    if start:
        cmd += ["-ss", f"{start:.4f}"]
    if dur:
        cmd += ["-t", f"{dur:.4f}"]
    cmd += ["-i", path]
    if channels(path) == 1:                       # ffmpeg's own mono-to-stereo upmix drops 3 dB; copy the channel instead
        cmd += ["-af", "pan=stereo|c0=c0|c1=c0"]
    else:
        cmd += ["-ac", "2"]
    cmd += ["-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.check_output(cmd)
    return np.frombuffer(raw, dtype="<f4").astype(np.float64).reshape(-1, 2)


def write(path, x, ch=1, dither=True):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    y = x.mean(axis=1, keepdims=True) if ch == 1 else x
    if dither:
        y = y + (_rng.random(y.shape) - _rng.random(y.shape)) / 32768.0
    y = np.clip(y, -1.0, 1.0 - 1 / 32768.0)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    wavfile.write(path, SR, np.round(y * 32767).astype("<i2").squeeze() if ch == 1 else np.round(y * 32767).astype("<i2"))


def db(v):
    return 20 * np.log10(np.maximum(v, 1e-12))


def lin(d):
    return 10 ** (d / 20.0)


def st(x):
    x = np.asarray(x, dtype=np.float64)
    return np.stack([x, x], axis=1) if x.ndim == 1 else x


def secs(t):
    return int(round(t * SR))


# ------------------------------------------------------------------ filters
def _sos(x, s):
    return signal.sosfilt(s, x, axis=0)


def hp(x, f, order=2):
    return _sos(x, signal.butter(order, f, "high", fs=SR, output="sos"))


def lp(x, f, order=2):
    return _sos(x, signal.butter(order, min(f, SR / 2 - 100), "low", fs=SR, output="sos"))


def lp0(x, f, order=4):
    """Zero-phase low-pass, so that x - lp0(x) is a clean high-pass (used to split a sound into two bands)."""
    return signal.sosfiltfilt(signal.butter(order, f, "low", fs=SR, output="sos"), x, axis=0)


def bp(x, lo, hi, order=2):
    return _sos(x, signal.butter(order, (lo, min(hi, SR / 2 - 100)), "band", fs=SR, output="sos"))


def _biquad(x, b, a):
    return signal.lfilter(b / a[0], a / a[0], x, axis=0)


def bell(x, f, gain_db, q=1.0):
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f / SR; al = np.sin(w) / (2 * q); c = np.cos(w)
    return _biquad(x, np.array([1 + al * A, -2 * c, 1 - al * A]), np.array([1 + al / A, -2 * c, 1 - al / A]))


def shelf(x, f, gain_db, high=True):
    A = 10 ** (gain_db / 40); w = 2 * np.pi * f / SR; c = np.cos(w); al = np.sin(w) / 2 * np.sqrt(2.0); s = 2 * np.sqrt(A) * al
    if high:
        b = np.array([A * ((A + 1) + (A - 1) * c + s), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - s)])
        a = np.array([(A + 1) - (A - 1) * c + s, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - s])
    else:
        b = np.array([A * ((A + 1) - (A - 1) * c + s), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - s)])
        a = np.array([(A + 1) + (A - 1) * c + s, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - s])
    return _biquad(x, b, a)


# ------------------------------------------------------------------ time
def fade(x, fin=0.003, fout=0.03, curve=1.0):
    x = x.copy(); n = len(x)
    a = min(secs(fin), n); b = min(secs(fout), n)
    if a > 0:
        x[:a] *= (np.linspace(0, 1, a) ** curve)[:, None]
    if b > 0:
        x[-b:] *= (np.linspace(1, 0, b) ** curve)[:, None]
    return x


def cut(x, start, dur=None):
    a = secs(start)
    return x[a:a + secs(dur)] if dur else x[a:]


def pad(x, before=0.0, after=0.0):
    return np.concatenate([np.zeros((secs(before), 2)), x, np.zeros((secs(after), 2))])


def pitch(x, ratio):
    """Tape-style: ratio 0.5 = an octave down and twice as long."""
    from fractions import Fraction
    fr = Fraction(1.0 / ratio).limit_denominator(200)
    return signal.resample_poly(x, fr.numerator, fr.denominator, axis=0)


def rev(x):
    return x[::-1].copy()


def decay(x, t60, start=0.0):
    """Force an exponential fall (t60 seconds to -60 dB) from `start` on: shortens a ringing tail."""
    n = len(x); t = np.maximum(np.arange(n) / SR - start, 0)
    return x * (10 ** (-3 * t / t60))[:, None]


def mix(layers, length=None):
    """layers: (signal, start seconds, gain dB)"""
    end = max(secs(s) + len(x) for x, s, g in layers)
    out = np.zeros((length and secs(length) or end, 2))
    for x, s, g in layers:
        a = secs(s); n = min(len(x), len(out) - a)
        if n > 0:
            out[a:a + n] += st(x)[:n] * lin(g)
    return out


def loop_xfade(x, t):
    """Fold the last t seconds over the first t seconds (equal power): the result loops without a seam."""
    n = secs(t); k = np.linspace(0, np.pi / 2, n)[:, None]
    head = x[:n] * np.sin(k) + x[-n:] * np.cos(k)
    return np.concatenate([head, x[n:-n]])


# ------------------------------------------------------------------ level
def peak(x):
    return db(np.abs(x).max()) if len(x) else -120.0


def _kw(x):
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = np.tan(np.pi * f0 / SR); Vh = 10 ** (G / 20); Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    y = signal.lfilter([(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0],
                       [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0], x, axis=0)
    f0, Q = 38.13547087602444, 0.5003270373238773
    K = np.tan(np.pi * f0 / SR); a0 = 1 + K / Q + K * K
    return signal.lfilter([1, -2, 1], [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0], y, axis=0)


def loud(x, mono=False):
    """Loudest 400 ms window, K-weighted (momentary max, LUFS).  mono=True measures the mono fold-down."""
    x = st(x)
    if mono:
        x = x.mean(axis=1, keepdims=True)
    p = (_kw(x) ** 2).sum(axis=1)
    n = secs(0.4)
    if len(p) <= n:
        return -0.691 + 10 * np.log10(max(p.sum() / n, 1e-12))
    c = np.concatenate(([0.0], np.cumsum(p)))
    w = (c[n::n // 8] - c[:-n:n // 8]) / n
    return -0.691 + 10 * np.log10(max(w.max(), 1e-12))


def integrated(x, mono=False):
    x = st(x)
    if mono:
        x = x.mean(axis=1, keepdims=True)
    p = (_kw(x) ** 2).sum(axis=1); n = secs(0.4)
    if len(p) <= n:
        return loud(x)
    c = np.concatenate(([0.0], np.cumsum(p)))
    w = (c[n::n // 4] - c[:-n:n // 4]) / n
    l = -0.691 + 10 * np.log10(np.maximum(w, 1e-12))
    g = w[l > -70]
    if not len(g):
        return -70.0
    rel = -0.691 + 10 * np.log10(g.mean()) - 10
    g2 = w[l > rel]
    return -0.691 + 10 * np.log10(max((g2 if len(g2) else g).mean(), 1e-12))


def loud_small(x, mono=True, f=220.0):
    """Loudness as a laptop speaker plays it: everything under about 220 Hz gone."""
    return loud(hp(st(x), f, 4), mono)


def balance(x, gap=3.5, f=200.0, mono=True):
    """Turn the band under f down (never up) until a laptop hears the sound within `gap` dB of what full speakers hear."""
    low = lp0(x, f, 3); rest = x - low
    def d(k):
        y = rest + k * low
        return loud(y, mono) - loud_small(y, mono)
    if d(1.0) <= gap:
        return x
    a, b = 0.03, 1.0
    if d(a) > gap:
        return rest + a * low
    for _ in range(14):
        m = (a + b) / 2
        if d(m) > gap:
            b = m
        else:
            a = m
    return rest + a * low


def low_share(x, f=200):
    m = st(x).mean(axis=1)
    return 100 * (lp(m[:, None], f, 4) ** 2).sum() / ((m ** 2).sum() + 1e-20)


def limit(x, ceiling=-1.0, look=0.006):
    """Look-ahead peak limiter.  The gain never rises above what the next few milliseconds need."""
    c = lin(ceiling); L = max(secs(look), 2)
    need = np.minimum(1.0, c / np.maximum(np.abs(x).max(axis=1), 1e-9))
    g = uniform_filter1d(minimum_filter1d(need, size=2 * L + 1, mode="nearest"), size=L, mode="nearest")
    return x * g[:, None]


def clip_soft(x, drive_db=0.0, ceiling=-0.5):
    """tanh soft clip: rounds peaks off instead of ducking the whole sound; adds density."""
    c = lin(ceiling)
    return np.tanh(x * lin(drive_db) / c) * c


def compress(x, thresh=-18.0, ratio=3.0, attack=0.005, release=0.12, knee=6.0, makeup=0.0):
    hop = 24
    e = np.abs(x).max(axis=1)
    nblk = len(e) // hop + 1
    eb = np.pad(e, (0, nblk * hop - len(e))).reshape(nblk, hop).max(axis=1)
    lv = db(eb)
    over = lv - thresh
    gr = np.where(over <= -knee / 2, 0.0, np.where(over >= knee / 2, over * (1 - 1 / ratio), (1 - 1 / ratio) * (over + knee / 2) ** 2 / (2 * knee)))
    aa = np.exp(-hop / (SR * attack)); ar = np.exp(-hop / (SR * release))
    out = np.empty(nblk); s = 0.0
    for i in range(nblk):
        k = aa if gr[i] > s else ar
        s = k * s + (1 - k) * gr[i]
        out[i] = s
    g = np.interp(np.arange(len(e)), np.arange(nblk) * hop + hop / 2, out)
    return x * lin(makeup - g)[:, None]


def to_loud(x, target, ceiling=-1.0, mono=True, soft=True):
    """Bring the loudest moment to `target` LUFS; anything over the ceiling is rounded off, then limited."""
    for _ in range(3):
        x = x * lin(target - loud(x, mono))
        if peak(x) > ceiling:
            if soft:
                x = clip_soft(x, 0.0, ceiling + 1.5) if peak(x) > ceiling + 1.5 else x
            x = limit(x, ceiling)
    return x


def to_peak(x, d=-1.0):
    return x * lin(d - peak(x))


# ------------------------------------------------------------------ character
def _smooth(e, t):
    k = np.exp(-1.0 / (SR * t))
    return signal.lfilter([1 - k], [1, -k], e, axis=0)


def transient(x, attack_db=6.0, sustain_db=0.0):
    """Lift (or soften) the first few milliseconds of every hit; optionally push the body up or down."""
    e = np.abs(x).max(axis=1)
    fast = _smooth(e, 0.0008); slow = _smooth(e, 0.030) + 1e-7
    r = np.clip(fast / slow, 1.0, 4.0)
    ga = attack_db * np.log(r) / np.log(4.0)
    late = np.clip(slow / (_smooth(e, 0.004) + 1e-7), 1.0, 4.0)
    gs = sustain_db * np.log(late) / np.log(4.0)
    return x * lin(ga + gs)[:, None]


def saturate(x, drive_db=6.0, mixv=1.0):
    g = lin(drive_db)
    y = np.tanh(x * g) / np.tanh(g) if g > 0 else x
    y *= (np.sqrt((x ** 2).mean()) + 1e-12) / (np.sqrt((y ** 2).mean()) + 1e-12)
    return x * (1 - mixv) + y * mixv


def bass_harm(x, fc=170.0, amount=1.0, top=950.0, keep_low=1.0):
    """Psychoacoustic bass: make harmonics of everything under fc and put them between fc and `top`.

    amount = level of the harmonics relative to the low band they come from (1.0 = equal RMS).
    keep_low scales the original low band (1 keeps it for real speakers and headphones)."""
    low = lp0(x, fc, 2)
    rest = x - low
    pk = np.abs(low).max() + 1e-9
    n = low / pk
    h = np.abs(n) - 0.45 + 0.9 * np.tanh(3.0 * n) + 0.5 * n ** 3      # even and odd harmonics
    h = bp(h, fc * 1.15, top, 2)
    h *= amount * np.sqrt((low ** 2).mean() + 1e-20) / np.sqrt((h ** 2).mean() + 1e-20)
    return rest + low * keep_low + h


def exciter(x, f=3000.0, amount=0.25):
    """Air: gentle harmonics of the upper mids, for dull generated foley."""
    hi = hp(x, f, 2)
    h = hp(np.tanh(hi * 4.0 / (np.abs(hi).max() + 1e-9)), f * 1.5, 2)
    h *= amount * np.sqrt((hi ** 2).mean() + 1e-20) / np.sqrt((h ** 2).mean() + 1e-20)
    return x + h


def _ir(t60, pre=0.0, lo=180.0, hi=6000.0, seed=7, early=()):
    r = np.random.default_rng(seed)
    n = secs(t60 * 1.15)
    t = np.arange(n) / SR
    ir = r.normal(size=(n, 2)) * (10 ** (-3 * t / t60))[:, None]
    ir = lp(hp(ir, lo, 2), hi, 2)
    # brighter at the start, darker in the tail
    dark = lp(ir, hi * 0.35, 1)
    k = np.clip(t / (t60 * 0.6), 0, 1)[:, None]
    ir = ir * (1 - k) + dark * k
    ir *= np.clip(t / 0.004, 0, 1)[:, None]
    for d, g in early:
        i = secs(d)
        if i < n:
            ir[i, 0] += g * (1 if r.random() > 0.5 else -1); ir[min(i + secs(0.0011), n - 1), 1] += g * 0.9
    ir /= np.sqrt((ir ** 2).sum(axis=0, keepdims=True)) + 1e-12
    return np.concatenate([np.zeros((secs(pre), 2)), ir])


def reverb(x, t60=1.2, wet=-12.0, pre=0.012, lo=180.0, hi=6000.0, seed=7, early=()):
    ir = _ir(t60, pre, lo, hi, seed, early)
    w = np.stack([signal.fftconvolve(x[:, c], ir[:, c]) for c in (0, 1)], axis=1)
    out = np.zeros_like(w); out[:len(x)] = x
    return out + w * lin(wet)


def room(x, wet=-15.0, size=0.32, seed=3):
    """A small plaster-and-board room: early reflections and a short dull tail.  Makes dry foley sit in the house."""
    return reverb(x, t60=size, wet=wet, pre=0.004, lo=250.0, hi=5200.0, seed=seed,
                  early=((0.007, 0.5), (0.013, 0.38), (0.021, 0.3), (0.034, 0.2)))


def through_wall(x, f=1500.0):
    return lp(hp(x, 110, 2), f, 2)


# ------------------------------------------------------------------ analysis
def events(x, thresh=-28.0, gap=0.12, min_len=0.03, pre=0.004):
    """Separate hits in a recording: [(start s, end s, peak dB)], loudest threshold relative to the file peak."""
    e = _smooth(np.abs(st(x)).max(axis=1), 0.004)
    on = e > e.max() * lin(thresh)
    idx = np.flatnonzero(np.diff(np.concatenate(([0], on.astype(np.int8), [0]))))
    seg = [(idx[i], idx[i + 1]) for i in range(0, len(idx), 2)]
    merged = []
    for a, b in seg:
        if merged and a - merged[-1][1] < secs(gap):
            merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    out = []
    for a, b in merged:
        if b - a >= secs(min_len):
            a2 = max(a - secs(pre), 0)
            out.append((a2 / SR, b / SR, peak(x[a2:b])))
    return out


def grab(x, ev, i, tail=0.0, lead=0.0):
    a, b, _ = ev[i]
    return x[max(secs(a - lead), 0):secs(b + tail)]


# ------------------------------------------------------------------ synthesis
def sub_drop(f0=95.0, f1=38.0, dur=1.6, t60=1.2, bend=0.25):
    t = np.arange(secs(dur)) / SR
    f = f1 + (f0 - f1) * np.exp(-t / bend)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * 10 ** (-3 * t / t60) * np.clip(t / 0.002, 0, 1)
    return st(y)


def noise(dur, lo, hi, seed=11):
    r = np.random.default_rng(seed)
    return bp(r.normal(size=(secs(dur), 2)), lo, hi, 2)
