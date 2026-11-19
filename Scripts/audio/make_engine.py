"""The cruiser's engine, third version (Cheyenne, 2026-11-19).

  1. The library cabin hum at -25 LUFS: "too low if it's there at all".
  2. A real Mustang V8 from the Sonniss bundle: on her laptop speakers the body of it (below 200 Hz) cannot be heard at
     all and its exhaust burble is all that is left: "snap, crackle, pop" and "the engine is not there".
  3. This: an engine built from its own harmonics, so that most of what it is sits between 150 Hz and 1.5 kHz where a
     small speaker can play it; a steady pull with a slow drift in the revs, the uneven beat of a V8 in the half orders,
     and no transients at all.  The old cabin and road noise is kept quietly underneath.  -20 LUFS, a 20 s seamless loop.

Run with Blender's Python (numpy):  blender -b --factory-startup -P make_engine.py
Nothing generated or paid for.
"""
import os, shutil, subprocess, wave
import numpy as np

A = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio"
U = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio_unused"
SR, DUR = 48000, 20.0
os.makedirs(U, exist_ok=True)
old = U + "/amb_car_old.wav"
if not os.path.exists(old):
    shutil.copyfile(A + "/amb_car.wav", old)

n = int(SR * DUR)
t = np.arange(n) / SR
rng = np.random.default_rng(1993)
# firing frequency: about 1,400 rpm (4 firings a turn), drifting a few per cent, every drift a whole number of times in the loop
F0 = 92.0
f = F0 * (1.0 + 0.030 * np.sin(2 * np.pi * t / 10.0) + 0.018 * np.sin(2 * np.pi * t / 4.0 + 1.0) + 0.008 * np.sin(2 * np.pi * t / 1.25 + 2.0))
phase = 2 * np.pi * np.cumsum(f) / SR
phase *= (2 * np.pi * round(F0 * DUR / 2) * 2) / phase[-1]            # an even number of whole cycles: the half orders loop too
sig = np.zeros(n)
for k in range(1, 46):                                                 # whole orders: the firing and its harmonics
    fk = F0 * k
    amp = 1.0 / k ** 0.85
    amp *= 0.55 + 1.1 * np.exp(-((fk - 230.0) / 150.0) ** 2) + 0.9 * np.exp(-((fk - 560.0) / 260.0) ** 2) + 0.5 * np.exp(-((fk - 1150.0) / 420.0) ** 2)
    if fk < 130.0:
        amp *= 0.5                                                     # the part a laptop cannot play is not what it is built on
    sig += amp * np.sin(k * phase + rng.uniform(0, 2 * np.pi))
for k in (0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5):                           # half orders: the lope of a V8
    fk = F0 * k
    amp = 0.38 / (k + 0.5) ** 0.7 * (0.6 + np.exp(-((fk - 300.0) / 220.0) ** 2))
    sig += amp * np.sin(k * phase + rng.uniform(0, 2 * np.pi))
sig *= 1.0 + 0.10 * np.sin(0.5 * phase) + 0.05 * np.sin(2 * np.pi * t / 2.5)        # the beat, and a slow breathing
# air: intake and fan, shaped noise that rides with the firing (periodic, because it is built in the frequency domain)
spec = rng.normal(size=n // 2 + 1) + 1j * rng.normal(size=n // 2 + 1)
fr = np.fft.rfftfreq(n, 1 / SR)
spec = spec * (np.exp(-((fr - 700.0) / 650.0) ** 2) + 0.35 * np.exp(-((fr - 2200.0) / 900.0) ** 2))
air = np.fft.irfft(spec, n)
air /= np.abs(air).max()
sig = sig / np.abs(sig).max() + 0.16 * air * (0.7 + 0.3 * np.sin(phase))
sig = np.tanh(1.6 * sig) / np.tanh(1.6)                                 # a little grit, no peaks
sig *= 0.125 / np.sqrt(np.mean(sig ** 2))
tmp = A + "/raw_lib/_eng_synth.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(sig, -1, 1) * 32767).astype("<i2").tobytes())


def ff(args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + args, check=True, stdin=subprocess.DEVNULL)


# the engine a little wide, over the old cabin noise looped to the same twenty seconds across its own ends
cab = A + "/raw_lib/_cab.wav"
ff(["-i", old, "-t", "22", "-af", "aformat=channel_layouts=stereo,lowpass=f=2500", "-ar", "48000", cab])
cab2 = A + "/raw_lib/_cab_loop.wav"
ff(["-i", cab, "-filter_complex",
    "[0]atrim=0:2,asetpts=PTS-STARTPTS[head];[0]atrim=2:20,asetpts=PTS-STARTPTS[body];[0]atrim=20:22,asetpts=PTS-STARTPTS[tail];"
    "[tail][head]acrossfade=d=2:c1=qsin:c2=qsin[seam];[body][seam]concat=n=2:v=0:a=1[o]", "-map", "[o]", "-ar", "48000", cab2])
mix = A + "/raw_lib/_eng_mix.wav"
ff(["-i", tmp, "-i", cab2, "-filter_complex",
    "[0]aformat=channel_layouts=mono,asplit=2[l][r];[r]adelay=9:all=1[rd];[l][rd]join=inputs=2:channel_layout=stereo[e];"
    "[1]volume=0.30[c];[e][c]amix=inputs=2:normalize=0:duration=first[o]",
    "-map", "[o]", "-t", "20", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", mix])
# one gain for the whole file (loudnorm would breathe and break the seam): measure, then set
r = subprocess.run(["ffmpeg", "-nostdin", "-i", mix, "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
lufs = float([l for l in r.stderr.splitlines() if l.strip().startswith("I:")][-1].split()[1])
ff(["-i", mix, "-af", f"volume={-20.0 - lufs:.2f}dB", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", A + "/amb_car.wav"])
for p in (tmp, cab, cab2, mix):
    os.remove(p)
r = subprocess.run(["ffmpeg", "-nostdin", "-i", A + "/amb_car.wav", "-af", "ebur128=framelog=quiet,astats=metadata=0", "-f", "null", "-"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
print("ENGINE", [l.strip() for l in r.stderr.splitlines() if l.strip().startswith("I:") or "Peak level dB" in l][-3:])
