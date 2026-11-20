#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCWorld.h"
#include "Components/AudioComponent.h"
#include "GameFramework/PlayerController.h"
#include "Components/SplineComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"

namespace
{
	// The westward run follows the return route through the rear hall, clear of the den doorway.
	constexpr float RearRadius=31.8f, CasterRadius=5.f, CoastDuration=10.5f;
	const FVector Mouth(2588.,-200.,0.);

	FTransform BaseboardContact(UWorld* World, AActor* Chair, APawn* Player, double WallX)
	{
		const FRotator Facing(0.,-135.,0.);
		// The front quadrant of the right main wheel touches first. Measure against the actual trim.
		const FVector LeadingEdge=Facing.RotateVector(FVector(32.3,31.6,31.8));
		FVector Contact(WallX,-183.,31.8);
		FHitResult Hit;
		FCollisionQueryParams Query(SCENE_QUERY_STAT(ChairBaseboard),false,Chair);
		Query.AddIgnoredActor(Player);
		if (World->LineTraceSingleByChannel(Hit,FVector(WallX,-98,31.8),FVector(WallX,-225,31.8),ECC_Visibility,Query))
			Contact=Hit.ImpactPoint;
		return FTransform(Facing,Contact-LeadingEdge);
	}
	bool CanSeeChair(AWCCharacter* Deputy, AActor* Chair, const FTransform& Home)
	{
		APlayerController* PC=Cast<APlayerController>(Deputy->GetController());
		if (!PC) return true;
		const FVector Eye=Deputy->EyeLocation();
		FCollisionQueryParams Query(SCENE_QUERY_STAT(BathChairSight),false,Deputy);
		Query.AddIgnoredActor(Chair);
		int32 Width=0,Height=0;
		PC->GetViewportSize(Width,Height);
		// Test the seat, back corners and wheels in both poses before letting it right itself.
		const FVector Samples[]={FVector(0,0,45),FVector(-23,29,95),FVector(-23,-29,95),
			FVector(26,28,16),FVector(26,-28,16),FVector(0,31,54),FVector(0,-31,54)};
		for (const FTransform& Pose : {Chair->GetActorTransform(),Home})
		{
			for (const FVector& Local : Samples)
			{
				const FVector Point=Pose.TransformPosition(Local);
				FVector2D Pixel;
				const bool InView=(Width>0 && Height>0) ?
					PC->ProjectWorldLocationToScreen(Point,Pixel) && Pixel.X>=-8 && Pixel.X<=Width+8 && Pixel.Y>=-8 && Pixel.Y<=Height+8 :
					FVector::DotProduct(Deputy->EyeForward(),(Point-Eye).GetSafeNormal())>.45;
				if (InView && !Chair->GetWorld()->LineTraceTestByChannel(Eye,Point,ECC_Visibility,Query)) return true;
			}
		}
		return false;
	}
}

