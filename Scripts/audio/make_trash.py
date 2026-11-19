"""The bin going over (Cheyenne, 2026-11-19 21:31 UTC: "the loud sound, banging sound, clanging sound of a big trash
can ... a loud knocking over with it skittering").  ffmpeg only, from the Open Game SFX library (Kenney packs, CC0).

  trash_crash   one heavy hollow hit as the bin lands (wood and punch pitched far down), the lid slapping the ground, a
                clang of everything metal in it, bottles, then four seconds of cans and lids skittering away over the
                dirt and settling.  Mastered hot (-9 LUFS): it is the first thing in the game meant to make him jump.
The heavy feet running off afterwards are the game's own her_step, played along the back of the house (WCStory.cpp)."""
import os, subprocess

A = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio"
K = "C:/Users/cheye/OneDrive/Documents/ChatGPT/forklight-tts/Open Game SFX - WAV Library/WAV Files"
I = K + "/Impacts and Footsteps/"
R = K + "/RPG Audio/"


def ff(args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + args, check=True, stdin=subprocess.DEVNULL)


parts = [  # (file, delay ms, gain, pitch)
    (I + "impactWood heavy 002.wav", 0, 1.6, 0.34), (I + "impactPunch heavy 001.wav", 0, 1.4, 0.40), (I + "impactSoft heavy 003.wav", 20, 1.2, 0.45),      # the body of it landing
    (I + "impactMetal heavy 002.wav", 30, 1.3, 0.50), (I + "impactMetal heavy 004.wav", 110, 1.1, 0.62), (I + "impactBell heavy 001.wav", 60, 0.35, 0.55),   # the clang
    (I + "impactPlate heavy 000.wav", 260, 1.0, 0.55), (I + "impactWood heavy 000.wav", 300, 0.9, 0.5),                                                   # the lid, flat on the ground
    (R + "metalPot1.wav", 180, 0.9, 0.55), (R + "metalPot2.wav", 420, 0.8, 0.62), (I + "impactTin medium 001.wav", 520, 0.9, 0.8),
    (I + "impactGlass heavy 001.wav", 380, 0.7, 0.85), (I + "impactGlass medium 002.wav", 640, 0.5, 0.95), (I + "impactGlass light 003.wav", 900, 0.4, 1.05),
]
# the skitter: tins and lids rolling off and coming to rest, quicker at first, then spaced out
t = 700
for k in range(18):
    f = I + ("impactTin medium %03d.wav" % (k % 5) if k % 3 else "impactMetal light %03d.wav" % (k % 5))
    parts.append((f, t, max(0.16, 0.75 - 0.035 * k), 0.85 + 0.03 * (k % 6)))
    t += 110 + 22 * k
args, chains, names = [], [], []
for i, (f, d, g, p) in enumerate(parts):
    args += ["-i", f]
    chains.append(f"[{i}:a]aformat=sample_rates=48000:channel_layouts=mono,asetrate=48000*{p},aresample=48000,volume={g},adelay={d}:all=1[a{i}]")
    names.append(f"[a{i}]")
chains.append("".join(names) + f"amix=inputs={len(parts)}:normalize=0,aecho=0.8:0.55:60|140|260:0.3|0.2|0.12,bass=g=4:f=70,apad=pad_dur=0.8,"
              "acompressor=threshold=-18dB:ratio=4:attack=2:release=200:makeup=6,loudnorm=I=-9:TP=-0.8:LRA=14")
ff(args + ["-filter_complex", ";".join(chains), "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", f"{A}/trash_crash.wav"])
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{A}/trash_crash.wav"], capture_output=True, text=True)
print("trash_crash", r.stdout.strip(), "s")
