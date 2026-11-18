"""Sounds taken from Cheyenne's own library (no paid generation): Sonniss GDC 2026 bundle, the Night Shift package and
re-processed versions of sounds we already have.  Files are copied out of the library zips, never moved or changed.

  python lib_sfx.py          extract + process everything that is missing
  python lib_sfx.py --force  redo all

Raw copies: SourceArt/Audio/raw_lib/   Final: SourceArt/Audio/<name>.wav (48 kHz 16-bit)
Sonniss GDC bundle licence: royalty-free, commercial use allowed, no attribution required (see licence in each zip).
"""
import glob, os, subprocess, sys, zipfile

ROOT = "C:/GameDev/Unreal/WellnessCheck"
OUT = ROOT + "/SourceArt/Audio"
RAW = OUT + "/raw_lib"
LIB = "C:/Users/cheye/OneDrive/Documents/ChatGPT/forklight-tts"
SON = LIB + "/Sonniss.com-GDC2026-GameAudioBundle%dof5.zip"
NS = LIB + "/Something Is Taking the Night Shift - Episode - 2026-10-13/Night_Shift_Audio_Package_v1.zip"
FADE = "afade=t=in:d=0.03,areverse,afade=t=in:d={f},areverse"
WALL = "lowpass=f=2600,highpass=f=120"          # heard through lath and plaster
FAR = "lowpass=f=900,aecho=0.8:0.7:55|97:0.35|0.22"