bool AWCDirector::PrepareRollingChair()
{
	AActor* Chair=BathChair.Get();
	UStaticMeshComponent* Frame=Chair->FindComponentByClass<UStaticMeshComponent>();
	if (!Frame || !Frame->GetStaticMesh()) return false;
	const TCHAR* Names[]={TEXT("Frame"),TEXT("RightWheel"),TEXT("LeftWheel"),TEXT("Caster")};
	UStaticMesh* Parts[4]={};
	for (int32 i=0;i<4;++i)
	{
		const FString Asset=FString(TEXT("SM_BathChair"))+Names[i];
		Parts[i]=LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/WC/Props/HouseDetails/%s.%s"),*Asset,*Asset));
		if (!Parts[i]) return false;
	}
	// Preserve the map's weathered material overrides as the intact chair becomes articulated.
	TMap<FName,UMaterialInterface*> Finishes;
	const auto& OriginalSlots=Frame->GetStaticMesh()->GetStaticMaterials();
	for (int32 i=0;i<OriginalSlots.Num();++i)
		if (OriginalSlots[i].MaterialInterface) Finishes.Add(OriginalSlots[i].MaterialInterface->GetFName(),Frame->GetMaterial(i));
	auto Fit=[&Finishes](UStaticMeshComponent* Component,UStaticMesh* Part)
	{
		Component->EmptyOverrideMaterials();
		Component->SetStaticMesh(Part);
		const auto& Slots=Part->GetStaticMaterials();
		for (int32 i=0;i<Slots.Num();++i)
			if (auto* Mat=Finishes.Find(Slots[i].MaterialSlotName)) Component->SetMaterial(i,*Mat);
	};
	Fit(Frame,Parts[0]);
	Chair->SetActorEnableCollision(false);
	const FVector Axles[]={FVector(.5,30.,31.8),FVector(.5,-30.,31.8),FVector(30.5,25.,6.8),FVector(30.5,-25.,6.8)};
	for (int32 i=0;i<4;++i)
	{
		auto* Wheel=NewObject<UStaticMeshComponent>(Chair);
		Chair->AddInstanceComponent(Wheel);
		Wheel->SetupAttachment(Frame);
		Wheel->SetRelativeLocation(Axles[i]);
		Wheel->SetMobility(EComponentMobility::Movable);
		Wheel->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Wheel->SetCanEverAffectNavigation(false);
		Wheel->SetLightingChannels(Frame->LightingChannels.bChannel0,Frame->LightingChannels.bChannel1,Frame->LightingChannels.bChannel2);
		Fit(Wheel,Parts[FMath::Min(i+1,3)]);
		Wheel->RegisterComponent();
		ChairWheels[i]=Wheel;
	}

	ChairWallPose=BaseboardContact(GetWorld(),Chair,Player(),1120.);
	return true;
}

void AWCDirector::BuildChairRail(bool bEastbound)
{
	ChairRail=NewObject<USplineComponent>(this);
	ChairRail->SetAbsolute(true,true,true);
	ChairRail->ClearSplinePoints(false);
	auto Knot=[this](FVector Point,FVector Tangent)
	{
		const int32 Index=ChairRail->GetNumberOfSplinePoints();
		ChairRail->AddSplinePoint(Point,ESplineCoordinateSpace::World,false);
		ChairRail->SetTangentsAtSplinePoint(Index,Tangent,Tangent,ESplineCoordinateSpace::World,false);
	};
	Knot(BathChairHome.GetLocation(),BathChairHome.GetRotation().GetForwardVector()*62.);
	Knot(FVector(2588,-279,0),FVector(0,91,0));
	Knot(FVector(2588,-153,0),FVector(-5,114,0));
	if (bEastbound)
	{
		// Sweep beside a player heading for the back door before turning into the long hallway.
		Knot(FVector(2654,-65,0),FVector(90,60,0));
		Knot(FVector(2723,14,0),FVector(5,100,0));
		Knot(FVector(2650,80,0),FVector(-110,12,0));
	}
	else Knot(FVector(2528,-34,0),FVector(-121,65,0));
	Knot(FVector(2380,5,0),FVector(-175,0,0));
	Knot(FVector(1970,6,0),FVector(-240,-5,0));
	Knot(FVector(1600,0,0),FVector(-210,0,0)); // centre of the narrow hall arch
	Knot(FVector(1370,-8,0),FVector(-170,-12,0));
	Knot(FVector(1200,-63,0),FVector(-115,-80,0));
	Knot(ChairWallPose.GetLocation(),ChairWallPose.GetRotation().GetForwardVector()*105.);
	ChairRail->UpdateSpline();
}

void AWCDirector::SpinChairWheel(int32 Wheel,float Radians,float CasterYaw)
{
	WheelRadians[Wheel]+=Radians;
	if (!ChairWheels[Wheel].IsValid()) return;
	const bool bCaster=Wheel>=2;
	const FQuat Spin(bCaster ? FVector::ForwardVector : FVector::RightVector,WheelRadians[Wheel]);
	const FQuat Swivel(FVector::UpVector,bCaster ? FMath::DegreesToRadians(CasterYaw) : 0.f);
	ChairWheels[Wheel]->SetRelativeRotation(Swivel*Spin);
}

