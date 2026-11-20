#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"
#include "Components/AudioComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Materials/MaterialInterface.h"

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
		TInlineComponentArray<UPrimitiveComponent*> Parts(H);
		for (UPrimitiveComponent* Part : Parts)
		{
			if (const FLightingChannels* Saved = MirrorMeshChannels.Find(Part))
				Part->SetLightingChannels(Saved->bChannel0,Saved->bChannel1,Saved->bChannel2);
			Part->bVisibleInSceneCaptureOnly = false;
			Part->MarkRenderStateDirty();
		}
		MirrorMeshChannels.Reset();
	}
	if (BathRim) BathRim->SetIntensity(1900.f);
	if (BathEyeFill) BathEyeFill->SetVisibility(false);
	MirrorShownAt = -1.;
	MirrorDwell = 0.f;
	MirrorWitnessSeconds = 0.f;
	NextMirrorCapture = 0.;
	bEventBusy = false;
	if (bWitnessed && !Has(TEXT("bath_mirror_first_turn")))
	{
		RememberAtCheckpoint(TEXT("bath_mirror_first_turn"));
		UE_LOG(LogTemp,Display,TEXT("WCMIRROR first turn: empty chair"));
	}
	else if (bWitnessed)
	{
		RememberAtCheckpoint(TEXT("bath_mirror_seen"));
		RefreshBathLetter();
		Rest(5.f);
		UE_LOG(LogTemp, Display, TEXT("WCMIRROR chair empty, letter available"));
	}
}

void AWCDirector::InitializeBathMirror()
{
	if (BathCapture || !BathChair.IsValid()) return;
	AActor* Frame=Find(TEXT("BathMirror"));
	if (!Frame) return;
	BathGlass=Frame->FindComponentByClass<UStaticMeshComponent>();
	if (!BathGlass.IsValid() || !BathGlass->GetMaterial(1)) return;
	// Use the texture actually bound to the glass in the house map, from its very first frame.
	UTexture* Reflect=nullptr;
	BathGlass->GetMaterial(1)->GetTextureParameterValue(FMaterialParameterInfo(TEXT("Reflect")),Reflect);
	BathTarget=Cast<UTextureRenderTarget2D>(Reflect);
	if (!ensureMsgf(BathTarget,TEXT("Bathroom glass has no authored render target"))) return;
	const FVector ChairSeat=BathChairHome.GetLocation();
	BathCapture = NewObject<USceneCaptureComponent2D>(this);
	BathCapture->bCaptureEveryFrame = BathCapture->bCaptureOnMovement = false;
	BathCapture->bAlwaysPersistRenderingState = true;
	BathCapture->TextureTarget = BathTarget;
	BathCapture->CaptureSource = ESceneCaptureSource::SCS_SceneColorHDR;
	BathCapture->bUseCustomProjectionMatrix = true;
	BathCapture->HiddenActors.Add(Frame);
	if (AWCCharacter* P=Player()) BathCapture->HiddenActors.Add(P);
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

	// The same moon blue as the upstairs doorway, grazing the good eye and the jaw below it.
	BathEyeFill = NewObject<UPointLightComponent>(this);
	BathEyeFill->SetLightingChannels(false,false,true);
	BathEyeFill->SetIntensityUnits(ELightUnits::Candelas);
	BathEyeFill->SetIntensity(2.8f);
	BathEyeFill->SetAttenuationRadius(38.f);
	BathEyeFill->SetLightColor(EdithMoonlight());
	BathEyeFill->SetSpecularScale(.16f);
	BathEyeFill->SetCastShadows(false);
	BathEyeFill->SetVisibility(false);
	BathEyeFill->RegisterComponent();
	CaptureBathMirror(FVector(2588.,-170.,155.));
}

void AWCDirector::CaptureBathMirror(const FVector& Eye)
{
	const double Depth=Eye.X-GlassCentre.X;
	if (!BathCapture || Depth<=2.) return;
	// Off-axis frustum through the four corners of the real glass. Depth also clips the wall behind it.
	BathCapture->SetWorldLocationAndRotation(FVector(GlassCentre.X-Depth,Eye.Y,Eye.Z), FRotator::ZeroRotator);
	BathCapture->CustomProjectionMatrix = FMatrix(FPlane(Depth/HalfWidth,0,0,0),FPlane(0,Depth/HalfHeight,0,0),
		FPlane((Eye.Y-GlassCentre.Y)/HalfWidth,(Eye.Z-GlassCentre.Z)/HalfHeight,0,1),FPlane(0,0,Depth+.4,0));
	BathCapture->CaptureScene();
}