# name: (source, member substring or existing file, start, length, extra filter, LUFS, channels)
#   source: 1..5 = Sonniss bundle, "ns" = Night Shift package, "own" = a file already in SourceArt/Audio
ITEMS = {
    # ---- the drive
    "amb_car": (3, "VEHCar_TownDrivingAmbience06", 20, 40, "lowpass=f=5000", -25, 2),
    "car_stop": (5, "VEHSkid_Tire Skids on Gravel", 0, 2.6, "volume=0.6", -22, 1),
    "car_door": (5, "VEHDoor_Car Foley Car Door Open and Close Exterior 04", 0, 4.0, "", -18, 1),
    # ---- the house breathing
    "wind_gust_01": (3, "WINDInt_ChimneyWind05", 2, 7, "", -27, 1),
    "wind_gust_02": (3, "WINDInt_ChimneyWind05", 14, 8, "", -27, 1),
    "wind_gust_03": (3, "WINDInt_ChimneyWind05", 30, 6, "asetrate=48000*0.9,aresample=48000", -28, 1),
    "amb_wind": (3, "WINDInt_ChimneyWind05", 0, 45, "lowpass=f=1800", -36, 2),
    "scratch_wall_01": (3, "GOREMisc_Cladding_NailScratch19", 0, 3.0, WALL, -25, 1),
    "scratch_wall_02": (3, "GOREMisc_Cladding_Scratch06", 0, 3.0, WALL, -25, 1),
    "scratch_wall_03": (3, "GOREMisc_Cladding_NailScratch19", 0, 3.0, "asetrate=48000*0.78,aresample=48000," + WALL, -26, 1),
    "scratch_wall_04": (3, "OBJMisc_ScratchCard_CoinTapScratch_01", 0, 3.0, "asetrate=48000*0.6,aresample=48000," + WALL, -27, 1),
    "skitter_01": ("ns", "skitter__Spider Chattering", 0, 2.4, "highpass=f=700,lowpass=f=6000", -28, 1),
    "skitter_02": ("ns", "skitter__Spider Chattering", 1.5, 2.0, "asetrate=48000*1.25,aresample=48000,highpass=f=900,lowpass=f=6500", -29, 1),
    "skitter_03": (2, "WOODFric_Wood Shaker Microphone Head Roll", 0, 2.2, "asetrate=48000*1.5,aresample=48000,highpass=f=800,lowpass=f=5000", -29, 1),
    "skitter_04": (2, "ICEFric_Dry Ice Squeak Metal Animal Mouse Imitation", 0, 1.6, "lowpass=f=5000", -30, 1),
    "bang_far_01": (1, "METLImpt_Metal Bangs, Metal Hits, Banging On Doors", 0, 4.0, FAR, -24, 1),
    "wood_hit_far_01": (1, "WOODImpt_Wooden Hit, Dark, Heavy Hit", 0, 3.5, "lowpass=f=1400", -22, 1),
    "chair_creak_01": (1, "FOLYProp_Sitting Down, Creaky Seat, Squeaks 3", 0, 3.0, "", -24, 1),
    "switch_click": (3, "MECHClik_USALightSwitch_On05", 0, 0.6, "", -20, 1),
    "bulb_buzz": (3, "ELECBuzz_Buzz27", 0, 1.6, "lowpass=f=6000,volume=0.7", -27, 1),
    "bulb_pop": (3, "ELECArc_ArcDesign15", 0, 0.9, "highpass=f=300", -20, 1),
    "amb_fridge": (3, "MACHAppl_Deep Fridge Hum", 2, 20, "", -34, 1),
    "toilet_far": (3, "WATRPlmb_ToiletFlush01", 0, 9, FAR, -27, 1),
    "radio_tune": (4, "SBvr_AM EQ Sweeping 002", 0, 7, "lowpass=f=3400,highpass=f=300", -24, 1),
    # ---- her
    "breath_near_01": (5, "CREAHmn_Violent Humanoid Creature Exhale Short 4", 0, 2.0, "asetrate=48000*1.12,aresample=48000,lowpass=f=5000", -25, 1),
    "breath_near_02": ("own", "her_breath", 0.3, 3.0, "", -25, 1),
    "her_hurt_01": (2, "HMNBrth_Construction Kit Male Screeching Breath Inhale Weak Squeal 05", 0, 2.4, "asetrate=48000*1.3,aresample=48000", -14, 1),
    "her_hurt_02": ("own", "her_scream_short_02", 0, 2.0, "asetrate=48000*1.18,aresample=48000,tremolo=f=11:d=0.6", -13, 1),
    "her_flinch_01": ("own", "her_scream_short_01", 0, 0.7, "asetrate=48000*1.25,aresample=48000", -16, 1),
    "her_flinch_02": (5, "CREAHmn_Violent Humanoid Creature Exhale Short 4", 0, 0.9, "asetrate=48000*1.4,aresample=48000", -16, 1),
    # ---- music beds and stings (stereo)
    "music_low": (2, "DSGNSynth_Dark Loop Mystic Forest Tonal Steady Synth", 0, None, "lowpass=f=1500", -30, 2),
    "music_stalk": (3, "CREAEthr_Aztec Death Whistle Drone_05", 0, None, "lowpass=f=3000", -24, 2),
    "music_evil": (1, "AMBDsgn_Evil Spell Ambience", 0, 60, "lowpass=f=4000", -27, 2),
    "sting_braam": (2, "Transition Braam Slow Dark Creepy", 0, 8, "", -16, 2),
    "sting_whisper": (2, "DSGNEthr_Jumpscare Vocal Aggressive Whisper Harsh Distortion 02", 0, 4, "", -14, 2),
    "sting_swell": (2, "UIAlert_Alert Designed Transition Swell Creature Strange Alien Layered 01", 0, 6, "", -17, 2),
    "sting_noisebox": (3, "DSGNErie_NoiseBoxHit_10", 0, 6, "", -16, 2),
    # ---- re-processed: the same sounds from another floor / another room
    "door_far_01": ("own", "door_close_01", 0, None, FAR, -27, 1),
    "door_far_02": ("own", "door_creak_long", 0, 4.0, FAR, -28, 1),
    "door_far_03": ("own", "door_slam", 0, None, "lowpass=f=600,aecho=0.8:0.8:70|130:0.4|0.25", -24, 1),
}
# footsteps overhead: several of our own wood steps in a row, heard through the ceiling
STEPS_ABOVE = {"steps_above_01": ([1, 3, 2, 4, 1, 5], 0.62), "steps_above_02": ([2, 4, 1, 3], 0.9), "steps_above_03": ([5, 1, 4, 2, 3, 1, 4, 2], 0.42)}


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def raw_copy(source, member):
    """Copy the first matching member out of the library zip; returns the local path."""
    if source == "own":
        return f"{OUT}/{member}.wav"
    zpath = NS if source == "ns" else SON % source
    z = zipfile.ZipFile(zpath)
    name = next((n for n in z.namelist() if member.lower() in n.lower() and n.lower().endswith((".wav", ".mp3", ".flac", ".ogg"))), None)
    if not name:
        raise RuntimeError("not in library: " + member)
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in os.path.basename(name))
    dst = f"{RAW}/{safe}"
    if not os.path.exists(dst):
        with z.open(name) as src, open(dst, "wb") as out:
            out.write(src.read())
    return dst, name


