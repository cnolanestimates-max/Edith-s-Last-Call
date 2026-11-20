"""Generate the sound effects with Higgsfield's text-to-audio model (0.25 credits per second), then prepare everything
for Unreal.

  python gen_sfx.py --list       what is missing and what it will cost
  python gen_sfx.py              generate missing raw sounds (no automatic retries), then process all
  python gen_sfx.py --process    only (re)process raw + library sounds into SourceArt/Audio

Raw generations: SourceArt/Audio/raw/<name>.wav   Final: SourceArt/Audio/<name>.wav (48 kHz, 16-bit)
Library sources (copied, never moved): Kenney CC0 packs and Kevin MacLeod / Scott Buckley music from the Forklight
library; see AUDIO_CREDITS.md written next to the output.
"""
import json, os, subprocess, sys, urllib.request

ROOT = "C:/GameDev/Unreal/WellnessCheck"
RAW = ROOT + "/SourceArt/Audio/raw"
OUT = ROOT + "/SourceArt/Audio"
HF = "C:/Users/cheye/.local/share/unreal-agent-tools/node-v26.13.1-win-x64/higgsfield.cmd"
LIB = "C:/Users/cheye/OneDrive/Documents/ChatGPT/forklight-tts"
KEN = LIB + "/Open Game SFX - WAV Library/WAV Files"
DRY = "dry close recording, no music, no voices"

