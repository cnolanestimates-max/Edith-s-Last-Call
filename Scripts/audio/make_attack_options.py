"""Edith's grab: five listening options for the attack sound (2026-11-24, Cheyenne: "give me a few different sounds ...
screaming witch sounds, some demonic attack sounds ... sound effect plus music plus ambience").

Each option is 7 s: two seconds of the hall (ambience, the low music), then the attack at 2.0 s, then the tail.  The
result is one video, a title card per option, so it can be heard on a phone: Saved/attack_options.mp4.
python make_attack_options.py <dir with the library sources>   (the copied Sonniss / CC0 creature files and the two
Higgsfield takes, names as below)
"""
import os, subprocess, sys

SRC = sys.argv[1]
GAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "SourceArt", "Audio")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Saved", "attack_options")
HF = "C:/Users/cheye/Documents/LocalAI/Higgsfield/wellness_stairs"
FONT = "C\\:/Windows/Fonts/arialbd.ttf"
os.makedirs(OUT, exist_ok=True)


def g(n):
    return os.path.join(GAME, n)


def s(n):
    return os.path.join(SRC, n)


# (title, ambience, music, [(file, start s, gain dB, pitch factor)])
OPTIONS = [
    ("1  Witch shriek", g("amb_house.wav"), g("music_drone.wav"),
     [(HF + "/witch_shriek.mp3", 2.0, 6, 1.0), (g("her_scream_short_01.wav"), 2.05, -9, 1.18), (g("sting_noisebox.wav"), 2.0, -6, 1.0)]),
    ("2  Demonic attack", g("amb_wind.wav"), g("music_low.wav"),
     [(HF + "/demon_attack.mp3", 2.0, 0, 1.0), (s("Demon Growl.wav"), 1.9, -4, 0.8),
      (s("GORESplt_Gore Designed Transient Heavy Impact Smash 01_ESM_HALG.wav"), 2.0, -3, 1.0), (g("sting_braam.wav"), 2.0, -8, 1.0)]),
    ("3  Screech in the dark (quiet before, harsh close)", None, g("music_drone.wav"),
     [(s("HMNBrth_Construction Kit Male Screeching Breath Inhale Weak Squeal 05_ESM_HC4.wav"), 1.75, 0, 0.9),
      (s("DSGNEthr_Jumpscare Vocal Aggressive Whisper Harsh Distortion 02_ESM_HALG.wav"), 2.0, -1, 1.0),
      (s("DSGNErie_NoiseBoxHit_36_InMotionAudio_SinisterTextures4.wav"), 2.0, -8, 1.0)]),
    ("4  Banshee wail", g("amb_house.wav"), g("music_drone.wav"),
     [(s("scream_01.ogg"), 2.0, -2, 1.0), (g("her_scream_02.wav"), 2.0, -4, 1.25), (s("scream_02.ogg"), 2.55, -6, 0.92),
      (s("CREAMnstr_Designed Sea Beast Creature Pain Intense Yell Long 04_ESM_HC4.wav"), 2.1, -12, 1.0), (g("sting_rise.wav"), 1.6, -10, 1.0)]),
    ("5  Current sound, for comparison", g("amb_house.wav"), g("music_drone.wav"),
     [(g("her_scream_01.wav"), 2.0, 0, 1.0), (g("sting_hit.wav"), 2.0, 0, 1.0)]),
]

parts = []
for i, (title, amb, mus, layers) in enumerate(OPTIONS):
    wav = os.path.join(OUT, f"option_{i + 1}.wav")
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    fc, mix, n = [], [], 0
    for path, vol in ((amb, -20), (mus, -22)):
        if not path:
            continue
        cmd += ["-stream_loop", "-1", "-i", path]
        fc.append(f"[{n}:a]atrim=0:7,aformat=sample_rates=48000:channel_layouts=stereo,volume={vol}dB,afade=t=out:st=5.5:d=1.5[b{n}]")
        mix.append(f"[b{n}]")
        n += 1
    for path, at, gain, pitch in layers:
        cmd += ["-i", path]
        p = f"asetrate=48000*{pitch},aresample=48000," if pitch != 1.0 else ""
        fc.append(f"[{n}:a]aresample=48000,{p}aformat=sample_rates=48000:channel_layouts=stereo,volume={gain}dB,adelay={int(at * 1000)}|{int(at * 1000)}[l{n}]")
        mix.append(f"[l{n}]")
        n += 1
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0,atrim=0:7,alimiter=limit=0.95[m]")
    subprocess.run(cmd + ["-filter_complex", ";".join(fc), "-map", "[m]", wav], check=True)
    mp4 = os.path.join(OUT, f"option_{i + 1}.mp4")
    t = title.replace(":", "\\:")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=7:r=30", "-i", wav,
                    "-vf", f"drawtext=fontfile='{FONT}':text='{t}':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=44:fontcolor=white",
                    "-c:v", "libx264", "-crf", "28", "-c:a", "aac", "-b:a", "192k", "-shortest", mp4], check=True)
    parts.append(mp4)
lst = os.path.join(OUT, "list.txt")
open(lst, "w").write("".join("file '" + os.path.abspath(p).replace("\\", "/") + "'\n" for p in parts))
final = os.path.join(OUT, "..", "attack_options.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final], check=True)
print("OPTIONS", os.path.abspath(final), round(os.path.getsize(final) / 1e6, 1), "MB")
