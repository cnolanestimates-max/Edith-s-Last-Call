# Pass 129 (Cheyenne, 21:31 UTC): the opening, as she laid it out.
#  1. The trash can is "a waste management type of trash can ... big", with "lots of trash strung out", a LOUD bang and
#     clang, skittering, then "thump, thump, thump, like running away", the screen shaking, and the deputy "scared".
#  2. At the door: his knock line; then he finds it locked and says so; then he says he will check round the side.
#     Back at the front after the shed: "Mrs. Harrow, people are worried about you. We're just trying to see if you're
#     okay. Can you please open up?" and the door opens as he says "open up".
# Also the 1990s: dispatch says "welfare check" (the word then), her own telephone and not "landline", and Edith is
# seventy-two (born 1921, as the clipping and the ring already have it; eighty-six made her forty at Ruth's birth in 1961).
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

ROOT = r"C:\GameDev\Unreal\WellnessCheck"
S = ROOT + r"\Source\WellnessCheck\WCStory.cpp"

edit(S, [
    ("""TEXT("Copy, Fourteen. Caller asked for a wellness check on an Edith Harrow, eighty-six, lives alone. Family's out of state. Nobody's laid eyes on her in months."), 1 },""",
     """TEXT("Copy, Fourteen. Caller asked for a welfare check on an Edith Harrow, seventy-two, lives alone. Family's out of state. Nobody's laid eyes on her in months."), 1 },"""),
    ("""	{ TEXT("d_dooropen"), TEXT("Deputy Brandt"), TEXT("...Door's open. Mrs. Harrow, I'm coming in."), 0 },
""",
     """	{ TEXT("d_dooropen"), TEXT("Deputy Brandt"), TEXT("...Door's open. Mrs. Harrow, I'm coming in."), 0 },
	{ TEXT("d_side"), TEXT("Deputy Brandt"), TEXT("It's locked. ...Maybe I'll check around the side."), 0 },
	{ TEXT("d_openup"), TEXT("Deputy Brandt"), TEXT("Mrs. Harrow, people are worried about you. We're just trying to see if you're okay. ...Can you please open up?"), 0 },
"""),
    ("""	{ TEXT("d_shedcall"), TEXT("Deputy Brandt"), TEXT("Mrs. Harrow? ...Is that you?"), 0 },""",
     """	{ TEXT("d_shedcall"), TEXT("Deputy Brandt"), TEXT("Jesus Christ! ...Who's there?! Sheriff's department! ...Mrs. Harrow? ...Is that you?"), 0 },"""),
    ("""TEXT("Fourteen, be advised. We ran the number on that wellness call. It came from the Harrow landline. From inside that house."), 1 },""",
     """TEXT("Fourteen, be advised. We ran the number on that welfare call. It came from Mrs. Harrow's own telephone. From inside that house."), 1 },"""),
    ("""TEXT("Fourteen... it's the Harrow landline again."), 1 },""",
     """TEXT("Fourteen... it's the Harrow number again."), 1 },"""),
    # the trash can
    ("""			ApplyWorldState();                                   // the can is on its side now, its trash across the ground
			PlayAt(TEXT("trash_crash"), Pos(TEXT("TrashPoint")), 1.f, 1.f, 8000.f);
			if (AWCCharacter* Pl = Player()) Pl->AddShake(0.35f);
			Tension = FMath::Max(Tension, 0.5f);
			const float T = Say(TEXT("d_shedcall"), 2.6f);
			After(T + 1.2f, [this]() { OutsideProgress(); });
""",
     """			ApplyWorldState();                                   // the bin is over now, everything in it across the yard
			// it is the first thing in the game that makes him jump: loud, everywhere, and it shakes him
			Play2D(TEXT("trash_crash"), 1.f);
			PlayAt(TEXT("trash_crash"), Pos(TEXT("TrashPoint")), 1.f, 1.f, 9000.f);
			if (AWCCharacter* Pl = Player()) Pl->AddShake(1.f);
			After(0.45f, [this]() { if (AWCCharacter* Pl = Player()) Pl->AddShake(0.6f); });
			Tension = 1.f;
			// and whatever did it goes: heavy feet, fast, away along the back of the house and gone
			const FVector From = Pos(TEXT("TrashPoint")), To = Pos(TEXT("TrashRunTo"));
			if (!From.IsNearlyZero() && !To.IsNearlyZero())
				for (int32 k = 0; k < 9; ++k) After(1.9f + k * 0.21f, [this, From, To, k]() { PlayAt(TEXT("her_step"), FMath::Lerp(From, To, k / 8.f) + FVector(0, 0, 10), 1.f - 0.07f * k, Rng.FRandRange(0.82f, 0.92f), 7000.f); });
			UE_LOG(LogWCStory, Display, TEXT("WCTRASH t=%.1f the bin goes over; something runs"), PlaySeconds);
			const float T = Say(TEXT("d_shedcall"), 1.1f);
			After(T + 1.2f, [this]() { OutsideProgress(); });
"""),
    # the first knock: locked, and he says where he is going
    ("""			const float T = Say(TEXT("d_knock"), 0.9f);
			After(T + 2.5f, [this]() { OutsideProgress(); });
		}
		else if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; PlayAt(TEXT("knock"), Pos(TEXT("FrontDoorPoint")), 0.9f); Feedback(TEXT("No answer.")); }
""",
     """			float T = Say(TEXT("d_knock"), 0.9f);
			// nobody comes.  He tries the handle, says so, and says where he is going
			After(T + 1.6f, [this]() { PlayAt(TEXT("door_locked"), Pos(TEXT("FrontDoorPoint")), 0.9f); });
			T = Say(TEXT("d_side"), T + 2.4f);
			After(T + 0.6f, [this]() { OutsideProgress(); });
		}
		else if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; PlayAt(TEXT("knock"), Pos(TEXT("FrontDoorPoint")), 0.9f); Feedback(TEXT("No answer.")); }
"""),
    # back at the front: a different line, and the door opens on its last words
    ("""				float T = Say(TEXT("d_knock"), 0.9f);
			After(T + 1.6f, [this]()
			{
""",
     """				// (Cheyenne: "when he says, can you please open up, the door will open")
				float T = Say(TEXT("d_openup"), 0.9f);
			After(T - 0.35f, [this]()
			{
"""),
])

edit(ROOT + r"\Scripts\audio\gen_vo.py", [
    ("""    "d_shedcall": "Badly startled by a crash behind him outdoors at night: the name sharp and loud as he spins round, then after a held breath, quieter and unsure, 'Is that you?'",
""",
     """    "d_shedcall": "Scared out of his wits by a huge metal crash right behind him outdoors at night. The first two words are a shout that cracks, breath knocked out of him. 'Who's there' loud and shaking. 'Sheriff's department' barked, trying to get his voice under control, breathing hard. Then a long held breath, and the last two questions small, quiet and frightened.",
    "d_side": "At a front door in the dark. The first two words flat and matter-of-fact as he lets go of the handle. Then to himself, thinking aloud, unhurried.",
    "d_openup": "Calling through a closed front door, loud enough to carry into the house. Patient and concerned, but rattled: something just frightened him badly round the back and he is trying not to show it. The last sentence slower, a real request, almost pleading.",
"""),
])
print("pass 129 applied")
