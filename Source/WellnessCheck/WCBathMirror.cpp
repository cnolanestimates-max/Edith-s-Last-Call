#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"
#include "Components/PointLightComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Materials/MaterialInstanceDynamic.h"

namespace
{
	const FVector GlassCentre(2430., -370., 185.8);
	constexpr double HalfWidth = 130., HalfHeight = 88.8;
}

void AWCDirector::RefreshBathLetter()
{
	if (AWCInteractable* Note = Thing(TEXT("note_bath_mirror")))
	{
		const bool bAvailable = Has(TEXT("bath_mirror_seen")) && !NotesRead.Contains(Note->WCId);
		Note->SetActorHiddenInGame(!bAvailable);
		Note->SetActorEnableCollision(bAvailable);
		Note->bEnabled = bAvailable;
	}
}

void AWCDirector::FinishBathMirror(bool bWitnessed)
{
	if (MirrorShownAt < 0.) return;
	if (AWCEntity* H = Her())
	{
		H->Vanish();
		H->Body->SetLightingChannels(MirrorBodyChannels.bChannel0,MirrorBodyChannels.bChannel1,MirrorBodyChannels.bChannel2);
		TInlineComponentArray<UPrimitiveComponent*> Parts(H);
		for (UPrimitiveComponent* Part : Parts)
		{
			Part->bVisibleInSceneCaptureOnly = false;
			Part->MarkRenderStateDirty();
		}
	}
	if (BathRim) BathRim->SetIntensity(1900.f);
	MirrorShownAt = -1.;
	MirrorDwell = 0.f;
	MirrorWitnessSeconds = 0.f;
	NextMirrorCapture = 0.;
	bEventBusy = false;
	if (bWitnessed)
	{
		RememberAtCheckpoint(TEXT("bath_mirror_seen"));
		RefreshBathLetter();
		Rest(5.f);
		UE_LOG(LogTemp, Display, TEXT("WCMIRROR chair empty, letter available"));
	}
}

