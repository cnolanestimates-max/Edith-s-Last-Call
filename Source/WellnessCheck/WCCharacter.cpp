#include "WCCharacter.h"
#include "WCDirector.h"
#include "WCEntity.h"
#include "WCWorld.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/Engine.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"
#include "Materials/MaterialInterface.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

static const int32 DustCount = 260;
static const float DustBox = 320.f;

AWCCharacter::AWCCharacter()
{
	PrimaryActorTick.bCanEverTick = true;
	GetCapsuleComponent()->InitCapsuleSize(30.f, 88.f);

	Cam = CreateDefaultSubobject<UCameraComponent>(TEXT("Cam"));
	Cam->SetupAttachment(GetCapsuleComponent());
	Cam->SetRelativeLocation(FVector(0.f, 0.f, 64.f));
	Cam->bUsePawnControlRotation = false;
	Cam->SetFieldOfView(85.f);
	Cam->PostProcessBlendWeight = 0.f;

	Flash = CreateDefaultSubobject<USpotLightComponent>(TEXT("Flash"));
	Flash->SetupAttachment(Cam);
	Flash->SetRelativeLocation(FVector(50.f, -23.f, -22.f));
	Flash->SetIntensityUnits(ELightUnits::Lumens);
	Flash->SetIntensity(0.f);
	Flash->SetInnerConeAngle(12.f);
	Flash->SetOuterConeAngle(37.f);                 // 20% wider
	Flash->SetAttenuationRadius(640.f);             // longer again (was 510, before that 390)
	Flash->SetLightColor(FLinearColor(1.f, 0.91f, 0.78f));
	Flash->SetSourceRadius(1.5f);
	Flash->SetCastShadows(true);
	Flash->SetVolumetricScatteringIntensity(2.4f);
	Flash->SetUsingAbsoluteRotation(true);

	// wide, weak halo around the hot spot, like the spill of a real torch
	Spill = CreateDefaultSubobject<USpotLightComponent>(TEXT("Spill"));
	Spill->SetupAttachment(Flash);
	Spill->SetIntensityUnits(ELightUnits::Lumens);
	Spill->SetIntensity(0.f);
	Spill->SetInnerConeAngle(24.f);
	Spill->SetOuterConeAngle(60.f);
	Spill->SetAttenuationRadius(390.f);
	Spill->SetLightColor(FLinearColor(1.f, 0.9f, 0.76f));
	Spill->SetCastShadows(false);
	Spill->SetVolumetricScatteringIntensity(0.4f);

	// the throw: a tight, far-reaching centre to the beam, so the middle of what he looks at carries about twice as far
	Throw = CreateDefaultSubobject<USpotLightComponent>(TEXT("Throw"));
	Throw->SetupAttachment(Flash);
	Throw->SetIntensityUnits(ELightUnits::Lumens);
	Throw->SetIntensity(0.f);
	Throw->SetInnerConeAngle(4.f);
	Throw->SetOuterConeAngle(11.f);
	Throw->SetAttenuationRadius(1000.f);
	Throw->SetLightColor(FLinearColor(1.f, 0.92f, 0.80f));
	Throw->SetSourceRadius(1.f);
	Throw->SetCastShadows(true);
	Throw->SetVolumetricScatteringIntensity(1.2f);

	GunPivot = CreateDefaultSubobject<USceneComponent>(TEXT("GunPivot"));
	GunPivot->SetupAttachment(Cam);
	Gun = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Gun"));
	Gun->SetupAttachment(GunPivot);
	Gun->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Gun->SetCastShadow(false);
	Gun->SetVisibility(false);
	Gun->SetRelativeRotation(FRotator(0.f, 173.f, 0.f));      // the model's barrel is its +Y; turned to point ahead and a touch inward
	Gun->SetRelativeLocation(FVector(4.f, 0.f, 0.f));
	FlashHand = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FlashHand"));
	FlashHand->SetupAttachment(Flash);
	FlashHand->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	FlashHand->SetCastShadow(false);
	FlashHand->SetRelativeRotation(FRotator(0.f, 0.f, 0.f));
	FlashHand->SetRelativeLocation(FVector(-19.f, 0.f, -1.f));
	FlashHand->SetRelativeScale3D(FVector(1.f, -1.f, 1.f));          // the model is a right hand; it is held in the left

	Muzzle = CreateDefaultSubobject<UPointLightComponent>(TEXT("Muzzle"));
	Muzzle->SetupAttachment(Cam);
	Muzzle->SetRelativeLocation(FVector(70.f, 12.f, -8.f));
	Muzzle->SetIntensityUnits(ELightUnits::Lumens);
	Muzzle->SetIntensity(0.f);
	Muzzle->SetAttenuationRadius(900.f);
	Muzzle->SetLightColor(FLinearColor(1.f, 0.72f, 0.4f));
	Muzzle->SetCastShadows(false);

	FaceLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("FaceLight"));
	FaceLight->SetupAttachment(Cam);
	FaceLight->SetRelativeLocation(FVector(4.f, -6.f, -4.f));
	FaceLight->SetIntensityUnits(ELightUnits::Lumens);
	FaceLight->SetIntensity(0.f);
	FaceLight->SetAttenuationRadius(260.f);
	FaceLight->SetLightColor(FLinearColor(1.f, 0.9f, 0.76f));
	FaceLight->SetCastShadows(false);
	FaceLight->SetVolumetricScatteringIntensity(0.f);

	Fill = CreateDefaultSubobject<UPointLightComponent>(TEXT("Fill"));
	Fill->SetupAttachment(Cam);
	Fill->SetIntensityUnits(ELightUnits::Lumens);
	Fill->SetIntensity(1.2f);
	Fill->SetAttenuationRadius(260.f);
	Fill->SetLightColor(FLinearColor(0.55f, 0.66f, 1.f));
	Fill->SetCastShadows(false);
	Fill->SetVolumetricScatteringIntensity(0.f);
	Fill->bUseInverseSquaredFalloff = true;

	InspectBack = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("InspectBack"));
	InspectBack->SetupAttachment(Cam);
	InspectBack->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	InspectBack->SetCastShadow(false);
	InspectBack->SetRelativeLocation(FVector(33.f, 0.f, 0.f));
	InspectBack->SetRelativeScale3D(FVector(0.01f, 6.f, 6.f));
	InspectBack->SetHiddenInGame(true);
	InspectBack->bAffectDynamicIndirectLighting = false;
	InspectBack->bAffectDistanceFieldLighting = false;
	InspectMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("InspectMesh"));
	InspectMesh->SetupAttachment(Cam);
	InspectMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	InspectMesh->SetCastShadow(false);
	InspectMesh->SetLightingChannels(false, false, true);
	InspectMesh->SetHiddenInGame(true);
	InspectMesh->bAffectDynamicIndirectLighting = false;
	InspectMesh->bAffectDistanceFieldLighting = false;
	for (int32 i = 0; i < 2; ++i)
	{
		UPointLightComponent* L = CreateDefaultSubobject<UPointLightComponent>(i == 0 ? TEXT("InspectKey") : TEXT("InspectFill"));
		L->SetupAttachment(Cam);
		L->SetRelativeLocation(i == 0 ? FVector(3.f, -15.f, 13.f) : FVector(6.f, 17.f, -9.f));
		L->SetIntensityUnits(ELightUnits::Lumens);
		L->SetIntensity(0.f);
		L->SetAttenuationRadius(90.f);
		L->SetLightColor(i == 0 ? FLinearColor(1.f, 0.9f, 0.76f) : FLinearColor(0.6f, 0.7f, 1.f));
		L->SetCastShadows(false);
		L->SetVolumetricScatteringIntensity(0.f);
		L->SetLightingChannels(false, false, true);
		(i == 0 ? InspectKey : InspectFill) = L;
	}

	Dust = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Dust"));
	Dust->SetupAttachment(GetCapsuleComponent());
	Dust->SetUsingAbsoluteLocation(true);
	Dust->SetUsingAbsoluteRotation(true);
	Dust->SetUsingAbsoluteScale(true);
	Dust->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Dust->SetCastShadow(false);
	Dust->bAffectDistanceFieldLighting = false;
	Dust->bAffectDynamicIndirectLighting = false;

	UCharacterMovementComponent* M = GetCharacterMovement();
	M->MaxWalkSpeed = WalkSpeed;
	M->MaxWalkSpeedCrouched = CrouchSpeed;
	M->GetNavAgentPropertiesRef().bCanCrouch = true;
	M->MaxStepHeight = 45.f;
	M->SetWalkableFloorAngle(50.f);
	M->BrakingDecelerationWalking = 1400.f;
	M->MaxAcceleration = 1100.f;
	M->GroundFriction = 7.f;
	M->SetCrouchedHalfHeight(52.f);

	bUseControllerRotationYaw = true;
	BaseEyeHeight = 64.f;
	CrouchedEyeHeight = 30.f;
}

