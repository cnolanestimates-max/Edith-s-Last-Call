#include "WCWorld.h"
#include "WCCharacter.h"
#include "WCDirector.h"
#include "Components/BoxComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Components/PointLightComponent.h"
#include "Animation/AnimSequence.h"
#include "Materials/MaterialInterface.h"

AWCInteractable::AWCInteractable()
{
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);
	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetupAttachment(Root);
	Mesh->SetCollisionProfileName(TEXT("BlockAll"));
	Mesh->SetCanEverAffectNavigation(false);
	Grab = CreateDefaultSubobject<UBoxComponent>(TEXT("Grab"));
	Grab->SetupAttachment(Root);
	Grab->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Grab->SetCollisionResponseToAllChannels(ECR_Ignore);
	Grab->SetCanEverAffectNavigation(false);
}

void AWCInteractable::BeginPlay()
{
	Super::BeginPlay();
	if (!GrabExtent.IsNearlyZero())
	{
		const bool bSmallPuzzlePickup = WCId == TEXT("pick_screwdriver") || WCId == TEXT("pick_key_sitting") || WCId == TEXT("pick_shears");
		Grab->SetBoxExtent(bSmallPuzzlePickup ? GrabExtent + FVector(4.f, 4.f, 3.f) : GrabExtent);
		Grab->SetRelativeLocation(GrabOffset);
		Grab->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
		Grab->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
	}
}

void AWCInteractable::Interact(AWCCharacter* By)
{
}

// ---------------------------------------------------------------------------------------------- door
AWCDoor::AWCDoor()
{
	PrimaryActorTick.bCanEverTick = true;
	Prompt = TEXT("Open");
}

void AWCDoor::BeginPlay()
{
	Super::BeginPlay();
	BaseYaw = GetActorRotation().Yaw;
	bOpen = bStartOpen;
	Angle = Target = bOpen ? OpenAngle : 0.f;
	Snap();
}

void AWCDoor::Snap()
{
	Angle = Target;
	FRotator R = GetActorRotation();
	R.Yaw = BaseYaw + Angle;
	SetActorRotation(R);
}

FString AWCDoor::GetPrompt() const
{
	if (bLocked)
	{
		if (WCId == TEXT("sitting")) return TEXT("Try the sitting-room door");
		if (WCId == TEXT("up_prayer")) return TEXT("Try the prayer-room door");
		if (WCId == TEXT("up_ell")) return TEXT("Try the rear upstairs hall");
		if (WCId == TEXT("music_sitting")) return TEXT("Try the door latched from the sitting room");
		if (WCId == TEXT("scullery_pantry") || WCId == TEXT("scullery_sickroom")) return TEXT("Try the scullery door");
		return TEXT("Try the door");
	}
	return bOpen ? TEXT("Close") : TEXT("Open");
}

void AWCDoor::SetAngle(float Degrees, float Seconds)
{
	Target = Degrees;
	Rate = FMath::Abs(Target - Angle) / FMath::Max(Seconds, 0.02f);
	bOpen = FMath::Abs(Target) > 2.f;
}

void AWCDoor::SetOpen(bool bNewOpen, float Seconds, bool bSilent)
{
	if (bNewOpen == bOpen && FMath::IsNearlyEqual(Target, bNewOpen ? OpenAngle : 0.f, 0.5f)) return;
	if (bNewOpen) { /* keep an already-chosen swing side when re-opening an ajar door */ if (FMath::Abs(Angle) > 3.f && (Angle > 0.f) != (OpenAngle > 0.f)) OpenAngle = -OpenAngle; }
	SetAngle(bNewOpen ? OpenAngle : 0.f, Seconds > 0.f ? Seconds : SwingSeconds);
	if (!bSilent)
	{
		if (AWCDirector* D = AWCDirector::Get(this))
		{
			D->PlayAt(bNewOpen ? TEXT("door_open") : TEXT("door_close"), GetActorLocation() + FVector(0, 0, 100), 0.8f);
		}
	}
}

