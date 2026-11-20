#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCWorld.h"
#include "AudioDevice.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/AudioComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Materials/MaterialInterface.h"
#include "GameFramework/PlayerController.h"

DEFINE_LOG_CATEGORY_STATIC(LogCryingDoor, Log, All);

namespace
{
constexpr float CrySeconds = 12.5f;
constexpr float SilenceSeconds = .68f;
constexpr float FaceSeconds = 1.03f;
constexpr float ReleaseSeconds = 1.00f;

AStaticMeshActor* SpawnCompanyMask(UWorld* World, FVector Point, FRotator Facing)
{
	UStaticMesh* Mesh = LoadObject<UStaticMesh>(nullptr,
		TEXT("/Game/WC/Props/HouseDetails/SM_CompanyMask.SM_CompanyMask"));
	if (!Mesh) return nullptr;
	AStaticMeshActor* Mask = World->SpawnActor<AStaticMeshActor>(Point, Facing);
	if (!Mask) return nullptr;
	UStaticMeshComponent* Face = Mask->GetStaticMeshComponent();
	Face->SetMobility(EComponentMobility::Movable);
	Face->SetStaticMesh(Mesh);
	UMaterialInterface* Finish = LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WC/Materials/M_CompanyMask.M_CompanyMask"));
	if (Finish) Face->SetMaterial(0,Finish);
	Face->SetTextureForceResidentFlag(true);
	Face->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Face->SetLightingChannels(true,true,false);

	auto* Smoke = NewObject<UInstancedStaticMeshComponent>(Mask);
	Smoke->SetupAttachment(Face);
	Smoke->SetRelativeLocation(FVector(-33,0,-169));
	Smoke->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Smoke->SetCastShadow(false);
	Smoke->RegisterComponent();
	AWCSmokeMan::Build(Smoke, 184.f, 1953);
	auto* Bounce = NewObject<UPointLightComponent>(Mask);
	Bounce->SetupAttachment(Face);
	Bounce->SetRelativeLocation(FVector(23,-12,13));
	Bounce->SetIntensityUnits(ELightUnits::Lumens);
	Bounce->SetIntensity(7.f);
	Bounce->SetLightColor(FLinearColor(.73f,.78f,.85f));
	Bounce->SetAttenuationRadius(57.f);
	Bounce->SetCastShadows(true);
	Bounce->SetLightingChannels(true,true,false);
	Bounce->RegisterComponent();
	return Mask;
}
}

void AWCDirector::SetDoorSilence(bool bMute)
{
	if (bDoorSilence == bMute) return;
	bDoorSilence = bMute;
	if (FAudioDevice* Device = GetWorld()->GetAudioDeviceRaw())
		Device->SetTransientPrimaryVolume(bMute ? 0.f : 1.f);
}

void AWCDirector::FinishDoorListening(bool bCompleted)
{
	SetDoorSilence(false);
	if (DoorCry.IsValid()) DoorCry->Stop();
	if (DoorWhisper.IsValid()) DoorWhisper->Stop();
	if (DoorMask.IsValid()) DoorMask->Destroy();
	if (DoorPeekCamera.IsValid())
	{
		if (AWCCharacter* P = Player())
		{
			if (APlayerController* PC = Cast<APlayerController>(P->GetController()))
			{
				PC->SetControlRotation(DoorPeekCamera->GetActorRotation());
				PC->SetViewTargetWithBlend(P,.3f,VTBlend_EaseInOut,2.f,true);
			}
			P->SetInputLocked(false);
		}
		DoorPeekCamera->SetLifeSpan(.4f);
	}
	DoorPeekCamera.Reset();
	DoorMask.Reset();
	DoorCry.Reset();
	DoorWhisper.Reset();
	DoorListening = EDoorListening::Idle;
	DoorListenTime = 0.f;
	NextDoorLook = Clock + .6;
	bBusy = false;
	if (!bCompleted) return;

	Set(TEXT("kids_open"));
	DoorOpenedAt = Clock;
	if (AWCDoor* Ruth = Door(TEXT("up_kids"))) Ruth->HoldAtCrack(false);
	PlayAt(TEXT("musicbox"),Pos(TEXT("MusicBoxPoint")),.67f);
	SetObjective(TEXT("Push open Ruth's door. Follow the music box to her bed."));
	Rest(30.f);
	Checkpoint(TEXT("ruth_door"));
	UE_LOG(LogCryingDoor,Display,TEXT("WCJAMB open; route to Ruth's music box available"));
}

