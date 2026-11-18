"""Cheyenne 21:56-22:04:
 - every grab after the first comes at about twice the speed, and the picture stays on her screaming face a second longer;
 - the bot un-pauses itself (she watches the runs and touches the keyboard);
 - the thing Edith asked in: a tall black silhouette (watcher kind 2) that is simply standing there, and is gone when you look."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"

# ---------------------------------------------------------------- Grab(): hold on her face, then the fall
edit(R + "WCDirector.h", [
    ('''	void ScareBook();''', '''	void ScareBook();
	/** She has him: she screams in his face for Hold seconds (the view is pulled to her), then Then() runs. */
	void Grab(float Hold, TFunction<void()> Then);
	double GrabHoldUntil = 0.0;'''),
])
p = R + "WCHouse.cpp"
s = io.open(p, encoding="utf-8").read()
s = s.rstrip() + '''

// ================================================================================================ the grab
void AWCDirector::Grab(float Hold, TFunction<void()> Then)
{
	AWCEntity* H = Her();
	AWCCharacter* P = Player();
	if (!H || !P) { if (Then) Then(); return; }
	bBusy = true;
	H->StopMoving();
	// right in front of him, whatever angle she arrived from
	const FVector Fwd = FRotator(0.f, P->GetControlRotation().Yaw, 0.f).Vector();
	const FVector Feet = P->GetActorLocation() - FVector(0, 0, 88.f);
	const FVector To = (H->GetActorLocation() - Feet).GetSafeNormal2D();
	const FVector Dir = (FVector::DotProduct(To, Fwd) > 0.2f ? To : Fwd);
	H->SetActorLocation(Feet + Dir * 118.f);
	H->SetYaw((-Dir).Rotation().Yaw);
	H->FacePlayer(true);
	H->Play(TEXT("Lunge"), false);
	H->SetScream(1.f);
	H->SetGlow(2.2f);
	Play2D(TEXT("her_scream"), 1.f);
	Play2D(TEXT("sting_hit"), 1.f, EWCSnd::Music);
	P->AddShake(1.f);
	P->SetLightScale(1.f);
	P->FlickerLight(Hold, 0.45f);
	P->SetInputLocked(true);
	GrabHoldUntil = Clock + Hold;
	After(Hold, [this, Then]()
	{
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		if (Then) Then();
	});
}
'''
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
edit(R + "WCHouse.cpp", [
    # the view is dragged to her face while she has him
    ('''	if (bDriving) { TickDrive(Dt); return; }''', '''	if (bDriving) { TickDrive(Dt); return; }
	if (Clock < GrabHoldUntil && Her() && Her()->IsShown())
	{
		if (AWCCharacter* Pl = Player())
		{
			if (AController* Ct = Pl->GetController())
			{
				const FRotator Want = (Her()->HeadLocation() - FVector(0, 0, 14.f) - Pl->EyeLocation()).Rotation();
				Ct->SetControlRotation(FMath::RInterpTo(Ct->GetControlRotation(), FRotator(Want.Pitch, Want.Yaw, 0.f), Dt, 14.f));
			}
		}
	}'''),
    # hunts: faster
    ('''			H->MoveAlong(Route, bAmbush ? 700.f : (bClose ? 640.f : 400.f), TEXT("Run"));''', '''H->MoveAlong(Route, bAmbush ? 1350.f : (bClose ? 1150.f : 520.f), TEXT("Run"));'''),
    ('''			H->StopMoving();
			H->Play(TEXT("Lunge"), false);
			Play2D(TEXT("her_scream"), 1.f);
			Play2D(TEXT("sting_hit"), 1.f, EWCSnd::Music);
			SetLoop(TEXT("music"), TEXT(""), 0.f, 1.5f, EWCSnd::Music);
			P->AddShake(1.f);
			UE_LOG(LogWCHouse, Display, TEXT("WCSTALK t=%.1f caught (%d)"), PlaySeconds, Catches);
			After(0.28f, [this]() { if (AWCCharacter* Pl = Player()) Pl->Knockdown(3.4f); FadeTo(1.f, 0.35f); });
			After(1.0f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); });''', '''SetLoop(TEXT("music"), TEXT(""), 0.f, 1.5f, EWCSnd::Music);
			UE_LOG(LogWCHouse, Display, TEXT("WCSTALK t=%.1f caught (%d)"), PlaySeconds, Catches);
			Grab(1.35f, [this]() { if (AWCCharacter* Pl = Player()) Pl->Knockdown(3.4f); FadeTo(1.f, 0.3f); After(0.7f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); }); });'''),
    ('''				After(1.6f, [this]() { BigText = TEXT("You stayed."); BigSub = TEXT(""); BigTarget = 1.f; });
				After(6.f, [this]() { RestartFromCheckpoint(); });''', '''After(3.0f, [this]() { BigText = TEXT("You stayed."); BigSub = TEXT(""); BigTarget = 1.f; });
				After(7.4f, [this]() { RestartFromCheckpoint(); });'''),
    ('''				After(3.2f, [this]() { FadeTo(0.f, 1.8f); Think(Catches <= 1''', '''After(4.6f, [this]() { FadeTo(0.f, 1.8f); Think(Catches <= 1'''),
])
edit(R + "WCStory.cpp", [
    # S3: the long hall (the one slow-ish encounter): the run at the end is quicker, and she holds him
    ('''H->MoveAlong(Pts, bLockInRun ? 780.f : 125.f, bLockInRun ? TEXT("Run") : TEXT("Walk"));''', '''H->MoveAlong(Pts, bLockInRun ? 1000.f : 125.f, bLockInRun ? TEXT("Run") : TEXT("Walk"));'''),
    ('''			bLockInActive = false;
			bBusy = true;
			if (!bLockInRun) Play2D(TEXT("her_scream"), 1.f);
			Play2D(TEXT("sting_hit"), 1.f, EWCSnd::Music);
			H->StopMoving();
			H->Play(TEXT("Lunge"), false);
			P->AddShake(1.f);
			After(0.28f, [this]() { if (AWCCharacter* Pl = Player()) Pl->Knockdown(3.0f); FadeTo(1.f, 0.35f); });
			After(1.0f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); });
			After(3.0f, [this]() { FadeTo(0.f, 1.6f); });''', '''bLockInActive = false;
			Grab(1.3f, [this]()
			{
				if (AWCCharacter* Pl = Player()) Pl->Knockdown(3.0f);
				FadeTo(1.f, 0.3f);
				After(0.7f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); });
				After(2.8f, [this]() { FadeTo(0.f, 1.6f); });
			});'''),
    # S4 / S6: the sprints
    ('''			H->MoveAlong(Pts, 640.f, TEXT("Run"));
		}
	}''', '''H->MoveAlong(Pts, 1250.f, TEXT("Run"));
		}
	}'''),
    ('''		SprintStart = -1.0;
		bSprintActive = false;
		bBusy = true;
		H->StopMoving();
		Play2D(TEXT("sting_hit"), 1.f, EWCSnd::Music);
		P->AddShake(1.f);
		const bool bCellar = Has(TEXT("sprint_started")) && !Has(TEXT("sprint_done"));
		P->Knockdown(bCellar ? 3.6f : 3.0f);
		FadeTo(1.f, 0.3f);
		After(0.7f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); if (AWCCharacter* Pl = Player()) Pl->SetLightScale(1.f); });
		if (bCellar)
		{
			After(1.2f, [this]()
			{
				if (AWCCharacter* Pl = Player()) Pl->Relocate(Pos(TEXT("P_CellarBottom")), YawOf(TEXT("P_CellarBottom")));
				Play2D(TEXT("body_fall"), 1.f);
				if (AWCDoor* D = Door(TEXT("cellar"))) { D->Slam(); D->SetLocked(true); D->KeyId = NAME_None; }
			});
		}
		After(3.2f, [this]() { FadeTo(0.f, 1.8f); });''', '''SprintStart = -1.0;
		bSprintActive = false;
		const bool bCellar = Has(TEXT("sprint_started")) && !Has(TEXT("sprint_done"));
		Grab(1.25f, [this, bCellar]()
		{
			if (AWCCharacter* Pl = Player()) Pl->Knockdown(bCellar ? 3.6f : 3.0f);
			FadeTo(1.f, 0.3f);
			After(0.7f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); if (AWCCharacter* Pl = Player()) Pl->SetLightScale(1.f); });
			if (bCellar)
			{
				After(1.2f, [this]()
				{
					if (AWCCharacter* Pl = Player()) Pl->Relocate(Pos(TEXT("P_CellarBottom")), YawOf(TEXT("P_CellarBottom")));
					Play2D(TEXT("body_fall"), 1.f);
					if (AWCDoor* D = Door(TEXT("cellar"))) { D->Slam(); D->SetLocked(true); D->KeyId = NAME_None; }
				});
			}
			After(3.2f, [this]() { FadeTo(0.f, 1.8f); });
		});'''),
    ('''			E->MoveAlong(Pts, 640.f, TEXT("Run"));
			Pl->SetLightScale(0.55f);''', '''E->MoveAlong(Pts, 1250.f, TEXT("Run"));
			Pl->SetLightScale(0.55f);'''),
    ('''		H->MoveAlong(Pts, 600.f, TEXT("Run"));
		P->FlickerLight(1.6f, 0.8f);''', '''H->MoveAlong(Pts, 1200.f, TEXT("Run"));
		P->FlickerLight(1.6f, 0.8f);'''),
    # S2: from the kitchen table, fast, and into his face
    ('''						E2->MoveAlong(Pts, 620.f, TEXT("Run"), [this]()
						{
							if (AWCCharacter* Q3 = Player()) { Q3->AddShake(1.f); Q3->SetLightScale(0.f); }
							if (AWCEntity* E3 = Her()) E3->Vanish();
							After(0.9f, [this]()
							{''', '''E2->MoveAlong(Pts, 1300.f, TEXT("Run"), [this]()
						{
							Grab(1.3f, [this]()
							{
							if (AWCCharacter* Q3 = Player()) { Q3->AddShake(1.f); Q3->SetLightScale(0.f); }
							if (AWCEntity* E3 = Her()) E3->Vanish();
							After(0.9f, [this]()
							{'''),
    ('''								After(T2, [this]() { SetObjective(TEXT("Search the kitchen")); Checkpoint(TEXT("phone_done")); });
								Tension = 0.55f;
							});
						});''', '''After(T2, [this]() { SetObjective(TEXT("Search the kitchen")); Checkpoint(TEXT("phone_done")); });
								Tension = 0.55f;
							});
							});
						});'''),
    # S5: the crawl
    ('''			E->MoveAlong(Pts, 430.f, TEXT("Crawl"), [this]()''', '''E->MoveAlong(Pts, 860.f, TEXT("Crawl"), [this]()'''),
    # the finale's last rush
    ('''		H->MoveAlong(Pts, 380.f, TEXT("Run"), [this]()''', '''H->MoveAlong(Pts, 760.f, TEXT("Run"), [this]()'''),
    ('''	H->MoveAlong(Pts, 560.f, TEXT("Run"), [this]()''', '''H->MoveAlong(Pts, 1100.f, TEXT("Run"), [this]()'''),
])
# S2: the script's own stop point is the player's position; stop short so Grab can place her
# ---------------------------------------------------------------- bot survives a pause
edit(R + "WCGame.cpp", [
    ('''	if (D->Mode == EWCMode::Playing && bEsc)
	{''', '''	if (D->bAuto && Screen == EWCScreen::Pause && RealNow - ScreenOpenedAt > 10.0)
	{
		// a test run was paused (somebody touched the keyboard): carry on by itself
		Open(EWCScreen::None);
		SetPaused(false);
	}
	if (D->Mode == EWCMode::Playing && bEsc)
	{'''),
])

# ---------------------------------------------------------------- watcher kind 2: the Company, a black shape standing in the dark
edit(R + "WCWorld.cpp", [
    ('''#include "Engine/StaticMesh.h"''', '''#include "Engine/StaticMesh.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimSequence.h"'''),
    ('''	if (Kind == 0)
	{
		if (UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")))''', '''if (Kind == 2)
	{
		// the thing she asked in: her own outline, drawn longer and thinner, with no light on it at all
		USkeletalMesh* SK = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/WC/Her/SK_Her.SK_Her"));
		UAnimSequence* Pose = LoadObject<UAnimSequence>(nullptr, TEXT("/Game/WC/Her/A_Her_Tall.A_Her_Tall"));
		UMaterialInterface* Void = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Void.M_Void"));
		if (SK)
		{
			USkeletalMeshComponent* C = NewObject<USkeletalMeshComponent>(this);
			C->SetupAttachment(Turn);
			C->SetSkeletalMeshAsset(SK);
			C->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));
			C->SetRelativeScale3D(FVector(0.74f, 0.74f, 1.2f * (Radius / 5.2f)));
			C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			C->SetCastShadow(false);
			for (int32 i = 0; i < C->GetNumMaterials(); ++i) if (Void) C->SetMaterial(i, Void);
			C->SetAnimationMode(EAnimationMode::AnimationSingleNode);
			C->RegisterComponent();
			if (Pose) { C->PlayAnimation(Pose, true); C->SetPlayRate(0.25f); }
		}
	}
	else if (Kind == 0)
	{
		if (UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")))'''),
    ('''		const float Dur = Kind == 0 ? 0.22f : 1.5f;''', '''if (Kind == 2) { bOut = false; bGone = true; SetActorHiddenInGame(true); return; }     // between one flicker and the next, it is not there
		const float Dur = Kind == 0 ? 0.22f : 1.5f;'''),
    ('''	if (Kind == 0)
	{
		// it follows you, as far as an eye can turn in its socket''', '''if (Kind == 2)
	{
		if (bScripted || !D->Has(TEXT("inside"))) return;
		const FVector Chest = Home + FVector(0, 0, 170.f);
		const bool bLit = Dist < 1500.f && D->PlayerSees(Chest, 0.93f, 1500.f);
		Seen = bLit ? Seen + Dt : FMath::Max(0.f, Seen - Dt);
		if (Seen > 0.45f || Dist < 420.f)
		{
			// the light stutters, and the corner is empty
			P->FlickerLight(0.5f, 0.95f);
			D->Play2D(TEXT("sting_soft"), 0.7f, EWCSnd::Music);
			Withdraw(true);
			D->Event(FName(*FString::Printf(TEXT("company:%s"), *WCId.ToString())));
		}
		return;
	}
	if (Kind == 0)
	{
		// it follows you, as far as an eye can turn in its socket'''),
])
edit(R + "WCHouse.cpp", [
    ('''	if (S.StartsWith(TEXT("watcher:")))''', '''if (S.StartsWith(TEXT("company:")))
	{
		Tension = FMath::Min(1.f, Tension + 0.25f);
		if (!Has(TEXT("company_seen"))) { Set(TEXT("company_seen")); After(1.6f, [this]() { Think(TEXT("That wasn't her. That was taller.")); }); }
		return true;
	}
	if (S.StartsWith(TEXT("watcher:")))'''),
])
print("ok")
