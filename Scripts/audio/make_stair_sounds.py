"""The stairwell scene's own sounds (2026-11-24): five bone cracks, synthesized, and the long high moan she makes on the
stairs, made from Edith's m_moan2 voice line (raised, slowed, wavering, with a stairwell echo).  Needs ffmpeg."""
import os, subprocess

AUDIO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "SourceArt", "Audio")


def ff(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args, check=True, cwd=AUDIO)


for i in range(1, 6):
    f1 = 120 + i * 23                       # the low knock of each crack
    d2 = round(0.012 + 0.009 * i, 3)        # the second snap, a little later each time
    src = (f"aevalsrc='(random(0)*2-1)*exp(-t*420)*0.9+(random(1)*2-1)*exp(-(t-{d2})*520)*gt(t\\,{d2})*0.7"
           f"+(random(2)*2-1)*exp(-(t-0.05)*60)*gt(t\\,0.05)*0.18+sin(2*PI*{f1}*t)*exp(-t*38)*0.55':s=48000:d=0.45")
    ff(["-f", "lavfi", "-i", src, "-af", "highpass=f=90,equalizer=f=2500:t=q:w=1.2:g=6,lowpass=f=9000,alimiter=limit=0.9,"
        "afade=t=out:st=0.3:d=0.15", "-ac", "1", f"bone_crack_0{i}.wav"])

ff(["-i", "VO/m_moan2.wav", "-af", "asetrate=48000*1.36,aresample=48000,atempo=0.62,vibrato=f=4.2:d=0.18,highpass=f=280,"
    "aecho=0.8:0.6:90|170:0.35|0.22,afade=t=in:d=0.6,afade=t=out:st=8.2:d=1.4,volume=1.6,alimiter=limit=0.95", "-ac", "1", "stair_moan.wav"])
print("stair sounds written to", os.path.abspath(AUDIO))