void AWCDoor::OpenAwayFrom(const FVector& From, float Seconds)
{
	// the leaf runs along the closed door's +X; its face normal is +Y.  Positive yaw swings the leaf toward +Y.
	const FRotator Closed(0.f, BaseYaw, 0.f);
	const FVector Normal = FRotationMatrix(Closed).GetUnitAxis(EAxis::Y);
	const float Side = FVector::DotProduct(From - GetActorLocation(), Normal);
	OpenAngle = FMath::Abs(OpenAngle) * (Side > 0.f ? -1.f : 1.f);
	SetOpen(true, Seconds);
}

void AWCDoor::Slam()
{
	SetAngle(0.f, 0.16f);
	if (AWCDirector* D = AWCDirector::Get(this)) D->PlayAt(TEXT("door_slam"), GetActorLocation() + FVector(0, 0, 100), 1.f);
}

void AWCDoor::HoldAtCrack(bool bHold, bool bSnap)
{
	bHeldAtCrack = bHold;
	bEnabled = !bHold;
	if (bHold)
	{
		SetLocked(false);
		SetAngle(FMath::Sign(OpenAngle) * 15.f, 3.2f);
		if (bSnap) Snap();
	}
}

void AWCDoor::Interact(AWCCharacter* By)
{
	AWCDirector* D = AWCDirector::Get(this);
	if (!D) return;
	if (WCId == TEXT("up_bath2") && D->IsCrawlingThroughRearBath()) return;
	if (WCId == TEXT("music_sitting") && !D->Has(TEXT("sitting_open")))
	{
		D->PlayAt(TEXT("door_locked"), GetActorLocation() + FVector(0, 0, 100), 0.9f);
		D->Feedback(TEXT("A bolt on the sitting-room side. I'll need to unlock its hall door first."));
		return;
	}
	if (bLocked)
	{
		if (!KeyId.IsNone() && D->HasItem(KeyId))
		{
			if (WCId == TEXT("sitting") && D->DeferSittingRoomUnlock()) return;
			if (WCId == TEXT("cellar"))
			{
				// the finale needs every keepsake and the shears: the cellar stays shut until he has them all, so the ending can
				// always be finished once he is down there (Cheyenne, 2026-11-23: the playtest went down without Ruth's music box)
				static const TCHAR* Need[][2] = { { TEXT("keep_ruth"), TEXT("Ruth's music box") }, { TEXT("keep_walter"), TEXT("Walter's ring") },
					{ TEXT("keep_daniel"), TEXT("Daniel's dog tags") }, { TEXT("keep_eye"), TEXT("her glass eye") }, { TEXT("shears"), TEXT("something to cut with") } };
				for (const auto& N : Need)
				{
					if (D->HasItem(FName(N[0]))) continue;
					D->PlayAt(TEXT("door_locked"), GetActorLocation() + FVector(0, 0, 100), 0.9f);
					D->Feedback(FString::Printf(TEXT("Not yet. Not without %s."), N[1]));
					D->SetCellarRouteObjective();
					return;
				}
			}
			bLocked = false;
			D->PlayAt(TEXT("door_unlock"), GetActorLocation() + FVector(0, 0, 100), 0.9f);
			D->Event(FName(*FString::Printf(TEXT("unlock:%s"), *WCId.ToString())));
			OpenAwayFrom(By ? By->GetActorLocation() : GetActorLocation());
			return;
		}
		D->PlayAt(TEXT("door_locked"), GetActorLocation() + FVector(0, 0, 100), 0.9f);
		D->Event(FName(*FString::Printf(TEXT("locked:%s"), *WCId.ToString())));
		return;
	}
	if (IsAjar() || !bOpen)
	{
		if (IsAjar()) { bOpen = false; }
		OpenAwayFrom(By ? By->GetActorLocation() : GetActorLocation());
	}
	else SetOpen(false);
	D->Event(FName(*FString::Printf(TEXT("door:%s"), *WCId.ToString())));
}

void AWCDoor::Tick(float Dt)
{
	Super::Tick(Dt);
	// a door only stops you when it is shut; an open leaf never pins you in a doorway
	const bool bSolid = bHeldAtCrack || (FMath::Abs(Angle) < 2.f && FMath::Abs(Target) < 2.f);
	if (bSolid != bWasSolid)
	{
		bWasSolid = bSolid;
		Mesh->SetCollisionResponseToChannel(ECC_Pawn, bSolid ? ECR_Block : ECR_Ignore);
	}
	if (FMath::IsNearlyEqual(Angle, Target, 0.01f)) return;
	Angle = FMath::FInterpConstantTo(Angle, Target, Dt, Rate);
	FRotator R = GetActorRotation();
	R.Yaw = BaseYaw + Angle;
	SetActorRotation(R);
}

