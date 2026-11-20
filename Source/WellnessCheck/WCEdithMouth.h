#pragma once

#include "CoreMinimal.h"
#include "Components/PoseableMeshComponent.h"
#include "WCEdithMouth.generated.h"

class USkeletalMeshComponent;
class UMaterialInstanceDynamic;

UCLASS()
class WELLNESSCHECK_API UWCEdithMouth : public UPoseableMeshComponent
{
	GENERATED_BODY()
public:
	void Fit(USkeletalMeshComponent* Body, FName Head, const FTransform& HeadRest, const FVector& Left, const FVector& Forward);
	void Pose(float Jaw, float Extension, float Time);
	void Close();
	bool IsOpen() const { return bOpen; }
private:
	static constexpr int32 JointCount = 65;
	UPROPERTY(Transient) TObjectPtr<USkeletalMeshComponent> Face;
	UPROPERTY(Transient) TObjectPtr<UMaterialInterface> RestSkin;
	UPROPERTY(Transient) TObjectPtr<UMaterialInstanceDynamic> OpenSkin;
	TArray<FVector> RestSpine;
	int32 TongueBones[JointCount]{};
	int32 ArchBones[2]{};
	bool bOpen = false;
};