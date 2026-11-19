#include "WCGame.h"
#include "WCCharacter.h"
#include "WCDirector.h"
#include "WCWorld.h"

#include "CanvasItem.h"
#include "Containers/Ticker.h"
#include "Engine/Canvas.h"
#include "Engine/GameViewportClient.h"
#include "SceneView.h"
#include "Engine/Font.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "HAL/FileManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "Materials/MaterialInterface.h"

// ---------------------------------------------------------------------------------------------- game mode / controller
AWCGameMode::AWCGameMode()
{
	DefaultPawnClass = AWCCharacter::StaticClass();
	HUDClass = AWCHUD::StaticClass();
	PlayerControllerClass = AWCPlayerController::StaticClass();
}

void AWCGameMode::StartPlay()
{
	if (!AWCDirector::Get(this))
	{
		GetWorld()->SpawnActor<AWCDirector>(AWCDirector::StaticClass(), FTransform::Identity);
	}
	Super::StartPlay();
}

AWCPlayerController::AWCPlayerController()
{
	bShouldPerformFullTickWhenPaused = true;
}

// ---------------------------------------------------------------------------------------------- HUD basics
static const FLinearColor Ink(0.86f, 0.84f, 0.78f, 1.f);
static const FLinearColor Dim(0.55f, 0.54f, 0.5f, 1.f);
static const FLinearColor Hot(1.f, 0.93f, 0.72f, 1.f);

AWCHUD::AWCHUD()
{
	PrimaryActorTick.bTickEvenWhenPaused = true;
}

void AWCHUD::BeginPlay()
{
	Super::BeginPlay();
	Font = LoadObject<UFont>(nullptr, TEXT("/Engine/EngineFonts/RobotoDistanceField.RobotoDistanceField"));
	TitleFont = LoadObject<UFont>(nullptr, TEXT("/Game/WC/UI/F_Title.F_Title"), nullptr, LOAD_NoWarn | LOAD_Quiet);
	if (!TitleFont) TitleFont = Font;
	if (Font) BaseH = FMath::Max(Font->GetMaxCharHeight(), 1.f);
	if (TitleFont) TitleBaseH = FMath::Max(TitleFont->GetMaxCharHeight(), 1.f);
	if (FParse::Value(FCommandLine::Get(), TEXT("WCMenuTest="), MenuTestDir))
	{
		MenuTestDir = FPaths::ConvertRelativePathToFull(MenuTestDir);
		IFileManager::Get().MakeDirectory(*MenuTestDir, true);
		MenuTestAt = FPlatformTime::Seconds() + 9.0;
	}
	if (FParse::Value(FCommandLine::Get(), TEXT("WCInvTest="), InvTestDir))
	{
		InvTestDir = FPaths::ConvertRelativePathToFull(InvTestDir);
		IFileManager::Get().MakeDirectory(*InvTestDir, true);
	}
}

float AWCHUD::Px(float P) const
{
	return Canvas ? P * Canvas->SizeY / 1080.f : P;
}

bool AWCHUD::CanvasMouse(float& X, float& Y) const
{
	if (!GetOwningPlayerController()->GetMousePosition(X, Y)) return false;
	if (Canvas->SceneView)
	{
		X -= Canvas->SceneView->UnscaledViewRect.Min.X;
		Y -= Canvas->SceneView->UnscaledViewRect.Min.Y;
	}
	return true;
}

FVector2D AWCHUD::Measure(const FString& S, float PxHeight, bool bTitle) const
{
	const UFont* F = bTitle ? TitleFont : Font;
	if (!F || !Canvas) return FVector2D::ZeroVector;
	const float Scale = PxHeight / (bTitle ? TitleBaseH : BaseH);
	float W = 0.f, H = 0.f;
	Canvas->TextSize(F, S, W, H, Scale, Scale);
	return FVector2D(W, H);
}

void AWCHUD::Text(const FString& S, float X, float Y, float PxHeight, const FLinearColor& C, int32 Align, bool bTitle, bool bShadow)
{
	UFont* F = bTitle ? TitleFont : Font;
	if (!F || !Canvas || S.IsEmpty()) return;
	const float Scale = PxHeight / (bTitle ? TitleBaseH : BaseH);
	if (Align != 0)
	{
		const FVector2D M = Measure(S, PxHeight, bTitle);
		X -= Align == 1 ? M.X * 0.5f : M.X;
	}
	FCanvasTextItem Item(FVector2D(X, Y), FText::FromString(S), F, C);
	Item.Scale = FVector2D(Scale, Scale);
	if (bShadow) Item.EnableShadow(FLinearColor(0, 0, 0, C.A * 0.9f), FVector2D(1.5f, 1.5f));
	Item.BlendMode = SE_BLEND_Translucent;
	Canvas->DrawItem(Item);
}

float AWCHUD::Wrapped(const FString& S, float X, float Y, float MaxW, float PxHeight, const FLinearColor& C, int32 Align, bool bShadow, bool bMeasureOnly)
{
	const float LineH = PxHeight * 1.32f;
	float Cy = Y;
	TArray<FString> Paras;
	S.ParseIntoArray(Paras, TEXT("\n"), false);
	for (const FString& Para : Paras)
	{
		if (Para.TrimStartAndEnd().IsEmpty()) { Cy += LineH * 0.7f; continue; }
		TArray<FString> Words;
		Para.ParseIntoArray(Words, TEXT(" "), true);
		FString Line;
		for (const FString& W : Words)
		{
			const FString Try = Line.IsEmpty() ? W : Line + TEXT(" ") + W;
			if (Measure(Try, PxHeight).X > MaxW && !Line.IsEmpty())
			{
				if (!bMeasureOnly) Text(Line, Align == 1 ? X + MaxW * 0.5f : X, Cy, PxHeight, C, Align, false, bShadow);
				Cy += LineH;
				Line = W;
			}
			else Line = Try;
		}
		if (!Line.IsEmpty())
		{
			if (!bMeasureOnly) Text(Line, Align == 1 ? X + MaxW * 0.5f : X, Cy, PxHeight, C, Align, false, bShadow);
			Cy += LineH;
		}
	}
	return Cy - Y;
}

void AWCHUD::Box(float X, float Y, float W, float H, const FLinearColor& C)
{
	FCanvasTileItem Tile(FVector2D(X, Y), FVector2D(W, H), C);
	Tile.BlendMode = SE_BLEND_Translucent;
	Canvas->DrawItem(Tile);
}

void AWCHUD::SetPaused(bool bPause)
{
	UGameplayStatics::SetGamePaused(this, bPause);
}

void AWCHUD::Open(EWCScreen S)
{
	Screen = S;
	Sel = 0;
	ScreenOpenedAt = RealNow;
	if (APlayerController* PC = GetOwningPlayerController())
	{
		const bool bUI = S != EWCScreen::None;
		PC->SetShowMouseCursor(bUI);
		if (bUI) { FInputModeGameAndUI M; M.SetHideCursorDuringCapture(false); PC->SetInputMode(M); }
		else PC->SetInputMode(FInputModeGameOnly());
	}
}

