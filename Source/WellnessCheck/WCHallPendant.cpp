#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "Components/SpotLightComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInterface.h"

void AWCDirector::TickHallPendant()
{
	AWCCharacter* P=Player();
	if (!HallPendant.IsValid() || !PendantBeam.IsValid() || !P) return;
	const FVector Mount=HallPendant->GetComponentLocation();
	const FVector Eye=P->EyeLocation();
	const bool bNear = Eye.Z>20 && Eye.Z<318 && FMath::Abs(Eye.Y-Mount.Y)<420 && FMath::Abs(Eye.X-Mount.X)<1250;
	// Rotation about a fixed ceiling hook carries the flex, bulb and attached cone in one transform.
	const double Wave=FMath::Sin(Clock*1.38);
	if (bNear)
		HallPendant->SetWorldRotation(FQuat(FVector::ForwardVector,FMath::DegreesToRadians(20.*Wave)));
	const FVector Mark(Mount.X+6.,Mount.Y-109.,0.);
	const bool bHall=bNear && FMath::Abs(Eye.Y)<176. && FVector::Dist2D(Eye,Mark)<770.;
	const FRoomLights* Hall=Rooms.Find(TEXT("hall"));
	const bool bStoryReady=Has(TEXT("peek_done")) || Has(TEXT("book_done"));
	if (Hall && !Hall->bOn && !bPowerOut && Clock>=Hall->DeadUntil && PendantWakeUntil<0. &&
		bStoryReady && !Has(TEXT("pendant_seen")) && !HasActiveEncounter() && bHall && Wave>.88 &&
		!P->IsInputLocked() && PlayerSees(Mark+FVector(0,0,133),.82f,800.f))
		PendantWakeUntil=Clock+7.;
	if (PendantWakeUntil>=0.)
	{
		if (!Hall || Hall->bOn) PendantWakeUntil=-1.;
		else
		{
			const float Power=(bNear && !bPowerOut && Clock>=Hall->DeadUntil) ? FMath::Clamp(float(PendantWakeUntil-Clock),0.f,1.f) : 0.f;
			PendantBeam->SetVisibility(Power>0.f);
			PendantBeam->SetIntensity(5700.f*Power);
			if (Power==0.f) PendantWakeUntil=-1.;
		}
	}
	const bool bLit = PendantBeam->IsVisible() && PendantBeam->Intensity>1.f;
	if (bNear && !PendantSpill)
	{
		PendantSpill=NewObject<UPointLightComponent>(this);
		PendantSpill->SetupAttachment(HallPendant.Get());
		PendantSpill->SetRelativeLocation(FVector(0.,0.,-90.));
		PendantSpill->SetIntensityUnits(ELightUnits::Lumens);
		PendantSpill->SetAttenuationRadius(250.f);
		PendantSpill->SetLightColor(FLinearColor(1.f,.59f,.26f));
		PendantSpill->SetLightingChannels(true,true,false);
		PendantSpill->SetCastShadows(false);
		PendantSpill->RegisterComponent();
	}
	if (PendantSpill)
	{
		PendantSpill->SetVisibility(bLit && bNear);
		if (bLit && bNear) PendantSpill->SetIntensity(PendantBeam->Intensity*.074f);
	}
	if (bLit!=bPendantLit && PendantBulbSlot!=INDEX_NONE)
	{
		HallPendant->SetMaterial(PendantBulbSlot,bLit ? PendantLit : PendantDark);
		bPendantLit=bLit;
	}
	AWCEntity* H=Her();
	if (bPendantReveal)
	{
		if (!bHall || !bLit || Wave>-.14 || bBusy || P->IsDown())
		{
			if (H) H->Vanish();
			bPendantReveal=false;
			bEventBusy=false;
			Rest(7.f);
		}
	}
	else if (bHall && bLit && H && !H->IsShown() && !HasActiveEncounter() && !ActiveNote.IsValid() &&
		!P->IsInputLocked() && !P->IsDown() && !Has(TEXT("pendant_seen")) && bStoryReady &&
		Wave<=-.40 && LastPendantWave>-.40 && FVector::Dist2D(Eye,Mark)>185. &&
		PlayerSees(Mark+FVector(0.,0.,133.),.82f,800.f))
	{
		H->Appear(Mark,(Eye-Mark).Rotation().Yaw,TEXT("Idle"));
		H->SetFarGlow(0.f);
		H->SetMood(TEXT("watch"));
		bPendantReveal=bEventBusy=true;
		RememberAtCheckpoint(TEXT("pendant_seen"));
		UE_LOG(LogTemp,Display,TEXT("WCPENDANT Edith caught on the downswing"));
	}
	LastPendantWave=Wave;
}
