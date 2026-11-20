#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "Components/SpotLightComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInterface.h"

void AWCDirector::TickHallPendant()
{
	AWCCharacter* P = Player();
	if (!HallPendant.IsValid() || !PendantBeam.IsValid() || !P) return;
	const FVector Mount = HallPendant->GetComponentLocation();
	const FVector Eye = P->EyeLocation();
	const double Wave = FMath::Sin(Clock * 1.38);
	HallPendant->SetWorldRotation(FQuat(FVector::ForwardVector, FMath::DegreesToRadians(20. * Wave)));
	const bool bInHall = Eye.Z > 20. && Eye.Z < 318. && FMath::Abs(Eye.Y - Mount.Y) < 270. &&
		FMath::Abs(Eye.X - Mount.X) < 1610. && IsInsideHouse(P->GetActorLocation());
	if (bInHall && ((LastPendantWave < .95 && Wave >= .95) || (LastPendantWave > -.95 && Wave <= -.95)))
		PlayAt(TEXT("pendant_creak"), Mount - FVector(0,0,22), Wave > 0. ? .58f : .46f, Wave > 0. ? .91f : 1.04f);
	LastPendantWave = Wave;
	const bool bLit = PendantBeam->IsVisible() && PendantBeam->Intensity > 1.f;
	if (bInHall && !PendantSpill)
	{
		PendantSpill = NewObject<UPointLightComponent>(this);
		PendantSpill->SetupAttachment(HallPendant.Get());
		PendantSpill->SetRelativeLocation(FVector(0,0,-90));
		PendantSpill->SetIntensityUnits(ELightUnits::Lumens);
		PendantSpill->SetAttenuationRadius(280.f);
		PendantSpill->SetLightColor(FLinearColor(1.f,.59f,.26f));
		PendantSpill->SetLightingChannels(true,true,false);
		PendantSpill->SetCastShadows(false);
		PendantSpill->RegisterComponent();
	}
	if (PendantSpill)
	{
		PendantSpill->SetVisibility(bLit && bInHall);
		if (bLit && bInHall) PendantSpill->SetIntensity(PendantBeam->Intensity * .09f);
	}
	if (bLit != bPendantLit && PendantBulbSlot != INDEX_NONE)
	{
		HallPendant->SetMaterial(PendantBulbSlot, bLit ? PendantLit : PendantDark);
		bPendantLit = bLit;
	}

	AWCEntity* H = Her();
	const FVector Mark(Mount.X + 6., Mount.Y + 72., 0.);
	const double Distance = FVector::Dist2D(Eye, Mark);
	// The player can hold their position for any number of swings. Approaching spends the scare.
	const bool bLookingAway = FVector::DotProduct(P->EyeForward(), (Mark + FVector(0,0,137) - Eye).GetSafeNormal()) < .15f;
	if (bPendantWatching && (!bInHall || !bLit || Distance <= 295. || bLookingAway || P->IsDown() || bBusy ||
		(Has(TEXT("heard_upstairs")) && !Has(TEXT("peek_done")))))
	{
		if (H && bPendantReveal) H->Vanish();
		bPendantReveal = bPendantWatching = bEventBusy = false;
		if (bInHall && Distance <= 295.) RememberAtCheckpoint(TEXT("pendant_seen"));
		return;
	}
	if (!H) return;
	const bool bSweepingOn = Wave > .36;
	if (!bPendantWatching)
	{
		if (!bInHall || !bLit || !bSweepingOn || Distance < 480. || Has(TEXT("pendant_seen")) ||
			!Has(TEXT("inside")) || HasActiveEncounter() || H->IsShown() || ActiveNote.IsValid() ||
			P->IsInputLocked() || P->IsDown() || (Has(TEXT("heard_upstairs")) && !Has(TEXT("peek_done"))) ||
			!PlayerSees(Mark + FVector(0,0,137), .83f, 1650.f)) return;
		bPendantWatching = bEventBusy = true;
	}
	// Warm light reflected back from the floor brings her face out on the lit swing.
	if (bSweepingOn) H->SetFarGlow(PendantBeam->Intensity * .26f * FMath::SmoothStep(.36f,.9f,float(Wave)));
	if (bSweepingOn == bPendantReveal) return;
	bPendantReveal = bSweepingOn;
	if (bPendantReveal)
	{
		H->Appear(Mark, (Eye-Mark).Rotation().Yaw, TEXT("Idle"));
		H->FarLight->SetLightColor(PendantBeam->GetLightColor());
		H->SetGlow(0.f);
		H->SetMood(TEXT("watch"));
		UE_LOG(LogTemp,Display,TEXT("WCPENDANT visible distance=%.0f"), Distance);
	}
	else H->Vanish();
}