// ---------------------------------------------------------------------------------------------- frame
void AWCHUD::DrawHUD()
{
	Super::DrawHUD();
	AWCDirector* D = AWCDirector::Get(this);
	APlayerController* PC = GetOwningPlayerController();
	if (!D || !Canvas || !PC) return;
	RealNow = FPlatformTime::Seconds();

	// menu state follows the game mode
	if (D->Mode == EWCMode::Menu && Screen == EWCScreen::None) Open(EWCScreen::Main);
	if (D->Mode == EWCMode::Playing && Screen == EWCScreen::Main) Open(EWCScreen::None);
	const bool bEsc = PC->WasInputKeyJustPressed(EKeys::Escape) || PC->WasInputKeyJustPressed(EKeys::Gamepad_Special_Right);
	if (D->bAuto && Screen == EWCScreen::Pause && RealNow - ScreenOpenedAt > 10.0)
	{
		// a test run was paused (somebody touched the keyboard): carry on by itself
		Open(EWCScreen::None);
		SetPaused(false);
	}
	const bool bInvKey = PC->WasInputKeyJustPressed(EKeys::Tab) || PC->WasInputKeyJustPressed(EKeys::I) || PC->WasInputKeyJustPressed(EKeys::Gamepad_Special_Left);
	if (D->Mode == EWCMode::Playing && bInvKey)
	{
		AWCCharacter* Pl = D->Player();
		if (Screen == EWCScreen::Inventory) CloseInventory(D);
		else if (Screen == EWCScreen::None && !D->ActiveNote.IsValid() && D->Fade < 0.5f && !D->bBusy && !D->IsDriving() && Pl && !Pl->IsDown() && !Pl->IsInputLocked()) OpenInventory(D);
	}
	if (D->Mode != EWCMode::Playing && Screen == EWCScreen::Inventory) CloseInventory(D);
	if (D->Mode == EWCMode::Playing && bEsc && Screen == EWCScreen::Inventory)
	{
		if (InvNote.IsValid()) InvNote = nullptr;
		else if (bInvInspect) bInvInspect = false;
		else CloseInventory(D);
	}
	else if (D->Mode == EWCMode::Playing && bEsc)
	{
		if (D->ActiveNote.IsValid()) D->CloseNote();
		else if (Screen == EWCScreen::None && D->Fade < 0.9f) { Back = EWCScreen::Pause; Open(EWCScreen::Pause); SetPaused(true); }
		else if (Screen == EWCScreen::Pause) { Open(EWCScreen::None); SetPaused(false); }
		else if (Screen == EWCScreen::Settings || Screen == EWCScreen::Controls) Open(Back);
	}
	else if (D->Mode == EWCMode::Menu && bEsc && Screen != EWCScreen::Main) Open(EWCScreen::Main);
	if ((D->Mode == EWCMode::Credits || D->Mode == EWCMode::Ending) && bEsc) D->QuitToMenu();

	if (D->Mode == EWCMode::Playing && Screen == EWCScreen::None)
	{
		AWCCharacter* Pl = D->Player();
		if (Pl && !Pl->IsInputLocked() && !D->ActiveNote.IsValid() && !D->IsDriving())
		{
			if (PC->WasInputKeyJustPressed(EKeys::LeftBracket)) CycleBeam(D, -1);
			else if (PC->WasInputKeyJustPressed(EKeys::RightBracket)) CycleBeam(D, 1);
		}
		DrawGame(D);
	}
	if (D->Fade > 0.003f) Box(0, 0, Canvas->SizeX, Canvas->SizeY, FLinearColor(0, 0, 0, D->Fade));
	if (D->Mode == EWCMode::Playing && Screen == EWCScreen::None && D->Fade > 0.5f)
	{
		// subtitles stay readable over black
		float Y = Canvas->SizeY - Px(150.f);
		if (AWCDirector::Settings.bSubtitles) for (const FWCSubtitle& S : D->Subtitles)
		{
			const FString Line = S.Speaker.IsEmpty() ? S.Text : FString::Printf(TEXT("%s: %s"), *S.Speaker, *S.Text);
			Wrapped(Line, Canvas->SizeX * 0.2f, Y, Canvas->SizeX * 0.6f, Px(27.f), Ink, 1);
		}
	}
	if (D->BigAlpha > 0.01f)
	{
		const FLinearColor C(0.88f, 0.86f, 0.8f, D->BigAlpha);
		Text(D->BigText, Canvas->SizeX * 0.5f, Canvas->SizeY * 0.42f, Px(88.f), C, 1, true);
		if (!D->BigSub.IsEmpty()) Text(D->BigSub, Canvas->SizeX * 0.5f, Canvas->SizeY * 0.42f + Px(110.f), Px(28.f), FLinearColor(0.6f, 0.6f, 0.58f, D->BigAlpha), 1);
	}
	if (D->Mode == EWCMode::Credits) DrawCredits(D);
	if (Screen == EWCScreen::Inventory) DrawInventory(D);
	else if (Screen != EWCScreen::None) DrawMenu(D);
	if (!InvTestDir.IsEmpty() && D->Mode == EWCMode::Playing)
	{
		// -WCInvTest=<dir>: fill the bag, open it, photograph every thing in Inspect (the doll from both sides, and emptied), quit
		struct FInvShot { const TCHAR* Item; float Yaw, Pitch; const TCHAR* Name; const TCHAR* Before; };
		static const FInvShot Shots[] = {
			{ TEXT(""), 0.f, 0.f, TEXT("inv_00_list"), nullptr },
			{ TEXT("doll"), 0.f, 0.f, TEXT("inv_01_doll_front"), nullptr }, { TEXT("doll"), 180.f, -10.f, TEXT("inv_02_doll_back_prompt"), nullptr },
			{ TEXT("doll_empty"), 180.f, -10.f, TEXT("inv_03_doll_emptied"), TEXT("inspect:doll") }, { TEXT("key_box"), 20.f, 0.f, TEXT("inv_04_small_key"), nullptr },
			{ TEXT("screwdriver"), 25.f, 0.f, TEXT("inv_05_screwdriver"), nullptr }, { TEXT("keep_eye"), 0.f, 0.f, TEXT("inv_06_glass_eye"), nullptr },
			{ TEXT("keep_eye"), 0.f, -55.f, TEXT("inv_07_glass_eye_iris"), nullptr }, { TEXT("key_sitting"), 20.f, 0.f, TEXT("inv_08_brass_key"), nullptr },
			{ TEXT("key_prayer"), 20.f, 0.f, TEXT("inv_09_iron_key"), nullptr }, { TEXT("key_desk"), 20.f, 0.f, TEXT("inv_10_desk_key"), nullptr },
			{ TEXT("key_ell"), 15.f, 0.f, TEXT("inv_11_keyring"), nullptr }, { TEXT("key_attic"), 20.f, 0.f, TEXT("inv_12_long_key"), nullptr },
			{ TEXT("key_cellar"), 20.f, 0.f, TEXT("inv_13_padlock_key"), nullptr }, { TEXT("fuse"), 30.f, 10.f, TEXT("inv_14_fuse"), nullptr },
			{ TEXT("shears"), 35.f, 18.f, TEXT("inv_15_shears"), nullptr }, { TEXT("keep_walter"), 30.f, 20.f, TEXT("inv_16_ring"), nullptr },
			{ TEXT("keep_daniel"), 10.f, 0.f, TEXT("inv_17_tags"), nullptr }, { TEXT("keep_ruth"), 30.f, 10.f, TEXT("inv_18_music_box"), nullptr },
			{ TEXT("pistol"), 0.f, 0.f, TEXT("inv_19_pistol"), nullptr }, { TEXT("!papers"), 0.f, 0.f, TEXT("inv_20_papers"), nullptr },
		};
		static const TCHAR* Give[] = { TEXT("doll"), TEXT("screwdriver"), TEXT("keep_eye"), TEXT("key_sitting"), TEXT("key_prayer"), TEXT("key_desk"), TEXT("key_ell"), TEXT("key_attic"),
			TEXT("key_cellar"), TEXT("fuse"), TEXT("shears"), TEXT("keep_ruth"), TEXT("keep_walter"), TEXT("keep_daniel") };
		const int32 NShots = UE_ARRAY_COUNT(Shots);
		static int32 SetFor = -1;
		if (InvTestStage == 0 && D->PlaySeconds > 7.f && Screen == EWCScreen::None)
		{
			for (const TCHAR* G : Give) D->Items.Add(G);
			int32 n = 0;
			for (TActorIterator<AWCNote> It(GetWorld()); It && n < 9; ++It, ++n) D->NotesRead.AddUnique(It->WCId);
			D->bBusy = false;
			OpenInventory(D);
			InvTestStage = 1;
			InvTestAt = RealNow + 2.5;
		}
		else if (InvTestStage >= 1 && InvTestStage <= NShots && Screen == EWCScreen::Inventory)
		{
			const FInvShot& S = Shots[InvTestStage - 1];
			if (SetFor != InvTestStage && RealNow > InvTestAt - 1.9)
			{
				SetFor = InvTestStage;
				if (S.Before) D->Event(S.Before);
				TArray<FInvItem> Now;
				BuildInventory(D, Now);
				const bool bPapers = FCString::Strcmp(S.Item, TEXT("!papers")) == 0;
				InvTab = bPapers ? 1 : 0;
				bInvInspect = !bPapers && S.Item[0] != 0;
				for (int32 i = 0; i < Now.Num(); ++i) if (Now[i].Id == FName(S.Item)) InvSel = i;
			}
			if (SetFor == InvTestStage) { InvYaw = S.Yaw; InvPitch = S.Pitch; InvTouchedAt = RealNow; }
			if (RealNow > InvTestAt)
			{
				FScreenshotRequest::RequestScreenshot(InvTestDir / (FString(S.Name) + TEXT(".png")), true, false);
				++InvTestStage;
				InvTestAt = RealNow + 2.2;
			}
		}
		else if (InvTestStage == NShots + 1 && RealNow > InvTestAt)
		{
			++InvTestStage;
			UKismetSystemLibrary::QuitGame(this, PC, EQuitPreference::Quit, false);
		}
	}
	if (!MenuTestDir.IsEmpty() && RealNow > MenuTestAt)
	{
		static const TCHAR* Names[] = { TEXT("menu_main"), TEXT("menu_settings"), TEXT("menu_controls") };
		if (MenuTestStage < 3)
		{
			if (FParse::Param(FCommandLine::Get(), TEXT("WCDisplayTest")) && GetWorld()->GetGameViewport())
			{
				FViewport* View = GetWorld()->GetGameViewport()->Viewport;
				if (View)
				{
					UE_LOG(LogTemp, Display, TEXT("WCDISPLAY selected=%d fullscreen=%d size=%s"),
						AWCDirector::Settings.bFullscreen, View->IsFullscreen(), *View->GetSizeXY().ToString());
					if (MenuTestStage < 2) { FItem Toggle; Toggle.Id = TEXT("full"); Activate(D, Toggle, 0); }
				}
			}
			FScreenshotRequest::RequestScreenshot(MenuTestDir / (FString(Names[MenuTestStage]) + TEXT(".png")), true, false);
			++MenuTestStage;
			MenuTestAt = RealNow + 1.5;
			// the next screen is opened a moment after this capture is taken
		}
		else if (MenuTestStage == 3)
		{
			UKismetSystemLibrary::QuitGame(this, PC, EQuitPreference::Quit, false);
			++MenuTestStage;
		}
	}
	else if (!MenuTestDir.IsEmpty() && MenuTestStage > 0 && MenuTestStage < 3 && RealNow > MenuTestAt - 1.0)
	{
		const EWCScreen Want = MenuTestStage == 1 ? EWCScreen::Settings : EWCScreen::Controls;
		if (Screen != Want) { Back = EWCScreen::Main; Open(Want); }
	}
}

