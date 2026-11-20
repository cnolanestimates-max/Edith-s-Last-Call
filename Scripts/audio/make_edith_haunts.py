"""Make short nonverbal one-shots from Edith's original, unlayered performances."""
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

AUDIO = Path(__file__).resolve().parents[2] / "SourceArt/Audio"
# Source seconds, pitch ratio, passband (Hz), mastered peak (dBFS).
TAKES = {
    "snicker_01": ("laugh1", .02, .73, 1.02, (560, 5700), -11),
    "snicker_02": ("laugh2", .91, 2.20, .98, (490, 4900), -12),
    "whimper_01": ("cry1", 1.47, 2.25, 1.12, (240, 4200), -6),
    "whimper_02": ("cry2", .18, 1.06, 1.06, (200, 4700), -6),
    "groan_01": ("moan2", 2.14, 4.31, .82, (73, 2400), -5),
    "groan_02": ("moan1", .15, 1.72, .85, (78, 2600), -6),
}


def band(x, hz, rate):
    return signal.sosfilt(signal.butter(3, hz, fs=rate, btype="bandpass", output="sos"), x)


def render(name, take):
    source, start, end, pitch, hz, peak = take
    sr, pcm = wavfile.read(AUDIO / "VO_dry" / f"m_{source}.wav")
    x = pcm[round(start*sr):round(end*sr)].astype(float) / 32768
    x = signal.resample(x, round(len(x) * 48000 / (sr * pitch)))
    x = band(x, hz, 48000)
    if name.startswith("snicker"):
        # Whisper the original cadence. Each frequency band's breath follows that
        # band in her performance, retaining mouth shape between the little pulses.
        rng = np.random.default_rng(810 + int(name[-2:]))
        air = rng.standard_normal(len(x))
        breath = np.zeros_like(x)
        envelope = signal.butter(2, 34, fs=48000, output="sos")
        for lo, hi in zip([480, 780, 1250, 2050, 3050], [780, 1250, 2050, 3050, 5900]):
            dynamics = np.sqrt(np.maximum(0, signal.sosfiltfilt(envelope, band(x, (lo, hi), 48000)**2)))
            carrier = band(air, (lo, hi), 48000)
            breath += carrier * dynamics / np.std(carrier)
        x = breath * .85 + x * .15
    elif name.startswith("groan"):
        x = np.tanh(x * 4.5)
    fade = np.sin(np.linspace(0, np.pi / 2, 1440))**2
    x[:len(fade)] *= fade
    x[-len(fade):] *= fade[::-1]
    x *= 10**(peak / 20) / max(abs(x))
    wavfile.write(AUDIO / "VO" / f"edith_{name}.wav", 48000, np.round(x * 32767).astype(np.int16))


if __name__ == "__main__":
    for name, take in TAKES.items():
        render(name, take)