void AWCCharacter::BeginPlay()
{
	Super::BeginPlay();
	AimQuat = Cam->GetComponentQuat();
	LastLoc = GetActorLocation();
	if (UStaticMesh* GunMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/WC/Props/SM_HandPistol.SM_HandPistol")))
	{
		Gun->SetStaticMesh(GunMesh);
	}
	if (UStaticMesh* HandMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/WC/Props/SM_HandFlashlight.SM_HandFlashlight")))
	{
		FlashHand->SetStaticMesh(HandMesh);
	}
	{
		// view-model tuning from the command line while dialling in: -WCHand=x,y,z,yaw,pitch,roll  -WCGun=...
		FString V;
		auto Apply = [](USceneComponent* C, const FString& S)
		{
			TArray<FString> P; S.ParseIntoArray(P, TEXT(","));
			if (P.Num() >= 3) C->SetRelativeLocation(FVector(FCString::Atof(*P[0]), FCString::Atof(*P[1]), FCString::Atof(*P[2])));
			if (P.Num() >= 6) C->SetRelativeRotation(FRotator(FCString::Atof(*P[4]), FCString::Atof(*P[3]), FCString::Atof(*P[5])));
		};
		if (FParse::Value(FCommandLine::Get(), TEXT("WCHand="), V, false)) Apply(FlashHand, V);
		if (FParse::Value(FCommandLine::Get(), TEXT("WCGun="), V, false)) Apply(Gun, V);
	}
	UStaticMesh* Mote = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	UMaterialInterface* MoteMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Dust.M_Dust"));
	if (Mote)
	{
		Dust->SetStaticMesh(Mote);
		if (MoteMat) Dust->SetMaterial(0, MoteMat);
		FRandomStream R(1337);
		const FVector C = GetActorLocation();
		for (int32 i = 0; i < DustCount; ++i)
		{
			const FVector P = C + FVector(R.FRandRange(-DustBox, DustBox), R.FRandRange(-DustBox, DustBox), R.FRandRange(-120.f, 150.f));
			DustPos.Add(P);
			DustVel.Add(FVector(R.FRandRange(-2.f, 2.f), R.FRandRange(-2.f, 2.f), R.FRandRange(-1.6f, 0.6f)));
			const float S = R.FRandRange(0.0022f, 0.0058f);
			Dust->AddInstance(FTransform(FQuat::Identity, P, FVector(S)), true);
		}
	}
	ApplySettings();
}

void AWCCharacter::ApplySettings()
{
	Cam->SetFieldOfView(AWCDirector::Settings.FOV);
}

FVector AWCCharacter::EyeLocation() const { return Cam->GetComponentLocation(); }
FVector AWCCharacter::EyeForward() const { return Cam->GetForwardVector(); }

void AWCCharacter::TeleportToCheckpoint(const FVector& Loc, float Yaw)
{
	FaceLumens = 0.f;
	SetActorLocation(Loc, false, nullptr, ETeleportType::TeleportPhysics);
	if (AController* C = GetController()) C->SetControlRotation(FRotator(0.f, Yaw, 0.f));
	LastLoc = Loc;
	KDTime = -1.f;
	AimQuat = FRotator(0.f, Yaw, 0.f).Quaternion();
}

void AWCCharacter::Relocate(const FVector& Loc, float Yaw)
{
	SetActorLocation(Loc, false, nullptr, ETeleportType::TeleportPhysics);
	if (AController* C = GetController()) C->SetControlRotation(FRotator(0.f, Yaw, 0.f));
	LastLoc = Loc;
	AimQuat = FRotator(0.f, Yaw, 0.f).Quaternion();
}

bool AWCCharacter::Blocked() const
{
	const AWCDirector* D = AWCDirector::Get(this);
	return bInputLocked || KDTime >= 0.f || !D || !D->IsPlaying() || D->ActiveNote.IsValid();
}

void AWCCharacter::BuildInput()
{
	auto MakeAction = [this](const TCHAR* Name, EInputActionValueType Type)
	{
		UInputAction* A = NewObject<UInputAction>(this, Name);
		A->ValueType = Type;
		return A;
	};
	Mapping = NewObject<UInputMappingContext>(this, TEXT("IMC_WC"));
	MoveAction = MakeAction(TEXT("IA_Move"), EInputActionValueType::Axis2D);
	LookAction = MakeAction(TEXT("IA_Look"), EInputActionValueType::Axis2D);
	PadLookAction = MakeAction(TEXT("IA_PadLook"), EInputActionValueType::Axis2D);
	SprintAction = MakeAction(TEXT("IA_Sprint"), EInputActionValueType::Boolean);
	CrouchAction = MakeAction(TEXT("IA_Crouch"), EInputActionValueType::Boolean);
	FlashAction = MakeAction(TEXT("IA_Flash"), EInputActionValueType::Boolean);
	UseAction = MakeAction(TEXT("IA_Use"), EInputActionValueType::Boolean);
	FireAction = MakeAction(TEXT("IA_Fire"), EInputActionValueType::Boolean);
	AimAction = MakeAction(TEXT("IA_Aim"), EInputActionValueType::Boolean);
	ReloadAction = MakeAction(TEXT("IA_Reload"), EInputActionValueType::Boolean);

	auto Swizzle = [this]() { return NewObject<UInputModifierSwizzleAxis>(this); };
	auto Negate = [this]() { return NewObject<UInputModifierNegate>(this); };
	auto Dead = [this]() { UInputModifierDeadZone* D = NewObject<UInputModifierDeadZone>(this); D->LowerThreshold = 0.22f; return D; };

	Mapping->MapKey(MoveAction, EKeys::D);
	Mapping->MapKey(MoveAction, EKeys::A).Modifiers.Add(Negate());
	Mapping->MapKey(MoveAction, EKeys::W).Modifiers.Add(Swizzle());
	{
		FEnhancedActionKeyMapping& S = Mapping->MapKey(MoveAction, EKeys::S);
		S.Modifiers.Add(Swizzle());
		S.Modifiers.Add(Negate());
	}
	Mapping->MapKey(MoveAction, EKeys::Gamepad_Left2D).Modifiers.Add(Dead());
	Mapping->MapKey(LookAction, EKeys::Mouse2D);
	Mapping->MapKey(PadLookAction, EKeys::Gamepad_Right2D).Modifiers.Add(Dead());
	Mapping->MapKey(SprintAction, EKeys::LeftShift);
	Mapping->MapKey(SprintAction, EKeys::Gamepad_LeftThumbstick);
	Mapping->MapKey(CrouchAction, EKeys::C);
	Mapping->MapKey(CrouchAction, EKeys::LeftControl);
	Mapping->MapKey(CrouchAction, EKeys::Gamepad_FaceButton_Right);
	Mapping->MapKey(FlashAction, EKeys::F);
	Mapping->MapKey(FlashAction, EKeys::Gamepad_FaceButton_Top);
	Mapping->MapKey(UseAction, EKeys::E);
	Mapping->MapKey(UseAction, EKeys::Gamepad_FaceButton_Bottom);
	Mapping->MapKey(FireAction, EKeys::LeftMouseButton);
	Mapping->MapKey(FireAction, EKeys::Gamepad_RightTrigger);
	Mapping->MapKey(AimAction, EKeys::RightMouseButton);
	Mapping->MapKey(AimAction, EKeys::Gamepad_LeftTrigger);
	Mapping->MapKey(ReloadAction, EKeys::R);
	Mapping->MapKey(ReloadAction, EKeys::Gamepad_FaceButton_Left);
}

void AWCCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);
	if (!Mapping) BuildInput();
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (UEnhancedInputLocalPlayerSubsystem* Sub = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
		{
			Sub->AddMappingContext(Mapping, 0);
		}
	}
	if (UEnhancedInputComponent* In = Cast<UEnhancedInputComponent>(PlayerInputComponent))
	{
		In->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AWCCharacter::Move);
		In->BindAction(LookAction, ETriggerEvent::Triggered, this, &AWCCharacter::Look);
		In->BindAction(PadLookAction, ETriggerEvent::Triggered, this, &AWCCharacter::Look);
		In->BindAction(SprintAction, ETriggerEvent::Started, this, &AWCCharacter::StartSprint);
		In->BindAction(SprintAction, ETriggerEvent::Completed, this, &AWCCharacter::StopSprint);
		In->BindAction(CrouchAction, ETriggerEvent::Started, this, &AWCCharacter::ToggleCrouch);
		In->BindAction(FlashAction, ETriggerEvent::Started, this, &AWCCharacter::ToggleFlashlight);
		In->BindAction(UseAction, ETriggerEvent::Started, this, &AWCCharacter::DoInteract);
		In->BindAction(FireAction, ETriggerEvent::Started, this, &AWCCharacter::DoFire);
		In->BindAction(AimAction, ETriggerEvent::Started, this, &AWCCharacter::AimOn);
		In->BindAction(AimAction, ETriggerEvent::Completed, this, &AWCCharacter::AimOff);
		In->BindAction(ReloadAction, ETriggerEvent::Started, this, &AWCCharacter::DoReload);
	}
}

