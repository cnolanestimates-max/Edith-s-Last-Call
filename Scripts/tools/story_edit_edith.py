"""One-off: fold the approved story details into WCStory.cpp (Edith, the call from her own landline, new ending beat)."""
import io

ROOT = "C:/GameDev/Unreal/WellnessCheck/"
p = ROOT + "Source/WellnessCheck/WCStory.cpp"
s = io.open(p, encoding="utf-8").read()
lines = s.split("\n")


def find(i):
    key = '\t{ TEXT("%s"),' % i
    for n, l in enumerate(lines):
        if l.startswith(key):
            return n
    raise KeyError(i)


def fmt(i, speaker, text, kind):
    return '\t{ TEXT("%s"), TEXT("%s"), TEXT("%s"), %d },' % (i, speaker, text, kind)


def setline(i, speaker, text, kind):
    lines[find(i)] = fmt(i, speaker, text, kind)


def addafter(after, i, speaker, text, kind):
    lines.insert(find(after) + 1, fmt(i, speaker, text, kind))


D = "Deputy Brandt"
R = "Dispatch"
setline("r_arrive1", R, "Copy, Fourteen. Caller asked for a wellness check on an Edith Harrow, eighty-six, lives alone. Family's out of state. Nobody's laid eyes on her in months.", 1)
setline("r_arrive2", R, "Caller didn't leave a name, Fourteen. Gave the address, said she needs company, and hung up.", 1)
setline("d_arrive3", D, "...Needs company. Copy.", 0)
setline("r_arrive3", R, "Check on her and call it in.", 1)
setline("d_radio1", D, "Dispatch, Fourteen. I've got movement in the house. No contact yet.", 0)
addafter("d_radio1", "r_trace", R, "Fourteen, be advised. We ran the number on that wellness call. It came from the Harrow landline. From inside that house.", 1)
addafter("r_trace", "d_trace", D, "...Say again? That phone's cut off at the wall.", 0)
setline("d_radio2", D, "Dispatch? ...Dead. I'll call it in from the car.", 0)
setline("d_ceiling", D, "...Edith?", 0)
setline("d_cellar_open", D, "Okay, Edith. Let's finish this.", 0)
setline("d_body", D, "Oh, Edith. How long have you been sitting down here.", 0)
setline("d_place", D, "Walter. Ruth. Daniel. They're here, Edith. They're all here.", 0)
setline("d_knot3", D, "It's alright, Edith. You're not alone. You can let go.", 0)
setline("d_end2", D, "I found her. She's been gone a long time. Send the coroner, and call the daughter.", 0)
setline("r_end2", R, "Copy, Fourteen. ...Stand by. I've got a call coming in on the emergency line.", 1)
addafter("r_end2", "r_end3", R, "Fourteen... it's the Harrow landline again.", 1)
setline("d_end3", D, "...That's not possible. I'm looking right at the house.", 0)
s = "\n".join(lines)

old = '''		T = Say(TEXT("d_radio1"), T + 1.2f);
		After(T, [this]() { Play2D(TEXT("radio_static"), 0.8f, EWCSnd::Voice); });
		T = Say(TEXT("r_static"), T + 0.2f);'''
new = '''		T = Say(TEXT("d_radio1"), T + 1.2f);
		T = Say(TEXT("r_trace"), T + 0.5f);
		T = Say(TEXT("d_trace"), T + 0.4f);
		After(T, [this]() { Play2D(TEXT("radio_static"), 0.8f, EWCSnd::Voice); });
		T = Say(TEXT("r_static"), T + 0.2f);'''
assert old in s
s = s.replace(old, new)
old = '''	T = Say(TEXT("r_end2"), T + 0.5f);
	T = Say(TEXT("d_end3"), T + 0.9f);
	After(T + 0.5f, [this]() { FadeTo(1.f, 4.f); });
	After(T + 5.f, [this]()'''
new = '''	T = Say(TEXT("r_end2"), T + 0.5f);
	After(T + 0.4f, [this]() { PlayAt(TEXT("phone_ring"), Pos(TEXT("FrontDoorPoint")), 0.7f); });
	T = Say(TEXT("r_end3"), T + 2.4f);
	T = Say(TEXT("d_end3"), T + 1.1f);
	After(T - 0.3f, [this]() { FadeTo(1.f, 0.05f); SetLoop(TEXT("amb"), TEXT(""), 0.f, 0.05f); SetLoop(TEXT("music"), TEXT(""), 0.f, 0.05f, EWCSnd::Music); });
	T += 2.5f;
	After(T + 5.f, [this]()'''
assert old in s
s = s.replace(old, new)
s = s.replace("Mabel", "Edith")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

for f in ["Source/WellnessCheck/WCEntity.h", "Scripts/level/notes.json", "Scripts/level/build_house.py", "Source/WellnessCheck/WCGame.cpp"]:
    t = io.open(ROOT + f, encoding="utf-8").read()
    t2 = t.replace("Mabel", "Edith").replace("Mrs. M. Harrow", "Mrs. E. Harrow").replace("MRS MABEL HARROW", "MRS EDITH HARROW")
    if t2 != t:
        io.open(ROOT + f, "w", encoding="utf-8", newline="\n").write(t2)
        print("renamed in", f)
g = ROOT + "Scripts/audio/gen_vo.py"
t = io.open(g, encoding="utf-8").read()
t = t.replace('"d_knot3": "Soft, kind, final.",', '"d_knot3": "Soft, kind, final.",\n    "r_trace": "Urgent, breaking protocol slightly, uneasy.",\n    "d_trace": "Stunned, slow, quiet.",\n    "r_end3": "Hushed and frightened, almost whispering.",\n    "r_arrive2": "Matter-of-fact, a little puzzled by it.",')
t = t.replace('"d_arrive3": "Puzzled, under his breath.",', '"d_arrive3": "Dry, uneasy, under his breath.",')
t = t.replace('"d_end3": "Quiet and heavy, a long pause before the last sentence.",', '"d_end3": "Cold dread, very quiet, slow.",')
t = t.replace('"r_end2": "Softer, concerned, off-protocol.",', '"r_end2": "Professional, then distracted mid-sentence by something on her console.",')
t = t.replace('"d_end2": "Flat, drained, gentle.",', '"d_end2": "Flat, drained, gentle.",\n    "d_radio1": "Speaking into a shoulder radio, low and controlled.",')
io.open(g, "w", encoding="utf-8", newline="\n").write(t)
print("ok")
