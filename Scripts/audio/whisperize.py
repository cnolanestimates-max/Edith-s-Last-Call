"""Turn a spoken take into a true whisper (2026-11-24, Edith's "You should never have come here.").

The TTS voices will not whisper on request: they speak softly but the vocal cords still sound.  A whisper is the same
mouth shapes driven by breath instead of a voice, so this keeps the shapes (LPC filter per 25 ms frame) and replaces the
voice under them with noise of the same loudness.  Then a little air is added on top and the low end that a whisper
does not have is taken out.  Needs numpy and scipy (the SF3D venv has them).

python whisperize.py <in.wav> <out.wav>   ->  prints how much voicing (pitch) is left, before and after
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import lfilter, butter, sosfilt
from scipy.linalg import solve_toeplitz


def lpc(frame, order):
    r = np.correlate(frame, frame, "full")[len(frame) - 1:len(frame) + order]
    if r[0] <= 1e-9:
        return np.zeros(order), 0.0
    a = solve_toeplitz(r[:order], -r[1:order + 1])
    err = max(r[0] + np.dot(a, r[1:order + 1]), 1e-12)
    return a, err


def voicing(x, sr):
    """Mean normalised autocorrelation peak in the 80-400 Hz pitch range over loud frames (1 = clearly pitched)."""
    n, hop = int(0.04 * sr), int(0.01 * sr)
    lo, hi = int(sr / 400), int(sr / 80)
    vals = []
    loud = np.sqrt(np.mean(x ** 2)) * 0.5
    for i in range(0, len(x) - n, hop):
        f = x[i:i + n] - np.mean(x[i:i + n])
        if np.sqrt(np.mean(f ** 2)) < loud:
            continue
        ac = np.correlate(f, f, "full")[n - 1:]
        if ac[0] <= 0:
            continue
        vals.append(np.max(ac[lo:hi]) / ac[0])
    return float(np.mean(vals)) if vals else 0.0


def main(src, dst):
    sr, x = wavfile.read(src)
    x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x /= max(np.max(np.abs(x)), 1e-9)
    order = int(sr / 1000) + 4
    n, hop = int(0.025 * sr), int(0.0125 * sr)
    win = np.hanning(n)
    out = np.zeros(len(x) + n)
    norm = np.zeros(len(x) + n)
    rng = np.random.default_rng(7)
    pre = lfilter([1, -0.9], [1], x)                       # pre-emphasis, so the filter follows the mouth, not the chest
    for i in range(0, len(x) - n, hop):
        f = pre[i:i + n] * win
        a, err = lpc(f, order)
        gain = np.sqrt(err / n)
        noise = rng.standard_normal(n) * gain
        y = lfilter([1], np.concatenate(([1], a)), noise) * win
        out[i:i + n] += y
        norm[i:i + n] += win ** 2
    out = out[:len(x)] / np.maximum(norm[:len(x)], 1e-3)
    out = lfilter([1], [1, -0.9], out)                     # undo the pre-emphasis
    out = sosfilt(butter(4, 380, "highpass", fs=sr, output="sos"), out)   # no chest in a whisper
    out = sosfilt(butter(2, 9000, "lowpass", fs=sr, output="sos"), out)
    # keep the original's loudness envelope (a whisper follows the words, it does not hiss between them)
    env_n = int(0.02 * sr)
    def env(s):
        return np.sqrt(np.convolve(s ** 2, np.ones(env_n) / env_n, "same")) + 1e-6
    out *= np.clip(env(x) / env(out), 0, 4)
    out /= max(np.max(np.abs(out)), 1e-9)
    out *= 0.89
    wavfile.write(dst, sr, (out * 32767).astype(np.int16))
    print(f"voicing before {voicing(x, sr):.2f}  after {voicing(out, sr):.2f}  ({len(x) / sr:.2f} s, {sr} Hz)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
