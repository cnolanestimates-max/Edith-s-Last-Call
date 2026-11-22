#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCWorld.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"

namespace
{
	constexpr double GripAt = .67;
	constexpr double ImpactAt = 1.14;
	constexpr double TurnAt = 2.83;
	constexpr double ReleaseAt = 4.69;
}

void AWCDirector::StartShedPickup(AWCPickup* Tape)
{
	AWCCharacter* P = Player();
	if (!P || !P->GetController() || !IsValid(Tape) || IsShedPickupActive() || Has(TEXT("tape1_taken"))) return;
	ShedTape = Tape;
	ShedTapeHome = Tape->Mesh->GetComponentTransform();
	ShedPickupAt = Clock;
	bShedImpactPlayed = false;
	ShedOrigin = P->GetActorLocation();
	ShedEye = P->EyeLocation();
	ShedInitialView = P->GetControlRotation().GetNormalized();
	const FVector ToTape = ShedTapeHome.GetLocation() - ShedEye;
	ShedReachYaw = ToTape.Rotation().Yaw;
	const FVector Exit = Pos(TEXT("A_Shed")) - ShedEye;
	ShedTurnDelta = FMath::FindDeltaAngleDegrees(ShedReachYaw, Exit.Rotation().Yaw);

	P->SetInputLocked(true);
	P->GetCharacterMovement()->StopMovementImmediately();
	P->ConsumeMovementInputVector();
	bBusy = true;
	Tape->bEnabled = false;
	Tape->SetActorEnableCollision(false);
	Tape->Mesh->SetMobility(EComponentMobility::Movable);

	if (UStaticMesh* Glove = LoadObject<UStaticMesh>(nullptr,TEXT("/Game/WC/Props/HouseDetails/SM_SettlersGlove.SM_SettlersGlove")))
	{
		ShedGlove = NewObject<UStaticMeshComponent>(this);
		ShedGlove->SetStaticMesh(Glove);
		ShedGlove->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		ShedGlove->SetCanEverAffectNavigation(false);
		ShedGlove->SetCastShadow(false);
		ShedGlove->SetVisibility(false);
		ShedGlove->RegisterComponent();
	}
	ShedFill = NewObject<UPointLightComponent>(this);
	ShedFill->SetIntensityUnits(ELightUnits::Lumens);
	ShedFill->SetLightColor(FLinearColor(.87f, .91f, 1.f));
	ShedFill->SetAttenuationRadius(112.f);
	ShedFill->SetCastShadows(false);
	ShedFill->SetIntensity(0.f);
	ShedFill->RegisterComponent();
	UE_LOG(LogTemp, Display, TEXT("WCSHED start glove=%d prop=%d at=%s tape=%s"),
		ShedGlove.IsValid(), Tape->Mesh->GetStaticMesh() != nullptr, *ShedOrigin.ToCompactString(), *ShedTapeHome.GetLocation().ToCompactString());
}

