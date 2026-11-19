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
enum class EWCScreen : uint8 { None, Main, Pause, Settings, Controls, Inventory };

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
	bool CanvasMouse(float& X, float& Y) const;
	void CycleBeam(AWCDirector* D, int32 Direction);
	FVector2D Measure(const FString& S, float PxHeight, bool bTitle = false) const;
	void Text(const FString& S, float X, float Y, float PxHeight, const FLinearColor& C, int32 Align = 0, bool bTitle = false, bool bShadow = true);
	float Wrapped(const FString& S, float X, float Y, float MaxW, float PxHeight, const FLinearColor& C, int32 Align = 0, bool bShadow = true, bool bMeasureOnly = false);
	void Box(float X, float Y, float W, float H, const FLinearColor& C);

	void DrawGame(AWCDirector* D);
	void DrawNote(AWCDirector* D);
	void DrawMenu(AWCDirector* D);
	void DrawCredits(AWCDirector* D);

	// inventory
	struct FInvItem { FName Id; FString Name; FString Desc; };
	void DrawInventory(AWCDirector* D);
	void DrawNotePage(const class AWCNote* N, const TCHAR* Footer);
	void OpenInventory(AWCDirector* D);
	void CloseInventory(AWCDirector* D);
	void BuildInventory(AWCDirector* D, TArray<FInvItem>& Out) const;
	void ShowInvItem(AWCDirector* D, FName Id);
	void InvUse(AWCDirector* D, FName Id);
	bool InvCanDrop(AWCDirector* D, FName Id, FString& Why) const;
	void InvDrop(AWCDirector* D, FName Id);
	void InvSay(const FString& Line) { InvMsg = Line; InvMsgUntil = RealNow + 3.5; }
	int32 InvSel = 0, InvAct = 0, InvTab = 0, InvPaper = 0;
	bool bInvInspect = false;
	float InvYaw = 0.f, InvPitch = 0.f, InvZoom = 1.f, InvMX = 0.f, InvMY = 0.f;
	double InvLast = 0.0, InvMsgUntil = 0.0, InvTouchedAt = -10.0;
	FName InvShown;
	FString InvMsg;
	TWeakObjectPtr<class AWCInteractable> InvFocus;
	TWeakObjectPtr<class AWCNote> InvNote;
	FString InvTestDir;
	int32 InvTestStage = 0;
	double InvTestAt = 0.0;
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
	bool bDisplayModePending = false;
	FString MenuTestDir;
	int32 MenuTestStage = 0;
	double MenuTestAt = 0.0;
};