// ---------------------------------------------------------------------------------------------- in-game overlay
static FString ItemName(FName Id)
{
	static const TMap<FName, FString> Names = {
		{ TEXT("key_sitting"), TEXT("Small brass key") }, { TEXT("key_prayer"), TEXT("Iron key on a ribbon") },
		{ TEXT("key_attic"), TEXT("Long key") }, { TEXT("key_cellar"), TEXT("Padlock key") },
		{ TEXT("keep_ruth"), TEXT("Ruth's music box") }, { TEXT("keep_walter"), TEXT("Walter's wedding ring") },
		{ TEXT("keep_daniel"), TEXT("Daniel's dog tags") }, { TEXT("key_desk"), TEXT("Small desk key") },
		{ TEXT("key_ell"), TEXT("Walter's keys (upstairs back rooms)") }, { TEXT("fuse"), TEXT("Spare fuse") }, { TEXT("shears"), TEXT("Sewing shears") } };
	const FString* N = Names.Find(Id);
	return N ? *N : Id.ToString();
}

void AWCHUD::DrawGame(AWCDirector* D)
{
	AWCCharacter* P = D->Player();
	APlayerController* PC = GetOwningPlayerController();
	if (!P) return;
	const float W = Canvas->SizeX, H = Canvas->SizeY;
	const double Now = D->Now();

	if (D->ActiveNote.IsValid()) { DrawNote(D); return; }

	// centre dot and prompt
	if (!P->IsDown() && !P->IsInputLocked())
	{
		const AWCInteractable* F = P->GetFocus();
		const float R = Px(F ? 3.f : 1.6f);
		Box(W * 0.5f - R, H * 0.5f - R, R * 2, R * 2, FLinearColor(1, 1, 1, F ? 0.85f : 0.28f));
		if (F) Text(FString::Printf(TEXT("[E]  %s"), *F->GetPrompt()), W * 0.5f, H * 0.5f + Px(26.f), Px(24.f), Ink, 1);
	}
	if (P->IsGunUp())
	{
		Text(FString::Printf(TEXT("%d / %d"), P->Ammo, P->Reserve), W - Px(60.f), H - Px(90.f), Px(30.f), Ink, 2);
	}

	// objective: shown for a while after it changes, or while Tab is held
	const bool bTab = false;       // Tab opens the inventory now, which shows all of this
	const float Age = (float)(Now - D->ObjectiveShownAt);
	float OA = bTab ? 1.f : FMath::Clamp(FMath::Min(Age / 0.6f, (9.f - Age) / 1.5f), 0.f, 1.f);
	if (!D->Objective.IsEmpty() && OA > 0.01f)
	{
		Text(TEXT("OBJECTIVE"), Px(60.f), Px(56.f), Px(17.f), FLinearColor(Dim.R, Dim.G, Dim.B, OA));
		Text(D->Objective, Px(60.f), Px(80.f), Px(27.f), FLinearColor(Ink.R, Ink.G, Ink.B, OA));
	}
	if (bTab)
	{
		float Y = Px(140.f);
		Text(TEXT("CARRYING"), Px(60.f), Y, Px(17.f), Dim); Y += Px(26.f);
		if (D->Items.Num() == 0) { Text(TEXT("Flashlight, service pistol, radio"), Px(60.f), Y, Px(22.f), Ink); }
		for (const FName& It : D->Items) { if (It.ToString().StartsWith(TEXT("ammo"))) continue; Text(ItemName(It), Px(60.f), Y, Px(22.f), Ink); Y += Px(30.f); }
		if (D->NotesRead.Contains(TEXT("note_prayer")) || D->NotesRead.Contains(TEXT("note_cellar")))
		{
			Y += Px(22.f);
			Text(TEXT("WHAT WAS THEIRS"), Px(60.f), Y, Px(17.f), Dim); Y += Px(26.f);
			static const TCHAR* Keep[][2] = { { TEXT("keep_ruth"), TEXT("Ruth's music box (under her bed)") }, { TEXT("keep_walter"), TEXT("Walter's ring (with her knots)") }, { TEXT("keep_daniel"), TEXT("Daniel's tags (his footlocker, attic)") }, { TEXT("shears"), TEXT("Something to cut the knots (her sewing shears)") } };
			for (const auto& K : Keep)
			{
				const bool bHave = D->Items.Contains(K[0]);
				Text(FString::Printf(TEXT("%s  %s"), bHave ? TEXT("[x]") : TEXT("[  ]"), K[1]), Px(60.f), Y, Px(22.f), bHave ? Ink : Dim); Y += Px(30.f);
			}
			Text(TEXT("Bring them to where she lies. Cut the three knots."), Px(60.f), Y + Px(6.f), Px(20.f), Dim);
		}
	}

	if (Now < D->ToastUntil) Text(D->Toast, W * 0.5f, H * 0.66f, Px(24.f), Hot, 1);
	if (Now < D->HintUntil)
	{
		const float A = FMath::Clamp((float)(D->HintUntil - Now) / 1.2f, 0.f, 1.f);
		Text(D->Hint, W * 0.5f, H - Px(70.f), Px(21.f), FLinearColor(Dim.R, Dim.G, Dim.B, A), 1);
	}

	if (AWCDirector::Settings.bSubtitles && D->Fade <= 0.5f)
	{
		float Y = H - Px(170.f);
		for (const FWCSubtitle& S : D->Subtitles)
		{
			const FString Line = S.Speaker.IsEmpty() ? S.Text : FString::Printf(TEXT("%s: %s"), *S.Speaker, *S.Text);
			const float Hh = Wrapped(Line, W * 0.2f, Y, W * 0.6f, Px(27.f), Ink, 1, true, true);
			Box(W * 0.19f, Y - Px(8.f), W * 0.62f, Hh + Px(12.f), FLinearColor(0, 0, 0, 0.45f));
			Wrapped(Line, W * 0.2f, Y, W * 0.6f, Px(27.f), Ink, 1);
			Y += Hh + Px(10.f);
		}
	}
}

void AWCHUD::DrawNote(AWCDirector* D)
{
	DrawNotePage(D->ActiveNote.Get(), TEXT("[E] Put it back"));
}

void AWCHUD::DrawNotePage(const AWCNote* N, const TCHAR* Footer)
{
	if (!N) return;
	const float W = Canvas->SizeX, H = Canvas->SizeY;
	Box(0, 0, W, H, FLinearColor(0, 0, 0, 0.72f));
	const float PW = FMath::Min(Px(820.f), W * 0.86f);
	const float X = (W - PW) * 0.5f;
	const float Pad = Px(54.f);
	const float Size = Px(N->Style == 2 ? 30.f : 26.f);
	const FLinearColor Paper = N->Style == 0 ? FLinearColor(0.74f, 0.72f, 0.66f, 1.f) : (N->Style == 2 ? FLinearColor(0.78f, 0.76f, 0.62f, 1.f) : FLinearColor(0.70f, 0.64f, 0.52f, 1.f));
	const FLinearColor InkC = N->Style == 2 ? FLinearColor(0.32f, 0.07f, 0.06f, 1.f) : FLinearColor(0.07f, 0.06f, 0.07f, 1.f);
	const float BodyH = Wrapped(N->Body, X + Pad, 0, PW - 2 * Pad, Size, InkC, 0, false, true);
	const float PH = FMath::Min(BodyH + Pad * 2 + Px(60.f), H * 0.9f);
	const float Y = (H - PH) * 0.5f;
	Box(X + Px(8.f), Y + Px(10.f), PW, PH, FLinearColor(0, 0, 0, 0.6f));
	Box(X, Y, PW, PH, Paper);
	Box(X, Y, PW, Px(3.f), FLinearColor(0, 0, 0, 0.12f));
	if (!N->Title.IsEmpty()) Text(N->Title, X + Pad, Y + Pad * 0.55f, Px(19.f), FLinearColor(InkC.R, InkC.G, InkC.B, 0.6f), 0, false, false);
	Wrapped(N->Body, X + Pad, Y + Pad + Px(24.f), PW - 2 * Pad, Size, InkC, 0, false);
	Text(Footer, W * 0.5f, Y + PH + Px(18.f), Px(21.f), Dim, 1);
}

void AWCHUD::DrawCredits(AWCDirector* D)
{
	static const TCHAR* Lines[] = {
		TEXT("#EDITH'S LAST CALL"), TEXT(""), TEXT(""),
		TEXT("#Created by"), TEXT("Cheyenne"), TEXT(""),
		TEXT("#Design, writing, code, animation"), TEXT("Built with Claude"), TEXT(""),
		TEXT("#Voices"), TEXT("Deputy Cole Brandt"), TEXT("Dispatch"), TEXT("Edith Harrow"), TEXT("Synthesised with Google Gemini text-to-speech"), TEXT(""),
		TEXT("#Music"), TEXT("Kevin MacLeod (incompetech.com)"), TEXT("Darren Curtis (darrencurtismusic.com)"), TEXT("Licensed under Creative Commons: By Attribution 4.0"), TEXT(""),
		TEXT("#Sound"), TEXT("Sonniss GDC Game Audio Bundle"), TEXT("Kenney (CC0)"), TEXT(""),
		TEXT("#Environment and props"), TEXT("Assets from Fab, used under the Fab Standard License"), TEXT("Megascans and Megaplants by Quixel"), TEXT(""),
		TEXT("#Made with"), TEXT("Unreal Engine"), TEXT(""), TEXT(""),
		TEXT("Unreal Engine and its logo are trademarks of Epic Games, Inc."), TEXT(""), TEXT(""), TEXT(""),
		TEXT("Thank you for staying."),
	};
	const float W = Canvas->SizeX, H = Canvas->SizeY;
	float Y = H - D->CreditsScroll * Px(46.f);
	for (const TCHAR* L : Lines)
	{
		FString S(L);
		const bool bHead = S.StartsWith(TEXT("#"));
		if (bHead) S.RightChopInline(1);
		if (Y > -Px(60.f) && Y < H + Px(20.f)) Text(S, W * 0.5f, Y, Px(bHead ? 20.f : 30.f), bHead ? Dim : Ink, 1, false, false);
		Y += Px(bHead ? 34.f : 46.f);
	}
}

