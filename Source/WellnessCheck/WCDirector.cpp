#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"

#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/AudioComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "Components/LightComponent.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "GameFramework/GameUserSettings.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Misc/CommandLine.h"
#include "Misc/ConfigCacheIni.h"
#include "Sound/SoundAttenuation.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundWave.h"

DEFINE_LOG_CATEGORY_STATIC(LogWC, Log, All);

FWCSettings AWCDirector::Settings;
int32 AWCDirector::PendingStart = 0;
static const TCHAR* Sec = TEXT("WellnessCheck");

// ---------------------------------------------------------------------------------------------- settings
void FWCSettings::Load()
{
	if (!GConfig) return;
	const FString& Ini = GGameUserSettingsIni;
	GConfig->GetFloat(Sec, TEXT("Sensitivity"), Sensitivity, Ini);
	GConfig->GetBool(Sec, TEXT("InvertY"), bInvertY, Ini);
	GConfig->GetFloat(Sec, TEXT("FOV"), FOV, Ini);
	GConfig->GetFloat(Sec, TEXT("Gamma"), Gamma, Ini);
	GConfig->GetInt(Sec, TEXT("FlashlightBeamChoice"), BeamChoice, Ini);
	BeamChoice = FMath::Clamp(BeamChoice, 0, BeamChoices - 1);
	GConfig->GetFloat(Sec, TEXT("VolMaster"), VolMaster, Ini);
	GConfig->GetFloat(Sec, TEXT("VolSFX"), VolSFX, Ini);
	GConfig->GetFloat(Sec, TEXT("VolMusic"), VolMusic, Ini);
	GConfig->GetFloat(Sec, TEXT("VolVoice"), VolVoice, Ini);
	GConfig->GetBool(Sec, TEXT("Subtitles"), bSubtitles, Ini);
	GConfig->GetBool(Sec, TEXT("HeadBob"), bHeadBob, Ini);
	GConfig->GetBool(Sec, TEXT("CameraShake"), bCameraShake, Ini);
	GConfig->GetInt(Sec, TEXT("Picture"), Filter, Ini);
	GConfig->GetInt(Sec, TEXT("Quality"), Quality, Ini);
	GConfig->GetBool(Sec, TEXT("Fullscreen"), bFullscreen, Ini);
	GConfig->GetBool(Sec, TEXT("VSync"), bVSync, Ini);
	Sensitivity = FMath::Clamp(Sensitivity, 0.2f, 3.f);
	FOV = FMath::Clamp(FOV, 65.f, 105.f);
	Gamma = FMath::Clamp(Gamma, 1.6f, 3.0f);
	Quality = FMath::Clamp(Quality, 0, 3);
}

void FWCSettings::Save() const
{
	if (!GConfig) return;
	const FString& Ini = GGameUserSettingsIni;
	GConfig->SetFloat(Sec, TEXT("Sensitivity"), Sensitivity, Ini);
	GConfig->SetBool(Sec, TEXT("InvertY"), bInvertY, Ini);
	GConfig->SetFloat(Sec, TEXT("FOV"), FOV, Ini);
	GConfig->SetFloat(Sec, TEXT("Gamma"), Gamma, Ini);
	GConfig->SetInt(Sec, TEXT("FlashlightBeamChoice"), BeamChoice, Ini);
	GConfig->SetFloat(Sec, TEXT("VolMaster"), VolMaster, Ini);
	GConfig->SetFloat(Sec, TEXT("VolSFX"), VolSFX, Ini);
	GConfig->SetFloat(Sec, TEXT("VolMusic"), VolMusic, Ini);
	GConfig->SetFloat(Sec, TEXT("VolVoice"), VolVoice, Ini);
	GConfig->SetBool(Sec, TEXT("Subtitles"), bSubtitles, Ini);
	GConfig->SetBool(Sec, TEXT("HeadBob"), bHeadBob, Ini);
	GConfig->SetBool(Sec, TEXT("CameraShake"), bCameraShake, Ini);
	GConfig->SetInt(Sec, TEXT("Picture"), Filter, Ini);
	GConfig->SetInt(Sec, TEXT("Quality"), Quality, Ini);
	GConfig->SetBool(Sec, TEXT("Fullscreen"), bFullscreen, Ini);
	GConfig->SetBool(Sec, TEXT("VSync"), bVSync, Ini);
	GConfig->Flush(false, Ini);
}

void FWCSettings::Apply(UObject* WorldContext) const
{
	if (GEngine) GEngine->DisplayGamma = Gamma;
	if (UGameUserSettings* U = GEngine ? GEngine->GetGameUserSettings() : nullptr)
	{
		U->SetOverallScalabilityLevel(Quality);
		U->SetVSyncEnabled(bVSync);
		U->ApplyNonResolutionSettings();
	}
	if (AWCDirector* D = AWCDirector::Get(WorldContext))
	{
		D->ApplyVolumes();
		if (AWCCharacter* P = D->Player()) P->ApplySettings();
		int32 Forced = 0;
		if (!FParse::Value(FCommandLine::Get(), TEXT("WCFilter="), Forced)) D->SetFilter(Filter);
	}
}

void FWCSettings::ApplyDisplayMode(UWorld* World) const
{
	// The desktop shortcut uses the editor executable in standalone -game mode.
	if (!World || World->WorldType != EWorldType::Game || FParse::Param(FCommandLine::Get(), TEXT("RenderOffscreen"))) return;
	UGameUserSettings* U = GEngine ? GEngine->GetGameUserSettings() : nullptr;
	if (!U) return;
	const FIntPoint Desktop = U->GetDesktopResolution();
	if (Desktop.X <= 0 || Desktop.Y <= 0) return;
	const FIntPoint Window(FMath::Min(1280, Desktop.X), FMath::Min(720, Desktop.Y));
	U->SetFullscreenMode(bFullscreen ? EWindowMode::WindowedFullscreen : EWindowMode::Windowed);
	U->SetScreenResolution(bFullscreen ? Desktop : Window);
	U->ApplyResolutionSettings(false);
	U->ConfirmVideoMode();
	U->SaveSettings();
}

// ---------------------------------------------------------------------------------------------- lifetime
AWCDirector::AWCDirector()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PostPhysics;
	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
	Flies = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Flies"));
	Flies->SetupAttachment(GetRootComponent());
	Flies->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Flies->SetCastShadow(false);
	Flies->bAffectDistanceFieldLighting = false;
	Flies->bAffectDynamicIndirectLighting = false;
}

AWCDirector* AWCDirector::Get(const UObject* WorldContext)
{
	UWorld* W = WorldContext ? WorldContext->GetWorld() : nullptr;
	if (!W) return nullptr;
	static TWeakObjectPtr<AWCDirector> Cached;
	if (Cached.IsValid() && Cached->GetWorld() == W) return Cached.Get();
	for (TActorIterator<AWCDirector> It(W); It; ++It) { Cached = *It; return *It; }
	return nullptr;
}