# name: (seconds, prompt)
GEN = {
    "her_scream_01": (4, "A terrifying blood-curdling scream of a very old woman, shrill, raw and furious, very close, no music"),
    "her_scream_02": (4, "An elderly woman shrieking in rage at the top of her lungs, long ragged horrible scream, close, no music"),
    "her_scream_03": (5, "A long inhuman wailing scream of an old woman rushing toward the listener, getting louder, horror film, no music"),
    "her_scream_short_01": (2, "A sudden short harsh shriek of an old woman, very close, startling, no music"),
    "her_scream_short_02": (2, "A sudden hoarse hissing screech of an old woman, right in your face, no music"),
    "her_breath": (6, "Slow rattling wheezing breathing of a very old woman, extremely close to the microphone, wet rasp in the throat, silence around, no music"),
    "whisper_far_01": (4, "An old woman whispering unintelligibly from another room in an empty house, faint, eerie, no music"),
    "whisper_far_02": (4, "Faint unintelligible muttering of an old woman behind a wall, distant, lonely, no music"),
    "crawl_knocks": (4, "Something scrabbling very fast on hands and knees across hollow wooden attic floorboards toward the listener, frantic rapid thumping, no music"),
    "creak_01": (2, "A single slow creak of an old wooden floorboard under a footstep, " + DRY),
    "creak_02": (2, "A short dry creak of an old wooden stair tread, " + DRY),
    "creak_03": (3, "A long groaning creak of old floorboards as weight shifts, " + DRY),
    "creak_04": (2, "A small sharp creak and tick of old dry wood, " + DRY),
    "house_groan_01": (5, "An old wooden house settling at night, a long low groan of timber, distant, quiet, no music"),
    "house_groan_02": (5, "Wind pressing on an old wooden house, beams creaking slowly, quiet interior, no music"),
    "knock_far_01": (3, "Three slow knocks on a wooden wall from a distant room in a silent old house, no music"),
    "knock_far_02": (3, "Two soft knocks from inside a wall, muffled, in a silent old house, no music"),
    "thump_far_01": (3, "A heavy muffled thump on the floor of the room above, old house, distant, no music"),
    "thump_far_02": (3, "Something heavy bumping against furniture in a far room, muffled, quiet house, no music"),
    "thump_heavy": (3, "A very heavy body dropping onto a wooden floor upstairs, a loud thud that rattles the ceiling, no music"),
    "drag_floor": (5, "Something heavy being slowly dragged across a wooden floor in the room above, heard through the ceiling, muffled, no music"),
    "door_open_01": (2, "An old interior wooden door opening, latch click and a short hinge creak, " + DRY),
    "door_close_01": (2, "An old interior wooden door closing with a latch click, " + DRY),
    "door_slam": (2, "A heavy wooden front door slamming shut violently, big boom with rattling frame, no music"),
    "door_locked_01": (2, "Rattling the handle of a locked old wooden door, it will not open, " + DRY),
    "door_unlock": (2, "An old key turning in a stiff door lock, heavy clunk, " + DRY),
    "door_creak_long": (5, "An old heavy wooden door slowly creaking open by itself, long eerie hinge creak, silence around, no music"),
    "knock": (3, "A firm police knock on a wooden front door, three hard knocks, outdoors at night, no music"),
    "phone_ring": (4, "An old rotary telephone ringing with a mechanical bell, two full rings, in a quiet room, no music"),
    "phone_pickup": (2, "Picking up an old telephone handset, plastic rattle and click, then a faint line hiss, no music"),
    "chair_scrape": (2, "A wooden chair scraping back across a wooden floor, " + DRY),
    "musicbox": (16, "A slow antique music box lullaby, slightly out of tune and winding down, lonely tinkling notes in a quiet room"),
    "shelf_scrape": (4, "A heavy wooden shelf full of glass jars being dragged across a stone floor, grinding with jars rattling, no music"),
    "trunk_open": (2, "The creaking metal lid of an old army footlocker being opened, latches snapping, " + DRY),
    "cut_rope": (3, "A pocket knife sawing through a thick dry cord, fibres tearing, then it snaps, " + DRY),
    "body_fall": (3, "A man falling down wooden cellar stairs, heavy tumbling thuds, no music"),
    "bulb_die": (2, "A flashlight bulb buzzing, flickering and dying with a small electrical fizz, " + DRY),
    "gun_shot": (2, "A single 9mm pistol gunshot inside a house, very loud sharp crack with a short room echo, no music"),
    "gun_empty": (1, "The dry click of a pistol trigger on an empty chamber, " + DRY),
    "gun_reload": (3, "A pistol magazine being ejected, a new magazine slapped in and the slide racked, " + DRY),
    "bullet_impact_01": (1, "A bullet smacking into a plaster and wood wall, debris falling, " + DRY),
    "car_door": (2, "A car door shutting outdoors at night on a quiet country road, no music"),
    "pickup": (1, "Picking up a small metal object from a wooden table, soft clink, " + DRY),
    "paper": (1, "Unfolding an old brittle sheet of paper, " + DRY),
    "flies_buzz": (6, "A swarm of houseflies buzzing around rotting food, close, constant, no music, no voices"),
    "radio_click": (1, "A police radio squelch click and short burst of static, dry"),
    "radio_static": (4, "Police radio static hiss with crackles and faint warbling interference, no voices, no music"),
    "sting_hit": (4, "A sudden violent horror movie jump scare sting, shrieking violins and a deep booming impact"),
    "sting_low": (5, "A slow ominous horror drone swell, deep sub bass and dissonant low strings rising, unsettling"),
    "sting_rise": (4, "A fast rising horror riser, dissonant strings sliding upward to a sharp peak"),
    "sting_soft": (4, "A quiet eerie horror stinger, a single cold high violin harmonic with a soft low thud"),
}
# straight copies from the CC0 library: name -> relative path under KEN (first that exists is used)
COPY = {
    "step_wood_01": "Impacts and Footsteps/footstep wood 000.wav", "step_wood_02": "Impacts and Footsteps/footstep wood 001.wav",
    "step_wood_03": "Impacts and Footsteps/footstep wood 002.wav", "step_wood_04": "Impacts and Footsteps/footstep wood 003.wav",
    "step_wood_05": "Impacts and Footsteps/footstep wood 004.wav",
    "step_gravel_01": "Impacts and Footsteps/footstep grass 000.wav", "step_gravel_02": "Impacts and Footsteps/footstep grass 001.wav",
    "step_gravel_03": "Impacts and Footsteps/footstep grass 002.wav", "step_gravel_04": "Impacts and Footsteps/footstep grass 003.wav",
    "step_stone_01": "Impacts and Footsteps/footstep concrete 000.wav", "step_stone_02": "Impacts and Footsteps/footstep concrete 001.wav",
    "step_stone_03": "Impacts and Footsteps/footstep concrete 002.wav", "step_stone_04": "Impacts and Footsteps/footstep concrete 003.wav",
    "step_stairs_01": "Impacts and Footsteps/footstep wood 001.wav", "step_stairs_02": "Impacts and Footsteps/footstep wood 003.wav",
    "ui_tick": "Interface/click 002.wav", "flashlight_click": "Interface/switch 002.wav",
}
MUSIC = {
    # name: (file in the Forklight library, start seconds, length seconds or None, credit)
    "music_drone": ("Long Note Four - Kevin MacLeod.mp3", 8, 150, "\"Long Note Four\" Kevin MacLeod (incompetech.com), CC BY 4.0"),
    "music_menu": ("Ossuary 6 - Air - Kevin MacLeod.mp3", 0, None, "\"Ossuary 6 - Air\" Kevin MacLeod (incompetech.com), CC BY 4.0"),
    "music_finale": ("Gathering Darkness - Kevin MacLeod.mp3", 0, None, "\"Gathering Darkness\" Kevin MacLeod (incompetech.com), CC BY 4.0"),
    "music_dawn": ("Sanctuary - Scott Buckley.mp3", 0, None, "\"Sanctuary\" Scott Buckley (scottbuckley.com.au), CC BY 4.0"),
}
STEREO = {"amb_night", "amb_house", "amb_cellar", "amb_dawn", "sting_hit", "sting_low", "sting_rise", "sting_soft"} | set(MUSIC)
LEVEL = {"amb_night": -30, "amb_house": -34, "amb_cellar": -30, "amb_dawn": -28, "musicbox": -24, "her_breath": -22, "whisper_far_01": -26,
         "whisper_far_02": -26, "music_drone": -27, "music_menu": -22, "music_finale": -20, "music_dawn": -21, "paper": -24, "pickup": -24,
         "ui_tick": -26, "flashlight_click": -22, "gun_shot": -11, "her_scream_01": -12, "her_scream_02": -12, "her_scream_03": -12,
         "her_scream_short_01": -13, "her_scream_short_02": -13, "sting_hit": -12, "door_slam": -13}


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def generate(name, secs, prompt):
    r = subprocess.run(["cmd", "/c", HF, "generate", "create", "mirelo_text_to_audio", "--prompt", prompt, "--duration", str(secs), "--wait", "--json"],
                       capture_output=True, text=True, timeout=600)
    out = r.stdout.strip()
    try:
        j = json.loads(out)
        url = j[0]["result_url"]
        job = j[0]["id"]
    except Exception:
        raise RuntimeError((out or r.stderr)[:200])
    ext = os.path.splitext(url.split("?")[0])[1] or ".wav"
    tmp = f"{RAW}/{name}{ext}"
    urllib.request.urlretrieve(url, tmp)
    if ext.lower() != ".wav":
        ff(["-i", tmp, f"{RAW}/{name}.wav"])
        os.remove(tmp)
    return job