// ---------------------------------------------------------------------------------------------- menus
static FString Pct(float V) { return FString::Printf(TEXT("%d%%"), FMath::RoundToInt(V * 100.f)); }
static FString OnOff(bool b) { return b ? TEXT("On") : TEXT("Off"); }

void AWCHUD::BuildItems(AWCDirector* D, TArray<FItem>& Out) const
{
	const FWCSettings& S = AWCDirector::Settings;
	auto Add = [&Out](const TCHAR* Label, const FString& Value, const TCHAR* Id, bool bSlider = false, float Frac = 0.f)
	{
		FItem I; I.Label = Label; I.Value = Value; I.Id = Id; I.bSlider = bSlider; I.Frac = Frac; Out.Add(I);
	};
	if (Screen == EWCScreen::Main)
	{
		if (D->HasSave()) Add(TEXT("Continue"), TEXT(""), TEXT("continue"));
		Add(TEXT("New Game"), TEXT(""), TEXT("new"));
		Add(TEXT("Settings"), TEXT(""), TEXT("settings"));
		Add(TEXT("Controls"), TEXT(""), TEXT("controls"));
		Add(TEXT("Quit"), TEXT(""), TEXT("quit"));
	}
	else if (Screen == EWCScreen::Pause)
	{
		Add(TEXT("Resume"), TEXT(""), TEXT("resume"));
		Add(TEXT("Reload last checkpoint"), TEXT(""), TEXT("restart"));
		Add(TEXT("Settings"), TEXT(""), TEXT("settings"));
		Add(TEXT("Controls"), TEXT(""), TEXT("controls"));
		Add(TEXT("Quit to menu"), TEXT(""), TEXT("tomenu"));
		Add(TEXT("Quit to desktop"), TEXT(""), TEXT("quit"));
	}
	else if (Screen == EWCScreen::Settings)
	{
		static const TCHAR* Q[] = { TEXT("Low"), TEXT("Medium"), TEXT("High"), TEXT("Epic") };
		Add(TEXT("Mouse sensitivity"), FString::Printf(TEXT("%.2f"), S.Sensitivity), TEXT("sens"), true, (S.Sensitivity - 0.2f) / 2.8f);
		Add(TEXT("Invert look"), OnOff(S.bInvertY), TEXT("invert"));
		Add(TEXT("Field of view"), FString::Printf(TEXT("%d"), FMath::RoundToInt(S.FOV)), TEXT("fov"), true, (S.FOV - 65.f) / 40.f);
		Add(TEXT("Brightness"), FString::Printf(TEXT("%.2f"), S.Gamma), TEXT("gamma"), true, (S.Gamma - 1.6f) / 1.4f);
		Add(TEXT("Flashlight beam width"), S.BeamLabel(), TEXT("beam"));
		Add(TEXT("Master volume"), Pct(S.VolMaster), TEXT("vmaster"), true, S.VolMaster);
		Add(TEXT("Effects volume"), Pct(S.VolSFX), TEXT("vsfx"), true, S.VolSFX);
		Add(TEXT("Music volume"), Pct(S.VolMusic), TEXT("vmusic"), true, S.VolMusic);
		Add(TEXT("Voice volume"), Pct(S.VolVoice), TEXT("vvoice"), true, S.VolVoice);
		Add(TEXT("Subtitles"), OnOff(S.bSubtitles), TEXT("subs"));
		Add(TEXT("Head bob"), OnOff(S.bHeadBob), TEXT("bob"));
		Add(TEXT("Camera shake"), OnOff(S.bCameraShake), TEXT("shake"));
		static const TCHAR* Pic[6] = { TEXT("Clean"), TEXT("VHS camcorder"), TEXT("Old film"), TEXT("Cold"), TEXT("Fisheye bodycam"), TEXT("Night vision") };
		Add(TEXT("Picture"), Pic[FMath::Clamp(S.Filter, 0, 5)], TEXT("picture"));
		Add(TEXT("Graphics quality"), Q[FMath::Clamp(S.Quality, 0, 3)], TEXT("quality"));
		Add(TEXT("Fullscreen"), OnOff(S.bFullscreen), TEXT("full"));
		Add(TEXT("VSync"), OnOff(S.bVSync), TEXT("vsync"));
		Add(TEXT("Back"), TEXT(""), TEXT("back"));
	}
	else if (Screen == EWCScreen::Controls)
	{
		Add(TEXT("Back"), TEXT(""), TEXT("back"));
	}
}

void AWCHUD::CycleBeam(AWCDirector* D, int32 Direction)
{
	FWCSettings& S = AWCDirector::Settings;
	S.BeamChoice = (S.BeamChoice + (Direction < 0 ? -1 : 1) + S.BeamChoices) % S.BeamChoices;
	if (AWCCharacter* P = D->Player()) P->ApplyBeamWidth();
	S.Save();
	if (Screen == EWCScreen::None) D->ShowToast(TEXT("Flashlight ") + S.BeamLabel());
}

void AWCHUD::Activate(AWCDirector* D, const FItem& It, int32 Dir)
{
	FWCSettings& S = AWCDirector::Settings;
	const FName Id = It.Id;
	const bool bPress = Dir == 0;
	const float Step = Dir == 0 ? 1.f : (float)Dir;
	bool bChanged = true;
	if (Id == TEXT("continue") && bPress) { D->ContinueGame(); return; }
	if (Id == TEXT("new") && bPress) { D->StartNewGame(); return; }
	if (Id == TEXT("settings") && bPress) { Back = Screen; Open(EWCScreen::Settings); return; }
	if (Id == TEXT("controls") && bPress) { Back = Screen; Open(EWCScreen::Controls); return; }
	if (Id == TEXT("quit") && bPress) { UKismetSystemLibrary::QuitGame(this, GetOwningPlayerController(), EQuitPreference::Quit, false); return; }
	if (Id == TEXT("resume") && bPress) { Open(EWCScreen::None); SetPaused(false); return; }
	if (Id == TEXT("restart") && bPress) { SetPaused(false); D->RestartFromCheckpoint(); return; }
	if (Id == TEXT("tomenu") && bPress) { SetPaused(false); D->QuitToMenu(); return; }
	if (Id == TEXT("back") && bPress) { Open(Back); return; }
	if (Id == TEXT("beam")) { CycleBeam(D, Dir); return; }
	if (Id == TEXT("full"))
	{
		if (bDisplayModePending) return;
		bDisplayModePending = true;
		ScreenOpenedAt = FPlatformTime::Seconds();
		S.bFullscreen = !S.bFullscreen;
		S.Save();
		D->Play2D(TEXT("ui_tick"), 0.5f);
		// Resizing draws the viewport synchronously. Finish this HUD frame before applying it.
		FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateWeakLambda(this, [this](float)
		{
			AWCDirector::Settings.ApplyDisplayMode(GetWorld());
			bDisplayModePending = false;
			return false;
		}));
		return;
	}

	if (Id == TEXT("sens")) S.Sensitivity = FMath::Clamp(S.Sensitivity + 0.1f * Step, 0.2f, 3.f);
	else if (Id == TEXT("invert")) S.bInvertY = !S.bInvertY;
	else if (Id == TEXT("fov")) S.FOV = FMath::Clamp(S.FOV + 5.f * Step, 65.f, 105.f);
	else if (Id == TEXT("gamma")) S.Gamma = FMath::Clamp(S.Gamma + 0.1f * Step, 1.6f, 3.0f);
	else if (Id == TEXT("vmaster")) S.VolMaster = FMath::Clamp(S.VolMaster + 0.1f * Step, 0.f, 1.f);
	else if (Id == TEXT("vsfx")) S.VolSFX = FMath::Clamp(S.VolSFX + 0.1f * Step, 0.f, 1.f);
	else if (Id == TEXT("vmusic")) S.VolMusic = FMath::Clamp(S.VolMusic + 0.1f * Step, 0.f, 1.f);
	else if (Id == TEXT("vvoice")) S.VolVoice = FMath::Clamp(S.VolVoice + 0.1f * Step, 0.f, 1.f);
	else if (Id == TEXT("subs")) S.bSubtitles = !S.bSubtitles;
	else if (Id == TEXT("bob")) S.bHeadBob = !S.bHeadBob;
	else if (Id == TEXT("shake")) S.bCameraShake = !S.bCameraShake;
	else if (Id == TEXT("picture")) S.Filter = (S.Filter + (Dir < 0 ? 5 : 1)) % 6;
	else if (Id == TEXT("quality")) S.Quality = (S.Quality + (Dir < 0 ? 3 : 1)) % 4;
	else if (Id == TEXT("vsync")) S.bVSync = !S.bVSync;
	else bChanged = false;
	if (bChanged)
	{
		S.Save();
		S.Apply(this);
		D->Play2D(TEXT("ui_tick"), 0.5f);
	}
}