void AWCCharacter::Move(const FInputActionValue& Value)
{
	if (Blocked()) return;
	const FVector2D Axis = Value.Get<FVector2D>();
	const FRotator Yaw(0.f, GetControlRotation().Yaw, 0.f);
	AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::X), Axis.Y);
	AddMovementInput(FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y), Axis.X);
}

void AWCCharacter::Look(const FInputActionValue& Value)
{
	const AWCDirector* D = AWCDirector::Get(this);
	if (KDTime >= 0.f || !D || !D->IsPlaying() || D->ActiveNote.IsValid()) return;
	const FVector2D Axis = Value.Get<FVector2D>();
	const FWCSettings& S = AWCDirector::Settings;
	const float K = 1.0f * S.Sensitivity * (bAiming ? 0.7f : 1.f);
	AddControllerYawInput(Axis.X * K);
	AddControllerPitchInput(Axis.Y * K * (S.bInvertY ? 1.f : -1.f));
}

void AWCCharacter::ToggleCrouch()
{
	if (Blocked()) return;
	if (bIsCrouched) UnCrouch(); else Crouch();
}

void AWCCharacter::SetFlashlight(bool bOn, bool bClick)
{
	if (bOn == bLightOn) return;
	bLightOn = bOn;
	if (bClick)
	{
		if (AWCDirector* D = AWCDirector::Get(this)) D->Play2D(TEXT("flashlight_click"), bOn ? 0.7f : 0.55f, EWCSnd::SFX, bOn ? 1.f : 0.9f);
	}
}

