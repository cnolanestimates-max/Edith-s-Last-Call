"""Generate dialogue with Google (Gemini) TTS from the line table in Source/WellnessCheck/WCStory.cpp.

  python gen_vo.py            -> generates every missing line (dry) then processes all
  python gen_vo.py --list     -> show what would be generated (no cost)
  python gen_vo.py --only id1,id2   --force   -> regenerate specific lines

Dry takes: SourceArt/Audio/VO_dry/<id>.wav (never overwritten unless --force).
Processed: SourceArt/Audio/VO/<id>.wav  (48 kHz mono 16-bit; radio/phone lines get Cheyenne's Forklight device effect).
Each generation is billed, so failures are NOT retried; they are listed at the end.
The API key is read from the user's GEMINI_API_KEY and never printed.
"""
import base64, json, os, re, subprocess, sys, urllib.request, winreg

ROOT = "C:/GameDev/Unreal/WellnessCheck"
STORY = ROOT + "/Source/WellnessCheck/WCStory.cpp"
DRY = ROOT + "/SourceArt/Audio/VO_dry"
OUT = ROOT + "/SourceArt/Audio/VO"
FX = "C:/Users/cheye/OneDrive/Documents/ChatGPT/forklight-tts/Forklight_Voice_Effects_v1_2026-10-10/voice_effects.py"
PY = "C:/Users/cheye/Documents/LocalAI/SF3D/.venv/Scripts/python.exe"
BASE = "https://generativelanguage.googleapis.com/v1beta"
MODEL = "gemini-3.8-flash-tts"

