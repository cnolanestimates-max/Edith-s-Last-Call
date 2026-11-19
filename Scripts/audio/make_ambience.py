"""The two background beds, rebuilt clean (Cheyenne 2026-11-19: "it's on a looping track, door shutting, literally every 5
seconds ... every 2 seconds you hear light switches"; "a tweeting bird ... while he's still driving").
The generated beds had things happening IN them (a thump, a ticking), so on a loop they came round like a track.
These have nothing happening in them at all: every event the player hears is now placed by the game.

  amb_house   40 s  a near-silent room: air, a very faint low hum.  No ticks, no knocks.
  amb_night   48 s  crickets in two voices and a little wind.  No birds.
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

keep("amb_night")
# a cricket: a steady high tone chopped at about 30 a second, in bursts; two of them at different pitches and rhythms, far off
cr1 = "sine=frequency=4350:duration=48:sample_rate=48000,tremolo=f=31:d=1,volume='if(lt(mod(t,1.9),1.15),1,0)':eval=frame,lowpass=f=6000"
cr2 = "sine=frequency=3720:duration=48:sample_rate=48000,tremolo=f=24:d=1,volume='if(lt(mod(t+0.7,2.7),1.5),1,0)':eval=frame,lowpass=f=5000"
cr3 = "sine=frequency=5100:duration=48:sample_rate=48000,tremolo=f=38:d=0.9,volume='if(lt(mod(t+1.3,4.1),0.8),1,0)':eval=frame"
ff(["-f", "lavfi", "-i", cr1, "-f", "lavfi", "-i", cr2, "-f", "lavfi", "-i", cr3,
    "-f", "lavfi", "-i", "anoisesrc=color=brown:duration=48:sample_rate=48000:seed=23",
    "-filter_complex",
    "[0:a]volume=0.020,aecho=0.8:0.5:60|130:0.3|0.2[a];[1:a]volume=0.014,aecho=0.8:0.5:90|170:0.3|0.2[b];[2:a]volume=0.006,aecho=0.8:0.6:140:0.3[c];"
    "[3:a]highpass=f=60,lowpass=f=420,tremolo=f=0.11:d=0.5,volume=1.1[wind];"
    "[a][b][c][wind]amix=inputs=4:normalize=0,afade=t=in:d=0.6,afade=t=out:st=47.4:d=0.6,loudnorm=I=-34:TP=-9:LRA=5,pan=stereo|c0=c0|c1=c0",
    "-ar", "48000", "-c:a", "pcm_s16le", f"{A}/amb_night.wav"])
for n in ("amb_house", "amb_night"):
    print(n, os.path.getsize(f"{A}/{n}.wav") // 1000, "KB")

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
