"""Sounds for the things that act by themselves (no paid generation):
  record_tune   Darren Curtis, "Sweet Little Lullaby" (free for commercial use WITH CREDIT; see his licence text beside the file
                in the Forklight library), played through a horn gramophone: narrow band, wow, hiss and crackle.
  record_stop   the needle dragged off the record.
  clock_tick    an antique clock (Sonniss GDC bundle 1), a loop.
  bell_toll     one stroke of a church bell, close (Sonniss GDC bundle 3).
  tv_static     television snow with mains hum (synthesised), a loop.
Files are copied out of the library, never changed there."""
import os, subprocess, zipfile

ROOT = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio"
RAW = ROOT + "/raw_lib"
LIB = "C:/Users/cheye/OneDrive/Documents/ChatGPT/forklight-tts"
os.makedirs(RAW, exist_ok=True)


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def from_zip(bundle, member):
    z = zipfile.ZipFile(f"{LIB}/Sonniss.com-GDC2026-GameAudioBundle{bundle}of5.zip")
    name = next(n for n in z.namelist() if member.lower() in n.lower() and n.lower().endswith(".wav"))
    dst = RAW + "/" + "".join(c if c.isalnum() or c in "._-" else "_" for c in os.path.basename(name))
    if not os.path.exists(dst):
        with z.open(name) as s, open(dst, "wb") as o:
            o.write(s.read())
    return dst, name


OUTFMT = ["-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le"]
credits = []

# ---- the record
song = f"{LIB}/Darren Curtis - Sweet Little Lullaby MP3.mp3"
ff(["-i", song, "-f", "lavfi", "-i", "anoisesrc=c=pink:r=48000:a=0.5", "-f", "lavfi", "-i", "anoisesrc=c=white:r=48000:a=1.0",
    "-filter_complex",
    # the tune: mono, narrow, wavering in pitch like a warped record
    "[0]aresample=48000,pan=mono|c0=0.5*c0+0.5*c1,atrim=0:98,highpass=f=320,lowpass=f=3300,vibrato=f=0.55:d=0.22,vibrato=f=5.3:d=0.04,"
    "acompressor=threshold=-24dB:ratio=4:attack=5:release=120,volume=1.6[t];"
    # surface hiss, and crackle: white noise cut to ticks by a fast irregular gate
    "[1]atrim=0:98,highpass=f=1200,lowpass=f=5200,volume=0.035[h];"
    "[2]atrim=0:98,highpass=f=2500,tremolo=f=11.3:d=1.0,tremolo=f=3.7:d=1.0,agate=threshold=0.55:ratio=20:attack=0.2:release=6,volume=0.5[c];"
    "[t][h][c]amix=inputs=3:normalize=0,afade=t=in:d=1.2,afade=t=out:st=95:d=3,loudnorm=I=-20:TP=-2:LRA=9[o]",
    "-map", "[o]"] + OUTFMT + [ROOT + "/record_tune.wav"])
credits.append("- record_tune: Darren Curtis, \"Sweet Little Lullaby\" (darrencurtismusic.com; free for commercial use with credit), processed to sound like a horn gramophone")

# ---- the needle coming off: half a second of the tune sliding down in pitch into a scrape
ff(["-i", ROOT + "/record_tune.wav", "-i", ROOT + "/shelf_scrape.wav", "-filter_complex",
    "[0]atrim=20:20.5,asetpts=PTS-STARTPTS,asetrate=48000*0.55,aresample=48000,afade=t=out:st=0.5:d=0.4[a];"
    "[1]atrim=0:0.45,asetpts=PTS-STARTPTS,asetrate=48000*1.7,aresample=48000,highpass=f=900,volume=0.8[b];"
    "[a][b]amix=inputs=2:normalize=0,loudnorm=I=-19:TP=-2[o]", "-map", "[o]"] + OUTFMT + [ROOT + "/record_stop.wav"])
credits.append("- record_stop: made from record_tune and our own shelf_scrape")

# ---- clock
src, name = from_zip(1, "CLOCKTick_Crooked Antique Clock")
ff(["-ss", "4", "-t", "12", "-i", src, "-af", "highpass=f=180,afade=t=in:d=0.05,loudnorm=I=-24:TP=-3:LRA=7"] + OUTFMT + [ROOT + "/clock_tick.wav"])
credits.append(f"- clock_tick: {name}")

# ---- bell
src, name = from_zip(3, "Church Bells, Near Distance, In Church Tower")
r = subprocess.run(["ffmpeg", "-v", "info", "-t", "40", "-i", src, "-af", "silencedetect=noise=-30dB:d=0.3", "-f", "null", "-"], capture_output=True, text=True)
import re
starts = [float(m.group(1)) for m in re.finditer(r"silence_end: ([\d.]+)", r.stderr)]
t0 = max(0.0, (starts[0] if starts else 0.0) - 0.05)
ff(["-ss", str(t0), "-t", "7", "-i", src, "-af", "aresample=48000,asetrate=48000*0.84,aresample=48000,afade=t=out:st=6.0:d=2.2,loudnorm=I=-14:TP=-1.5"] + OUTFMT + [ROOT + "/bell_toll.wav"])
credits.append(f"- bell_toll: {name} (first stroke, pitched down)")

# ---- television snow
ff(["-f", "lavfi", "-i", "anoisesrc=c=white:r=48000:a=0.6:d=8", "-f", "lavfi", "-i", "sine=f=60:r=48000:d=8", "-f", "lavfi", "-i", "sine=f=15734:r=48000:d=8",
    "-filter_complex", "[0]highpass=f=500,lowpass=f=7500,tremolo=f=0.7:d=0.25,volume=0.5[n];[1]volume=0.18[h];[2]volume=0.02[w];[n][h][w]amix=inputs=3:normalize=0,loudnorm=I=-25:TP=-3[o]",
    "-map", "[o]"] + OUTFMT + [ROOT + "/tv_static.wav"])
credits.append("- tv_static: synthesised (noise, 60 Hz hum, line whine)")

cred = ROOT + "/AUDIO_CREDITS.md"
text = open(cred, encoding="utf-8").read() if os.path.exists(cred) else ""
marker = "## Things that act by themselves"
if marker in text:
    text = text[:text.index(marker)].rstrip() + "\n"
open(cred, "w", encoding="utf-8").write(text.rstrip() + "\n\n" + marker + "\n\n" + "\n".join(credits) + "\n")
for n in ("record_tune", "record_stop", "clock_tick", "bell_toll", "tv_static"):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{ROOT}/{n}.wav"], capture_output=True, text=True)
    print(n, r.stdout.strip(), "s")
