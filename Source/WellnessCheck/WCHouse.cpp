// The house itself as a character: its lights (which work though the power was cut a year ago, and which she turns
// off), the slow build-up before she is ever seen, the drive up the forest road, the fetch errands, and her stalking
// you between the scripted scares (where your pistol finally matters: enough shots drive her off, they never kill her).
#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"

#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/AudioComponent.h"
#include "Components/LightComponent.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Engine/PostProcessVolume.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"

DEFINE_LOG_CATEGORY_STATIC(LogWCHouse, Log, All);

// ================================================================================================ set-up
void AWCDirector::HouseBegin()
{
	Rooms.Reset();
	for (TActorIterator<AActor> It(GetWorld()); It; ++It)
	{
		if (!It->ActorHasTag(TEXT("RoomLight"))) continue;
		FName Room;
		for (const FName& T : It->Tags) { const FString S = T.ToString(); if (S.StartsWith(TEXT("Room_"))) Room = FName(*S.Mid(5)); }
		if (Room.IsNone()) continue;
		FRoomLights& R = Rooms.FindOrAdd(Room);
		TArray<ULightComponent*> Ls;
		It->GetComponents(Ls);
		for (ULightComponent* L : Ls)
		{
			R.Lights.Add(L);
			R.Base.Add(L->Intensity);
			L->SetIntensity(0.f);
			L->SetVisibility(false);
		}
		R.Seed = Rng.FRandRange(0.f, 100.f);
	}
	for (TPair<FName, FRoomLights>& P : Rooms)
	{
		if (AWCInteractable* Sw = Thing(FName(*FString::Printf(TEXT("sw_%s"), *P.Key.ToString())))) P.Value.SwitchLoc = Sw->GetActorLocation();
	}
	ShowTagged(TEXT("BulbOn"), false);
	for (const TCHAR* M : { TEXT("Mem1"), TEXT("Mem2"), TEXT("Mem3") }) ShowTagged(M, false);
	NavPts.Reset();
	for (TActorIterator<AActor> It(GetWorld()); It; ++It) if (It->ActorHasTag(TEXT("NavNode"))) NavPts.Add(It->GetActorLocation());
	for (TActorIterator<AActor> It(GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(TEXT("Cruiser"))) { Car = *It; CarHome = It->GetActorLocation(); CarHomeRot = It->GetActorRotation(); }
		if (It->ActorHasTag(TEXT("DriverSeat"))) Seat = *It;
	}
	bPowerOut = Has(TEXT("power_out")) && !Has(TEXT("fuse_done"));
	NextStalkAt = Clock + 120.0;
	UE_LOG(LogWCHouse, Display, TEXT("WCHOUSE %d lit rooms, %d nav points, car %d"), Rooms.Num(), NavPts.Num(), Car.IsValid() ? 1 : 0);
}

// ================================================================================================ lights
void AWCDirector::SwitchRoom(FName Room, bool bOn, bool bClick)
{
	FRoomLights* R = Rooms.Find(Room);
	if (!R) return;
	if (bClick) PlayAt(TEXT("switch_click"), R->SwitchLoc, 0.9f, Rng.FRandRange(0.95f, 1.05f), 900.f);
	R->bOn = bOn;
	if (bOn)
	{
		R->FlickUntil = Clock + Rng.FRandRange(0.35, 0.9);
		// she lets it burn a while, less and less as the night goes on
		const float Patience = FMath::Lerp(95.f, 28.f, FMath::Clamp(Tension * 1.3f, 0.f, 1.f));
		R->KillAt = Clock + Rng.FRandRange(Patience * 0.6f, Patience * 1.5f);
	}
	else
	{
		for (int32 i = 0; i < R->Lights.Num(); ++i) if (ULightComponent* L = R->Lights[i].Get()) { L->SetIntensity(0.f); L->SetVisibility(false); }
	}
	ShowTagged(FName(*FString::Printf(TEXT("BulbOn_%s"), *Room.ToString())), bOn);
}

void AWCDirector::KillLights(float DeadSeconds, bool bPop)
{
	bool bAny = false;
	for (TPair<FName, FRoomLights>& P : Rooms)
	{
		if (P.Value.bOn) { bAny = true; SwitchRoom(P.Key, false, false); }
		P.Value.DeadUntil = FMath::Max(P.Value.DeadUntil, Clock + DeadSeconds);
	}
	if (bAny && bPop) Play2D(TEXT("bulb_pop"), 0.8f);
}

static bool AnyRoomOn(const TMap<FName, AWCDirector::FRoomLights>& Rooms)
{
	for (const TPair<FName, AWCDirector::FRoomLights>& P : Rooms) if (P.Value.bOn) return true;
	return false;
}

void AWCDirector::TickHouseLights(float Dt)
{
	const float T = (float)Clock;
	const bool bMayKill = Has(TEXT("inside")) && !Has(TEXT("dawn")) && !bBusy && StalkState == 0 && (PlaySeconds - InsideAt) > 170.f * TestPace;
	for (TPair<FName, FRoomLights>& P : Rooms)
	{
		FRoomLights& R = P.Value;
		if (!R.bOn) continue;
		float N = 0.84f + 0.08f * FMath::Sin(T * 7.3f + R.Seed) + 0.05f * FMath::Sin(T * 19.1f + R.Seed * 2.f);
		if (FMath::Sin(T * 0.41f + R.Seed) > 0.975f) N *= 0.3f + 0.3f * FMath::Abs(FMath::Sin(T * 31.f));           // a sag, now and then
		if (Clock < R.FlickUntil) N *= (FMath::Sin(T * 61.f + R.Seed) > 0.1f) ? 1.f : 0.12f;                        // catching as it comes on
		N *= 1.f - 0.3f * Tension * FMath::Max(0.f, FMath::Sin(T * 2.3f + R.Seed));                                   // the house browns out when she is near
		for (int32 i = 0; i < R.Lights.Num(); ++i)
		{
			if (ULightComponent* L = R.Lights[i].Get()) { L->SetVisibility(true); L->SetIntensity(R.Base[i] * N); }
		}
		if (bMayKill && Clock > R.KillAt && Clock > NextLightKill)
		{
			// she turns it off
			NextLightKill = Clock + 12.0;
			SwitchRoom(P.Key, false, true);
			PlayAt(TEXT("bulb_buzz"), R.SwitchLoc + FVector(0, 0, 120), 0.6f, 1.f, 900.f);
			R.DeadUntil = Clock + Rng.FRandRange(5.f, 12.f);
			++R.Kills;
			Tension = FMath::Min(1.f, Tension + 0.08f);
			if (!Has(TEXT("light_killed"))) { Set(TEXT("light_killed")); After(1.6f, [this]() { Think(TEXT("I didn't touch that.")); }); }
			UE_LOG(LogWCHouse, Display, TEXT("WCLIGHT t=%.1f she turned off %s"), PlaySeconds, *P.Key.ToString());
		}
	}
}