void AWCHUD::DrawMenu(AWCDirector* D)
{
	APlayerController* PC = GetOwningPlayerController();
	const float W = Canvas->SizeX, H = Canvas->SizeY;
	const bool bMain = D->Mode == EWCMode::Menu;
	Box(0, 0, W, H, FLinearColor(0, 0, 0, bMain ? (Screen == EWCScreen::Main ? 0.25f : 0.7f) : 0.78f));

	TArray<FItem> Items;
	BuildItems(D, Items);
	Sel = FMath::Clamp(Sel, 0, FMath::Max(Items.Num() - 1, 0));

	const float Left = Px(150.f);
	float Y = Px(300.f);
	if (Screen == EWCScreen::Main)
	{
		Text(TEXT("EDITH'S LAST CALL"), Left, Px(150.f), Px(96.f), FLinearColor(0.9f, 0.88f, 0.82f, 1.f), 0, true);
		Text(TEXT("1140 County Road 9.  3:07 a.m."), Left + Px(4.f), Px(262.f), Px(24.f), Dim);
		Y = Px(400.f);
		Text(TEXT("Contains horror, sudden loud sounds and flickering light.   Headphones recommended."), Left, H - Px(70.f), Px(19.f), Dim);
	}
	else
	{
		const TCHAR* Title = Screen == EWCScreen::Pause ? TEXT("PAUSED") : (Screen == EWCScreen::Settings ? TEXT("SETTINGS") : TEXT("CONTROLS"));
		Text(Title, Left, Px(130.f), Px(60.f), Ink, 0, true);
		Y = Px(250.f);
		if (Screen == EWCScreen::Pause && !D->Objective.IsEmpty())
		{
			Text(TEXT("OBJECTIVE"), W * 0.58f, Px(250.f), Px(17.f), Dim);
			Wrapped(D->Objective, W * 0.58f, Px(276.f), W * 0.34f, Px(27.f), Ink);
		}
	}
	if (Screen == EWCScreen::Controls)
	{
		static const TCHAR* Rows[][2] = {
			{ TEXT("Move"), TEXT("W A S D") }, { TEXT("Look"), TEXT("Mouse") }, { TEXT("Run"), TEXT("Left Shift") },
			{ TEXT("Crouch"), TEXT("C or Left Ctrl") }, { TEXT("Flashlight"), TEXT("F") }, { TEXT("Flashlight beam width"), TEXT("[  /  ]") }, { TEXT("Use / read / open"), TEXT("E") },
			{ TEXT("Raise pistol"), TEXT("Hold Right Mouse") }, { TEXT("Fire"), TEXT("Left Mouse") }, { TEXT("Reload"), TEXT("R") },
			{ TEXT("Inventory and objective"), TEXT("Tab or I") }, { TEXT("Pause"), TEXT("Esc") } };
		for (const auto& R : Rows)
		{
			Text(R[0], Left, Y, Px(27.f), Ink);
			Text(R[1], Left + Px(420.f), Y, Px(27.f), Hot);
			Y += Px(44.f);
		}
		Y += Px(20.f);
	}

	// input
	const bool bFresh = RealNow - ScreenOpenedAt < 0.15;
	int32 Move = 0, Side = 0;
	bool bGo = false;
	if (!bFresh)
	{
		if (PC->WasInputKeyJustPressed(EKeys::Down) || PC->WasInputKeyJustPressed(EKeys::S) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Down)) Move = 1;
		if (PC->WasInputKeyJustPressed(EKeys::Up) || PC->WasInputKeyJustPressed(EKeys::W) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Up)) Move = -1;
		if (PC->WasInputKeyJustPressed(EKeys::Left) || PC->WasInputKeyJustPressed(EKeys::A) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Left)) Side = -1;
		if (PC->WasInputKeyJustPressed(EKeys::Right) || PC->WasInputKeyJustPressed(EKeys::D) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Right)) Side = 1;
		bGo = PC->WasInputKeyJustPressed(EKeys::Enter) || PC->WasInputKeyJustPressed(EKeys::SpaceBar) || PC->WasInputKeyJustPressed(EKeys::Gamepad_FaceButton_Bottom);
	}
	if (Move != 0 && Items.Num() > 0) { Sel = (Sel + Move + Items.Num()) % Items.Num(); D->Play2D(TEXT("ui_tick"), 0.35f); }
	float MX = 0.f, MY = 0.f;
	const bool bMouse = CanvasMouse(MX, MY);
	const bool bClick = !bFresh && PC->WasInputKeyJustPressed(EKeys::LeftMouseButton);

	const bool bSettings = Screen == EWCScreen::Settings;
	const float RowH = Px(bSettings ? 43.f : 58.f);
	const float Size = Px(bSettings ? 26.f : 34.f);
	const float RowW = Px(bSettings ? 760.f : 520.f);
	static float LastMX = -1.f, LastMY = -1.f;
	const bool bMouseMoved = bMouse && (FMath::Abs(MX - LastMX) > 0.5f || FMath::Abs(MY - LastMY) > 0.5f);
	LastMX = MX; LastMY = MY;
	for (int32 i = 0; i < Items.Num(); ++i)
	{
		const FItem& It = Items[i];
		const bool bHover = bMouse && MX >= Left - Px(20.f) && MX <= Left + RowW && MY >= Y - Px(4.f) && MY < Y + RowH - Px(4.f);
		if (bHover && bMouseMoved && Sel != i) Sel = i;
		const bool bSel = Sel == i;
		if (bSel) Box(Left - Px(22.f), Y + Size * 0.18f, Px(5.f), Size * 0.95f, Hot);
		Text(It.Label, Left, Y, Size, bSel ? Hot : Ink);
		if (It.bSlider)
		{
			const float BX = Left + Px(400.f), BW = Px(220.f), BY = Y + Size * 0.62f;
			Box(BX, BY, BW, Px(4.f), FLinearColor(1, 1, 1, 0.18f));
			Box(BX, BY, BW * FMath::Clamp(It.Frac, 0.f, 1.f), Px(4.f), bSel ? Hot : Ink);
			Text(It.Value, BX + BW + Px(24.f), Y, Size, bSel ? Hot : Dim);
		}
		else if (!It.Value.IsEmpty()) Text(It.Value, Left + Px(400.f), Y, Size, bSel ? Hot : Dim);
		if (bHover && bClick)
		{
			const bool bAdjustable = It.bSlider || It.Id == TEXT("quality");
			Activate(D, It, bAdjustable ? (MX < Left + Px(510.f) ? -1 : 1) : 0);
			return;
		}
		Y += RowH;
	}
	if (Items.IsValidIndex(Sel))
	{
		if (bGo) { Activate(D, Items[Sel], 0); return; }
		if (Side != 0 && Screen == EWCScreen::Settings && Items[Sel].Id != TEXT("back")) Activate(D, Items[Sel], Side);
	}
}

