"""Audio pass 2: before / after comparison videos for Cheyenne to sign off (label on screen, live waveform).

  <numpy python> pass2_compare.py [stings] [wheel] [oneshots] [ambience]     -> Saved/AudioPass2/*.mp4

Each sound is played as the game plays it (same volume number the code uses), first the old file, then the new one.
The wheelchair video is the bath scene rebuilt from the timings in WCBathChair.cpp: roll, baseboard, fall, wheel squeaks.
"""
import os, subprocess, sys
import numpy as np
import pass2_lib as L
import pass2_sources as S

OLD = S.ROOT + "/SourceArt/Audio"
NEW = S.ROOT + "/SourceArt/AudioPass2/new"
OUT = S.ROOT + "/Saved/AudioPass2"
FONT = "C\\:/Windows/Fonts/arialbd.ttf"


BEFORE = S.ROOT + "/SourceArt/AudioPass2/before"


def path(folder, name):
    if folder == OLD and os.path.exists(f"{BEFORE}/{name}.wav"):      # after the pass is applied the old files live here
        return f"{BEFORE}/{name}.wav"
    return f"{folder}/{name}.wav"


def get(folder, name, gain=1.0, rate=1.0):
    x = L.load(path(folder, name))
    if rate != 1.0:
        x = L.pitch(x, rate)
    return x * gain


def render(tag, title, segs, norm=True):
    """segs: list of (label 'BEFORE'/'AFTER'/'' , caption, signal)"""
    os.makedirs(OUT, exist_ok=True)
    gap = np.zeros((L.secs(0.7), 2))
    parts = [np.zeros((L.secs(1.2), 2))]; marks = []; t = 1.2
    for lab, cap, x in segs:
        marks.append((t, t + len(x) / L.SR + 0.35, lab, cap))
        parts += [x, gap]; t += len(x) / L.SR + 0.7
    a = np.concatenate(parts)
    if norm:
        a *= L.lin(-1.0 - L.peak(a))
    wav = f"{OUT}/{tag}.wav"
    L.write(wav, a, 2)
    f = [f"color=c=0x0b0b0d:s=1280x720:r=30:d={t:.2f}[bg]",
         "[0:a]showwaves=s=1280x300:mode=cline:colors=0xd8d2c4:rate=30:scale=sqrt[wv]",
         "[bg][wv]overlay=0:400:shortest=1[v0]"]
    chain = f"[v0]drawtext=fontfile='{FONT}':text='{title}':x=40:y=28:fontsize=30:fontcolor=0x9a958a"
    for a0, b0, lab, cap in marks:
        en = f"enable='between(t,{a0:.2f},{b0:.2f})'"
        col = {"BEFORE": "0xd96a5a", "AFTER": "0x7fd08a"}.get(lab, "0xe8e2d0")
        if lab:
            chain += f",drawtext=fontfile='{FONT}':text='{lab}':x=(w-text_w)/2:y=130:fontsize=120:fontcolor={col}:{en}"
        chain += f",drawtext=fontfile='{FONT}':text='{cap}':x=(w-text_w)/2:y=290:fontsize=44:fontcolor=0xe8e2d0:{en}"
    f.append(chain + "[v]")
    script = f"{OUT}/{tag}.filter.txt"
    open(script, "w", encoding="utf-8").write(";\n".join(f))
    mp4 = f"{OUT}/{tag}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-nostdin", "-y", "-i", wav, "-/filter_complex", script,
                    "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4], check=True)
    os.remove(script)
    print(f"{mp4}  {t:.0f} s  {os.path.getsize(mp4) / 1048576:.1f} MB")


def pair(name, caption, gain=1.0, rate=1.0):
    return [("BEFORE", caption, get(OLD, name, gain, rate)), ("AFTER", caption, get(NEW, name, gain, rate))]


def seq(folder, items, length=None):
    """items: (name, time, gain, rate)"""
    return L.mix([(get(folder, n, g, r), t, 0) for n, t, g, r in items], length)


def stings():
    segs = []
    for nm, cap, g in (("sting_hit", "Jump scare hit", 1.0), ("sting_rise", "Rise into a scare", 0.9), ("sting_low", "Low dread", 0.8),
                       ("sting_soft", "First sight of her", 0.7), ("sting_braam", "Braam", 0.7), ("sting_swell", "Swell", 0.6)):
        segs += pair(nm, cap, g)
    # the hit as it lands in the game: under her scream
    for lab, folder in (("BEFORE", OLD), ("AFTER", NEW)):
        segs.append((lab, "Hit with her scream on top", L.mix([(get(folder, "sting_hit"), 0, 0), (get(OLD, "her_scream_01"), 0.0, 0)])))
    render("01_scare_stings", "Scare stings", segs)