// ================================================================================================ events
bool AWCDirector::HouseEvent(FName Id)
{
	AWCCharacter* P = Player();
	if (!P) return false;
	const FString S = Id.ToString();

	if (S.StartsWith(TEXT("use:sw_")))
	{
		const FName Room(*S.Mid(7));
		FRoomLights* R = Rooms.Find(Room);
		const FVector At = Thing(FName(*S.Mid(4))) ? Thing(FName(*S.Mid(4)))->GetActorLocation() : P->GetActorLocation();
		if (!R || R->Lights.Num() == 0)
		{
			PlayAt(TEXT("switch_click"), At, 0.9f, 1.f, 900.f);
			Think(Room == TEXT("dining") ? TEXT("Nothing. The chandelier is on the floor.") : (Room == TEXT("prayer") ? TEXT("Nothing. Somebody took the bulb out.") : TEXT("Nothing.")));
			return true;
		}
		if (bPowerOut)
		{
			PlayAt(TEXT("switch_click"), At, 0.9f, 1.f, 900.f);
			Think(Has(TEXT("seen_fusebox")) ? TEXT("Dead. It needs that fuse.") : TEXT("Dead. The whole house is dead. There'll be a fuse box somewhere off the kitchen."));
			return true;
		}
		if (Clock < R->DeadUntil && !R->bOn)
		{
			PlayAt(TEXT("switch_click"), At, 0.9f, 1.f, 900.f);
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Think(TEXT("It won't come on.")); }
			return true;
		}
		SwitchRoom(Room, !R->bOn);
		if (R->bOn && !Has(TEXT("lights_tried")))
		{
			Set(TEXT("lights_tried"));
			After(1.4f, [this]() { Think(TEXT("Power's on. Barely.")); });
		}
		return true;
	}
	if (S.StartsWith(TEXT("look:"))) { LooksSeen.Add(Id); return true; }
	if (S.StartsWith(TEXT("take:ammo")))
	{
		P->Reserve += 8;
		ShowToast(TEXT("Taken: box of cartridges (+8)"));
		return true;
	}
	if (Id == TEXT("closed:note_mail") && Has(TEXT("lights_tried")) && !Has(TEXT("power_puzzled")))
	{
		Set(TEXT("power_puzzled"));
		Think(TEXT("Cut off last September. ...Then what's running the lights?"));
		return true;
	}
	if (Id == TEXT("closed:note_prayer") && !HasItem(TEXT("shears")))
	{
		After(0.8f, [this]() { Think(TEXT("A living hand, and something to cut with. She said scissors.")); });
		return false;     // the story also listens for this
	}
	if (Id == TEXT("invuse:radio"))
	{
		Play2D(TEXT("radio_static"), 0.6f);
		Think(Has(TEXT("locked_in")) ? TEXT("Static. Nothing gets out of this house.") : TEXT("Dispatch reads me fine out here."));
		return true;
	}
	if (Id == TEXT("invuse:keep_ruth"))
	{
		// it still plays; and somewhere in the house something hums along
		TWeakObjectPtr<UAudioComponent> Box = Play2D(TEXT("musicbox"), 0.55f);
		After(6.5f, [Box]() { if (Box.IsValid()) Box->FadeOut(1.5f, 0.f); });
		Think(TEXT("It still plays."));
		if (Has(TEXT("locked_in")) && !bBusy)
		{
			After(4.6f, [this]()
			{
				AWCCharacter* Pl = Player();
				if (!Pl || bBusy) return;
				PlayAt(TEXT("VO/m_hum"), Pl->GetActorLocation() + FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * 650.f, 0.6f, 1.f, 2600.f);
				Tension = FMath::Min(1.f, Tension + 0.2f);
			});
		}
		return true;
	}
	if (Id == TEXT("use:fusebox"))
	{
		Set(TEXT("seen_fusebox"));
		if (Has(TEXT("fuse_done")) || !bPowerOut) { Think(TEXT("Glass fuses. One is newer than the rest.")); return true; }
		if (!HasItem(TEXT("fuse"))) { Think(TEXT("One fuse is blown black. I need a spare.")); return true; }
		Set(TEXT("fuse_done"));
		bPowerOut = false;
		Items.Remove(TEXT("fuse"));
		PlayAt(TEXT("switch_click"), Pos(TEXT("FusePoint")), 1.f, 0.8f);
		PlayAt(TEXT("bulb_buzz"), Pos(TEXT("FusePoint")), 0.8f);
		After(0.7f, [this]() { SwitchRoom(TEXT("pantry"), true, false); Think(TEXT("That's got it.")); });
		return true;
	}
	if (Id == TEXT("use:desk"))
	{
		if (Has(TEXT("desk_open"))) return true;
		if (!HasItem(TEXT("key_desk")))
		{
			PlayAt(TEXT("door_locked"), P->GetActorLocation() + P->GetActorForwardVector() * 80.f, 0.6f);
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Think(TEXT("The roll-top is locked. A small brass lock.")); }
			return true;
		}
		Set(TEXT("desk_open"));
		Play2D(TEXT("door_unlock"), 0.8f);
		if (AWCInteractable* Desk = Thing(TEXT("desk"))) Desk->bEnabled = false;
		After(0.9f, [this]()
		{
			GiveItem(TEXT("key_ell"), TEXT("Walter's keys"));
			if (AWCCharacter* Pl = Player()) Pl->Reserve += 8;
			Think(TEXT("Walter's key ring. Upstairs, the back rooms. And a box of his cartridges."));
			if (!Has(TEXT("placed"))) SetObjective(TEXT("Upstairs: the locked back rooms"));
			Checkpoint(TEXT("desk"));
		});
		return true;
	}
	if (Id == TEXT("take:key_desk")) { Think(TEXT("The key was in the book. Walter's desk.")); return true; }
	if (Id == TEXT("use:book_settlers"))
	{
		if (Has(TEXT("book_done"))) return true;
		if (!NotesRead.Contains(TEXT("note_deskkey")))
		{
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Think(TEXT("County histories. One spine is cleaner than the rest: 'Customs of the First Settlers'.")); }
			return true;
		}
		ScareBook();
		return true;
	}
	if (S.StartsWith(TEXT("company:")))
	{
		Tension = FMath::Min(1.f, Tension + 0.25f);
		if (!Has(TEXT("company_seen"))) { Set(TEXT("company_seen")); After(1.6f, [this]() { Think(TEXT("That wasn't her. That was taller.")); }); }
		return true;
	}
	if (S.StartsWith(TEXT("watcher:")))
	{
		// nothing happens.  That is the point.  (The house just breathes a little closer.)
		Tension = FMath::Min(1.f, Tension + 0.12f);
		if (!Has(TEXT("watcher_seen"))) { Set(TEXT("watcher_seen")); After(1.8f, [this]() { Think(TEXT("...Was that")); }); }
		return true;
	}
	if (Id == TEXT("take:fuse")) { if (!bPowerOut) Think(TEXT("A spare fuse. Might want that.")); return true; }
	if (Id == TEXT("take:key_attic"))
	{
		SetObjective(TEXT("The attic"));
		// his radio comes on by itself, and something answers to his name
		After(1.6f, [this]()
		{
			PlayAt(TEXT("radio_tune"), Pos(TEXT("DanielRadioPoint")), 1.f);
			if (AWCCharacter* Pl = Player()) Pl->FlickerLight(1.4f, 0.7f);
			Tension = FMath::Max(Tension, 0.6f);
		});
		Say(TEXT("m_whisper2"), 5.5f);
		return true;
	}
	if (Id == TEXT("take:shears")) { ShowTagged(TEXT("Hide_shears"), false); ScareSewing(); return true; }
	if (Id == TEXT("shot") && StalkState >= 1 && StalkState <= 2)
	{
		AWCEntity* H = Her();
		if (H && H->IsShown() && PlayerSees(H->HeadLocation() - FVector(0, 0, 60), 0.94f, 3200.f)) StalkShot();
		return true;
	}
	return false;
}