// ---------------------------------------------------------------------------------------------- inventory
namespace
{
	struct FWCItemInfo { const TCHAR* Id; const TCHAR* Name; const TCHAR* Desc; const TCHAR* Mesh; };
	const FWCItemInfo GWCItemInfo[] = {
		{ TEXT("flashlight"), TEXT("Flashlight"), TEXT("County issue, three cells. It goes dim when she is close, and out when she is closer."), TEXT("/Game/HorrorHouseKit/Meshes/Lights_Ambience/SM_Flashlight_Off.SM_Flashlight_Off") },
		{ TEXT("pistol"), TEXT("Service pistol"), TEXT("Eight to the magazine. It does not hurt her. She cannot stand the noise and the flash: three or four shots and she goes, for a while."), TEXT("/Game/WC/Props/SM_Item_Pistol.SM_Item_Pistol") },
		{ TEXT("radio"), TEXT("Radio"), TEXT("Clear as a bell in the car. Inside this house it gives nothing but static."), TEXT("/Game/WC/Props/SM_Item_Radio.SM_Item_Radio") },
		{ TEXT("keep_eye"), TEXT("Glass eye"), TEXT("Pale blue, painted by hand, older than I am. It was wrapped in a handkerchief. Hers."), TEXT("/Game/WC/Props/SM_Item_GlassEye.SM_Item_GlassEye") },
		{ TEXT("screwdriver"), TEXT("Screwdriver"), TEXT("A flat-head with a turned wooden handle. The tip is bright: somebody has used it not long ago."), TEXT("/Game/WC/Props/SM_Item_Screwdriver.SM_Item_Screwdriver") },
		{ TEXT("tape1"), TEXT("VHS tape"), TEXT("A home video cassette. The label says 'Ruthie - bedtime, Oct. 1991' in ballpoint."), TEXT("/Game/WC/Props/SM_Item_Tape1.SM_Item_Tape1") },
		{ TEXT("tape2"), TEXT("VHS tape"), TEXT("Another cassette. 'Living room, Thanksgiving 1991.'"), TEXT("/Game/WC/Props/SM_Item_Tape2.SM_Item_Tape2") },
		{ TEXT("tape3"), TEXT("VHS tape"), TEXT("'Mother - porch, Nov. 1991.' The handwriting is not Edith's."), TEXT("/Game/WC/Props/SM_Item_Tape3.SM_Item_Tape3") },
		{ TEXT("doll"), TEXT("Rag doll"), TEXT("A child's rag doll, pushed deep into the duct. One button eye is gone. There is something hard inside her."), TEXT("/Game/WC/Props/SM_Item_Doll.SM_Item_Doll") },
		{ TEXT("doll_empty"), TEXT("Rag doll"), TEXT("Ruth's, I would guess. The seam down her back has been cut and sewn up again more than once."), TEXT("/Game/WC/Props/SM_Item_DollEmpty.SM_Item_DollEmpty") },
		{ TEXT("key_box"), TEXT("Small key"), TEXT("Small and fancy, with a heart worked into the bow. Too small for any door in this house."), TEXT("/Game/WC/Props/SM_Item_KeyHeart.SM_Item_KeyHeart") },
		{ TEXT("key_sitting"), TEXT("Small brass key"), TEXT("Worn smooth, two little scrolls in the bow. It was lying in a drawer that had been shut."), TEXT("/Game/WC/Props/SM_Item_Key.SM_Item_Key") },
		{ TEXT("key_prayer"), TEXT("Iron key on a ribbon"), TEXT("Heavy and old, on a faded red ribbon gone grey where it was held."), TEXT("/Game/WC/Props/SM_Item_KeyIron.SM_Item_KeyIron") },
		{ TEXT("key_desk"), TEXT("Small desk key"), TEXT("It was inside a hollow book. A barrel key, too small for a door."), TEXT("/Game/WC/Props/SM_Item_KeyDesk.SM_Item_KeyDesk") },
		{ TEXT("key_ell"), TEXT("Walter's keys"), TEXT("Three that do not match, on a split ring with a leather fob. W.H. From his desk."), TEXT("/Game/WC/Props/SM_Item_Keyring.SM_Item_Keyring") },
		{ TEXT("key_attic"), TEXT("Long key"), TEXT("It was in Daniel's room, kept where a boy keeps things. Long, with a paper tag too worn to read."), TEXT("/Game/WC/Props/SM_Item_KeyLong.SM_Item_KeyLong") },
		{ TEXT("key_cellar"), TEXT("Padlock key"), TEXT("Flat brass, stamped 27. From the bottom of Daniel's footlocker."), TEXT("/Game/WC/Props/SM_Item_KeyPadlock.SM_Item_KeyPadlock") },
		{ TEXT("fuse"), TEXT("Spare fuse"), TEXT("A screw-in plug fuse, the old kind. Fifteen amperes."), TEXT("/Game/WC/Props/SM_Item_Fuse.SM_Item_Fuse") },
		{ TEXT("shears"), TEXT("Sewing shears"), TEXT("Heavy tailor's shears, still sharp. Her hands could not close on them any more. Mine can."), TEXT("/Game/WC/Props/SM_Item_Shears.SM_Item_Shears") },
		{ TEXT("keep_ruth"), TEXT("Ruth's music box"), TEXT("Her name is scratched into the bottom in a child's capitals. It still plays."), TEXT("") },
		{ TEXT("keep_walter"), TEXT("Walter's wedding ring"), TEXT("Worn thin. It was lying with her knots."), TEXT("/Game/WC/Props/SM_Item_Ring.SM_Item_Ring") },
		{ TEXT("keep_daniel"), TEXT("Daniel's dog tags"), TEXT("HARROW, DANIEL. He went, and in March of 1969 a telegram came instead of him."), TEXT("/Game/WC/Props/SM_Item_Tags.SM_Item_Tags") },
	};
	// Some things have something hidden on them: turn that side toward him in Inspect and it can be taken.
	struct FWCHidden { const TCHAR* Item; FVector Side; const TCHAR* Hint; const TCHAR* Prompt; const TCHAR* Found; const TCHAR* Event; };
	const FWCHidden GWCHidden[] = {
		{ TEXT("doll"), FVector(0.f, 0.f, -1.f), TEXT("Something hard is sewn inside her. Turn her over."), TEXT("[E]  Work it out through the seam"), TEXT("A small key, sewn into the stuffing."), TEXT("inspect:doll") },
	};
	const FWCItemInfo* FindWCItemInfo(FName Id)
	{
		for (const FWCItemInfo& I : GWCItemInfo) if (Id == I.Id) return &I;
		return nullptr;
	}
}

void AWCHUD::BuildInventory(AWCDirector* D, TArray<FInvItem>& Out) const
{
	auto Add = [&Out](FName Id)
	{
		const FWCItemInfo* I = FindWCItemInfo(Id);
		FInvItem It; It.Id = Id; It.Name = I ? I->Name : ItemName(Id); It.Desc = I ? I->Desc : TEXT("");
		Out.Add(It);
	};
	Add(TEXT("flashlight")); Add(TEXT("pistol")); Add(TEXT("radio"));
	for (const FName& It : D->Items) if (!It.ToString().StartsWith(TEXT("ammo"))) Add(It);
}

void AWCHUD::OpenInventory(AWCDirector* D)
{
	AWCCharacter* P = D->Player();
	InvFocus = P ? P->GetFocus() : nullptr;
	Open(EWCScreen::Inventory);
	SetPaused(true);
	InvAct = 0; InvTab = 0; bInvInspect = false; InvNote = nullptr;
	InvYaw = 0.f; InvPitch = 0.f; InvZoom = 1.f; InvShown = NAME_None; InvMsgUntil = 0.0; InvLast = RealNow; InvTouchedAt = -10.0;
	D->Play2D(TEXT("paper"), 0.4f);
}

void AWCHUD::CloseInventory(AWCDirector* D)
{
	if (AWCCharacter* P = D->Player()) P->HideInspect();
	InvShown = NAME_None; InvNote = nullptr; bInvInspect = false;
	Open(EWCScreen::None);
	SetPaused(false);
}

void AWCHUD::ShowInvItem(AWCDirector* D, FName Id)
{
	AWCCharacter* P = D->Player();
	if (!P) return;
	InvShown = Id;
	InvYaw = 0.f; InvPitch = 0.f; InvZoom = 1.f;
	UStaticMesh* Mesh = nullptr;
	TArray<UMaterialInterface*> Mats;
	FVector Part = FVector::OneVector;
	const FWCItemInfo* I = FindWCItemInfo(Id);
	if (I && I->Mesh[0]) Mesh = LoadObject<UStaticMesh>(nullptr, I->Mesh, nullptr, LOAD_NoWarn | LOAD_Quiet);
	if (!Mesh)
	{
		// the thing itself, as it lay in the house
		for (TActorIterator<AWCPickup> It(GetWorld()); It; ++It)
		{
			if (It->ItemId != Id || !It->Mesh || !It->Mesh->GetStaticMesh()) continue;
			Mesh = It->Mesh->GetStaticMesh();
			Part = It->Mesh->GetRelativeScale3D();
			for (int32 m = 0; m < It->Mesh->GetNumMaterials(); ++m) Mats.Add(It->Mesh->GetMaterial(m));
			break;
		}
	}
	P->ShowInspect(Mesh, Mats, Part);
}

bool AWCHUD::InvCanDrop(AWCDirector* D, FName Id, FString& Why) const
{
	if (Id == TEXT("flashlight") || Id == TEXT("pistol") || Id == TEXT("radio")) { Why = TEXT("Not in this house."); return false; }
	const FString S = Id.ToString();
	if (S.StartsWith(TEXT("key_")))
	{
		bool bAnyDoor = false;
		for (TActorIterator<AWCDoor> It(GetWorld()); It; ++It)
		{
			if (It->KeyId != Id) continue;
			bAnyDoor = true;
			if (It->bLocked) { Why = TEXT("I still need this."); return false; }
		}
		if (!bAnyDoor && !(Id == TEXT("key_desk") && D->Has(TEXT("desk_open")))) { Why = TEXT("I still need this."); return false; }
		return true;                       // every lock it fits is open
	}
	Why = TEXT("I still need this.");
	return false;
}

void AWCHUD::InvDrop(AWCDirector* D, FName Id)
{
	FString Why;
	if (!InvCanDrop(D, Id, Why)) { InvSay(Why); return; }
	D->Items.Remove(Id);
	AWCCharacter* P = D->Player();
	for (TActorIterator<AWCPickup> It(GetWorld()); It && P; ++It)
	{
		if (It->ItemId != Id) continue;
		// set it down on the floor in front of him, where it can be picked up again
		const FVector From = P->GetActorLocation() + FRotator(0.f, P->GetControlRotation().Yaw, 0.f).Vector() * 62.f;
		FHitResult Hit;
		FCollisionQueryParams Q(SCENE_QUERY_STAT(WCDrop), false, P);
		Q.AddIgnoredActor(*It);
		const bool bFloor = GetWorld()->LineTraceSingleByChannel(Hit, From + FVector(0, 0, 30), From - FVector(0, 0, 220), ECC_Visibility, Q);
		It->SetActorLocation((bFloor ? Hit.ImpactPoint : From - FVector(0, 0, 88)) + FVector(0, 0, 1.f));
		It->SetActorHiddenInGame(false);
		It->SetActorEnableCollision(true);
		break;
	}
	InvShown = NAME_None;
	InvSay(TEXT("Left it here."));
	D->Play2D(TEXT("pickup"), 0.5f, EWCSnd::SFX, 0.8f);
}