def process(name, src, start=0.0, length=None):
    dst = f"{OUT}/{name}.wav"
    ch = "2" if name in STEREO else "1"
    lvl = LEVEL.get(name, -18)
    pre = ["-ss", str(start)] if start else []
    if length:
        pre += ["-t", str(length)]
    if name.startswith(("amb_", "music_")):
        # loops: equal-power crossfade of the tail into the head so the seam is silent
        tmp = f"{RAW}/_loop_{name}.wav"
        ff(pre + ["-i", src, "-ac", ch, "-ar", "48000", tmp])
        d = dur(tmp)
        x = min(2.0, d * 0.2)
        ff(["-i", tmp, "-filter_complex",
            f"[0]atrim=0:{x},asetpts=PTS-STARTPTS[head];[0]atrim={x}:{d - x},asetpts=PTS-STARTPTS[body];[0]atrim={d - x}:{d},asetpts=PTS-STARTPTS[tail];"
            f"[tail][head]acrossfade=d={x}:c1=qsin:c2=qsin[seam];[body][seam]concat=n=2:v=0:a=1,loudnorm=I={lvl}:TP=-2:LRA=20[o]",
            "-map", "[o]", "-ac", ch, "-ar", "48000", "-c:a", "pcm_s16le", dst])
        os.remove(tmp)
    else:
        trim = "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02," if not name.startswith(("sting_", "door_creak", "house_", "drag")) else ""
        fade = max(0.05, min(0.4, dur(src) * 0.15))
        ff(pre + ["-i", src, "-af", f"{trim}areverse,afade=t=in:d={fade},areverse,loudnorm=I={lvl}:TP=-1.5:LRA=15", "-ac", ch, "-ar", "48000", "-c:a", "pcm_s16le", dst])


