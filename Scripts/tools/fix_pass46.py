"""Cheyenne 22:44-22:50:
 - her face moves (jaw when she speaks or breathes, brow, a sneer that twitches) using three shape keys;
 - her heavy, wet, creaking footsteps are the warning that she is coming; hunts start far off at a stride, then rush;
 - the under-the-bed lunge is gone: her long arm comes slowly out from under Ruth's bed, takes the music box and draws it under
   (the view is held on it); he has to crouch and get it back.  It comes two quiet minutes after the hallway, not on top of it;
 - the boards creak more under his own feet."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"

# ---------------------------------------------------------------- entity: face, footsteps
edit(R + "WCEntity.h", [
    ('''	float ScreamTarget = 0.f;
	float ScreamAlpha = 0.f;''', '''	float ScreamTarget = 0.f;
	float ScreamAlpha = 0.f;
	float FaceT = 0.f, TalkLeft = 0.f, NextTwitch = 2.f, TwitchLeft = 0.f, StepAcc = 0.f;
public:
	/** Her mouth works for this long (she is speaking). */
	void Talk(float Seconds) { TalkLeft = FMath::Max(TalkLeft, Seconds); }
private:'''),
])
edit(R + "WCEntity.cpp", [
    ('''#include "WCCharacter.h"''', '''#include "WCCharacter.h"
#include "WCDirector.h"'''),
    ('''	if (!FMath::IsNearlyEqual(ScreamAlpha, ScreamTarget, 0.002f))
	{
		ScreamAlpha = FMath::FInterpConstantTo(ScreamAlpha, ScreamTarget, Dt, ScreamTarget > ScreamAlpha ? 7.f : 2.2f);
		Body->SetMorphTarget(TEXT("Scream"), ScreamAlpha);
	}''', '''	{
		// her face is never still: the jaw works when she speaks and hangs a little when she breathes, the brow
		// creeps, and one side of her mouth twitches up off the teeth
		ScreamAlpha = FMath::FInterpConstantTo(ScreamAlpha, ScreamTarget, Dt, ScreamTarget > ScreamAlpha ? 7.f : 2.2f);
		FaceT += Dt;
		TalkLeft = FMath::Max(0.f, TalkLeft - Dt);
		TwitchLeft = FMath::Max(0.f, TwitchLeft - Dt);
		if (FaceT > NextTwitch) { TwitchLeft = FMath::FRandRange(0.12f, 0.3f); NextTwitch = FaceT + FMath::FRandRange(1.2f, 5.5f); }
		float Jaw = 0.03f + 0.03f * FMath::Sin(FaceT * 1.4f);
		if (TalkLeft > 0.f) Jaw = 0.10f + 0.24f * FMath::Abs(FMath::Sin(FaceT * 17.f) * 0.6f + FMath::Sin(FaceT * 29.f + 1.f) * 0.4f);
		Jaw = FMath::Max(Jaw, ScreamAlpha);
		const float Sneer = TwitchLeft > 0.f ? 1.f : 0.18f + 0.16f * FMath::Sin(FaceT * 0.7f + 2.f) + 0.5f * ScreamAlpha;
		const float Brow = FMath::Clamp(0.35f + 0.35f * FMath::Sin(FaceT * 0.45f) + 0.6f * ScreamAlpha + (TwitchLeft > 0.f ? 0.3f : 0.f), 0.f, 1.f);
		Body->SetMorphTarget(TEXT("Scream"), Jaw);
		Body->SetMorphTarget(TEXT("Sneer"), FMath::Clamp(Sneer, 0.f, 1.f));
		Body->SetMorphTarget(TEXT("Brow"), Brow);
	}'''),
    ('''		SetActorLocation(Loc);
		if (PathIndex >= Path.Num())''', '''		// her feet: bare, heavy, wet on old boards.  You hear her before you see her.
		StepAcc += MoveSpeed * Dt;
		const float Stride = FMath::Clamp(MoveSpeed * 0.42f, 62.f, 175.f);
		if (StepAcc >= Stride)
		{
			StepAcc = 0.f;
			if (AWCDirector* D = AWCDirector::Get(this))
			{
				D->PlayAt(TEXT("her_step"), Loc + FVector(0, 0, 10), 1.f, FMath::FRandRange(0.9f, 1.08f), 3400.f);
				if (FMath::FRand() < 0.55f) D->PlayAt(TEXT("creak"), Loc, 0.6f, FMath::FRandRange(0.8f, 1.0f), 2600.f);
			}
		}
		SetActorLocation(Loc);
		if (PathIndex >= Path.Num())'''),
])
edit(R + "WCDirector.cpp", [
    ('''	if (Surface == TEXT("Wood") && Rng.FRand() < 0.14f) PlayAt(TEXT("creak"), Feet, 0.5f * Loud, Rng.FRandRange(0.85f, 1.1f));''',
     '''	if ((Surface == TEXT("Wood") || Surface == TEXT("Stairs")) && Rng.FRand() < 0.34f) PlayAt(TEXT("creak"), Feet, 0.55f * Loud, Rng.FRandRange(0.85f, 1.15f));'''),
])

# ---------------------------------------------------------------- story
edit(R + "WCDirector.h", [
    ('''	double GrabHoldUntil = 0.0;''', '''	double GrabHoldUntil = 0.0;
	FVector LookAtPoint = FVector::ZeroVector;
	double LookAtUntil = 0.0;'''),
])
edit(R + "WCStory.cpp", [
    # she speaks: her mouth moves
    ('''			if (USoundBase* S = Snd(Asset)) UGameplayStatics::SpawnSoundAtLocation(this, S, Her()->HeadLocation(), FRotator::ZeroRotator, FMath::Max(Vol(EWCSnd::Voice) * 1.2f, 0.0001f), 1.f, 0.f, Atten);''',
     '''			if (USoundBase* S = Snd(Asset)) UGameplayStatics::SpawnSoundAtLocation(this, S, Her()->HeadLocation(), FRotator::ZeroRotator, FMath::Max(Vol(EWCSnd::Voice) * 1.2f, 0.0001f), 1.f, 0.f, Atten);
			Her()->Talk(Len);'''),
    # after the hallway: nothing for two minutes, then Ruth's door
    ('''				After(T + 1.f, [this]()
				{
					if (AWCDoor* D = Door(TEXT("up_kids"))) { D->SetLocked(false); D->SetOpen(true, 4.5f, true); PlayAt(TEXT("door_creak_long"), D->GetActorLocation() + FVector(0, 0, 110), 1.f); }
					PlayAt(TEXT("musicbox"), Pos(TEXT("MusicBoxPoint")), 1.f);
					SetObjective(TEXT("Find what was theirs"));
					Checkpoint(TEXT("ceiling_done"));
				});''', '''				After(T + 1.f, [this]() { Set(TEXT("kids_pending")); SetObjective(TEXT("Find what was theirs")); Checkpoint(TEXT("ceiling_done")); });'''),
    ('''	if (Is(Id, TEXT("take:keep_ruth"))) { ScareUnderBed(); return; }''', '''	if (Is(Id, TEXT("take:keep_ruth"))) { Think(TEXT("Ruth's. Her name is scratched in the bottom.")); Checkpoint(TEXT("underbed")); return; }
	if (Is(Id, TEXT("trig:t_kids")) && Has(TEXT("kids_open")) && !Has(TEXT("underbed_done")) && Gate()) { ScareUnderBed(); return; }'''),
    ('''	if (Has(TEXT("backdoor_tried")) && !Has(TEXT("phone_ringing"))''', '''	if (Has(TEXT("kids_pending")) && !Has(TEXT("kids_open")) && Gate())
	{
		// a quiet while after the hallway, a door that was locked creaks open and a music box starts
		Set(TEXT("kids_open"));
		if (AWCDoor* D = Door(TEXT("up_kids"))) { D->SetLocked(false); D->SetOpen(true, 4.5f, true); PlayAt(TEXT("door_creak_long"), D->GetActorLocation() + FVector(0, 0, 110), 1.f); }
		PlayAt(TEXT("musicbox"), Pos(TEXT("MusicBoxPoint")), 1.f);
	}
	if (Has(TEXT("backdoor_tried")) && !Has(TEXT("phone_ringing"))'''),
    # ambience: sometimes it is simply her, walking somewhere, and stopping
    ('''		PlayAt(Chosen->Name, P->GetActorLocation() + Off, Chosen->Vol * Rng.FRandRange(0.75f, 1.f), Rng.FRandRange(0.92f, 1.07f));''',
     '''		if (Has(TEXT("locked_in")) && Rng.FRand() < 0.13f + 0.1f * Tension)
		{
			const FVector From = P->GetActorLocation() + FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * Rng.FRandRange(700.f, 1300.f) + FVector(0, 0, (Rng.FRand() < 0.5f ? 0.f : (P->GetActorLocation().Z > 300.f ? -330.f : 330.f)) - 80.f);
			const FVector Step = FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * 72.f;
			const int32 N = Rng.RandRange(3, 6);
			for (int32 k = 0; k < N; ++k) After(k * 0.62f, [this, From, Step, k]() { PlayAt(TEXT("her_step"), From + Step * k, 0.9f, Rng.FRandRange(0.9f, 1.05f), 3400.f); if (k % 2 == 0) PlayAt(TEXT("creak"), From + Step * k, 0.5f, 0.85f, 2600.f); });
		}
		else PlayAt(Chosen->Name, P->GetActorLocation() + Off, Chosen->Vol * Rng.FRandRange(0.75f, 1.f), Rng.FRandRange(0.92f, 1.07f));'''),
])
# the new S7: replace the whole function
p = R + "WCStory.cpp"
s = io.open(p, encoding="utf-8").read()
a = s.index("// ---------------------------------------------------------------------------------------------- S7 under the bed")
b = s.index("// ---------------------------------------------------------------------------------------------- S5 the attic")
s = s[:a] + '''// ---------------------------------------------------------------------------------------------- S7 the hand under the bed
// Slow.  He comes into Ruth's room and sees the music box on the floor; the view is held on it; her arm comes out from under the
// bed, closes on the box and draws it back under.  She is never seen.  Then he has to get down and take it back.
void AWCDirector::ScareUnderBed()
{
	if (Has(TEXT("underbed_done"))) return;
	Set(TEXT("underbed_done"));
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S7_hand"), PlaySeconds);
	for (TObjectIterator<UAudioComponent> It; It; ++It) if (It->GetWorld() == GetWorld() && It->Sound && It->Sound->GetName().Contains(TEXT("musicbox"))) It->FadeOut(2.5f, 0.f);
	AWCEntity* H = Her();
	AWCCharacter* P = Player();
	AWCInteractable* Box = Thing(TEXT("pick_keep_ruth"));
	if (!H || !P || !Box) return;
	bBusy = true;
	P->SetInputLocked(true);
	const FVector BoxFrom = Box->GetActorLocation();
	const FVector Under = Pos(TEXT("Her_Under"));
	const FVector Dir = (BoxFrom - Under).GetSafeNormal2D();
	const float Reach = 150.f;                                   // from her shoulders to her fingertips, lying flat
	const FVector Hidden = BoxFrom - Dir * (Reach + 190.f), AtBox = BoxFrom - Dir * (Reach + 6.f);
	LookAtPoint = BoxFrom + FVector(0, 0, 6);
	LookAtUntil = Clock + 9.6;
	Box->bEnabled = false;
	H->Appear(FVector(Hidden.X, Hidden.Y, Under.Z), Dir.Rotation().Yaw, TEXT("Under"), true, 0.5f);
	H->SetGlow(0.f);
	Tension = 0.8f;
	SetLoop(TEXT("amb"), TEXT("amb_house"), 0.1f, 1.5f);
	After(1.6f, [this, AtBox, Under]()
	{
		if (AWCEntity* E = Her()) { E->Slide(FVector(AtBox.X, AtBox.Y, Under.Z), 3.4f); PlayAt(TEXT("scratch_wall"), E->GetActorLocation(), 0.8f, 0.7f, 1500.f); }
		Play2D(TEXT("sting_low"), 0.6f, EWCSnd::Music);
	});
	After(5.3f, [this, Box, BoxFrom, Hidden, Under, Dir]()
	{
		// the fingers close; the box goes with them
		PlayAt(TEXT("pickup"), BoxFrom, 0.9f, 0.7f, 1200.f);
		if (AWCEntity* E = Her()) E->Slide(FVector(Hidden.X, Hidden.Y, Under.Z), 3.0f);
		const FVector To = BoxFrom - Dir * 128.f;
		for (int32 i = 1; i <= 60; ++i) After(i * 0.05f, [Box, BoxFrom, To, i]() { if (IsValid(Box)) Box->SetActorLocation(FMath::Lerp(BoxFrom, To, FMath::InterpEaseInOut(0.f, 1.f, i / 60.f, 2.f))); });
		PlayAt(TEXT("drag_floor"), BoxFrom, 0.5f, 1.3f, 1200.f);
	});
	After(9.4f, [this, Box]()
	{
		if (AWCEntity* E = Her()) E->Vanish();
		if (IsValid(Box)) Box->bEnabled = true;
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		bBusy = false;
		LookAtUntil = 0.0;
		Rest(140.f);
		ApplyWorldState();
		Think(TEXT("...It took it. It's under the bed."));
		ShowHint(TEXT("C: crouch"), 6.f);
		Checkpoint(TEXT("hand"));
	});
}

''' + s[b:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

edit(R + "WCHouse.cpp", [
    # the held look
    ('''	if (Clock < GrabHoldUntil && Her() && Her()->IsShown())''', '''	if (Clock < LookAtUntil)
	{
		if (AWCCharacter* Pl = Player())
		{
			if (AController* Ct = Pl->GetController())
			{
				const FRotator Want = (LookAtPoint - Pl->EyeLocation()).Rotation();
				Ct->SetControlRotation(FMath::RInterpTo(Ct->GetControlRotation(), FRotator(Want.Pitch, Want.Yaw, 0.f), Dt, 3.2f));
			}
		}
	}
	if (Clock < GrabHoldUntil && Her() && Her()->IsShown())'''),
    # hunts: you hear her coming at a stride from far off; the rush is for the last few metres
    ('''H->MoveAlong(Route, bAmbush ? 1350.f : (bClose ? 1150.f : 520.f), TEXT("Run"));''', '''if (bAmbush || bClose) H->MoveAlong(Route, bAmbush ? 1350.f : 1150.f, TEXT("Run"));
			else H->MoveAlong(Route, 250.f, TEXT("Walk"));'''),
    ('''			const bool bAmbushPick = StalksDone == 0;
			if (D < (bAmbushPick ? 520.f : 1150.f)''', '''			const bool bAmbushPick = StalksDone == 0;
			if (D < (bAmbushPick ? 520.f : 1500.f)'''),
])
edit(L + "build_house.py", [('''point("Her_Under", 640, -430, UZ, 90)''', '''point("Her_Under", 600, -480, UZ, 90)''')])
# bot: the new S7
edit(R + "WCAuto.cpp", [
    ('''	Go(TEXT("A_Kids")); Wait(3.f); Shot(TEXT("19_kids")); Use(TEXT("pick_keep_ruth")); Wait(1.5f); LookHer(0.4f); Shot(TEXT("20_S7_underbed")); Wait(8.f);''',
     '''	Flag(TEXT("kids_open"), 20.f * Slow); Go(TEXT("A_Kids")); Flag(TEXT("underbed_done"), 30.f); Wait(4.6f); Shot(TEXT("19_S7_hand_out")); Wait(2.6f); Shot(TEXT("20_S7_hand_takes")); Wait(4.f);
	AutoSteps.Add({ A_Crouch, NAME_None, 1.f }); Use(TEXT("pick_keep_ruth")); AutoSteps.Add({ A_Crouch, NAME_None, 0.f }); Wait(1.f);'''),
])
print("ok")
