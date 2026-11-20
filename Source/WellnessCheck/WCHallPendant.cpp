#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"
#include "GameFramework/Controller.h"
#include "Components/SpotLightComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"

void AWCDirector::InitializeHallPose()
{
	// Beyond the grandfather clock, with a fixed pool of blue low on her dress.
	PendantMark = FVector(1429.,-125.,0.);
	HallBlueFill = NewObject<UPointLightComponent>(this);
	HallBlueFill->SetWorldLocation(FVector(1393.3,-90.2,126.6));
	HallBlueFill->SetIntensityUnits(ELightUnits::Candelas);
	HallBlueFill->SetIntensity(82.f);
	HallBlueFill->SetAttenuationRadius(124.f);
	HallBlueFill->SetLightColor(FLinearColor(.095f,.30f,1.f));
	HallBlueFill->SetSpecularScale(.22f);
	HallBlueFill->SetCastShadows(false);
	HallBlueFill->SetVolumetricScatteringIntensity(0.f);
	HallBlueFill->SetVisibility(false);
	HallBlueFill->RegisterComponent();
}

void AWCDirector::ShowHallFigureLight(AWCEntity* H)
{
	HallBlueFill->SetVisibility(true);
	if (!HallEyeHighlight)
	{
		HallEyeHighlight = NewObject<UStaticMeshComponent>(H);
		HallEyeHighlight->SetupAttachment(H->Eye);
		HallEyeHighlight->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		HallEyeHighlight->SetCastShadow(false);
		HallEyeHighlight->SetStaticMesh(H->EyeBall->GetStaticMesh());
		HallEyeHighlight->SetRelativeLocation(FVector(1.12f * H->EyeRadius,-.35f,.45f));
		HallEyeHighlight->SetRelativeScale3D(FVector(.022f)); // 2.2 cm across on the eye sphere mesh.
		UMaterialInterface* Material = LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WC/Materials/M_HallEyeGlint.M_HallEyeGlint"));
		if (UMaterialInstanceDynamic* Glint = HallEyeHighlight->CreateDynamicMaterialInstance(0,Material))
			Glint->SetScalarParameterValue(TEXT("Glow"),36.f * .98f);
		HallEyeHighlight->RegisterComponent();
	}
	HallEyeHighlight->SetVisibility(true);
}

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
	if (bPendantWatching && (bFinished || bSightInterrupted || !bInHall || P->IsDown() || bBusy ||
		P->IsInputLocked() || !PendantScareDue()))
	{
		if (H) H->Vanish();
		HallBlueFill->SetVisibility(false);
		if (HallEyeHighlight) HallEyeHighlight->SetVisibility(false);
		bPendantGuiding = bPendantWatching = bEventBusy = false;
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
		// The nine-second idle shifts her weight with both feet planted.
		H->Appear(Mark, 149.9f, TEXT("Idle"));
		H->FarLight->SetLightColor(PendantBeam->GetLightColor());
		H->SetGlow(0.f);
		H->SetMood(TEXT("watch"));
		ShowHallFigureLight(H);
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
	// Only the reflected warmth follows the moving pendant. Her blue pool is fixed to the room.
	H->SetFarGlow(bLit ? PendantBeam->Intensity * .15f * FMath::SmoothStep(.36f,.9f,float(ClockSideSweep)) : 0.f);
}
