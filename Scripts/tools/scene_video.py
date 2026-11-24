"""Turn a recorded scene into a video with its sound (2026-11-24, for the stairwell scene).

A frame-by-frame run (-UseFixedTimeStep -FPS=30, rec:<name> step) is slower than real time, so its own sound is useless;
the sound comes from a second, real-time run of the same scripted scene with -WCNoFrames.  Both logs print
"WCREC start t=" (game time when the frames start) and the sound run prints "WCMIX start t=" (when its mix starts), so
the mix is cut to line up with frame 0.

python scene_video.py <frames dir> <out.mp4> [--mix <mix.wav> --mixlog <audio run log> [--framelog <frame run log>]]
                      [--start s] [--end s] [--small]
With --framelog the two runs are also lined up on every scene beat both logs print (WCSCARE / WCMEMORY lines, in order):
the sound between two beats is stretched or squeezed to fit the picture, so a chase that ran a second longer in one run
still lands its grab on the frame.
"""
import argparse, os, re, shutil, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("frames")
ap.add_argument("out")
ap.add_argument("--mix")
ap.add_argument("--mixlog")
ap.add_argument("--framelog")
ap.add_argument("--gain", type=float, default=6.0, help="dB added to the game mix (then limited), for listening on a phone")
ap.add_argument("--start", type=float, default=0.0)
ap.add_argument("--end", type=float, default=0.0)
ap.add_argument("--small", action="store_true", help="also write <out>_small.mp4 under 20 MB for chat")
a = ap.parse_args()

# a frame request now and then is dropped: repeat the one before so the timing holds
have = sorted(int(f[2:7]) for f in os.listdir(a.frames) if f.startswith("f_") and f.endswith(".png"))
filled = 0
for i in range(have[0] + 1, have[-1]):
    p = os.path.join(a.frames, "f_%05d.png" % i)
    if not os.path.exists(p):
        shutil.copy(os.path.join(a.frames, "f_%05d.png" % (i - 1)), p)
        filled += 1
n = have[-1] + 1
print(f"frames {n} ({n / 30:.1f} s), filled {filled}")

cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", os.path.join(a.frames, "f_%05d.png")]
offset = 0.0
if a.mix:
    txt = open(a.mixlog, encoding="utf-8", errors="replace").read()
    mix0 = float(re.search(r"WCMIX start t=([\d.]+)", txt).group(1))
    rec0 = float(re.search(r"WCREC start t=([\d.]+)", txt).group(1))
    offset = rec0 - mix0
    print(f"mix offset {offset:.3f} s")
    mix_in = a.mix
    if a.framelog:
        ftxt = open(a.framelog, encoding="utf-8", errors="replace").read()
        frec0 = float(re.search(r"WCREC start t=([\d.]+)", ftxt).group(1))
        beat = r"(WCSCARE t=([\d.]+) (\S+ \S+)|WCMEMORY t=([\d.]+) (\d+))"
        def beats(t):
            return [((m.group(3) or "mem" + m.group(5)), float(m.group(2) or m.group(4))) for m in re.finditer(beat, t)]
        fb, ab = beats(ftxt), beats(txt)
        pairs, j = [(0.0, rec0 - mix0)], 0
        for name, ft in fb:
            while j < len(ab) and ab[j][0] != name:
                j += 1
            if j < len(ab):
                pairs.append((ft - frec0, ab[j][1] - mix0))
                j += 1
        print("beats", [(round(v, 2), round(x, 2)) for v, x in pairs])
        parts = []
        tmp = a.out + "_seg"
        os.makedirs(tmp, exist_ok=True)
        pairs.append((n / 30.0 + 5, pairs[-1][1] + (n / 30.0 + 5 - pairs[-1][0])))
        for k in range(len(pairs) - 1):
            (v0, x0), (v1, x1) = pairs[k], pairs[k + 1]
            if v1 <= v0 or x1 <= x0:
                continue
            r = (x1 - x0) / (v1 - v0)
            seg = os.path.join(tmp, f"s{k:02d}.wav")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{x0:.4f}", "-t", f"{x1 - x0:.4f}", "-i", a.mix, "-af",
                            f"atempo={min(max(r, 0.5), 2.0):.5f}", "-ar", "48000", "-ac", "2", seg], check=True)
            parts.append(seg)
        lst = os.path.join(tmp, "list.txt")
        open(lst, "w").write("".join("file '" + os.path.abspath(p_).replace("\\", "/") + "'\n" for p_ in parts))
        mix_in = os.path.join(tmp, "mix_fit.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, mix_in], check=True)
        cmd += ["-ss", f"{a.start:.3f}", "-i", mix_in]
    else:
        cmd += ["-ss", f"{offset + a.start:.3f}", "-i", mix_in]
vf = []
if a.start or a.end:
    vf.append(f"trim=start={a.start}" + (f":end={a.end}" if a.end else "") + ",setpts=PTS-STARTPTS")
vf.append("format=yuv420p")
cmd += ["-filter:v", ",".join(vf)]
if a.mix:
    cmd += ["-map", "0:v", "-map", "1:a", "-filter:a", f"volume={a.gain}dB,alimiter=limit=0.95", "-c:a", "aac", "-b:a", "192k", "-shortest"]
cmd += ["-c:v", "libx264", "-crf", "18", "-preset", "medium", "-movflags", "+faststart", a.out]
subprocess.run(cmd, check=True)
print("VIDEO", os.path.abspath(a.out), round(os.path.getsize(a.out) / 1e6, 1), "MB")

if a.small:
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.out],
                               capture_output=True, text=True).stdout.strip())
    kbps = int(18.5 * 8000 / dur) - 128                     # aim under 19 MB with the sound
    small = a.out[:-4] + "_small.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.out, "-c:v", "libx264", "-b:v", f"{kbps}k", "-maxrate", f"{int(kbps * 1.3)}k",
                    "-bufsize", f"{kbps * 2}k", "-preset", "slow", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", small], check=True)
    print("SMALL", os.path.abspath(small), round(os.path.getsize(small) / 1e6, 1), "MB")
