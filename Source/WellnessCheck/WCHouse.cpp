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
#include "Components/PointLightComponent.h"
#include "Components/SpotLightComponent.h"
#include "Materials/MaterialInterface.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/SkeletalMeshActor.h"
#include "Engine/SkeletalMesh.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "HAL/FileManager.h"
#include "Engine/PostProcessVolume.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Engine/StaticMeshActor.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Engine/Light.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Components/LightComponent.h"
#include "Components/SkyLightComponent.h"
#include "EngineUtils.h"

DEFINE_LOG_CATEGORY_STATIC(LogWCHouse, Log, All);

// ================================================================================================ set-up
void AWCDirector::HouseBegin()
{
	// The authored foliage uses frozen skeletal meshes. Past the headlight and fog
	// range the ferns disappear first, while the taller canopy keeps its silhouette.
	int32 TreeCount = 0, FernCount = 0;
	for (TActorIterator<ASkeletalMeshActor> It(GetWorld()); It; ++It)
	{
		USkeletalMeshComponent* Plant = It->GetSkeletalMeshComponent();
		USkeletalMesh* Mesh = Plant->GetSkeletalMeshAsset();
		if (!Mesh) continue;
		const FString Package = Mesh->GetOutermost()->GetName();
		if (!Package.StartsWith(TEXT("/Game/Megaplant_Library/"))) continue;
		const bool bFern = Package.StartsWith(TEXT("/Game/Megaplant_Library/Plant_Bracken_Fern/"));
		if (bFern) ++FernCount; else ++TreeCount;
		Plant->SetCullDistance(bFern ? 5200.f : 10000.f);
		Plant->ShadowCacheInvalidationBehavior = EShadowCacheInvalidationBehavior::Rigid;
		Plant->MarkRenderStateDirty();
	}
	UE_LOG(LogWCHouse, Display, TEXT("WCFOREST visibility configured for %d trees and %d ferns"), TreeCount, FernCount);
	ShowTagged(TEXT("CabinOnly"), false);
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
	BathChair = Find(TEXT("BathWheelchair"));
	if (BathChair.IsValid()) BathChairHome = BathChair->GetActorTransform();
	if (AActor* Fixture = Find(TEXT("HallPendant"))) HallPendant = Fixture->FindComponentByClass<UStaticMeshComponent>();
	if (AActor* Beam = Find(TEXT("HallPendantBeam")))
	{
		PendantBeam = Beam->FindComponentByClass<USpotLightComponent>();
		if (PendantBeam.IsValid()) PendantBeam->SetRelativeRotation(FRotator(-68.f,90.f,0.f));
	}
	if (HallPendant.IsValid())
	{
		PendantBulbSlot = HallPendant->GetMaterialIndex(TEXT("M_GlowBulb"));
		if (PendantBulbSlot != INDEX_NONE) PendantLit = HallPendant->GetMaterial(PendantBulbSlot);
		PendantDark = LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WC/Materials/M_BulbOff.M_BulbOff"));
	}
	if (!bPowerOut && !Has(TEXT("pendant_off"))) SwitchRoom(TEXT("pendant"), true, false);
	NextStalkAt = Clock + 300.0 / 1.15;
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
		const float Patience = FMath::Lerp(58.f, 18.f, FMath::Clamp(Tension * 1.3f, 0.f, 1.f));          // lights go out often, for no reason
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

void AWCDirector::SetReturnBlackout(bool bActive)
{
	if (bActive)
	{
		for (FName Room : {FName(TEXT("uphall")), FName(TEXT("uprear")), FName(TEXT("master"))})
			SwitchRoom(Room, false, false);
		if (AWCDoor* Master = Door(TEXT("up_master"))) Master->SetOpen(true, .2f, true);
	}
	SetLightsTagged(TEXT("W_U_master"), bActive ? 4.f : 1.f);
	SetLightsTagged(TEXT("W_U_hall"), bActive ? 3.f : 1.f);
	if (bActive && !PeekMoonKey)
	{
		const FVector Doorway = Pos(TEXT("Her_Peek"));
		const FVector Source = Doorway + FVector(160,-60,230);
		const FVector Chest = Doorway + FVector(0,0,150);
		PeekMoonKey = NewObject<USpotLightComponent>(this);
		PeekMoonKey->SetWorldLocationAndRotation(Source,(Chest-Source).Rotation());
		PeekMoonKey->SetIntensityUnits(ELightUnits::Lumens);
		PeekMoonKey->SetIntensity(3584.f);
		PeekMoonKey->SetLightColor(FLinearColor(.33f,.54f,1.f));
		PeekMoonKey->SetInnerConeAngle(19.f);
		PeekMoonKey->SetOuterConeAngle(34.f);
		PeekMoonKey->SetAttenuationRadius(385.f);
		PeekMoonKey->SetSourceRadius(12.f);
		PeekMoonKey->SetLightingChannels(false,true,false);
		PeekMoonKey->RegisterComponent();
	}
	if (PeekMoonKey) PeekMoonKey->SetVisibility(bActive);
	SetLightsTagged(TEXT("W_U_living"), bActive ? 0.f : 1.f);
}

static bool AnyRoomOn(const TMap<FName, AWCDirector::FRoomLights>& Rooms)
{
	for (const TPair<FName, AWCDirector::FRoomLights>& P : Rooms) if (P.Value.bOn) return true;
	return false;
}

void AWCDirector::TickHouseLights(float Dt)
{
	const float T = (float)Clock;
	const bool bMayKill = Has(TEXT("inside")) && !Has(TEXT("dawn")) && !bBusy && StalkState == 0 && (PlaySeconds - InsideAt) > 35.f && Player() && IsInsideHouse(Player()->GetActorLocation());
	FName NextRoom;
	float Best = -1.f;
	for (const auto& Pair : Rooms)
	{
		const FRoomLights& Room = Pair.Value;
		if (Pair.Key == TEXT("pendant") && !Has(TEXT("pendant_seen"))) continue;
		if (!bMayKill || Clock < NextLightKill || !Room.bOn || Clock < Room.KillAt) continue;
		const float Weight = Rng.FRandRange(.5f, 1.5f) / (1.f + Room.Kills);
		if (Weight > Best) { Best = Weight; NextRoom = Pair.Key; }
	}
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
		if (P.Key == NextRoom)
		{
			// she turns it off: a staged thing, minutes apart, not a tic
			NextLightKill = Clock + Rng.FRandRange(31.f, 75.f);
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
	if (EventsEvent(Id) || FurnitureEvent(Id)) return true;
	const FString S = Id.ToString();

	if (S.StartsWith(TEXT("use:sw_")))
	{
		const FName Room(*S.Mid(7));
		FRoomLights* R = Rooms.Find(Room);
		const FVector At = Thing(FName(*S.Mid(4))) ? Thing(FName(*S.Mid(4)))->GetActorLocation() : P->GetActorLocation();
		if (!R || R->Lights.Num() == 0)
		{
			PlayAt(TEXT("switch_click"), At, 0.9f, 1.f, 900.f);
			Feedback(TEXT("Nothing."));
			return true;
		}
		const bool bReturnBlackout = Has(TEXT("heard_upstairs")) && !Has(TEXT("peek_done")) &&
			(Room == TEXT("uphall") || Room == TEXT("uprear") || Room == TEXT("master"));
		if (bPowerOut || bReturnBlackout)
		{
			PlayAt(TEXT("switch_click"), At, 0.9f, 1.f, 900.f);
			Feedback(TEXT("Dead."));
			return true;
		}
		if (Clock < R->DeadUntil && !R->bOn)
		{
			PlayAt(TEXT("switch_click"), At, 0.9f, 1.f, 900.f);
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Feedback(TEXT("Dead.")); }
			return true;
		}
		SwitchRoom(Room, !R->bOn);
		if (Room == TEXT("pendant"))
		{
			if (R->bOn) Flags.Remove(TEXT("pendant_off"));
			else Set(TEXT("pendant_off"));
		}
		if (R->bOn && !Has(TEXT("lights_tried")))
		{
			Set(TEXT("lights_tried"));
			After(1.4f, [this]() { Think(TEXT("Power's on. Barely.")); });
		}
		return true;
	}
	if (S.StartsWith(TEXT("look:"))) { LooksSeen.Add(Id); return true; }
	if (Id == TEXT("take:key_ell"))
	{
		if (!Has(TEXT("placed"))) SetObjective(TEXT("Unlock the rear upstairs hall. Check the aide's room for her videotape."));
		Checkpoint(TEXT("desk"));
		return true;
	}
	if (S.StartsWith(TEXT("take:ammo")))
	{
		if (Id == TEXT("take:ammo_desk")) Set(TEXT("desk_ammo"));
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
		if (Has(TEXT("fuse_done")) || !bPowerOut) { Feedback(TEXT("Glass fuses. One is newer than the rest.")); return true; }
		if (!HasItem(TEXT("fuse"))) { Feedback(TEXT("A fuse is blown.")); return true; }
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
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Feedback(TEXT("Locked. A tag under the handle reads: W. Harrow. Desk key in First Settlers, living-room shelf by the stairs."));
				SetObjective(TEXT("Find the settlers' book on the living-room shelf beside the stairs")); }
			return true;
		}
		Set(TEXT("desk_open"));
		Play2D(TEXT("door_unlock"), 0.8f);
		if (AWCInteractable* Desk = Thing(TEXT("desk"))) Desk->bEnabled = false;
		// the roll-top is open: his key ring and a box of cartridges are lying in it, for him to take
		After(0.5f, [this]() { ApplyWorldState(); });
		return true;
	}
	if (Id == TEXT("take:key_desk")) { SetObjective(TEXT("Use the book's small key on Walter's desk in the downstairs den")); Checkpoint(TEXT("desk_key")); return true; }
	if (Id == TEXT("use:book_settlers"))
	{
		if (Has(TEXT("book_done")) || bBusy) return true;
		// he has to be standing square in front of it, and close, for what is behind it to be seen at all
		if (AWCInteractable* Bk = Thing(TEXT("book_settlers")))
		{
			const FVector Rel = P->GetActorLocation() - Bk->GetActorLocation();
			const float Back = -Rel.Y, Aside = FMath::Abs(Rel.X);                 // the bookcase is on the hall-side wall: the room is toward -Y
			if (Aside > 74.f || Back < 12.f || Back > 185.f)
			{
				if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 2.5; Feedback(TEXT("Stand right in front of it.")); }
				return true;
			}
		}
		// (it used to wait until he had read her scrap about the hollow book.  Cheyenne: "I don't think it's necessary
		// for that to wait ... that scare is such a small scare that it could just add to the scares in general.")
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
		SetObjective(TEXT("Take the long key to the attic door upstairs"));
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
	case 1: BuildStep = 7; break;          // (the rest of the build-up is set off by what he does: WCEvents.cpp, GWCCues)
	default: break;
	}
	// (the thump used to come on a clock here; it is now set off by taking the small key: AWCDirector::UpstairsThump)
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