VOICE = {"deputy": "algenib", "dispatch": "kore", "mabel": "gacrux"}
STYLE = {
    "deputy": "A rural county sheriff's deputy in his mid-forties, alone in a dark, silent house at night. Low, tense, quiet, natural and understated, like real body-cam audio. American Midwest. No theatrics.",
    "dispatch": "A calm, experienced female county sheriff's dispatcher speaking over the police radio at 3 a.m. Clipped, professional, even pace, slightly flat. American Midwest.",
    "mabel": "A very old, frail woman in her late eighties. Thin, dry, trembling voice, slow, breathy, barely above a whisper, lonely and eerily gentle. Rural American.",
}
# per-line direction (added to the speaker style)
DIRECT = {
    "m_laugh1": "No words at all: only laughter. A very old woman giggling quietly to herself, dry, breathy and childlike, as if at a private joke. Eerie.",
    "m_laugh2": "No words at all: only a soft, pleased, slightly unhinged little laugh, under her breath.",
    "m_cry1": "No real words: a very old woman crying softly, alone, thin wet hopeless sobs.",
    "m_cry2": "No words: quiet, muffled weeping, as if into her hands, with shaky breaths.",
    "m_ear1": "Whispered, extremely close, right into the listener's ear. One breath. Intimate and wrong.",
    "m_ear2": "Whispered, extremely close, right into the listener's ear, almost fond.",
    "m_ear3": "Whispered, extremely close, pleading, right into the listener's ear.",
    "m_hum": "No words: humming a slow lullaby to herself, tunelessly and very quietly, mouth closed.",
    "d_arrive3": "Dry, uneasy, under his breath.",
    "d_knock": "Calling out loudly at a front door, projecting, official.",
    "d_dooropen": "Quiet, wary, then calling into the house.",
    "d_foyer": "Disgusted by a smell, muttering, then calling out.",
    "d_thump": "Startled, calling up a staircase, trying to sound steady.",
    "d_peek": "Very soft and careful, as if to a frightened animal.",
    "d_masterempty": "Unsettled, thinking out loud.",
    "d_radio1": "Speaking into a shoulder radio, urgent but controlled.",
    "d_doorstuck": "Rising panic, straining at a door.",
    "d_stop": "Shouting a police command, frightened but forceful.",
    "d_stop2": "Shouting, voice cracking with fear.",
    "d_getup1": "Shaken, out of breath, getting up off the floor.",
    "d_getup1b": "Disbelief, breathing hard.",
    "d_wayout": "Talking himself down, shaky.",
    "d_light_dead": "Panicked whisper, shaking a dead flashlight.",
    "d_after_kitchen": "A terrified shout, gasping.",
    "d_ceiling": "A horrified whisper, barely audible.",
    "d_getup2": "Grim realisation, quiet, winded.",
    "d_underbed": "A sharp startled cry.",
    "d_tags": "Sad, slowly understanding.",
    "d_cellar_open": "Resolved, quiet, steadying himself.",
    "d_body": "Gentle, grieving, very quiet.",
    "d_place": "Tender and steady, speaking to the dead.",
    "d_knot1": "Tense, through his teeth.",
    "d_knot2": "Tenser, louder, afraid.",
    "d_knot3": "Soft, kind, final.",
    "r_trace": "Urgent, breaking protocol slightly, uneasy.",
    "d_trace": "Stunned, slow, quiet.",
    "r_end3": "Hushed and frightened, almost whispering.",
    "r_arrive2": "Matter-of-fact, a little puzzled by it.",
    "d_dawn": "Exhausted, relieved, almost a breath.",
    "d_end1": "Exhausted, hoarse, into the radio.",
    "d_end2": "Flat, drained, gentle.",
    "d_radio1": "Speaking into a shoulder radio, low and controlled.",
    "d_end3": "Cold dread, very quiet, slow.",
    "r_end1": "Alarmed and relieved, faster than usual.",
    "r_end2": "Professional, then distracted mid-sentence by something on her console.",
    "m_phone1": "Over a telephone, delighted in a hollow way, almost a sigh.",
    "m_phone2": "Mournful, very slow.",
    "m_phone3": "Sweet and coaxing, with something wrong underneath.",
    "m_fin1": "A single pleading word, fragile.",
    "m_fin2": "Begging, tearful, a little louder.",
    "m_fin3": "Anguished, rising to a wail on the second sentence.",
    "m_fin4": "A raw, terrible, drawn-out scream of the single word.",
    "m_end": "At peace, a faint relieved whisper, fading.",
    "m_whisper1": "A faint, suspicious whisper from another room.",
    "m_whisper2": "A hopeful, heartbreaking whisper.",
    "r_static": "A barely audible whisper of one word.",
    "m_post": "A gentle, inviting whisper, smiling.",
}
SPEAK_AS = {"r_static": "mabel", "m_post": "mabel"}
TEXT = {"r_static": "Stay.", "m_whisper1": "Who's there?", "m_whisper2": "Is that you, Danny?", "m_post": "Come back and visit."}
EFFECT = {"r_static": "radio", "m_post": "radio"}


def key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as h:
            k = winreg.QueryValueEx(h, "GEMINI_API_KEY")[0]
    return k


def lines():
    src = open(STORY, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'\{\s*TEXT\("([a-z0-9_]+)"\),\s*TEXT\("([^"]*)"\),\s*TEXT\("((?:[^"\\]|\\.)*)"\),\s*(\d)\s*\}', src):
        lid, speaker, text, kind = m.group(1), m.group(2), m.group(3).replace('\\"', '"'), int(m.group(4))
        who = SPEAK_AS.get(lid) or ("dispatch" if lid.startswith("r_") else ("mabel" if lid.startswith("m_") else "deputy"))
        fx = EFFECT.get(lid) or ("radio" if kind == 1 else ("phone" if kind == 4 else ("ghost" if who == "mabel" else "dry")))
        out.append({"id": lid, "who": who, "text": TEXT.get(lid, text), "fx": fx, "style": (STYLE[who] + " " + DIRECT.get(lid, "")).strip()})
    return out