void AWCCharacter::ToggleFlashlight()
{
	if (Blocked()) return;
	SetFlashlight(!bLightOn);
	if (AWCDirector* D = AWCDirector::Get(this)) D->Event(TEXT("flashlight"));
}

void AWCCharacter::FlickerLight(float Seconds, float Depth)
{
	FlickerUntil = Clock + Seconds;
	FlickerDepth = Depth;
}

void AWCCharacter::DoInteract()
{
	AWCDirector* D = AWCDirector::Get(this);
	if (!D || !D->IsPlaying()) return;
	if (D->ActiveNote.IsValid()) { D->CloseNote(); return; }
	if (bInputLocked || KDTime >= 0.f) return;
	if (AWCInteractable* T = Focus.Get()) T->Interact(this);
}

void AWCCharacter::DoReload()
{
	if (Blocked() || !bGunAllowed || ReloadUntil > Clock || Ammo >= MagSize || Reserve <= 0) return;
	ReloadUntil = Clock + 1.9f;
	if (AWCDirector* D = AWCDirector::Get(this)) D->Play2D(TEXT("gun_reload"), 0.8f);
}

void AWCCharacter::DoFire()
{
	AWCDirector* D = AWCDirector::Get(this);
	if (Blocked() || !D || !bGunAllowed || GunAlpha < 0.75f || Clock < FireReady || ReloadUntil > Clock) return;
	FireReady = Clock + 0.3f;
	if (Ammo <= 0)
	{
		D->Play2D(TEXT("gun_empty"), 0.7f);
		return;
	}
	--Ammo;
	D->Play2D(TEXT("gun_shot"), 1.f);
	Recoil = 1.f;
	MuzzleUntil = Clock + 0.06f;
	AddShake(0.5f);

	const FVector Start = Cam->GetComponentLocation();
	const FVector Dir = Cam->GetForwardVector();
	const FVector End = Start + Dir * 6000.f;
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(WCFire), true, this);
	const bool bHit = GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params);
	const FVector Stop = bHit ? Hit.ImpactPoint : End;
	if (AWCEntity* Her = D->Her())
	{
		if (Her->IsShown() && Her->SegmentHits(Start, Stop)) D->Event(TEXT("shot_her"));
	}
	if (bHit)
	{
		D->PlayAt(TEXT("bullet_impact"), Hit.ImpactPoint, 0.9f, FMath::FRandRange(0.9f, 1.1f));
	}
	D->Event(TEXT("shot"));
}