// ---------------------------------------------------------------------------------------------- note / pickup / usable
AWCNote::AWCNote()
{
	Prompt = TEXT("Read");
}

void AWCNote::Interact(AWCCharacter* By)
{
	if (AWCDirector* D = AWCDirector::Get(this)) D->OpenNote(this);
}

AWCPickup::AWCPickup()
{
	Prompt = TEXT("Take");
}

void AWCPickup::Interact(AWCCharacter* By)
{
	if (AWCDirector* D = AWCDirector::Get(this))
	{
		if (ItemId == TEXT("tape1"))
		{
			D->StartShedPickup(this);
			return;
		}
		D->GiveItem(ItemId, DisplayName);
		SetActorHiddenInGame(true);
		SetActorEnableCollision(false);
		D->Event(FName(*FString::Printf(TEXT("take:%s"), *ItemId.ToString())));
	}
}

AWCLook::AWCLook()
{
	Prompt = TEXT("Look");
	Mesh->SetCollisionProfileName(TEXT("NoCollision"));
}

void AWCLook::Interact(AWCCharacter* By)
{
	if (AWCDirector* D = AWCDirector::Get(this))
	{
		D->Feedback(Text);
		D->Event(FName(*FString::Printf(TEXT("look:%s"), *WCId.ToString())));
	}
}

void AWCUsable::Interact(AWCCharacter* By)
{
	if (AWCDirector* D = AWCDirector::Get(this)) D->Event(FName(*FString::Printf(TEXT("use:%s"), *WCId.ToString())));
}

// ---------------------------------------------------------------------------------------------- trigger
AWCTrigger::AWCTrigger()
{
	Box = CreateDefaultSubobject<UBoxComponent>(TEXT("Box"));
	SetRootComponent(Box);
	Box->SetBoxExtent(FVector(100.f));
	Box->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Box->SetCollisionResponseToAllChannels(ECR_Ignore);
	Box->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
	Box->SetCanEverAffectNavigation(false);
}

bool AWCTrigger::Contains(const FVector& P) const
{
	const FVector L = Box->GetComponentTransform().InverseTransformPositionNoScale(P);
	const FVector E = Box->GetScaledBoxExtent();
	return FMath::Abs(L.X) <= E.X && FMath::Abs(L.Y) <= E.Y && FMath::Abs(L.Z) <= E.Z;
}

// ---------------------------------------------------------------------------------------------- watcher
AWCWatcher::AWCWatcher()
{
	PrimaryActorTick.bCanEverTick = true;
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);
	Turn = CreateDefaultSubobject<USceneComponent>(TEXT("Turn"));
	Turn->SetupAttachment(Root);
}