void AWCDirector::TickBathMirror(float Dt)
{
	AWCCharacter* P = Player();
	if (!P) return;
	const FVector Eye = P->EyeLocation();
	const bool bRoom = Eye.X > 2440 && Eye.X < 2786 && Eye.Y > -583 && Eye.Y < -214 && Eye.Z > 38 && Eye.Z < 270;
	if (!bRoom)
	{
		if (BathBounce) BathBounce->SetVisibility(false);
		if (BathRim) BathRim->SetVisibility(false);
		FinishBathMirror(false);
		MirrorDwell = 0.f;
		return;
	}
	const FVector Gaze = P->EyeForward();
	if (!BathChair.IsValid()) return;
	const FVector ChairSeat = BathChairHome.GetLocation();
	const double Depth = Eye.X - GlassCentre.X;
	const FVector CentreRay = (GlassCentre - Eye).GetSafeNormal();
	// Her reflected head is behind the glass at the same depth as the real tub.
	const FVector VirtualHead(2.*GlassCentre.X-ChairSeat.X, ChairSeat.Y, 171.);
	const FVector Sight = (VirtualHead - Eye).GetSafeNormal();
	const FVector OnGlass = Eye + Sight * (-Depth / Sight.X);
	// The reflective oval sits inside the wider rectangle occupied by the gilt frame.
	const bool bInPane = FMath::Square((OnGlass.Y-GlassCentre.Y)/101.) + FMath::Square((OnGlass.Z-178.)/70.) < 1.;
	const bool bFacing = FVector::DotProduct(Gaze, CentreRay) > .10;
	bool bLookingAtHer = bInPane && FVector::DotProduct(Sight,Gaze) > .86;
	if (bLookingAtHer && !Has(TEXT("bath_mirror_seen")))
	{
		FHitResult Hit;
		FCollisionQueryParams Query(SCENE_QUERY_STAT(BathMirrorSight),false,P);
		if (GetWorld()->LineTraceSingleByChannel(Hit,Eye,OnGlass+FVector(5.,0.,0.),ECC_Visibility,Query))
		{
			const AWCInteractable* Inspect=Cast<AWCInteractable>(Hit.GetActor());
			bLookingAtHer = (Inspect && Inspect->WCId==TEXT("look_bathg_mirror")) ||
				(Hit.GetActor() && Hit.GetActor()->ActorHasTag(TEXT("BathMirror")));
		}
	}
	if (MirrorShownAt>=0. && bLookingAtHer) MirrorWitnessSeconds+=Dt;
	if (MirrorShownAt >= 0. && (!bFacing || Gaze.X > .15 || bBusy || P->IsDown()))
		FinishBathMirror(!bBusy && !P->IsDown() && MirrorWitnessSeconds>=.5f);
	if (!bFacing) { MirrorDwell=0.f; return; }
	if (!BathTarget)
	{
		AActor* Frame = Find(TEXT("BathMirror"));
		if (!Frame) return;
		BathGlass = Frame->FindComponentByClass<UStaticMeshComponent>();
		if (!BathGlass.IsValid()) return;
		UMaterialInstanceDynamic* Silver = BathGlass->CreateDynamicMaterialInstance(1);
		if (!Silver) return;
		BathTarget = NewObject<UTextureRenderTarget2D>(this);
		BathTarget->RenderTargetFormat = RTF_RGBA16f;
		BathTarget->InitAutoFormat(640, 440);
		BathTarget->UpdateResourceImmediate(true);
		Silver->SetTextureParameterValue(TEXT("Reflect"), BathTarget);
		BathCapture = NewObject<USceneCaptureComponent2D>(this);
		BathCapture->bCaptureEveryFrame = BathCapture->bCaptureOnMovement = false;
		BathCapture->bAlwaysPersistRenderingState = true;
		BathCapture->TextureTarget = BathTarget;
		BathCapture->CaptureSource = ESceneCaptureSource::SCS_SceneColorHDR;
		BathCapture->bUseCustomProjectionMatrix = true;
		BathCapture->HiddenActors.Add(Frame);
		BathCapture->HiddenActors.Add(P);
		BathCapture->PostProcessSettings.bOverride_AutoExposureMethod = true;
		BathCapture->PostProcessSettings.AutoExposureMethod = EAutoExposureMethod::AEM_Manual;
		BathCapture->PostProcessSettings.bOverride_AutoExposureBias = true;
		BathCapture->PostProcessSettings.AutoExposureBias = -1.f;
		BathCapture->ShowFlags.SetMotionBlur(false);
		BathCapture->ShowFlags.SetVolumetricFog(false);
		BathCapture->RegisterComponent();
		// A little cold bounce on the bath wall gives the glass depth with the room switch off.
		BathBounce = NewObject<UPointLightComponent>(this);
		BathBounce->SetWorldLocation(ChairSeat+FVector(-83.,-49.,165.));
		// The bathroom and chair keep their fill; the seated apparition only catches the rim.
		BathBounce->SetLightingChannels(false,true,false);
		BathBounce->SetAttenuationRadius(295.f);
		BathBounce->SetIntensityUnits(ELightUnits::Lumens);
		BathBounce->SetIntensity(4200.f);
		BathBounce->SetLightColor(FLinearColor(.54f,.68f,.76f));
		BathBounce->SetCastShadows(false);
		BathBounce->RegisterComponent();
		BathRim = NewObject<UPointLightComponent>(this);
		BathRim->SetWorldLocation(ChairSeat + FVector(25.,74.,111.));
		BathRim->SetLightingChannels(true,true,false);
		BathRim->SetAttenuationRadius(225.f);
		BathRim->SetIntensityUnits(ELightUnits::Lumens);
		BathRim->SetIntensity(1900.f);
		BathRim->SetLightColor(FLinearColor(.84f,.66f,.47f));
		BathRim->SetCastShadows(false);
		BathRim->RegisterComponent();
	}
	BathBounce->SetVisibility(true);
	BathRim->SetVisibility(true);
	if (!Has(TEXT("bath_mirror_seen")) && MirrorShownAt < 0. && !HasActiveEncounter() &&
		!P->IsDown() && !P->IsInputLocked() && !ActiveNote.IsValid() && Her() && !Her()->IsShown() && bLookingAtHer)
	{
		MirrorDwell += Dt;
		if (MirrorDwell >= .22f)
		{
			AWCEntity* H = Her();
			TInlineComponentArray<UPrimitiveComponent*> Parts(H);
			for (UPrimitiveComponent* Part : Parts)
			{
				Part->bVisibleInSceneCaptureOnly = true;
				Part->MarkRenderStateDirty();
			}
			H->Appear(ChairSeat, 183.f, TEXT("Wheelchair"));
			MirrorBodyChannels = H->Body->LightingChannels;
			H->Body->SetLightingChannels(false,false,true);
			BathRim->SetLightingChannels(true,true,true);
			BathRim->SetIntensity(145.f);
			H->SetFarGlow(0.f);
			H->SetGlow(0.f);
			H->SetEyeShine(.018f);
			H->SetMood(TEXT("watch"));
			MirrorShownAt = Clock;
			NextMirrorCapture = 0.;
			bEventBusy = true;
			UE_LOG(LogTemp, Display, TEXT("WCMIRROR reflection seated"));
		}
	}
	else MirrorDwell = 0.f;
	if (MirrorShownAt >= 0. && Her()) Her()->LookAtReflection(FVector(GlassCentre.X-Depth,Eye.Y,Eye.Z));
	if (Clock < NextMirrorCapture) return;
	NextMirrorCapture = Clock + 1./16.;
	// Off-axis frustum through the four corners of the real glass. Depth also clips the wall behind it.
	BathCapture->SetWorldLocationAndRotation(FVector(GlassCentre.X-Depth,Eye.Y,Eye.Z), FRotator::ZeroRotator);
	BathCapture->CustomProjectionMatrix = FMatrix(FPlane(Depth/HalfWidth,0,0,0),FPlane(0,Depth/HalfHeight,0,0),
		FPlane((Eye.Y-GlassCentre.Y)/HalfWidth,(Eye.Z-GlassCentre.Z)/HalfHeight,0,1),FPlane(0,0,Depth+.4,0));
	BathCapture->CaptureScene();
}
