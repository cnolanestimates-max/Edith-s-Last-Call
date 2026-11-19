// The deputy: first-person movement, flashlight, service pistol, look-and-press-E interaction,
// scripted knock-downs and camera shake.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "WCCharacter.generated.h"

class UCameraComponent;
class USpotLightComponent;
class UPointLightComponent;
class UStaticMeshComponent;
class UStaticMesh;
class UMaterialInterface;
class UInstancedStaticMeshComponent;
class UInputAction;
class UInputMappingContext;
class AWCInteractable;

UCLASS()
class WELLNESSCHECK_API AWCCharacter : public ACharacter
{
	GENERATED_BODY()
public:
	AWCCharacter();
	virtual void Tick(float Dt) override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;

	AWCInteractable* GetFocus() const { return Focus.Get(); }
	bool IsFlashlightOn() const { return bLightOn; }
	void SetFlashlight(bool bOn, bool bClick = true);
	/** Scripted brightness multiplier (0 = dead). The player's switch still works; the bulb just gives nothing. */
	void SetLightScale(float Scale) { LightScale = Scale; }
	/** Stops the camera down by so many stops (0 = normal): real black, when the house lights are meant to be out. */
	void SetDarkAdapt(float Stops);
	float GetLightScale() const { return LightScale; }
	void FlickerLight(float Seconds, float Depth = 0.85f);
	void SetInputLocked(bool bLocked) { bInputLocked = bLocked; }
	bool IsInputLocked() const { return bInputLocked; }
	/** Thrown onto your back. The screen is black while down; control returns after you get up. */
	void Knockdown(float DownSeconds);
	bool IsDown() const { return KDTime >= 0.f; }
	void AddShake(float Amount) { Shake = FMath::Max(Shake, Amount); }
	void SetGunAllowed(bool bAllowed) { bGunAllowed = bAllowed; }
	bool IsGunUp() const { return GunAlpha > 0.75f; }
	void ApplySettings();
	void TeleportToCheckpoint(const FVector& Loc, float Yaw);
	/** Move the player without touching any state (used while they are down and the screen is black). */
	void Relocate(const FVector& Loc, float Yaw);
	FVector EyeLocation() const;
	FVector EyeForward() const;

	// also used by the automatic play-through
	void DoInteract();
	void DoFire();
	void DoReload();
	void ToggleFlashlight();
	void SetAiming(bool bAim) { bAiming = bAim; }
	/** Light at his own eye, for when something is closer than the torch in his hand. Lumens; 0 = off. */
	void SetFaceLight(float Lumens) { FaceLumens = Lumens; }

	// inventory: one thing held up in front of the camera, lit by its own lamps, against black
	void ShowInspect(UStaticMesh* InMesh, const TArray<UMaterialInterface*>& Mats, const FVector& PartScale);
	void SetInspectView(const FQuat& Rot, float Zoom);
	void HideInspect();
	bool IsInspectFlat() const;
	/** How the thing is turned so its broad side faces him. */
	FQuat InspectBase() const;

	UPROPERTY(EditAnywhere, Category = "WC") float WalkSpeed = 100.f;
	UPROPERTY(EditAnywhere, Category = "WC") float SprintSpeed = 190.f;
	UPROPERTY(EditAnywhere, Category = "WC") float CrouchSpeed = 62.f;
	UPROPERTY(EditAnywhere, Category = "WC") float InteractRange = 190.f;        // along the line of sight: long enough to reach the floor at his feet
	/** ... but the thing itself has to be this close to him on the floor plan (arm's length). */
	UPROPERTY(EditAnywhere, Category = "WC") float InteractReach = 115.f;
	UPROPERTY(EditAnywhere, Category = "WC") float FlashLumens = 150.f;       // Cheyenne: about five feet of sight, the rest black (was 980 with a 26 m reach)

	int32 Ammo = 8;
	int32 Reserve = 16;
	static const int32 MagSize = 8;

	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UCameraComponent> Cam;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<USpotLightComponent> Flash;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<USpotLightComponent> Spill;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<USpotLightComponent> Throw;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> Muzzle;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> Fill;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> FaceLight;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<USceneComponent> GunPivot;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UStaticMeshComponent> Gun;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UStaticMeshComponent> FlashHand;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UInstancedStaticMeshComponent> Dust;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UStaticMeshComponent> InspectMesh;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UStaticMeshComponent> InspectBack;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> InspectKey;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> InspectFill;

protected:
	virtual void BeginPlay() override;

private:
	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);
	void StartSprint() { bSprinting = true; }
	void StopSprint() { bSprinting = false; }
	void ToggleCrouch();
	void AimOn() { bAiming = true; }
	void AimOff() { bAiming = false; }
	void BuildInput();
	void TickDust(float Dt);
	bool Blocked() const;

	UPROPERTY(Transient) TObjectPtr<UInputMappingContext> Mapping;
	UPROPERTY(Transient) TObjectPtr<UInputAction> MoveAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> LookAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> PadLookAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> SprintAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> CrouchAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> FlashAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> UseAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> FireAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> AimAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> ReloadAction;

	TWeakObjectPtr<AWCInteractable> Focus;
	bool bLightOn = false;
	float AimDist = 600.f;
	float FaceLumens = 0.f;
	float FaceAim = 0.f;
	FVector FacePoint = FVector::ZeroVector;
	FVector InspectPart = FVector::OneVector;
	bool bSprinting = false;
	bool bAiming = false;
	bool bInputLocked = false;
	bool bGunAllowed = true;
	float LightScale = 1.f;
	float FlickerUntil = -1.f;
	float FlickerDepth = 0.85f;
	float Clock = 0.f;
	float BobTime = 0.f;
	float StepDist = 0.f;
	float Shake = 0.f;
	float GunAlpha = 0.f;
	float Recoil = 0.f;
	float FireReady = 0.f;
	float ReloadUntil = -1.f;
	float MuzzleUntil = -1.f;
	float KDTime = -1.f;
	float KDDown = 2.f;
	float EyeZ = 64.f;
	FQuat AimQuat = FQuat::Identity;
	FVector LastLoc = FVector::ZeroVector;
	TArray<FVector> DustPos;
	TArray<FVector> DustVel;
};