void AWCHUD::InvUse(AWCDirector* D, FName Id)
{
	AWCCharacter* P = D->Player();
	if (!P) return;
	AWCInteractable* F = InvFocus.Get();
	if (F && !F->CanInteract()) F = nullptr;
	auto OnWhatHeFaces = [this, D, P]() { CloseInventory(D); P->DoInteract(); };
	const FString S = Id.ToString();
	if (Id == TEXT("flashlight")) { CloseInventory(D); P->SetFlashlight(!P->IsFlashlightOn()); return; }
	if (Id == TEXT("pistol")) { InvSay(TEXT("Hold the right mouse button to raise it. Left fires. R reloads.")); return; }
	if (Id == TEXT("radio")) { CloseInventory(D); D->Event(TEXT("invuse:radio")); return; }
	if (S.StartsWith(TEXT("key_")))
	{
		AWCDoor* Door = Cast<AWCDoor>(F);
		if (Door && Door->KeyId == Id) { OnWhatHeFaces(); return; }
		if (Id == TEXT("key_desk") && F && F->WCId == TEXT("desk")) { OnWhatHeFaces(); return; }
		InvSay(Door ? TEXT("It does not fit this lock.") : TEXT("Nothing here it fits. I have to be standing at the lock."));
		return;
	}
	if (S.StartsWith(TEXT("tape"))) { if (F && F->WCId == TEXT("tv")) OnWhatHeFaces(); else InvSay(TEXT("It goes in the television.")); return; }
	if (Id == TEXT("doll")) { InvSay(TEXT("There is something hard inside her. Inspect her.")); return; }
	if (Id == TEXT("screwdriver")) { if (F && F->WCId == TEXT("vent")) OnWhatHeFaces(); else InvSay(TEXT("Nothing here to unscrew.")); return; }
	if (Id == TEXT("fuse")) { if (F && F->WCId == TEXT("fusebox")) OnWhatHeFaces(); else InvSay(TEXT("It goes in the fuse box.")); return; }
	if (Id == TEXT("shears")) { if (F && F->WCId.ToString().StartsWith(TEXT("knot"))) OnWhatHeFaces(); else InvSay(TEXT("Nothing here to cut.")); return; }
	if (S.StartsWith(TEXT("keep_")) && F && F->WCId == TEXT("place")) { OnWhatHeFaces(); return; }
	if (Id == TEXT("keep_ruth")) { CloseInventory(D); D->Event(TEXT("invuse:keep_ruth")); return; }
	if (S.StartsWith(TEXT("keep_"))) { InvSay(TEXT("Not here. Where she lies.")); return; }
	InvSay(TEXT("I can't use that here."));
}