void AWCDirector::TickCryingDoor(float Dt)
{
	if (Has(TEXT("kids_open"))) return;
	const bool bReady = Has(TEXT("kids_pending")) || (Has(TEXT("peek_done")) && Has(TEXT("lockin_done")) && Has(TEXT("phone_done")));
	if (!bReady || (DoorListening == EDoorListening::Idle && Clock < NextDoorLook)) return;
	AWCCharacter* P = Player();
	AWCDoor* D = Door(TEXT("up_kids"));
	if (!D || !P) return;
	APlayerController* PC = Cast<APlayerController>(P->GetController());
	if (!PC) return;
	// This leaf is hinged at its west jamb. Use the surveyed closed axes, never the swinging leaf's axes.
	const FVector Along = FVector::ForwardVector, Hall = FVector::RightVector;
	const FVector Hinge = D->GetActorLocation(), Eye = P->EyeLocation();
	const float Height = FMath::Clamp(Eye.Z-Hinge.Z,94.f,158.f);
	const FVector Latch = Hinge + 113.f*Along + FVector::UpVector*Height;
	const FVector At = Latch - 7.f*Along + 9.f*Hall;
	const float Dist = FVector::Dist(Eye,At);
	if (DoorListening == EDoorListening::Idle)
	{
		NextDoorLook = Clock + .16;
		if (HasActiveEncounter() || bDriving || P->IsInputLocked() || P->IsDown() ||
			ActiveNote.IsValid() || Clock < DialogueUntil || !Has(TEXT("inside")) ||
			FMath::Abs(Eye.Z-Latch.Z)>50.f || FVector::DotProduct(Eye-Latch,Hall)<10.f) return;
		if (!Has(TEXT("ruth_door_ajar")))
		{
			if (!D->bLocked || !PlayerSees(At,.82f,760.f)) return;
			PlayAt(TEXT("door_unlock"),At,.93f);
			D->HoldAtCrack(true);
			PlayAt(TEXT("door_creak_long"),At,.79f,.88f);
			Set(TEXT("ruth_door_ajar"));
			DoorOpenedAt = Clock;
			SetObjective(TEXT("A lock turned on the front upstairs landing. Look through the cracked door."));
			Checkpoint(TEXT("ruth_door_ajar"));
			UE_LOG(LogCryingDoor,Display,TEXT("WCJAMB opened in view dot=%.3f range=%.0f"),FVector::DotProduct(P->EyeForward(),(At-Eye).GetSafeNormal()),Dist);
			return;
		}
		if (Clock < DoorOpenedAt+3.2 || Dist>154.f || !PlayerSees(At,.66f,155.f)) return;
		// The latch is 29 cm inside the room at 15 degrees. Keep the entire mask
		// beyond that sweep. The real door leaf and the jamb occlude either cheek.
		DoorMaskPoint = Latch + 16.f*Along - 51.f*Hall;
		DoorPeekPoint = Latch - 46.f*Along + 82.f*Hall;
		const FRotator Facing = (DoorPeekPoint-DoorMaskPoint).Rotation();
		DoorMask = SpawnCompanyMask(GetWorld(),DoorMaskPoint + 65.f*Along - 90.f*Hall,Facing);
		if (!DoorMask.IsValid()) { FinishDoorListening(true); return; }
		bBusy = true;
		DoorListenTime = 0.f;
		DoorListening = EDoorListening::Listening;
		// Two voices start together. Their reflections originate at different points in the room.
		DoorCry = PlayAt(TEXT("door_weeping"),At-Hall*43.f,1.22f);
		DoorWhisper = PlayAt(TEXT("door_whispering"),At-Hall*25.f-Along*28.f,.91f);
		UE_LOG(LogCryingDoor,Display,TEXT("WCJAMB listening t=%.2f crying=%d whisper=%d"),Clock,DoorCry.IsValid(),DoorWhisper.IsValid());
		return;
	}

	DoorListenTime += Dt;
	if (DoorListening == EDoorListening::Listening)
	{
		if (Dist>210.f || P->IsDown() || (P->IsInputLocked() && !DoorPeekCamera.IsValid()))
		{
			FinishDoorListening(false);
			return;
		}
		if (!DoorPeekCamera.IsValid() && DoorListenTime >= CrySeconds - 1.45f)
		{
			if (!PlayerSees(At,.50f,210.f)) { FinishDoorListening(false); return; }
			const FRotator View = (DoorMaskPoint-DoorPeekPoint).Rotation();
			DoorPeekCamera = GetWorld()->SpawnActor<ACameraActor>(DoorPeekPoint,View);
			if (!DoorPeekCamera.IsValid()) { FinishDoorListening(true); return; }
			DoorPeekCamera->GetCameraComponent()->SetFieldOfView(66.f);
			P->SetInputLocked(true);
			PC->SetViewTargetWithBlend(DoorPeekCamera.Get(),.95f,VTBlend_EaseInOut,2.f,true);
		}
		if (DoorListenTime < CrySeconds) return;
		if (DoorCry.IsValid()) DoorCry->Stop();
		if (DoorWhisper.IsValid()) DoorWhisper->Stop();
		SetDoorSilence(true);
		DoorListening = EDoorListening::Silence;
		UE_LOG(LogCryingDoor,Display,TEXT("WCJAMB silence after %.2f seconds"),DoorListenTime);
	}
	const float RevealTime = DoorListenTime - CrySeconds - SilenceSeconds;
	if (RevealTime < 0.f) return;
	if (DoorListening == EDoorListening::Silence)
	{
		SetDoorSilence(false);
		DoorListening = EDoorListening::FaceVisible;
		DoorMask->SetActorLocation(DoorMaskPoint);
		PlayAt(TEXT("door_room_scream"),Latch - 25.f*Along - 182.f*Hall,1.04f);
		UE_LOG(LogCryingDoor,Display,TEXT("WCJAMB face in seam t=%.2f"),Clock);
	}
	if (DoorListening == EDoorListening::FaceVisible)
	{
		if (RevealTime < FaceSeconds) return;
		DoorMask->SetActorHiddenInGame(true);
		DoorListening = EDoorListening::Recover;
		UE_LOG(LogCryingDoor,Display,TEXT("WCJAMB empty seam t=%.2f"),Clock);
	}
	if (RevealTime >= FaceSeconds + ReleaseSeconds) FinishDoorListening(true);
}
