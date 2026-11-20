"""Cut the game's licensed male pant into individual resting and frightened breaths."""
from pathlib import Path
import subprocess

import numpy as np
from scipy import signal
from scipy.io import wavfile


audio = Path(__file__).resolve().parents[2] / "SourceArt/Audio"
rate, original = wavfile.read(audio / "deputy_pant.wav")
original = original.astype(float) / 32768


def shape(start, end, tempo, cutoff, rms):
    samples = original[round(start * rate):round(end * rate)]
    result = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-f", "f32le", "-ar", str(rate), "-ac", "1",
         "-i", "pipe:0", "-af", f"atempo={tempo}", "-f", "f32le", "pipe:1"],
        input=samples.astype("<f4").tobytes(), stdout=subprocess.PIPE, check=True)
    take = np.frombuffer(result.stdout, dtype="<f4").astype(float)
    band = signal.butter(2, [105, cutoff], btype="bandpass", fs=rate, output="sos")
    take = signal.sosfilt(band, take)
    edge = round(.022 * rate)
    take[:edge] *= np.linspace(0, 1, edge)
    take[-edge:] *= np.linspace(1, 0, edge)
    return take * rms / np.sqrt(np.mean(take ** 2))


# The softer intake and the voiced outward puff have different envelopes.
for i, (inhale, exhale) in enumerate([
    ((.52, .95), (1.15, 1.70)),
    ((1.72, 2.16), (2.47, 3.09)),
    ((3.11, 3.58), (3.85, 4.50)),
], 1):
    for family in ("steady", "quick"):
        rest = family == "steady"
        intake = shape(*inhale, .57 if rest else 1.16, 2400 if rest else 4300, .092)
        release = shape(*exhale, .56 if rest else 1.27, 2100 if rest else 3900, .122)
        if rest:
            # Soften the sharp attack of the pant into an easy release.
            ramp = np.clip(np.arange(len(release)) / (.18 * rate), 0, 1)
            release *= .18 + .82 * ramp
        elif i == 3:
            # A catch midway through this exhale leaves two distinct puffs of air.
            t = np.arange(len(release)) / rate
            release *= 1 - .96 * np.exp(-((t - .157) / .047) ** 4)
        gap = np.zeros(round((.14 if rest else .065) * rate))
        breath = np.concatenate((intake, gap, release))
        breath *= min(1., .86 / np.max(np.abs(breath)))
        wavfile.write(audio / f"deputy_{family}_{i:02}.wav", rate, (breath * 32767).astype("<i2"))
