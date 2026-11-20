"""Split the approved field recordings at pauses, preserving full breaths and their original levels."""
from pathlib import Path

import numpy as np
from scipy.io import wavfile


audio = Path(__file__).resolve().parents[2] / "SourceArt/Audio"
takes = [
    ("steady", "BSB_2195_Man_Breathing_excerpt.wav", (0, 3.825, 7.325, 11.0)),
    ("quick", "BSB_1103_Breathless_Man_excerpt.wav", (0, 2.865, 5.690, 8.4)),
]

for family, source, boundaries in takes:
    rate, field_recording = wavfile.read(audio / "FieldRecordings" / source)
    for i, (begin, end) in enumerate(zip(boundaries, boundaries[1:]), 1):
        take = field_recording[round(begin * rate):round(end * rate)].astype(float)
        # A short edge fade prevents clicks where the microphone's room tone joins.
        fade = np.linspace(0, 1, round(.025 * rate))
        take[:len(fade)] *= fade
        take[-len(fade):] *= fade[::-1]
        wavfile.write(audio / f"deputy_{family}_{i:02}.wav", rate, np.rint(take).astype("<i2"))
