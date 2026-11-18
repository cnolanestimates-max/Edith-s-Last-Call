#include "WCGame.h"
#include "WCCharacter.h"
#include "WCDirector.h"
#include "WCWorld.h"

#include "CanvasItem.h"
#include "Engine/Canvas.h"
#include "Engine/Font.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "HAL/FileManager.h"
#include "Misc/CommandLine.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"

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
}

float AWCHUD::Px(float P) const
{
	return Canvas ? P * Canvas->SizeY / 1080.f : P;
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
	if (D->Mode == EWCMode::Playing && bEsc)
	{
		if (D->ActiveNote.IsValid()) D->CloseNote();
		else if (Screen == EWCScreen::None && D->Fade < 0.9f) { Back = EWCScreen::Pause; Open(EWCScreen::Pause); SetPaused(true); }
		else if (Screen == EWCScreen::Pause) { Open(EWCScreen::None); SetPaused(false); }
		else if (Screen == EWCScreen::Settings || Screen == EWCScreen::Controls) Open(Back);
	}
	else if (D->Mode == EWCMode::Menu && bEsc && Screen != EWCScreen::Main) Open(EWCScreen::Main);
	if ((D->Mode == EWCMode::Credits || D->Mode == EWCMode::Ending) && bEsc) D->QuitToMenu();

	if (D->Mode == EWCMode::Playing && Screen == EWCScreen::None) DrawGame(D);
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
	if (Screen != EWCScreen::None) DrawMenu(D);
	if (!MenuTestDir.IsEmpty() && RealNow > MenuTestAt)
	{
		static const TCHAR* Names[] = { TEXT("menu_main"), TEXT("menu_settings"), TEXT("menu_controls") };
		if (MenuTestStage < 3)
		{
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
		{ TEXT("key_attic"), TEXT("Attic key") }, { TEXT("key_cellar"), TEXT("Padlock key") },
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
	const bool bTab = PC && PC->IsInputKeyDown(EKeys::Tab);
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
	const AWCNote* N = D->ActiveNote.Get();
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
	Text(TEXT("[E] Put it back"), W * 0.5f, Y + PH + Px(18.f), Px(21.f), Dim, 1);
}

void AWCHUD::DrawCredits(AWCDirector* D)
{
	static const TCHAR* Lines[] = {
		TEXT("#EDITH'S LAST CALL"), TEXT(""), TEXT(""),
		TEXT("#Created by"), TEXT("Cheyenne"), TEXT(""),
		TEXT("#Design, writing, code, animation"), TEXT("Built with Claude"), TEXT(""),
		TEXT("#Voices"), TEXT("Deputy Cole Brandt"), TEXT("Dispatch"), TEXT("Edith Harrow"), TEXT("Synthesised with Google Gemini text-to-speech"), TEXT(""),
		TEXT("#Music"), TEXT("Kevin MacLeod (incompetech.com)"), TEXT("Licensed under Creative Commons: By Attribution 4.0"), TEXT(""),
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
		Add(TEXT("Master volume"), Pct(S.VolMaster), TEXT("vmaster"), true, S.VolMaster);
		Add(TEXT("Effects volume"), Pct(S.VolSFX), TEXT("vsfx"), true, S.VolSFX);
		Add(TEXT("Music volume"), Pct(S.VolMusic), TEXT("vmusic"), true, S.VolMusic);
		Add(TEXT("Voice volume"), Pct(S.VolVoice), TEXT("vvoice"), true, S.VolVoice);
		Add(TEXT("Subtitles"), OnOff(S.bSubtitles), TEXT("subs"));
		Add(TEXT("Head bob"), OnOff(S.bHeadBob), TEXT("bob"));
		Add(TEXT("Camera shake"), OnOff(S.bCameraShake), TEXT("shake"));
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
	else if (Id == TEXT("quality")) S.Quality = (S.Quality + (Dir < 0 ? 3 : 1)) % 4;
	else if (Id == TEXT("full")) S.bFullscreen = !S.bFullscreen;
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
			{ TEXT("Crouch"), TEXT("C or Left Ctrl") }, { TEXT("Flashlight"), TEXT("F") }, { TEXT("Use / read / open"), TEXT("E") },
			{ TEXT("Raise pistol"), TEXT("Hold Right Mouse") }, { TEXT("Fire"), TEXT("Left Mouse") }, { TEXT("Reload"), TEXT("R") },
			{ TEXT("Objective and items"), TEXT("Hold Tab") }, { TEXT("Pause"), TEXT("Esc") } };
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
	const bool bMouse = PC->GetMousePosition(MX, MY);
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
