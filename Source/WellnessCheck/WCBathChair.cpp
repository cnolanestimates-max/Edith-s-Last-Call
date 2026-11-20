#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"
#include "GameFramework/Controller.h"
#include "GameFramework/CharacterMovementComponent.h"

namespace
{
	const FVector BathThreshold(2588.,-204.,0.);
}

void AWCDirector::SetBathChairTilt(float Degrees)
{
	if (!BathChair.IsValid()) return;
	// Rotate about the outer wheel's contact patch. Rotating about the actor origin lifts both wheels.
	const FVector Pivot = BathChairHome.TransformPosition(FVector(0.,-31.,0.));
	const FQuat Roll(FVector::ForwardVector,FMath::DegreesToRadians(-Degrees));
	const FVector Loc = Pivot + Roll.RotateVector(BathChairHome.GetLocation()-Pivot);
	BathChair->SetActorLocationAndRotation(Loc,Roll*BathChairHome.GetRotation(),false,nullptr,ETeleportType::TeleportPhysics);
}

void AWCDirector::TickBathChair(float Dt)
{
	if (!BathChair.IsValid() || ChairBeat == EBathChairBeat::Finished) return;
	if (Has(TEXT("bath_chair_done")))
	{
		BathChair->SetActorEnableCollision(false);
		SetBathChairTilt(84.f);
		ChairBeat = EBathChairBeat::Finished;
		return;
	}
	if (!NotesRead.Contains(TEXT("note_bath_mirror")) || ActiveNote.IsValid()) return;
	AWCCharacter* P = Player();
	AWCEntity* H = Her();
	if (!P || !H || !P->GetController()) return;
	const FVector Eye = P->EyeLocation();
	const FVector TowardDoor = (BathThreshold + FVector(0,0,142.) - Eye).GetSafeNormal();
	const FVector ChairCentre = BathChairHome.GetLocation();
	const bool bNearRoom = Eye.Z>40. && Eye.Z<260. && Eye.X>2410. && Eye.X<2785. && Eye.Y>-590. && Eye.Y<-160.;
	const double Age = Clock - ChairBeatAt;
	switch (ChairBeat)
	{
	case EBathChairBeat::Waiting:
		if (!bNearRoom || HasActiveEncounter() || P->IsDown() || P->IsInputLocked() || H->IsShown()) return;
		if (FVector::DotProduct(TowardDoor,P->EyeForward()) < .67 ||
			FVector::DotProduct((ChairCentre+FVector(0,0,56)-Eye).GetSafeNormal(),P->EyeForward()) > .55) return;
		bEventBusy = true;
		ChairBeat = EBathChairBeat::Tipping;
		ChairBeatAt = Clock;
		ChairTurnStart = P->GetController()->GetControlRotation();
		P->SetInputLocked(true);
		P->GetCharacterMovement()->StopMovementImmediately();
		BathChair->SetActorEnableCollision(false);
		if (AWCDoor* DoorLeaf = Door(TEXT("bath_g")); DoorLeaf && !DoorLeaf->IsOpen()) DoorLeaf->OpenAwayFrom(P->GetActorLocation(),.7f);
		PlayAt(TEXT("chair_scrape"),ChairCentre,.83f,.86f,800.f);
		Play2D(TEXT("deputy_pant"),.91f);
		UE_LOG(LogTemp,Display,TEXT("WCBATHCHAIR tip and deputy breath"));
		break;
	case EBathChairBeat::Tipping:
	{
		const float T = FMath::Clamp(float(Age/.60),0.f,1.f);
		const float Degrees = Age < .60 ? 88.f*T*T : 84.f+4.f*FMath::Exp(-8.f*(Age-.60))*FMath::Cos(19.f*(Age-.60));
		SetBathChairTilt(Degrees);
		if (!bChairImpact && Age>=.58)
		{
			bChairImpact = true;
			PlayAt(TEXT("body_fall"),BathChair->GetActorLocation(),1.1f,.92f,1000.f);
			PlayAt(TEXT("chair_creak_01"),ChairCentre,.68f,.79f,650.f);
			P->AddShake(.24f);
		}
		const FVector Focus = ChairCentre+FVector(0.,31.,30.);
		const FRotator Want = (Focus-Eye).Rotation();
		const float Blend = FMath::SmoothStep(.12f,1.02f,float(Age));
		P->GetController()->SetControlRotation(FQuat::Slerp(ChairTurnStart.Quaternion(),Want.Quaternion(),Blend).Rotator());
		if (Age < 1.65) break;
		SetBathChairTilt(84.f);
		H->Appear(BathThreshold+FVector(0.,16.,0.),(P->GetActorLocation()-BathThreshold).Rotation().Yaw,TEXT("Threshold"));
		H->SetFarGlow(0.f);
		H->SetGlow(38.f);
		H->SetMood(TEXT("watch"));
		P->SetInputLocked(false);
		ChairBeatAt = Clock;
		ChairBeat = EBathChairBeat::AtDoor;
		UE_LOG(LogTemp,Display,TEXT("WCBATHCHAIR controls returned; Edith waiting at threshold"));
		break;
	}
	case EBathChairBeat::AtDoor:
	{
		const bool bClose = FVector::Dist2D(P->GetActorLocation(),BathThreshold)<75.;
		const bool bExitingBackwards = bClose && Eye.Y>BathThreshold.Y && P->GetVelocity().Size2D()>20.;
		if (!bNearRoom && Eye.Y>-135. && !bExitingBackwards)
		{
			H->Vanish();
			bEventBusy=false;
			RememberAtCheckpoint(TEXT("bath_chair_done"));
			ChairBeat=EBathChairBeat::Finished;
			break;
		}
		const bool bDiscovered = PlayerSees(H->EyeLocation(),.70f,620.f);
		if (bDiscovered && ChairDoorSeenAt<0.) ChairDoorSeenAt=Clock;
		if (Age < .24 || (!bExitingBackwards && (ChairDoorSeenAt<0. || Clock-ChairDoorSeenAt<.24))) break;
		const FVector Out = (P->GetActorLocation()-H->GetActorLocation()).GetSafeNormal2D();
		ChairLungeFrom=H->EyeLocation();
		ChairLungeTo=Eye-Out*69.+FVector(0.,0.,5.);
		H->SetYaw(Out.Rotation().Yaw);
		H->Play(TEXT("Lunge"),false,1.08f);
		H->SetMood(TEXT("scream"));
		PlayAt(TEXT("her_scream_short_01"),H->HeadLocation(),1.1f,.97f,1200.f);
		P->AddShake(.49f);
		ChairBeatAt = Clock;
		ChairBeat = EBathChairBeat::Lunging;
		UE_LOG(LogTemp,Display,TEXT("WCBATHCHAIR lunge with player control"));
		break;
	}
	case EBathChairBeat::Lunging:
		// Drive the eye, not the root. Her tall rig thrusts its head forward during this clip.
		// Keeping the face just in front of his viewpoint preserves her expression at impact.
		H->SetActorLocation(H->GetActorLocation()+FMath::Lerp(ChairLungeFrom,ChairLungeTo,
			FMath::SmoothStep(0.f,.43f,float(Age)))-H->EyeLocation());
		if (Age<.68) break;
		H->Vanish();
		bEventBusy = false;
		Rest(12.f);
		RememberAtCheckpoint(TEXT("bath_chair_done"));
		ChairBeat = EBathChairBeat::Finished;
		break;
	default: break;
	}
}
