"""One still for a television tape, made with an image model that follows a pose drawing (2 credits at 1k), to be checked
BEFORE the 10-credit video is made from it (gen_tv_clips.py uses it as the start image).

Cheyenne 04:48 UTC, with a drawing: the thing is very lanky and bent almost entirely in half, legs and body going straight up
side by side like a hairpin, head hanging at the bottom by its feet, level with the girl's face; its face is UPSIDE DOWN and is
a grey grinning mask with hollow eyes, looking at the girl.  (An original mask face, not a copy of any film's mask.)

  python gen_tv_still.py <name> [--force]     writes SourceArt/TV/raw/<name>_still.png   (never retried on failure)
"""
import json, os, subprocess, sys, urllib.request

ROOT = "C:/GameDev/Unreal/WellnessCheck/SourceArt/TV"
STILLS = {
    "bedtime5": (
        "Photorealistic still frame from a 1991 family home video shot on a VHS camcorder, 4:3, dim warm bedside lamp light, soft focus, "
        "dull washed colour, a white date stamp OCT 31 1991 in the lower right corner. Keep the same child's bedroom, the same little girl in "
        "a white nightgown standing by her bed seen from the side, and the same elderly woman in a dark dress smiling in the doorway, as in "
        "the first reference image. Replace the creature with a new one in exactly the pose of the stick drawing in the second reference "
        "image: an impossibly lanky, emaciated, soot-black humanoid, far too tall for the room, folded completely in half like a hairpin. "
        "Its two stick-thin legs stand on the floor and go straight up to the ceiling; at the ceiling its body bends sharply back over, and "
        "its long thin torso comes straight back down, parallel to its legs and almost touching them, a tight narrow upside-down U. Its head "
        "hangs at the very bottom, down beside its own shins, exactly level with the little girl's face and only inches in front of her. "
        "Its head is UPSIDE DOWN: chin at the top, forehead at the bottom. Its face is a smooth pale grey mask: hollow black eye holes, thin "
        "arched painted eyebrows, round rosy cheeks, and a wide, fixed, closed-lip painted grin with a thin upturned painted moustache line; "
        "because the head is inverted the grin is above the eyes. The mask stares straight into the girl's eyes. Its long thin arms hang "
        "limp to the floor. Thin black smoke seeps off its body. The girl looks calmly back at it; the old woman smiles at it fondly, not at "
        "the camera. Nobody is afraid. Mundane, cheerful, deeply uncanny. No gore.",
        ["refs/room_frame.png", "refs/figure_pose_sketch.png"]),
    # Cheyenne 04:51 UTC on the still above: "pretty dang good ... the body a little more smokey ... and grey the face more".
    "bedtime6": (
        "Edit the reference image. Keep the room, the little girl, the old woman, the lighting, the framing, the date stamp and the "
        "creature's pose and position exactly as they are. Change only two things. First, the creature's body: make it smokier, as if it "
        "were half made of dense black smoke: its legs, back and arms are still solid enough to read, but their edges dissolve and tear "
        "away into thick drifting black smoke and soot that curls off the whole body and trails upward and along the ceiling. Second, the "
        "upside-down mask face: make it entirely grey, the dull colourless grey of ash or unpainted clay, with no pink and no skin tone at "
        "all: grey cheeks, grey lips, hollow black eye holes, the same fixed grin. Photorealistic VHS home video still, no gore.",
        ["raw/bedtime5_still.png"]),
    # Cheyenne 04:52 UTC: "grey the entire mask ... remove [the pink cheeks] and make the cheeks a little more pointy".
    "bedtime7": (
        "Edit the reference image. Keep everything exactly as it is: the room, the little girl, the old woman, the lighting, the framing, "
        "the date stamp, the smoky black creature and its pose. Change only the creature's upside-down mask face. It stays upside down, in "
        "the same place and the same size, and entirely dull ash grey with no pink or skin tone anywhere. Give the mask sharp, pointed, "
        "jutting cheekbones that stick out to angular points on either side of the face, and a wide, thin, fixed, closed-lip grin that "
        "curls up sharply at both corners toward those pointed cheeks; hollow black eye holes, thin arched brows. A theatrical grinning "
        "mask carved from grey clay. Photorealistic VHS home video still, no gore.",
        ["raw/bedtime6_still.png"]),
    # Cheyenne 04:59 UTC approved tape 1 and asked for three more with the same creature: one "further out ... the family in the
    # living room on the couches ... creature in the back ... in the kitchen or something ... the camera's not focusing on it ...
    # the family living their normal life"; the other two are mine to invent.
    "living": (
        "A new photorealistic still frame from a 1991 family home video shot on a VHS camcorder, 4:3, warm evening lamp light, soft focus, "
        "dull washed colour, a white date stamp NOV 24 1991 in the lower right corner. A wide shot of an ordinary wood-panelled American "
        "living room: a father, a mother, a boy of about twelve, a small girl of about six and an elderly grandmother in a dark dress sit "
        "on two worn sofas with supper plates on their laps, all watching a television that is off-frame to the left, laughing, relaxed, "
        "an ordinary evening. The camera is focused on the family. Behind them, an open doorway leads to a dim kitchen in the background, "
        "slightly out of focus. In that kitchen doorway stands the SAME creature as in the reference image, the same design in the same "
        "folded pose: an impossibly lanky smoke-black figure bent double so its back is up against the kitchen ceiling, its long legs and "
        "arms hanging straight down, thin black smoke curling off it, and its upside-down pointed grey mask face hanging at about the "
        "height of a seated person's head, turned toward the family, watching them. It is small in the frame, far back, half in shadow; "
        "nobody looks at it or notices it. Mundane, cheerful, and deeply uncanny. No gore.",
        ["raw/bedtime7_still.png"]),
    "yard": (
        "A new photorealistic still frame from a 1991 family home video shot on a VHS camcorder, 4:3, bright overcast summer afternoon, "
        "soft focus, dull washed colour, a white date stamp JUL 04 1991 in the lower right corner. The back yard of an old yellow "
        "farmhouse: a small girl of about six in a swimsuit runs laughing through a lawn sprinkler in the foreground, a boy of twelve "
        "chases her, and their mother in a summer dress pegs white bed sheets on a long washing line across the middle of the yard, "
        "smiling over her shoulder at the camera. Among the hanging white sheets, in full daylight, stands the SAME creature as in the "
        "reference image, the same design in the same folded pose: an impossibly lanky smoke-black figure taller than the washing line "
        "poles, bent double so that its long legs and arms hang straight down between the sheets, thin black smoke curling off it into "
        "the bright sky, and its upside-down pointed grey mask face hanging low between two sheets at the height of the mother's "
        "shoulder, right beside her, turned toward the playing children. Nobody looks at it or reacts to it. Mundane, cheerful, sunny, "
        "and deeply uncanny. No gore.",
        ["raw/bedtime7_still.png"]),
    "rocker": (
        "A new photorealistic still frame from a home video shot on a VHS camcorder left running on a tripod, 4:3, a dim parlour at night "
        "lit by a few candles, soft focus, dull washed colour, a white date stamp NOV 26 1998 in the lower right corner. The same elderly "
        "woman as in the reference image, older now, thinner and unkempt, in the same dark dress, sits alone in a wooden rocking chair "
        "in a neglected old-fashioned room, seen from the side. Folded over her is the SAME creature as in the reference image, the same "
        "design in the same folded pose: an impossibly lanky smoke-black figure bent double with its back against the ceiling, its long "
        "legs and arms hanging straight down around her chair, thin black smoke curling off it, and its upside-down pointed grey mask "
        "face hanging only inches in front of her face. She is smiling up at it with tired devotion and holds one thin hand flat against "
        "the cheek of the mask, as you would touch a husband's face. Nobody else is in the room; a supper table set for four stands "
        "untouched and dusty in the background. Lonely, tender, and deeply uncanny. No gore.",
        ["raw/bedtime7_still.png"]),
    # no pictures or lettering on anybody's clothes (the generator put cartoon figures and a band name on the children)
    "living2": (
        "Edit the reference image. Keep everything exactly as it is: the room, the five people and their poses and faces, the lamps, the "
        "kitchen doorway, the smoke-black folded creature and its grey mask, the framing and the date stamp. Change only the clothes of "
        "the two children and the things on the side table: the boy wears a plain grey T-shirt with nothing printed on it, the small girl "
        "wears a plain pale sweatshirt with nothing printed on it, and there is no drinks can, only a plain glass. No logos, lettering, "
        "brand names or cartoon characters anywhere in the picture.",
        ["raw/living_still.png"]),
    # the video service refused the first yard still (a child in a swimsuit): ordinary play clothes instead
    "yard2": (
        "Edit the reference image. Keep everything exactly as it is: the yellow farmhouse, the washing line and white sheets, the mother, "
        "the boy, the sprinkler, the smoke-black folded creature and its grey mask, the daylight, the framing and the date stamp. Change "
        "only the little girl's clothes: she wears a loose yellow T-shirt and long blue denim dungarees, fully dressed, running and "
        "laughing as before. No logos or lettering anywhere.",
        ["raw/yard_still.png"]),
    # Cheyenne 05:26 UTC picked two more ideas: the family asleep on their feet at 3 AM being "tucked in", and the grandmother on the
    # porch at night ("straight nighttime ... out in the cornfield or some shit the thing is").
    "hall3am": (
        "A new photorealistic still frame from a 1991 family home video shot on a hand-held VHS camcorder in the middle of the night, 4:3, "
        "lit only by the weak little lamp on the camcorder, everything else black, soft focus, dull washed colour, heavy noise, a white "
        "date stamp DEC 14 1991 in the lower right corner. The camera is in a dark upstairs hallway looking through a half-open door into "
        "a bedroom. Inside, the whole family from the second reference image (the father, the mother, the boy, the small girl and the "
        "elderly grandmother), all in pyjamas and nightgowns, stand in a row with their backs to the camera, facing the wallpapered wall, "
        "motionless, heads bowed, asleep on their feet. Folded over them is the SAME creature as in the first reference image, the same "
        "design in the same folded pose: an impossibly lanky smoke-black figure bent double with its back against the ceiling, legs and "
        "arms hanging straight down, black smoke curling off it, its upside-down pointed grey mask face hanging beside the mother's bowed "
        "head. With its long thin fingers it is gently drawing a blanket up around the boy's shoulders, tucking him in where he stands. "
        "Nobody is awake. Quiet, tender, and deeply uncanny. No gore.",
        ["raw/bedtime7_still.png", "raw/living2_still.png"]),
    "porchnight": (
        "A new photorealistic still frame from a 1992 family home video shot on a hand-held VHS camcorder at night, 4:3, soft focus, dull "
        "washed colour, heavy noise, a white date stamp AUG 09 1992 in the lower right corner. Full night, a black sky, no dusk glow. In "
        "the foreground on the left, on the wooden porch of an old farmhouse under one dim yellow porch bulb, the elderly woman from the "
        "reference image sits on a porch swing in a dark dress with a shawl, seen from behind and to the side, looking out into the dark "
        "and humming to herself. Beyond the porch rail is a cornfield at night, the nearest rows of tall corn faintly lit by the porch "
        "bulb and by weak moonlight, the rest black. Standing out in the corn, taller than the stalks, is the SAME creature as in the "
        "reference image, the same design in the same folded pose: an impossibly lanky smoke-black figure bent double, its long legs "
        "rising out of the corn and its body folded back down, black smoke drifting off it, its upside-down pointed grey mask face hanging "
        "low just above the tops of the corn and catching the light, turned toward the porch. One of its very long thin arms is raised "
        "high above the corn, the long-fingered hand open, waving slowly. The old woman is not afraid. Lonely, still, and deeply uncanny. "
        "No gore.",
        ["raw/bedtime7_still.png"]),
    # Cheyenne 05:35 UTC: "he needs to actually be in the cornfield ... standing straight up ... 15, 20 foot tall" (not folded here).
    "porchnight2": (
        "Edit the first reference image. Keep the porch, the yellow porch bulb, the porch swing, the old woman seen from behind, the night "
        "sky, the cornfield, the framing and the date stamp exactly as they are. Remove the creature from where it is and put it far out "
        "IN the cornfield, well back among the rows, standing fully upright this time, not folded: the same impossibly lanky smoke-black "
        "figure as in the second reference image, but drawn up to its full height of about six metres, three times the height of the corn, "
        "which only reaches its knees. Thin as a rail: very long straight legs, a long narrow torso, arms so long that the hands hang "
        "below the tops of the corn, black smoke drifting off it into the night sky. Its head is at the very top, upright, and its face "
        "is the same grey pointed-cheeked mask with hollow black eyes and a fixed grin, small and pale against the black sky, looking "
        "straight at the porch. It stands perfectly still, a tall dark shape against the night, only dimly lit by the porch bulb and the "
        "moon. The old woman is not afraid. Lonely, still, and deeply uncanny. Photorealistic VHS home video still, heavy noise, no gore.",
        ["raw/porchnight_still.png", "raw/bedtime7_still.png"]),
    # Cheyenne 05:36 UTC: "the kid's bedroom camera ... the whole black and white or night vision" (replaces the 3 AM hall idea).
    "nursery": (
        "A new still frame from a 1990s baby-monitor camera fixed high in the corner of a small nursery at night, looking down across "
        "the room, 4:3. Black-and-white infrared night vision: grey, grainy, low resolution, soft, slightly fish-eyed, blown-out "
        "highlights, scan lines, white on-screen text in the top left corner reading CAM 2 and in the lower right corner 03:07 AM. A "
        "wooden crib with a mobile hanging above it stands in the middle of the room; the crib is EMPTY, only a rumpled blanket and a "
        "soft toy in it. A rocking chair, a chest of drawers, a rug. Standing over the crib is the SAME creature as in the reference "
        "image, the same design in the same folded pose, seen in infrared: an impossibly lanky black figure bent double with its back "
        "against the ceiling, its long legs and arms hanging straight down, black smoke drifting off it, and its upside-down "
        "pointed-cheeked mask face hanging just above the empty crib, looking down into it, the mask and its hollow eyes glowing pale in "
        "the infrared. Both of its long-fingered hands hold the rail of the crib, rocking it gently. Nobody else is in the room. Quiet, "
        "tender, and deeply uncanny. No gore.",
        ["raw/bedtime7_still.png"]),
    # it came out standing on the grass in a gap in front of the corn; she wants it IN the field
    "porchnight3": (
        "Edit the reference image. Keep everything exactly as it is: the porch, the bulb, the swing, the old woman, the night sky, the "
        "framing, the date stamp, and the tall upright smoke-black creature with its grey pointed mask. Change only where the creature "
        "stands and the field: the cornfield is one unbroken wall of tall corn right across the picture with no gap and no path in it, "
        "and the creature stands much farther back, deep inside the field, in the middle of the corn. The corn hides its legs completely "
        "up to the thighs, corn stalks stand in front of it and all round it, and it still towers far above the field, its thin body, "
        "long hanging arms and small pale mask rising high over the corn tops against the black sky. Because it is farther away it is "
        "smaller in the frame and darker, lit only faintly. Photorealistic VHS home video still, heavy noise, no gore.",
        ["raw/porchnight2_still.png"]),
}


