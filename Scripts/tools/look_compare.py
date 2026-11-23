"""Side-by-side comparison videos for the look previews (Cheyenne, 2026-11-23): the game as it is on the left, the new
look on the right, every walk of the tour in turn.  Frames come from a -WCLookTour run per version (Saved/look/<version>/
<walk>/f_00000.png).
python look_compare.py [looks...]   ->   Saved/look/compare_<look>.mp4"""
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


def main():
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