// ================================================================================================ the build-up: nothing to see for a long time
void AWCDirector::TickBuildUp(float Dt)
{
	AWCCharacter* P = Player();
	if (!P || !Has(TEXT("inside")) || Has(TEXT("peek_started")) || bBusy) return;
	const float T = (PlaySeconds - InsideAt) / FMath::Max(TestPace, 0.01f);
	const FVector L = P->GetActorLocation();
	auto Above = [&L](float Dx, float Dy) { return L + FVector(Dx, Dy, 300.f); };
	switch (BuildStep)
	{
	case 0:
		if (T > 26.f || L.X > 700.f)
		{
			// the front door shuts behind him
			++BuildStep;
			Set(TEXT("locked_in"));
			if (AWCDoor* D = Door(TEXT("front"))) { D->Slam(); D->SetLocked(true); }
			P->AddShake(0.3f);
			Tension = FMath::Max(Tension, 0.3f);
			After(2.2f, [this]() { if (!Has(TEXT("door_stuck"))) Think(TEXT("...The front door.")); });
		}
		break;
	case 1: if (T > 85.f) { ++BuildStep; PlayAt(TEXT("thump_far"), Above(260.f, -180.f), 1.f, 0.95f, 2600.f); } break;
	case 2: if (T > 150.f) { ++BuildStep; PlayAt(TEXT("steps_above"), Above(-120.f, 60.f), 1.f, 1.f, 2600.f); After(4.f, [this]() { Think(TEXT("Somebody's up there.")); }); } break;
	case 3:
		if (T > 215.f)
		{
			++BuildStep;
			if (AActor* Chair = Find(TEXT("RockingChair"))) { RockActor = Chair; RockUntil = Clock + 9.0; RockBase = Chair->GetActorRotation(); PlayAt(TEXT("chair_creak"), Chair->GetActorLocation() + FVector(0, 0, 50), 1.f, 1.f, 2200.f); After(3.2f, [this, Chair]() { if (IsValid(Chair)) PlayAt(TEXT("chair_creak"), Chair->GetActorLocation() + FVector(0, 0, 50), 0.9f, 0.94f, 2200.f); }); }
		}
		break;
	case 4:
		if (T > 280.f)
		{
			++BuildStep;
			if (AnyRoomOn(Rooms)) { for (TPair<FName, FRoomLights>& R : Rooms) if (R.Value.bOn) { R.Value.KillAt = Clock; break; } NextLightKill = 0.0; }
			else PlayAt(TEXT("door_far_03"), Above(600.f, 0.f), 1.f, 1.f, 3200.f);
		}
		break;
	case 5:
		if (T > 345.f)
		{
			++BuildStep;
			const FVector Side = FRotator(0.f, P->GetControlRotation().Yaw + 90.f, 0.f).Vector();
			PlayAt(TEXT("scratch_wall"), L + Side * 170.f + FVector(0, 0, 30), 1.f, 1.f, 1200.f);
			After(2.6f, [this, L, Side]() { PlayAt(TEXT("skitter"), L + Side * 260.f + FVector(120, 0, 60), 1.f, 1.f, 1200.f); });
		}
		break;
	case 6:
		if (T > 400.f)
		{
			++BuildStep;
			PlayAt(TEXT("radio_tune"), Pos(TEXT("RadioPoint")), 1.f, 1.f, 3200.f);
			After(8.f, [this]() { Play2D(TEXT("breath_near"), 0.55f); if (AWCCharacter* Pl = Player()) Pl->FlickerLight(0.5f, 0.7f); });
		}
		break;
	default: break;
	}
	if (!Has(TEXT("heard_upstairs")) && T > 640.f && L.Z > 300.f && L.Z < 650.f)
	{
		Set(TEXT("heard_upstairs"));
		UpstairsAt = Clock;
		PlayAt(TEXT("thump_heavy"), Pos(TEXT("Snd_UpstairsThump")), 1.f);
		P->AddShake(0.25f);
		After(1.6f, [this]() { PlayAt(TEXT("drag_floor"), Pos(TEXT("Snd_UpstairsThump")), 1.f); });
		SetObjective(TEXT("Find her upstairs"));
		Tension = 0.35f;
	}
	// the rocking chair
	if (RockActor.IsValid() && Clock < RockUntil)
	{
		const float A = FMath::Sin((float)(RockUntil - Clock) * 3.4f) * 7.f * FMath::Min(1.f, (float)(RockUntil - Clock) / 3.f);
		RockActor->SetActorRotation(RockBase + FRotator(A, 0.f, 0.f));
		if (PlayerSees(RockActor->GetActorLocation() + FVector(0, 0, 60), 0.9f, 900.f) && RockUntil - Clock > 1.2) RockUntil = Clock + 1.2;   // it stops when you look
	}
}