void AWCDirector::TickShedPickup()
{
	if (!IsShedPickupActive()) return;
	AWCCharacter* P = Player();
	AWCPickup* Tape = ShedTape.Get();
	if (!P || !P->GetController() || !Tape)
	{
		FinishShedPickup();
		return;
	}
	const double T = Clock - ShedPickupAt;
	auto Ease = [T](double A, double B) { return FMath::SmoothStep(A,B,T); };
	const FRotator ReachHeading(0., ShedReachYaw, 0.);
	const FVector Fwd = ReachHeading.Vector();
	const FVector Side = FRotationMatrix(ReachHeading).GetUnitAxis(EAxis::Y);
	const FVector Up = FVector::UpVector;
	const FVector Rest = ShedTapeHome.GetLocation();
	const double Lift = Ease(GripAt, 1.32);
	const double Stow = Ease(1.30, 1.86);
	const FVector Held = ShedEye + Fwd * 45. + Side * 5. - Up * 33.;
	const FVector TapeAt = FMath::Lerp(Rest, Held, Lift) + Stow * (-Fwd * 19. + Side * 19. - Up * 56.);
	const FQuat Grip = FRotator(43. * Lift + 20. * Stow, ShedReachYaw, -10. * Lift).Quaternion();
	const FQuat Carry = Grip * FRotator(0.,90.,0.).Quaternion();
	const FQuat TapeRotation = FQuat::Slerp(ShedTapeHome.GetRotation(), Carry, Ease(GripAt,1.19));
	Tape->Mesh->SetWorldLocationAndRotation(TapeAt, TapeRotation);
	if (ShedGlove.IsValid())
	{
		const double Reach = Ease(.12, GripAt);
		const FVector From = ShedEye + Fwd * 33. + Side * 26. - Up * 59.;
		const FVector Grasp = TapeAt + Grip.RotateVector(FVector(4.,-.7,-1.65));
		ShedGlove->SetRelativeScale3D(FVector(1., .89, .69));
		const FVector Hand = FMath::Lerp(From, Grasp, Reach) + Up * (7. * FMath::Sin(PI * Reach));
		ShedGlove->SetWorldLocationAndRotation(Hand, Grip);
		ShedGlove->SetVisibility(T > .12 && T < 1.85);
	}
	if (ShedFill.IsValid())
	{
		ShedFill->SetWorldLocation(TapeAt - Fwd * 23. - Side * 9. + Up * 29.);
		ShedFill->SetIntensity(19.f * Ease(0.,.35) * (1.-Stow));
	}
	Tape->SetActorHiddenInGame(T >= 1.86);

	if (T < TurnAt)
	{
		const FVector LookPoint = FMath::Lerp(Rest, Held, Lift) + Up * 2.;
		const FRotator ToTape = (LookPoint - ShedEye).Rotation();
		const FRotator Level(0., ShedReachYaw, 0.);
		const FQuat Look = FQuat::Slerp(ShedInitialView.Quaternion(), ToTape.Quaternion(), Ease(0.,.30));
		P->GetController()->SetControlRotation(FQuat::Slerp(Look, Level.Quaternion(), Ease(1.32,2.28)).Rotator());
	}
	else
	{
		P->GetController()->SetControlRotation(FRotator(0., ShedReachYaw + ShedTurnDelta * Ease(TurnAt,ReleaseAt), 0.));
	}
	if (!bShedImpactPlayed && T >= ImpactAt)
	{
		bShedImpactPlayed = true;
		ApplyWorldState();
		const FVector Bin = Pos(TEXT("TrashPoint"));
		PlayAt(TEXT("trash_can_fall"), Bin + Up * 24., 1.f, 1.f, 2400.f, true);
		P->AddShake(.48f);
		StartleDeputy(.81f);
		Tension = 1.f;
		const FVector Away = Pos(TEXT("TrashRunTo"));
		constexpr float Footfalls[] = {1.73f, 2.05f, 2.35f, 2.68f, 3.03f};
		for (int32 I = 0; I < UE_ARRAY_COUNT(Footfalls); ++I)
		{
			const FVector Step = FMath::Lerp(Bin,Away,I/4.f) + Up * 10.;
			After(Footfalls[I], [this,Step,I]() { PlayAt(TEXT("step_gravel"),Step,2.1f-.17f*I,.94f+.035f*I,2400.f,true); });
		}
		Say(TEXT("d_shedcall"), 3.22f);
		UE_LOG(LogTemp, Display, TEXT("WCSHED impact and shake t=%.2f lift=%.2f stow=%.2f locked=%d"),T,Lift,Stow,P->IsInputLocked());
	}
	if (T >= ReleaseAt) FinishShedPickup();
}

void AWCDirector::FinishShedPickup()
{
	ShedPickupAt = -1.;
	if (ShedGlove.IsValid()) ShedGlove->DestroyComponent();
	if (ShedFill.IsValid()) ShedFill->DestroyComponent();
	if (AWCPickup* Tape = ShedTape.Get())
	{
		Tape->SetActorHiddenInGame(true);
		Tape->Mesh->SetWorldTransform(ShedTapeHome);
	}
	Set(TEXT("tape1_taken"));
	Set(TEXT("shed_seen"));
	bShedImpactPlayed = false;
	bBusy = false;
	if (AWCCharacter* P = Player())
	{
		P->SetInputLocked(false);
		UE_LOG(LogTemp, Display, TEXT("WCSHED released drift=%.1f cm pitch=%.1f"),
			FVector::Dist2D(ShedOrigin,P->GetActorLocation()),P->GetControlRotation().GetNormalized().Pitch);
	}
	if (!HasItem(TEXT("tape1"))) GiveItem(TEXT("tape1"), TEXT("VHS tape"));
	Event(TEXT("take:tape1"));
	ApplyWorldState();
	OutsideProgress();
}
