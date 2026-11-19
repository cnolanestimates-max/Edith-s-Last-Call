"""The moving pictures for the living-room television (Cheyenne approved Higgsfield for this, 2026-11-19 03:56 UTC:
"macabre ... a family with a giant dark figure behind them but they act like the shadow figure is their friend").
Four 10-second shots, text to video, Grok Imagine Video 1.5 Lite at 480p 4:3: 10 credits each, 40 in all.
A shot that fails is NOT retried.  Raw results: SourceArt/TV/raw/<name>.mp4, job records in _jobs.json.

  python gen_tv_clips.py <name> [<name>...]     make those shots if they are missing (nothing is made unless named)
  python gen_tv_clips.py <name> --list          show what would be made
"""
import json, os, subprocess, sys, urllib.request

OUT = "C:/GameDev/Unreal/WellnessCheck/SourceArt/TV/raw"
MODEL = "grok_video_v15_lite"
STYLE = (" Shot on a consumer VHS camcorder in the late 1970s, 4:3, washed-out faded colour, soft focus, tape tracking lines, "
         "analog static and grain, slight handheld wobble, a date stamp burned into the corner. Analog horror, found footage. "
         "Quiet, slow, deeply unsettling. No blood, no gore, no text.")
SHOTS = {
    "porch": "A rural American family of four stands stiffly in a row on the porch of an old yellow farmhouse, smiling too widely and waving "
             "slowly at the camera. Directly behind them towers a gigantic, featureless, pitch-black shadow figure, nine feet tall and "
             "thin, with very long arms; its hands rest on the parents' shoulders like an old family friend. Nobody is afraid. The mother "
             "reaches up and pats its hand fondly.",
    "supper": "A family sits at a dining table set for supper by candlelight, all smiling fixedly at the camera. At the head of the table "
              "sits an enormous, featureless, pitch-black shadow figure, far too tall for its chair, its head bent under the ceiling. The "
              "grandmother sets a full plate in front of it and pats its long black arm, as you would for a favourite guest.",
    "bedtime": "A dim child's bedroom at night. A little girl in a white nightgown stands by her bed holding the enormous long-fingered hand "
               "of a towering, featureless, pitch-black shadow figure that stands beside her like a parent. She looks up at it and smiles. "
               "An old woman in the doorway nods and smiles at the camera.",
    "rocker": "An elderly woman in a floral dress sits in a rocking chair in an old-fashioned parlour, knitting and talking pleasantly to the "
              "camera. Close behind her chair stands a gigantic, motionless, featureless pitch-black shadow figure, its long hands resting on "
              "her shoulders. She stops knitting, reaches up, and holds one of its hands against her cheek.",
}


# Second pass after Cheyenne's notes (04:18 and 04:25 UTC): the figure must be horrifying, flowing black smoke in the shape of a
# man; Edith looks at IT, never at the camera; there are voices; photographic and mundane like her "uncanny video" references;
# much more grain.  These prompts stand alone (FULL: no shared style line is added).
REAL = (" Photorealistic amateur camcorder footage from 1989, 4:3, handheld, real ordinary people, mundane and matter-of-fact, nobody is "
        "afraid, deeply uncanny. Very heavy VHS grain and noise, dull washed-out colour, soft focus, tape tracking distortion, a white "
        "date stamp in the corner.")
SMOKE = ("a horrifying presence: a towering humanoid shape nearly three metres tall made entirely of dense flowing black smoke, constantly "
         "churning, billowing and curling like ink in water, its edges tearing away in drifting wisps, with a long stretched faceless head, "
         "elongated limbs and far too long fingers of smoke")
