"""Cut individual contacts from Pixabay's Walking on Wooden Floor for the ceiling crawl."""

import argparse
from pathlib import Path
import subprocess

import numpy as np
from scipy import signal
from scipy.io import wavfile


RATE = 48000
OUTPUT = Path(__file__).resolve().parents[2] / "SourceArt/Audio"
PITCH_RATIO = .90
TEMPO_RATIO = 1.10
STEP_PEAKS = (.185, .655, 1.105, 1.660, 2.675, 3.235)
HIT_SECONDS = .190
BASS_BOOST = .58


def cut_step(recording, peak):
    # Locate each contact on the retimed recording and trim the gap before it.
    start = round((peak - .11) * RATE)
    window = recording[start:round((peak + .020) * RATE)]
    rms = np.sqrt(np.convolve(window**2, np.ones(144) / 144, "same"))
    onset = start + int(np.flatnonzero(rms > rms.max() * .14)[0])
    onset -= round(.004 * RATE)
    step = recording[onset:onset+round(HIT_SECONDS * RATE)].copy()
    fade_in = round(.003 * RATE)
    fade_out = round(.032 * RATE)
    step[:fade_in] *= np.linspace(0, 1, fade_in)
    step[-fade_out:] *= np.linspace(1, 0, fade_out)
    rms = np.sqrt(np.mean(step[:round(.085 * RATE)]**2))
    step *= min(.89 / np.max(np.abs(step)), .265 / rms)

    # Bring the low end up by about half after the filter and peak limiter.
    bass_filter = signal.butter(2, 170, fs=RATE, btype="lowpass", output="sos")
    bass = signal.sosfiltfilt(bass_filter, step)
    bass[:fade_in] *= np.linspace(0, 1, fade_in)
    bass[-fade_out:] *= np.linspace(1, 0, fade_out)
    step += BASS_BOOST * bass

    # Tame peaks after the boost so the transient keeps its shape below the knee.
    magnitude = np.abs(step)
    over = magnitude > .76
    step[over] = np.sign(step[over]) * (.76 + .19 * np.tanh((magnitude[over] - .76) / .19))
    return step


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("walking_on_wooden_floor_mp3", type=Path)
    args = parser.parse_args()
    # Resampling sets the pitch, then atempo restores the desired faster tempo.
    filters = (
        f"aresample={RATE},asetrate={round(RATE * PITCH_RATIO)},aresample={RATE},"
        f"atempo={TEMPO_RATIO / PITCH_RATIO:.6f},bass=f=105:g=2"
    )
    raw = subprocess.check_output([
        "ffmpeg", "-nostdin", "-v", "error", "-i", str(args.walking_on_wooden_floor_mp3),
        "-af", filters, "-ac", "1", "-f", "f32le", "-",
    ])
    recording = np.frombuffer(raw, dtype="<f4")
    if not 3.4 <= len(recording) / RATE <= 3.7:
        parser.error("Expected Walking on Wooden Floor (Pixabay recording 94493).")

    for i, peak in enumerate(STEP_PEAKS, 1):
        step = cut_step(recording, peak)
        wavfile.write(OUTPUT / f"ceiling_boot_step_{i:02d}.wav", RATE,
                      np.rint(step * 32767).astype("<i2"))


if __name__ == "__main__":
    main()
