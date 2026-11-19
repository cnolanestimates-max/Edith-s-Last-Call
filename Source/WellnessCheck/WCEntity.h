// "Her": Edith Harrow. A scripted apparition: the director tells her where to appear, how to move and when to go.
// She has no collision and cannot be hurt. Her one eye always finds you.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WCEntity.generated.h"

class USkeletalMeshComponent;
class UStaticMeshComponent;
class UAnimSequence;
class UPointLightComponent;

UCLASS()
class WELLNESSCHECK_API AWCEntity : public AActor
{
	GENERATED_BODY()
public:
	AWCEntity();
	virtual void Tick(float Dt) override;

	/** Clips by name: Idle, Walk, Run, Peek, Rise, Tall, Crawl, Sit, Under, Lunge. Filled in by the level build script. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") TMap<FName, TObjectPtr<UAnimSequence>> Anims;
	/** Ground speed (cm/s) each moving clip was authored for. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") TMap<FName, float> AnimSpeeds;
	/** Eye centre measured on the model: X = cm toward her left, Y = cm forward of the body axis, Z = cm up. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FVector EyeRef = FVector(6.0f, 21.9f, 246.6f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") float EyeRadius = 4.3f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FName HeadBone = TEXT("Head");

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<USceneComponent> Root;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<USkeletalMeshComponent> Body;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<USceneComponent> Eye;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<UStaticMeshComponent> EyeBall;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<UStaticMeshComponent> Iris;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<UStaticMeshComponent> Pupil;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<UPointLightComponent> EyeGlint;

	void Appear(const FVector& Loc, float Yaw, FName Anim, bool bLoop = true, float Rate = 1.f);
	void Vanish();
	bool IsShown() const { return bShown; }
	void Play(FName Anim, bool bLoop = true, float Rate = 1.f);
	/** Travel through the points at Speed cm/s playing Anim; OnDone fires at the last point. */
	void MoveAlong(const TArray<FVector>& Points, float Speed, FName Anim, TFunction<void()> OnDone = nullptr);
	void Slide(const FVector& To, float Seconds, TFunction<void()> OnDone = nullptr);
	void StopMoving();
	bool IsMoving() const { return Path.Num() > 0 || SlideT >= 0.f; }
	void FacePlayer(bool bFace) { bFacePlayer = bFace; }
	void SetYaw(float Yaw);
	/** Kept for the story script; playback is always smooth now. */
	void SetStutter(float Fps) {}
	/** 0..1: how far her jaw is unhinged.  Set automatically from the clip (Run, Lunge, Rise, Crawl scream). */
	void SetScream(float Amount) { ScreamTarget = FMath::Clamp(Amount, 0.f, 1.f); }
	/** Faint cold light on her face (lumens; 0 = off). */
	void SetGlow(float Lumens);
	/** A faint cold light she carries while she is beyond the reach of his flashlight (0 = none: she is only found close to). */
	void SetFarGlow(float Lumens) { FarGlow = Lumens; }
	static constexpr float DefaultFarGlow = 320.f;
	float FarGlow = DefaultFarGlow;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> FarLight;
	/** How brightly her iris shines by itself (0.06 is the ordinary faint gleam). */
	void SetEyeShine(float Glow, float Swell = 1.f);
	UPROPERTY(Transient) TObjectPtr<class UMaterialInstanceDynamic> IrisMID;
	bool SegmentHits(const FVector& A, const FVector& B) const;
	FVector HeadLocation() const;
	FVector EyeLocation() const;
	float DistToPlayer() const;

protected:
	virtual void BeginPlay() override;

private:
	FVector RefPos(FName Bone) const;
	bool bShown = false;
	bool bFacePlayer = false;
	TArray<FVector> Path;
	int32 PathIndex = 0;
	float MoveSpeed = 0.f;
	TFunction<void()> MoveDone;
	FVector SlideFrom, SlideTo;
	float SlideT = -1.f, SlideDur = 1.f;
	TFunction<void()> SlideDone;
	FName CurrentAnim;
	bool bEyeReady = false;
	float ScreamTarget = 0.f;
	float ScreamAlpha = 0.f;
	float FaceT = 0.f, TalkLeft = 0.f, NextTwitch = 2.f, TwitchLeft = 0.f, StepAcc = 0.f;
public:
	/** Her mouth works for this long (she is speaking). */
	void Talk(float Seconds) { TalkLeft = FMath::Max(TalkLeft, Seconds); }
	FVector BoneWorld(FName Bone) const;
private:
	FQuat EyeQuat = FQuat::Identity;
};