FULL = {
    "bedtime2": "A small dim child's bedroom at night lit by one weak lamp. A little girl in a white nightgown stands by her bed. Over her looms "
                + SMOKE + ". It bends slowly down over the girl, and she calmly holds one of its smoke hands as if it were her father. An elderly "
                "woman in a dark dress stands in the doorway gazing up at the smoke figure with tender devotion; she never looks at the camera. "
                "She says softly, in a frail old voice: \"Say goodnight to our friend, Ruthie.\" The girl answers: \"Goodnight.\" A low "
                "rattling breath comes from the figure." + REAL,
}
# Third pass (Cheyenne 04:33 UTC: "better but not uncanny enough, more like the reference pics"; grain and voices are right).
# Her references are photographic, mundane, warmly lit home video in which one thing is physically wrong and far too close, and
# everybody behaves as if it were normal.  So: daylight-ordinary room, real people, and the Company as a body: soot-black,
# stretched, bent under the ceiling, smoke coming off it, a grin and no eyes, its face beside the child's.
UNCANNY = ("an impossibly tall, emaciated humanoid figure almost three metres tall, bent double under the low ceiling, its whole body matte "
           "soot-black with thin black smoke constantly seeping and curling off its skin, grotesquely long thin arms and fingers, a long "
           "stretched head with no eyes and only a faint, far too wide, fixed grin")
HOME = (" Authentic family home video shot on a VHS camcorder in 1991, 4:3, warm indoor tungsten light, photorealistic real people, natural "
        "amateur handheld framing, slightly out of focus, dull washed colour, heavy VHS noise and tracking lines, a white date stamp in the "
        "corner. Mundane and cheerful, and deeply uncanny. No gore.")
# (Cheyenne 04:33: "just the visuals that need work, mainly the figure": the bedroom scene and the voices stay.)
FULL["bedtime3"] = ("A small child's bedroom at night lit by one weak bedside lamp. A little girl in a white nightgown stands by her bed. "
                    "An elderly woman in a dark dress stands in the doorway, smiling up, not at the camera but at the thing standing over the "
                    "child: " + UNCANNY + ", stooping so that its face is only inches from the top of the girl's head, one enormous long-fingered "
                    "hand resting gently on her shoulder. Nobody reacts to it; they behave as if it were her father. The old woman says softly, in "
                    "a frail old voice: \"Say goodnight to our friend, Ruthie.\" The girl answers: \"Goodnight.\"" + HOME.replace("warm indoor tungsten light", "dim warm lamp light"))
# Fourth pass (Cheyenne 04:38 UTC: "that's better ... so tall that it's bent ... a U shape, a tight U, almost a V ... its head is where
# its knees are ... its face right in front of hers, its torso where the mom's head is").  Same room, same people, same words.
FOLDED = ("an impossibly tall, emaciated humanoid figure, far too tall for the room, its whole body matte soot-black with thin black smoke "
          "constantly seeping and curling off its skin. Its stick-thin legs rise straight up to the ceiling, and there its body folds sharply "
          "in half at the waist like a hairpin, a tight upside-down U, so that its long torso hangs straight back down in front of its own legs "
          "and its head dangles at the height of its own knees. Its long stretched head has no eyes and only a faint, far too wide, fixed grin, "
          "and it hangs level with the little girl's face, face to face with her, only inches away. Its grotesquely long thin arms hang down to "
          "the floor, one enormous long-fingered hand resting gently on her shoulder. The fold of its back is up above the old woman's head")
FULL["bedtime4"] = ("A small child's bedroom at night lit by one weak bedside lamp. A little girl in a white nightgown stands by her bed, seen from "
                    "the side. An elderly woman in a dark dress stands in the doorway, smiling, looking not at the camera but at the thing that "
                    "stands folded over the child: " + FOLDED + ". Nobody reacts to it; they behave as if it were her father. The girl looks calmly "
                    "straight into its face. The old woman says softly, in a frail old voice: \"Say goodnight to our friend, Ruthie.\" The girl "
                    "answers: \"Goodnight.\"" + HOME.replace("warm indoor tungsten light", "dim warm lamp light"))