def main():
    os.makedirs(RAW, exist_ok=True)
    todo = [n for n in GEN if not os.path.exists(f"{RAW}/{n}.wav")]
    secs = sum(GEN[n][0] for n in todo)
    print(f"{len(GEN)} generated sounds, {len(todo)} missing, {secs} s = {secs * 0.25:.1f} credits")
    if "--list" in sys.argv:
        print(", ".join(todo))
        return
    jobs = {}
    if os.path.exists(RAW + "/_jobs.json"):
        jobs = json.load(open(RAW + "/_jobs.json"))
    failed = []
    if "--process" not in sys.argv:
        for i, n in enumerate(todo):
            try:
                jobs[n] = generate(n, *GEN[n])
                json.dump(jobs, open(RAW + "/_jobs.json", "w"), indent=1)
                print(f"  [{i + 1}/{len(todo)}] {n} ok", flush=True)
            except Exception as exc:
                failed.append(n)
                print(f"  [{i + 1}/{len(todo)}] {n} FAILED (not retried): {exc}", flush=True)
                if "credit" in str(exc).lower():
                    break
    credits = ["# Wellness Check: audio sources", "",
               "## Generated", "Sound effects and ambiences named below were generated for this game with Higgsfield (Mirelo text-to-audio) on Cheyenne's paid plan; job ids are in raw/_jobs.json.", ""]
    credits.append(", ".join(sorted(n for n in GEN if os.path.exists(f"{RAW}/{n}.wav"))))
    credits += ["", "## Kenney (CC0 1.0), from the Open Game SFX library", ""]
    done = 0
    for n in GEN:
        if os.path.exists(f"{RAW}/{n}.wav"):
            try:
                process(n, f"{RAW}/{n}.wav"); done += 1
            except Exception as exc:
                print("  process", n, "failed:", str(exc)[:160])
    for n, rel in COPY.items():
        src = f"{KEN}/{rel}"
        if os.path.exists(src):
            process(n, src); done += 1
            credits.append(f"- {n}: {rel}")
        else:
            print("  missing library file", rel)
    credits += ["", "## Music (credit required)", ""]
    for n, (f, st, ln, cr) in MUSIC.items():
        src = f"{LIB}/{f}"
        if os.path.exists(src):
            process(n, src, st, ln); done += 1
            credits.append(f"- {n}: {cr}")
        else:
            print("  missing music", f)
    credits += ["", "## Voices", "Dialogue generated with Google Gemini TTS (see VO/_manifest.json). Radio and phone treatment: Cheyenne's Forklight Voice Effects v1 (voice_effects.py).", ""]
    # Later mastering passes maintain their own credit sections below Voices.
    credit_file = os.path.join(OUT, "AUDIO_CREDITS.md")
    if os.path.exists(credit_file):
        with open(credit_file, encoding="utf-8") as prior:
            voices = prior.read().partition("\n## Voices\n")[2]
            extra = voices.partition("\n## ")[2]
            if extra:
                credits.append("## " + extra)
    with open(credit_file, "w", encoding="utf-8") as out:
        out.write("\n".join(credits))
    print(f"processed {done}; failed: {failed}")


if __name__ == '__main__':
    main()
