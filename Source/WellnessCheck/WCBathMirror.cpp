#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"
#include "Components/PointLightComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"

namespace
{
	const FVector GlassCentre(2430., -370., 185.8);
	const FVector ApprovedEyeLight(2581.2, -340.0, 153.2);
	constexpr double SeatedScale = 1.25;
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

void AWCDirector::SeatBathReflection()
{
	AWCEntity* Edith = Her();
	if (!Edith || !Edith->Body->GetSkeletalMeshAsset() || Has(TEXT("bath_mirror_seen"))) return;
	const FVector ChairSeat = BathChairHome.GetLocation();
	const FTransform Pose(FRotator(0.,183.,0.), ChairSeat, Edith->GetActorScale3D());
	BathReflection = GetWorld()->SpawnActorDeferred<AWCEntity>(AWCEntity::StaticClass(), Pose, this, nullptr,
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if (!BathReflection) return;
	BathReflection->Anims = Edith->Anims;
	BathReflection->EyeRef = Edith->EyeRef;
	BathReflection->EyeRadius = Edith->EyeRadius;
	BathReflection->HeadBone = Edith->HeadBone;
	BathReflection->Body->SetSkeletalMeshAsset(Edith->Body->GetSkeletalMeshAsset());
	BathReflection->Body->SetRelativeTransform(Edith->Body->GetRelativeTransform());
	UGameplayStatics::FinishSpawningActor(BathReflection, Pose);
	BathReflection->SetActorEnableCollision(false);
	TInlineComponentArray<UPrimitiveComponent*> Parts(BathReflection);
	for (UPrimitiveComponent* Part : Parts)
	{
		Part->SetLightingChannels(false,false,true);
		Part->SetVisibleInSceneCaptureOnly(true);
		Part->SetCastShadow(false);
	}
	BathReflection->Appear(ChairSeat, 183.f, TEXT("Wheelchair"));
	if (BathWrithingSkin) BathReflection->Body->SetMaterial(0, BathWrithingSkin);

	// Scale around the pelvis so the larger pose stays on the real cushion.
	const FVector Hips = BathReflection->BoneWorld(TEXT("Hips"));
	const FVector EyeShift = (BathReflection->EyeLocation()-Hips)*(SeatedScale-1.);
	BathReflection->SetActorScale3D(Pose.GetScale3D()*SeatedScale);
	BathReflection->SetActorLocation(Hips+(ChairSeat-Hips)*SeatedScale);
	BathEyeFill->SetWorldLocation(ApprovedEyeLight+EyeShift);
	BathEyeFill->SetVisibility(true);
	const FVector FillSource = Hips + BathReflection->GetActorForwardVector()*62. -
		BathReflection->GetActorRightVector()*20. + FVector(0,0,77.);
	const FVector FillTarget = Hips + BathReflection->GetActorForwardVector()*10. + FVector(0,0,53.);
	BathTorsoFill->SetWorldLocationAndRotation(FillSource,(FillTarget-FillSource).Rotation());
	BathTorsoFill->SetVisibility(true);
	BathRim->SetLightingChannels(true,true,true);
	BathRim->SetIntensity(145.f);
	BathReflection->SetFarGlow(0.f);
	BathReflection->SetGlow(0.f);
	BathReflection->SetEyeShine(.021f);
	BathReflection->SetMood(TEXT("watch"));
	UE_LOG(LogTemp,Display,TEXT("WCMIRROR seated reflection prepared before first capture"));
}

void AWCDirector::ClearBathReflection()
{
	if (!BathReflection) return;
	BathReflection->Destroy();
	BathReflection = nullptr;
	BathEyeFill->SetVisibility(false);
	BathTorsoFill->SetVisibility(false);
	BathRim->SetLightingChannels(true,true,false);
	BathRim->SetIntensity(1900.f);
	BathTarget->ResizeTarget(BathBaseResolution.X,BathBaseResolution.Y);
	MirrorWitnessSeconds = 0.f;
	NextMirrorCapture = 0.;
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
	BathBaseResolution = FIntPoint(BathTarget->SizeX,BathTarget->SizeY);
	BathWrithingSkin = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Her/M_HerMirror.M_HerMirror"));
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
	BathEyeFill->SetWorldLocation(ApprovedEyeLight);
	BathEyeFill->SetLightingChannels(false,false,true);
	BathEyeFill->SetIntensityUnits(ELightUnits::Candelas);
	BathEyeFill->SetIntensity(9.45f);
	BathEyeFill->SetAttenuationRadius(38.f);
	BathEyeFill->SetLightColor(EdithMoonlight());
	BathEyeFill->SetSpecularScale(.16f);
	BathEyeFill->SetCastShadows(false);
	BathEyeFill->SetVisibility(false);
	BathEyeFill->RegisterComponent();

	// A wider pool of reflected moonlight picks up the abdomen and the folds across her lap.
	BathTorsoFill = NewObject<USpotLightComponent>(this);
	BathTorsoFill->SetLightingChannels(false,false,true);
	BathTorsoFill->SetIntensityUnits(ELightUnits::Candelas);
	BathTorsoFill->SetIntensity(44.f);
	BathTorsoFill->SetAttenuationRadius(116.f);
	BathTorsoFill->SetInnerConeAngle(28.f);
	BathTorsoFill->SetOuterConeAngle(52.f);
	BathTorsoFill->SetSourceRadius(12.f);
	BathTorsoFill->SetSpecularScale(.12f);
	BathTorsoFill->SetLightColor(EdithMoonlight());
	BathTorsoFill->SetCastShadows(false);
	BathTorsoFill->SetVisibility(false);
	BathTorsoFill->RegisterComponent();
	SeatBathReflection();
	if (BathReflection) BathTarget->ResizeTarget(BathBaseResolution.X*2,BathBaseResolution.Y*2);
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
	if (BathReflection) BathReflection->LookAtReflection(FVector(GlassCentre.X-Depth,Eye.Y,Eye.Z));
	BathCapture->CaptureScene();
}

bool AWCDirector::IsInMirrorBathroom(const FVector& Eye)
{
	return Eye.X > 2440 && Eye.X < 2786 && Eye.Y > -583 && Eye.Y < -214 && Eye.Z > 38 && Eye.Z < 270;
}

void AWCDirector::TickBathMirror(float Dt)
{
	AWCCharacter* P = Player();
	if (!P || !BathChair.IsValid() || !BathCapture) return;
	const FVector Eye = P->EyeLocation();
	const FVector Gaze = P->EyeForward();
	const FVector CentreRay = (GlassCentre-Eye).GetSafeNormal();
	const bool bRoom = IsInMirrorBathroom(Eye);
	const bool bFacing = FVector::DotProduct(Gaze,CentreRay) > .10;
	const double Depth = Eye.X-GlassCentre.X;
	if (BathReflection && Has(TEXT("bath_mirror_seen"))) ClearBathReflection();
	if (!bRoom) MirrorWitnessSeconds = 0.f;

	if (bRoom && BathReflection && !P->IsDown() && !P->IsInputLocked() && !ActiveNote.IsValid())
	{
		// Read the two looks while the figure stays seated even when the glass is off screen.
		const FVector Head = BathReflection->EyeLocation();
		const FVector VirtualHead(2.*GlassCentre.X-Head.X,Head.Y,Head.Z);
		const FVector Sight = (VirtualHead-Eye).GetSafeNormal();
		const FVector OnGlass = Eye + Sight * (-Depth/Sight.X);
		const bool bInPane = FMath::Square((OnGlass.Y-GlassCentre.Y)/101.) +
			FMath::Square((OnGlass.Z-178.)/70.) < 1.;
		bool bLookingAtHer = bInPane && FVector::DotProduct(Sight,Gaze) > .86;
		if (bLookingAtHer)
		{
			FHitResult Hit;
			FCollisionQueryParams Query(SCENE_QUERY_STAT(BathMirrorSight),false,P);
			if (GetWorld()->LineTraceSingleByChannel(Hit,Eye,OnGlass+FVector(5.,0.,0.),ECC_Visibility,Query))
			{
				const AWCInteractable* Inspect = Cast<AWCInteractable>(Hit.GetActor());
				bLookingAtHer = (Inspect && Inspect->WCId==TEXT("look_bathg_mirror")) ||
					(Hit.GetActor() && Hit.GetActor()->ActorHasTag(TEXT("BathMirror")));
			}
		}
		if (bLookingAtHer)
		{
			MirrorWitnessSeconds += Dt;
			if (!Has(TEXT("bath_mirror_first_turn")) && !Has(TEXT("bath_mirror_snicker")) &&
				PlayAt(TEXT("VO/edith_snicker_01"), BathReflection->HeadLocation(), .34f))
				RememberAtCheckpoint(TEXT("bath_mirror_snicker"));
		}
		const FVector SeatDirection = (BathChairHome.GetLocation()+FVector(0,0,65)-Eye).GetSafeNormal();
		if (MirrorWitnessSeconds>=.25f && !bFacing && FVector::DotProduct(Gaze,SeatDirection)>.63)
		{
			MirrorWitnessSeconds = 0.f;
			if (!Has(TEXT("bath_mirror_first_turn")))
			{
				RememberAtCheckpoint(TEXT("bath_mirror_first_turn"));
				UE_LOG(LogTemp,Display,TEXT("WCMIRROR first turn: empty physical chair, reflection stays seated"));
			}
			else
			{
				RememberAtCheckpoint(TEXT("bath_mirror_seen"));
				ClearBathReflection();
				RefreshBathLetter();
				Rest(5.f);
				CaptureBathMirror(Eye);
				UE_LOG(LogTemp,Display,TEXT("WCMIRROR second turn: reflection cleared, letter available"));
			}
		}
	}
	// Keep the glass current as it comes into view through the open doorway.
	const bool bApproach = Depth > 2. && Eye.Z>30. && Eye.Z<285. &&
		FVector::DistSquared(Eye,GlassCentre)<FMath::Square(660.);
	if (!bApproach || Clock < NextMirrorCapture || FVector::DotProduct(Gaze,CentreRay)<-.25) return;
	NextMirrorCapture = Clock + (BathReflection ? 1./20. : 1./16.);
	CaptureBathMirror(Eye);
}