# Fifth pass: Cheyenne approved a STILL first (gen_tv_still.py; her Paint sketch for the pose, 04:48 to 04:55 UTC: folded in half,
# upside-down grey mask with pointed cheeks, smoky body; she picked "b").  The video starts from that still.
START = {"bedtime7": OUT + "/bedtime7_still.png"}
FULL["bedtime7"] = ("Continue this exact shot as a locked-off amateur camcorder take; nothing changes its design. The tall folded smoke-black "
                    "creature barely moves: its upside-down grey mask sways very slightly, slowly tilting as it stares into the little girl's "
                    "face, and black smoke keeps curling and drifting off its body toward the ceiling. Its long fingers twitch once. The little "
                    "girl stands still, calmly looking up into the mask. The elderly woman in the doorway smiles fondly at the creature, not "
                    "at the camera, and says softly, in a frail old voice: \"Say goodnight to our friend, Ruthie.\" The girl answers in a small "
                    "voice: \"Goodnight.\" Then silence, and the mask slowly tilts a little further. Slight handheld wobble, VHS home video, 1991, "
                    "heavy tape noise, mundane and deeply uncanny. No cuts, no new characters, no gore.")
# Tapes 2 to 4 (Cheyenne 04:59 UTC: "3 more videos like this"; the living room one is hers, the other two are mine).
START.update({"t_living": OUT + "/living2_still.png", "t_yard": OUT + "/yard2_still.png", "t_rocker": OUT + "/rocker_still.png"})
KEEP = " VHS home video, heavy tape noise, mundane and deeply uncanny. No cuts, no new characters, nothing changes its design, no gore."
FULL["t_living"] = ("Continue this exact shot from a camcorder on a tripod. The family keeps watching the television off-frame, laughing at it and "
                    "eating from the plates on their laps. The father says cheerfully: \"Oh, here it comes, watch this part.\" and they all laugh. "
                    "Nobody ever looks behind them. In the kitchen doorway in the background the folded smoke-black creature stays where it is, "
                    "out of focus: smoke drifts off it, and its upside-down grey mask very slowly tilts and drifts a little closer toward the "
                    "backs of their heads." + KEEP)
FULL["t_yard"] = ("Continue this exact shot, handheld camcorder, summer afternoon. The little girl in dungarees runs laughing across the lawn and the boy "
                  "chases her; the mother pegs the sheet and calls, laughing: \"Careful, you two!\" The white sheets sway in the breeze. The tall "
                  "folded smoke-black creature among the sheets does not move, except for the smoke curling off it and its upside-down grey mask, "
                  "which slowly turns to follow the little girl as she runs. Nobody looks at it or reacts to it." + KEEP)
FULL["t_rocker"] = ("Continue this exact shot from a camcorder left on a tripod. The old woman rocks gently in her chair, stroking the cheek of the "
                    "upside-down grey mask, and says softly, in a frail old voice: \"They all left. But you stayed. You always stay.\" Smoke curls "
                    "off the folded creature and the candle flames waver. Then the mask slowly turns away from her and looks straight into the "
                    "camera, and holds still. She keeps smiling up at it." + KEEP)