void AWCCharacter::Knockdown(float DownSeconds)
{
	if (KDTime >= 0.f) return;
	KDTime = 0.f;
	KDDown = DownSeconds;
	bAiming = false;
	GetCharacterMovement()->StopMovementImmediately();
}

void AWCCharacter::TickDust(float Dt)
{
	if (DustPos.Num() == 0) return;
	const FVector C = Cam->GetComponentLocation();
	const int32 N = DustPos.Num();
	// a slice per frame is enough: motes barely move
	static int32 Cursor = 0;
	const int32 Slice = 65;
	for (int32 k = 0; k < Slice; ++k)
	{
		const int32 i = (Cursor + k) % N;
		FVector& P = DustPos[i];
		P += DustVel[i] * Dt * (float)N / (float)Slice;
		bool bWrap = false;
		for (int32 a = 0; a < 3; ++a)
		{
			const float Half = a == 2 ? 140.f : DustBox;
			const float D = P[a] - C[a];
			if (D > Half) { P[a] -= 2.f * Half; bWrap = true; }
			else if (D < -Half) { P[a] += 2.f * Half; bWrap = true; }
		}
		FTransform T;
		Dust->GetInstanceTransform(i, T, true);
		T.SetLocation(P);
		Dust->UpdateInstanceTransform(i, T, true, k == Slice - 1, bWrap);
	}
	Cursor = (Cursor + Slice) % N;
}

