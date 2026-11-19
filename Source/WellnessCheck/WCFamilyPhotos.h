#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "WCFamilyPhotos.generated.h"

/** Dresses the existing Harrow picture frames when the house opens. */
UCLASS()
class WELLNESSCHECK_API UWCFamilyPhotos : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	virtual void OnWorldBeginPlay(UWorld& World) override;
};