static const float GAirDur = 18.f;            // how long the camera is outside the car at the start of the drive
static float GAirMoon = 7.f, GAirSky = 5.f;   // the moon and the sky, while the camera is high: times the game's own night
static float GAirHi = 12000.f, GAirLo = 7000.f, GAirFov = 28.f, GAirHead = 6.f;



void AWCDirector::AirIntoCar()
{
	for (const auto& H : AirHeads) if (H.Key.IsValid()) H.Key->SetIntensity(H.Value);
	for (const auto& T : AirTrees) if (T.Key.IsValid()) T.Key->SetCullDistance(T.Value);
	AirTrees.Reset();
	if (AirWood.IsValid()) AirWood->Destroy();



	if (AirMoon.IsValid()) AirMoon->GetLightComponent()->SetIntensity(AirMoonBase);
	if (AirSky.IsValid()) AirSky->GetLightComponent()->SetIntensity(AirSkyBase);

	// the camera is through the roof: the outside of the car goes, the inside is there, the night is shut out
	if (bAirSwapped) return;
	bAirSwapped = true;
	ShowTagged(TEXT("CabinOnly"), true);
	if (Car.IsValid()) Car->SetActorHiddenInGame(true);
	SetLoop(TEXT("amb"), TEXT(""), 0.f, 0.8f);
}