void AWCCharacter::Tick(float Dt)
{
	Super::Tick(Dt);
	Clock += Dt;
	AWCDirector* D = AWCDirector::Get(this);
	const FWCSettings& S = AWCDirector::Settings;
	UCharacterMovementComponent* M = GetCharacterMovement();
	const bool bBlocked = Blocked();

	M->MaxWalkSpeed = (bSprinting && !bIsCrouched && !bAiming) ? SprintSpeed : (bAiming ? WalkSpeed * 0.65f : WalkSpeed);
	M->MaxWalkSpeedCrouched = CrouchSpeed;

	// ---- footsteps
	const FVector Loc = GetActorLocation();
	const float Moved = FVector::Dist2D(Loc, LastLoc);
	LastLoc = Loc;
	const float Speed = GetVelocity().Size2D();
	if (M->IsMovingOnGround() && Moved < 120.f && Speed > 20.f)
	{
		StepDist += Moved;
		const float Stride = bIsCrouched ? 50.f : (Speed > WalkSpeed * 1.3f ? 92.f : 66.f);
		if (StepDist >= Stride)
		{
			StepDist = 0.f;
			FName Surface = TEXT("Wood");
			FHitResult Hit;
			FCollisionQueryParams P(SCENE_QUERY_STAT(WCStep), false, this);
			if (GetWorld()->LineTraceSingleByChannel(Hit, Loc, Loc - FVector(0, 0, 160), ECC_Visibility, P) && Hit.GetActor())
			{
				for (const FName& Tag : Hit.GetActor()->Tags)
				{
					if (Tag.ToString().StartsWith(TEXT("Floor_"))) { Surface = FName(*Tag.ToString().Mid(6)); break; }
				}
			}
			if (D) D->Footstep(Loc - FVector(0, 0, 88), FMath::Clamp(Speed / WalkSpeed, 0.4f, 1.5f) * (bIsCrouched ? 0.45f : 1.f), Surface);
		}
	}
	else if (Speed < 5.f) StepDist = FMath::Min(StepDist, 40.f);

	// ---- camera: eye height, bob, shake, knock-down
	const float TargetEye = bIsCrouched ? CrouchedEyeHeight : BaseEyeHeight;
	EyeZ = FMath::FInterpTo(EyeZ, TargetEye, Dt, 9.f);
	if (Speed > 10.f && M->IsMovingOnGround()) BobTime += Dt * Speed / 36.f;
	const float BobAmt = S.bHeadBob ? FMath::Clamp(Speed / 300.f, 0.f, 1.f) : 0.f;
	float Z = EyeZ + FMath::Sin(BobTime * 2.f) * 1.6f * BobAmt;
	float Roll = FMath::Sin(BobTime) * 0.5f * BobAmt;
	float PitchAdd = 0.f, YawAdd = 0.f;

	Shake = FMath::FInterpTo(Shake, 0.f, Dt, 2.2f);
	if (S.bCameraShake && Shake > 0.002f)
	{
		PitchAdd += Shake * 2.2f * FMath::Sin(Clock * 47.f) * FMath::Sin(Clock * 13.f + 1.f);
		YawAdd += Shake * 2.0f * FMath::Sin(Clock * 39.f + 2.f) * FMath::Sin(Clock * 17.f);
		Roll += Shake * 1.6f * FMath::Sin(Clock * 31.f + 4.f);
	}
	Recoil = FMath::FInterpTo(Recoil, 0.f, Dt, 9.f);
	PitchAdd += Recoil * 3.2f;

	if (KDTime >= 0.f)
	{
		KDTime += Dt;
		const float Fall = 0.42f, Rise = 2.2f;
		float A;   // 0 standing .. 1 flat on your back
		if (KDTime < Fall) A = FMath::InterpEaseIn(0.f, 1.f, KDTime / Fall, 2.2f);
		else if (KDTime < Fall + KDDown) A = 1.f;
		else A = 1.f - FMath::InterpEaseInOut(0.f, 1.f, FMath::Clamp((KDTime - Fall - KDDown) / Rise, 0.f, 1.f), 2.f);
		Z = FMath::Lerp(Z, -62.f, A);
		PitchAdd += 46.f * A;
		Roll += 24.f * A * (1.f + 0.15f * FMath::Sin(Clock * 3.f));
		if (KDTime >= Fall + KDDown + Rise)
		{
			KDTime = -1.f;
			if (D) D->Event(TEXT("gotup"));
		}
	}
	Cam->SetRelativeLocation(FVector(0.f, 0.f, Z));
	FRotator View = GetControlRotation();
	View.Pitch = FMath::Clamp(FRotator::NormalizeAxis(View.Pitch) + PitchAdd, -89.f, 89.f);
	View.Yaw += YawAdd;
	View.Roll = Roll;
	Cam->SetWorldRotation(View);
	const float WantFov = S.FOV - 9.f * GunAlpha;
	Cam->SetFieldOfView(FMath::FInterpTo(Cam->FieldOfView, WantFov, Dt, 8.f));

	// ---- flashlight: lags behind the view and sways with your steps
	{
		FHitResult FH;
		FCollisionQueryParams FQ(SCENE_QUERY_STAT(WCFlashAim), false, this);
		const FVector CS = Cam->GetComponentLocation();
		const FVector CFwd = Cam->GetForwardVector();
		float Want = GetWorld()->LineTraceSingleByChannel(FH, CS, CS + CFwd * 1200.f, ECC_Visibility, FQ) ? FMath::Max(FH.Distance, 100.f) : 1200.f;
		float FaceWant = 0.f;
		if (AWCDirector* DD = AWCDirector::Get(this))
		{
			AWCEntity* E = DD->Her();
			if (E && E->IsShown())
			{
				const FVector Head = E->HeadLocation();
				const float T = FVector::DotProduct(Head - CS, CFwd);
				const float Off = FVector::Dist(CS + CFwd * T, Head);
				if (T > 30.f && T < Want && Off < 95.f) Want = FMath::Max(T, 100.f);
				// close and in front of him: the light finds her face
				if (T > 20.f && T < 330.f && Off < 0.75f * T + 40.f) { FaceWant = 1.f; FacePoint = Head + FVector(0, 0, -6.f); }
			}
		}
		AimDist = FMath::FInterpTo(AimDist, Want, Dt, 7.f);
		FaceAim = FMath::FInterpTo(FaceAim, FaceWant, Dt, 6.f);
	}
	const FVector AimPoint = FMath::Lerp(Cam->GetComponentLocation() + Cam->GetForwardVector() * AimDist, FacePoint, FaceAim * 0.9f);
	const FQuat Target = (AimPoint - Flash->GetComponentLocation()).ToOrientationQuat();
	AimQuat = FQuat::Slerp(AimQuat, Target, 1.f - FMath::Exp(-13.f * Dt)).GetNormalized();
	const float Walk = FMath::Clamp(Speed / WalkSpeed, 0.f, 1.7f);
	const FRotator SwayRot(0.7f * Walk * FMath::Sin(Clock * 6.3f), 0.9f * Walk * FMath::Sin(Clock * 3.15f), 0.f);
	Flash->SetWorldRotation(AimQuat * SwayRot.Quaternion());
	float Level = bLightOn ? LightScale : 0.f;
	if (Clock < FlickerUntil)
	{
		const float N = FMath::Sin(Clock * 61.f) * FMath::Sin(Clock * 23.f + 1.3f);
		Level *= FMath::Clamp(1.f - FlickerDepth * (0.55f + 0.45f * N) - (N > 0.55f ? 0.5f : 0.f), 0.f, 1.f);
	}
	Flash->SetIntensity(FlashLumens * Level);
	Spill->SetIntensity(FlashLumens * 0.11f * Level);
	Throw->SetIntensity(FlashLumens * 0.24f * Level);
	FaceLight->SetIntensity(FaceLumens * FMath::Clamp(Level, 0.25f, 1.f));

	// ---- pistol
	const bool bWantGun = bAiming && bGunAllowed && !bBlocked;
	GunAlpha = FMath::FInterpConstantTo(GunAlpha, bWantGun ? 1.f : 0.f, Dt, 4.5f);
	if (ReloadUntil > 0.f && Clock >= ReloadUntil)
	{
		const int32 Take = FMath::Min(MagSize - Ammo, Reserve);
		Ammo += Take; Reserve -= Take;
		ReloadUntil = -1.f;
	}
	const float ReloadDip = ReloadUntil > Clock ? FMath::Sin(FMath::Clamp((ReloadUntil - Clock) / 1.9f, 0.f, 1.f) * PI) : 0.f;
	Gun->SetVisibility(GunAlpha > 0.02f && Gun->GetStaticMesh() != nullptr);
	const FVector Low(30.f, 27.f, -62.f), High(39.f, 14.5f, -15.5f);
	GunPivot->SetRelativeLocation(FMath::Lerp(Low, High, FMath::InterpEaseOut(0.f, 1.f, GunAlpha, 2.f)) + FVector(-5.f * Recoil, 0.f, 1.5f * Recoil - 16.f * ReloadDip));
	GunPivot->SetRelativeRotation(FRotator(-28.f * (1.f - GunAlpha) + 7.f * Recoil - 30.f * ReloadDip, 0.f, 0.f));
	FlashHand->SetVisibility(FlashHand->GetStaticMesh() != nullptr && KDTime < 0.f);
	Muzzle->SetIntensity(Clock < MuzzleUntil ? 9000.f : 0.f);

	// ---- what are we looking at?
	Focus = nullptr;
	if (!bBlocked)
	{
		FHitResult Hit;
		const FVector Start = Cam->GetComponentLocation();
		const FVector End = Start + Cam->GetForwardVector() * InteractRange;
		FCollisionQueryParams P(SCENE_QUERY_STAT(WCUse), false, this);
		if (GetWorld()->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, P))
		{
			AWCInteractable* T = Cast<AWCInteractable>(Hit.GetActor());
			if (T && T->CanInteract() && FVector::Dist2D(Hit.ImpactPoint, GetActorLocation()) <= InteractReach) Focus = T;
		}
	}
	TickDust(Dt);
}

