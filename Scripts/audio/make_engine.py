"""The cruiser's engine (Cheyenne, 2026-11-19 21:24 UTC: "I need the engine in the car to be amplified, it's too low if
it's there at all; this is set around the 90s so engines were louder than they are now").

The old amb_car was a modern car's cabin hum at -25 LUFS.  This one is a real American V8 at low speed (SoundBits "Cars -
Mad Mustang Mercury", from her Sonniss GDC 2026 bundle 5: royalty-free, commercial use allowed, no attribution required),
heard from the driver's seat: bass lifted, top rolled off, the old cabin and road noise kept quietly underneath, looped
over one slow swell of the revs, at -15 LUFS.  ffmpeg only; nothing generated or paid for.
"""
import os, shutil, subprocess

A = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio"
U = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Audio_unused"
V8 = A + "/raw_lib/VEHCar_Various_Driving_at_Slow_Speed_15_06_SNDBTS_CRS-MMM.wav"
os.makedirs(U, exist_ok=True)


def ff(args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + args, check=True, stdin=subprocess.DEVNULL)


old = U + "/amb_car_old.wav"
if not os.path.exists(old):
    shutil.copyfile(A + "/amb_car.wav", old)

# 1. the engine: the 15 seconds where it is pulling (4 s to 19 s of the take), from inside the car
eng = A + "/raw_lib/_eng.wav"
ff(["-ss", "4", "-t", "15", "-i", V8, "-af",
    "aresample=48000,highpass=f=28,lowpass=f=3800,bass=g=5:f=85:w=0.9,equalizer=f=160:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=20:release=250:makeup=4",
    "-ac", "1", "-ar", "48000", eng])
# 2. looped across its own ends, so the swell of the revs comes round without a seam
loop = A + "/raw_lib/_eng_loop.wav"
d, x = 15.0, 2.5
ff(["-i", eng, "-filter_complex",
    f"[0]atrim=0:{x},asetpts=PTS-STARTPTS[head];[0]atrim={x}:{d - x},asetpts=PTS-STARTPTS[body];[0]atrim={d - x}:{d},asetpts=PTS-STARTPTS[tail];"
    f"[tail][head]acrossfade=d={x}:c1=qsin:c2=qsin[seam];[body][seam]concat=n=2:v=0:a=1[o]", "-map", "[o]", "-ar", "48000", loop])
# 3. eight times round (100 s: the engine comes round every 12.5 s, the cabin noise every 20, so both meet their own
#    ends exactly at 100), a little wider than mono, over the old cabin and road noise
ff(["-stream_loop", "7", "-i", loop, "-stream_loop", "4", "-i", old, "-filter_complex",
    "[0]aformat=channel_layouts=mono,asplit=2[l][r];[r]adelay=11:all=1,highpass=f=60[rd];[l][rd]join=inputs=2:channel_layout=stereo,volume=1.0[e];"
    "[1]aformat=channel_layouts=stereo,volume=0.5[c];[e][c]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-15:TP=-1.5:LRA=11[o]",
    "-map", "[o]", "-t", "100", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", A + "/amb_car.wav"])
for f in (eng, loop):
    os.remove(f)
r = subprocess.run(["ffmpeg", "-nostdin", "-i", A + "/amb_car.wav", "-af", "ebur128=framelog=quiet", "-f", "null", "-"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
print("amb_car:", [l.strip() for l in r.stderr.splitlines() if "I:" in l or "LRA:" in l][-2:])