void AWCDirector::BeginDrive()
{

	ShowTagged(TEXT("CabinOnly"), true);          // the inside of the car exists only while he is in it
	if (Car.IsValid()) Car->SetActorHiddenInGame(true);      // and the outside does not (its aerial stood in the windscreen like a black pole)
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
	DriveSpeed = 620.f;
	ShadowDist = -1.f; ShadowPhase = 0; ShadowT = 0.f;
	if (AActor* Sh = Find(TEXT("RoadShadow")))
	{
		float Best = 1e9f;
		for (float D0 = 0.f; D0 < DriveTotal; D0 += 100.f)
		{
			const float Dd = FVector::Dist2D(PathPoint(DrivePts, DriveLen, D0), Sh->GetActorLocation());
			if (Dd < Best) { Best = Dd; ShadowDist = D0; }
		}
		ShowTagged(TEXT("RoadShadow"), true);
		UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE the thing on the road stands %.0f m in"), ShadowDist / 100.f);
	}
	bDriving = true;
	bParkedCarCollision = Car->GetActorEnableCollision();
	Car->SetActorEnableCollision(false);
	P->SetInputLocked(true);
	P->SetFlashlight(false, false);
	P->SetActorHiddenInGame(true);
	FActorSpawnParameters SP;
	ACameraActor* Cam = GetWorld()->SpawnActor<ACameraActor>(Seat->GetActorLocation(), FRotator::ZeroRotator, SP);
	if (Cam)
	{
		CabinFov = FMath::Min(Settings.FOV - 8.f, 66.f);
			Cam->GetCameraComponent()->SetFieldOfView(CabinFov);      // tighter, so the windscreen fills the picture

		Cam->GetCameraComponent()->bConstrainAspectRatio = false;
		DriveCam = Cam;
		PC->SetViewTargetWithBlend(Cam, 0.f);
	}
	DriveHeading = (PathPoint(DrivePts, DriveLen, 400.f) - PathPoint(DrivePts, DriveLen, 0.f)).Rotation().Yaw;
	PC->SetControlRotation(FRotator(0.f, DriveHeading, 0.f));
	ShowTagged(TEXT("CarRunning"), true);
	SetLoop(TEXT("car"), TEXT("amb_car"), 1.f, 1.2f);
	SetLoop(TEXT("amb"), TEXT(""), 0.f, 1.f);              // windows up: the night is not heard until he gets out
	// the opening shot: high over the forest, his headlights threading the road, then down and into the car
	bAir = !FParse::Param(FCommandLine::Get(), TEXT("WCNoAir"));
	AirT = 0.f; bAirDip = false; bAirSwapped = !bAir;
	if (bAir)
	{
		ShowTagged(TEXT("CabinOnly"), false);
		Car->SetActorHiddenInGame(false);
		SetLoop(TEXT("amb"), TEXT("amb_night"), 0.5f, 1.5f);        // out here the night is all there is to hear
		FParse::Value(FCommandLine::Get(), TEXT("WCAirMoon="), GAirMoon);
		FParse::Value(FCommandLine::Get(), TEXT("WCAirSky="), GAirSky);
		FParse::Value(FCommandLine::Get(), TEXT("WCAirHi="), GAirHi);
		FParse::Value(FCommandLine::Get(), TEXT("WCAirLo="), GAirLo);
		FParse::Value(FCommandLine::Get(), TEXT("WCAirFov="), GAirFov);
		FParse::Value(FCommandLine::Get(), TEXT("WCAirHead="), GAirHead);
		// the forest is culled at 100 m for the game's sake; from the air it has to be there as far as the eye goes
		AirTrees.Reset();
		for (TActorIterator<AStaticMeshActor> It(GetWorld()); It; ++It)
		{
			UStaticMeshComponent* C = It->GetStaticMeshComponent();
			if (C && C->LDMaxDrawDistance >= 9000.f) { AirTrees.Add(TPair<TWeakObjectPtr<UStaticMeshComponent>, float>(C, C->LDMaxDrawDistance)); C->SetCullDistance(0.f); }
		}
		UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE from the air: %d trees drawn at any distance"), AirTrees.Num());
		// a road through a wood, not a hedge across a field: from the air the forest has to go on to the edge of the picture
		{
			TArray<UStaticMesh*> Kinds;
			float TreeZ = -44.f;
			for (const auto& T : AirTrees)
			{
				UStaticMesh* M = T.Key.IsValid() ? T.Key->GetStaticMesh() : nullptr;
				if (!M || !M->GetName().Contains(TEXT("Pine")) || M->GetName().Contains(TEXT("Sapling")) || Kinds.Contains(M)) continue;
				if (Kinds.Num() == 0) TreeZ = T.Key->GetComponentLocation().Z;
				Kinds.Add(M);
				if (Kinds.Num() >= 4) break;
			}
			// (off unless asked for with -WCAirWood=<trees>: 420 of them took the shot from 37 frames a second to 14, and
			// what his headlights light is the road's own trees anyway; the rest is dark either way)
			int32 WoodN = 0;
			FParse::Value(FCommandLine::Get(), TEXT("WCAirWood="), WoodN);
			AActor* Wood = Kinds.Num() > 0 && WoodN > 0 ? GetWorld()->SpawnActor<AActor>(AActor::StaticClass(), FTransform::Identity) : nullptr;
			if (Wood)
			{
				USceneComponent* Root = NewObject<USceneComponent>(Wood);
				Wood->SetRootComponent(Root);
				Root->RegisterComponent();
				TArray<UInstancedStaticMeshComponent*> Ism;
				for (UStaticMesh* M : Kinds)
				{
					UInstancedStaticMeshComponent* C = NewObject<UInstancedStaticMeshComponent>(Wood);
					C->SetStaticMesh(M);
					C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
					C->SetCastShadow(false);
					C->SetupAttachment(Root);
					C->RegisterComponent();
					Ism.Add(C);
				}
				FRandomStream Rs(7741);
				const FVector Gate = PathPoint(DrivePts, DriveLen, DriveTotal);
				int32 N = 0;
				for (int32 i = 0; i < WoodN * 8 && N < WoodN; ++i)
				{
					const float D = Rs.FRandRange(-4000.f, 20000.f);
					const float Dc = FMath::Clamp(D, 0.f, DriveTotal);
					const FVector Dir = (PathPoint(DrivePts, DriveLen, FMath::Min(Dc + 300.f, DriveTotal)) - PathPoint(DrivePts, DriveLen, FMath::Max(Dc - 300.f, 0.f))).GetSafeNormal2D();
					FVector Q = PathPoint(DrivePts, DriveLen, Dc) + Dir * (D - Dc);
					Q += FVector(-Dir.Y, Dir.X, 0.f) * Rs.FRandRange(1500.f, 7500.f) * (Rs.FRand() < 0.5f ? -1.f : 1.f);
					if (FVector::Dist2D(Q, Gate) < 9000.f) continue;                    // not in her yard
					bool bOnRoad = false;
					for (float D0 = 0.f; D0 <= DriveTotal && !bOnRoad; D0 += 500.f) bOnRoad = FVector::Dist2D(PathPoint(DrivePts, DriveLen, D0), Q) < 1400.f;
					if (bOnRoad) continue;
					const float Sc = Rs.FRandRange(0.9f, 1.3f);
					Ism[Rs.RandRange(0, Ism.Num() - 1)]->AddInstance(FTransform(FRotator(0.f, Rs.FRandRange(0.f, 360.f), 0.f), FVector(Q.X, Q.Y, TreeZ), FVector(Sc, Sc, Sc * Rs.FRandRange(0.92f, 1.1f))), true);
					++N;
				}
				AirWood = Wood;
				UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE from the air: a wood of %d more trees either side of the road (%d kinds)"), N, Kinds.Num());
			}
		}

		AirHeads.Reset();

		for (TActorIterator<ALight> It(GetWorld()); It; ++It)
			if (It->ActorHasTag(TEXT("Headlight")) && It->GetLightComponent()) AirHeads.Add(TPair<TWeakObjectPtr<ULightComponent>, float>(It->GetLightComponent(), It->GetLightComponent()->Intensity));
		AirMoon = nullptr; AirSky = nullptr;

		for (TActorIterator<ADirectionalLight> It(GetWorld()); It; ++It) if (It->ActorHasTag(TEXT("Hide_dawn"))) { AirMoon = *It; AirMoonBase = It->GetLightComponent()->Intensity; }
		for (TActorIterator<ASkyLight> It(GetWorld()); It; ++It) { AirSky = *It; AirSkyBase = It->GetLightComponent()->Intensity; }
		UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE from the air: moon %.1f x%.1f, sky %.2f x%.1f"), AirMoonBase, GAirMoon, AirSkyBase, GAirSky);

	}
		TickDrive(0.f);
	After(bAir ? GAirDur + 2.f : 5.f, [this]() { if (bDriving) ShowHint(TEXT("Mouse: look around        Space: skip the drive"), 6.f); });

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
		if (bAir) { bAir = false; AirIntoCar(); if (DriveCam.IsValid()) DriveCam->GetCameraComponent()->SetFieldOfView(CabinFov); }
		ShadowPhase = 3;

		ShowTagged(TEXT("RoadShadow"), false);
	}
	const float Left = DriveTotal - DriveDist;
	const float Cruise = 620.f;                   // slow: a deputy on a dirt road at night he does not know
	float Want = Left < 2600.f ? FMath::Max(55.f, Cruise * FMath::Sqrt(FMath::Max(Left, 0.f) / 2600.f)) : Cruise;
	float Ease = 2.5f;
	float LookBack = 0.f;
	if (ShadowDist > 0.f && ShadowPhase < 3)
	{
		ShadowT += Dt;
		if (ShadowPhase == 0 && DriveDist > ShadowDist + 230.f)
		{
			// it has just left the headlights: and it is not there any more
			ShadowPhase = 1; ShadowT = 0.f;
			ShowTagged(TEXT("RoadShadow"), false);
			UE_LOG(LogWCHouse, Display, TEXT("WCEVENT t=%.1f passed the thing on the road"), PlaySeconds);
		}
		else if (ShadowPhase == 1)
		{
			if (ShadowT > 1.3f) { Want = 0.f; Ease = 0.75f; }
			if (ShadowT > 1.3f && DriveSpeed < 14.f) { ShadowPhase = 2; ShadowT = 0.f; DriveSpeed = 0.f; }
			if (ShadowT > 1.9f && ShadowT - Dt <= 1.9f) Think(TEXT("...Was somebody standing there?"), 4.5f);
		}
		else if (ShadowPhase == 2)
		{
			Want = 0.f; DriveSpeed = 0.f;
			// a slow turn in the seat, a long look down the road behind, a slow turn back
			if (ShadowT < 1.2f) LookBack = 0.f;
			else if (ShadowT < 5.0f) LookBack = FMath::InterpEaseInOut(0.f, 1.f, (ShadowT - 1.2f) / 3.8f, 2.f);
			else if (ShadowT < 9.0f) LookBack = 1.f;
			else if (ShadowT < 12.4f) LookBack = FMath::InterpEaseInOut(1.f, 0.f, (ShadowT - 9.0f) / 3.4f, 2.f);
			else { ShadowPhase = 3; ShadowT = 0.f; }
			if (ShadowT > 6.4f && ShadowT - Dt <= 6.4f) Think(TEXT("Nothing. Just the road."), 4.f);
		}
	}
	else if (ShadowPhase == 3 && ShadowDist > 0.f && DriveSpeed < Cruise * 0.9f && Left > 2600.f) Ease = 0.5f;      // and he pulls away gently
	DriveSpeed = FMath::FInterpTo(DriveSpeed, Want, Dt, Ease);
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
	if (ShadowPhase == 2) { Rel.Yaw = 154.f * LookBack; Rel.Pitch = -2.f * LookBack; }      // over his right shoulder, where it stood
	DriveHeading = Heading;
	Car->SetActorLocationAndRotation(FVector(Pos0.X, Pos0.Y, CarHome.Z + Bump * 0.5f), FRotator(0.f, Heading + CarHomeRot.Yaw, Roll * 0.6f));
	if (PC) PC->SetControlRotation(FRotator(Rel.Pitch, Heading + Rel.Yaw, 0.f));
	float AirS = 1.f;
	if (DriveCam.IsValid() && Seat.IsValid())
	{
		const FVector SeatPos = Seat->GetActorLocation() + FVector(0, 0, Bump * 0.8f);
		const FRotator SeatRot(Rel.Pitch + Bump * 0.12f, Heading + Rel.Yaw, Roll);
		if (bAir)
		{
			AirT += Dt;
			const float U = FMath::Clamp(AirT / GAirDur, 0.f, 1.f);
			// the first half and a little more it stays up and follows; then it comes down a long curve to the seat
			AirS = FMath::SmoothStep(0.f, 1.f, (U - 0.55f) / 0.45f);
			const float Up = FMath::Clamp(U / 0.55f, 0.f, 1.f);
			const FVector CarPos(Pos0.X, Pos0.Y, CarHome.Z);
			const FVector Fwd = FRotator(0.f, Heading, 0.f).Vector();
			const float Orbit = Heading + 180.f + 42.f * FMath::Sin(AirT * 0.21f + 0.6f);
			const FVector High = CarPos + FRotator(0.f, Orbit, 0.f).Vector() * FMath::Lerp(GAirHi * 0.12f, GAirLo * 0.5f, Up) + FVector(0, 0, FMath::Lerp(GAirHi, GAirLo, Up));

			const FVector Chase = CarPos - Fwd * 1000.f + FVector(0, 0, 420.f);
			const FVector Cp = FMath::Square(1.f - AirS) * High + 2.f * AirS * (1.f - AirS) * Chase + AirS * AirS * SeatPos;
			const FVector LookAt = CarPos + Fwd * FMath::Lerp(0.f, 2600.f, AirS) + FVector(0, 0, 90.f);
			const FQuat Q = FQuat::Slerp((LookAt - Cp).Rotation().Quaternion(), SeatRot.Quaternion(), FMath::SmoothStep(0.f, 1.f, (AirS - 0.72f) / 0.28f));
			DriveCam->SetActorLocationAndRotation(Cp, Q);
			DriveCam->GetCameraComponent()->SetFieldOfView(FMath::Lerp(GAirFov, CabinFov, AirS));

			// from up here there is only the moon to see by: it is let in while the camera is high, and gone again by the time it is in the trees
			const float Night = FMath::SmoothStep(0.f, 1.f, (AirS - 0.2f) / 0.5f);
			if (AirMoon.IsValid()) AirMoon->GetLightComponent()->SetIntensity(AirMoonBase * FMath::Lerp(GAirMoon, 1.f, Night));
			if (AirSky.IsValid()) AirSky->GetLightComponent()->SetIntensity(AirSkyBase * FMath::Lerp(GAirSky, 1.f, Night));
			for (const auto& H : AirHeads) if (H.Key.IsValid()) H.Key->SetIntensity(H.Value * FMath::Lerp(GAirHead, 1.f, Night));


			if (!bAirDip && AirS > 0.80f) { bAirDip = true; FadeTo(0.85f, 0.3f); }
			if (!bAirSwapped && AirS > 0.88f) { AirIntoCar(); After(0.12f, [this]() { FadeTo(0.f, 0.7f); }); }
			if (bAuto && !AutoShotDir.IsEmpty())
			{
				static int32 AirShotN = -1;
				const int32 N = (int32)(AirT / 1.5f);
				if (N != AirShotN) { AirShotN = N; FScreenshotRequest::RequestScreenshot(AutoShotDir / FString::Printf(TEXT("air_%02d.png"), N), false, false); }
			}
			if (U >= 1.f)
			{
				bAir = false;
				AirIntoCar();
				DriveCam->GetCameraComponent()->SetFieldOfView(CabinFov);
				UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE t=%.1f the camera is in the car, %.0f m in"), PlaySeconds, DriveDist / 100.f);
				if (FParse::Param(FCommandLine::Get(), TEXT("WCAirOnly")))
				{
					const FString Dir0 = AutoShotDir;
					After(2.f, [Dir0]() { if (!Dir0.IsEmpty()) FScreenshotRequest::RequestScreenshot(Dir0 / TEXT("air_in_the_seat.png"), false, false); });
					After(3.5f, [this]() { UKismetSystemLibrary::QuitGame(this, UGameplayStatics::GetPlayerController(this, 0), EQuitPreference::Quit, false); });
				}
			}
		}
		else DriveCam->SetActorLocationAndRotation(SeatPos, SeatRot);
	}
	// a 1990s V8 cruiser: it is always there, idling or pulling, and it can be heard from the air too (Cheyenne: "amplified ... engines were louder")
	// (Cheyenne, 21:49: loud until the camera is in the cab; then well down, so the deputy and dispatch are heard over it)
	if (FLoop* Eng = Loops.Find(TEXT("car"))) Eng->Target = FMath::Lerp(1.f, 0.30f + 0.05f * Rough, FMath::SmoothStep(0.f, 1.f, (AirS - 0.6f) / 0.4f));

	if (Left < 4.f && DriveSpeed < 70.f) EndDrive();
}