# Cheyenne 05:15 UTC: "your videos aren't very dynamic ... like moving stills ... I would like more dynamic videos".  The lite model
# and my own "barely moves" prompts were the cause.  Seedance 2.5 (30 credits for 10 s at 480p, with sound) from the still she approved,
# with a hand-held camera and everybody, the creature included, properly moving.
SEEDANCE = ["--mode", "omni_reference", "--generate_audio", "true"]
ENGINE = {"bedtime8": ("seedance_2_5", SEEDANCE), "living8": ("seedance_2_5", SEEDANCE + ["--duration", "15"])}
START["bedtime8"] = OUT + "/bedtime7_still.png"
FULL["bedtime8"] = ("Hand-held VHS camcorder home video from 1991, starting on this exact frame. The camera is held by a father walking into the "
                    "bedroom: it sways and bobs with his steps, drifts, and zooms in clumsily. Everything is in fluid, natural, continuous "
                    "motion. The little girl in the white nightgown bounces on her toes and giggles, glances round at the camera and waves, "
                    "then turns back and reaches up with both hands to pat the cheeks of the grey mask. The tall folded smoke-black creature "
                    "moves like a living animal: its long thin legs shift and re-plant like a spider's, its bent back ripples against the "
                    "ceiling, its dangling arms sway, thick black smoke pours and rolls off it. Its upside-down grey mask head swings down "
                    "on its long neck, tilts sharply from side to side like a curious bird, presses close to the girl's face, and one of its "
                    "long-fingered hands comes up and strokes her hair. The old woman walks in from the doorway laughing, straightens the "
                    "girl's collar and says warmly, in a frail old voice: \"Say goodnight to our friend, Ruthie.\" The girl says brightly: "
                    "\"Goodnight!\" At the very end the mask snaps round and stares straight into the camera. Nobody is afraid; a cheerful "
                    "family bedtime. Keep the creature's design, the grey pointed mask, the room and the people exactly as in the frame. "
                    "Heavy VHS tape noise, dull washed colour, a date stamp in the corner. No cuts, no gore.")
# Cheyenne 05:24 UTC on the Seedance test: "way better ... make them all like that ... redo the living room too ... about 15 seconds".
START["living8"] = OUT + "/living2_still.png"
FULL["living8"] = ("Hand-held VHS camcorder home video from 1991, starting on this exact frame. An uncle is filming: the camera sways, drifts and "
                   "pans across the room, zooming clumsily. Everything is in fluid, natural, continuous motion. The family is watching "
                   "television and eating supper off their laps: the father laughs with his mouth full and points at the screen with his "
                   "fork, saying: \"Oh, here it comes, watch this part!\" The mother rocks with laughter and slaps his knee. The boy and the "
                   "little girl squabble over a cushion and the girl squeals. While they laugh, the tall folded smoke-black creature in the "
                   "kitchen doorway behind them comes into the room: its long thin legs step over the threshold like a spider's, its bent "
                   "back slides along the ceiling, black smoke rolling off it, and its upside-down grey mask head swings slowly down over "
                   "the back of the sofa until it hangs between the boy and the grandmother, tilting sharply from side to side like a "
                   "curious bird. Without looking round, the grandmother reaches up, pats the mask's cheek and says fondly, in a frail old "
                   "voice: \"Sit down, dear, you are in the light.\" The little girl twists round, grins and waves at it. The camera pans "
                   "back to the father, still laughing. At the very end the mask turns and stares straight into the camera. Nobody is "
                   "afraid; an ordinary happy evening. Keep the creature's design, the grey mask, the room and the people exactly as in the "
                   "frame. Heavy VHS tape noise, dull washed colour, a date stamp in the corner. No cuts, no gore.")
# Tapes 3 and 4 (Cheyenne 05:26 UTC: "I like 3 and 4"; 05:27: the porch is "straight nighttime ... out in the cornfield").
ENGINE["nursery8"] = ENGINE["porch8"] = ("seedance_2_5", SEEDANCE + ["--duration", "15"])
START["nursery8"] = OUT + "/nursery2_still.png"       # (the 3 AM hall idea was rejected and is not made)
START["porch8"] = OUT + "/porchnight4_still.png"
FULL["nursery8"] = ("Footage from a 1990s baby-monitor camera fixed high in the corner of a child's bedroom at night, starting on this exact "
                    "frame: black-and-white infrared night vision, grainy, scan lines, the CAM 2 and 03:07 AM text staying fixed on screen. "
                    "The camera does not move, but everything in the room does, in fluid, natural, continuous motion. The tall folded black "
                    "creature rocks the empty crib slowly back and forth with both long hands; the crib creaks, the mobile above it turns and "
                    "tinkles, black smoke rolls off the creature along the ceiling, and its upside-down mask head sways gently over the "
                    "empty mattress, its eyes shining white. It hums, low and tuneless. The rocking horse begins to rock by itself. The door "
                    "on the left swings slowly further open. Then the creature stops rocking, lets go of the rail, and its mask head turns, "
                    "slowly, all the way round, until the two white eyes are looking straight up into the camera. It unfolds one long arm "
                    "and reaches toward the lens, and the picture breaks into static. Keep the creature's design, the mask and the room "
                    "exactly as in the frame. No cuts, no people, no gore.")
