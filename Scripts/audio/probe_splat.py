"""Find the separate hits inside a library file (prints start/end of each non-silent stretch)."""
import os, re, subprocess, sys, zipfile
LIB = "C:/Users/cheye/OneDrive/Documents/ChatGPT/forklight-tts"
RAW = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio/raw_lib"
bundle, member = int(sys.argv[1]), sys.argv[2]
z = zipfile.ZipFile(LIB + "/Sonniss.com-GDC2026-GameAudioBundle%dof5.zip" % bundle)
name = next(n for n in z.namelist() if member.lower() in n.lower() and n.lower().endswith(".wav"))
safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in os.path.basename(name))
dst = RAW + "/" + safe
if not os.path.exists(dst):
    with z.open(name) as s, open(dst, "wb") as o:
        o.write(s.read())
r = subprocess.run(["ffmpeg", "-v", "info", "-i", dst, "-af", "silencedetect=noise=-38dB:d=0.25", "-f", "null", "-"], capture_output=True, text=True)
print(dst)
print(re.findall(r"Duration: [\d:.]+", r.stderr)[:1])
for m in re.finditer(r"silence_(start|end): ([\d.]+)", r.stderr):
    print(m.group(1), m.group(2))
