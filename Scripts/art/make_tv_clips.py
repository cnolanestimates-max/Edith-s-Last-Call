"""Cuts the raw Higgsfield shots (SourceArt/TV/raw) into the 20-second tapes the living-room television plays:
title card, the shot, a slow push in on its last frame, an end card; then the whole thing is run down like an old VHS
(washed colour, colour bleed, noise, a tracking bar, soft focus) with hum, snow and a warped tune underneath.

  python make_tv_clips.py bedtime        one tape
  python make_tv_clips.py                all four
Writes SourceArt/TV/tape_<name>.mp4 (640x480, 30 fps, with sound).  ffmpeg only: no paid generation here."""
import os, subprocess, sys

ROOT = "C:/GameDev/Unreal/WellnessCheck/SourceArt"
RAW, OUT, AUD = ROOT + "/TV/raw", ROOT + "/TV", ROOT + "/Audio"
FONT = "C\\:/Windows/Fonts/lucon.ttf"
# name: (title lines, caption over the push-in, end-card lines, where the push-in heads (0..1 across, 0..1 down))
TAPES = {
    "bedtime": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 9"], "HE TUCKS HER IN NOW", ["NOBODY IN THIS HOUSE", "SLEEPS ALONE"], (0.55, 0.42)),
    "bedtime2": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 9"], "HE TUCKS HER IN NOW", ["NOBODY IN THIS HOUSE", "SLEEPS ALONE"], (0.50, 0.35)),
    "bedtime3": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 9"], "HE TUCKS HER IN NOW", ["NOBODY IN THIS HOUSE", "SLEEPS ALONE"], (0.50, 0.30)),
    "bedtime4": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 9"], "HE TUCKS HER IN NOW", ["NOBODY IN THIS HOUSE", "SLEEPS ALONE"], (0.50, 0.45)),
    "bedtime7": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 9"], "HE TUCKS HER IN NOW", ["NOBODY IN THIS HOUSE", "SLEEPS ALONE"], (0.44, 0.52)),
    "t_living": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 4"], "HE LIKES TO WATCH US", ["THERE IS ALWAYS", "ROOM FOR ONE MORE"], (0.66, 0.36)),
    "t_yard": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 6"], "HE NEVER MISSES A SUMMER", ["HE CAME TO STAY", "", "HE NEVER LEAVES"], (0.45, 0.5)),
    "t_rocker": (["A WORD FROM", "MRS. EDITH HARROW", "", "REEL 31"], "EVERYBODY LEFT. HE STAYED.", ["ASK AND YOU WILL", "HAVE COMPANY"], (0.62, 0.5)),
    "hall8": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 11"], "", ["NOBODY IN THIS HOUSE", "SLEEPS ALONE"], (0.5, 0.5)),
    "porch8": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 17"], "", ["HE CAME TO STAY", "", "HE NEVER LEAVES"], (0.5, 0.5)),
    "living8": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 4"], "HE LIKES TO WATCH US", ["HE LIKES TO WATCH US", "", "THERE IS ALWAYS ROOM"], (0.5, 0.5)),
    "bedtime8": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 9"], "HE TUCKS HER IN NOW", ["SAY GOODNIGHT", "TO OUR FRIEND"], (0.5, 0.5)),
    "supper": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 4"], "WE SET HIM A PLACE", ["THERE IS ALWAYS", "ROOM AT THE TABLE"], (0.50, 0.30)),
    "porch": (["HARROW FAMILY", "HOME MOVIES", "", "REEL 1"], "SAY HELLO TO OUR FRIEND", ["HE CAME TO STAY", "", "HE NEVER LEAVES"], (0.50, 0.25)),
    "rocker": (["A WORD FROM", "MRS. EDITH HARROW", "", "COUNTY ROAD 9"], "SHE ASKED. HE ANSWERED.", ["ASK AND YOU WILL", "HAVE COMPANY"], (0.50, 0.30)),
}


# the generator cannot hold the numbers of a date stamp still from frame to frame: rub its stamp out and burn in our own
DATEFIX = {"bedtime7": "OCT 31 1991", "t_living": "NOV 24 1991", "t_yard": "JUL 04 1991", "t_rocker": "NOV 26 1998"}


# shots that move for their whole length (Cheyenne: "they're like moving stills"): no frozen push-in; a caption card instead
DYNAMIC = {"bedtime8": 10, "living8": 15, "hall8": 15, "porch8": 15}      # seconds of real video in the shot


def ff(args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + args, check=True, stdin=subprocess.DEVNULL)


def text(lines, size, y0, color="white", alpha=0.92, box=False):
    out = []
    for i, ln in enumerate(lines):
        if not ln:
            continue
        ln = ln.replace(":", "\\:").replace("'", "")
        out.append(f"drawtext=fontfile='{FONT}':text='{ln}':fontsize={size}:fontcolor={color}@{alpha}:x=(w-text_w)/2:y={y0}+{i}*{int(size * 1.5)}"
                   + (":box=1:boxcolor=black@0.55:boxborderw=8" if box else ""))
    return ",".join(out) if out else "null"


