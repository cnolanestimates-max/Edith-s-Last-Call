#include "WCDirector.h"
#include "WCCharacter.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/Controller.h"

void AWCDirector::StageSettlersPickup(AActor* ShelfBook, const FVector& Start, const FVector& Out, float FloorZ)
{
	AWCCharacter* P = Player();
	if (!P || !IsValid(ShelfBook)) { FinishSettlersPickup(); return; }
	SettlersStart = Start;
	SettlersFloor = Start + Out * 14. + FVector(-Out.Y, Out.X, 0.) * 27.;
	SettlersFloor.Z = FloorZ;
	SettlersFacing = (SettlersFloor - P->EyeLocation()).GetSafeNormal2D().Rotation();
	SettlersEye = P->EyeLocation();
	SettlersInitialView = P->GetControlRotation();
	SettlersDropAt = Clock;
	ShelfBook->SetActorHiddenInGame(true);
	ShelfBook->SetActorEnableCollision(false);

	auto Part = [this](const TCHAR* Path, USceneComponent* Parent = nullptr) -> UStaticMeshComponent*
	{
		UStaticMesh* Asset = LoadObject<UStaticMesh>(nullptr, Path);
		if (!Asset) return nullptr;
		UStaticMeshComponent* Mesh = NewObject<UStaticMeshComponent>(this);
		Mesh->SetMobility(EComponentMobility::Movable);
		Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Mesh->SetCanEverAffectNavigation(false);
		Mesh->SetStaticMesh(Asset);
		if (Parent) Mesh->SetupAttachment(Parent);
		Mesh->RegisterComponent();
		return Mesh;
	};
	SettlersPages = Part(TEXT("/Game/WC/Props/HouseDetails/SM_SettlersPages.SM_SettlersPages"));
	if (SettlersPages.IsValid())
	{
		SettlersCover = Part(TEXT("/Game/WC/Props/HouseDetails/SM_SettlersCover.SM_SettlersCover"), SettlersPages.Get());
		SettlersKey = Part(TEXT("/Game/WC/Props/SM_Item_KeyDesk.SM_Item_KeyDesk"), SettlersPages.Get());
		SettlersGlove = Part(TEXT("/Game/WC/Props/HouseDetails/SM_SettlersGlove.SM_SettlersGlove"), SettlersPages.Get());
	}
	if (SettlersCover.IsValid()) SettlersCover->SetRelativeLocation(FVector(0., -7.86, 4.28));
	if (SettlersKey.IsValid())
	{
		SettlersKey->SetRelativeLocation(FVector(.25, .1, .81));
		SettlersKey->SetRelativeRotation(FRotator(0., -14., 0.));
		SettlersKey->SetRelativeScale3D(FVector(1.48));
	}
	if (SettlersGlove.IsValid()) SettlersGlove->SetVisibility(false);
	// A little bounce inside the cut pages keeps the key legible even with the flashlight off.
	SettlersFill = NewObject<UPointLightComponent>(this);
	SettlersFill->SetIntensityUnits(ELightUnits::Lumens);
	SettlersFill->SetIntensity(0.f);
	SettlersFill->SetAttenuationRadius(90.f);
	SettlersFill->SetLightColor(FLinearColor(1.f, .87f, .70f));
	SettlersFill->SetCastShadows(false);
	SettlersFill->RegisterComponent();
	TickSettlersPickup();
}