void AWCDirector::TickBathMirror(float Dt)
{
	AWCCharacter* P = Player();
	if (!P) return;
	const FVector Eye = P->EyeLocation();
	const bool bRoom = Eye.X > 2440 && Eye.X < 2786 && Eye.Y > -583 && Eye.Y < -214 && Eye.Z > 38 && Eye.Z < 270;
	if (!BathChair.IsValid() || !BathCapture) return;
	if (!bRoom || Has(TEXT("bath_mirror_seen")))
	{
		if (BathEdithBreath.IsValid()) BathEdithBreath->FadeOut(.18f,0.f);
		BathEdithBreath.Reset();
		NextBathBreath=0.;
	}
	else if (Clock>=NextBathBreath && (!BathEdithBreath.IsValid() || !BathEdithBreath->IsPlaying()))
	{
		BathEdithBreath=PlayAt(TEXT("her_breath"),BathChairHome.GetLocation()+FVector(0,0,112),.92f,.92f,1300.f);
		NextBathBreath=Clock+6.9;
	}
	const FVector Gaze=P->EyeForward();
	if (!bRoom)
	{
		FinishBathMirror(false);
		MirrorDwell=0.f;
		// Keep the reflection live on the hallway approach without drawing the bathroom across the house.
		if (Clock>=NextMirrorCapture && Eye.Z>30. && Eye.Z<285. && Eye.X>GlassCentre.X+2. &&
			FVector::DistSquared(Eye,GlassCentre)<FMath::Square(730.) &&
			FVector::DotProduct(Gaze,(GlassCentre-Eye).GetSafeNormal())>-.1)
		{
			CaptureBathMirror(Eye);
			NextMirrorCapture=Clock+1./16.;
		}
		return;
	}
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
	const FVector SeatDirection=(ChairSeat+FVector(0,0,65)-Eye).GetSafeNormal();
	const bool bTurnedToChair=!bFacing && FVector::DotProduct(Gaze,SeatDirection)>.63;
	if (MirrorShownAt>=0. && (bTurnedToChair || bBusy || P->IsDown()))
		FinishBathMirror(bTurnedToChair && !bBusy && !P->IsDown() && MirrorWitnessSeconds>=.4f);
	if (!bFacing) { MirrorDwell=0.f; return; }
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
				MirrorMeshChannels.Add(Part,Part->LightingChannels);
				Part->SetLightingChannels(false,false,true);
				Part->bVisibleInSceneCaptureOnly = true;
				Part->MarkRenderStateDirty();
			}
			H->Appear(ChairSeat, 183.f, TEXT("Wheelchair"));
			BathRim->SetLightingChannels(true,true,true);
			BathRim->SetIntensity(Has(TEXT("bath_mirror_first_turn")) ? 175.f : 145.f);
			H->SetFarGlow(0.f);
			H->SetGlow(0.f);
			H->SetEyeShine(.018f);
			H->SetMood(TEXT("watch"));
			MirrorShownAt = Clock;
			NextMirrorCapture = 0.;
			bEventBusy = true;
			UE_LOG(LogTemp, Display, TEXT("WCMIRROR reflection seated, appearance %d"),Has(TEXT("bath_mirror_first_turn")) ? 2 : 1);
		}
	}
	else MirrorDwell = 0.f;
	if (MirrorShownAt>=0. && Her())
	{
		Her()->LookAtReflection(FVector(GlassCentre.X-Depth,Eye.Y,Eye.Z));
		const AWCEntity* H = Her();
		BathEyeFill->SetWorldLocation(H->EyeLocation() + H->GetActorForwardVector()*16. -
			H->GetActorRightVector()*17. - FVector(0,0,9));
		BathEyeFill->SetVisibility(true);
	}
	if (Clock < NextMirrorCapture) return;
	NextMirrorCapture = Clock + 1./16.;
	CaptureBathMirror(Eye);
}