def tape(name):
    title, caption, end, (px, py) = TAPES[name]
    src = f"{RAW}/{name}.mp4"
    last = f"{RAW}/_{name}_last.png"
    ff(["-sseof", "-0.2", "-i", src, "-frames:v", "1", "-update", "1", last])
    tmp = f"{OUT}/_{name}_cut.mp4"
    stamp = stamp2 = ""
    if name in DATEFIX:
        d = DATEFIX[name]
        stamp = f"delogo=x=392:y=414:w=222:h=54,drawtext=fontfile='{FONT}':text='{d}':fontsize=27:fontcolor=white@0.93:x=404:y=428,"
        stamp2 = f"delogo=x=784:y=828:w=444:h=108,drawtext=fontfile='{FONT}':text='{d}':fontsize=54:fontcolor=white@0.93:x=808:y=856,"
    fc = (
        # 1. title card: station blue, blocky white letters
        f"color=c=0x101a4a:s=640x480:r=30:d=2.6,{text(title, 34, 150)}[a];"
        # 2. the shot
        f"[0:v]fps=30,scale=640:480,setsar=1,{stamp}trim=0:9.9,setpts=PTS-STARTPTS[b];"
        # 3. the last frame, pushing slowly in toward the tall one, with a line of type under it
        f"[1:v]scale=1280:960,{stamp2}zoompan=z='1+0.22*on/126':x='(iw-iw/zoom)*{px}':y='(ih-ih/zoom)*{py}':d=1:s=640x480:fps=30,"
        f"eq=contrast=1.15:brightness=-0.05:saturation=0.5,{text([caption], 26, 400, box=True)}[c];"
        # 4. end card on black
        f"color=c=black:s=640x480:r=30:d=3.3,{text(end, 30, 180, color='0xe8e0c0')}[d];"
    )
    lead, cap_d, parts = 2.6, 4.2, "[a][b][c][d]concat=n=4"
    if name in DYNAMIC:
        shot = DYNAMIC[name]
        lead, end_d = (2.6, 3.6) if shot <= 10 else (2.2, 2.8)
        cap_d = round(20 - lead - shot - end_d, 2)                 # a caption card only if there is room for one
        fc = (f"color=c=0x101a4a:s=640x480:r=30:d={lead},{text(title, 34, 150)}[a];"
              f"[0:v]fps=30,scale=640:480,setsar=1,{stamp}trim=0:{shot},setpts=PTS-STARTPTS[b];"
              + (f"[1:v]scale=640:480,setsar=1,fps=30,eq=brightness=-1,{text([caption], 28, 220, color='0xe8e0c0')}[c];" if cap_d > 0.1 else "")
              + f"color=c=black:s=640x480:r=30:d={end_d},{text(end, 30, 180, color='0xe8e0c0')}[d];")
        if cap_d <= 0.1:
            parts, cap_d = "[a][b][d]concat=n=3", 1.0
    fc += (
        parts + ":v=1:a=0,"
        # the tape itself: soft, washed, colours slipping sideways, noise, a tracking bar crawling up, dark corners
        "gblur=sigma=1.0,eq=saturation=0.55:contrast=0.92:brightness=-0.03:gamma=0.93,chromashift=cbh=7:crh=-6,"
        # grain, and plenty of it (Cheyenne: "the grainy of the video needs amped up"): heavy in the light, coloured in the darks, never the same twice
        "noise=c0s=46:c0f=t+u:c1s=26:c1f=t+u:c2s=26:c2f=t+u,gblur=sigma=0.45,noise=alls=14:allf=t,"
        "drawbox=x=0:y='ih-mod(t*70\\,ih+60)':w=iw:h=16:color=white@0.10:t=fill,"
        "drawbox=x=0:y='ih-mod(t*70\\,ih+60)+16':w=iw:h=5:color=black@0.25:t=fill,"
        "drawbox=x=0:y=ih-22:w=iw:h=22:color=black@0.35:t=fill,"
        "vignette=PI/4.5,format=yuv420p[v]"
    )
    ff(["-i", src, "-loop", "1", "-framerate", "30", "-t", str(cap_d), "-i", last, "-filter_complex", fc, "-map", "[v]", "-t", "20", "-r", "30",
        "-c:v", "libx264", "-preset", "medium", "-crf", "29", tmp])
    # sound: mains hum and snow all the way through, the shot's own sound thin and far away, the lullaby running slow underneath
    ff(["-i", tmp, "-i", src, "-stream_loop", "3", "-i", AUD + "/tv_static.wav", "-i", AUD + "/record_tune.wav", "-filter_complex",
        # the voices on the tape stay clear enough to follow: thin, like a camcorder microphone, but in front of the hum and the tune
        f"[1:a]aresample=48000,adelay={int(lead * 1000)}:all=1,"
        "highpass=f=220,lowpass=f=3600,acompressor=threshold=-26dB:ratio=3,volume=1.5[shot];"
        "[2:a]atrim=0:20,volume=0.32[snow];"
        "[3:a]atrim=6:30,asetpts=PTS-STARTPTS,asetrate=48000*0.74,aresample=48000,vibrato=f=0.8:d=0.5,lowpass=f=2200,volume=0.3[tune];"
        "[shot][snow][tune]amix=inputs=3:normalize=0:duration=longest,atrim=0:20,afade=t=in:d=0.3,afade=t=out:st=19.4:d=0.6,loudnorm=I=-21:TP=-2[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-t", "20", "-movflags", "+faststart", f"{OUT}/tape_{name}.mp4"])
    os.remove(tmp)
    print("tape", name, os.path.getsize(f"{OUT}/tape_{name}.mp4") // 1000, "KB")


for n in (sys.argv[1:] or list(TAPES)):
    if os.path.exists(f"{RAW}/{n}.mp4"):
        tape(n)
    else:
        print("no raw shot for", n)