def main():
    os.makedirs(RAW, exist_ok=True)
    force = "--force" in sys.argv
    credits = ["", "## From Cheyenne's Sonniss GDC 2026 Game Audio Bundle and Night Shift package (royalty-free, no attribution required)", ""]
    ok = 0
    for name, (source, member, start, length, filt, lufs, ch) in ITEMS.items():
        dst = f"{OUT}/{name}.wav"
        try:
            got = raw_copy(source, member)
            src, origin = (got, member + " (re-processed)") if isinstance(got, str) else got
            credits.append(f"- {name}: {origin}")
            if os.path.exists(dst) and not force:
                ok += 1
                continue
            pre = ["-ss", str(start)] if start else []
            if length:
                pre += ["-t", str(length)]
            loop = name.startswith(("amb_", "music_"))
            if loop:
                tmp = f"{RAW}/_loop_{name}.wav"
                ff(pre + ["-i", src, "-af", filt or "anull", "-ac", str(ch), "-ar", "48000", tmp])
                d = dur(tmp)
                x = min(2.5, d * 0.2)
                ff(["-i", tmp, "-filter_complex",
                    f"[0]atrim=0:{x},asetpts=PTS-STARTPTS[head];[0]atrim={x}:{d - x},asetpts=PTS-STARTPTS[body];[0]atrim={d - x}:{d},asetpts=PTS-STARTPTS[tail];"
                    f"[tail][head]acrossfade=d={x}:c1=qsin:c2=qsin[seam];[body][seam]concat=n=2:v=0:a=1,loudnorm=I={lufs}:TP=-2:LRA=20[o]",
                    "-map", "[o]", "-ac", str(ch), "-ar", "48000", "-c:a", "pcm_s16le", dst])
                os.remove(tmp)
            else:
                f = max(0.05, min(0.5, (length or dur(src)) * 0.2))
                chain = (filt + "," if filt else "") + FADE.format(f=f) + f",loudnorm=I={lufs}:TP=-1.5:LRA=15"
                ff(pre + ["-i", src, "-af", chain, "-ac", str(ch), "-ar", "48000", "-c:a", "pcm_s16le", dst])
            ok += 1
            print("  ", name, round(dur(dst), 1), "s")
        except Exception as exc:
            print("  FAILED", name, str(exc)[:200])
    for name, (order, gap) in STEPS_ABOVE.items():
        dst = f"{OUT}/{name}.wav"
        if os.path.exists(dst) and not force:
            continue
        ins, parts = [], []
        for i, k in enumerate(order):
            ins += ["-i", f"{OUT}/step_wood_0{k}.wav"]
            parts.append(f"[{i}]adelay={int(i * gap * 1000 + (37 * i) % 90)}:all=1[s{i}]")
        mix = "".join(f"[s{i}]" for i in range(len(order)))
        ff(ins + ["-filter_complex", ";".join(parts) + f";{mix}amix=inputs={len(order)}:normalize=0,lowpass=f=420,aecho=0.8:0.6:40|75:0.4|0.25,loudnorm=I=-26:TP=-2[o]",
                  "-map", "[o]", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", dst])
        print("  ", name, round(dur(dst), 1), "s")
        ok += 1
    cred = OUT + "/AUDIO_CREDITS.md"
    text = open(cred, encoding="utf-8").read() if os.path.exists(cred) else ""
    marker = "## From Cheyenne's Sonniss"
    if marker in text:
        text = text[:text.index(marker)].rstrip() + "\n"
    open(cred, "w", encoding="utf-8").write(text.rstrip() + "\n" + "\n".join(credits) + "\n")
    print("library sounds ready:", ok)


main()
