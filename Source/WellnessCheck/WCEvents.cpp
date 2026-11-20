// Things in the house that act by themselves: the phonograph that will not stay off, and her voice coming closer.
// (Cheyenne: "fear can be cultivated by sounds, and by other stuff too ... stuff that can turn on by itself".)
#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"

#include "Components/AudioComponent.h"
#include "Sound/SoundBase.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"
#include "GameFramework/Controller.h"
#include "Components/PointLightComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Texture2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/KismetRenderingLibrary.h"
#include "Engine/PostProcessVolume.h"
#include "EngineUtils.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UObject/UObjectIterator.h"

DEFINE_LOG_CATEGORY_STATIC(LogWCEvents, Log, All);

// ================================================================================================ the phonograph (S11)
void AWCDirector::RecordPlay(bool bOn)
{
	AWCInteractable* Ph = Thing(TEXT("phonograph"));
	if (!Ph) return;
	const FVector At = Ph->GetActorLocation() + FVector(0, 0, 95);
	if (RecordAudio.IsValid()) { RecordAudio->FadeOut(bOn ? 0.05f : 0.2f, 0.f); RecordAudio = nullptr; }
	if (bOn)
	{
		PlayAt(TEXT("radio_click"), At, 0.7f, 0.8f, 1500.f);
		RecordAudio = PlayAt(TEXT("record_tune"), At, 1.f, 1.f, 3400.f);
		Ph->Prompt = TEXT("Lift the needle");
	}
	else
	{
		PlayAt(TEXT("record_stop"), At, 0.9f, 1.f, 1800.f);
		Ph->Prompt = TEXT("Look at the phonograph");
	}
}

void AWCDirector::TickRecord(float Dt)
{
	if (RecordPhase >= 9) return;
	if (Has(TEXT("record_done")) || Has(TEXT("dawn")) || Has(TEXT("sprint_started")))
	{
		if (RecordPhase > 0) { RecordPlay(false); bEventBusy = false; }
		RecordPhase = 9;
		return;
	}
	AWCCharacter* P = Player();
	AWCInteractable* Ph = Thing(TEXT("phonograph"));
	if (!P || !Ph) return;
	const FVector At = Ph->GetActorLocation();
	const float Dist = FVector::Dist(P->GetActorLocation(), At + FVector(0, 0, 88));
	const double In = (Clock - RecordAt) / FMath::Max(TestPace, 0.2f);          // waits shrink in fast test runs
	auto Go = [this](int32 Phase)
	{
		RecordPhase = Phase; RecordAt = Clock;
		UE_LOG(LogWCEvents, Display, TEXT("WCRECORD t=%.1f phase %d"), PlaySeconds, Phase);
	};
	switch (RecordPhase)
	{
	case 0:      // a quiet stretch, after he has been through her sitting room, with him somewhere else
		if (HasItem(TEXT("key_prayer")) && Gate() && !bBusy && !P->IsDown() && Dist > 650.f && Dist < 2600.f)
		{
			UE_LOG(LogWCEvents, Display, TEXT("WCSCARE t=%.1f S11_record"), PlaySeconds);
			bEventBusy = true;
			RecordSeenAt = -1.0;
			RecordPlay(true);
			After(3.5f, [this]() { Think(TEXT("Music. From her sitting room.")); });
			Go(1);
		}
		break;
	case 1: case 3: case 6:      // playing, until he lifts the needle (or it runs down)
		if (In > 95.0) { RecordPlay(false); Go(RecordPhase == 6 ? 7 : RecordPhase + 1); }
		break;
	case 2:      // a few steps away, and it starts again
		if (Dist > 330.f || In > 45.0) { RecordPlay(true); Go(3); }
		break;
	case 4:      // and again: and this time the light goes
		if (Dist > 330.f || In > 45.0)
		{
			RecordPlay(true);
			KillLights(30.f, true);
			P->FlickerLight(1.6f, 0.95f);
			After(1.5f, [this]() { if (AWCCharacter* Pl = Player()) Pl->SetLightScale(0.f); });
			After(4.2f, [this]() { if (AWCCharacter* Pl = Player()) PlayAt(TEXT("creak"), Pl->GetActorLocation() - Pl->GetActorForwardVector() * 170.f, 1.f, 0.8f, 1200.f); });
			After(6.6f, [this]() { if (AWCCharacter* Pl = Player()) PlayAt(TEXT("breath_near"), Pl->GetActorLocation() - Pl->GetActorForwardVector() * 70.f + FVector(0, 0, 50), 1.f, 1.f, 600.f); });
			Tension = 0.9f;
			Go(5);
		}
		break;
	case 5:      // in the dark, with the music
		if (In > 10.0) { P->SetLightScale(1.f); P->FlickerLight(0.9f, 0.7f); Go(6); }
		break;
	case 7:      // needle up for the third time.  He turns away from it, and she is in the doorway.
	{
		const FVector ToPh = (At - P->GetActorLocation()).GetSafeNormal2D();
		const bool bTurned = FVector::DotProduct(P->EyeForward().GetSafeNormal2D(), ToPh) < 0.2f || Dist > 270.f;
		if ((bTurned && In > 0.8) || In > 25.0)
		{
			if (AWCEntity* H = Her())
			{
				H->Appear(Pos(TEXT("Her_RecordDoor")), YawOf(TEXT("Her_RecordDoor")), TEXT("Idle"));
				H->FacePlayer(true);
				H->SetGlow(1.4f);
			}
			if (bAuto && !AutoShotDir.IsEmpty())
			{
				// test runs: turn to the door and photograph her
				if (AController* Ct = P->GetController()) Ct->SetControlRotation((Pos(TEXT("Her_RecordDoor")) + FVector(0, 0, 170) - P->EyeLocation()).Rotation());
				const FString File = AutoShotDir / TEXT("S11_record_doorway.png");
				After(0.25f, [File]() { FScreenshotRequest::RequestScreenshot(File, false, false); });
			}
			Go(8);
		}
		break;
	}
	case 8:      // gone in an instant
	{
		AWCEntity* H = Her();
		if (H && H->IsShown() && RecordSeenAt < 0.0 && PlayerSees(H->HeadLocation(), 0.5f, 2600.f)) { RecordSeenAt = Clock; Play2D(TEXT("sting_soft"), 0.7f, EWCSnd::Music); }
		if ((RecordSeenAt > 0.0 && Clock - RecordSeenAt > 0.5) || Clock - RecordAt > 7.0)
		{
			if (H) H->Vanish();
			P->FlickerLight(0.5f, 0.8f);
			RecordPhase = 9;
			bEventBusy = false;
			Set(TEXT("record_done"));
			Rest(150.f);
			Tension = 0.6f;
			if (RecordSeenAt > 0.0) After(1.8f, [this]() { Think(TEXT("She was standing right there.")); });
			Checkpoint(TEXT("record"));
		}
		break;
	}
	default: break;
	}
}

