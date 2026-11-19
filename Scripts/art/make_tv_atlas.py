"""Turns each finished tape (SourceArt/TV/tape_<name>.mp4) into what the game plays on the television:
  SourceArt/TV/T_Tape_<n>.png      240 frames (12 a second for 20 s), 256x192 each, in a sheet 16 across and 15 down
  SourceArt/Audio/tv_tape_<n>.wav  its sound, mono
The order of the tapes is the order they play in the game.  ffmpeg only."""
import os, subprocess

ROOT = "C:/GameDev/Unreal/WellnessCheck/SourceArt"
ORDER = ["bedtime8", "living8", "porch8"]      # the moving versions Cheyenne asked for (2026-11-19 05:24 to 05:55 UTC); everything else is retired
n = 0
for name in ORDER:
    src = f"{ROOT}/TV/tape_{name}.mp4"
    if not os.path.exists(src):
        print("no tape yet:", name)
        continue
    n += 1
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-vf", "fps=12,scale=256:192,tile=16x15", "-frames:v", "1", "-update", "1",
                    f"{ROOT}/TV/T_Tape_{n}.png"], check=True, stdin=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le",
                    f"{ROOT}/Audio/tv_tape_{n}.wav"], check=True, stdin=subprocess.DEVNULL)
    print(f"tape {n}: {name}", os.path.getsize(f"{ROOT}/TV/T_Tape_{n}.png") // 1000, "KB")
for k in range(n + 1, 9):
    for stale in (f"{ROOT}/TV/T_Tape_{k}.png", f"{ROOT}/Audio/tv_tape_{k}.wav"):
        if os.path.exists(stale):
            os.remove(stale)
            print("retired", stale)
print(n, "tapes")
