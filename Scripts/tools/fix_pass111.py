"""Pass 111: sound on triggers, not on a track (Cheyenne 2026-11-19 16:42 UTC).
"There's still some kind of thump, big, door slamming or door opening ... on a repeat track every 5 to 10 seconds ... The only
thing that should be on a looping track is the horrific sounding music. Everything else should be on a timed sequence where
when the player passes this part, this sound goes off; picks this up, this sound triggers; returning to a room for the fifth
time, this sound triggers ... I like a moan ... a long, drawn out moan."  And: "the only thing I do like ... is the whispers."

FOUND: the repeating thump was the indoor "chimney wind" loop (amb_wind.wav): 15 bumps in its 42 seconds, looping whenever he
was inside (Scripts/audio/find_hits.py lists them).  It is gone.  The cellar loop had a loud drip every 18 s: replaced.

  - the wind loop is removed; the cellar bed is a clean synthesized one
  - the random house-noise timer is removed.  Every house sound is now one line in a table: an event (entering a room for the
    Nth time, taking a thing, opening a door), and the one sound it sets off, once.  At least 22 s between any two.
  - the old timed build-up (thump at 85 s, steps at 150 s, the rocking chair ...) is in the same table, on triggers
  - the whispers are kept as they were: seldom, on their own long timer
  - two long moans (m_moan1, m_moan2) are in the table (taking her glass eye; taking the padlock key)
  - the television's soundtrack is quieter, reaches less far, and no longer cuts hard when it comes round
  - -WCSndLog writes every one-shot to the log (WCSND) so a run can be audited"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

# ---------------------------------------------------------------- story: loops and the old timer
p = R + "Source/WellnessCheck/WCStory.cpp"
s = open(p, encoding="utf-8").read()
a = s.index("	// ---- the house is never silent: things in the walls, boards, wind, something moving on another floor")
b = s.index("	// he calls out to her while he looks round, three times, before he has seen anything")
s = s[:a] + "	// (the house's own noises are no longer on a timer: each is set off by something he does.  WCEvents.cpp, TickCues)\n" + s[b:]
old = '''	SetLoop(TEXT("wind"), (bIn || bCellar) ? TEXT("amb_wind") : TEXT(""), bIn ? 0.55f : 0.f, 5.f);'''
assert old in s
s = s.replace(old, '''	SetLoop(TEXT("wind"), TEXT(""), 0.f, 2.f);          // the chimney-wind loop had a bump in it every few seconds: gone''')
old = '''	{ TEXT("m_hum"), TEXT(""), TEXT("Mm mm mmm, mm mm mmm, mmm mm, mmm."), 2 },'''
assert old in s
s = s.replace(old, old + '''
	{ TEXT("m_moan1"), TEXT(""), TEXT("Ohhhhhhhhh... ohhhhhhh..."), 2 },
	{ TEXT("m_moan2"), TEXT(""), TEXT("Mmmmmmmmmhhhh... hhhhhnnnnn..."), 2 },''')
open(p, "w", encoding="utf-8", newline="\n").write(s)

edit(R + "Scripts/audio/gen_vo.py", [
    ('''    "m_hum": "No words: humming''', '''    "m_moan1": "No words at all: one long, low, drawn-out moan of grief from deep in the chest of a very old woman, slow, swelling a little and trailing away into a breath. Then a second, weaker one. Mournful and frightening.",
    "m_moan2": "No words at all: a long, low, closed-mouth moan that turns into a strained groan, slow and drawn out, as if in pain, ending in a shaky exhale.",
    "m_hum": "No words: humming'''),
])

# ---------------------------------------------------------------- the old timed build-up goes into the table
p = R + "Source/WellnessCheck/WCHouse.cpp"
s = open(p, encoding="utf-8").read()
a = s.index("	case 1: if (T > 85.f) { ++BuildStep;")
b = s.index("	default: break;", a)
s = s[:a] + "	case 1: BuildStep = 7; break;          // (the rest of the build-up is set off by what he does: WCEvents.cpp, GWCCues)\n" + s[b:]
open(p, "w", encoding="utf-8", newline="\n").write(s)

edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('void UpstairsThump();', '''void UpstairsThump();
	void CueEvent(FName Id);
	void TickCues(float Dt);
	TMap<FName, int32> CueCount;
	TSet<int32> CueFired;
	TSet<FName> TrigInside;
	double CueFreeAt = 0.0, WhisperAt = -1.0;'''),
])

# ---------------------------------------------------------------- director: route events, tick, log
edit(R + "Source/WellnessCheck/WCDirector.cpp", [
    ('''	UE_LOG(LogWC, Display, TEXT("WCEVENT t=%.1f %s"), PlaySeconds, *Id.ToString());''', '''	UE_LOG(LogWC, Display, TEXT("WCEVENT t=%.1f %s"), PlaySeconds, *Id.ToString());
	CueEvent(Id);'''),
    ('''		if (T.IsValid() && T->Contains(L)) StoryEvent(FName(*FString::Printf(TEXT("trig:%s"), *T->WCId.ToString())));
	}''', '''		if (!T.IsValid()) continue;
		const bool bIn = T->Contains(L);
		if (bIn) StoryEvent(FName(*FString::Printf(TEXT("trig:%s"), *T->WCId.ToString())));
		// coming into a room is an event of its own (the triggered sounds count them)
		if (bIn && !TrigInside.Contains(T->WCId)) { TrigInside.Add(T->WCId); CueEvent(FName(*FString::Printf(TEXT("enter:%s"), *T->WCId.ToString()))); }
		else if (!bIn) TrigInside.Remove(T->WCId);
	}
	TickCues(0.f);'''),
    ('''	USoundBase* S = Snd(Name);
	if (!S) return nullptr;
	UAudioComponent* A = UGameplayStatics::SpawnSound2D(''', '''	USoundBase* S = Snd(Name);
	if (!S) return nullptr;
	static const bool bSndLog = FParse::Param(FCommandLine::Get(), TEXT("WCSndLog"));
	if (bSndLog && Cat != EWCSnd::Music && Name != TEXT("ui_tick")) UE_LOG(LogWC, Display, TEXT("WCSND t=%.1f 2D %s vol %.2f"), PlaySeconds, *Name, Volume);
	UAudioComponent* A = UGameplayStatics::SpawnSound2D('''),
    ('''	USoundBase* S = Snd(Name);
	if (!S) return nullptr;
	if (!Atten)''', '''	USoundBase* S = Snd(Name);
	if (!S) return nullptr;
	static const bool bSndLogAt = FParse::Param(FCommandLine::Get(), TEXT("WCSndLog"));
	if (bSndLogAt && !Name.StartsWith(TEXT("step_"))) UE_LOG(LogWC, Display, TEXT("WCSND t=%.1f at %s vol %.2f, %.0f cm away"), PlaySeconds, *Name, Volume, Player() ? FVector::Dist(Player()->GetActorLocation(), Where) : -1.f);
	if (!Atten)'''),
])

# ---------------------------------------------------------------- the television's soundtrack
edit(R + "Source/WellnessCheck/WCEvents.cpp", [
    ('''			if (TVAudio.IsValid()) TVAudio->Stop();
			TVAudio = PlayAt(FString::Printf(TEXT("tv_tape_%d"), TVTapeNow), At, 1.5f, 1.f, 2000.f);''',
     '''			if (TVAudio.IsValid()) TVAudio->FadeOut(0.35f, 0.f);          // no hard cut when the tape comes round
			TVAudio = PlayAt(FString::Printf(TEXT("tv_tape_%d"), TVTapeNow), At, 0.42f, 1.f, 1000.f);       // heard in the room and from the hall, not through the house
			if (TVAudio.IsValid()) TVAudio->FadeIn(0.35f, 1.f);'''),
])

# ---------------------------------------------------------------- the table
p = R + "Source/WellnessCheck/WCEvents.cpp"
s = open(p, encoding="utf-8").read()
assert "GWCCues" not in s
s += r'''
// ================================================================================================ sounds on triggers
// Cheyenne: "Everything else should be on a timed sequence where when the player passes this part, this sound goes off ...
// picks this up, this sound triggers ... returning to a room for the fifth time, this sound triggers."
// One line = one sound, once.  On: the event ("enter:<trigger>" = walking into a room, "take:<item>", "use:<thing>",
// "door:<door>").  Nth: on which time that happens.  Where: 0 somewhere round him, 1 on the other floor, 2 in a wall close by,
// 3 behind him.  Need: a story flag that has to be set first (nullptr = none).  Act: 1 the rocking chair rocks, 2 a light he
// left on goes out, 3 Walter's radio tunes itself, 4 bare feet run across the other floor.
namespace
{
	struct FWCCue { const TCHAR* On; int32 Nth; const TCHAR* Sound; int32 Where; float Near, Far, Vol, Pitch; const TCHAR* Need; int32 Act; };
	const FWCCue GWCCues[] = {
		// ---- the house only: before the thump
		{ TEXT("enter:t_dining"), 1, TEXT("creak"), 0, 300.f, 600.f, 0.8f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_kitchen"), 1, TEXT("thump_far"), 1, 200.f, 400.f, 0.9f, 0.95f, nullptr, 0 },
		{ TEXT("use:vent"), 1, TEXT("skitter"), 2, 120.f, 220.f, 0.8f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_hall_mid"), 2, TEXT("steps_above"), 1, 100.f, 300.f, 0.9f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_living"), 2, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, nullptr, 1 },
		{ TEXT("enter:t_pantry"), 1, TEXT("skitter"), 2, 150.f, 300.f, 0.8f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_den"), 1, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, nullptr, 3 },
		{ TEXT("enter:t_sickroom"), 1, TEXT("VO/m_hum"), 1, 200.f, 500.f, 0.45f, 1.f, TEXT("locked_in"), 0 },
		{ TEXT("enter:t_up_landing"), 1, TEXT("house_groan"), 0, 500.f, 900.f, 0.9f, 1.f, nullptr, 0 },
		{ TEXT("take:screwdriver"), 1, TEXT("creak"), 3, 180.f, 260.f, 0.9f, 0.9f, nullptr, 0 },
		{ TEXT("enter:t_foyer"), 3, TEXT("door_far"), 1, 400.f, 700.f, 0.9f, 1.f, nullptr, 2 },
		{ TEXT("enter:t_kitchen"), 3, TEXT("scratch_wall"), 2, 150.f, 220.f, 0.9f, 1.f, nullptr, 0 },
		// ---- after the first sight of her
		{ TEXT("take:keep_eye"), 1, TEXT("VO/m_moan1"), 1, 500.f, 900.f, 0.75f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_up_corridor"), 3, TEXT("door_far"), 3, 500.f, 800.f, 0.8f, 1.f, TEXT("peek_done"), 0 },
		// ---- after the long hall
		{ TEXT("enter:t_hall_mid"), 5, TEXT("VO/m_cry1"), 1, 300.f, 700.f, 0.6f, 1.f, TEXT("lockin_done"), 0 },
		{ TEXT("enter:t_dining"), 3, TEXT("knock_far"), 0, 600.f, 1000.f, 0.9f, 1.f, TEXT("lockin_done"), 0 },
		{ TEXT("enter:t_master"), 3, TEXT("chair_creak"), 3, 200.f, 300.f, 0.8f, 1.f, TEXT("lockin_done"), 0 },
		{ TEXT("take:key_sitting"), 1, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, nullptr, 4 },
		{ TEXT("door:sitting"), 1, TEXT("VO/m_laugh1"), 2, 250.f, 400.f, 0.5f, 1.f, nullptr, 0 },
		{ TEXT("take:key_prayer"), 1, TEXT("thump_far"), 1, 200.f, 500.f, 0.9f, 1.f, nullptr, 0 },
		{ TEXT("take:fuse"), 1, TEXT("skitter"), 2, 150.f, 260.f, 0.8f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_living"), 4, TEXT("scratch_wall"), 2, 200.f, 320.f, 0.9f, 0.85f, TEXT("phone_done"), 0 },
		{ TEXT("enter:t_kitchen"), 5, TEXT("chair_scrape"), 3, 220.f, 320.f, 0.7f, 1.f, TEXT("phone_done"), 0 },
		{ TEXT("enter:t_sitting"), 2, TEXT("VO/m_hum"), 2, 300.f, 500.f, 0.45f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_up_landing"), 4, TEXT("VO/m_cry2"), 0, 500.f, 900.f, 0.55f, 1.f, TEXT("ceiling_done"), 0 },
		{ TEXT("enter:t_den"), 3, TEXT("knock_far"), 1, 300.f, 600.f, 0.9f, 1.f, nullptr, 0 },
		{ TEXT("take:key_ell"), 1, TEXT("VO/m_cry2"), 2, 300.f, 500.f, 0.55f, 1.f, nullptr, 0 },
		// ---- the back rooms upstairs, the attic, the cellar
		{ TEXT("door:up_ell"), 1, TEXT("house_groan"), 0, 500.f, 900.f, 0.9f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_aide"), 1, TEXT("VO/m_laugh2"), 1, 300.f, 600.f, 0.5f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_bath2"), 1, TEXT("skitter"), 2, 150.f, 260.f, 0.8f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_up_ell"), 3, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, nullptr, 4 },
		{ TEXT("enter:t_attic"), 1, TEXT("wind_gust"), 0, 600.f, 1000.f, 0.8f, 1.f, nullptr, 0 },
		{ TEXT("take:key_cellar"), 1, TEXT("VO/m_moan2"), 1, 400.f, 800.f, 0.75f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_foyer"), 6, TEXT("door_far"), 1, 500.f, 900.f, 0.9f, 0.9f, TEXT("attic_done"), 0 },
		{ TEXT("enter:t_backhall"), 3, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, TEXT("lockin_done"), 4 },
		{ TEXT("enter:t_pantry"), 2, TEXT("thump_far"), 1, 200.f, 500.f, 0.9f, 1.f, TEXT("lockin_done"), 0 },
		{ TEXT("enter:t_cellar_shelf"), 1, TEXT("scratch_wall"), 2, 150.f, 240.f, 0.9f, 0.9f, nullptr, 0 },
	};
}

void AWCDirector::CueEvent(FName Id)
{
	const FString S = Id.ToString();
	if (!(S.StartsWith(TEXT("enter:")) || S.StartsWith(TEXT("take:")) || S.StartsWith(TEXT("use:")) || S.StartsWith(TEXT("door:")))) return;
	CueCount.FindOrAdd(Id) += 1;
	AWCCharacter* P = Player();
	if (!P || !Has(TEXT("inside")) || Has(TEXT("dawn")) || Has(TEXT("placed"))) return;
	// nothing over a staged moment, a hunt, or another of these
	if (bBusy || bEventBusy || StalkState != 0 || Clock < CueFreeAt) return;
	const int32 Count = CueCount[Id];
	for (int32 i = 0; i < UE_ARRAY_COUNT(GWCCues); ++i)
	{
		const FWCCue& C = GWCCues[i];
		if (CueFired.Contains(i) || Id != FName(C.On) || Count < C.Nth) continue;
		if (C.Need && !Has(FName(C.Need))) continue;
		CueFired.Add(i);
		CueFreeAt = Clock + 22.0;
		const FVector L = P->GetActorLocation();
		const FRotator Yaw(0.f, P->GetControlRotation().Yaw, 0.f);
		FVector Off = FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * Rng.FRandRange(C.Near, C.Far);
		if (C.Where == 1) Off.Z = (L.Z > 500.f ? -1.f : 1.f) * 330.f;
		else if (C.Where == 2) Off.Z = Rng.FRandRange(-60.f, 120.f);
		else if (C.Where == 3) Off = -Yaw.Vector() * Rng.FRandRange(C.Near, C.Far) + FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y) * Rng.FRandRange(-90.f, 90.f) + FVector(0, 0, 20.f);
		else Off.Z = Rng.FRandRange(-80.f, 200.f);
		UE_LOG(LogWCEvents, Display, TEXT("WCCUE t=%.1f %s (%s, time %d) act %d"), PlaySeconds, C.Sound, C.On, Count, C.Act);
		// a moment after he has done the thing, not on top of it
		const FString Sound = C.Sound;
		const float Vol = C.Vol, Pitch = C.Pitch;
		const int32 Act = C.Act;
		After(Rng.FRandRange(0.9f, 2.2f), [this, Sound, Vol, Pitch, Act, L, Off]()
		{
			AWCCharacter* Pl = Player();
			if (!Pl || bBusy) return;
			if (!Sound.IsEmpty()) PlayAt(Sound, L + Off, Vol, Pitch * Rng.FRandRange(0.96f, 1.04f));
			if (Act == 1)
			{
				if (AActor* Chair = Find(TEXT("RockingChair")))
				{
					RockActor = Chair; RockUntil = Clock + 9.0; RockBase = Chair->GetActorRotation();
					PlayAt(TEXT("chair_creak"), Chair->GetActorLocation() + FVector(0, 0, 50), 1.f, 1.f, 2200.f);
					After(3.2f, [this, Chair]() { if (IsValid(Chair)) PlayAt(TEXT("chair_creak"), Chair->GetActorLocation() + FVector(0, 0, 50), 0.9f, 0.94f, 2200.f); });
				}
			}
			else if (Act == 2)
			{
				for (TPair<FName, FRoomLights>& Rm : Rooms) if (Rm.Value.bOn) { Rm.Value.KillAt = Clock; NextLightKill = 0.0; break; }
			}
			else if (Act == 3)
			{
				PlayAt(TEXT("radio_tune"), Pos(TEXT("RadioPoint")), 1.f, 1.f, 3200.f);
				After(8.f, [this]() { if (bBusy) return; Play2D(TEXT("breath_near"), 0.55f); if (AWCCharacter* Q = Player()) Q->FlickerLight(0.5f, 0.7f); });
			}
			else if (Act == 4)
			{
				const FVector From = Pl->GetActorLocation() + FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * Rng.FRandRange(500.f, 900.f) + FVector(0, 0, (Pl->GetActorLocation().Z > 300.f ? -330.f : 330.f) - 80.f);
				const FVector Step = FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * 72.f;
				const int32 N = Rng.RandRange(4, 6);
				for (int32 k = 0; k < N; ++k) After(k * 0.42f, [this, From, Step, k]() { PlayAt(TEXT("her_step"), From + Step * k, 0.9f, Rng.FRandRange(0.9f, 1.05f), 3400.f); });
			}
		});
		return;                              // one at a time
	}
}

void AWCDirector::TickCues(float Dt)
{
	// the whispers, as they were: seldom, hers, only once the door has locked behind him (Cheyenne: "I like the whisper")
	AWCCharacter* P = Player();
	if (!P || !Has(TEXT("locked_in")) || Has(TEXT("dawn")) || Has(TEXT("placed"))) return;
	if (WhisperAt < 0.0) WhisperAt = Clock + Rng.FRandRange(300.f, 600.f);
	if (Clock < WhisperAt || bBusy || bEventBusy || StalkState != 0 || Clock < CueFreeAt) return;
	WhisperAt = Clock + Rng.FRandRange(420.f, 840.f);
	CueFreeAt = Clock + 22.0;
	const float Pick = Rng.FRand();
	if (Pick < 0.6f)
	{
		const FVector Off = FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * Rng.FRandRange(400.f, 900.f) + FVector(0, 0, Rng.FRandRange(-80.f, 200.f));
		UE_LOG(LogWCEvents, Display, TEXT("WCCUE t=%.1f whisper_far (the whispers)"), PlaySeconds);
		PlayAt(TEXT("whisper_far"), P->GetActorLocation() + Off, 0.64f * Rng.FRandRange(0.75f, 1.f), Rng.FRandRange(0.92f, 1.07f));
	}
	else
	{
		// at his ear: just behind him, to one side.  He turns, and there is nothing there.
		static const TCHAR* Ear[3] = { TEXT("VO/m_ear1"), TEXT("VO/m_ear2"), TEXT("VO/m_ear3") };
		const FRotator Yaw(0.f, P->GetControlRotation().Yaw, 0.f);
		const FVector Off = -Yaw.Vector() * 28.f + FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y) * (Rng.FRand() < 0.5f ? -24.f : 24.f) + FVector(0, 0, 58.f);
		const int32 Which = Rng.RandRange(0, 2);
		UE_LOG(LogWCEvents, Display, TEXT("WCCUE t=%.1f %s (the whispers)"), PlaySeconds, Ear[Which]);
		PlayAt(Ear[Which], P->GetActorLocation() + Off, 0.4f * Rng.FRandRange(0.75f, 1.f), Rng.FRandRange(0.92f, 1.07f));
	}
}
'''
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("pass 111 applied")