// ================================================================================================ "you left me" (S12)
void AWCDirector::LeftScare()
{
	Flags.Remove(TEXT("left_pending"));
	Set(TEXT("left_done"));
	bEventBusy = true;
	UE_LOG(LogWCEvents, Display, TEXT("WCSCARE t=%.1f S12_left"), PlaySeconds);
	// somewhere behind him, wherever he is facing by then
	auto Behind = [this](float Dist, float Up)
	{
		AWCCharacter* Pl = Player();
		return Pl ? Pl->GetActorLocation() - FRotator(0.f, Pl->GetControlRotation().Yaw, 0.f).Vector() * Dist + FVector(0, 0, Up) : FVector::ZeroVector;
	};
	PlayAt(TEXT("whisper_far"), Behind(1300.f, 0.f), 0.6f, 1.f, 2600.f);
	After(4.5f, [this, Behind]() { PlayAt(TEXT("whisper_far"), Behind(800.f, 0.f), 0.8f, 1.05f, 2200.f); });
	After(8.0f, [this, Behind]() { PlayAt(TEXT("VO/m_left"), Behind(520.f, 20.f), 0.55f, 1.f, 1800.f); });
	After(11.0f, [this, Behind]() { PlayAt(TEXT("VO/m_left"), Behind(260.f, 30.f), 0.8f, 1.06f, 1200.f); });
	After(12.4f, [this, Behind]() { PlayAt(TEXT("VO/m_left"), Behind(130.f, 40.f), 1.f, 1.12f, 900.f); });
	// the beat: everything stops, even the clock
	After(14.8f, [this]()
	{
		HoldDeputyBreath(3.2f);
		SetLoop(TEXT("amb"), TEXT(""), 0.f, 0.3f);
		SetLoop(TEXT("music"), TEXT(""), 0.f, 0.3f);
		for (TObjectIterator<UAudioComponent> It; It; ++It) if (It->GetWorld() == GetWorld() && It->Sound && It->Sound->GetName().Contains(TEXT("m_left"))) It->FadeOut(0.1f, 0.f);
		Tension = 0.15f;
	});
	// then all at once
	After(18.0f, [this]()
	{
		Play2D(TEXT("bell_toll"), .30f);
		Say(TEXT("m_whyleave"));
		StartleDeputy(1.f);
		if (AWCCharacter* Pl = Player()) { Pl->AddShake(1.f); Pl->FlickerLight(1.6f, 0.9f); }
		Tension = 1.f;
	});
	After(18.f + LineSeconds(TEXT("m_whyleave")) + .55f, [this]()
	{
		ApplyWorldState();
		bEventBusy = false;
		Rest(170.f);
		Think(TEXT("...Nobody. There is nobody there."));
		Checkpoint(TEXT("left"));
	});
}

// ================================================================================================ events
bool AWCDirector::EventsEvent(FName Id)
{
	if (Id == TEXT("use:tv"))
	{
		if (TVPhase == 1)
		{
			AWCCharacter* Pl = Player();
			AWCInteractable* Tv = Thing(TEXT("tv"));
			const bool bClose = Pl && Tv && FVector::Dist2D(Pl->GetActorLocation(), Tv->GetActorLocation()) < 175.f;
			if (Pl && Pl->bIsCrouched && bClose) TVOff(true);
			else
			{
				ShowHint(TEXT("C: crouch, close to the set, then E to switch it off"), 6.f);
			}
		}
		else if (TVPhase == 0)
		{
			static const TCHAR* TapeId[3] = { TEXT("tape1"), TEXT("tape2"), TEXT("tape3") };
			int32 Have = 0;
			for (int32 i = 0; i < 3 && Have == 0; ++i) if (HasItem(TapeId[i])) Have = i + 1;
			if (Have == 0)
			{
				Feedback(Has(TEXT("tape_played")) ? TEXT("The slot is empty. There were more tapes than this.") : TEXT("An old console set with a tape slot under the screen. Nothing in it."));
				return true;
			}
			if (TVWant != 0) return true;
			if (Have == 2 && (StalkState != 0 || bBusy || bEventBusy))
			{
				Feedback(TEXT("Something is here. Hold on to the tape."));
				return true;
			}
			if (Have == 2) bEventBusy = true;
			Items.Remove(TapeId[Have - 1]);
			Set(TEXT("tape_played"));
			Set(FName(*FString::Printf(TEXT("tape%d_played"), Have)));
			UE_LOG(LogWCEvents, Display, TEXT("WCTAPE t=%.1f tape %d goes into the set"), PlaySeconds, Have);
			if (AWCInteractable* Tv0 = Thing(TEXT("tv"))) PlayAt(TEXT("door_unlock"), Tv0->GetActorLocation() + FVector(0, 0, 90), 0.8f, 0.6f, 1200.f);       // the tape going home
			TVWant = Have;
			After(1.5f, [this]() { if (TVPhase == 0) TVOn(); });
		}
		return true;
	}
	if (Id == TEXT("use:phonograph"))
	{
		if (RecordPhase == 1 || RecordPhase == 3 || RecordPhase == 6)
		{
			RecordPlay(false);
			RecordPhase = RecordPhase == 6 ? 7 : RecordPhase + 1;
			RecordAt = Clock;
			UE_LOG(LogWCEvents, Display, TEXT("WCRECORD t=%.1f he lifted the needle, phase %d"), PlaySeconds, RecordPhase);
		}
		else Feedback(TEXT("The record is worn white in one groove. One song. I can almost hear which."));
		return true;
	}
	if (Id == TEXT("trig:t_daniel") && Has(TEXT("peek_done")) && !Has(TEXT("left_done")) && !Has(TEXT("left_pending")))
	{
		// Daniel's room: the one who left first
		Set(TEXT("left_pending"));
		WhenQuiet([this]() { LeftScare(); },
			[this]() { AWCCharacter* Pl = Player(); return Pl && Pl->GetActorLocation().X > 1600.f && Pl->GetActorLocation().Y < -190.f && Pl->GetActorLocation().Z > 300.f; },
			[this]() { Flags.Remove(TEXT("left_pending")); }, 45.f);
	}
	return false;
}

// ================================================================================================ the television (S13)
static const int32 GTapeFrames = 240;        // 20 s at 12 a second, 16 across and 15 down
static const float GTapeFps = 12.f;

void AWCDirector::TVOn()
{
	AWCInteractable* Tv = Thing(TEXT("tv"));
	if (!Tv || !Tv->Mesh) return;
	if (!TVScreen)
	{
		// the picture is whichever material slot is called Screen
		const int32 Slot = FMath::Max(0, Tv->Mesh->GetMaterialIndex(TEXT("Screen")));
		TVScreen = Tv->Mesh->CreateDynamicMaterialInstance(Slot);
		UE_LOG(LogWCEvents, Display, TEXT("WCTV screen slot %d of %d, material %s, parent %s"), Slot, Tv->Mesh->GetNumMaterials(), *GetNameSafe(Tv->Mesh->GetMaterial(Slot)), TVScreen ? *GetNameSafe(TVScreen->Parent) : TEXT("none"));
		float G = 0.f;
		if (TVScreen && FParse::Value(FCommandLine::Get(), TEXT("WCTVGain="), G)) TVScreen->SetScalarParameterValue(TEXT("Gain"), G);
		if (TVScreen && FParse::Value(FCommandLine::Get(), TEXT("WCTVRGain="), G)) TVScreen->SetScalarParameterValue(TEXT("RGain"), G);
		TVGlow = NewObject<UPointLightComponent>(Tv);
		TVGlow->SetupAttachment(Tv->GetRootComponent());
		TVGlow->RegisterComponent();
		TVGlow->SetIntensityUnits(ELightUnits::Lumens);
		TVGlow->SetAttenuationRadius(950.f);
		TVGlow->SetLightColor(FLinearColor(0.62f, 0.74f, 1.f));
		TVGlow->SetCastShadows(true);
		TVGlow->SetIntensity(0.f);
	}
	int32 Tapes = 0;
	for (int32 i = 1; i <= 8; ++i) if (LoadObject<UTexture2D>(nullptr, *FString::Printf(TEXT("/Game/WC/TV/T_Tape_%d.T_Tape_%d"), i, i), nullptr, LOAD_NoWarn | LOAD_Quiet)) Tapes = i; else break;
	if (Tapes == 0 || !TVScreen) { UE_LOG(LogWCEvents, Warning, TEXT("WCTV no tapes imported")); TVNextAt = Clock + 600.0; return; }
	const int32 N = TVWant > 0 ? FMath::Clamp(TVWant, 1, Tapes) : 1 + (TVTape % Tapes);
	TVWant = 0;
	++TVTape;
	TVScreen->SetTextureParameterValue(TEXT("Atlas"), LoadObject<UTexture2D>(nullptr, *FString::Printf(TEXT("/Game/WC/TV/T_Tape_%d.T_Tape_%d"), N, N)));
	TVScreen->SetScalarParameterValue(TEXT("Mode"), 1.f);
	TVScreen->SetScalarParameterValue(TEXT("Frame"), 0.f);
	const FVector At = Tv->GetActorLocation() + FVector(0, 0, 55);
	// in front of the glass, wherever the set faces
	TVGlow->SetWorldLocation(At + (Player() ? (Player()->GetActorLocation() - At).GetSafeNormal2D() * 45.f : FVector(0, 45, 0)));
	PlayAt(TEXT("switch_click"), At, 1.f, 0.8f, 1500.f);
	if (TVAudio.IsValid()) TVAudio->Stop();
	TVTapeNow = N;
	TVLoop = -1;                                    // the sound is started (and restarted each time round) in TickTV
	Tv->Prompt = TEXT("Crouch close and switch the television off");
	TVPhase = 1;
	TVAt = Clock;
	Tension = FMath::Max(Tension, 0.6f);
	UE_LOG(LogWCEvents, Display, TEXT("WCTV t=%.1f switched itself on, tape %d of %d"), PlaySeconds, N, Tapes);
	if (!Has(TEXT("tv_seen"))) Set(TEXT("tv_seen"));
	else if (!Has(TEXT("tv_again"))) { Set(TEXT("tv_again")); After(2.5f, [this]() { Think(TEXT("I switched that off.")); }); }
}