void AWCDirector::PoseFallenChair(const FTransform& Upright, float Degrees)
{
	// Roll about the left tyre's floor contact. The right wheel ends up on top.
	const FVector Pivot=Upright.TransformPosition(FVector(.5,-31.6,0.));
	const FQuat Tilt(Upright.GetRotation().GetForwardVector(),FMath::DegreesToRadians(Degrees));
	BathChair->SetActorLocationAndRotation(Pivot+Tilt.RotateVector(Upright.GetLocation()-Pivot),
		Tilt*Upright.GetRotation(),false,nullptr,ETeleportType::TeleportPhysics);
}

FVector AWCDirector::RollingChairPathPoint(float Distance) const
{
	const auto Space=ESplineCoordinateSpace::World;
	const FVector Base=ChairRail->GetLocationAtDistanceAlongSpline(Distance,Space);
	if (Distance<=ChairBypassStart || Distance>=ChairBypassEnd) return Base;
	const float Weight=Distance<ChairBypassMiddle
		? FMath::SmoothStep(ChairBypassStart,ChairBypassMiddle,Distance)
		: 1.f-FMath::SmoothStep(ChairBypassMiddle,ChairBypassEnd,Distance);
	const FVector Cross=FVector::CrossProduct(FVector::UpVector,ChairRail->GetDirectionAtDistanceAlongSpline(Distance,Space));
	return Base+Cross*(Weight*ChairBypassOffset);
}