// ================================================================================================ the drive up the forest road
static FVector PathPoint(const TArray<FVector>& Pts, const TArray<float>& Len, float D)
{
	if (Pts.Num() == 0) return FVector::ZeroVector;
	D = FMath::Clamp(D, 0.f, Len.Last());
	int32 i = 0;
	while (i < Len.Num() - 2 && Len[i + 1] < D) ++i;
	const float Seg = FMath::Max(Len[i + 1] - Len[i], 1.f);
	return FMath::Lerp(Pts[i], Pts[i + 1], (D - Len[i]) / Seg);
}

void AWCDirector::BeginDrive()
{
	DrivePts.Reset(); DriveLen.Reset();
	TArray<TPair<FString, FVector>> Raw;
	for (TActorIterator<AActor> It(GetWorld()); It; ++It)
	{
		if (!It->ActorHasTag(TEXT("DrivePath"))) continue;
		for (const FName& T : It->Tags) { const FString S = T.ToString(); if (S.StartsWith(TEXT("Drive_"))) Raw.Add(TPair<FString, FVector>(S, It->GetActorLocation())); }
	}
	Raw.Sort([](const TPair<FString, FVector>& A, const TPair<FString, FVector>& B) { return A.Key < B.Key; });
	AWCCharacter* P = Player();
	APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
	if (Raw.Num() < 4 || !Car.IsValid() || !Seat.IsValid() || !P || !PC) { UE_LOG(LogWCHouse, Warning, TEXT("WCDRIVE unavailable (%d points)"), Raw.Num()); return; }
	float Acc = 0.f;
	for (int32 i = 0; i < Raw.Num(); ++i)
	{
		if (i > 0) Acc += FVector::Dist2D(Raw[i].Value, Raw[i - 1].Value);
		DrivePts.Add(Raw[i].Value); DriveLen.Add(Acc);
	}
	DriveTotal = Acc;
	DriveDist = 0.f;
	DriveSpeed = 800.f;
	bDriving = true;
	P->SetInputLocked(true);
	P->SetFlashlight(false, false);
	P->SetActorHiddenInGame(true);
	FActorSpawnParameters SP;
	ACameraActor* Cam = GetWorld()->SpawnActor<ACameraActor>(Seat->GetActorLocation(), FRotator::ZeroRotator, SP);
	if (Cam)
	{
		Cam->GetCameraComponent()->SetFieldOfView(Settings.FOV - 8.f);
		Cam->GetCameraComponent()->bConstrainAspectRatio = false;
		DriveCam = Cam;
		PC->SetViewTargetWithBlend(Cam, 0.f);
	}
	DriveHeading = (PathPoint(DrivePts, DriveLen, 400.f) - PathPoint(DrivePts, DriveLen, 0.f)).Rotation().Yaw;
	PC->SetControlRotation(FRotator(0.f, DriveHeading, 0.f));
	ShowTagged(TEXT("CarRunning"), true);
	SetLoop(TEXT("car"), TEXT("amb_car"), 0.9f, 1.5f);
	SetLoop(TEXT("amb"), TEXT("amb_night"), 0.25f, 1.f);
		TickDrive(0.f);
	After(5.f, [this]() { if (bDriving) ShowHint(TEXT("Mouse: look around        Space: skip the drive"), 6.f); });
	UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE begin: %.0f m of road"), DriveTotal / 100.f);
}

void AWCDirector::TickDrive(float Dt)
{
	if (!bDriving || !Car.IsValid()) return;
	APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
		if (PC && PC->WasInputKeyJustPressed(EKeys::SpaceBar) && DriveDist > 200.f && DriveTotal - DriveDist > 3200.f)
	{
		// skipped: drop the rest of the radio traffic and roll up to the gate
		Steps.Reset();
		Subtitles.Reset();
		BigTarget = 0.f;
		HintUntil = 0.0;
		FadeTo(0.f, 1.f);
		DriveDist = DriveTotal - 3000.f;
	}
	const float Left = DriveTotal - DriveDist;
	const float Want = Left < 2600.f ? FMath::Max(55.f, 800.f * FMath::Sqrt(FMath::Max(Left, 0.f) / 2600.f)) : 800.f;
	DriveSpeed = FMath::FInterpTo(DriveSpeed, Want, Dt, 2.5f);
	DriveDist = FMath::Min(DriveTotal, DriveDist + DriveSpeed * Dt);
	if (bAuto && !AutoShotDir.IsEmpty())
	{
		static int32 DriveShotN = -1;
		const int32 ShotN = (int32)(DriveDist / 3500.f);
		if (ShotN != DriveShotN) { DriveShotN = ShotN; FScreenshotRequest::RequestScreenshot(AutoShotDir / FString::Printf(TEXT("drive_%02d.png"), ShotN), false, false); }
	}
	const FVector Pos0 = PathPoint(DrivePts, DriveLen, DriveDist);
	const FVector Ahead = PathPoint(DrivePts, DriveLen, DriveDist + 420.f), Behind = PathPoint(DrivePts, DriveLen, DriveDist - 220.f);
	float Heading = (Ahead - Behind).IsNearlyZero(1.f) ? DriveHeading : (Ahead - Behind).Rotation().Yaw;
	if (Left < 300.f) Heading = FMath::FixedTurn(DriveHeading, 0.f, 40.f * Dt);            // square up as it parks
	const float T = (float)Clock;
	const float Rough = FMath::Clamp(DriveSpeed / 800.f, 0.f, 1.f);
	const float Bump = (FMath::Sin(T * 8.7f) * 0.9f + FMath::Sin(T * 13.9f + 1.f) * 0.5f + FMath::Sin(T * 3.1f) * 1.4f) * Rough;
	const float Roll = (FMath::Sin(T * 2.3f) * 0.7f + FMath::Sin(T * 6.1f) * 0.3f) * Rough;
	// keep where the driver is looking, relative to the car, as the car turns
	FRotator Rel = PC ? (PC->GetControlRotation() - FRotator(0.f, DriveHeading, 0.f)).GetNormalized() : FRotator::ZeroRotator;
	Rel.Yaw = FMath::Clamp(Rel.Yaw, -80.f, 80.f);
	Rel.Pitch = FMath::Clamp(Rel.Pitch, -30.f, 28.f);
	DriveHeading = Heading;
	Car->SetActorLocationAndRotation(FVector(Pos0.X, Pos0.Y, CarHome.Z + Bump * 0.5f), FRotator(0.f, Heading + CarHomeRot.Yaw, Roll * 0.6f));
	if (PC) PC->SetControlRotation(FRotator(Rel.Pitch, Heading + Rel.Yaw, 0.f));
	if (DriveCam.IsValid() && Seat.IsValid())
	{
		DriveCam->SetActorLocationAndRotation(Seat->GetActorLocation() + FVector(0, 0, Bump * 0.8f), FRotator(Rel.Pitch + Bump * 0.12f, Heading + Rel.Yaw, Roll));
	}
	if (FLoop* Eng = Loops.Find(TEXT("car"))) Eng->Target = 0.55f + 0.4f * Rough;
	if (Left < 4.f && DriveSpeed < 70.f) EndDrive();
}