void AWCDirector::TVOff(bool bByHim, bool bForceScare)
{
	AWCInteractable* Tv = Thing(TEXT("tv"));
	AWCCharacter* P = Player();
	if (!Tv || !TVScreen) return;
	const FVector At = Tv->GetActorLocation() + FVector(0, 0, 55);
	if (TVAudio.IsValid()) { TVAudio->Stop(); TVAudio = nullptr; }
	PlayAt(TEXT("switch_click"), At, 1.f, 0.7f, 1500.f);
	PlayAt(TEXT("bulb_die"), At, 0.5f, 1.3f, 1200.f);
	if (TVGlow) TVGlow->SetIntensity(0.f);
	Tv->Prompt = TEXT("Look at the television");
	const bool bScare = P && (bForceScare || (bByHim && TVTapeNow == 2 && !Has(TEXT("tv_scare"))));
	if (!bScare)
	{
		if (TVTapeNow == 2) bEventBusy = false;
		TVScreen->SetScalarParameterValue(TEXT("Mode"), 0.f);
		TVPhase = 0;
		TVNextAt = Clock + 420.0 * FMath::Max(TestPace, 0.25f);
		return;
	}
	// ---- the dead glass shows the room behind him
	UE_LOG(LogWCEvents, Display, TEXT("WCSCARE t=%.1f S13_tv_reflection"), PlaySeconds);
	Set(TEXT("tv_scare"));
	bEventBusy = true;
	if (!TVTarget)
	{
		TVTarget = NewObject<UTextureRenderTarget2D>(this);
		TVTarget->RenderTargetFormat = RTF_RGBA8;
		TVTarget->InitAutoFormat(512, 384);
		TVTarget->UpdateResourceImmediate(true);
		TVCapture = NewObject<USceneCaptureComponent2D>(Tv);
		TVCapture->SetupAttachment(Tv->GetRootComponent());
		TVCapture->RegisterComponent();
		TVCapture->TextureTarget = TVTarget;
		TVCapture->CaptureSource = ESceneCaptureSource::SCS_FinalColorLDR;
		TVCapture->FOVAngle = 78.f;
		TVCapture->bCaptureOnMovement = false;
		// its own exposure: with the room's grade alone the mirror came out about six stops darker than the game view
		float Ev = -2.0f;
		FParse::Value(FCommandLine::Get(), TEXT("WCTVEV="), Ev);
		TVCapture->PostProcessSettings.bOverride_AutoExposureMethod = true;
		TVCapture->PostProcessSettings.AutoExposureMethod = EAutoExposureMethod::AEM_Manual;
		TVCapture->PostProcessSettings.bOverride_AutoExposureBias = true;
		TVCapture->PostProcessSettings.AutoExposureBias = Ev;
		TVCapture->PostProcessSettings.bOverride_VignetteIntensity = true;
		TVCapture->PostProcessSettings.VignetteIntensity = 0.f;
		TVCapture->PostProcessSettings.bOverride_FilmGrainIntensity = true;
		TVCapture->PostProcessSettings.FilmGrainIntensity = 0.f;
		TVCapture->PostProcessBlendWeight = 1.f;
		TVCapture->bAlwaysPersistRenderingState = true;
	}
	const FVector Out = (P->GetActorLocation() - At).GetSafeNormal2D();
	TVCapture->SetWorldLocationAndRotation(At + Out * 34.f + FVector(0, 0, 8), FRotator(9.f, Out.Rotation().Yaw, 0.f));
	TVCapture->bCaptureEveryFrame = true;
	TVCapture->SetActive(true);
	TVScreen->SetTextureParameterValue(TEXT("Reflect"), TVTarget);
	TVScreen->SetScalarParameterValue(TEXT("Mode"), 2.f);
	P->SetLightScale(0.07f);                     // his own light sinks with the tube: the dead glass is the brightest thing left
	SetLoop(TEXT("amb"), TEXT("amb_house"), 0.05f, 0.4f);
	TVPhase = 2;
	TVAt = Clock;
	TVHerAt = -1.0;
	TVRunAt = -1.0;
}

void AWCDirector::TVReflectionEnd()
{
	if (AWCEntity* H = Her())
	{
		TInlineComponentArray<UPrimitiveComponent*> Prims(H);
		for (UPrimitiveComponent* C : Prims) { C->bVisibleInSceneCaptureOnly = false; C->MarkRenderStateDirty(); }
		H->Vanish();
	}
	if (TVHerLight) { TVHerLight->DestroyComponent(); TVHerLight = nullptr; }
	if (TVCapture) { TVCapture->bCaptureEveryFrame = false; TVCapture->SetActive(false); }
	if (TVScreen) TVScreen->SetScalarParameterValue(TEXT("Mode"), 0.f);
	if (AWCCharacter* Pl = Player()) { Pl->SetLightScale(1.f); Pl->FlickerLight(0.5f, 0.7f); }
	for (TObjectIterator<UAudioComponent> It; It; ++It) if (It->GetWorld() == GetWorld() && It->Sound && It->Sound->GetName().Contains(TEXT("her_scream"))) It->FadeOut(0.12f, 0.f);
	TVPhase = 0;
	TVNextAt = Clock + 420.0 * FMath::Max(TestPace, 0.25f);
	bEventBusy = false;
	Rest(170.f);
	Tension = 0.7f;
	ApplyWorldState();
	After(1.6f, [this]() { Think(TEXT("...Nothing. Nothing behind me.")); });
	Checkpoint(TEXT("tv"));
}