void AWCDirector::EndDrive()
{
	if (!bDriving) return;
	bDriving = false;
	Set(TEXT("arrived"));
	ShowTagged(TEXT("CabinOnly"), false);
	if (Car.IsValid()) Car->SetActorHiddenInGame(false);
	if (FParse::Param(FCommandLine::Get(), TEXT("WCDriveOnly")))
	{
		const FString Dir0 = AutoShotDir;
		After(5.f, [Dir0]() { if (!Dir0.IsEmpty()) FScreenshotRequest::RequestScreenshot(Dir0 / TEXT("drive_parked.png"), false, false); });
		// when filming, stay until he has walked up to the house
		After(FParse::Param(FCommandLine::Get(), TEXT("WCFilm")) ? 34.f : 7.f, [this]() { UKismetSystemLibrary::QuitGame(this, UGameplayStatics::GetPlayerController(this, 0), EQuitPreference::Quit, false); });
	}
	if (Car.IsValid())
	{
		Car->SetActorLocationAndRotation(CarHome, CarHomeRot);
		Car->SetActorEnableCollision(bParkedCarCollision);
	}
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
		SetLoop(TEXT("amb"), TEXT("amb_yard"), 1.f, 2.f);
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
			&& !Has(TEXT("phone_ringing")) && Clock >= NextScareAt && Clock >= NextStalkAt && StalksDone < 4 && !bEventBusy && L.Z > -60.f && L.Z < 560.f && !P->IsDown();
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
			if (bAmbush || bClose) H->MoveAlong(Route, bAmbush ? 2000.f : 1725.f, TEXT("Run"));      // half as fast again (Cheyenne, 03:54)
			else H->MoveAlong(Route, 185.f, TEXT("Walk"));          // as fast as her walk plays without her feet sliding; he hears every step
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
			NextStalkAt = Clock + (Rng.FRandRange(360.f, 540.f) / 1.15f) * FMath::Max(TestPace, 0.3f);
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
	NextStalkAt = Clock + (Rng.FRandRange(360.f, 540.f) / 1.15f) * FMath::Max(TestPace, 0.3f);
	Tension = 0.5f;
	UE_LOG(LogWCHouse, Display, TEXT("WCSTALK t=%.1f end driven=%d"), PlaySeconds, bDriven ? 1 : 0);
}

