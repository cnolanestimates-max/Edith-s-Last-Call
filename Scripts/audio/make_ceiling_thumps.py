"""Cut three close, dry joist impacts for the ceiling crawl from the game's wooden hits."""
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile


AUDIO = Path(__file__).resolve().parents[2] / "SourceArt/Audio"
RATE = 48000
SECONDS = np.arange(round(.23 * RATE)) / RATE


def cut_hit(name, onset, speed, band):
    rate, pcm = wavfile.read(AUDIO / f"{name}.wav")
    samples = pcm.astype(float) / 32768
    clip = np.interp((onset + SECONDS * speed) * rate, np.arange(len(samples)), samples)
    filtered = signal.sosfilt(signal.butter(2, band, fs=RATE, btype="bandpass", output="sos"), clip)
    return filtered / np.max(np.abs(filtered))


# A single dry wooden strike supplies the leading knock. Give each take the
# weight of a different overhead impact and damp the board before the next plant.
for index, (body, onset, speed) in enumerate((
    ("thump_heavy", .025, .94),
    ("thump_far_01", .042, 1.03),
    ("thump_far_02", .009, .88),
), 1):
    wood = cut_hit("wood_hit_far_01", 2.269, speed, (110, 2500))
    weight = cut_hit(body, onset, speed, (42, 470))
    impact = .69 * wood * np.exp(-SECONDS / .065) + weight * np.exp(-SECONDS / .076)
    impact *= np.minimum(SECONDS / .0015, 1) * np.minimum((SECONDS[-1] - SECONDS) / .022, 1)
    impact = np.tanh(1.4 * impact)
    impact *= .93 / np.max(np.abs(impact))
    wavfile.write(AUDIO / f"ceiling_thump_{index:02d}.wav", RATE, np.rint(impact * 32767).astype("<i2"))