def generate(line, k):
    body = {"model": MODEL,
            "input": [{"type": "user_input", "content": [{"type": "text", "text": line["text"], "annotations": [{"type": "speech_metadata", "style": line["style"]}]}]}],
            "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [{"voice": VOICE[line["who"]]}]}}
    req = urllib.request.Request(BASE + "/interactions", data=json.dumps(body).encode(), method="POST",
                                 headers={"x-goog-api-key": k, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        res = json.loads(r.read())
    audio = None
    for step in res.get("steps", []):
        if step.get("type") == "model_output":
            for c in step.get("content", []):
                if c.get("type") == "audio":
                    audio = c
    if not audio or not audio.get("data"):
        raise RuntimeError("no audio returned")
    return base64.b64decode(audio["data"])


def ff(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args, check=True)


def process(line):
    src = f"{DRY}/{line['id']}.wav"
    dst = f"{OUT}/{line['id']}.wav"
    tmp = f"{DRY}/_tmp_{line['id']}.wav"
    tmp2 = f"{DRY}/_tmp2_{line['id']}.wav"
    # clean: trim silence, add small handles, level
    ff(["-i", src, "-af", "silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-48dB:start_silence=0.12,areverse,"
        "adelay=60|60,apad=pad_dur=0.18,loudnorm=I=-19:TP=-2.5:LRA=11", "-ac", "1", "-ar", "48000", tmp])
    fx = line["fx"]
    if fx in ("radio", "phone"):
        if os.path.exists(tmp2):
            os.remove(tmp2)
        subprocess.run([PY, FX, tmp, tmp2, "--device-line", "--preset", fx, "--intensity", "standard"], check=True, capture_output=True)
        ff(["-i", tmp2, "-af", "loudnorm=I=-18:TP=-2.0", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", dst])
        os.remove(tmp2)
    elif fx == "ghost":
        # she is not quite in the room: a little lower, a close whispering double and a cold tail
        ff(["-i", tmp, "-af", "asetrate=48000*0.94,aresample=48000,atempo=1.04,highpass=f=140,"
            "aecho=0.8:0.55:38|71:0.32|0.22,aecho=0.9:0.5:260|410:0.20|0.12,loudnorm=I=-18:TP=-2.0", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", dst])
    else:
        ff(["-i", tmp, "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", dst])
    os.remove(tmp)


def main():
    os.makedirs(DRY, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    L = lines()
    only = None
    force = "--force" in sys.argv
    if "--only" in sys.argv:
        only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
    todo = [l for l in L if (only is None or l["id"] in only) and (force or not os.path.exists(f"{DRY}/{l['id']}.wav"))]
    chars = sum(len(l["text"]) for l in todo)
    print(f"{len(L)} lines in script, {len(todo)} to generate, {chars} characters")
    if "--list" in sys.argv:
        for l in todo:
            print(f"  {l['id']:16s} {l['who']:8s} {l['fx']:6s} {l['text'][:70]}")
        return
    failed = []
    if todo and "--process-only" not in sys.argv:
        k = key()
        import time
        pace = float(sys.argv[sys.argv.index("--pace") + 1]) if "--pace" in sys.argv else 0.0
        for i, l in enumerate(todo):
            if i and pace:
                time.sleep(pace)
            try:
                data = generate(l, k)
                open(f"{DRY}/{l['id']}.wav", "wb").write(data)
                print(f"  [{i + 1}/{len(todo)}] {l['id']} {len(data) // 1024} KB")
            except Exception as exc:
                msg = str(exc)
                failed.append((l["id"], msg[:160]))
                print(f"  [{i + 1}/{len(todo)}] {l['id']} FAILED (not retried): {msg[:160]}")
                if "429" in msg:
                    print("  rate limited: stopping this run")
                    break
    done = 0
    for l in L:
        if only is not None and l["id"] not in only:
            continue
        if os.path.exists(f"{DRY}/{l['id']}.wav"):
            try:
                process(l)
                done += 1
            except Exception as exc:
                print(f"  process {l['id']} failed: {str(exc)[:200]}")
    json.dump(L, open(OUT + "/_manifest.json", "w"), indent=1)
    print(f"processed {done}; failed generations: {failed}")


main()