void AWCDirector::EndDrive()
{
	if (!bDriving) return;
	bDriving = false;
	Set(TEXT("arrived"));
	if (FParse::Param(FCommandLine::Get(), TEXT("WCDriveOnly")))
	{
		const FString Dir0 = AutoShotDir;
		After(5.f, [Dir0]() { if (!Dir0.IsEmpty()) FScreenshotRequest::RequestScreenshot(Dir0 / TEXT("drive_parked.png"), false, false); });
		After(7.f, [this]() { UKismetSystemLibrary::QuitGame(this, UGameplayStatics::GetPlayerController(this, 0), EQuitPreference::Quit, false); });
	}
	if (Car.IsValid()) Car->SetActorLocationAndRotation(CarHome, CarHomeRot);
	Play2D(TEXT("car_stop"), 0.6f);
	SetLoop(TEXT("car"), TEXT(""), 0.f, 1.8f);
	UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE arrived t=%.1f"), PlaySeconds);
	// engine off, a breath, then out of the car
	After(2.6f, [this]() { ShowTagged(TEXT("CarRunning"), false); FadeTo(1.f, 0.7f); });
	After(3.6f, [this]()
	{
		Play2D(TEXT("car_door"), 0.9f);
		APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
		if (AWCCharacter* P = Player())
		{
			P->SetActorHiddenInGame(false);
			if (PC) { PC->SetViewTargetWithBlend(P, 0.f); PC->SetControlRotation(FRotator(0.f, 8.f, 0.f)); }
		}
		if (DriveCam.IsValid()) DriveCam->Destroy();
		SetLoop(TEXT("amb"), TEXT("amb_night"), 1.f, 2.f);
	});
	After(5.2f, [this]()
	{
		FadeTo(0.f, 2.2f);
		if (AWCCharacter* P = Player()) P->SetInputLocked(false);
		ShowHint(TEXT("WASD move    Mouse look    F flashlight    E use / examine    Shift hurry    C crouch"), 10.f);
		DriveDone();
	});
}