void AWCHUD::DrawInventory(AWCDirector* D)
{
	APlayerController* PC = GetOwningPlayerController();
	AWCCharacter* P = D->Player();
	if (!PC || !P) return;
	const float W = Canvas->SizeX, H = Canvas->SizeY;
	const float Dt = (float)FMath::Clamp(RealNow - InvLast, 0.0, 0.1);
	InvLast = RealNow;
	const bool bFresh = RealNow - ScreenOpenedAt < 0.15;

	// a paper being read again covers everything
	if (const AWCNote* Note = InvNote.Get())
	{
		DrawNotePage(Note, TEXT("[E] or [Esc]  Back"));
		if (!bFresh && (PC->WasInputKeyJustPressed(EKeys::E) || PC->WasInputKeyJustPressed(EKeys::Enter) || PC->WasInputKeyJustPressed(EKeys::LeftMouseButton))) { InvNote = nullptr; ScreenOpenedAt = RealNow; }
		return;
	}

	TArray<FInvItem> Items;
	BuildInventory(D, Items);
	InvSel = FMath::Clamp(InvSel, 0, Items.Num() - 1);

	// ---- input
	int32 Move = 0, Side = 0;
	bool bGo = false;
	float MX = 0.f, MY = 0.f;
	const bool bMouse = CanvasMouse(MX, MY);
	const float DX = MX - InvMX, DY = MY - InvMY;
	const bool bMouseMoved = bMouse && (FMath::Abs(DX) > 0.5f || FMath::Abs(DY) > 0.5f);
	InvMX = MX; InvMY = MY;
	const bool bClick = !bFresh && PC->WasInputKeyJustPressed(EKeys::LeftMouseButton);
	const bool bHeld = PC->IsInputKeyDown(EKeys::LeftMouseButton);
	if (!bFresh)
	{
		if (PC->WasInputKeyJustPressed(EKeys::Down) || PC->WasInputKeyJustPressed(EKeys::S) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Down)) Move = 1;
		if (PC->WasInputKeyJustPressed(EKeys::Up) || PC->WasInputKeyJustPressed(EKeys::W) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Up)) Move = -1;
		if (PC->WasInputKeyJustPressed(EKeys::Left) || PC->WasInputKeyJustPressed(EKeys::A) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Left)) Side = -1;
		if (PC->WasInputKeyJustPressed(EKeys::Right) || PC->WasInputKeyJustPressed(EKeys::D) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Right)) Side = 1;
		bGo = PC->WasInputKeyJustPressed(EKeys::Enter) || PC->WasInputKeyJustPressed(EKeys::SpaceBar) || PC->WasInputKeyJustPressed(EKeys::E) || PC->WasInputKeyJustPressed(EKeys::Gamepad_FaceButton_Bottom);
		if (!bInvInspect)
		{
			if (PC->WasInputKeyJustPressed(EKeys::One)) InvTab = 0;
			if (PC->WasInputKeyJustPressed(EKeys::Two)) InvTab = 1;
		}
	}
	auto Hover = [&](float X0, float Y0, float X1, float Y1) { return bMouse && MX >= X0 && MX <= X1 && MY >= Y0 && MY <= Y1; };

	// ---- the thing itself
	const FName WantShown = InvTab == 0 && Items.IsValidIndex(InvSel) ? Items[InvSel].Id : FName(TEXT("__none"));
	if (WantShown != InvShown) ShowInvItem(D, WantShown);
	if (bInvInspect)
	{
		if (bHeld && !bFresh) { InvYaw -= DX * 0.45f; InvPitch = FMath::Clamp(InvPitch + DY * 0.45f, -85.f, 85.f); InvTouchedAt = RealNow; }
		const float Turn = 110.f * Dt;
		if (PC->IsInputKeyDown(EKeys::A) || PC->IsInputKeyDown(EKeys::Left)) { InvYaw += Turn; InvTouchedAt = RealNow; }
		if (PC->IsInputKeyDown(EKeys::D) || PC->IsInputKeyDown(EKeys::Right)) { InvYaw -= Turn; InvTouchedAt = RealNow; }
		if (PC->IsInputKeyDown(EKeys::W) || PC->IsInputKeyDown(EKeys::Up)) { InvPitch = FMath::Clamp(InvPitch - Turn, -85.f, 85.f); InvTouchedAt = RealNow; }
		if (PC->IsInputKeyDown(EKeys::S) || PC->IsInputKeyDown(EKeys::Down)) { InvPitch = FMath::Clamp(InvPitch + Turn, -85.f, 85.f); InvTouchedAt = RealNow; }
		if (PC->WasInputKeyJustPressed(EKeys::MouseScrollUp) || PC->IsInputKeyDown(EKeys::Q)) InvZoom = FMath::Min(1.5f, InvZoom + (PC->IsInputKeyDown(EKeys::Q) ? Dt : 0.1f));
		if (PC->WasInputKeyJustPressed(EKeys::MouseScrollDown) || PC->IsInputKeyDown(EKeys::Z)) InvZoom = FMath::Max(0.65f, InvZoom - (PC->IsInputKeyDown(EKeys::Z) ? Dt : 0.1f));
	}
	if (RealNow - InvTouchedAt > 2.5) InvYaw += 22.f * Dt;                 // left alone, it turns slowly
	{
		const FQuat Base = P->InspectBase();
		const FQuat Q = FQuat(FRotator(InvPitch, 0.f, 0.f)) * FQuat(FRotator(0.f, InvYaw, 0.f)) * Base;
		static float ZoomShown = 1.f;
		ZoomShown = FMath::FInterpTo(ZoomShown, InvZoom * (bInvInspect ? 1.3f : 0.92f), Dt, 9.f);
		P->SetInspectView(Q, ZoomShown);
	}

	const FInvItem* Cur = InvTab == 0 && Items.IsValidIndex(InvSel) ? &Items[InvSel] : nullptr;

	// ---- inspecting: just the thing, its name and what he makes of it
	if (bInvInspect && Cur)
	{
		Text(Cur->Name, W * 0.5f, Px(70.f), Px(40.f), Hot, 1, true);
		Wrapped(Cur->Desc, W * 0.24f, H - Px(210.f), W * 0.52f, Px(25.f), Ink, 1);
		Text(TEXT("Drag, or W A S D: turn it      Wheel, or Q / Z: closer, further      Esc: back"), W * 0.5f, H - Px(64.f), Px(19.f), Dim, 1);
		for (const FWCHidden& Hd : GWCHidden)
		{
			if (Cur->Id != Hd.Item) continue;
			const FQuat Qv = FQuat(FRotator(InvPitch, 0.f, 0.f)) * FQuat(FRotator(0.f, InvYaw, 0.f)) * P->InspectBase();
			const bool bSide = Qv.RotateVector(Hd.Side).X < -0.62f;                 // that side is toward him
			if (bSide) InvTouchedAt = RealNow;                                        // hold still while he looks at it
			Text(bSide ? Hd.Prompt : Hd.Hint, W * 0.5f, H - Px(262.f), Px(25.f), bSide ? Hot : Dim, 1);
			if (bSide && bGo)
			{
				const float Y0 = InvYaw, P0 = InvPitch, Z0 = InvZoom;
				D->Event(Hd.Event);
				TArray<FInvItem> Now;
				BuildInventory(D, Now);
				for (int32 i = 0; i < Now.Num(); ++i) if (Now[i].Id == TEXT("doll_empty")) InvSel = i;
				if (Now.IsValidIndex(InvSel)) { ShowInvItem(D, Now[InvSel].Id); InvYaw = Y0; InvPitch = P0; InvZoom = Z0; }
				InvSay(Hd.Found);
				return;
			}
		}
		if (RealNow < InvMsgUntil) Text(InvMsg, W * 0.5f, H - Px(262.f), Px(25.f), Hot, 1);
		if (!bFresh && (PC->WasInputKeyJustPressed(EKeys::RightMouseButton) || PC->WasInputKeyJustPressed(EKeys::BackSpace))) bInvInspect = false;
		return;
	}

	// ---- frame
	const float Left = Px(70.f);
	Text(TEXT("CARRYING"), Left, Px(58.f), Px(52.f), Ink, 0, true);
	{
		// two pages
		static const TCHAR* Tabs[] = { TEXT("[1]  THINGS"), TEXT("[2]  PAPERS") };
		float X = Left;
		for (int32 t = 0; t < 2; ++t)
		{
			const FString Label = t == 1 ? FString::Printf(TEXT("%s  (%d)"), Tabs[t], D->NotesRead.Num()) : FString(Tabs[t]);
			const float Tw = Measure(Label, Px(21.f)).X;
			const bool bOver = Hover(X - Px(8.f), Px(132.f), X + Tw + Px(8.f), Px(166.f));
			Text(Label, X, Px(136.f), Px(21.f), InvTab == t ? Hot : (bOver ? Ink : Dim));
			if (InvTab == t) Box(X, Px(164.f), Tw, Px(2.f), Hot);
			if (bOver && bClick) { InvTab = t; return; }
			X += Tw + Px(46.f);
		}
	}
	// right-hand side: what he is doing, what he has left in the gun, what he is looking for
	{
		const float RX = W * 0.735f, RW = W * 0.225f;
		float Y = Px(136.f);
		if (!D->Objective.IsEmpty())
		{
			Text(TEXT("OBJECTIVE"), RX, Y, Px(17.f), Dim); Y += Px(26.f);
			Y += Wrapped(D->Objective, RX, Y, RW, Px(24.f), Ink) + Px(26.f);
		}
		Text(TEXT("CARTRIDGES"), RX, Y, Px(17.f), Dim); Y += Px(26.f);
		Text(FString::Printf(TEXT("%d in the pistol, %d spare"), P->Ammo, P->Reserve), RX, Y, Px(24.f), Ink); Y += Px(54.f);
		if (D->NotesRead.Contains(TEXT("note_prayer")) || D->NotesRead.Contains(TEXT("note_cellar")))
		{
			Text(TEXT("WHAT WAS THEIRS"), RX, Y, Px(17.f), Dim); Y += Px(26.f);
			static const TCHAR* Keep[][2] = { { TEXT("keep_ruth"), TEXT("Ruth's music box") }, { TEXT("keep_walter"), TEXT("Walter's ring") }, { TEXT("keep_daniel"), TEXT("Daniel's tags") }, { TEXT("shears"), TEXT("Something to cut with") } };
			for (const auto& K : Keep)
			{
				const bool bHave = D->Items.Contains(K[0]);
				Text(FString::Printf(TEXT("%s  %s"), bHave ? TEXT("[x]") : TEXT("[  ]"), K[1]), RX, Y, Px(22.f), bHave ? Ink : Dim); Y += Px(30.f);
			}
			Y += Px(6.f);
			Wrapped(TEXT("Bring them to where she lies. Cut the three knots."), RX, Y, RW, Px(19.f), Dim);
		}
	}

	if (InvTab == 1)
	{
		// ---- papers he has read
		TArray<const AWCNote*> Notes;
		for (const FName& Id : D->NotesRead) if (const AWCNote* N = Cast<AWCNote>(D->Thing(Id))) Notes.Add(N);
		if (Notes.Num() == 0) { Text(TEXT("Nothing read yet."), Left, Px(200.f), Px(24.f), Dim); }
		InvPaper = FMath::Clamp(InvPaper, 0, FMath::Max(Notes.Num() - 1, 0));
		if (Move != 0 && Notes.Num() > 0) { InvPaper = (InvPaper + Move + Notes.Num()) % Notes.Num(); D->Play2D(TEXT("ui_tick"), 0.35f); }
		const int32 PerCol = 13;
		const float RowH = Px(38.f), ColW = W * 0.31f;
		for (int32 i = 0; i < Notes.Num() && i < PerCol * 2; ++i)
		{
			const float X = Left + (i / PerCol) * ColW, Y = Px(200.f) + (i % PerCol) * RowH;
			FString Title = Notes[i]->Title;
			if (Title.IsEmpty()) Title = Notes[i]->Body.Left(34).Replace(TEXT("\n"), TEXT(" ")) + TEXT("...");
			if (Title.Len() > 40) Title = Title.Left(38) + TEXT("...");
			const bool bOver = Hover(X - Px(14.f), Y - Px(3.f), X + ColW - Px(30.f), Y + RowH - Px(5.f));
			if (bOver && bMouseMoved) InvPaper = i;
			const bool bSel = InvPaper == i;
			if (bSel) Box(X - Px(18.f), Y + Px(5.f), Px(4.f), Px(22.f), Hot);
			Text(Title, X, Y, Px(23.f), bSel ? Hot : Ink);
			if (bOver && bClick) { InvNote = const_cast<AWCNote*>(Notes[i]); ScreenOpenedAt = RealNow; return; }
		}
		if (bGo && Notes.IsValidIndex(InvPaper)) { InvNote = const_cast<AWCNote*>(Notes[InvPaper]); ScreenOpenedAt = RealNow; return; }
		Text(TEXT("W / S: choose      Enter: read it again      1: things      Tab: close"), W * 0.5f, H - Px(64.f), Px(19.f), Dim, 1);
		return;
	}

	// ---- things: the list
	if (Move != 0 && Items.Num() > 0) { InvSel = (InvSel + Move + Items.Num()) % Items.Num(); InvMsgUntil = 0.0; D->Play2D(TEXT("ui_tick"), 0.35f); }
	{
		const float RowH = Px(41.f);
		float Y = Px(200.f);
		for (int32 i = 0; i < Items.Num(); ++i)
		{
			const bool bOver = Hover(Left - Px(22.f), Y - Px(3.f), Left + Px(330.f), Y + RowH - Px(5.f));
			if (bOver && bMouseMoved && InvSel != i) { InvSel = i; InvMsgUntil = 0.0; }
			if (bOver && bClick) InvSel = i;
			const bool bSel = InvSel == i;
			if (bSel) Box(Left - Px(20.f), Y + Px(6.f), Px(4.f), Px(24.f), Hot);
			Text(Items[i].Name, Left, Y, Px(25.f), bSel ? Hot : Ink);
			if (i == 2) { Y += Px(14.f); Box(Left, Y + RowH - Px(8.f), Px(250.f), Px(1.f), FLinearColor(1, 1, 1, 0.12f)); }
			Y += RowH;
		}
	}
	Cur = Items.IsValidIndex(InvSel) ? &Items[InvSel] : nullptr;
	if (!Cur) return;

	// ---- name, what he makes of it, and what can be done with it
	Text(Cur->Name, W * 0.5f, H * 0.655f, Px(36.f), Hot, 1, true);
	Wrapped(Cur->Desc, W * 0.29f, H * 0.655f + Px(56.f), W * 0.42f, Px(22.f), Ink, 1);
	if (RealNow < InvMsgUntil) Text(InvMsg, W * 0.5f, H - Px(176.f), Px(23.f), Hot, 1);

	FString Why;
	const bool bCanDrop = InvCanDrop(D, Cur->Id, Why);
	static const TCHAR* Acts[] = { TEXT("USE"), TEXT("INSPECT"), TEXT("DROP") };
	if (Side != 0) { InvAct = (InvAct + Side + 3) % 3; D->Play2D(TEXT("ui_tick"), 0.35f); }
	const float BW = Px(190.f), BH = Px(48.f), Gap = Px(22.f);
	const float BX0 = W * 0.5f - (BW * 3 + Gap * 2) * 0.5f, BY = H - Px(134.f);
	int32 Do = -1;
	for (int32 a = 0; a < 3; ++a)
	{
		const float X = BX0 + a * (BW + Gap);
		const bool bOver = Hover(X, BY, X + BW, BY + BH);
		if (bOver && bMouseMoved) InvAct = a;
		const bool bSel = InvAct == a;
		const bool bOff = a == 2 && !bCanDrop;
		Box(X, BY, BW, BH, FLinearColor(1, 1, 1, bSel ? 0.10f : 0.04f));
		Box(X, BY + BH - Px(2.f), BW, Px(2.f), bSel ? Hot : FLinearColor(1, 1, 1, 0.16f));
		Text(Acts[a], X + BW * 0.5f, BY + Px(11.f), Px(24.f), bOff ? FLinearColor(Dim.R, Dim.G, Dim.B, 0.45f) : (bSel ? Hot : Ink), 1);
		if (bOver && bClick) Do = a;
	}
	if (bGo) Do = InvAct;
	Text(TEXT("W / S: choose      A / D: what to do      Enter: do it      2: papers      Tab: close"), W * 0.5f, H - Px(64.f), Px(19.f), Dim, 1);

	if (Do == 0) InvUse(D, Cur->Id);
	else if (Do == 1) { bInvInspect = true; InvTouchedAt = RealNow - 1.0; ScreenOpenedAt = RealNow; }
	else if (Do == 2) InvDrop(D, Cur->Id);
}