// ================================================================================================ per-frame
FVector AWCDirector::BinFocusPoint() const
{
	if (const AActor* Body = Find(TEXT("BinBody")))
	{
		FVector Center, Extent;
		Body->GetActorBounds(false, Center, Extent);
		return Center;
	}
	return Pos(TEXT("TrashPoint")) + FVector(0, 0, -5);
}

void AWCDirector::TickBinTurn(float Dt)
{
	if (!IsBinTurnActive()) return;
	AWCCharacter* Deputy = Player();
	if (!Deputy || !Deputy->GetController()) { BinTurnAt = -1.; return; }
	const double Age = Clock - BinTurnAt;
	if (Age < 0.) return;
	const FVector Target = BinFocusPoint();
	const FVector From = Deputy->GetActorLocation();
	if (bStepToShedDoor && Age > .12)
	{
		const FVector Exit = Pos(TEXT("A_Shed"));
		// Ease across the threshold on a swept path. Align with the opening first
		// when starting beside the door jamb, and keep the capsule on its floor.
		const float Side = FMath::SmoothStep(.12f,.85f,float(Age));
		const float Delay = FMath::Abs(BinStartPos.Y-Exit.Y) > 48.f ? .48f : .12f;
		const float Step = FMath::SmoothStep(Delay,2.12f,float(Age));
		Deputy->SetActorLocation(FVector(FMath::Lerp(BinStartPos.X,Exit.X,Step),
			FMath::Lerp(BinStartPos.Y,Exit.Y,Side),From.Z),true);
	}
	const FRotator Want = (Target - Deputy->EyeLocation()).Rotation();
	BinTargetYaw += FMath::FindDeltaAngleDegrees(BinTargetYaw, float(Want.Yaw));
	const float Turn = FMath::SmoothStep(0.f, 1.95f, float(Age));
	Deputy->GetController()->SetControlRotation(FRotator(FMath::Lerp(BinViewStart.Pitch,Want.Pitch,Turn),
		FMath::Lerp(BinViewStart.Yaw,double(BinTargetYaw),double(Turn)),0.));
	if (Age >= 2.44)
	{
		BinTurnAt = -1.;
		UE_LOG(LogWCHouse, Display, TEXT("WCBIN camera finished alignment=%.3f sight=%d"),
			FVector::DotProduct(Deputy->EyeForward(), (Target-Deputy->EyeLocation()).GetSafeNormal()),
			PlayerSees(Target, .8f, 1800.f));
	}
}