def wheel():
    def scene(folder):
        roll = get(folder, "wheel_on_boards", 0.60, 1.18)
        roll = L.fade(roll[:L.secs(3.3)], 0.25, 0.16)
        items = [(roll, 0.0, 0), (get(folder, "wheel_baseboard", 1.35, 0.96), 3.3, 0), (get(folder, "wheel_sidefall", 1.38, 0.91), 4.24, 0)]
        for t, sp in ((5.11, 0.95), (5.7, 0.82), (6.35, 0.68), (7.15, 0.52), (8.2, 0.34)):
            items.append((get(folder, "wheel_axle_rub", 0.67 * sp, 0.72 + 0.31 * sp), t, 0))
        return L.mix(items, 9.2)
    segs = [("BEFORE", "Wheelchair rolls out, hits the wall, falls", scene(OLD)), ("AFTER", "Wheelchair rolls out, hits the wall, falls", scene(NEW))]
    segs += pair("wheel_sidefall", "The chair tipping over in the bathroom", 1.30)
    render("02_bathroom_wheelchair", "Bathroom wheelchair", segs)


def oneshots():
    segs = []
    segs += pair("gun_shot", "Pistol shot")
    for lab, folder in (("BEFORE", OLD), ("AFTER", NEW)):
        segs.append((lab, "Doors. locked, unlock, open, close, slam",
                     seq(folder, [("door_locked_01", 0, .9, 1), ("door_unlock", 1.6, .9, 1), ("door_open_01", 3.0, 1, 1), ("door_close_01", 4.6, 1, 1), ("door_slam", 6.2, 1, 1)])))
    segs += pair("door_creak_long", "Door creaking open by itself")
    for lab, folder in (("BEFORE", OLD), ("AFTER", NEW)):
        segs.append((lab, "Your footsteps on the boards, then the stairs",
                     seq(folder, [(f"step_wood_0{(i % 5) + 1}", i * 0.62, .9, 1) for i in range(6)] +
                         [(f"step_stairs_0{(i % 2) + 1}", 3.9 + i * 0.6, .9, 1) for i in range(4)])))
    for lab, folder in (("BEFORE", OLD), ("AFTER", NEW)):
        segs.append((lab, "Upstairs. steps above, a heavy thump, her steps",
                     seq(folder, [("steps_above_01", 0, .9, 1), ("thump_heavy", 3.6, 1, 1)] + [(f"her_step_0{(i % 4) + 1}", 6.0 + i * 0.42, .9, 1) for i in range(5)])))
    for lab, folder in (("BEFORE", OLD), ("AFTER", NEW)):
        segs.append((lab, "Lights. switch, bulb dying, bulb pop",
                     seq(folder, [("switch_click", 0, .9, 1), ("bulb_die", 0.8, .8, 1), ("bulb_pop", 3.0, .8, 1)])))
    segs += pair("phone_ring", "Her dead landline ringing", .87)
    for lab, folder in (("BEFORE", OLD), ("AFTER", NEW)):
        segs.append((lab, "Knock at the front door, body hits the floor, picture falls",
                     seq(folder, [("knock", 0, 1, 1), ("body_fall", 3.0, 1, 1), ("frame_fall", 5.6, 1, 1)])))
    render("03_one_shots", "One-shots", segs)


def ambience():
    a = L.load(path(OLD, "music_house"), 20, 50) * 0.55
    b = L.load(f"{NEW}/music_house.wav", 20, 50) * 0.55
    c = L.load(path(OLD, "music_stalk")) * 0.75
    d = L.load(f"{NEW}/music_stalk.wav") * 0.75
    segs = [("BEFORE", "Main house ambience", L.fade(a, 1.0, 2.0)), ("AFTER", "Main house ambience", L.fade(b, 1.0, 2.0)),
            ("BEFORE", "Hunt music (she is coming)", L.fade(c, 0.5, 1.0)), ("AFTER", "Hunt music (she is coming)", L.fade(d, 0.5, 1.0))]
    # ambience is quiet in the game; lift both by the same amount so it can be judged on small speakers
    g = L.lin(-16.0 - max(L.integrated(a), L.integrated(b)))
    render("04_house_ambience", "House ambience (both raised by the same amount)", [(l, c2, x * g) for l, c2, x in segs], norm=False)


def car():
    a = L.fade(L.load(path(OLD, "amb_car"), 0, 22), 0.5, 1.5)
    b = L.fade(L.load(f"{NEW}/amb_car.wav", 0, 22), 0.5, 1.5)
    render("05_cruiser_engine", "Cruiser engine on the drive in", [("BEFORE", "Engine (modern car hum)", a), ("AFTER", "Engine (recorded V8 over the cab)", b)], norm=False)


if __name__ == "__main__":
    todo = sys.argv[1:] or ["stings", "wheel", "oneshots", "ambience"]
    for t in todo:
        globals()[t]()
