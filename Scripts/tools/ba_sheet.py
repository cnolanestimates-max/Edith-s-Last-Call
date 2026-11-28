"""Before / after pictures side by side, labelled, from two folders of same-named screenshots.

  python ba_sheet.py <before dir> <after dir> <out dir> [--width 960] [--pairs-per-sheet 3] [--only a,b,c] [--gamma 1.0]
Writes <out dir>/pair_<name>.jpg for every shot and sheets sheet_1.jpg ... of a few pairs each (ffmpeg)."""
import os, subprocess, sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
opt = {sys.argv[i][2:]: sys.argv[i + 1] for i in range(len(sys.argv) - 1) if sys.argv[i].startswith("--")}
B, A, OUT = args[:3]
W = int(opt.get("width", 960))
PER = int(opt.get("pairs-per-sheet", 3))
GAMMA = float(opt.get("gamma", 1.0))
ONLY = [s for s in opt.get("only", "").split(",") if s]
FONT = "C\\:/Windows/Fonts/arialbd.ttf"
os.makedirs(OUT, exist_ok=True)
names = sorted(f for f in os.listdir(B) if f.lower().endswith(".png") and os.path.exists(os.path.join(A, f)))
if ONLY:
    names = [n for n in names if any(o in n for o in ONLY)]
pairs = []
for n in names:
    title = n[:-4].split("_", 1)[-1].replace("_", " ")
    out = os.path.join(OUT, f"pair_{n[:-4]}.jpg")
    eq = f",eq=gamma={GAMMA}" if GAMMA != 1.0 else ""

    def lab(text, col):
        return f"drawtext=fontfile='{FONT}':text='{text}':x=18:y=14:fontsize=34:fontcolor={col}:box=1:boxcolor=black@0.55:boxborderw=8"
    f = (f"[0:v]scale={W}:-1{eq},{lab('BEFORE', '0xd96a5a')}[a];[1:v]scale={W}:-1{eq},{lab('AFTER', '0x7fd08a')},"
         f"drawtext=fontfile='{FONT}':text='{title}':x=w-text_w-18:y=h-text_h-16:fontsize=26:fontcolor=0xe8e2d0:box=1:boxcolor=black@0.55:boxborderw=6[b];"
         f"[a][b]hstack=inputs=2[v]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(B, n), "-i", os.path.join(A, n), "-filter_complex", f, "-map", "[v]",
                    "-frames:v", "1", "-q:v", "3", out], check=True)
    pairs.append(out)
for k in range(0, len(pairs), PER):
    grp = pairs[k:k + PER]
    out = os.path.join(OUT, f"sheet_{k // PER + 1}.jpg")
    if len(grp) == 1:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", grp[0], "-frames:v", "1", "-q:v", "3", out], check=True)
        continue
    ins = []
    for g in grp:
        ins += ["-i", g]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y"] + ins + ["-filter_complex", f"vstack=inputs={len(grp)}", "-frames:v", "1", "-q:v", "3", out], check=True)
print(len(pairs), "pairs,", (len(pairs) + PER - 1) // PER, "sheets in", OUT)