// ================================================================================================ she comes looking for you
void AWCDirector::TickStalk(float Dt)
{
	AWCCharacter* P = Player();
	AWCEntity* H = Her();
	if (!P || !H) return;
	const FVector L = P->GetActorLocation();

	if (StalkState == 0)
	{
		const bool bMay = Has(TEXT("lockin_done")) && !Has(TEXT("sprint_started")) && !Has(TEXT("dawn")) && !bBusy && !H->IsShown() && !ActiveNote.IsValid()
			&& !Has(TEXT("phone_ringing")) && Clock >= NextScareAt && Clock >= NextStalkAt && StalksDone < 6 && L.Z > -60.f && L.Z < 560.f && !P->IsDown();
		if (!bMay) return;
		// somewhere on this floor, not too near, where he is not looking
		FVector Best = FVector::ZeroVector; float BestScore = -1.f;
		for (const FVector& N : NavPts)
		{
			if (FMath::Abs(N.Z - (L.Z - 88.f)) > 130.f) continue;
			const float D = FVector::Dist2D(N, L);
			const bool bAmbushPick = StalksDone == 0;
			if (D < (bAmbushPick ? 520.f : 1500.f) || D > (bAmbushPick ? 1300.f : 2700.f) || N.X < 60.f) continue;        // never out in the yard
			if (PlayerSees(N + FVector(0, 0, 150), 0.35f, 4000.f)) continue;
			const float Score = D + Rng.FRandRange(0.f, 500.f);
			if (Score > BestScore) { BestScore = Score; Best = N; }
		}
		if (BestScore < 0.f) { NextStalkAt = Clock + 12.0; return; }
		StalkState = 1;
		StalkAt = Clock;
		StalkHits = 0;
		bAmbush = StalksDone == 0;                 // the first time after the long hall there is nothing he can do
		StalkNeed = bAmbush ? 99 : 3 + (Rng.FRand() < 0.45f ? 1 : 0);
		StalkLostAt = 0.0;
		KillLights(40.f, true);
		H->Appear(Best, (L - Best).Rotation().Yaw, TEXT("Idle"));
		H->FacePlayer(true);
		H->SetGlow(1.2f);
		Play2D(TEXT("sting_braam"), 0.7f, EWCSnd::Music);
		SetLoop(TEXT("music"), TEXT("music_stalk"), 0.75f, 2.5f, EWCSnd::Music);
		PlayAt(TEXT("creak"), Best, 1.f, 0.8f, 2600.f);
		P->FlickerLight(1.1f, 0.7f);
		Tension = FMath::Max(Tension, 0.85f);
		if (bAmbush)
		{
			// round the corner at a dead run
			StalkState = 2;
			StalkRepath = 0.0;
			Play2D(TEXT("her_scream_short"), 1.f);
			Play2D(TEXT("sting_rise"), 0.9f, EWCSnd::Music);
		}
		else if (!Has(TEXT("stalk_hint"))) { Set(TEXT("stalk_hint")); ShowHint(TEXT("Right Mouse: raise your pistol.  She cannot be killed, but enough shots drive her off."), 9.f); }
		UE_LOG(LogWCHouse, Display, TEXT("WCSTALK t=%.1f begin #%d at %s (needs %d)"), PlaySeconds, StalksDone + 1, *Best.ToString(), StalkNeed);
		return;
	}
	if (!H->IsShown()) { StalkState = 0; return; }
	const float Dist = H->DistToPlayer();
	const double In = Clock - StalkAt;
	if (StalkState == 1 && In > 1.1) { StalkState = 2; StalkRepath = 0.0; Play2D(TEXT("her_scream_short"), 0.9f); }
	if (StalkState == 2)
	{
		if (Clock > StalkRepath && Clock > StalkPauseUntil)
		{
			StalkRepath = Clock + 0.8;
			TArray<FVector> Route;
			AutoRoute(H->GetActorLocation() + FVector(0, 0, 88), L - FVector(0, 0, 88), Route);
			for (FVector& V : Route) V.Z = FMath::RoundToFloat(V.Z / 350.f) * 350.f;
			const bool bClose = Dist < 420.f;
			// she comes fast: quicker than he can run, and faster again for the last few steps
			if (bAmbush || bClose) H->MoveAlong(Route, bAmbush ? 1350.f : 1150.f, TEXT("Run"));
			else H->MoveAlong(Route, 165.f, TEXT("Walk"));          // as fast as her walk plays without her feet sliding; he hears every step
			if (bClose && !Has(TEXT("stalk_rushing"))) { Set(TEXT("stalk_rushing")); Play2D(TEXT("her_scream"), 0.9f); }
		}
		if (Dist < 165.f)
		{
			// she has you
			Flags.Remove(TEXT("stalk_rushing"));
			StalkState = 0;
			++StalksDone;
			if (!bAmbush) ++Catches;
			bBusy = true;
			SetLoop(TEXT("music"), TEXT(""), 0.f, 1.5f, EWCSnd::Music);
			UE_LOG(LogWCHouse, Display, TEXT("WCSTALK t=%.1f caught (%d)"), PlaySeconds, Catches);
			Grab(1.35f, [this]()
			{
				if (AWCCharacter* Pl = Player()) Pl->Knockdown(Catches >= 3 ? 9.f : 3.4f);
				FadeTo(1.f, 0.3f);
				After(0.7f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); });
				if (Catches >= 3)
				{
					After(1.6f, [this]() { BigText = TEXT("You stayed."); BigSub = TEXT(""); BigTarget = 1.f; });
					After(6.0f, [this]() { RestartFromCheckpoint(); });
				}
				else
				{
					After(3.2f, [this]() { FadeTo(0.f, 1.8f); Think(Catches <= 1 ? TEXT("She had me. She let go.") : TEXT("Not again. Next time she keeps me.")); });
				}
			});
			Rest(170.f);
			NextStalkAt = Clock + Rng.FRandRange(210.f, 320.f) * FMath::Max(TestPace, 0.3f);
			return;
		}
		// she gives up if he gets right away from her
		const bool bFar = Dist > 2700.f || FMath::Abs(H->GetActorLocation().Z - (L.Z - 88.f)) > 200.f;
		if (bFar) { if (StalkLostAt <= 0.0) StalkLostAt = Clock; } else StalkLostAt = 0.0;
		if ((StalkLostAt > 0.0 && Clock - StalkLostAt > 14.0) || In > 80.0) EndStalk(false);
	}
}

void AWCDirector::StalkShot()
{
	AWCEntity* H = Her();
	AWCCharacter* P = Player();
	if (!H || !P) return;
	++StalkHits;
	UE_LOG(LogWCHouse, Display, TEXT("WCSTALK t=%.1f shot %d/%d"), PlaySeconds, StalkHits, StalkNeed);
	if (StalkHits >= StalkNeed) { EndStalk(true); return; }
	// she flinches: stops, is thrown back a step, and comes on again
	H->StopMoving();
	PlayAt(TEXT("her_flinch"), H->HeadLocation(), 1.f, Rng.FRandRange(0.92f, 1.08f), 3000.f);
	const FVector Away = (H->GetActorLocation() - P->GetActorLocation()).GetSafeNormal2D();
	H->Slide(H->GetActorLocation() + Away * (bAmbush ? 30.f : 150.f), 0.16f);
	H->Play(TEXT("Idle"));
	P->FlickerLight(0.25f, 0.8f);
	StalkPauseUntil = Clock + (bAmbush ? 0.2 : 0.85);
	if (StalkState == 1) StalkAt = Clock - 1.4;
}

void AWCDirector::EndStalk(bool bDriven)
{
	AWCEntity* H = Her();
	Flags.Remove(TEXT("stalk_rushing"));
	StalkState = 0;
	++StalksDone;
	SetLoop(TEXT("music"), TEXT(""), 0.f, 3.f, EWCSnd::Music);
	if (H && H->IsShown())
	{
		if (bDriven)
		{
			AWCCharacter* P = Player();
			H->StopMoving();
			Play2D(TEXT("her_hurt"), 1.f);
			Play2D(TEXT("sting_swell"), 0.6f, EWCSnd::Music);
			const FVector Away = P ? (H->GetActorLocation() - P->GetActorLocation()).GetSafeNormal2D() : FVector::ForwardVector;
			if (P) { P->FlickerLight(0.9f, 0.9f); P->AddShake(0.4f); }
			H->Slide(H->GetActorLocation() + Away * 320.f, 0.45f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); });
			if (!Has(TEXT("stalk_learned"))) { Set(TEXT("stalk_learned")); After(2.4f, [this]() { Think(TEXT("It doesn't hurt her. But she can't stand it. The noise, the flash. It buys time.")); }); }
		}
		else H->Vanish();
	}
	Rest(bDriven ? 150.f : 90.f);
	NextStalkAt = Clock + Rng.FRandRange(200.f, 330.f) * FMath::Max(TestPace, 0.3f);
	Tension = 0.5f;
	UE_LOG(LogWCHouse, Display, TEXT("WCSTALK t=%.1f end driven=%d"), PlaySeconds, bDriven ? 1 : 0);
}