void AWCDirector::TickSettlersPickup()
{
	AWCCharacter* P = Player();
	if (!P || !P->GetController()) { FinishSettlersPickup(); return; }
	const double T = Clock - SettlersDropAt;
	auto Ease = [T](double Begin, double End) { return FMath::SmoothStep(Begin, End, T); };
	const FQuat Facing = SettlersFacing.Quaternion();
	const FVector Forward = Facing.GetForwardVector(), Right = Facing.GetRightVector();
	// Finish the original eye hold and the first running treads before the deputy looks down.
	const double Drop = FMath::Clamp(T / .48, 0., 1.);
	FVector Book = FMath::Lerp(SettlersStart, SettlersFloor, Drop);
	Book.Z = FMath::Lerp(SettlersStart.Z, SettlersFloor.Z, Drop * Drop);
	const double Reach = Ease(3.50, 4.54), Lift = Ease(4.56, 5.85), Pocket = Ease(7.18, 7.95);
	const FVector Hold = SettlersEye + Forward * 41. + Right * 4. - FVector(0., 0., 43.);
	Book = FMath::Lerp(Book, Hold, Lift) + Pocket * (Right * 14. - Forward * 16. - FVector(0., 0., 65.));
	const FRotator Tilt(81. * (1.-Drop) + 15.*Lift, 10.*Drop, 44.*(1.-Drop) - 4.*Lift);
	if (SettlersPages.IsValid()) SettlersPages->SetWorldLocationAndRotation(Book, Facing * Tilt.Quaternion());
	if (SettlersGlove.IsValid())
	{
		// The wrist enters from the deputy's right; the thumb settles against the fore edge.
		SettlersGlove->SetVisibility(T > 3.5);
		SettlersGlove->SetRelativeLocation((1.-Reach) * FVector(-40., 34., 19.));
	}
	const double Open = Ease(4.86, 5.99);
	if (SettlersCover.IsValid())
		SettlersCover->SetRelativeRotation(FQuat(FVector::ForwardVector, FMath::DegreesToRadians(141. * Open)));
	if (SettlersFill.IsValid())
	{
		SettlersFill->SetWorldLocation(Book - Forward * 14. - Right * 12. + FVector(0,0,32));
		SettlersFill->SetIntensity(34. * Ease(2.95, 4.19) * (1.-Pocket));
	}
	if (T < 2.95) return;

	const double Bend = Ease(2.95, 4.48), Rise = Ease(4.61, 6.00);
	const FVector KneelingEye = SettlersFloor - Forward * 47. + FVector(0., 0., 59.);
	P->PickupEyeOffset = (KneelingEye - SettlersEye) * Bend * (1.-Rise);
	const FVector Eye = SettlersEye + P->PickupEyeOffset;
	const FVector GazePoint = Book - Right * (2. + 2.*Open) + FVector(0,0,3.5);
	const FRotator Look = (GazePoint - Eye).Rotation();
	const FRotator ReturnView(-9., SettlersInitialView.Yaw, 0.);
	const FQuat Down = FQuat::Slerp(SettlersInitialView.Quaternion(), Look.Quaternion(), Ease(2.95, 4.10));
	P->GetController()->SetControlRotation(FQuat::Slerp(Down, ReturnView.Quaternion(), Ease(7.08, 7.98)).Rotator());
	if (T >= 8.) FinishSettlersPickup();
}

void AWCDirector::FinishSettlersPickup()
{
	SettlersDropAt = -1.;
	if (SettlersFill.IsValid()) SettlersFill->DestroyComponent();
	if (SettlersGlove.IsValid()) SettlersGlove->DestroyComponent();
	if (SettlersKey.IsValid()) SettlersKey->DestroyComponent();
	if (SettlersCover.IsValid()) SettlersCover->DestroyComponent();
	if (SettlersPages.IsValid()) SettlersPages->DestroyComponent();
	ShowTagged(TEXT("SettlersBook"), false);
	ShowTagged(TEXT("Show_bookkey"), false);
	Set(TEXT("book_done"));
	if (!HasItem(TEXT("key_desk")) && !Has(TEXT("desk_open")))
		GiveItem(TEXT("key_desk"), TEXT("Walter's desk key"));
	if (AWCCharacter* P = Player())
	{
		P->PickupEyeOffset = FVector::ZeroVector;
		P->SetInputLocked(false);
	}
	bBusy = false;
	Tension = .6f;
	Rest(120.f);
	if (!Has(TEXT("desk_open"))) Event(TEXT("take:key_desk"));
}