def main():
    name = sys.argv[1]
    prompt, refs = STILLS[name]
    out = f"{ROOT}/raw/{name}_still.png"
    if os.path.exists(out) and "--force" not in sys.argv:
        print("already made:", out)
        return
    cmd = ["cmd", "/c", "higgsfield.cmd", "generate", "create", "nano_banana_pro", "--prompt", prompt, "--aspect_ratio", "4:3", "--resolution", "1k"]
    for r in refs:
        cmd += ["--image-references", (ROOT + "/" + r).replace("/", "\\")]
    cmd += ["--wait", "--json"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    text = (r.stdout or "") + (r.stderr or "")
    url = next((v for v in text.replace("\\/", "/").split('"') if v.startswith("http") and any(e in v.lower() for e in (".png", ".jpg", ".jpeg", ".webp"))), None)
    jobs_path = ROOT + "/raw/_jobs.json"
    jobs = json.load(open(jobs_path)) if os.path.exists(jobs_path) else {}
    if not url:
        print("FAILED (not retried)", text[-400:].replace("\n", " "))
        jobs[name + "_still"] = {"failed": text[-300:]}
    else:
        tmp = out + ".dl"
        urllib.request.urlretrieve(url, tmp)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", tmp, "-update", "1", out], check=True, stdin=subprocess.DEVNULL)
        os.remove(tmp)
        jobs[name + "_still"] = {"url": url}
        print("still", name, os.path.getsize(out) // 1000, "KB")
    json.dump(jobs, open(jobs_path, "w"), indent=1)


main()