// ================================================================================================ per-frame
void AWCDirector::HouseTick(float Dt)
{
	if (bDriving) { TickDrive(Dt); return; }
	if (Clock < LookAtUntil)
	{
		if (AWCCharacter* Pl = Player())
		{
			if (AController* Ct = Pl->GetController())
			{
				const FRotator Want = (LookAtPoint - Pl->EyeLocation()).Rotation();
				Ct->SetControlRotation(FMath::RInterpTo(Ct->GetControlRotation(), FRotator(Want.Pitch, Want.Yaw, 0.f), Dt, 3.2f));
			}
		}
	}
	if (Clock < GrabHoldUntil && Her() && Her()->IsShown())
	{
		if (AWCCharacter* Pl = Player())
		{
			if (AController* Ct = Pl->GetController())
			{
				const FRotator Want = (Her()->HeadLocation() - FVector(0, 0, 14.f) - Pl->EyeLocation()).Rotation();
				Ct->SetControlRotation(FMath::RInterpTo(Ct->GetControlRotation(), FRotator(Want.Pitch, Want.Yaw, 0.f), Dt, 14.f));
			}
		}
	}
	TickHouseLights(Dt);
	TickBuildUp(Dt);
	TickStalk(Dt);
}

// ================================================================================================ S9: the sewing room
void AWCDirector::ScareSewing()
{
	if (Has(TEXT("sewing_done"))) return;
	Set(TEXT("sewing_done"));
	UE_LOG(LogWCHouse, Display, TEXT("WCSCARE t=%.1f S9_sewing"), PlaySeconds);
	AWCEntity* H = Her();
	AWCCharacter* P = Player();
	if (!H || !P) return;
	bBusy = true;
	KillLights(30.f, true);
	P->FlickerLight(0.8f, 0.9f);
	After(0.8f, [this]() { if (AWCCharacter* Pl = Player()) Pl->SetLightScale(0.f); Play2D(TEXT("bulb_die"), 0.7f); });
	After(2.4f, [this]()
	{
		AWCEntity* E = Her();
		AWCCharacter* Pl = Player();
		if (!E || !Pl) return;
		// she is in the rocking chair, rocking
		E->Appear(Pos(TEXT("Her_Sewing")), YawOf(TEXT("Her_Sewing")), TEXT("Sit"));
		E->SetGlow(1.4f);
		PlayAt(TEXT("chair_creak"), E->GetActorLocation() + FVector(0, 0, 60), 1.f);
		Pl->SetLightScale(0.55f);
		Pl->FlickerLight(0.5f, 0.7f);
		Play2D(TEXT("sting_low"), 0.8f, EWCSnd::Music);
		Tension = 0.9f;
	});
	After(4.0f, [this]() { if (AWCEntity* E = Her()) PlayAt(TEXT("chair_creak"), E->GetActorLocation() + FVector(0, 0, 60), 1.f, 0.92f); });
	After(5.6f, [this]() { Say(TEXT("m_fin2")); });
	After(7.4f, [this]()
	{
		AWCEntity* E = Her();
		AWCCharacter* Pl = Player();
		if (!E || !Pl) return;
		E->Play(TEXT("Rise"), false, 1.6f);
		E->FacePlayer(true);
		Play2D(TEXT("her_scream_short"), 1.f);
		Play2D(TEXT("sting_hit"), 0.9f, EWCSnd::Music);
		Pl->AddShake(0.8f);
		Pl->FlickerLight(0.8f, 0.95f);
	});
	After(8.3f, [this]() { if (AWCCharacter* Pl = Player()) Pl->SetLightScale(0.f); });
	After(9.2f, [this]()
	{
		if (AWCEntity* E = Her()) E->Vanish();
		if (AWCCharacter* Pl = Player()) { Pl->SetLightScale(1.f); Pl->FlickerLight(0.6f, 0.8f); }
		if (AWCDoor* D = Door(TEXT("up_sewing"))) D->Slam();
		bBusy = false;
		Rest(140.f);
		Tension = 0.55f;
		Checkpoint(TEXT("sewing"));
	});
}

// ================================================================================================ S10: the book
void AWCDirector::ScareBook()
{
	Set(TEXT("book_done"));
	UE_LOG(LogWCHouse, Display, TEXT("WCSCARE t=%.1f S10_book"), PlaySeconds);
	AWCCharacter* P = Player();
	AActor* Book = Find(TEXT("SettlersBook"));
	AWCWatcher* EyeW = nullptr;
	for (TActorIterator<AWCWatcher> It(GetWorld()); It; ++It) if (It->WCId == TEXT("book_eye")) EyeW = *It;
	if (AWCInteractable* U = Thing(TEXT("book_settlers"))) U->bEnabled = false;
	if (!P || !Book) { GiveItem(TEXT("key_desk"), TEXT("Small desk key")); return; }
	bBusy = true;
	P->SetInputLocked(true);
	Play2D(TEXT("paper"), 0.8f, EWCSnd::SFX, 0.7f);
	const FVector From = Book->GetActorLocation();
	const FVector Out = (P->GetActorLocation() - From).GetSafeNormal2D();
	// he draws the book out...
	for (int32 i = 1; i <= 14; ++i) After(i * 0.035f, [Book, From, Out, i]() { if (IsValid(Book)) Book->SetActorLocation(From + Out * (26.f * i / 14.f)); });
	if (EyeW) EyeW->Reveal();
	// ...and she is looking at him through the wall
	After(0.95f, [this, EyeW, Book, From, Out]()
	{
		AWCCharacter* Pl = Player();
		Play2D(TEXT("sting_hit"), 0.9f, EWCSnd::Music);
		Play2D(TEXT("breath_near"), 0.9f);
		if (Pl) { Pl->AddShake(0.9f); Pl->SetLightScale(1.f); }
		Tension = 1.f;
		// the book goes out of his hand
		const FVector Start = From + Out * 26.f;
		const float FloorZ = FMath::FloorToFloat((From.Z + 20.f) / 350.f) * 350.f + 3.f;
		for (int32 i = 1; i <= 16; ++i)
		{
			After(i * 0.03f, [Book, Start, Out, FloorZ, i]()
			{
				if (!IsValid(Book)) return;
				const float U = i / 16.f;
				Book->SetActorLocation(FVector(Start.X + Out.X * 22.f * U, Start.Y + Out.Y * 22.f * U, FMath::Lerp(Start.Z, FloorZ, U * U)));
				Book->SetActorRotation(FRotator(70.f * U, Book->GetActorRotation().Yaw + 9.f, 80.f * U));
			});
		}
		After(0.5f, [this, Start, Out, FloorZ]()
		{
			PlayAt(TEXT("thump_far"), FVector(Start.X, Start.Y, FloorZ), 1.f, 1.5f, 900.f);
			ShowTagged(TEXT("Show_bookkey"), true);
		});
		// she is away along the inside of the wall
		After(0.55f, [this, EyeW]()
		{
			if (EyeW)
			{
				const FVector At = EyeW->GetActorLocation();
				const FVector Along = EyeW->GetActorRightVector();
				EyeW->Withdraw(true);
				for (int32 k = 0; k < 6; ++k) After(k * 0.28f, [this, At, Along, k]() { PlayAt(k % 2 ? TEXT("skitter") : TEXT("scratch_wall"), At + Along * (120.f * k) + FVector(0, 0, 30.f * k), 1.f, 1.1f, 1600.f); });
			}
		});
	});
	After(2.9f, [this]()
	{
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		bBusy = false;
		Rest(120.f);
		Tension = 0.6f;
		Think(TEXT("She's in the walls."));
		Checkpoint(TEXT("book"));
	});
}