void AWCDirector::TickBathChair(float Dt)
{
	if (!BathChair.IsValid() || ChairBeat==EBathChairBeat::Finished) return;
	AWCCharacter* P=Player();
	if (!P) return;
	const FVector Deputy=P->GetActorLocation();
	AActor* Chair=BathChair.Get();
	const double Age=Clock-ChairBeatAt;
	switch (ChairBeat)
	{
	case EBathChairBeat::Waiting:
		if (Has(TEXT("bath_chair_rolled")))
		{
			ChairWallPose=BaseboardContact(GetWorld(),Chair,P,Has(TEXT("bath_chair_long_roll")) ? 1120. : 2040.);
			Chair->SetActorEnableCollision(false);
			PoseFallenChair(ChairWallPose,88.f);
			ChairBeat=EBathChairBeat::Finished;
			return;
		}
		if (!NotesRead.Contains(TEXT("note_bath_mirror")) || ActiveNote.IsValid() || Deputy.Z<35. || Deputy.Z>190.) return;
		if (Deputy.X>2414. && Deputy.X<2786. && Deputy.Y>-590. && Deputy.Y<Mouth.Y-75.) bChairExitArmed=true;
		if (!Has(TEXT("bath_chair_exit_tip")) && (!bChairExitArmed || Deputy.Y<Mouth.Y-65. ||
			Deputy.Y>Mouth.Y+60. || FMath::Abs(Deputy.X-Mouth.X)>76.)) return;
		if (P->IsInputLocked() || P->IsDown() || HasActiveEncounter()) return;
		if (!PrepareRollingChair())
		{
			UE_LOG(LogTemp,Error,TEXT("WCBATHCHAIR missing articulated chair assets"));
			ChairBeat=EBathChairBeat::Finished;
			return;
		}
		ChairBeatAt=Clock;
		if (Has(TEXT("bath_chair_exit_tip")))
		{
			PoseFallenChair(BathChairHome,88.f);
			ChairBeat=EBathChairBeat::WaitingForLookAway;
			return;
		}
		ChairBeat=EBathChairBeat::RoomTipping;
		bEventBusy=true;
		UE_LOG(LogTemp,Display,TEXT("WCBATHCHAIR room tip at exit %s"),*Deputy.ToCompactString());
		return;
	case EBathChairBeat::RoomTipping:
	{
		const float T=FMath::Clamp(float(Age/.64),0.f,1.f);
		PoseFallenChair(BathChairHome,88.f*T*T);
		if (T<1.f) return;
		PlayAt(TEXT("wheel_sidefall"),Chair->GetActorLocation(),.82f,.93f,1200.f);
		RememberAtCheckpoint(TEXT("bath_chair_exit_tip"));
		bEventBusy=false;
		ChairBeat=EBathChairBeat::WaitingForLookAway;
		ChairBeatAt=Clock;
		return;
	}
	case EBathChairBeat::WaitingForLookAway:
		// The deputy and capsule must clear the threshold. Re-entering or glancing back restarts the wait.
		if (Deputy.Y<Mouth.Y+38. || Deputy.Y>182. || Deputy.X<1180. || Deputy.X>2790. ||
			Deputy.Z<35. || Deputy.Z>190. || P->IsInputLocked() || P->IsDown() || HasActiveEncounter() ||
			CanSeeChair(P,Chair,BathChairHome))
		{
			ChairBeatAt=Clock;
			return;
		}
		if (Age<.38) return;
		BuildChairRail(Deputy.X>Mouth.X+75. || (Deputy.X>Mouth.X-45. && P->EyeForward().X>.45));
		Chair->SetActorTransform(BathChairHome);
		bEventBusy=true;
		ChairBeatAt=Clock;
		ChairBeat=EBathChairBeat::Rolling;
		UE_LOG(LogTemp,Display,TEXT("WCBATHCHAIR released unseen at %s, route %.0f cm"),*Deputy.ToCompactString(),ChairRail->GetSplineLength());
		ChairRollSound=PlayAt(TEXT("wheel_on_boards"),Chair->GetActorLocation()+FVector(0,0,17),.40f,.73f,1100.f);
		if (ChairRollSound.IsValid()) ChairRollSound->AttachToComponent(Chair->GetRootComponent(),FAttachmentTransformRules::KeepWorldTransform);
		return;
	case EBathChairBeat::Rolling:
	{
		const float Length=ChairRail->GetSplineLength();
		const FVector Here=Chair->GetActorLocation();
		const auto Space=ESplineCoordinateSpace::World;
		const FVector Ahead=(RollingChairPathPoint(ChairTravel+2.f)-RollingChairPathPoint(ChairTravel-2.f)).GetSafeNormal2D();
		const FVector Offset=Deputy-Here;
		const float Forward=FVector::DotProduct(Offset,Ahead);
		const float Side=FMath::Abs(FVector::CrossProduct(Ahead,Offset).Z);
		// Once clear of the narrow doorway, choose a lane around a listener who stops in its path.
		// Commit to the arc so the chair doesn't jitter or keep following their flashlight.
		if (ChairTravel>195.f && ChairTravel>=ChairBypassEnd && FMath::Abs(Offset.Z)<165. &&
			Forward>15.f && Forward<203.f && Side<98.f)
		{
			const float Middle=ChairRail->GetDistanceAlongSplineAtLocation(Deputy,Space);
			const FVector Mid=ChairRail->GetLocationAtDistanceAlongSpline(Middle,Space);
			const FVector Across=FVector::CrossProduct(FVector::UpVector,ChairRail->GetDirectionAtDistanceAlongSpline(Middle,Space));
			const float Lateral=FVector::DotProduct(Deputy-Mid,Across);
			if (FMath::Abs(Mid.X-1600.)>170. && Middle>ChairTravel+25.f && Middle<Length-52.f && FMath::Abs(Lateral)<75.f)
			{
				float Margin=Lateral>0.f ? -89.f : 89.f;
				if (FMath::Abs((Mid+Across*(Lateral+Margin)).Y)>123.f) Margin=-Margin;
				ChairBypassOffset=Lateral+Margin;
				ChairBypassStart=ChairTravel;
				ChairBypassMiddle=Middle;
				ChairBypassEnd=FMath::Min(Length,Middle+155.f);
			}
		}
		// Build enough speed to draw level even when the deputy hurries away.
		float Speed=FMath::Lerp(95.f,218.f,FMath::SmoothStep(0.f,200.f,ChairTravel));
		if (Forward>160.f) Speed+=38.f*FMath::SmoothStep(160.f,420.f,Forward);
		if (FMath::Abs(Offset.Z)<165. && Side<57. && Forward>0. && Forward<105.)
			Speed*=FMath::SmoothStep(59.f,105.f,Forward);
		if (ChairTravel<250.f)
			if (AWCDoor* Leaf=Door(TEXT("bath_g")); Leaf && !Leaf->IsOpen()) Leaf->SetOpen(true,.75f,true);
		ChairSpeed=FMath::FInterpConstantTo(ChairSpeed,Speed,Dt,Speed<ChairSpeed ? 390.f : 210.f);
		const float Distance=FMath::Min(ChairSpeed*Dt,Length-ChairTravel);
		const float OldYaw=Chair->GetActorRotation().Yaw;
		ChairTravel+=Distance;
		const FVector Next=RollingChairPathPoint(ChairTravel);
		const FRotator Facing=(RollingChairPathPoint(ChairTravel+2.f)-RollingChairPathPoint(ChairTravel-2.f)).Rotation();
		Chair->SetActorLocationAndRotation(Next,Facing);
		const float Turn=FMath::DegreesToRadians(FMath::FindDeltaAngleDegrees(OldYaw,Facing.Yaw));
		const float Rolled=FVector::Dist2D(Next,Here);
		SpinChairWheel(0,(Rolled-30.f*Turn)/RearRadius);
		SpinChairWheel(1,(Rolled+30.f*Turn)/RearRadius);
		const float Swivel=90.f*FMath::SmoothStep(0.f,30.f,ChairTravel);
		SpinChairWheel(2,Rolled/CasterRadius,Swivel);
		SpinChairWheel(3,Rolled/CasterRadius,Swivel);
		if (ChairRollSound.IsValid())
		{
			ChairRollSound->SetPitchMultiplier(.64f+.52f*ChairSpeed/172.f);
			ChairRollSound->SetVolumeMultiplier(Vol(EWCSnd::SFX)*(.62f*FMath::Clamp(ChairSpeed/110.f,0.f,1.f)));
		}
		if (ChairTravel<Length-.02f) return;
		if (ChairRollSound.IsValid()) ChairRollSound->FadeOut(.16f,0.f);
		PlayAt(TEXT("wheel_baseboard"),Next+Facing.Vector()*31.f,.78f,.95f,1000.f);
		ChairImpactOmega=ChairSpeed/RearRadius;
		ChairBeat=EBathChairBeat::Tipping;
		ChairBeatAt=Clock;
		UE_LOG(LogTemp,Display,TEXT("WCBATHCHAIR struck hall baseboard at %s"),*Next.ToCompactString());
		return;
	}
	case EBathChairBeat::Tipping:
	{
		const float T=FMath::Clamp(float((Age-.18)/.76),0.f,1.f);
		float Degrees=88.f*T*T;
		if (Age>=.94) Degrees=88.f-5.f*FMath::Exp(-7.f*(Age-.94))*FMath::Abs(FMath::Sin(19.f*(Age-.94)));
		PoseFallenChair(ChairWallPose,Degrees);
		SpinChairWheel(0,ChairImpactOmega*Dt);
		SpinChairWheel(1,ChairImpactOmega*FMath::Max(0.f,1.f-float(Age)*4.f)*Dt);
		if (Age>=.94 && !bChairLanded)
		{
			bChairLanded=true;
			StartleDeputy(.76f);
			PlayAt(TEXT("wheel_sidefall"),Chair->GetActorLocation(),.83f,.94f,1200.f);
			UE_LOG(LogTemp,Display,TEXT("WCBATHCHAIR chassis landed, upper wheel free"));
		}
		if (Age<1.65) return;
		PoseFallenChair(ChairWallPose,88.f);
		RememberAtCheckpoint(TEXT("bath_chair_long_roll"));
		RememberAtCheckpoint(TEXT("bath_chair_rolled"));
		ChairBeat=EBathChairBeat::Coasting;
		ChairBeatAt=Clock;
		return;
	}
	case EBathChairBeat::Coasting:
	{
		const float Speed=FMath::Clamp(1.f-float(Age)/CoastDuration,0.f,1.f);
		const float Previous=WheelRadians[0];
		SpinChairWheel(0,ChairImpactOmega*Speed*Speed*Dt);
		if (Speed>.12f && FMath::FloorToInt(Previous/(2.f*PI))!=FMath::FloorToInt(WheelRadians[0]/(2.f*PI)))
			PlayAt(TEXT("wheel_axle_rub"),ChairWheels[0]->GetComponentLocation(),.31f*Speed,.74f+.26f*Speed,650.f);
		if (Age<CoastDuration) return;
		bEventBusy=false;
		Rest(8.f);
		ChairBeat=EBathChairBeat::Finished;
		UE_LOG(LogTemp,Display,TEXT("WCBATHCHAIR wheel stopped"));
		return;
	}
	default: return;
	}
}
