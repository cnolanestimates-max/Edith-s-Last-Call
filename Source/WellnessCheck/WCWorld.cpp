#include "WCWorld.h"
#include "WCCharacter.h"
#include "WCDirector.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
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
		Grab->SetBoxExtent(GrabExtent);
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
	if (bLocked) return TEXT("Try the door");
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

void AWCDoor::Interact(AWCCharacter* By)
{
	AWCDirector* D = AWCDirector::Get(this);
	if (!D) return;
	if (bLocked)
	{
		if (!KeyId.IsNone() && D->HasItem(KeyId))
		{
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
	const bool bSolid = FMath::Abs(Angle) < 2.f && FMath::Abs(Target) < 2.f;
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
		D->Think(Text);
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
	UMaterialInterface* Pale = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_EyeIris.M_EyeIris"));
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
	};
	if (Kind == 2)
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
		if (UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")))
		{
			const float R = Radius;
			Part(Sphere, FVector::ZeroVector, FVector(R / 50.f), Black);
			Part(Sphere, FVector(R * 0.80f, 0.f, 0.f), FVector(R * 0.30f / 50.f, R * 0.34f / 50.f, R * 0.34f / 50.f), Pale);
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

void AWCWatcher::Reveal()
{
	if (bGone) return;
	SetActorLocationAndRotation(Home, HomeQuat);
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
		if (!bQuiet) D->PlayAt(Kind == 0 ? TEXT("skitter") : TEXT("scratch_wall"), Home, 0.9f, Kind == 0 ? 1.f : 1.2f, 1400.f);
		if (!bScripted) D->Event(FName(*FString::Printf(TEXT("watcher:%s"), *WCId.ToString())));
	}
}

void AWCWatcher::Tick(float Dt)
{
	Super::Tick(Dt);
	if (Kind == 2 && !bOut && !bGone && !bScripted)
	{
		AWCDirector* Dir = AWCDirector::Get(this);
		if (Dir && Dir->Has(TEXT("peek_done")) && Dir->Player() && FVector::Dist(Dir->Player()->GetActorLocation(), Home) > 900.f) Reveal();
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
		SetActorLocation(Home + Away * (Kind == 0 ? U : U * U));
		if (U >= 1.f) { bOut = false; bGone = !bScripted; SetActorHiddenInGame(true); }
		return;
	}
	const FVector Eye = P->EyeLocation();
	const float Dist = FVector::Dist(Eye, Home);
	if (Kind == 2)
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