void AWCDirector::TickTV(float Dt)
{
	AWCCharacter* P = Player();
	AWCInteractable* Tv = Thing(TEXT("tv"));
	if (!P || !Tv) return;
	const FVector At = Tv->GetActorLocation() + FVector(0, 0, 55);
	if (TVPhase == 0)
	{
		if (Has(TEXT("dawn")) || Has(TEXT("sprint_started"))) return;
		// The set is off until he puts a tape in (it used to be playing when he came in, and came on by itself later).
		// (the set has its own tape slot under the screen: SM_Item_TV)
		Tv->Prompt = (HasItem(TEXT("tape1")) || HasItem(TEXT("tape2")) || HasItem(TEXT("tape3"))) ? TEXT("Put the tape in") : TEXT("Look at the television");
		return;
	}
	if (TVPhase == 1)
	{
		const float T = (float)(Clock - TVAt);
		if (TVScreen) TVScreen->SetScalarParameterValue(TEXT("Frame"), (float)(FMath::FloorToInt(T * GTapeFps) % GTapeFrames));
		if (TVGlow) TVGlow->SetIntensity(1500.f * (0.72f + 0.2f * FMath::Sin(T * 23.f) * FMath::Sin(T * 7.1f) + 0.08f * FMath::Sin(T * 61.f)));
		// the tape and its voices come round together, every twenty seconds
		const int32 LoopNow = FMath::FloorToInt(T / 20.f);
		if (LoopNow != TVLoop)
		{
			TVLoop = LoopNow;
			if (TVAudio.IsValid()) TVAudio->FadeOut(0.35f, 0.f);          // no hard cut when the tape comes round
			TVAudio = PlayAt(FString::Printf(TEXT("tv_tape_%d"), TVTapeNow), At, 0.42f, 1.f, 1000.f);       // heard in the room and from the hall, not through the house
			if (TVAudio.IsValid()) TVAudio->FadeIn(0.35f, 1.f);
		}
		// (every tape plays until he switches the set off)
		return;
	}
	// ---- the reflection
	const float T = (float)(Clock - TVAt);
	AWCEntity* H = Her();
	const FVector ToTv = (At - P->GetActorLocation()).GetSafeNormal2D();
	const bool bDbg = FParse::Param(FCommandLine::Get(), TEXT("WCTVDebug"));
	const bool bTurned = !bDbg && FVector::DotProduct(P->EyeForward().GetSafeNormal2D(), ToTv) < -0.05f;
	if (TVHerAt < 0.0 && T > 1.1f && H)
	{
		// in the doorway behind him, standing quite still: only the glass can see her
		const FVector Far = Pos(TEXT("Her_TVFar"));
		H->Appear(Far, (P->GetActorLocation() - Far).Rotation().Yaw, TEXT("Idle"));
		H->SetFarGlow(0.f);
		TInlineComponentArray<UPrimitiveComponent*> Prims(H);
		for (UPrimitiveComponent* C : Prims) { C->bVisibleInSceneCaptureOnly = !bDbg; C->MarkRenderStateDirty(); }
		TVHerLight = NewObject<UPointLightComponent>(H);
		TVHerLight->SetupAttachment(H->GetRootComponent());
		TVHerLight->RegisterComponent();
		TVHerLight->SetRelativeLocation(FVector(85.f, 0.f, 170.f));
		TVHerLight->SetIntensityUnits(ELightUnits::Lumens);
		TVHerLight->SetIntensity(1500.f);
		TVHerLight->SetAttenuationRadius(700.f);
		TVHerLight->SetLightColor(FLinearColor(0.8f, 0.86f, 1.f));
		TVHerLight->SetCastShadows(false);
		TVHerAt = Clock;
		Tension = 0.9f;
		UE_LOG(LogWCEvents, Display, TEXT("WCTV she stands at %s (shown %d, %d parts), her light at %s, he is at %s, the glass looks from %s toward %s"),
			*H->GetActorLocation().ToCompactString(), H->IsShown() ? 1 : 0, Prims.Num(), *TVHerLight->GetComponentLocation().ToCompactString(),
			*P->GetActorLocation().ToCompactString(), *TVCapture->GetComponentLocation().ToCompactString(), *TVCapture->GetComponentRotation().ToCompactString());
		PlayAt(TEXT("her_breath"), Far + FVector(0, 0, 200), 0.8f, 0.8f, 1600.f);
		if (bAuto && !AutoShotDir.IsEmpty())
		{
			const FString D0 = AutoShotDir;
			After(1.1f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_0_standing.png"), false, false); });
			After(0.8f, [this, D0]() { if (TVTarget) UKismetRenderingLibrary::ExportRenderTarget(this, TVTarget, D0, TEXT("S13_what_the_glass_sees_standing.png")); });
			
		}
	}
	// slowly: she only stands there.  Then all at once.
	if (TVHerAt > 0.0 && TVRunAt < 0.0 && Clock - TVHerAt > 1.7 && H)
	{
		TArray<FVector> Pts;
		Pts.Add(FVector(218.f, -335.f, H->GetActorLocation().Z));          // round the end of the sofa
		Pts.Add(P->GetActorLocation() - FVector(0, 0, 88.f));
		H->MoveAlong(Pts, 600.f, TEXT("Run"));
		H->SetScream(1.f);
		Play2D(TEXT("her_scream"), 1.f);
		Play2D(TEXT("sting_hit"), 0.9f, EWCSnd::Music);
		TVRunAt = Clock;
		Tension = 1.f;
		if (bAuto && !AutoShotDir.IsEmpty())
		{
			const FString D0 = AutoShotDir;
			After(0.22f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_1.png"), false, false); });
			After(0.42f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_2.png"), false, false); });
			After(0.32f, [this, D0]() { if (TVTarget) UKismetRenderingLibrary::ExportRenderTarget(this, TVTarget, D0, TEXT("S13_what_the_glass_sees_running.png")); });
		}
	}
	if (TVRunAt > 0.0)
	{
		P->AddShake(0.75f);
		const bool bReached = H && H->IsShown() && H->DistToPlayer() < 120.f;
		if (bTurned || bReached || Clock - TVRunAt > 1.5)
		{
			UE_LOG(LogWCEvents, Display, TEXT("WCTV the reflection ends %.2f s after she ran (turned %d, reached %d)"), (float)(Clock - TVRunAt), bTurned ? 1 : 0, bReached ? 1 : 0);
			TVReflectionEnd();
		}
	}
	else if (bTurned && T > 0.4f) TVReflectionEnd();            // he turned before she ran: the room is empty
}

// ================================================================================================ the eye in the dark (S14)
// Cheyenne: "all of a sudden all lights go out ... flashlight, lights in the house, everything, but then down the hall in the air
// close to the ceiling there's just her eye ... then your flashlight comes back on only and the player can shine it on her, she
// won't be there. Then when the player goes to move the light away from that spot the eye will reappear, then it will disappear
// in the dark" and "not crazy: very eerie and creepy sound design".
bool AWCDirector::EyeTry(bool bForce)
{
	AWCCharacter* P = Player();
	if (!P || !Her()) return false;
	// a long level look the way he is facing: a hall
	const FVector Eye = P->EyeLocation();
	const FVector Fwd = P->EyeForward().GetSafeNormal2D();
	FHitResult Hit;
	FCollisionQueryParams Q(FName(TEXT("WCEye")), false, P);
	const bool bHit = GetWorld()->LineTraceSingleByChannel(Hit, Eye, Eye + Fwd * 1500.f, ECC_Visibility, Q);
	const float Free = bHit ? Hit.Distance : 1500.f;
	if (Free < 720.f && !bForce) return false;
	EyeSpot = P->GetActorLocation() - FVector(0, 0, 88.f) + Fwd * FMath::Clamp(Free - 80.f, 300.f, 600.f);
	Set(TEXT("eye_done"));
	bEventBusy = true;
	bEyeLooked = false;
	EyePhase = 1;
	EyeAt = Clock;
	UE_LOG(LogWCEvents, Display, TEXT("WCSCARE t=%.1f S14_eye (%.0f cm of hall ahead)"), PlaySeconds, Free);
	// everything goes: the house and his own light.  No bang; the bulbs just stop.
	KillLights(45.f, false);
	P->SetLightScale(0.f);
	P->SetDarkAdapt(4.5f);                       // truly black: no moonlit doorway, no outline
	Play2D(TEXT("bulb_die"), 0.4f, EWCSnd::SFX, 0.8f);
	SetLoop(TEXT("amb"), TEXT("amb_house"), 0.03f, 1.2f);
	SetLoop(TEXT("music"), TEXT(""), 0.f, 1.2f);
	Tension = 0.55f;
	return true;
}

void AWCDirector::EyeEnd(bool bSeenTwice)
{
	if (AWCEntity* H = Her()) H->Vanish();
	if (AWCCharacter* P = Player()) { P->SetLightScale(1.f); P->SetDarkAdapt(0.f); }
	SetLoop(TEXT("eye"), TEXT(""), 0.f, 3.f);
	EyePhase = 0;
	bEventBusy = false;
	Rest(170.f);
	Tension = 0.6f;
	ApplyWorldState();
	UE_LOG(LogWCEvents, Display, TEXT("WCSCARE t=%.1f S14_eye over (seen twice %d)"), PlaySeconds, bSeenTwice ? 1 : 0);
	After(2.2f, [this]() { Think(TEXT("Up by the ceiling. It was up by the ceiling.")); });
}

void AWCDirector::TickEye(float Dt)
{
	AWCCharacter* P = Player();
	AWCEntity* H = Her();
	if (!P || !H) return;
	if (EyePhase == 0)
	{
		if (Has(TEXT("eye_done")) || !Has(TEXT("lockin_done")) || Has(TEXT("dawn")) || Has(TEXT("sprint_started")) || bBusy || P->IsDown()) return;
		if (EyeNextAt < 0.0) EyeNextAt = Clock + 260.0 * FMath::Max(TestPace, 0.25f);
		if (Clock < EyeNextAt || !Gate()) return;
		if (!EyeTry(false)) EyeNextAt = Clock + 3.0;                 // not a hall: look again in a moment
		return;
	}
	const float T = (float)(Clock - EyeAt);
	const FVector EyePoint = EyeSpot + FVector(0, 0, 252.f);                    // where her eye is, up by the ceiling
	const float Dot = FVector::DotProduct(P->EyeForward(), (EyePoint - P->EyeLocation()).GetSafeNormal());
	// Dark = the camera is stopped down 4.5 stops, so everything of hers has to be about 22 times brighter to show the same
	auto Show = [this, H, P](bool bDark)
	{
		H->Appear(EyeSpot, (P->GetActorLocation() - EyeSpot).Rotation().Yaw, TEXT("Tall"));
		H->SetFarGlow(0.f);
		H->SetGlow(bDark ? 55.f : 2.5f);
		H->SetEyeShine(bDark ? 2400.f : 150.f, 2.3f);
	};
	switch (EyePhase)
	{
	case 1:                     // black.  Nothing at all for a while.
		P->SetLightScale(0.f);
		if (T > 2.8f)
		{
			Show(true);
			SetLoop(TEXT("eye"), TEXT("music_low"), 0.16f, 4.f, EWCSnd::Music);
			PlayAt(TEXT("her_breath"), EyePoint, 0.45f, 0.75f, 3000.f);
			EyePhase = 2; EyeAt = Clock;
		}
		break;
	case 2:                     // only the eye
		P->SetLightScale(0.f);
		if (T > 2.2f && T - Dt <= 2.2f) PlayAt(TEXT("whisper_far"), EyePoint, 0.35f, 0.9f, 3000.f);
		if (T > 5.0f || FVector::Dist2D(P->GetActorLocation(), EyeSpot) < 380.f)
		{
			H->Vanish();                                           // gone in the same instant the light comes back
			P->SetDarkAdapt(0.f);
			P->SetLightScale(1.f);
			P->FlickerLight(0.6f, 0.8f);
			Play2D(TEXT("flashlight_click"), 0.5f);
			EyePhase = 3; EyeAt = Clock;
		}
		break;
	case 3:                     // his light is back, and the hall is empty
		if (Dot > 0.94f) bEyeLooked = true;
		if ((bEyeLooked && Dot < 0.80f && T > 1.5f) || (T > 10.f && Dot < 0.80f))
		{
			Show(false);                                           // the light is off that spot: it is there again
			PlayAt(TEXT("VO/m_whisper1"), EyePoint, 0.4f, 0.95f, 3000.f);
			EyePhase = 4; EyeAt = Clock;
		}
		else if (T > 18.f) EyeEnd(false);                          // he never looked away: let it go
		break;
	case 4:                     // at the edge of his sight
		if (Dot > 0.86f || T > 6.f) { EyePhase = 5; EyeAt = Clock; }
		break;
	case 5:                     // it goes out in the dark before the light can find it
		H->SetGlow(2.5f * FMath::Clamp(1.f - T / 0.3f, 0.f, 1.f));
		H->SetEyeShine(150.f * FMath::Clamp(1.f - T / 0.3f, 0.f, 1.f), 2.3f);
		if (T > 0.3f) EyeEnd(true);
		break;
	default: break;
	}
}

// ================================================================================================ the picture filter
// One layer over the finished picture, switched by a number.  It changes nothing in the game itself.
void AWCDirector::SetFilter(int32 Look)
{
	FilterLook = FMath::Clamp(Look, 0, 5);
	if (!FilterVolume)
	{
		UMaterialInterface* M = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Filter.M_Filter"));
		if (!M) { UE_LOG(LogWCEvents, Warning, TEXT("WCFILTER no M_Filter (import step items)")); return; }
		FilterVolume = GetWorld()->SpawnActor<APostProcessVolume>();
		if (!FilterVolume) return;
		FilterVolume->bUnbound = true;
		FilterVolume->Priority = 100.f;
		FilterMID = UMaterialInstanceDynamic::Create(M, this);
		FilterVolume->Settings.AddBlendable(FilterMID, 1.f);
	}
	FilterMID->SetScalarParameterValue(TEXT("Look"), (float)FilterLook);
	FilterVolume->bEnabled = FilterLook > 0;
	FilterVolume->BlendWeight = FilterLook > 0 ? 1.f : 0.f;
	UE_LOG(LogWCEvents, Display, TEXT("WCFILTER look %d"), FilterLook);
}

// ================================================================================================ a door opens by itself
// Cheyenne: "have one of the doors in the house open ... the creak of the door opening and actually having the door open ...
// in moderation, once, maybe twice in the whole game."
bool AWCDirector::DoorOpensByItself()
{
	AWCCharacter* P = Player();
	if (!P) return false;
	AWCDoor* Best = nullptr;
	float BestScore = -1.f;
	const FVector Eye = P->EyeLocation();
	for (TActorIterator<AWCDoor> It(GetWorld()); It; ++It)
	{
		AWCDoor* D = *It;
		if (D->bLocked || D->IsOpen() || D->WCId == TEXT("front") || D->WCId == TEXT("back") ||
			D->WCId == TEXT("up_kids") || D->WCId == TEXT("cellar") || D->WCId == TEXT("up_master")) continue;
		const FVector At = D->GetActorLocation() + D->GetActorForwardVector()*57.f + FVector(0, 0, 115);
		const float Dist = FVector::Dist(Eye, At);
		if (Dist < 125.f || Dist > 820.f || FMath::Abs(At.Z - Eye.Z) > 130.f) continue;
		FHitResult Hit;
		FCollisionQueryParams Q(FName(TEXT("WCDoorSelf")), false, P);
		Q.AddIgnoredActor(D);
		if (GetWorld()->LineTraceSingleByChannel(Hit, Eye, At, ECC_Visibility, Q)) continue;         // he has to be able to see it go
		const float Facing = FVector::DotProduct(P->EyeForward(), (At - Eye).GetSafeNormal());
		const float Score = Facing + 0.3f * (1.f - Dist / 950.f);
		if (Facing > .86f && Score > BestScore) { BestScore = Score; Best = D; }
	}
	if (!Best) return false;
	Best->SetOpen(true, 6.5f, true);                                          // slowly
	PlayAt(TEXT("door_creak_long"), Best->GetActorLocation() + FVector(0, 0, 110), 1.f, 0.9f, 2200.f);
	UE_LOG(LogWCEvents, Display, TEXT("WCDOOR t=%.1f %s opened by itself"), PlaySeconds, *Best->GetActorNameOrLabel());
	return true;
}

// ================================================================================================ sounds on triggers
// Cheyenne: "Everything else should be on a timed sequence where when the player passes this part, this sound goes off ...
// picks this up, this sound triggers ... returning to a room for the fifth time, this sound triggers."
// One line = one sound, once.  On: the event ("enter:<trigger>" = walking into a room, "take:<item>", "use:<thing>",
// "door:<door>").  Nth: on which time that happens.  Where: 0 somewhere round him, 1 on the other floor, 2 in a wall close by,
// 3 behind him.  Need: a story flag that has to be set first (nullptr = none).  Act: 1 the rocking chair rocks, 2 a light he
// left on goes out, 3 Walter's radio tunes itself, 4 bare feet run across the other floor, 5 something moves behind the kitchen
// vent, 6 a picture frame comes off the hall wall.
namespace
{
	struct FWCCue { const TCHAR* On; int32 Nth; const TCHAR* Sound; int32 Where; float Near, Far, Vol, Pitch; const TCHAR* Need; int32 Act; };
	const FWCCue GWCCues[] = {
		// ---- the house only: before the thump
		{ TEXT("enter:t_dining"), 1, TEXT("creak"), 0, 300.f, 600.f, 0.8f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_kitchen"), 1, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, nullptr, 5 },                    // something moves behind the wall vent
		{ TEXT("enter:t_hall_mid"), 2, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, TEXT("locked_in"), 6 },          // a picture comes off the wall behind him
		{ TEXT("enter:t_hall_mid"), 3, TEXT("steps_above"), 1, 100.f, 300.f, 0.9f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_dining"), 2, TEXT("thump_far"), 1, 200.f, 400.f, 0.9f, 0.95f, nullptr, 0 },
		{ TEXT("enter:t_living"), 2, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, nullptr, 1 },
		{ TEXT("enter:t_den"), 1, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, nullptr, 3 },
		{ TEXT("enter:t_sickroom"), 1, TEXT("VO/m_hum"), 1, 200.f, 500.f, 0.45f, 1.f, TEXT("locked_in"), 0 },
		{ TEXT("enter:t_up_landing"), 1, TEXT("house_groan"), 0, 500.f, 900.f, 0.9f, 1.f, nullptr, 0 },
		{ TEXT("take:screwdriver"), 1, TEXT("creak"), 3, 180.f, 260.f, 0.9f, 0.9f, nullptr, 0 },
		{ TEXT("enter:t_foyer"), 3, TEXT("door_far"), 1, 400.f, 700.f, 0.9f, 1.f, nullptr, 2 },
		{ TEXT("enter:t_kitchen"), 3, TEXT("scratch_wall"), 2, 150.f, 220.f, 0.9f, 1.f, nullptr, 0 },
		// ---- after the first sight of her
		{ TEXT("take:keep_eye"), 1, TEXT("VO/m_moan1"), 1, 500.f, 900.f, 0.75f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_up_corridor"), 3, TEXT("door_far"), 3, 500.f, 800.f, 0.8f, 1.f, TEXT("peek_done"), 0 },
		// ---- after the long hall
		{ TEXT("enter:t_hall_mid"), 5, TEXT("VO/m_cry1"), 1, 300.f, 700.f, 0.6f, 1.f, TEXT("lockin_done"), 0 },
		{ TEXT("enter:t_dining"), 3, TEXT("knock_far"), 0, 600.f, 1000.f, 0.9f, 1.f, TEXT("lockin_done"), 0 },
		{ TEXT("enter:t_master"), 3, TEXT("chair_creak"), 3, 200.f, 300.f, 0.8f, 1.f, TEXT("lockin_done"), 0 },
		{ TEXT("take:key_sitting"), 1, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, nullptr, 4 },
		{ TEXT("door:sitting"), 1, TEXT("VO/edith_snicker"), 2, 250.f, 400.f, 0.34f, 1.f, nullptr, 0 },
		{ TEXT("take:key_prayer"), 1, TEXT("thump_far"), 1, 200.f, 500.f, 0.9f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_living"), 4, TEXT("scratch_wall"), 2, 200.f, 320.f, 0.9f, 0.85f, TEXT("phone_done"), 0 },
		{ TEXT("enter:t_kitchen"), 5, TEXT("chair_scrape"), 3, 220.f, 320.f, 0.7f, 1.f, TEXT("phone_done"), 0 },
		{ TEXT("enter:t_sitting"), 2, TEXT("VO/m_hum"), 2, 300.f, 500.f, 0.45f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_up_landing"), 4, TEXT("VO/m_cry2"), 0, 500.f, 900.f, 0.55f, 1.f, TEXT("ceiling_done"), 0 },
		{ TEXT("enter:t_den"), 3, TEXT("knock_far"), 1, 300.f, 600.f, 0.9f, 1.f, nullptr, 0 },
		{ TEXT("take:key_ell"), 1, TEXT("VO/m_cry2"), 2, 300.f, 500.f, 0.55f, 1.f, nullptr, 0 },
		// ---- the back rooms upstairs, the attic, the cellar
		{ TEXT("door:up_ell"), 1, TEXT("house_groan"), 0, 500.f, 900.f, 0.9f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_aide"), 1, TEXT("VO/edith_snicker"), 1, 300.f, 600.f, 0.34f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_up_ell"), 3, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, nullptr, 4 },
		{ TEXT("enter:t_attic"), 1, TEXT("wind_gust"), 0, 600.f, 1000.f, 0.8f, 1.f, nullptr, 0 },
		{ TEXT("take:key_cellar"), 1, TEXT("VO/m_moan2"), 1, 400.f, 800.f, 0.75f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_foyer"), 6, TEXT("door_far"), 1, 500.f, 900.f, 0.9f, 0.9f, TEXT("attic_done"), 0 },
		{ TEXT("enter:t_backhall"), 3, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, TEXT("lockin_done"), 4 },
		{ TEXT("enter:t_pantry"), 2, TEXT("thump_far"), 1, 200.f, 500.f, 0.9f, 1.f, TEXT("lockin_done"), 0 },
		{ TEXT("enter:t_cellar_shelf"), 1, TEXT("scratch_wall"), 2, 150.f, 240.f, 0.9f, 0.9f, nullptr, 0 },
	};
}

void AWCDirector::CueEvent(FName Id)
{
	const FString S = Id.ToString();
	if (!(S.StartsWith(TEXT("enter:")) || S.StartsWith(TEXT("take:")) || S.StartsWith(TEXT("use:")) || S.StartsWith(TEXT("door:")))) return;
	CueCount.FindOrAdd(Id) += 1;
	AWCCharacter* P = Player();
	if (!P || SpaceAt(P->GetActorLocation()) == EListeningSpace::Exterior || !Has(TEXT("inside")) || Has(TEXT("dawn")) || Has(TEXT("placed"))) return;
	// nothing over a staged moment, a hunt, or another of these
	if (bBusy || bEventBusy || StalkState != 0 || Clock < CueFreeAt) return;
	const int32 Count = CueCount[Id];
	for (int32 i = 0; i < UE_ARRAY_COUNT(GWCCues); ++i)
	{
		const FWCCue& C = GWCCues[i];
		if (CueFired.Contains(i) || Id != FName(C.On) || Count < C.Nth) continue;
		if (C.Need && !Has(FName(C.Need))) continue;
		CueFired.Add(i);
		CueFreeAt = Clock + 22.0;
		const FVector L = P->GetActorLocation();
		const FRotator Yaw(0.f, P->GetControlRotation().Yaw, 0.f);
		FVector Off = FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * Rng.FRandRange(C.Near, C.Far);
		if (C.Where == 1) Off.Z = (L.Z > 500.f ? -1.f : 1.f) * 330.f;
		else if (C.Where == 2) Off.Z = Rng.FRandRange(-60.f, 120.f);
		else if (C.Where == 3) Off = -Yaw.Vector() * Rng.FRandRange(C.Near, C.Far) + FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y) * Rng.FRandRange(-90.f, 90.f) + FVector(0, 0, 20.f);
		else Off.Z = Rng.FRandRange(-80.f, 200.f);
		UE_LOG(LogWCEvents, Display, TEXT("WCCUE t=%.1f %s (%s, time %d) act %d"), PlaySeconds, C.Sound, C.On, Count, C.Act);
		// a moment after he has done the thing, not on top of it
		const FString Sound = C.Sound;
		const float Vol = C.Vol, Pitch = C.Pitch;
		const int32 Act = C.Act;
		After(Rng.FRandRange(0.9f, 2.2f), [this, Sound, Vol, Pitch, Act, L, Off]()
		{
			AWCCharacter* Pl = Player();
			if (!Pl || bBusy || SpaceAt(Pl->GetActorLocation()) == EListeningSpace::Exterior) return;
			if (!Sound.IsEmpty()) PlayAt(Sound, L + Off, Vol, Pitch * Rng.FRandRange(0.96f, 1.04f));
			if (Act == 1)
			{
				if (AActor* Chair = Find(TEXT("RockingChair")))
				{
					RockActor = Chair; RockUntil = Clock + 9.0; RockBase = Chair->GetActorRotation();
					PlayAt(TEXT("chair_creak"), Chair->GetActorLocation() + FVector(0, 0, 50), 1.f, 1.f, 2200.f);
					After(3.2f, [this, Chair]() { if (IsValid(Chair)) PlayAt(TEXT("chair_creak"), Chair->GetActorLocation() + FVector(0, 0, 50), 0.9f, 0.94f, 2200.f); });
				}
			}
			else if (Act == 2)
			{
				for (TPair<FName, FRoomLights>& Rm : Rooms) if (Rm.Value.bOn) { Rm.Value.KillAt = Clock; NextLightKill = 0.0; break; }
			}
			else if (Act == 3)
			{
				PlayAt(TEXT("radio_tune"), Pos(TEXT("RadioPoint")), 1.f, 1.f, 3200.f);
				After(8.f, [this]() { if (bBusy) return; Play2D(TEXT("breath_near"), 0.55f); if (AWCCharacter* Q = Player()) Q->FlickerLight(0.5f, 0.7f); });
			}
			else if (Act == 5)
			{
				const FVector Vp = Pos(TEXT("VentPoint"));
				After(1.5f, [this, Vp]() { PlayAt(TEXT("scratch_wall"), Vp, 0.8f, 1.1f, 1600.f); });
				After(2.3f, [this]() { if (!Has(TEXT("vent_seen")) && !bBusy) Feedback(TEXT("Something moved behind the wall vent.")); });
			}
			else if (Act == 6)
			{
				Set(TEXT("frame_fell"));
				ApplyWorldState();
				PlayAt(TEXT("frame_fall"), Pos(TEXT("FramePoint")), 1.f, 1.f, 5000.f);
				Play2D(TEXT("sting_hit"), 0.75f, EWCSnd::Music);
				Pl->AddShake(0.4f);
				Tension = FMath::Max(Tension, 0.6f);
				Rest(60.f);
				UE_LOG(LogWCEvents, Display, TEXT("WCSCARE t=%.1f frame off the wall"), PlaySeconds);
			}
			else if (Act == 4)
			{
				const FVector From = Pl->GetActorLocation() + FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * Rng.FRandRange(500.f, 900.f) + FVector(0, 0, (Pl->GetActorLocation().Z > 300.f ? -330.f : 330.f) - 80.f);
				const FVector Step = FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * 72.f;
				const int32 N = Rng.RandRange(4, 6);
				for (int32 k = 0; k < N; ++k) After(k * 0.42f, [this, From, Step, k]() { PlayAt(TEXT("her_step"), From + Step * k, 0.9f, Rng.FRandRange(0.9f, 1.05f), 3400.f); });
			}
		});
		return;                              // one at a time
	}
}

void AWCDirector::TickYardCrows()
{
	const AWCCharacter* P = Player();
	if (!P || YardCawsLeft == 0 || !Has(TEXT("briefed")) || Has(TEXT("inside")) || Has(TEXT("dawn")) ||
		IsInsideHouse(P->GetActorLocation()) || bEventBusy || IsBinTurnActive() || Clock < DialogueUntil) return;
	if (YardCawsLeft < 0) YardCawsLeft = Rng.RandRange(4, 8);
	if (NextYardCaw < 0.) NextYardCaw = Clock + Rng.FRandRange(5.f, 11.f);
	if (Clock < NextYardCaw) return;

	const FName Perches[] = {TEXT("CrowGate"), TEXT("CrowBranch")};
	const int32 First = Rng.RandRange(0, 1);
	NextYardCaw = Clock + 4.;
	for (int32 Offset = 0; Offset < 2; ++Offset)
	{
		const int32 Index = (First + Offset) % 2;
		const AActor* Perch = Find(Perches[Index]);
		if (!Perch) continue;
		FVector Center, Extent;
		Perch->GetActorBounds(false, Center, Extent);
		const FVector At = Center + FVector(0, 0, Extent.Z * .8f);
		if (FVector::DistSquared(At, P->GetActorLocation()) > FMath::Square(2200.f)) continue;
		const float Pitch = (Index == 0 ? .94f : 1.02f) * Rng.FRandRange(.975f, 1.025f);
		YardCrowVoice = PlayAt(TEXT("yard_caw"), At, .34f, Pitch);
		if (YardCrowVoice.IsValid())
		{
			--YardCawsLeft;
			NextYardCaw = Clock + Rng.FRandRange(13.f, 29.f);
			UE_LOG(LogWCEvents, Verbose, TEXT("WCCROW at=%.1f perch=%s remaining=%d next=%.1f"),Clock,*Perches[Index].ToString(),YardCawsLeft,NextYardCaw);
		}
		break;
	}
}

void AWCDirector::TickHallClock()
{
	const AWCCharacter* P = Player();
	const AActor* Cabinet = Find(TEXT("HallClockSource"));
	if (!P || !Cabinet) return;
	const FVector Mechanism = Cabinet->GetActorLocation() + FVector(0, 0, 125);
	const FVector Here = P->GetActorLocation();
	if (!IsInsideHouse(Here) || FMath::Abs(Here.Z - Mechanism.Z) > 180.f ||
		FVector::DistSquared(Here, Mechanism) > FMath::Square(650.f) || Has(TEXT("dawn")))
	{
		NextHallTick = -1.;
		ExtraHallTicks = 0;
		return;
	}
	if (NextHallTick < 0.) NextHallTick = Clock + Rng.FRandRange(3.f, 8.f);
	if (Clock < NextHallTick || bEventBusy || Clock < DialogueUntil || StalkState != 0 || ActiveNote.IsValid()) return;
	if (ExtraHallTicks == 0)
		ExtraHallTicks = Rng.RandRange(1, 3);
	PlayAt(TEXT("clock_single"), Mechanism, .62f, Rng.FRandRange(.97f, 1.03f));
	--ExtraHallTicks;
	NextHallTick = Clock + (ExtraHallTicks ? Rng.FRandRange(.84f, 1.16f) : Rng.FRandRange(27.f, 45.f));
	UE_LOG(LogWCEvents, Verbose, TEXT("WCCLOCK tick at %.1f, next %.1f"), Clock, NextHallTick);
}

void AWCDirector::TickCues(float Dt)
{
	AWCCharacter* P = Player();
	if (!P || !IsInsideHouse(P->GetActorLocation()) || !Has(TEXT("inside")) || Has(TEXT("dawn")) || Has(TEXT("placed")))
	{
		WhisperAt = -1.;
		return;
	}
	if (WhisperAt < 0.) WhisperAt = Clock + Rng.FRandRange(28.f, 64.f);
	if (Clock < WhisperAt || Clock < CueFreeAt || Clock < DialogueUntil || bBusy || bEventBusy ||
		StalkState != 0 || ActiveNote.IsValid() || Mode != EWCMode::Playing || (Has(TEXT("heard_upstairs")) && !Has(TEXT("peek_done")))) return;
	WhisperAt = Clock + Rng.FRandRange(43.f, 102.f);
	CueFreeAt = Clock + 14.;
	if (!Has(TEXT("heard_listening_snicker")) && !P->IsInputLocked() && !P->IsDown() &&
		(!Her() || !Her()->IsShown()) && TryListeningSnicker(P))
	{
		LastHaunt = 1; // Keep the ordinary laugh out of the next random slot.
		return;
	}
	constexpr int32 GroupCount = 9;
	const int32 Pick = LastHaunt < 0 ? Rng.RandHelper(GroupCount) : (LastHaunt + 1 + Rng.RandHelper(GroupCount - 1)) % GroupCount;
	LastHaunt = Pick;
	PlayHouseHaunt(Pick);
	UE_LOG(LogWCEvents, Display, TEXT("WCHAUNT one-shot group=%d next=%.1f"), Pick, WhisperAt - Clock);
}

bool AWCDirector::TryListeningSnicker(AWCCharacter* P)
{
	const FVector Eye = P->EyeLocation();
	const FRotator Yaw(0.f, P->GetControlRotation().Yaw, 0.f);
	const FVector Forward = Yaw.Vector();
	const FVector Side = FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y);
	const float FirstSide = Rng.RandBool() ? 1.f : -1.f;
	const FCollisionQueryParams Query(SCENE_QUERY_STAT(WCListeningSnicker), false, P);
	for (float Sign : {FirstSide, -FirstSide})
	{
		const FVector Direction = (-Forward + .52f * Sign * Side).GetSafeNormal();
		FHitResult Hit;
		const bool bHit = GetWorld()->LineTraceSingleByChannel(Hit, Eye, Eye + 135.f * Direction, ECC_Visibility, Query);
		const float Distance = bHit ? Hit.Distance - 10.f : 135.f;
		const FVector Source = Eye + Direction * Distance;
		if (Distance < 50.f || !IsInsideHouse(Source)) continue;

		ListeningSnicker = PlayAt(TEXT("VO/edith_listening_snicker_01"), Source, .34f, .96f);
		if (!ListeningSnicker.IsValid()) return false;
		ListeningStartForward = Forward;
		RememberAtCheckpoint(TEXT("heard_listening_snicker"));
		return true;
	}
	return false;
}

void AWCDirector::TickListeningSnicker()
{
	UAudioComponent* Voice = ListeningSnicker.Get();
	AWCCharacter* P = Player();
	if (!Voice || !Voice->IsPlaying() || !P)
	{
		ListeningSnicker.Reset();
		return;
	}

	const FVector Forward = FRotator(0.f, P->GetControlRotation().Yaw, 0.f).Vector();
	const FVector Toward = (Voice->GetComponentLocation() - P->EyeLocation()).GetSafeNormal2D();
	// Compare both headings against the same world-space source. Walking past the
	// sound or glancing a few degrees won't cut the laugh off.
	const bool bTurned = FVector::DotProduct(Forward, ListeningStartForward) < .77f &&
		FVector::DotProduct(Forward - ListeningStartForward, Toward) > .35f;
	const bool bInterrupted = bBusy || bEventBusy || StalkState != 0 || Clock < DialogueUntil ||
		P->IsInputLocked() || P->IsDown() || ActiveNote.IsValid() || !IsInsideHouse(P->GetActorLocation());
	if (bTurned || bInterrupted)
	{
		Voice->FadeOut(.045f, 0.f);
		ListeningSnicker.Reset();
	}
}

void AWCDirector::PlayHouseHaunt(int32 Pick)
{
	AWCCharacter* P = Player();
	if (!P) return;
	const FVector Eye = P->EyeLocation();
	const FRotator Yaw(0.f, P->GetControlRotation().Yaw, 0.f);
	const FVector Side = FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y) * (Rng.RandBool() ? 1.f : -1.f);
	FVector At = Eye - Yaw.Vector() * Rng.FRandRange(110.f, 210.f) + Side * 58.f;
	if (!IsInsideHouse(At)) At = Eye - Yaw.Vector() * 23.f;
	if (!IsInsideHouse(At)) At = Eye;
	const float Pitch = Rng.FRandRange(.93f, 1.04f);
	if (Pick == 0)
	{
		const FVector Ear = Eye - Yaw.Vector() * 24.f + Side * 19.f;
		PlayAt(FString::Printf(TEXT("VO/m_ear%d"),Rng.RandRange(1,3)), IsInsideHouse(Ear) ? Ear : Eye, .77f, Pitch);
	}
	else if (Pick == 1) PlayAt(TEXT("VO/edith_snicker"), At, .34f, Pitch);
	else if (Pick == 7) PlayAt(TEXT("VO/edith_whimper"), At, .64f, Pitch);
	else if (Pick == 8) PlayAt(TEXT("VO/edith_groan"), At, .66f, Pitch);
	else if (Pick < 4)
	{
		const TCHAR* Voice[] = {TEXT("cry"),TEXT("moan")};
		PlayAt(FString::Printf(TEXT("VO/m_%s%d"), Voice[Pick - 2], Rng.RandRange(1,2)), At, .74f, Pitch);
	}
	else if (Pick == 4) PlayAt(TEXT("whisper_far"), At, .86f, Pitch);
	else
	{
		const bool Upstairs = Pick == 5 && Eye.Z < 340.f;
		At.Z = Upstairs ? (Eye.Z < 0 ? 8.f : 358.f) : P->GetActorLocation().Z - 80.f;
		const int32 Count = Rng.RandRange(2,4);
		float Delay = 0.f;
		for (int32 i=0; i<Count; ++i)
		{
			const FVector Foot = At + Side * (37.f * i);
			if (IsInsideHouse(Foot)) After(Delay, [this, Foot, Pitch]()
			{
				if (Player() && IsInsideHouse(Player()->GetActorLocation()) && !bBusy && !bEventBusy && Clock >= DialogueUntil)
					PlayAt(TEXT("her_step"), Foot, .91f, Pitch);
			});
			Delay += Rng.FRandRange(.38f,.72f);
		}
	}
}
