"""Cheyenne, 03:14 UTC, after watching a run:
 - scares further apart: every rest between scares is 1.6 times longer; hunts come 6 to 9 minutes apart and at most four in a
   game; the attic crawl and the cellar-door rush wait for a quiet stretch instead of firing the instant he opens the thing
   (if he is already down the cellar stairs when it would come, the door simply slams and locks above him);
 - Edith much darker;
 - the flashlight dimmer;
 - the ending is the first grey of morning, not sunshine."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
P = "C:/GameDev/Unreal/WellnessCheck/"
R = P + "Source/WellnessCheck/"

edit(R + "WCDirector.h", [
    ('''	void Rest(float Seconds) { NextScareAt = FMath::Max(NextScareAt, Clock + Seconds * TestPace); }''',
     '''	void Rest(float Seconds) { NextScareAt = FMath::Max(NextScareAt, Clock + Seconds * 1.6f * TestPace); }       // 1.6: she asked for them further apart
	/** Run Go at the next quiet stretch (now, if it is quiet). If Valid turns false first, run Skip instead. */
	void WhenQuiet(TFunction<void()> Go, TFunction<bool()> Valid, TFunction<void()> Skip, float MaxWait);
	struct FDeferred { TFunction<void()> Go; TFunction<bool()> Valid; TFunction<void()> Skip; double Deadline = 0.0; };
	TArray<FDeferred> Deferred;
	void CellarSprint();
	void CellarQuiet();
	void AtticCrawl();'''),
])
edit(R + "WCDirector.cpp", [
    ('''	Steps.Reset();''', '''	Steps.Reset();
	Deferred.Reset();'''),
])
edit(R + "WCCharacter.h", [
    ('''float FlashLumens = 1500.f;''', '''float FlashLumens = 980.f;'''),
])
edit(R + "WCHouse.cpp", [
    ('''	NextStalkAt = Clock + 120.0;''', '''	NextStalkAt = Clock + 300.0;'''),
    ('''			NextStalkAt = Clock + Rng.FRandRange(210.f, 320.f) * FMath::Max(TestPace, 0.3f);''', '''			NextStalkAt = Clock + Rng.FRandRange(360.f, 540.f) * FMath::Max(TestPace, 0.3f);'''),
    ('''	NextStalkAt = Clock + Rng.FRandRange(200.f, 330.f) * FMath::Max(TestPace, 0.3f);''', '''	NextStalkAt = Clock + Rng.FRandRange(360.f, 540.f) * FMath::Max(TestPace, 0.3f);'''),
    ('''&& Clock >= NextScareAt && Clock >= NextStalkAt && StalksDone < 6 &&''', '''&& Clock >= NextScareAt && Clock >= NextStalkAt && StalksDone < 4 &&'''),
    ('''	P->SetFaceLight(120.f);''', '''	P->SetFaceLight(85.f);'''),
])

p = R + "WCStory.cpp"
s = io.open(p, encoding="utf-8").read()

# ---- the attic: the crawl waits for a quiet stretch (at most 50 s, and only while he is still up there)
old = '''	After(T, [this]() { GiveItem(TEXT("key_cellar"), TEXT("Padlock key")); });
	After(T + 1.4f, [this]()
	{
		AWCEntity* H = Her();
		AWCCharacter* P = Player();
		if (!H || !P) { Set(TEXT("attic_done"));
						Rest(120.f); return; }
		PlayAt(TEXT("thump_heavy"), Pos(TEXT("Her_AtticFar")), 1.f);'''
new = '''	After(T, [this]() { GiveItem(TEXT("key_cellar"), TEXT("Padlock key")); });
	After(T + 1.4f, [this]()
	{
		const float AtticZ = Pos(TEXT("Her_AtticFar")).Z;
		WhenQuiet([this]() { AtticCrawl(); },
			[this, AtticZ]() { AWCCharacter* Pl = Player(); return Pl && Pl->GetActorLocation().Z > AtticZ - 40.f; },
			[this]() { Set(TEXT("attic_done")); Rest(60.f); SetObjective(TEXT("Unlock the cellar")); Checkpoint(TEXT("attic_done")); }, 50.f);
	});
}

void AWCDirector::AtticCrawl()
{
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S5_crawl"), PlaySeconds);
	{
		AWCEntity* H = Her();
		AWCCharacter* P = Player();
		if (!H || !P) { Set(TEXT("attic_done"));
						Rest(120.f); return; }
		PlayAt(TEXT("thump_heavy"), Pos(TEXT("Her_AtticFar")), 1.f);'''
assert old in s
s = s.replace(old, new)
# the old lambda closed with "\t});\n}" before the S6 header; the body is now a plain block inside AtticCrawl()
old = '''					});
				});
			});
		});
	});
}

// ---------------------------------------------------------------------------------------------- S6 the sprint down the'''
new = '''					});
				});
			});
		});
	}
}

// ---------------------------------------------------------------------------------------------- S6 the sprint down the'''
assert old in s
s = s.replace(old, new)

# ---- the cellar door
old = '''void AWCDirector::ScareCellarDoor()
{
	Set(TEXT("sprint_started"));
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S6_sprint"), PlaySeconds);
	float T = Say(TEXT("d_cellar_open"), 0.6f);
	After(T + 0.5f, [this]()
	{
		AWCEntity* H = Her();'''
new = '''void AWCDirector::ScareCellarDoor()
{
	Set(TEXT("sprint_started"));
	float T = Say(TEXT("d_cellar_open"), 0.6f);
	After(T + 0.5f, [this]()
	{
		// she comes when it has been quiet for a while; if he is already at the bottom by then, the door just shuts on him
		WhenQuiet([this]() { CellarSprint(); },
			[this]() { AWCCharacter* Pl = Player(); return Pl && Pl->GetActorLocation().Z > -230.f; },
			[this]() { CellarQuiet(); }, 150.f);
	});
}

void AWCDirector::CellarQuiet()
{
	if (Has(TEXT("sprint_done"))) return;
	UE_LOG(LogWCStory, Display, TEXT("WCEVENT t=%.1f cellar door shuts behind him (no rush)"), PlaySeconds);
	if (AWCDoor* D = Door(TEXT("cellar")))
	{
		D->Slam(); D->SetLocked(true); D->KeyId = NAME_None;
		PlayAt(TEXT("door_slam"), D->GetActorLocation() + FVector(0, 0, 110), 1.f, 0.9f, 3000.f);
	}
	if (AWCCharacter* Pl = Player()) { Pl->FlickerLight(1.4f, 0.8f); Pl->AddShake(0.4f); }
	Tension = 0.8f;
	Set(TEXT("sprint_done"));
	ApplyWorldState();
	After(1.6f, [this]() { Think(TEXT("The door. She shut it.")); });
	Say(TEXT("d_cellar"), 4.f);
	SetObjective(TEXT("Find her"));
	Checkpoint(TEXT("cellar"));
}

void AWCDirector::CellarSprint()
{
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S6_sprint"), PlaySeconds);
	{
		AWCEntity* H = Her();'''
assert old in s
s = s.replace(old, new)
old = '''		SprintStart = -1.0;
		bSprintActive = true;
		Tension = 1.f;
	});
}

// ---------------------------------------------------------------------------------------------- S8 finale'''
new = '''		SprintStart = -1.0;
		bSprintActive = true;
		Tension = 1.f;
	}
}

void AWCDirector::WhenQuiet(TFunction<void()> Go, TFunction<bool()> Valid, TFunction<void()> Skip, float MaxWait)
{
	if (Gate() && !bBusy) { Go(); return; }
	FDeferred D;
	D.Go = MoveTemp(Go); D.Valid = MoveTemp(Valid); D.Skip = MoveTemp(Skip);
	D.Deadline = Clock + MaxWait * FMath::Max(TestPace, 0.15f);
	Deferred.Add(MoveTemp(D));
}

// ---------------------------------------------------------------------------------------------- S8 finale'''
assert old in s
s = s.replace(old, new)
# tick the deferred scares
old = '''	if (Has(TEXT("kids_pending")) && !Has(TEXT("kids_open")) && Gate())'''
new = '''	for (int32 i = Deferred.Num() - 1; i >= 0; --i)
	{
		if (Deferred[i].Valid && !Deferred[i].Valid()) { FDeferred D = Deferred[i]; Deferred.RemoveAt(i); if (D.Skip) D.Skip(); }
		else if (!bBusy && (Gate() || Clock >= Deferred[i].Deadline)) { FDeferred D = Deferred[i]; Deferred.RemoveAt(i); if (D.Go) D.Go(); }
	}
	if (Has(TEXT("kids_pending")) && !Has(TEXT("kids_open")) && Gate())'''
assert old in s
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

edit(R + "WCAuto.cpp", [
    ('''Use(TEXT("cellar")); Flag(TEXT("sprint_started"), 10.f); WaitHer(12.f);''', '''Use(TEXT("cellar")); Flag(TEXT("sprint_started"), 10.f); WaitHer(40.f);'''),
])

# ---- Edith much darker; barely dawn
edit(P + "Scripts/level/import_assets.py", [
    ('''tint = vparam(m, "Tint", (0.50, 0.46, 0.41, 1), -700, -420)''', '''tint = vparam(m, "Tint", (0.21, 0.19, 0.17, 1), -700, -420)        # Cheyenne: "way darker"; was (0.50, 0.46, 0.41)'''),
])
edit(P + "Scripts/level/lighting.py", [
    ('''grade("Grade_Dawn", NIGHT_EV + 4.1, [          # was +5.5: the foyer and porch at dawn were burnt out to white
    ("vignette_intensity", 0.35), ("film_grain_intensity", 0.1), ("bloom_intensity", 0.5),
    ("color_saturation", unreal.Vector4(0.95, 0.93, 0.9, 1.0)), ("white_temp", 6000.0)]''',
     '''grade("Grade_Dawn", NIGHT_EV + 2.4, [          # the first grey before sunrise (Cheyenne: "barely breaking morning, not bright sun")
    ("vignette_intensity", 0.45), ("film_grain_intensity", 0.15), ("bloom_intensity", 0.3),
    ("color_saturation", unreal.Vector4(0.72, 0.74, 0.8, 1.0)), ("white_temp", 6900.0)]'''),
    ('''sc.set_intensity(700.0)
sc.set_light_color(unreal.LinearColor(1.0, 0.72, 0.5, 1.0))''', '''sc.set_intensity(170.0)
sc.set_light_color(unreal.LinearColor(0.78, 0.74, 0.84, 1.0))'''),
    ('''sc.set_editor_property("volumetric_scattering_intensity", 1.1)''', '''sc.set_editor_property("volumetric_scattering_intensity", 0.8)'''),
    ('''light_spot(name + "_dawn", x, y, z, yaw, pitch + 4, 42000, (1.0, 0.7, 0.45), 1100, 36, 62,''', '''light_spot(name + "_dawn", x, y, z, yaw, pitch + 4, 9000, (0.72, 0.76, 0.92), 1100, 36, 62,'''),
])
print("ok")