void AWCWatcher::BeginPlay()
{
	Super::BeginPlay();
	Home = GetActorLocation();
	HomeQuat = GetActorQuat();
	UMaterialInterface* Black = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_EyeBlack.M_EyeBlack"));
	UMaterialInterface* PaleIris = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_EyeIris.M_EyeIris"));
	UMaterialInterface* Hair = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Hair.M_Hair"));
	auto Part = [this](UStaticMesh* Mesh, const FVector& Loc, const FVector& Scale, UMaterialInterface* Mat, const FRotator& Rot = FRotator::ZeroRotator)
	{
		UStaticMeshComponent* C = NewObject<UStaticMeshComponent>(this);
		C->SetupAttachment(Turn);
		C->SetStaticMesh(Mesh);
		C->SetRelativeLocation(Loc);
		C->SetRelativeRotation(Rot);
		C->SetRelativeScale3D(Scale);
		C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		C->SetCastShadow(false);
		C->SetLightingChannels(true, true, false);
		if (Mat) C->SetMaterial(0, Mat);
		C->RegisterComponent();
		return C;
	};
	if (Kind == 2)
	{
		// the thing she asked in: not her outline, and not solid.  Black smoke standing like a man.
		UInstancedStaticMeshComponent* C = NewObject<UInstancedStaticMeshComponent>(this);
		C->SetupAttachment(Turn);
		C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		C->SetCastShadow(false);
		C->RegisterComponent();
		AWCSmokeMan::Build(C, 300.f * (Radius / 5.2f), GetTypeHash(WCId));
		if (WCId == TEXT("company_foyer") || WCId == TEXT("company_landing"))
		{
			// A cold patch on the wall beyond him outlines the smoke even on a dark monitor.
			auto* Bounce = NewObject<UPointLightComponent>(this);
			Bounce->SetupAttachment(Turn); Bounce->SetRelativeLocation(FVector(-96,60,145));
			Bounce->SetIntensityUnits(ELightUnits::Lumens); Bounce->SetIntensity(360.f);
			Bounce->SetLightColor(FLinearColor(.57f,.68f,.78f)); Bounce->SetSourceRadius(10.f);
			Bounce->SetAttenuationRadius(340.f); Bounce->SetCastShadows(true); Bounce->RegisterComponent();
		}
	}
	else if (WCId == TEXT("book_eye"))
	{
		UStaticMesh* Plane = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Plane.Plane"));
		UMaterialInterface* Pigment = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_ShelfPupil.M_ShelfPupil"));
		if (ensure(Plane && Pigment))
		{
			const FRotator FacingGap = FRotationMatrix::MakeFromXZ(FVector::RightVector, FVector::ForwardVector).Rotator();
			auto* Pupil = Part(Plane, FVector(-2.8f, 0.f, 0.f), FVector(Radius / 100.f), Pigment, FacingGap);
			Pupil->SetReceivesDecals(false);
		}
	}
	else if (Kind == 0)
	{
		if (UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")))
		{
			const float R = Radius;
			Part(Sphere, FVector::ZeroVector, FVector(R / 50.f), Black);
			Part(Sphere, FVector(R * 0.80f, 0.f, 0.f), FVector(R * 0.30f / 50.f, R * 0.34f / 50.f, R * 0.34f / 50.f), PaleIris);
			Part(Sphere, FVector(R * 0.985f, 0.f, 0.f), FVector(R * 0.14f / 50.f, R * 0.16f / 50.f, R * 0.16f / 50.f), Black);
		}
	}
	else if (UStaticMesh* Cyl = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")))
	{
		// a hank of long grey-blonde hair: a few dozen strands of uneven length hanging from the actor's origin
		FRandomStream Rs(GetTypeHash(WCId) + 7);
		for (int32 i = 0; i < 46; ++i)
		{
			const float Len = Rs.FRandRange(55.f, 150.f) * (Radius / 5.2f);
			const float Thick = Rs.FRandRange(0.35f, 0.9f);
			const FVector Off(Rs.FRandRange(-9.f, 9.f), Rs.FRandRange(-5.f, 5.f), -Len * 0.5f);
			Part(Cyl, Off, FVector(Thick / 100.f, Thick / 100.f, Len / 100.f), Hair, FRotator(Rs.FRandRange(-2.5f, 2.5f), 0.f, Rs.FRandRange(-2.5f, 2.5f)));
		}
	}
	bOut = !bScripted && Kind != 2;            // the Company waits until she has been seen
	SetActorHiddenInGame(!bOut);
}

FVector AWCWatcher::ShelfPupilOffset() const
{
	// The watcher faces the reader, so its left is the right edge of the reader's view.
	return FVector(0.f, -2.15f * Radius, 0.f);
}

void AWCWatcher::Reveal()
{
	if (bGone) return;
	SetActorLocationAndRotation(Home, HomeQuat);
	if (WCId == TEXT("book_eye"))
	{
		ShelfEyeAge = 0.f;
		Turn->SetRelativeLocation(ShelfPupilOffset());
	}
	SetActorHiddenInGame(false);
	bOut = true;
	LeaveT = -1.f;
}

void AWCWatcher::Withdraw(bool bQuiet)
{
	if (!bOut || LeaveT >= 0.f) return;
	LeaveT = 0.f;
	if (AWCDirector* D = AWCDirector::Get(this))
	{
		if (!bQuiet && Kind != 0) D->PlayAt(TEXT("scratch_wall"), Home, 0.9f, 1.2f, 1400.f);
		if (!bScripted) D->Event(FName(*FString::Printf(TEXT("watcher:%s"), *WCId.ToString())));
	}
}

void AWCWatcher::Tick(float Dt)
{
	Super::Tick(Dt);
	if (Kind == 2 && !bOut && !bGone && !bScripted)
	{
		AWCDirector* Dir = AWCDirector::Get(this);
		if (!Dir || !Dir->Player() || !Dir->IsPlaying() || Dir->Has(WCId)) return;
		const bool bFoyer = WCId == TEXT("company_foyer");
		const bool bReady = bFoyer ? Dir->Has(TEXT("inside")) : Dir->Has(TEXT("peek_done"));
		if (bReady && !Dir->HasActiveEncounter()) Reveal();
		return;
	}
	if (!bOut) return;
	AWCDirector* D = AWCDirector::Get(this);
	AWCCharacter* P = D ? D->Player() : nullptr;
	if (!P) return;
	if (LeaveT >= 0.f)
	{
		// going: the eye sinks back into the dark; the hair is drawn up out of sight
		LeaveT += Dt;
		if (Kind == 2) { bOut = false; bGone = true; SetActorHiddenInGame(true); return; }     // between one flicker and the next, it is not there
		const float Dur = Kind == 0 ? 0.22f : 1.5f;
		const float U = FMath::Clamp(LeaveT / Dur, 0.f, 1.f);
		const FVector Away = Kind == 0 ? -HomeQuat.GetForwardVector() * (Radius * 3.2f) : FVector(0, 0, 190.f * (Radius / 5.2f));
		if (WCId == TEXT("book_eye")) Turn->SetRelativeLocation(ShelfPupilOffset() * U);
		else SetActorLocation(Home + Away * (Kind == 0 ? U : U * U));
		if (U >= 1.f) { bOut = false; bGone = !bScripted; SetActorHiddenInGame(true); }
		return;
	}
	const FVector Eye = P->EyeLocation();
	if (WCId == TEXT("book_eye"))
	{
		if (ShelfEyeAge >= 3.8f) return;
		ShelfEyeAge = FMath::Min(ShelfEyeAge + Dt, 3.8f);
		const float Travel = FMath::SmoothStep(0.f, 3.8f, ShelfEyeAge);
		Turn->SetRelativeLocation(ShelfPupilOffset() * (1.f - Travel));
		return;
	}
	const float Dist = FVector::Dist(Eye, Home);
	if (Kind == 2)
	{
		if (bScripted || !D->Has(TEXT("inside")) || D->HasActiveEncounter() || P->IsDown()) return;
		const FVector Chest = Home + FVector(0, 0, 170.f);
		const bool bLit = Dist < 1500.f && D->PlayerSees(Chest, 0.84f, 1500.f);
		Seen = bLit ? Seen + Dt : FMath::Max(0.f, Seen - Dt);
		if (Seen >= 1.15f)
		{
			// the light stutters, and the corner is empty
			P->FlickerLight(0.5f, 0.95f);
			D->Play2D(TEXT("sting_soft"), 0.7f, EWCSnd::Music);
			Withdraw(true);
			D->Set(WCId);
			D->Event(FName(*FString::Printf(TEXT("company:%s"), *WCId.ToString())));
		}
		return;
	}
	if (Kind == 0)
	{
		// it follows you, as far as an eye can turn in its socket
		const FVector Local = HomeQuat.UnrotateVector((Eye - Home).GetSafeNormal());
		FRotator Want = Local.Rotation();
		Want.Yaw = FMath::Clamp(Want.Yaw, -52.f, 52.f);
		Want.Pitch = FMath::Clamp(Want.Pitch, -45.f, 45.f);
		Turn->SetRelativeRotation(FMath::RInterpTo(Turn->GetRelativeRotation(), Want, Dt, 5.f));
	}
	else
	{
		// the faintest sway
		Turn->SetRelativeRotation(FRotator(FMath::Sin(GetWorld()->GetTimeSeconds() * 0.9f + Home.X) * 1.6f, 0.f, FMath::Sin(GetWorld()->GetTimeSeconds() * 0.7f + Home.Y) * 1.3f));
	}
	if (bScripted || !D->Has(TEXT("inside"))) return;
	const FVector Mid = Kind == 0 ? Home : Home - FVector(0, 0, 55.f);
	const bool bLooked = Dist < 1100.f && D->PlayerSees(Mid, Kind == 0 ? 0.988f : 0.965f, 1100.f) && P->IsFlashlightOn();
	Seen = bLooked ? Seen + Dt : FMath::Max(0.f, Seen - Dt * 0.5f);
	if (Seen > (Kind == 0 ? 0.55f : 0.9f) || Dist < (Kind == 0 ? 120.f : 230.f)) Withdraw();
}

// ================================================================================================ the Company, as smoke
AWCSmokeMan::AWCSmokeMan()
{
	PrimaryActorTick.bCanEverTick = false;
	Smoke = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Smoke"));
	RootComponent = Smoke;
	Smoke->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Smoke->SetCastShadow(false);
	Smoke->bAffectDynamicIndirectLighting = false;
	Smoke->bAffectDistanceFieldLighting = false;
}

void AWCSmokeMan::BeginPlay()
{
	Super::BeginPlay();
	Build(Smoke, Tall, GetTypeHash(GetName()));
}

void AWCSmokeMan::Build(UInstancedStaticMeshComponent* C, float Height, int32 Seed)
{
	if (!C) return;
	UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	UMaterialInterface* Mat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Smoke.M_Smoke"));
	if (!Sphere) return;
	C->SetStaticMesh(Sphere);
	if (Mat) C->SetMaterial(0, Mat);
	C->ClearInstances();
	const float K = Height / 300.f;
	FRandomStream Rs(Seed);
	// (centre x forward, y left, z up; size across, deep, high), all in cm for a 3 m figure
	auto Blob = [C, K](float X, float Y, float Z, float W, float D, float H)
	{
		C->AddInstance(FTransform(FRotator::ZeroRotator, FVector(X, Y, Z) * K, FVector(D, W, H) * K / 100.f));
	};
	// a long head with nothing on it, a thick neck, shoulders far too wide, a narrow waist
	Blob(4, 0, 274, 30, 32, 50);
	Blob(2, 0, 246, 22, 22, 26);
	Blob(0, 0, 216, 104, 40, 50);
	Blob(0, 0, 184, 78, 38, 54);
	Blob(-2, 0, 150, 58, 34, 52);
	Blob(-2, 0, 118, 54, 34, 44);
	for (int32 Side = -1; Side <= 1; Side += 2)
	{
		// arms that hang past the knee and end in nothing
		Blob(0, Side * 56.f, 196, 22, 22, 66);
		Blob(4, Side * 62.f, 142, 18, 18, 72);
		Blob(8, Side * 65.f, 92, 15, 15, 56);
		Blob(10, Side * 66.f, 58, 11, 12, 34);
		// legs that thin out and never reach the floor
		Blob(-2, Side * 17.f, 84, 26, 26, 62);
		Blob(-4, Side * 16.f, 44, 20, 22, 54);
		Blob(-8, Side * 14.f, 14, 13, 18, 34);
	}
	// what drifts off it: behind, above the shoulders, round the feet
	for (int32 i = 0; i < 22; ++i)
	{
		const float Z = Rs.FRandRange(6.f, 286.f);
		const float Wide = Z > 170.f && Z < 240.f ? 62.f : 36.f;
		const float S = Rs.FRandRange(14.f, 34.f);
		Blob(Rs.FRandRange(-34.f, -6.f), Rs.FRandRange(-Wide, Wide), Z, S, S * Rs.FRandRange(0.9f, 1.6f), S * Rs.FRandRange(1.1f, 2.2f));
	}
	for (int32 i = 0; i < 8; ++i)
	{
		const float S = Rs.FRandRange(16.f, 30.f);
		Blob(Rs.FRandRange(-30.f, 16.f), Rs.FRandRange(-34.f, 34.f), Rs.FRandRange(0.f, 26.f), S * 1.4f, S * 1.4f, S * 0.8f);
	}
}