void AWCDirector::HouseTick(float Dt)
{
	{
		// -WCVideo=<dir>: every frame of the opening as a numbered picture (run with -UseFixedTimeStep -FPS=30)
		static FString VideoDir;
		static bool bVideoInit = false;
		static int32 VideoFrame = 0;
		if (!bVideoInit)
		{
			bVideoInit = true;
			if (FParse::Value(FCommandLine::Get(), TEXT("WCVideo="), VideoDir)) { VideoDir = FPaths::ConvertRelativePathToFull(VideoDir); IFileManager::Get().MakeDirectory(*VideoDir, true); }
		}
		if (!VideoDir.IsEmpty() && Mode == EWCMode::Playing && VideoFrame < 4500) FScreenshotRequest::RequestScreenshot(VideoDir / FString::Printf(TEXT("f_%05d.png"), VideoFrame++), false, false);
	}
	if (bDriving) { TickDrive(Dt); return; }
	TickBinTurn(Dt);
	UpdateFurniture(Dt);
	TickVentTool();
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
	TickRecord(Dt);
	TickTV(Dt);
	TickEye(Dt);
	if (!bFilterInit) bDev = FParse::Param(FCommandLine::Get(), TEXT("WCDev"));
	if (bDev)
	{
		if (APlayerController* DevPC = GetWorld()->GetFirstPlayerController())
		{
			if (DevPC->WasInputKeyJustPressed(EKeys::F9) && Has(TEXT("inside")) && !Has(TEXT("heard_upstairs")))
			{
				if (!HasItem(TEXT("key_box")) && !Has(TEXT("box_open"))) GiveItem(TEXT("key_box"), TEXT("Small key"));
				Set(TEXT("doll_opened"));
				UpstairsThump();                                     // as if he had just taken the small key
				ShowToast(TEXT("DEV: the upstairs thump is coming. Go up the stairs."));
			}
			if (DevPC->WasInputKeyJustPressed(EKeys::F10))
			{
				NextScareAt = Clock; EyeNextAt = Clock; TVNextAt = Clock; NextDoorAt = Clock; NextLightKill = Clock;
				ShowToast(TEXT("DEV: the quiet gap is over. Whatever is waiting may happen now."));
			}
		}
	}
	if (!bFilterInit) { bFilterInit = true; int32 L = Settings.Filter; FParse::Value(FCommandLine::Get(), TEXT("WCFilter="), L); SetFilter(L); }
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
	UE_LOG(LogWCHouse, Display, TEXT("WCSCARE t=%.1f S10_book"), PlaySeconds);
	AWCCharacter* P = Player();
	AActor* Book = Find(TEXT("SettlersBook"));
	AWCWatcher* EyeW = nullptr;
	for (TActorIterator<AWCWatcher> It(GetWorld()); It; ++It) if (It->WCId == TEXT("book_eye")) EyeW = *It;
	if (AWCInteractable* U = Thing(TEXT("book_settlers"))) U->bEnabled = false;
	if (!P || !Book) { FinishSettlersPickup(); return; }
	bBusy = true;
	P->SetInputLocked(true);
	Play2D(TEXT("paper"), 0.8f, EWCSnd::SFX, 0.7f);
	const FVector From = Book->GetActorLocation();
	const FVector Out = (P->GetActorLocation() - From).GetSafeNormal2D();
	// he draws the book out...
	for (int32 i = 1; i <= 14; ++i) After(i * 0.035f, [Book, From, Out, i]() { if (IsValid(Book)) Book->SetActorLocation(From + Out * (26.f * i / 14.f)); });
	TWeakObjectPtr<UStaticMeshComponent> Backing;
	if (EyeW)
	{
		UStaticMeshComponent* Dark = NewObject<UStaticMeshComponent>(this);
		Dark->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
		Dark->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WC/Materials/M_Void.M_Void")));
		Dark->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Dark->SetCastShadow(false);
		Dark->SetReceivesDecals(false);
		Dark->SetWorldLocationAndRotation(EyeW->GetActorLocation()-EyeW->GetActorForwardVector()*14.,EyeW->GetActorRotation());
		Dark->SetWorldScale3D(FVector(.012,.17,.26));
		Dark->RegisterComponent();
		Backing = Dark;
	}
	// while his hands are on the book his eyes settle on the gap it is leaving
	{
		const FVector Gap = EyeW ? EyeW->GetActorLocation() : From;
		const FVector Side = EyeW ? EyeW->GetActorRightVector() : FVector::ZeroVector;
		for (int32 i = 1; i <= 16; ++i) After(i * 0.035f, [this, Gap, Side]()
		{
			AWCCharacter* Q = Player();
			if (!Q || !Q->GetController()) return;
			// a half step to the side, no more: he ends up square to the hole
			const float Off = FVector::DotProduct(Q->GetActorLocation() - Gap, Side);
			Q->SetActorLocation(Q->GetActorLocation() - Side * (Off - FMath::FInterpTo(Off, 0.f, 0.035f, 9.f)), true);

			const FRotator Want = (Gap - Q->EyeLocation()).Rotation();
			Q->GetController()->SetControlRotation(FMath::RInterpTo(Q->GetController()->GetControlRotation(), Want, 0.035f, 9.f));
		});
	}
	// ...and she is looking at him through the wall
	After(0.62f, [this, EyeW, Book, From, Out, Backing]()
	{
		Tension = .65f;
		// the book goes out of his hand
		const FVector Start = From + Out * 26.f;
		// The living-room floor dressing over the structural slab reaches Z=8 here.
		const float FloorZ = FMath::FloorToFloat((From.Z + 20.f) / 350.f) * 350.f + 8.3f;
		StageSettlersPickup(Book, Start, Out, FloorZ);
		After(.8f, [this, From]() { PlayAt(TEXT("shelf_violin"), From, .77f); });
		After(1.05f, [EyeW]()
		{
			if (IsValid(EyeW)) EyeW->Reveal();
		});
		// Hold the stare after the pupil stops, then let the treads carry her away.
		After(4.85f, [this]() { StartleDeputy(.84f); });
		After(6.4f, [this, EyeW, Backing]()
		{
			if (IsValid(EyeW)) EyeW->Withdraw(true);
			StartleDeputy(.93f);
			After(.4f, [Backing]() { if (Backing.IsValid()) Backing->DestroyComponent(); });
			const FVector A = Pos(TEXT("StairRunA")), B = Pos(TEXT("StairRunB")), C = Pos(TEXT("StairRunC"));
			if (A.IsNearlyZero() || B.IsNearlyZero()) return;
			UE_LOG(LogWCHouse, Display, TEXT("WCSCARE t=%.1f S10_book she runs up the stairs"), PlaySeconds);
			// seven treads at a run, then away along the landing overhead
			const float Treads[] = {.09f,.32f,.50f,.71f,.89f,1.10f,1.29f};
			for (int32 k = 0; k < UE_ARRAY_COUNT(Treads); ++k)
				After(Treads[k], [this, A, B, k]() {
					PlayAt(TEXT("shelf_stair_step"), FMath::Lerp(A,B,k/6.f), k%2 ? 1.22f : 1.34f, Rng.FRandRange(.92f,1.03f));
				});
			for (int32 k = 0; k < 4; ++k)
				After(1.50f + k*.23f, [this, B, C, k]() {
					PlayAt(TEXT("shelf_stair_step"), FMath::Lerp(B,C,(k+1)/4.f), 1.18f-.085f*k, Rng.FRandRange(.95f,1.06f));
				});
		});

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
	P->SetFaceLight(85.f);
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
		FadeTo(0.f, 1.4f);                      // back to the house (whatever comes next may fade again; it used to stay black)
		if (Then) Then();
	});
}
