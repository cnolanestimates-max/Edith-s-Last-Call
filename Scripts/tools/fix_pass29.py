"""Cheyenne 21:13: her scream opens the mouth (morph 'Scream'); encounters re-timed:
 S3: she comes quicker, he gets 2-3 shots, then she screams, runs and grabs.
 The next encounter is an ambush: round a corner at a dead run and on him.
 After that she hunts fast (unscripted): shots still stagger her and 3-4 drive her off.
Also the one lit window that dies when he knocks."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"

# ---------------------------------------------------------------- entity: scream morph
edit(R + "WCEntity.h", [
    ('''	/** Faint cold light on her face (lumens; 0 = off). */''', '''	/** 0..1: how far her jaw is unhinged.  Set automatically from the clip (Run, Lunge, Rise, Crawl scream). */
	void SetScream(float Amount) { ScreamTarget = FMath::Clamp(Amount, 0.f, 1.f); }
	/** Faint cold light on her face (lumens; 0 = off). */'''),
    ('''	bool bEyeReady = false;''', '''	bool bEyeReady = false;
	float ScreamTarget = 0.f;
	float ScreamAlpha = 0.f;'''),
])
edit(R + "WCEntity.cpp", [
    ('''	Super::Tick(Dt);
	if (!bShown) return;
''', '''Super::Tick(Dt);
	if (!bShown) return;
	if (!FMath::IsNearlyEqual(ScreamAlpha, ScreamTarget, 0.002f))
	{
		ScreamAlpha = FMath::FInterpConstantTo(ScreamAlpha, ScreamTarget, Dt, ScreamTarget > ScreamAlpha ? 7.f : 2.2f);
		Body->SetMorphTarget(TEXT("Scream"), ScreamAlpha);
	}
'''),
    ('''	Body->SetPlayRate(Rate);
}''', '''Body->SetPlayRate(Rate);
	// the mouth: wide open whenever she is coming for you
	static const TMap<FName, float> Mouths = { { TEXT("Run"), 1.f }, { TEXT("Lunge"), 1.f }, { TEXT("Rise"), 1.f }, { TEXT("Crawl"), 0.9f }, { TEXT("Under"), 0.35f } };
	const float* M = Mouths.Find(Anim);
	SetScream(M ? *M : 0.f);
}'''),
    ('''	EyeGlint->SetIntensity(0.f);
	Body->Stop();''', '''EyeGlint->SetIntensity(0.f);
	ScreamTarget = ScreamAlpha = 0.f;
	Body->SetMorphTarget(TEXT("Scream"), 0.f);
	Body->Stop();'''),
])

# ---------------------------------------------------------------- story: the lit window; S3 pacing
edit(R + "WCDirector.h", [('''	int32 ShotsAtHer = 0;''', '''	int32 ShotsAtHer = 0;
	int32 LockInShots = 0;''')])
edit(R + "WCStory.cpp", [
    ('''	ShowTagged(TEXT("Hide_shears"), !HasItem(TEXT("shears")));''', '''	ShowTagged(TEXT("Hide_shears"), !HasItem(TEXT("shears")));
	ShowTagged(TEXT("L_Welcome"), !Has(TEXT("knocked")));'''),
    ('''				float T = Say(TEXT("d_knock"), 0.9f);''', '''After(2.4f, [this]() { ShowTagged(TEXT("L_Welcome"), false); });      // the one lit window goes dark
				float T = Say(TEXT("d_knock"), 0.9f);'''),
    ('''	if (Is(Id, TEXT("shot_her"))) { ++ShotsAtHer; return; }''', '''	if (Is(Id, TEXT("shot_her"))) { ++ShotsAtHer; return; }
	if (Is(Id, TEXT("shot"))) { if (bLockInActive) ++LockInShots; return; }'''),
    ('''	ShotsAtHer = 0;
	Set(TEXT("power_out"));''', '''ShotsAtHer = 0;
	LockInShots = 0;
	Set(TEXT("power_out"));'''),
    ('''			if (!bLockInRun && (H->DistToPlayer() < LockInDist0 * 0.52f || Elapsed > 30.0 || H->DistToPlayer() < 600.f))''',
     '''if (!bLockInRun && (LockInShots >= 3 || H->DistToPlayer() < LockInDist0 * 0.5f || Elapsed > 9.0 || H->DistToPlayer() < 600.f))'''),
    ('''			H->MoveAlong(Pts, bLockInRun ? 660.f : 62.f, bLockInRun ? TEXT("Run") : TEXT("Walk"));''', '''H->MoveAlong(Pts, bLockInRun ? 780.f : 125.f, bLockInRun ? TEXT("Run") : TEXT("Walk"));'''),
    ('''				HerNextStep = Clock + 0.75;
				PlayAt(TEXT("her_flinch"), H->HeadLocation(), 1.f, 1.f, 3500.f);''', '''HerNextStep = Clock + 0.45;
				PlayAt(TEXT("her_flinch"), H->HeadLocation(), 1.f, 1.f, 3500.f);'''),
])

# ---------------------------------------------------------------- the hunt: an ambush first, then fast
edit(R + "WCHouse.cpp", [
    ('''			if (D < 850.f || D > 2400.f || N.X < 60.f) continue;        // never out in the yard''',
     '''const bool bAmbushPick = StalksDone == 0;
			if (D < (bAmbushPick ? 520.f : 1150.f) || D > (bAmbushPick ? 1300.f : 2700.f) || N.X < 60.f) continue;        // never out in the yard'''),
    ('''		StalkNeed = 4 + (Rng.FRand() < 0.45f ? 1 : 0);''', '''bAmbush = StalksDone == 0;                 // the first time after the long hall there is nothing he can do
		StalkNeed = bAmbush ? 99 : 3 + (Rng.FRand() < 0.45f ? 1 : 0);'''),
    ('''		if (!Has(TEXT("stalk_hint"))) { Set(TEXT("stalk_hint")); ShowHint(TEXT("Right Mouse: raise your pistol.  She cannot be killed. But she flinches from the shots."), 9.f); }''',
     '''if (bAmbush)
		{
			// round the corner at a dead run
			StalkState = 2;
			StalkRepath = 0.0;
			Play2D(TEXT("her_scream_short"), 1.f);
			Play2D(TEXT("sting_rise"), 0.9f, EWCSnd::Music);
		}
		else if (!Has(TEXT("stalk_hint"))) { Set(TEXT("stalk_hint")); ShowHint(TEXT("Right Mouse: raise your pistol.  She cannot be killed, but enough shots drive her off."), 9.f); }'''),
    ('''	if (StalkState == 1 && In > 2.6) { StalkState = 2; StalkRepath = 0.0; }''', '''	if (StalkState == 1 && In > 1.1) { StalkState = 2; StalkRepath = 0.0; Play2D(TEXT("her_scream_short"), 0.9f); }'''),
    ('''			const bool bClose = Dist < 330.f;
			H->MoveAlong(Route, bClose ? 560.f : FMath::Lerp(74.f, 112.f, FMath::Clamp((float)In / 45.f, 0.f, 1.f)), bClose ? TEXT("Run") : TEXT("Walk"));
			if (bClose && !Has(TEXT("stalk_rushing"))) { Set(TEXT("stalk_rushing")); Play2D(TEXT("her_scream_short"), 0.9f); }''',
     '''const bool bClose = Dist < 420.f;
			// she comes fast: quicker than he can run, and faster again for the last few steps
			H->MoveAlong(Route, bAmbush ? 700.f : (bClose ? 640.f : 400.f), TEXT("Run"));
			if (bClose && !Has(TEXT("stalk_rushing"))) { Set(TEXT("stalk_rushing")); Play2D(TEXT("her_scream"), 0.9f); }'''),
    ('''			++StalksDone; ++Catches;''', '''++StalksDone;
			if (!bAmbush) ++Catches;'''),
    ('''	const FVector Away = (H->GetActorLocation() - P->GetActorLocation()).GetSafeNormal2D();
	H->Slide(H->GetActorLocation() + Away * 70.f, 0.18f);
	H->Play(TEXT("Idle"));
	P->FlickerLight(0.25f, 0.8f);
	StalkPauseUntil = Clock + 1.1;''', '''const FVector Away = (H->GetActorLocation() - P->GetActorLocation()).GetSafeNormal2D();
	H->Slide(H->GetActorLocation() + Away * (bAmbush ? 30.f : 150.f), 0.16f);
	H->Play(TEXT("Idle"));
	P->FlickerLight(0.25f, 0.8f);
	StalkPauseUntil = Clock + (bAmbush ? 0.2 : 0.85);'''),
    ('''				After(3.2f, [this]() { FadeTo(0.f, 1.8f); Think(Catches == 1 ? TEXT("She had me. She let go.") : TEXT("Not again. Next time she keeps me.")); });''',
     '''After(3.2f, [this]() { FadeTo(0.f, 1.8f); Think(Catches <= 1 ? TEXT("She had me. She let go.") : TEXT("Not again. Next time she keeps me.")); });'''),
])
edit(R + "WCDirector.h", [('''	int32 StalkHits = 0, StalkNeed = 4, StalksDone = 0, Catches = 0;''', '''	int32 StalkHits = 0, StalkNeed = 4, StalksDone = 0, Catches = 0;
	bool bAmbush = false;''')])
edit(L + "lighting.py", [('''tags=["Flicker", "L_Welcome", "Hide_dawn"], shadows=True, vol=1.6, source=3.0)''', '''tags=["Flicker", "L_Welcome"], shadows=True, vol=1.6, source=3.0)''')])
print("ok")
