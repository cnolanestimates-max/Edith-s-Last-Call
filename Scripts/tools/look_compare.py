"""Side-by-side comparison videos for the look previews (Cheyenne, 2026-11-23): the game as it is on the left, the new
look on the right, every walk of the tour in turn.  Frames come from a -WCLookTour run per version (Saved/look/<version>/
<walk>/f_00000.png).
python look_compare.py [looks...]   ->   Saved/look/compare_<look>.mp4
python look_compare.py --three <a> <b> <title a> <title b> <out>   ->   original | a | b in one row"""
import os, subprocess, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Saved", "look")
FONT = "C\\:/Windows/Fonts/arialbd.ttf"
NAMES = {"lighting": "NEW LIGHTING (bounce light, thicker air, moonlight shafts)", "grade": "NEW COLOUR GRADE (cold shadows, warm highlights, grain, eye adjustment)",
         "camera": "NEW CAMERA FEEL (head bob, sway, step nod, breathing, motion blur)"}


def label(text, x):
    t = text.replace(":", "\\:").replace("'", "")
    return f"drawbox=x={x}:y=0:w=960:h=34:color=black@0.65:t=fill,drawtext=fontfile='{FONT}':text='{t}':x={x}+12:y=9:fontsize=17:fontcolor=white"


def walk_clip(look, walk, out):
    a = os.path.join(ROOT, "base", walk, "f_%05d.png")
    b = os.path.join(ROOT, look, walk, "f_%05d.png")
    n = min(len(os.listdir(os.path.join(ROOT, "base", walk))), len(os.listdir(os.path.join(ROOT, look, walk))))
    nice = walk.split("_", 1)[1].replace("_", " ")
    fc = (f"[0:v]scale=960:540,{label('ORIGINAL  -  ' + nice, 0)}[l];"
          f"[1:v]scale=960:540,{label(NAMES[look], 0)}[r];[l][r]hstack=inputs=2,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", a, "-framerate", "30", "-i", b, "-frames:v", str(n),
                    "-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-crf", "19", "-preset", "medium", out], check=True)


def label_w(text, x, w):
    t = text.replace(":", "\\:").replace("'", "")
    return f"drawbox=x={x}:y=0:w={w}:h=30:color=black@0.65:t=fill,drawtext=fontfile='{FONT}':text='{t}':x={x}+10:y=8:fontsize=15:fontcolor=white"


def three(a, b, ta, tb, out_name):
    parts = []
    for w in sorted(os.listdir(os.path.join(ROOT, "base"))):
        srcs = [os.path.join(ROOT, v, w, "f_%05d.png") for v in ("base", a, b)]
        n = min(len(os.listdir(os.path.join(ROOT, v, w))) for v in ("base", a, b))
        nice = w.split("_", 1)[1].replace("_", " ")
        fc = (f"[0:v]scale=640:360,{label_w('ORIGINAL  -  ' + nice, 0, 640)}[x];[1:v]scale=640:360,{label_w(ta, 0, 640)}[y];"
              f"[2:v]scale=640:360,{label_w(tb, 0, 640)}[z];[x][y][z]hstack=inputs=3,format=yuv420p[v]")
        p = os.path.join(ROOT, f"_part3_{w}.mp4")
        cmd = ["ffmpeg", "-y", "-loglevel", "error"]
        for s_ in srcs:
            cmd += ["-framerate", "30", "-i", s_]
        subprocess.run(cmd + ["-frames:v", str(n), "-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-crf", "19", "-preset", "medium", p], check=True)
        parts.append(p)
    lst = os.path.join(ROOT, "_list3.txt")
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    out = os.path.join(ROOT, out_name)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
    for p in parts:
        os.remove(p)
    os.remove(lst)
    print("LOOK compare", os.path.abspath(out), round(os.path.getsize(out) / 1e6, 1), "MB")


def main():
    if sys.argv[1:2] == ["--three"]:
        three(*sys.argv[2:7])
        return
    looks = sys.argv[1:] or ["lighting", "grade", "camera"]
    walks = sorted(os.listdir(os.path.join(ROOT, "base")))
    for look in looks:
        parts = []
        for w in walks:
            if not os.path.isdir(os.path.join(ROOT, look, w)):
                continue
            p = os.path.join(ROOT, f"_part_{look}_{w}.mp4")
            walk_clip(look, w, p)
            parts.append(p)
        lst = os.path.join(ROOT, f"_list_{look}.txt")
        open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
        out = os.path.join(ROOT, f"compare_{look}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
        for p in parts:
            os.remove(p)
        os.remove(lst)
        print("LOOK compare", os.path.abspath(out), round(os.path.getsize(out) / 1e6, 1), "MB")


main()