// ---------------------------------------------------------------------------------------------- inventory: the thing held up
static const float InspectK = 0.45f;
void AWCCharacter::ShowInspect(UStaticMesh* InMesh, const TArray<UMaterialInterface*>& Mats, const FVector& PartScale)
{
	if (!InspectBack->GetStaticMesh())
	{
		InspectBack->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
		InspectBack->SetMaterial(0, LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Void.M_Void")));
	}
	// everything is held small and very close, so the room cannot come between the eye and the black card
	InspectBack->SetRelativeLocation(FVector(33.f * InspectK, 0.f, 0.f));
	InspectBack->SetRelativeScale3D(FVector(0.004f, 6.f * InspectK, 6.f * InspectK));
	InspectKey->SetRelativeLocation(FVector(3.f, -15.f, 13.f) * InspectK);
	InspectFill->SetRelativeLocation(FVector(6.f, 17.f, -9.f) * InspectK);
	InspectKey->SetAttenuationRadius(90.f * InspectK);
	InspectFill->SetAttenuationRadius(90.f * InspectK);
	if (GEngine) GEngine->Exec(GetWorld(), TEXT("r.SetNearClipPlane 2"));
	InspectBack->SetHiddenInGame(false);
	GunPivot->SetHiddenInGame(true, true);
	FlashHand->SetHiddenInGame(true, true);
	Dust->SetHiddenInGame(true);
	InspectPart = PartScale;
	InspectMesh->SetStaticMesh(InMesh);
	InspectMesh->EmptyOverrideMaterials();
	for (int32 i = 0; i < Mats.Num(); ++i) if (Mats[i]) InspectMesh->SetMaterial(i, Mats[i]);
	InspectMesh->SetHiddenInGame(InMesh == nullptr);
	InspectKey->SetIntensity(InMesh ? 150.f * InspectK * InspectK : 0.f);
	InspectFill->SetIntensity(InMesh ? 45.f * InspectK * InspectK : 0.f);
}

FQuat AWCCharacter::InspectBase() const
{
	const UStaticMesh* M = InspectMesh->GetStaticMesh();
	if (!M) return FQuat::Identity;
	const FVector E = M->GetBounds().BoxExtent * InspectPart;
	const float Big = E.GetMax();
	if (E.Z <= E.X && E.Z <= E.Y && E.Z < 0.45f * Big) return FQuat(FRotator(68.f, 0.f, 0.f));        // lies flat: tip its top toward him
	if (E.Y <= E.X && E.Y <= E.Z && E.Y < 0.45f * Big) return FQuat(FRotator(0.f, -90.f, 0.f));       // thin from side to side: show the side
	if (E.X < 0.45f * Big) return FQuat::Identity;
	return FQuat(FRotator(8.f, 180.f, 0.f));
}

bool AWCCharacter::IsInspectFlat() const
{
	const UStaticMesh* M = InspectMesh->GetStaticMesh();
	if (!M) return false;
	const FVector E = M->GetBounds().BoxExtent * InspectPart;
	return E.Z < 0.42f * FMath::Min(E.X, E.Y) || E.Z < 0.16f * FMath::Max(E.X, E.Y);
}

void AWCCharacter::SetInspectView(const FQuat& Rot, float Zoom)
{
	const UStaticMesh* M = InspectMesh->GetStaticMesh();
	if (!M) return;
	const FBoxSphereBounds B = M->GetBounds();
	const float Radius = FMath::Max((B.BoxExtent * InspectPart).Size(), 0.3f);
	const FVector Scale = InspectPart * (6.2f * InspectK * Zoom / Radius);
	InspectMesh->SetRelativeScale3D(Scale);
	InspectMesh->SetRelativeRotation(Rot);
	InspectMesh->SetRelativeLocation(FVector(21.f, 0.f, 1.4f) * InspectK - Rot.RotateVector(B.Origin * Scale));
}

void AWCCharacter::HideInspect()
{
	InspectBack->SetHiddenInGame(true);
	InspectMesh->SetHiddenInGame(true);
	InspectKey->SetIntensity(0.f);
	InspectFill->SetIntensity(0.f);
	GunPivot->SetHiddenInGame(false, true);
	FlashHand->SetHiddenInGame(false, true);
	Dust->SetHiddenInGame(false);
	if (GEngine) GEngine->Exec(GetWorld(), TEXT("r.SetNearClipPlane 10"));
}

void AWCCharacter::SetDarkAdapt(float Stops)
{
	const bool bOn = Stops > 0.01f;
	Cam->PostProcessSettings.bOverride_AutoExposureMethod = bOn;
	Cam->PostProcessSettings.AutoExposureMethod = EAutoExposureMethod::AEM_Manual;
	Cam->PostProcessSettings.bOverride_AutoExposureBias = bOn;
	Cam->PostProcessSettings.AutoExposureBias = -5.f - Stops;            // the night grade is -5 (lighting.py NIGHT_EV)
	Cam->PostProcessBlendWeight = bOn ? 1.f : 0.f;
}