FULL["porch8"] = ("Hand-held VHS camcorder home video at night, 1992, starting on this exact frame. Full darkness beyond the one yellow porch "
                  "bulb; crickets. The camera sways gently in someone's hands. Everything is in fluid, natural, continuous motion. The old "
                  "woman rocks slowly on the creaking porch swing, humming an old lullaby in a frail voice, and lifts one hand to wave at "
                  "the field. Out in the corn, waist-deep, the tall upright smoke-black creature sways with the tune: it lifts one very "
                  "long thin arm high out of the corn and waves slowly from side to side in time with her humming, the corn stalks bend "
                  "and rustle round it in the night wind, black smoke drifts off its shoulders, and its grey mask head tilts from side to "
                  "side like a curious bird. The camera drifts off her and zooms clumsily in on the thing in the corn. It stops waving. It "
                  "begins to wade toward the porch through the corn, slowly, the stalks parting and shaking in front of it, the mask held "
                  "perfectly level and getting larger. The old woman says softly and fondly: \"There you are. Come on "
                  "in, then.\" Keep the creature's design, the grey mask, the porch and the old woman exactly as in the frame. Heavy VHS "
                  "tape noise, dull washed colour, a date stamp in the corner. No cuts, no gore.")
SHOTS.update(FULL)


def main():
    os.makedirs(OUT, exist_ok=True)
    jobs_path = OUT + "/_jobs.json"
    jobs = json.load(open(jobs_path)) if os.path.exists(jobs_path) else {}
    want = [a for a in sys.argv[1:] if not a.startswith("--")]
    todo = [n for n in SHOTS if not os.path.exists(f"{OUT}/{n}.mp4") and n in want]
    skipped = [n for n in SHOTS if not os.path.exists(f"{OUT}/{n}.mp4") and n not in want]
    if skipped:
        print("not asked for, not made:", ", ".join(skipped))
    cost = sum((45 if "15" in ENGINE[n][1] else 30) if n in ENGINE else 10 for n in todo)
    print(f"{len(SHOTS)} shots, {len(todo)} to make, about {cost} credits")
    if "--list" in sys.argv:
        for n in todo:
            print("  ", n)
        return
    for n in todo:
        model, extra = ENGINE.get(n, (MODEL, []))
        cmd = ["cmd", "/c", "higgsfield.cmd", "generate", "create", model, "--prompt", SHOTS[n] + ("" if n in FULL else STYLE),
               "--resolution", "480p", "--aspect_ratio", "4:3"] + (extra if "--duration" in extra else ["--duration", "10"] + extra)
        if n in START:
            cmd += ["--start-image", START[n].replace("/", "\\")]
        cmd += ["--wait", "--json"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1500)
        text = (r.stdout or "") + (r.stderr or "")
        url = None
        try:
            data = json.loads(r.stdout[r.stdout.index("{"):])
            jobs[n] = {k: data.get(k) for k in ("id", "status", "job_type", "result_url", "credits") if k in data}
            url = data.get("result_url") or next((v for v in json.dumps(data).split('"') if v.startswith("http") and ".mp4" in v), None)
        except Exception:
            url = next((v for v in text.split('"') if v.startswith("http") and ".mp4" in v), None)
        if not url:
            print("  FAILED (not retried)", n, text[-300:].replace("\n", " "))
            jobs[n] = {"failed": text[-300:]}
        else:
            urllib.request.urlretrieve(url, f"{OUT}/{n}.mp4")
            print("  ", n, os.path.getsize(f"{OUT}/{n}.mp4") // 1000, "KB")
        json.dump(jobs, open(jobs_path, "w"), indent=1)


main()
