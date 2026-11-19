"""The two background beds, rebuilt clean (Cheyenne 2026-11-19: "it's on a looping track, door shutting, literally every 5
seconds ... every 2 seconds you hear light switches"; "a tweeting bird ... while he's still driving").
The generated beds had things happening IN them (a thump, a ticking), so on a loop they came round like a track.
These have nothing happening in them at all: every event the player hears is now placed by the game.

  amb_house   40 s  a near-silent room: air, a very faint low hum.  No ticks, no knocks.
  amb_yard and amb_dawn use the dedicated ground-level exterior mastering script.
ffmpeg only; the old files are kept beside them as *_old.wav."""
import os, shutil, subprocess

A = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio"


def ff(args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + args, check=True, stdin=subprocess.DEVNULL)


def keep(name):
    if os.path.exists(f"{A}/{name}.wav") and not os.path.exists(f"{A}/{name}_old.wav"):
        shutil.copy2(f"{A}/{name}.wav", f"{A}/{name}_old.wav")


keep("amb_house")
ff(["-f", "lavfi", "-i", "anoisesrc=color=brown:duration=40:sample_rate=48000:seed=11",
    "-f", "lavfi", "-i", "anoisesrc=color=pink:duration=40:sample_rate=48000:seed=5",
    "-f", "lavfi", "-i", "sine=frequency=58:duration=40:sample_rate=48000",
    "-filter_complex",
    "[0:a]highpass=f=35,lowpass=f=210,volume=1.6[air];"
    "[1:a]highpass=f=300,lowpass=f=1400,volume=0.05[hiss];"
    "[2:a]volume=0.012[hum];"
    "[air][hiss][hum]amix=inputs=3:normalize=0,afade=t=in:d=0.5,afade=t=out:st=39.5:d=0.5,loudnorm=I=-40:TP=-9:LRA=3,pan=stereo|c0=c0|c1=c0",
    "-ar", "48000", "-c:a", "pcm_s16le", f"{A}/amb_house.wav"])

from make_exterior_beds import build as build_exterior_beds
build_exterior_beds()

# the cellar: the generated bed had a loud drip coming round every 18 seconds.  A low stone-room rumble with nothing in it.
keep("amb_cellar")
ff(["-f", "lavfi", "-i", "anoisesrc=color=brown:duration=44:sample_rate=48000:seed=31",
    "-f", "lavfi", "-i", "anoisesrc=color=pink:duration=44:sample_rate=48000:seed=9",
    "-f", "lavfi", "-i", "sine=frequency=41:duration=44:sample_rate=48000",
    "-filter_complex",
    "[0:a]highpass=f=25,lowpass=f=140,tremolo=f=0.1:d=0.35,volume=2.0[rumble];"
    "[1:a]highpass=f=500,lowpass=f=2200,volume=0.035[air];"
    "[2:a]volume=0.02[hum];"
    "[rumble][air][hum]amix=inputs=3:normalize=0,aecho=0.8:0.6:180|310:0.25|0.15,afade=t=in:d=0.6,afade=t=out:st=43.4:d=0.6,loudnorm=I=-36:TP=-9:LRA=3,pan=stereo|c0=c0|c1=c0",
    "-ar", "48000", "-c:a", "pcm_s16le", f"{A}/amb_cellar.wav"])
print("amb_cellar", os.path.getsize(f"{A}/amb_cellar.wav") // 1000, "KB")
