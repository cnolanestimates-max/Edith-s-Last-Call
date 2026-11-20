#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"
#include "GameFramework/Controller.h"
#include "Components/SpotLightComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInterface.h"

bool AWCDirector::PendantScareDue() const
{
	return Has(TEXT("inside")) && Has(TEXT("peek_done")) && HasItem(TEXT("key_sitting")) &&
		!Has(TEXT("sitting_open")) && !Has(TEXT("pendant_seen")) && !Has(TEXT("dawn"));
}

bool AWCDirector::DeferSittingRoomUnlock()
{
	if (!PendantScareDue() || !HallPendant.IsValid() || !PendantBeam.IsValid() || !Her()) return false;
	if (!PendantBeam->IsVisible())
	{
		if (Clock >= SpeechFreeAt)
		{
			SpeechFreeAt = Clock + 3.;
			Feedback(Has(TEXT("pendant_off")) ? TEXT("Too dark to see the keyhole. The hall switch is on the kitchen wall.") :
				TEXT("The key catches. Wait for the hall light."));
		}
		return true;
	}
	// Catch a player who reached the handle by a side room or walked the hall in the dark.
	bPendantUnlockWaiting = true;
	return true;
}

void AWCDirector::TickHallPendant(float Dt)
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
	const FVector& Mark = PendantMark;
	const double Distance = FVector::Dist2D(Eye, Mark);
	const FVector Chest = Mark + FVector(0,0,137);
	AWCDoor* SittingDoor = bPendantUnlockWaiting ? Door(TEXT("sitting")) : nullptr;
	if (bPendantUnlockWaiting && (!SittingDoor || FVector::Dist2D(Eye,SittingDoor->GetActorLocation()) > 255.))
		bPendantUnlockWaiting = false;
	const bool bSightInterrupted = bPendantGuiding && (!P->GetController() || !PlayerSees(Chest,-1.f,1650.f));
	const bool bFinished = (Distance <= 295. && PendantSweepsSeen > 0 && !bPendantUnlockWaiting) ||
		(PendantSweepsSeen >= 2 && bPendantUnlockWaiting);
	if (bPendantWatching && (bFinished || bSightInterrupted || !bInHall || !bLit || P->IsDown() || bBusy ||
		P->IsInputLocked() || !PendantScareDue()))
	{
		if (H) H->Vanish();
		bPendantReveal = bPendantGuiding = bPendantWatching = bEventBusy = false;
		if (bFinished)
		{
			RememberAtCheckpoint(TEXT("pendant_seen"));
			if (bPendantUnlockWaiting && SittingDoor && SittingDoor->bLocked) SittingDoor->Interact(P);
		}
		bPendantUnlockWaiting = false;
		return;
	}
	if (!H) return;
	const double ClockSideSweep = -Wave;
	const bool bSweepingOn = ClockSideSweep > .36;
	if (!bPendantWatching)
	{
		if (!bInHall || !bLit || !PendantScareDue() || HasActiveEncounter() || H->IsShown() ||
			ActiveNote.IsValid() || P->IsInputLocked() || P->IsDown() || !P->GetController()) return;
		const bool bOnApproach = Eye.Z < 220. && FMath::Abs(Eye.Y) < 177. && Eye.X < Mark.X - 155.;
		if (!bOnApproach && !bPendantUnlockWaiting) return;
		if (bPendantUnlockWaiting && !PlayerSees(Chest,-1.f,1650.f)) return;
		bPendantWatching = bEventBusy = true;
		PendantSweepsSeen = 0;
		PendantLitDwell = 0.f;
		H->Appear(Mark, (Eye-Mark).Rotation().Yaw, TEXT("Idle"));
		H->FarLight->SetLightColor(PendantBeam->GetLightColor());
		H->SetGlow(0.f);
		H->SetMood(TEXT("watch"));
		H->SetActorHiddenInGame(true);
	}
	// She is already waiting around the stair wall. Only a player who missed
	// her and is trying the locked door needs the existing guided glance.
	bPendantGuiding = bPendantUnlockWaiting && PendantSweepsSeen < 2;
	if (bPendantGuiding)
	{
		AController* Controller = P->GetController();
		if (Controller) Controller->SetControlRotation(FMath::RInterpTo(Controller->GetControlRotation(), (Chest-Eye).Rotation(), Dt, 3.2f));
	}
	if (!bSweepingOn) PendantLitDwell = 0.f;
	else if (PendantLitDwell < .32f && PlayerSees(Chest,.80f,1650.f))
	{
		PendantLitDwell += Dt;
		if (PendantLitDwell >= .32f) ++PendantSweepsSeen;
	}
	// A little reflected warmth lets the face register at the edge of the beam.
	H->SetFarGlow(PendantBeam->Intensity * .15f * FMath::SmoothStep(.36f,.9f,float(ClockSideSweep)));
	if (bSweepingOn == bPendantReveal) return;
	bPendantReveal = bSweepingOn;
	H->SetActorHiddenInGame(!bPendantReveal);
	if (bPendantReveal) UE_LOG(LogTemp,Display,TEXT("WCPENDANT visible distance=%.0f"), Distance);
}
