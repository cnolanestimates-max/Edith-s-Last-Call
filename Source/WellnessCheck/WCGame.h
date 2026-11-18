// Game mode, player controller and the HUD (which also draws and runs every menu).
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "GameFramework/PlayerController.h"
#include "WCGame.generated.h"

class UFont;
class AWCDirector;

UCLASS()
class WELLNESSCHECK_API AWCGameMode : public AGameModeBase
{
	GENERATED_BODY()
public:
	AWCGameMode();
	virtual void StartPlay() override;
};

UCLASS()
class WELLNESSCHECK_API AWCPlayerController : public APlayerController
{
	GENERATED_BODY()
public:
	AWCPlayerController();
};

UENUM()
enum class EWCScreen : uint8 { None, Main, Pause, Settings, Controls };

UCLASS()
class WELLNESSCHECK_API AWCHUD : public AHUD
{
	GENERATED_BODY()
public:
	AWCHUD();
	virtual void DrawHUD() override;
	virtual void BeginPlay() override;

private:
	struct FItem { FString Label; FString Value; FName Id; bool bSlider = false; float Frac = 0.f; };

	float Px(float P) const;
	FVector2D Measure(const FString& S, float PxHeight, bool bTitle = false) const;
	void Text(const FString& S, float X, float Y, float PxHeight, const FLinearColor& C, int32 Align = 0, bool bTitle = false, bool bShadow = true);
	float Wrapped(const FString& S, float X, float Y, float MaxW, float PxHeight, const FLinearColor& C, int32 Align = 0, bool bShadow = true, bool bMeasureOnly = false);
	void Box(float X, float Y, float W, float H, const FLinearColor& C);

	void DrawGame(AWCDirector* D);
	void DrawNote(AWCDirector* D);
	void DrawMenu(AWCDirector* D);
	void DrawCredits(AWCDirector* D);
	void BuildItems(AWCDirector* D, TArray<FItem>& Out) const;
	void Activate(AWCDirector* D, const FItem& It, int32 Dir);
	void Open(EWCScreen S);
	void SetPaused(bool bPause);

	UPROPERTY(Transient) TObjectPtr<UFont> Font;
	UPROPERTY(Transient) TObjectPtr<UFont> TitleFont;
	EWCScreen Screen = EWCScreen::None;
	EWCScreen Back = EWCScreen::Main;
	int32 Sel = 0;
	float BaseH = 32.f;
	float TitleBaseH = 32.f;
	double RealNow = 0.0;
	double ScreenOpenedAt = 0.0;
	bool bSettingsDirty = false;
	FString MenuTestDir;
	int32 MenuTestStage = 0;
	double MenuTestAt = 0.0;
};