AWCCharacter* AWCDirector::Player() const
{
	return Cast<AWCCharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
}

void AWCDirector::BeginPlay()
{
	Super::BeginPlay();
	Rng.Initialize(FPlatformTime::Cycles());
	Settings.Load();
	Settings.Apply(this);
	Settings.ApplyDisplayMode(GetWorld());
	for (TActorIterator<AWCEntity> It(GetWorld()); It; ++It) { HerActor = *It; break; }
	for (TActorIterator<AWCTrigger> It(GetWorld()); It; ++It) Triggers.Add(*It);
	// flies over everything that rots
	if (UStaticMesh* FlyMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/WC/Props/SM_HouseFly.SM_HouseFly")))
	{
		Flies->SetStaticMesh(FlyMesh);

		for (TActorIterator<AActor> It(GetWorld()); It; ++It)
		{
			if (!It->ActorHasTag(TEXT("Flies"))) continue;
			const FVector C = It->GetActorLocation();
			for (int32 i = 0; i < 12; ++i)
			{
				FFly F;
				F.Centre = C + FVector(Rng.FRandRange(-12.f, 12.f), Rng.FRandRange(-12.f, 12.f), Rng.FRandRange(-10.f, 10.f));
				F.Radii = FVector(Rng.FRandRange(14.f, 46.f), Rng.FRandRange(14.f, 46.f), Rng.FRandRange(6.f, 26.f));
				F.Freq = FVector(Rng.FRandRange(1.6f, 4.2f), Rng.FRandRange(1.6f, 4.2f), Rng.FRandRange(2.2f, 5.f));
				F.Phase = FVector(Rng.FRandRange(0.f, 6.28f), Rng.FRandRange(0.f, 6.28f), Rng.FRandRange(0.f, 6.28f));
				FlyData.Add(F);
				Flies->AddInstance(FTransform(FQuat::Identity, F.Centre, FVector(.105f)), true);
			}

		}
	}
	for (TActorIterator<AActor> It(GetWorld()); It; ++It)
	{
		const int32 Kind = It->ActorHasTag(TEXT("Flicker")) ? 0 : (It->ActorHasTag(TEXT("BarRed")) ? 1 : (It->ActorHasTag(TEXT("BarBlue")) ? 2 : -1));
		if (It->ActorHasTag(TEXT("BarRedMesh"))) BarMeshes[0].Add(*It);
		if (It->ActorHasTag(TEXT("BarBlueMesh"))) BarMeshes[1].Add(*It);
		if (Kind < 0) continue;
		TArray<ULightComponent*> Ls;
		It->GetComponents(Ls);
		for (ULightComponent* L : Ls) { FLive X; X.Light = L; X.Base = L->Intensity; X.Seed = Rng.FRandRange(0.f, 100.f); X.Kind = Kind; LiveLights.Add(X); }
	}

	for (const TCHAR* Cmd : { TEXT("r.Lumen.ScreenProbeGather.ScreenTraces 1"), TEXT("r.VolumetricFog 1") })
	{
		UKismetSystemLibrary::ExecuteConsoleCommand(this, Cmd, nullptr);
	}

	bAuto = FParse::Param(FCommandLine::Get(), TEXT("WCAuto")) || FParse::Param(FCommandLine::Get(), TEXT("WCTour")) || FParse::Param(FCommandLine::Get(), TEXT("WCHerLook")) || FParse::Param(FCommandLine::Get(), TEXT("WCItems"));
	if (bAuto && FParse::Param(FCommandLine::Get(), TEXT("WCListeningCheck")))
		SaveSlot = TEXT("WCListeningCheck");
	if (bAuto && FParse::Param(FCommandLine::Get(), TEXT("WCCorner24")))
		SaveSlot = TEXT("WCCorner24Check");
	if (bAuto && FParse::Param(FCommandLine::Get(), TEXT("WCRoomConnections")))
		SaveSlot = TEXT("WCRoomConnectionsCheck");
	if (bAuto && FParse::Param(FCommandLine::Get(), TEXT("WCSettlersCheck")))
		SaveSlot = TEXT("WCSettlersCheck");
	if (bAuto && FParse::Param(FCommandLine::Get(), TEXT("WCBreathCheck")))
		SaveSlot = TEXT("WCDeputyBreathCheck");
	if (FParse::Param(FCommandLine::Get(), TEXT("WCFast"))) TestPace = 0.08f;
	FParse::Value(FCommandLine::Get(), TEXT("WCShots="), AutoShotDir);
	static int32 AutoRuns = 0;
	if (bAuto && PendingStart == 0 && AutoRuns > 0)
	{
		UE_LOG(LogWC, Display, TEXT("WCAUTO DONE back at the menu after a complete play-through"));
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (bAuto) ++AutoRuns;
	if ((bAuto && PendingStart == 0) || FParse::Param(FCommandLine::Get(), TEXT("WCNewGame"))) PendingStart = 1;
	if (FParse::Param(FCommandLine::Get(), TEXT("WCContinue"))) PendingStart = 2;

	Fade = 1.f; FadeTarget = 0.f; FadeRate = 0.7f;
	const int32 Start = PendingStart;
	PendingStart = 0;
	if (Start == 0)
	{
		Mode = EWCMode::Menu;
		// Warm the small set of sounds that otherwise synchronously load at departure,
		// on the radio, or as the camera hands back to the player.
		for (const TCHAR* Id : { TEXT("amb_car"), TEXT("radio_click"), TEXT("car_stop"), TEXT("car_door"),
			TEXT("VO/d_arrive1"), TEXT("VO/r_arrive1"), TEXT("VO/r_arrive2"), TEXT("VO/d_arrive3"),
			TEXT("VO/d_arrive2"), TEXT("VO/r_arrive3"), TEXT("VO/d_arrive4") })
		{
			const FString Name(Id);
			const FSoftObjectPath Path(FString::Printf(TEXT("/Game/WC/Audio/%s.%s"), Id, *FPaths::GetCleanFilename(Name)));
			Path.LoadAsync(FLoadSoftObjectPathAsyncDelegate::CreateWeakLambda(this, [this, Name](const FSoftObjectPath&, UObject* Object)
			{
				if (USoundBase* Sound = Cast<USoundBase>(Object)) SoundCache.Add(Name, Sound);
			}));
		}
		if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
		{
			if (ACameraActor* Cam = Cast<ACameraActor>(Find(TEXT("MenuCam"))))
			{
				Cam->GetCameraComponent()->bConstrainAspectRatio = false;
				PC->SetViewTargetWithBlend(Cam, 0.f);
			}
		}
		SetLoop(TEXT("amb"), TEXT("amb_night"), 0.9f, 2.f);
		SetLoop(TEXT("music"), TEXT("music_menu"), 0.7f, 4.f, EWCSnd::Music);
		HouseBegin();
	}
	else
	{
		Mode = EWCMode::Playing;
		const bool bLoaded = Start == 2 && DoLoad();
		HouseBegin();
		StoryBegin(bLoaded);
		if (bAuto) AutoBegin();
	}
}

void AWCDirector::EndPlay(const EEndPlayReason::Type Reason)
{
	if (DeputyBreath.IsValid()) DeputyBreath->Stop();
	SetDoorSilence(false);
	Steps.Reset();
	Deferred.Reset();
	Super::EndPlay(Reason);
}

void AWCDirector::After(float Delay, TFunction<void()> Fn)
{
	Steps.Add({ Clock + FMath::Max(Delay, 0.f), MoveTemp(Fn) });
}

void AWCDirector::Tick(float Dt)
{
	Super::Tick(Dt);
	Clock += Dt;
	if (Mode == EWCMode::Playing) PlaySeconds += Dt;

	// scheduled steps (copy out first: a step may schedule more)
	TArray<TFunction<void()>> Due;
	for (int32 i = Steps.Num() - 1; i >= 0; --i)
	{
		if (Steps[i].At <= Clock) { Due.Insert(MoveTemp(Steps[i].Fn), 0); Steps.RemoveAt(i); }
	}
	for (TFunction<void()>& Fn : Due) if (Fn) Fn();

	Fade = FMath::FInterpConstantTo(Fade, FadeTarget, Dt, FadeRate);
	BigAlpha = FMath::FInterpConstantTo(BigAlpha, BigTarget, Dt, 0.6f);
	for (int32 i = Subtitles.Num() - 1; i >= 0; --i) if (Subtitles[i].Until < Clock) Subtitles.RemoveAt(i);

	if (Mode == EWCMode::Playing)
	{
					if (Clock >= NextTrigPoll) { NextTrigPoll = Clock + 0.1; TickTriggers(); }
			HouseTick(Dt);
			TickBathMirror(Dt);
			TickBathChair(Dt);
			TickHallPendant(Dt);
			TickCeilingCorner(Dt);
			StoryTick(Dt);
			if (BedCamera.IsValid()) TickUnderBed(Dt);
			if (SettlersDropAt >= 0.) TickSettlersPickup();
		if (ListeningSnicker.IsValid()) TickListeningSnicker();
		if (bAuto) AutoTick(Dt);
	}
	else if (Mode == EWCMode::Credits && CreditsScroll >= 0.f)
	{
		CreditsScroll += Dt;
	}
	TickDeputyBreathing(Dt);
	TickAudio(Dt);
	TickLights(Dt);
	if (!bDriving) TickFlies(Dt);
}

void AWCDirector::TickFlies(float Dt)
{
	const int32 N = FlyData.Num();
	if (N == 0) return;
	const float T = (float)Clock;
	if (Mode == EWCMode::Playing && Clock > NextFlyBuzz && Player())
	{
		NextFlyBuzz = Clock + .55;
		const FVector Ear = Player()->EyeLocation();
		const bool Inside = IsInsideHouse(Ear);
		const FFly* Closest = nullptr;
		float Best = FMath::Square(167.f);
		for (const FFly& Fly : FlyData)
		{
			const float D = FVector::DistSquared(Ear, Fly.Centre);
			if (D < Best && IsInsideHouse(Fly.Centre) == Inside) { Best = D; Closest = &Fly; }
		}
		if (Closest && !bBusy && !bEventBusy && (!FlyVoice.IsValid() || !FlyVoice->IsPlaying()))
		{
			FlyVoice = PlayAt(TEXT("flies_buzz"), Closest->Centre, .42f, Rng.FRandRange(.91f,1.07f));
			const auto Voice = FlyVoice;
			After(Rng.FRandRange(.65f,1.25f), [Voice](){ if (Voice.IsValid()) Voice->FadeOut(.22f,0.f); });
			NextFlyBuzz = Clock + Rng.FRandRange(4.5f,9.f);
		}
	}
	for (int32 i = 0; i < N; ++i)
	{
		const FFly& F = FlyData[i];
		// two layered wobbles per axis: darting, never a clean orbit
		const FVector P = F.Centre + FVector(
			F.Radii.X * (FMath::Sin(T * F.Freq.X + F.Phase.X) * 0.7f + FMath::Sin(T * F.Freq.Y * 2.3f + F.Phase.Z) * 0.3f),
			F.Radii.Y * (FMath::Sin(T * F.Freq.Y + F.Phase.Y) * 0.7f + FMath::Sin(T * F.Freq.Z * 1.9f + F.Phase.X) * 0.3f),
			F.Radii.Z * FMath::Sin(T * F.Freq.Z + F.Phase.Z));
		// (never bMarkRenderStateDirty here: it rebuilds the whole proxy every frame, and that crashed; see fix_pass126.py)
		const FVector Velocity(
			F.Radii.X * (.7f * F.Freq.X * FMath::Cos(T * F.Freq.X + F.Phase.X) + .69f * F.Freq.Y * FMath::Cos(T * F.Freq.Y * 2.3f + F.Phase.Z)),
			F.Radii.Y * (.7f * F.Freq.Y * FMath::Cos(T * F.Freq.Y + F.Phase.Y) + .57f * F.Freq.Z * FMath::Cos(T * F.Freq.Z * 1.9f + F.Phase.X)),
			F.Radii.Z * F.Freq.Z * FMath::Cos(T * F.Freq.Z + F.Phase.Z));
		Flies->UpdateInstanceTransform(i, FTransform(Velocity.Rotation(), P, FVector(.09f + .006f * F.Freq.X)), true, false, false);

	}
}

void AWCDirector::TickLights(float Dt)
{
	const float T = (float)Clock;
	// light bar: red and blue trade double flashes
	const float Ph = FMath::Fmod(T, 0.9f);
	const bool bRed = Ph < 0.09f || (Ph > 0.16f && Ph < 0.25f);
	const bool bBlue = (Ph > 0.45f && Ph < 0.54f) || (Ph > 0.61f && Ph < 0.70f);
	for (FLive& L : LiveLights)
	{
		ULightComponent* C = L.Light.Get();
		if (!C || !C->IsVisible()) continue;
		if (L.Kind == 0)
		{
			const float N = 0.82f + 0.12f * FMath::Sin(T * 9.1f + L.Seed) + 0.06f * FMath::Sin(T * 23.7f + L.Seed * 2.f) + (FMath::Sin(T * 1.3f + L.Seed) > 0.96f ? -0.25f : 0.f);
			C->SetIntensity(L.Base * N);
		}
		else C->SetIntensity((L.Kind == 1 ? bRed : bBlue) ? L.Base : L.Base * 0.02f);
	}
	for (int32 k = 0; k < 2; ++k) for (TWeakObjectPtr<AActor>& A : BarMeshes[k])
	{
		if (A.IsValid() && !Has(TEXT("dawn"))) A->SetActorHiddenInGame(!(k == 0 ? bRed : bBlue));
	}
}

void AWCDirector::TickTriggers()
{
	const AWCCharacter* P = Player();
		if (!P || bBusy || bDriving) return;
	const FVector L = P->GetActorLocation();
	for (const TWeakObjectPtr<AWCTrigger>& T : Triggers)
	{
		if (!T.IsValid()) continue;
		const bool bIn = T->Contains(L);
		if (bIn) StoryEvent(FName(*FString::Printf(TEXT("trig:%s"), *T->WCId.ToString())));
		// coming into a room is an event of its own (the triggered sounds count them)
		if (bIn && !TrigInside.Contains(T->WCId)) { TrigInside.Add(T->WCId); CueEvent(FName(*FString::Printf(TEXT("enter:%s"), *T->WCId.ToString()))); }
		else if (!bIn) TrigInside.Remove(T->WCId);
	}
	TickYardCrows();
	TickHallClock();
	TickCues(0.f);
}

// ---------------------------------------------------------------------------------------------- flow
bool AWCDirector::HasSave() const
{
	return UGameplayStatics::DoesSaveGameExist(SaveSlot, 0);
}

static void Reopen(AWCDirector* D)
{
	UGameplayStatics::SetGamePaused(D, false);
	UGameplayStatics::OpenLevel(D, FName(*UGameplayStatics::GetCurrentLevelName(D, true)));
}

void AWCDirector::StartNewGame()
{
	if (Mode != EWCMode::Menu) return;
	UGameplayStatics::DeleteGameInSlot(SaveSlot, 0);
	StartFromMenu(false);
}

void AWCDirector::ContinueGame()
{
	if (Mode == EWCMode::Menu) StartFromMenu(true);
}

void AWCDirector::StartFromMenu(bool bContinue)
{
	// The menu camera is already in a fresh, initialized House. Traveling to it again
	// discards the loaded world and interrupts the opening on the next render frame.
	Mode = EWCMode::Playing;
	Clock = 0.0;
	UGameplayStatics::SetGamePaused(this, false);
	const bool bLoaded = bContinue && DoLoad();
	Fade = 1.f;
	FadeTarget = 1.f;
	StoryBegin(bLoaded);
	UE_LOG(LogWC, Display, TEXT("WCSTART from main menu: %s"), bLoaded ? TEXT("checkpoint") : TEXT("new game"));
}

void AWCDirector::RestartFromCheckpoint()
{
	PendingStart = HasSave() ? 2 : 1;
	Reopen(this);
}

void AWCDirector::QuitToMenu()
{
	PendingStart = 0;
	Reopen(this);
}

void AWCDirector::FadeTo(float Target, float Seconds)
{
	FadeTarget = Target;
	FadeRate = FMath::Abs(Target - Fade) / FMath::Max(Seconds, 0.01f);
	if (Seconds <= 0.f) Fade = Target;
}

// ---------------------------------------------------------------------------------------------- state
void AWCDirector::Event(FName Id)
{
	if (Mode != EWCMode::Playing) return;
	UE_LOG(LogWC, Display, TEXT("WCEVENT t=%.1f %s"), PlaySeconds, *Id.ToString());
	CueEvent(Id);
	StoryEvent(Id);
}

void AWCDirector::GiveItem(FName Item, const FString& DisplayName)
{
	Items.Add(Item);
	Play2D(TEXT("pickup"), 0.7f);
	if (!DisplayName.IsEmpty()) ShowToast(FString::Printf(TEXT("Taken: %s"), *DisplayName));
	if (!Item.ToString().StartsWith(TEXT("ammo")) && !Has(TEXT("inv_hint"))) { Set(TEXT("inv_hint")); ShowHint(TEXT("Tab: what you are carrying"), 7.f); }
}

void AWCDirector::SetObjective(const FString& Text)
{
	if (Objective == Text) return;
	Objective = Text;
	ObjectiveShownAt = Clock;
	UE_LOG(LogWC, Display, TEXT("WCOBJECTIVE t=%.1f %s"), PlaySeconds, *Text);
}

void AWCDirector::ShowToast(const FString& Text, float Seconds)
{
	Toast = Text;
	ToastUntil = Clock + Seconds;
}

void AWCDirector::ShowHint(const FString& Text, float Seconds)
{
	Hint = Text;
	HintUntil = Clock + Seconds;
}

void AWCDirector::OpenNote(AWCNote* Note)
{
	if (!Note) return;
	ActiveNote = Note;
	Play2D(TEXT("paper"), 0.7f);
	if (!NotesRead.Contains(Note->WCId)) NotesRead.Add(Note->WCId);
	if (Note->WCId == TEXT("note_bath_mirror"))
	{
		RefreshBathLetter();
		Checkpoint(TEXT("bath_letter_collected"));
	}
	Event(FName(*FString::Printf(TEXT("read:%s"), *Note->WCId.ToString())));
}

void AWCDirector::CloseNote()
{
	if (!ActiveNote.IsValid()) return;
	const FName Id = ActiveNote->WCId;
	ActiveNote = nullptr;
	Play2D(TEXT("paper"), 0.5f, EWCSnd::SFX, 0.9f);
	Event(FName(*FString::Printf(TEXT("closed:%s"), *Id.ToString())));
}

void AWCDirector::Checkpoint(FName Id)
{
	if (LastCheckpoint == Id) return;
	LastCheckpoint = Id;
	DoSave(Id);
	UE_LOG(LogWC, Display, TEXT("WCCHECKPOINT t=%.1f %s"), PlaySeconds, *Id.ToString());
}

void AWCDirector::RememberAtCheckpoint(FName Flag, bool bEnabled)
{
	if (bEnabled) Set(Flag); else Flags.Remove(Flag);
	// A restart should remember the encounter but restore the original checkpoint,
	// including its inventory, doors and player position.
	if (UWCSave* Saved = Cast<UWCSave>(UGameplayStatics::LoadGameFromSlot(SaveSlot, 0)))
	{
		if (bEnabled) Saved->Flags.AddUnique(Flag); else Saved->Flags.Remove(Flag);
		if (!UGameplayStatics::SaveGameToSlot(Saved, SaveSlot, 0))
			UE_LOG(LogWC, Warning, TEXT("WC: could not persist %s at the current checkpoint"), *Flag.ToString());
	}
}

void AWCDirector::DoSave(FName Id)
{
	UWCSave* S = Cast<UWCSave>(UGameplayStatics::CreateSaveGameObject(UWCSave::StaticClass()));
	if (!S) return;
	S->Flags = Flags.Array();
	S->YardCawsLeft = YardCawsLeft;
	S->Items = Items.Array();
	S->NotesRead = NotesRead;
	S->Objective = Objective;
	S->PlaySeconds = PlaySeconds;
	S->Checkpoint = Id;
	if (AWCCharacter* P = Player())
	{
		S->PlayerLoc = P->GetActorLocation();
		S->PlayerYaw = P->GetControlRotation().Yaw;
		S->Ammo = P->Ammo;
		S->Reserve = P->Reserve;
		S->bLightOn = P->IsFlashlightOn();
	}
	for (TActorIterator<AWCDoor> It(GetWorld()); It; ++It)
	{
		if (It->IsOpen()) S->OpenDoors.Add(It->WCId);
		if (It->bLocked) S->UnlockedDoors.Add(It->WCId);   // (holds the doors that are still locked)
	}
	UGameplayStatics::SaveGameToSlot(S, SaveSlot, 0);
}

bool AWCDirector::DoLoad()
{
	UWCSave* S = Cast<UWCSave>(UGameplayStatics::LoadGameFromSlot(SaveSlot, 0));
	if (!S) return false;
	// Older checkpoints recorded the eye scare before the loose floor key was taken.
	// Repair that same slot in place, preserving its position, doors and other progress.
	if (S->Flags.Contains(TEXT("book_done")) && !S->Flags.Contains(TEXT("desk_open")) && !S->Items.Contains(TEXT("key_desk")))
	{
		S->Items.Add(TEXT("key_desk"));
		if (S->Checkpoint == TEXT("book") || S->Objective.Contains(TEXT("settlers")) || S->Objective.Contains(TEXT("desk key")))
			S->Objective = TEXT("Use the book's small key on Walter's desk in the downstairs den");
		if (!UGameplayStatics::SaveGameToSlot(S, SaveSlot, 0))
			UE_LOG(LogWC, Warning, TEXT("WC: repaired desk key in memory; could not update checkpoint"));
	}
	if (DoorListening != EDoorListening::Idle) FinishDoorListening(false);
	Flags = TSet<FName>(S->Flags);
	YardCawsLeft = FMath::Clamp(S->YardCawsLeft,-1,8);
	NextYardCaw = -1.;
	Items = TSet<FName>(S->Items);
	if (Has(TEXT("scullery_key_found"))) Items.Add(TEXT("key_scullery"));
	NotesRead = S->NotesRead;
	Objective = S->Objective;
	PlaySeconds = S->PlaySeconds;
	LastCheckpoint = S->Checkpoint;
	for (TActorIterator<AWCDoor> It(GetWorld()); It; ++It)
	{
		It->bLocked = S->UnlockedDoors.Contains(It->WCId);
		bool bOpen = S->OpenDoors.Contains(It->WCId);
		if (It->WCId == TEXT("music_sitting"))
		{
			It->bLocked = !Has(TEXT("sitting_open"));
			bOpen &= !It->bLocked;
		}
		else if (It->WCId == TEXT("scullery_pantry") || It->WCId == TEXT("scullery_sickroom"))
		{
			It->bLocked = !Has(TEXT("scullery_open"));
			bOpen &= !It->bLocked;
		}
		It->SetOpen(bOpen, 0.01f, true);
		It->Snap();
	}
	if (AWCDoor* Ruth = Door(TEXT("up_kids")))
		Ruth->HoldAtCrack(Has(TEXT("ruth_door_ajar")) && !Has(TEXT("kids_open")), true);
	for (TActorIterator<AWCPickup> It(GetWorld()); It; ++It)
	{
		if (Items.Contains(It->ItemId)) { It->SetActorHiddenInGame(true); It->SetActorEnableCollision(false); }
	}
	if (AWCCharacter* P = Player())
	{
		P->TeleportToCheckpoint(S->PlayerLoc, S->PlayerYaw);
		P->Ammo = S->Ammo;
		P->Reserve = S->Reserve;
		P->SetFlashlight(S->bLightOn, false);
	}
	ObjectiveShownAt = 2.0;
	return true;
}

// ---------------------------------------------------------------------------------------------- lookups
AActor* AWCDirector::Find(FName Tag) const
{
	if (const TWeakObjectPtr<AActor>* C = TagCache.Find(Tag)) if (C->IsValid()) return C->Get();
	for (TActorIterator<AActor> It(GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(Tag)) { const_cast<AWCDirector*>(this)->TagCache.Add(Tag, *It); return *It; }
	}
	UE_LOG(LogWC, Warning, TEXT("WC: nothing tagged %s"), *Tag.ToString());
	return nullptr;
}

FVector AWCDirector::Pos(FName Tag) const
{
	const AActor* A = Find(Tag);
	return A ? A->GetActorLocation() : FVector::ZeroVector;
}

float AWCDirector::YawOf(FName Tag) const
{
	const AActor* A = Find(Tag);
	return A ? A->GetActorRotation().Yaw : 0.f;
}

AWCDoor* AWCDirector::Door(FName Id) const
{
	for (TActorIterator<AWCDoor> It(GetWorld()); It; ++It) if (It->WCId == Id) return *It;
	UE_LOG(LogWC, Warning, TEXT("WC: no door %s"), *Id.ToString());
	return nullptr;
}

AWCInteractable* AWCDirector::Thing(FName Id) const
{
	for (TActorIterator<AWCInteractable> It(GetWorld()); It; ++It) if (It->WCId == Id) return *It;
	UE_LOG(LogWC, Warning, TEXT("WC: no interactable %s"), *Id.ToString());
	return nullptr;
}

void AWCDirector::ShowTagged(FName Tag, bool bShow)
{
	for (TActorIterator<AActor> It(GetWorld()); It; ++It)
	{
		if (!It->ActorHasTag(Tag)) continue;
		It->SetActorHiddenInGame(!bShow);
		It->SetActorEnableCollision(bShow);
		TArray<ULightComponent*> Lights;
		It->GetComponents(Lights);
		for (ULightComponent* L : Lights) L->SetVisibility(bShow);
	}
}

void AWCDirector::SetLightsTagged(FName Tag, float Scale)
{
	static TMap<TWeakObjectPtr<ULightComponent>, float> Base;
	for (TActorIterator<AActor> It(GetWorld()); It; ++It)
	{
		if (!It->ActorHasTag(Tag)) continue;
		TArray<ULightComponent*> Lights;
		It->GetComponents(Lights);
		for (ULightComponent* L : Lights)
		{
			float* B = Base.Find(L);
			if (!B) B = &Base.Add(L, L->Intensity);
			L->SetIntensity(*B * Scale);
		}
	}
}

bool AWCDirector::PlayerSees(const FVector& Point, float MinDot, float MaxDist) const
{
	const AWCCharacter* P = Player();
	if (!P) return false;
	const FVector Eye = P->EyeLocation();
	const FVector To = Point - Eye;
	const float D = To.Size();
	if (D > MaxDist || D < 1.f) return false;
	if (FVector::DotProduct(To / D, P->EyeForward()) < MinDot) return false;
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(WCSees), false, P);
	return !GetWorld()->LineTraceSingleByChannel(Hit, Eye, Point, ECC_Visibility, Params);
}

// ---------------------------------------------------------------------------------------------- sound
float AWCDirector::Vol(EWCSnd Cat) const
{
	const FWCSettings& S = Settings;
	const float C = Cat == EWCSnd::Music ? S.VolMusic : (Cat == EWCSnd::Voice ? S.VolVoice : S.VolSFX);
	return S.VolMaster * C;
}

USoundBase* AWCDirector::Snd(const FString& Name)
{
	if (Name.IsEmpty()) return nullptr;
	if (TObjectPtr<USoundBase>* Hit = SoundCache.Find(Name)) return Hit->Get();
	if (const TArray<FString>* Vars = SoundVariants.Find(Name))
	{
		if (Vars->Num() == 0) return nullptr;
		return SoundCache.FindRef((*Vars)[Rng.RandHelper(Vars->Num())]);
	}
	const FString Leaf = FPaths::GetCleanFilename(Name);
	if (USoundBase* S = LoadObject<USoundBase>(nullptr, *FString::Printf(TEXT("/Game/WC/Audio/%s.%s"), *Name, *Leaf), nullptr, LOAD_NoWarn | LOAD_Quiet))
	{
		SoundCache.Add(Name, S);
		return S;
	}
	// variants: name_01 .. name_NN, one picked at random each call
	TArray<FString>& Vars = SoundVariants.Add(Name);
	for (int32 i = 1; i <= 12; ++i)
	{
		const FString V = FString::Printf(TEXT("%s_%02d"), *Name, i);
		const FString VLeaf = FPaths::GetCleanFilename(V);
		USoundBase* X = LoadObject<USoundBase>(nullptr, *FString::Printf(TEXT("/Game/WC/Audio/%s.%s"), *V, *VLeaf), nullptr, LOAD_NoWarn | LOAD_Quiet);
		if (!X) break;
		SoundCache.Add(V, X);
		Vars.Add(V);
	}
	if (Vars.Num() == 0)
	{
		UE_LOG(LogWC, Warning, TEXT("WC: missing sound %s"), *Name);
		return nullptr;
	}
	return SoundCache.FindRef(Vars[Rng.RandHelper(Vars.Num())]);
}

UAudioComponent* AWCDirector::Play2D(const FString& Name, float Volume, EWCSnd Cat, float Pitch)
{
	USoundBase* S = Snd(Name);
	if (!S) return nullptr;
	static const bool bSndLog = FParse::Param(FCommandLine::Get(), TEXT("WCSndLog"));
	if (bSndLog && Cat != EWCSnd::Music && Name != TEXT("ui_tick")) UE_LOG(LogWC, Display, TEXT("WCSND t=%.1f 2D %s vol %.2f"), PlaySeconds, *Name, Volume);
	UAudioComponent* A = UGameplayStatics::SpawnSound2D(this, S, FMath::Max(Volume * Vol(Cat), 0.0001f), Pitch, 0.f, nullptr, false, true);
	return A;
}

UAudioComponent* AWCDirector::PlayAt(const FString& Name, const FVector& Where, float Volume, float Pitch, float Radius, bool bShedImpact)
{
	const bool bHouseSource = SpaceAt(Where) != EListeningSpace::Exterior;
	if (bHouseSource && Player() && SpaceAt(Player()->GetActorLocation()) == EListeningSpace::Exterior) return nullptr;
	USoundBase* S = Snd(Name);
	if (!S) return nullptr;
	static const bool bSndLogAt = FParse::Param(FCommandLine::Get(), TEXT("WCSndLog"));
	if (bSndLogAt && (bShedImpact || !Name.StartsWith(TEXT("step_")))) UE_LOG(LogWC, Display, TEXT("WCSND t=%.1f at %s vol %.2f, %.0f cm away"), PlaySeconds, *Name, Volume, Player() ? FVector::Dist(Player()->GetActorLocation(), Where) : -1.f);
	if (!Atten)
	{
		Atten = NewObject<USoundAttenuation>(this);
		Atten->Attenuation.bAttenuate = true;
		Atten->Attenuation.bSpatialize = true;
		Atten->Attenuation.DistanceAlgorithm = EAttenuationDistanceModel::NaturalSound;
		Atten->Attenuation.AttenuationShape = EAttenuationShape::Sphere;
		Atten->Attenuation.AttenuationShapeExtents = FVector(120.f);
		Atten->Attenuation.FalloffDistance = 2600.f;
		Atten->Attenuation.dBAttenuationAtMax = -42.f;
		Atten->Attenuation.bAttenuateWithLPF = true;
		Atten->Attenuation.LPFRadiusMin = 500.f;
		Atten->Attenuation.LPFRadiusMax = 2400.f;
		Atten->Attenuation.bEnableOcclusion = true;
		Atten->Attenuation.OcclusionVolumeAttenuation = 0.55f;
		Atten->Attenuation.OcclusionLowPassFilterFrequency = 1800.f;
		Atten->Attenuation.OcclusionInterpolationTime = 0.3f;
	}
	USoundAttenuation* Profile = Atten;
	if (bShedImpact)
	{
		if (!BinAtten)
		{
			BinAtten = DuplicateObject<USoundAttenuation>(Atten, this);
			BinAtten->Attenuation.AttenuationShapeExtents = FVector(1150.f);
			BinAtten->Attenuation.FalloffDistance = 2400.f;
			BinAtten->Attenuation.LPFRadiusMin = 1200.f;
			BinAtten->Attenuation.OcclusionVolumeAttenuation = .93f;
			BinAtten->Attenuation.OcclusionLowPassFilterFrequency = 7400.f;
		}
		Profile = BinAtten;
	}
	else if (Name == TEXT("shelf_stair_step") || Name == TEXT("ceiling_boot_step"))
	{
		if (!StairRunAtten)
		{
			// The timber carries impacts from the stair treads and ceiling joists.
			StairRunAtten = DuplicateObject<USoundAttenuation>(Atten, this);
			StairRunAtten->Attenuation.AttenuationShapeExtents = FVector(320.f);
			StairRunAtten->Attenuation.FalloffDistance = 1680.f;
			StairRunAtten->Attenuation.dBAttenuationAtMax = -22.f;
			StairRunAtten->Attenuation.OcclusionVolumeAttenuation = .90f;
			StairRunAtten->Attenuation.OcclusionLowPassFilterFrequency = 3500.f;
		}
		Profile = StairRunAtten;
	}
	else if (Name == TEXT("yard_caw"))
	{
		if (!CrowAtten)
		{
			CrowAtten = DuplicateObject<USoundAttenuation>(Atten, this);
			CrowAtten->Attenuation.AttenuationShapeExtents = FVector(660.f);
			CrowAtten->Attenuation.FalloffDistance = 3900.f;
			CrowAtten->Attenuation.dBAttenuationAtMax = -30.f;
			CrowAtten->Attenuation.OcclusionVolumeAttenuation = .87f;
			CrowAtten->Attenuation.OcclusionLowPassFilterFrequency = 3900.f;
		}
		Profile = CrowAtten;
	}
	else if (Name == TEXT("wheel_baseboard") || Name == TEXT("wheel_sidefall") || Name == TEXT("wheel_axle_rub"))
	{
		if (!ChairImpactAtten)
		{
			ChairImpactAtten = DuplicateObject<USoundAttenuation>(Atten, this);
			ChairImpactAtten->Attenuation.AttenuationShapeExtents = FVector(340.f);
			ChairImpactAtten->Attenuation.FalloffDistance = 2650.f;
			ChairImpactAtten->Attenuation.dBAttenuationAtMax = -28.f;
			ChairImpactAtten->Attenuation.OcclusionVolumeAttenuation = .83f;
			ChairImpactAtten->Attenuation.OcclusionLowPassFilterFrequency = 4200.f;
		}
		Profile = ChairImpactAtten;
	}
	else if (Name == TEXT("flies_buzz"))
	{
		if (!FlyAtten)
		{
			FlyAtten = DuplicateObject<USoundAttenuation>(Atten, this);
			FlyAtten->Attenuation.DistanceAlgorithm = EAttenuationDistanceModel::Linear;
			FlyAtten->Attenuation.AttenuationShapeExtents = FVector(35.f);
			FlyAtten->Attenuation.FalloffDistance = 185.f;
		}
		Profile = FlyAtten;
	}
	UAudioComponent* Audio = UGameplayStatics::SpawnSoundAtLocation(this, S, Where, FRotator::ZeroRotator, FMath::Max(Volume * Vol(EWCSnd::SFX), 0.0001f), Pitch, 0.f, Profile, nullptr, true);
	if (Audio && bHouseSource) Audio->ComponentTags.Add(TEXT("HouseAudio"));
	return Audio;
}

void AWCDirector::SetLoop(FName Slot, const FString& Name, float Volume, float FadeSeconds, EWCSnd Cat)
{
	const bool bIndoor = Name == TEXT("amb_house") || Name == TEXT("amb_cellar") || Name == TEXT("music_house") || Name == TEXT("music_low") || Name == TEXT("music_stalk");
	if (bIndoor && Player() && SpaceAt(Player()->GetActorLocation()) == EListeningSpace::Exterior) return;
	FLoop& L = Loops.FindOrAdd(Slot);
	if (L.Name == Name && L.Audio.IsValid())
	{
		L.Target = Volume;
		L.Rate = 1.f / FMath::Max(FadeSeconds, 0.05f);
		return;
	}
	if (UAudioComponent* Old = L.Audio.Get())
	{
		Old->bAutoDestroy = true;
		if (FadeSeconds <= 0.f) Old->Stop();
		else Old->FadeOut(FadeSeconds, 0.f);
	}
	L = FLoop();
	L.Name = Name;
	L.Cat = Cat;
	L.Target = Volume;
	L.Rate = 1.f / FMath::Max(FadeSeconds, 0.05f);
	if (USoundBase* S = Snd(Name))
	{
		UAudioComponent* A = UGameplayStatics::SpawnSound2D(this, S, 0.0001f, 1.f, 0.f, nullptr, false, false);
		if (A)
		{
			A->bIsUISound = false;
			if (bIndoor) A->ComponentTags.Add(TEXT("HouseAudio"));
		}
		L.Audio = A;
	}
}

void AWCDirector::ApplyVolumes()
{
	if (DeputyBreath.IsValid()) DeputyBreath->SetVolumeMultiplier(DeputyBreathGain * Vol(EWCSnd::SFX));
	for (TPair<FName, FLoop>& P : Loops)
	{
		if (UAudioComponent* A = P.Value.Audio.Get()) A->SetVolumeMultiplier(FMath::Max(P.Value.Vol * Vol(P.Value.Cat), 0.0001f));
	}
}

// House coordinates match build_house.py and the ground-floor living-room extension.
AWCDirector::EListeningSpace AWCDirector::SpaceAt(const FVector& P)
{
	if (P.Z >= -22. && P.Z < 312. && ((P.X > 1690. && P.X < 2510. && P.Y >= 600. && P.Y < 892.) ||
		(P.X > 550. && P.X < 1205. && P.Y > -1015. && P.Y <= (P.X < 800. ? -750. : -600.))))
		return EListeningSpace::House;
	// The upstairs extension is over the open rear porch.
	const bool bUpperExtension = P.X < 3420. && P.Z >= 329. && P.Z < 1026.;
	if (P.X <= 0 || (P.X >= 2800 && !bUpperExtension) || P.Y >= 600) return EListeningSpace::Exterior;
	if (P.Y <= -600 && !(P.X < 800 && P.Y > -750 && P.Z >= 0 && P.Z < 330)) return EListeningSpace::Exterior;
	return P.Z < -25 && P.X < 1620 ? EListeningSpace::Cellar : EListeningSpace::House;
}

void AWCDirector::RefreshRoomTone(EListeningSpace Space)
{
	const bool bOutside = Space == EListeningSpace::Exterior;
	const bool bDarkInside = !bOutside && !Has(TEXT("dawn"));
	if (bOutside && ListeningSpace != Space)
	{
		for (TObjectIterator<UAudioComponent> It; It; ++It)
			if (It->GetWorld() == GetWorld() && It->ComponentHasTag(TEXT("HouseAudio"))) It->Stop();
		for (auto& Pair : Loops)
			if (Pair.Value.Audio.IsValid() && Pair.Value.Audio->ComponentHasTag(TEXT("HouseAudio")))
				Pair.Value.Target = 0.f;
	}
	if (!bOutside && YardCrowVoice.IsValid() && YardCrowVoice->IsPlaying())
		YardCrowVoice->FadeOut(.08f, 0.f);
	ListeningSpace = Space;
	const TCHAR* Bed = bOutside ? (Has(TEXT("dawn")) ? TEXT("amb_dawn") : TEXT("amb_yard")) :
		(Space == EListeningSpace::Cellar ? TEXT("amb_cellar") : TEXT("amb_house"));
	SetLoop(TEXT("amb"), Bed, 1.f, bOutside ? 0.f : 0.65f);
	const bool bYardScore = bOutside && !bDriving && !Has(TEXT("dawn"));
	SetLoop(TEXT("yard_score"), bYardScore ? TEXT("music_drone") : TEXT(""), bYardScore ? .23f : 0.f, 2.6f, EWCSnd::Music);
	SetLoop(TEXT("drone"), bDarkInside ? TEXT("music_house") : TEXT(""), 0.55f, bDarkInside ? 1.2f : 0.f, EWCSnd::Music);
	// The two tracks crossfade inside a single seamless house loop.
	if (FParse::Param(FCommandLine::Get(), TEXT("WCSndLog")))
		UE_LOG(LogWC, Display, TEXT("WCROOM bed=%s interiorScore=%d"), Bed, bDarkInside);
}

void AWCDirector::PlayScareLead(float Seconds)
{
	if (!Player() || (ScareLead.IsValid() && ScareLead->IsPlaying())) return;
	UAudioComponent* Cue = Play2D(TEXT("scare_bump"), .71f, EWCSnd::Music);
	if (!Cue) return;
	ScareLead = Cue;
	Cue->bIsUISound = false;
	if (IsInsideHouse(Player()->GetActorLocation())) Cue->ComponentTags.Add(TEXT("HouseAudio"));
	const TWeakObjectPtr<UAudioComponent> Voice = Cue;
	After(FMath::Max(.1f, Seconds - .22f), [Voice]()
	{
		if (Voice.IsValid()) Voice->FadeOut(.22f, 0.f);
	});
	if (FParse::Param(FCommandLine::Get(), TEXT("WCSndLog")))
		UE_LOG(LogWC, Display, TEXT("WCSCORE t=%.1f Bump in the Night (%.1fs)"), PlaySeconds, Seconds);
}

void AWCDirector::StartleDeputy(float Strength)
{
	BreathFear = FMath::Max(BreathFear, Strength);
}

void AWCDirector::HoldDeputyBreath(float Seconds)
{
	BreathResumeAt = FMath::Max(BreathResumeAt, Clock + Seconds);
	NextBreathAt = BreathResumeAt + .12;
	if (DeputyBreath.IsValid()) DeputyBreath->FadeOut(.08f, 0.f);
}

void AWCDirector::TickDeputyBreathing(float Dt)
{
	if ((!IsPlaying() && Mode != EWCMode::Ending) || !Player() || bDoorSilence)
	{
		if (DeputyBreath.IsValid()) DeputyBreath->Stop();
		NextBreathAt = Clock + .12;
		return;
	}

	const bool bChased = StalkState == 2 || bSprintActive || (bLockInActive && bLockInRun) || Clock < GrabHoldUntil;
	const float Unease = .55f * FMath::SmoothStep(.24f, .95f, Tension);
	const float Target = bChased ? 1.f : Unease;
	BreathFear = FMath::FInterpConstantTo(BreathFear, Target, Dt, Target > BreathFear ? 1.1f : .047f);
	if (Clock < NextBreathAt || Clock < BreathResumeAt || (DeputyBreath.IsValid() && DeputyBreath->IsPlaying())) return;

	// Independent cadence and takes keep the breath from changing the house's random events.
	LastBreathTake = (LastBreathTake + BreathRandom.RandRange(1, 2)) % 3;
	const bool bQuick = BreathFear >= .52f;
	const FString Cue = FString::Printf(TEXT("deputy_%s_%02d"), bQuick ? TEXT("quick") : TEXT("steady"), LastBreathTake + 1);
	// Gain is relative to the auditioned recordings. The takes carry their own timing.
	const float GainDb = FMath::Lerp(-18.f, 1.5f, FMath::SmoothStep(.22f, .82f, BreathFear));
	DeputyBreathGain = FMath::Pow(10.f, GainDb / 20.f) * (Clock < DialogueUntil ? .78f : 1.f);
	NextBreathAt = Clock + .5;  // avoid polling for a missing asset every frame
	if (USoundBase* Clip = Snd(Cue))
	{
		DeputyBreath = UGameplayStatics::CreateSound2D(this, Clip, DeputyBreathGain * Vol(EWCSnd::SFX));
		if (DeputyBreath.IsValid())
		{
			DeputyBreath->bIsUISound = false;
			DeputyBreath->Play();
			const float Rest = bQuick ? BreathRandom.FRandRange(.02f,.10f) : BreathRandom.FRandRange(.10f,.38f);
			NextBreathAt = Clock + Clip->GetDuration() + Rest;
			static const bool bLog = FParse::Param(FCommandLine::Get(), TEXT("WCSndLog"));
			if (bLog) UE_LOG(LogWC,Display,TEXT("WCBREATH t=%.2f %s fear=%.2f pitch=1.000 gain=%.2f drive=%d chase=%d"), PlaySeconds, *Cue, BreathFear, DeputyBreathGain, bDriving, bChased);
		}
	}
}

void AWCDirector::TickAudio(float Dt)
{
	for (TPair<FName, FLoop>& P : Loops)
	{
		FLoop& L = P.Value;
		UAudioComponent* A = L.Audio.Get();
		if (!A) continue;
		const bool bDuck = P.Key == TEXT("drone") && ScareLead.IsValid() && ScareLead->IsPlaying();
		const float Target = bDuck ? .28f * L.Target : L.Target;
		if (!FMath::IsNearlyEqual(L.Vol, Target, 0.0005f))
		{
			L.Vol = FMath::FInterpConstantTo(L.Vol, Target, Dt, L.Rate);
			A->SetVolumeMultiplier(FMath::Max(L.Vol * Vol(L.Cat), 0.0001f));
		}
		if (!A->IsPlaying() && L.Target > 0.f && A->Sound && A->Sound->IsLooping()) A->Play();
	}
}

void AWCDirector::Footstep(const FVector& Feet, float Loud, FName Surface)
{
	const FString Name = FString::Printf(TEXT("step_%s"), *Surface.ToString().ToLower());
	const float Gain = Player() && IsInsideHouse(Player()->GetActorLocation()) ? .90f : .42f;
	UAudioComponent* A = Play2D(Name, Gain * Loud, EWCSnd::SFX, Rng.FRandRange(0.93f, 1.07f));
	if (!A && Surface != TEXT("Wood")) Play2D(TEXT("step_wood"), Gain * Loud, EWCSnd::SFX, Rng.FRandRange(0.93f, 1.07f));
	if (Clock >= NextBoardCreak && (Surface == TEXT("Wood") || Surface == TEXT("Stairs")) &&
		ListeningSpace != EListeningSpace::Exterior && Rng.FRand() < .12f)
	{
		NextBoardCreak = Clock + Rng.FRandRange(12.f, 26.f);
		PlayAt(TEXT("creak"), Feet, .36f * Loud, Rng.FRandRange(.88f, 1.06f));
	}
}
