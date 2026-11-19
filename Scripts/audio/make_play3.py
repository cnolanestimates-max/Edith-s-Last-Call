"""Sounds for Cheyenne's play-test of 2026-11-19 19:33 UTC.  ffmpeg only; nothing generated or paid for.
  frame_fall    a picture frame hitting the floor: wood, then glass (same library)
  music_drone   the bed under the whole house.  The old one (a library track) had a low boom in it about every ten seconds,
                which is the "thudding on a loop" she kept hearing.  This one is a steady synthesized drone: nothing ever hits.
  The exterior beds and bin have their own mastering scripts."""
import os, shutil, subprocess

A = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio"
U = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio_unused"
K = "C:/Users/cheye/OneDrive/Documents/ChatGPT/forklight-tts/Open Game SFX - WAV Library/WAV Files"
os.makedirs(U, exist_ok=True)


def ff(args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + args, check=True, stdin=subprocess.DEVNULL)


def layer(out, parts, tail, level):
    """parts: (file, delay ms, gain, pitch)."""
    args, chains, names = [], [], []
    for i, (f, d, g, p) in enumerate(parts):
        args += ["-i", f]
        chains.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=mono,asetrate=48000*{p},aresample=48000,volume={g},adelay={d}:all=1[a{i}]")
        names.append(f"[a{i}]")
    chains.append("".join(names) + f"amix=inputs={len(parts)}:normalize=0,{tail},loudnorm=I={level}:TP=-1.5:LRA=11")
    ff(args + ["-filter_complex", ";".join(chains), "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", out])


I = K + "/Impacts and Footsteps/"
layer(f"{A}/frame_fall.wav", [
    (f"{A}/wood_hit_far_01.wav", 0, 0.9, 1.3), (I + "impactGlass heavy 001.wav", 60, 1.0, 0.9), (I + "impactGlass medium 003.wav", 210, 0.6, 1.0),
    (I + "impactGlass light 000.wav", 420, 0.4, 1.1), (I + "impactGlass light 003.wav", 700, 0.25, 1.2)], "aecho=0.8:0.4:40|90:0.2|0.1,apad=pad_dur=0.4", -15)

if not os.path.exists(f"{U}/music_drone_old.wav"):
    shutil.copy2(f"{A}/music_drone.wav", f"{U}/music_drone_old.wav")
D = 96
ff(["-f", "lavfi", "-i", f"sine=frequency=55:duration={D}:sample_rate=48000", "-f", "lavfi", "-i", f"sine=frequency=55.6:duration={D}:sample_rate=48000",
    "-f", "lavfi", "-i", f"sine=frequency=82.6:duration={D}:sample_rate=48000", "-f", "lavfi", "-i", f"sine=frequency=110.9:duration={D}:sample_rate=48000",
    "-f", "lavfi", "-i", f"sine=frequency=164.2:duration={D}:sample_rate=48000", "-f", "lavfi", "-i", f"anoisesrc=color=brown:duration={D}:sample_rate=48000:seed=4",
    "-filter_complex",
    "[0:a]volume=0.50[a];[1:a]volume=0.45[b];[2:a]tremolo=f=0.13:d=0.6,volume=0.20[c];[3:a]tremolo=f=0.21:d=0.7,volume=0.10[d];"
    "[4:a]tremolo=f=0.17:d=0.8,volume=0.035[e];[5:a]highpass=f=40,lowpass=f=260,tremolo=f=0.11:d=0.5,volume=0.9[n];"
    f"[a][b][c][d][e][n]amix=inputs=6:normalize=0,aecho=0.8:0.7:480|910:0.35|0.25,afade=t=in:d=3,afade=t=out:st={D - 3}:d=3,loudnorm=I=-27:TP=-6:LRA=4,pan=stereo|c0=c0|c1=c0",
    "-ar", "48000", "-c:a", "pcm_s16le", f"{A}/music_drone.wav"])

for n in ("frame_fall", "music_drone"):
    print(n, os.path.getsize(f"{A}/{n}.wav") // 1000, "KB")
