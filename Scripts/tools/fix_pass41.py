"""Cheyenne 22:16: her laugh, her crying, a whisper at your ear, in the walls and round corners; quiet and occasional."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCStory.cpp", [
    ('''	{ TEXT("m_mem1"), TEXT("Edith"),''', '''	{ TEXT("m_laugh1"), TEXT(""), TEXT("Heh heh heh heh... hee hee hee."), 2 },
	{ TEXT("m_laugh2"), TEXT(""), TEXT("Hm hm hm hm hm. Ha... ha ha ha."), 2 },
	{ TEXT("m_cry1"), TEXT(""), TEXT("Ohh... oh... oh no... ohh."), 2 },
	{ TEXT("m_cry2"), TEXT(""), TEXT("Hnnh... hh... hh... mmm... hh."), 2 },
	{ TEXT("m_ear1"), TEXT(""), TEXT("Stay."), 2 },
	{ TEXT("m_ear2"), TEXT(""), TEXT("I see you."), 2 },
	{ TEXT("m_ear3"), TEXT(""), TEXT("Don't go."), 2 },
	{ TEXT("m_hum"), TEXT(""), TEXT("Mm mm mmm, mm mm mmm, mmm mm, mmm."), 2 },
	{ TEXT("m_mem1"), TEXT("Edith"),'''),
    # ambience: her voice joins the house noises (more of it as the night goes on)
    ('''			{ TEXT("whisper_far"), 0.7f, 400.f, 900.f, 0.8f, 0 }, { TEXT("breath_near"), 0.35f, 90.f, 160.f, 0.7f, 0 } };''',
     '''{ TEXT("whisper_far"), 0.7f, 400.f, 900.f, 0.8f, 0 }, { TEXT("breath_near"), 0.35f, 90.f, 160.f, 0.7f, 0 },
			{ TEXT("VO/m_laugh1"), 0.30f, 350.f, 800.f, 0.55f, 2 }, { TEXT("VO/m_laugh2"), 0.30f, 300.f, 700.f, 0.55f, 1 },
			{ TEXT("VO/m_cry1"), 0.32f, 400.f, 900.f, 0.6f, 1 }, { TEXT("VO/m_cry2"), 0.30f, 250.f, 600.f, 0.55f, 2 }, { TEXT("VO/m_hum"), 0.30f, 400.f, 900.f, 0.5f, 0 },
			{ TEXT("VO/m_ear1"), 0.16f, 35.f, 55.f, 0.5f, 3 }, { TEXT("VO/m_ear2"), 0.14f, 35.f, 55.f, 0.5f, 3 }, { TEXT("VO/m_ear3"), 0.14f, 35.f, 55.f, 0.5f, 3 } };'''),
    ('''		for (const FCue& C : Cues) Total += C.Weight * (FCString::Strcmp(C.Name, TEXT("breath_near")) == 0 || FCString::Strcmp(C.Name, TEXT("whisper_far")) == 0 ? (0.3f + 2.f * Tension) : 1.f);''',
     '''auto Scale = [this](const FCue& C) -> float
		{
			// her own voice (and breath) is rare while the house is only a house, and grows with the night; none of it before the door locks
			const bool bHers = FCString::Strncmp(C.Name, TEXT("VO/"), 3) == 0 || FCString::Strcmp(C.Name, TEXT("breath_near")) == 0 || FCString::Strcmp(C.Name, TEXT("whisper_far")) == 0;
			if (!bHers) return 1.f;
			return Has(TEXT("locked_in")) ? (0.3f + 2.f * Tension) : 0.f;
		};
		for (const FCue& C : Cues) Total += C.Weight * Scale(C);'''),
    ('''			const float W = C.Weight * (FCString::Strcmp(C.Name, TEXT("breath_near")) == 0 || FCString::Strcmp(C.Name, TEXT("whisper_far")) == 0 ? (0.3f + 2.f * Tension) : 1.f);''',
     '''const float W = C.Weight * Scale(C);'''),
    ('''		else if (Chosen->Where == 2) Off.Z = Rng.FRandRange(-60.f, 120.f);''', '''else if (Chosen->Where == 2) Off.Z = Rng.FRandRange(-60.f, 120.f);
		else if (Chosen->Where == 3)
		{
			// at his ear: just behind him, to one side.  He turns, and there is nothing there.
			const FRotator Yaw(0.f, P->GetControlRotation().Yaw, 0.f);
			Off = -Yaw.Vector() * 28.f + FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y) * (Rng.FRand() < 0.5f ? -24.f : 24.f) + FVector(0, 0, 58.f);
		}'''),
])
p = "C:/GameDev/Unreal/WellnessCheck/Scripts/audio/gen_vo.py"
s = io.open(p, encoding="utf-8").read()
a = 'DIRECT = {\n'
assert a in s
s = s.replace(a, a + '''    "m_laugh1": "No words at all: only laughter. A very old woman giggling quietly to herself, dry, breathy and childlike, as if at a private joke. Eerie.",
    "m_laugh2": "No words at all: only a soft, pleased, slightly unhinged little laugh, under her breath.",
    "m_cry1": "No real words: a very old woman crying softly, alone, thin wet hopeless sobs.",
    "m_cry2": "No words: quiet, muffled weeping, as if into her hands, with shaky breaths.",
    "m_ear1": "Whispered, extremely close, right into the listener's ear. One breath. Intimate and wrong.",
    "m_ear2": "Whispered, extremely close, right into the listener's ear, almost fond.",
    "m_ear3": "Whispered, extremely close, pleading, right into the listener's ear.",
    "m_hum": "No words: humming a slow lullaby to herself, tunelessly and very quietly, mouth closed.",
''', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
compile(s, p, "exec")
print("ok")