// ================================================================================================ the grab
static float GrabSink = 30.f;       // how far she stoops to him (cm); -WCGrabSink=<n> to try others
static float GrabDist = 150.f;      // how far her feet are from his; -WCGrabDist=<n>

void AWCDirector::Grab(float Hold, TFunction<void()> Then)
{
	FParse::Value(FCommandLine::Get(), TEXT("WCGrabSink="), GrabSink);
	FParse::Value(FCommandLine::Get(), TEXT("WCGrabDist="), GrabDist);
	AWCEntity* H = Her();
	AWCCharacter* P = Player();
	if (!H || !P) { if (Then) Then(); return; }
	bBusy = true;
	H->StopMoving();
	// right in front of him, whatever angle she arrived from
	const FVector Fwd = FRotator(0.f, P->GetControlRotation().Yaw, 0.f).Vector();
	const FVector Feet = P->GetActorLocation() - FVector(0, 0, 88.f);
	const FVector To = (H->GetActorLocation() - Feet).GetSafeNormal2D();
	const FVector Dir = (FVector::DotProduct(To, Fwd) > 0.2f ? To : Fwd);
	H->SetActorLocation(Feet + Dir * GrabDist - FVector(0, 0, GrabSink));
	H->SetYaw((-Dir).Rotation().Yaw);
	H->FacePlayer(true);
	H->Play(TEXT("Lunge"), false);
	H->SetScream(1.f);
	H->SetGlow(2.2f);
	Play2D(TEXT("her_scream"), 1.f);
	Play2D(TEXT("sting_hit"), 1.f, EWCSnd::Music);
	P->AddShake(1.f);
	P->SetLightScale(1.f);
	P->FlickerLight(Hold, 0.45f);
	P->SetFaceLight(120.f);
	P->SetInputLocked(true);
	GrabHoldUntil = Clock + Hold;
	if (bAuto && !AutoShotDir.IsEmpty())
	{
		static int32 GrabShots = 0;
		const FString File = AutoShotDir / FString::Printf(TEXT("grab_%02d.png"), ++GrabShots);
		After(FMath::Min(0.85f, Hold * 0.7f), [File]() { FScreenshotRequest::RequestScreenshot(File, false, false); });
	}
	After(Hold, [this, Then]()
	{
		// the first three times she has him, he sees what made her
		const int32 N = !Has(TEXT("mem1")) ? 1 : (!Has(TEXT("mem2")) ? 2 : (!Has(TEXT("mem3")) ? 3 : 0));
		if (AWCCharacter* Pl0 = Player()) Pl0->SetFaceLight(0.f);
		if (N > 0 && !Has(TEXT("placed")) && Find(FName(*FString::Printf(TEXT("Cam_Mem%d"), N)))) { PlayMemory(N, Then); return; }
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		if (Then) Then();
	});
}

// ================================================================================================ her memories
void AWCDirector::PlayMemory(int32 N, TFunction<void()> Then)
{
	const FName Group(*FString::Printf(TEXT("Mem%d"), N));
	Set(FName(*FString::Printf(TEXT("mem%d"), N)));
	UE_LOG(LogWCHouse, Display, TEXT("WCMEMORY t=%.1f %d"), PlaySeconds, N);
	bBusy = true;
	if (AWCCharacter* P = Player()) P->SetInputLocked(true);
	FadeTo(1.f, 0.22f);
	auto Grade = [this](bool bOn)
	{
		for (TActorIterator<APostProcessVolume> It(GetWorld()); It; ++It) if (It->ActorHasTag(TEXT("PP_Memory"))) It->bEnabled = bOn;
	};
	After(0.4f, [this, N, Group, Grade]()
	{
		if (AWCEntity* E = Her()) E->Vanish();
		ShowTagged(Group, true);
		Grade(true);
		if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
		{
			if (AActor* Cam = Find(FName(*FString::Printf(TEXT("Cam_Mem%d"), N)))) PC->SetViewTargetWithBlend(Cam, 0.f);
		}
		SetLoop(TEXT("mem"), TEXT("musicbox"), 0.5f, 1.2f);
		SetLoop(TEXT("amb"), TEXT(""), 0.f, 0.4f);
		FadeTo(0.f, 1.6f);
		static const TCHAR* Caption[] = { TEXT("The last Thanksgiving anyone came."), TEXT("The attic. Her grandmother's book, under Danny's things."), TEXT("The ninth. She asked. Something answered.") };
		Think(Caption[FMath::Clamp(N - 1, 0, 2)], 7.f);
		Say(FName(*FString::Printf(TEXT("m_mem%d"), N)), 1.8f);
	});
	if (bAuto && !AutoShotDir.IsEmpty())
	{
		const FString File = AutoShotDir / FString::Printf(TEXT("memory_%d.png"), N);
		After(4.4f, [File]() { FScreenshotRequest::RequestScreenshot(File, false, false); });
	}
	After(8.2f, [this]() { FadeTo(1.f, 0.6f); });
	After(9.0f, [this, Group, Grade, Then]()
	{
		ShowTagged(Group, false);
		Grade(false);
		AWCCharacter* P = Player();
		if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0)) { if (P) PC->SetViewTargetWithBlend(P, 0.f); }
		SetLoop(TEXT("mem"), TEXT(""), 0.f, 0.2f);
		Subtitles.Reset();
		ApplyWorldState();
		Play2D(TEXT("her_scream_short"), 1.f);
		if (P) P->SetInputLocked(false);
		if (Then) Then();
	});
}
