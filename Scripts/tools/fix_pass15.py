"""Wire the house systems (WCHouse.cpp) into the director and re-pace the story:
drive-up opening, locked in on arrival, 8-10 minutes before she is seen, lights, fuse, desk, shears, gun deterrent."""
import io
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"


import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
import patchlib


def edit(f, pairs):
    patchlib.edit(R + f, pairs)


# ================================================================ WCDirector.h
edit("WCDirector.h", [
    ('''	bool Gate() const { return Clock >= NextScareAt; }''', '''	bool Gate() const { return Clock >= NextScareAt && StalkState == 0 && !bDriving; }'''),
    ('''	float Tension = 0.f;      // 0 calm .. 1 frantic; drives ambience, breathing, random cues''', '''	float Tension = 0.f;      // 0 calm .. 1 frantic; drives ambience, breathing, random cues

	// ------------------------------------------------------------------ the house (WCHouse.cpp)
	struct FRoomLights
	{
		TArray<TWeakObjectPtr<class ULightComponent>> Lights;
		TArray<float> Base;
		bool bOn = false;
		double KillAt = 0.0, FlickUntil = 0.0, DeadUntil = 0.0;
		float Seed = 0.f;
		FVector SwitchLoc = FVector::ZeroVector;
		int32 Kills = 0;
	};
	TMap<FName, FRoomLights> Rooms;
	void SwitchRoom(FName Room, bool bOn, bool bClick = true);
	/** Every house light out, and the switches dead for a while. */
	void KillLights(float DeadSeconds, bool bPop = false);
	bool IsDriving() const { return bDriving; }
	bool bPowerOut = false;
	int32 StalkState = 0;     // 0 none, 1 she has appeared, 2 she is coming
	TSet<FName> LooksSeen;'''),
    ('''	void FinaleStep(int32 Knot);
	void FinaleCaught();''', '''	void FinaleStep(int32 Knot);
	void FinaleCaught();
	void ScareSewing();
	// the house (WCHouse.cpp)
	void HouseBegin();
	void HouseTick(float Dt);
	bool HouseEvent(FName Id);
	void TickHouseLights(float Dt);
	void TickBuildUp(float Dt);
	void BeginDrive();
	void TickDrive(float Dt);
	void EndDrive();
	void DriveDone();
	void TickStalk(float Dt);
	void StalkShot();
	void EndStalk(bool bDriven);
	bool bDriving = false;
	TArray<FVector> DrivePts;
	TArray<float> DriveLen;
	float DriveTotal = 0.f, DriveDist = 0.f, DriveSpeed = 0.f, DriveHeading = 0.f;
	TWeakObjectPtr<AActor> Car;
	TWeakObjectPtr<AActor> Seat;
	TWeakObjectPtr<class ACameraActor> DriveCam;
	FVector CarHome = FVector::ZeroVector;
	FRotator CarHomeRot = FRotator::ZeroRotator;
	TArray<FVector> NavPts;
	double NextLightKill = 0.0;
	int32 BuildStep = 0;
	TWeakObjectPtr<AActor> RockActor;
	double RockUntil = 0.0;
	FRotator RockBase = FRotator::ZeroRotator;
	double StalkAt = 0.0, NextStalkAt = 0.0, StalkLostAt = 0.0, StalkRepath = 0.0, StalkPauseUntil = 0.0;
	int32 StalkHits = 0, StalkNeed = 4, StalksDone = 0, Catches = 0;'''),
])

# ================================================================ WCDirector.cpp
edit("WCDirector.cpp", [
    ('''			SetLoop(TEXT("amb"), TEXT("amb_night"), 0.9f, 2.f);
			SetLoop(TEXT("music"), TEXT("music_menu"), 0.7f, 4.f, EWCSnd::Music);
		}''', '''			SetLoop(TEXT("amb"), TEXT("amb_night"), 0.9f, 2.f);
			SetLoop(TEXT("music"), TEXT("music_menu"), 0.7f, 4.f, EWCSnd::Music);
			HouseBegin();
		}'''),
    ('''			const bool bLoaded = Start == 2 && DoLoad();
			StoryBegin(bLoaded);''', '''			const bool bLoaded = Start == 2 && DoLoad();
			HouseBegin();
			StoryBegin(bLoaded);'''),
    ('''			if (Clock >= NextTrigPoll) { NextTrigPoll = Clock + 0.1; TickTriggers(); }
			StoryTick(Dt);''', '''			if (Clock >= NextTrigPoll) { NextTrigPoll = Clock + 0.1; TickTriggers(); }
			HouseTick(Dt);
			StoryTick(Dt);'''),
    ('''	if (!P || bBusy) return;
	const FVector L = P->GetActorLocation();''', '''	if (!P || bBusy || bDriving) return;
	const FVector L = P->GetActorLocation();'''),
])

# ================================================================ WCStory.cpp
edit("WCStory.cpp", [
    # world state
    ('''	ShowTagged(TEXT("Show_drawer"), Has(TEXT("phone_done")));
	ShowTagged(TEXT("L_Welcome"), !Has(TEXT("knocked")));''', '''	ShowTagged(TEXT("Show_drawer"), Has(TEXT("phone_done")));
	ShowTagged(TEXT("Hide_shears"), !HasItem(TEXT("shears")));
	if (AWCInteractable* Desk = Thing(TEXT("desk"))) Desk->bEnabled = !Has(TEXT("desk_open"));
	bPowerOut = Has(TEXT("power_out")) && !Has(TEXT("fuse_done"));'''),
    ('''	SetLoop(TEXT("low"), bIn ? TEXT("music_low") : TEXT(""), bIn ? 0.25f : 0.f, 6.f, EWCSnd::Music);''',
     '''	SetLoop(TEXT("low"), bIn ? TEXT("music_low") : TEXT(""), bIn ? 0.25f : 0.f, 6.f, EWCSnd::Music);
	SetLoop(TEXT("wind"), (bIn || bCellar) ? TEXT("amb_wind") : TEXT(""), bIn ? 0.55f : 0.f, 5.f);'''),
    # the opening: drive, or (for tests / if the road is missing) standing by the car
    ('''	AWCCharacter* P = Player();
	if (P) { P->SetInputLocked(true); P->SetFlashlight(false, false); }
	Play2D(TEXT("car_door"), 0.8f);
	After(1.2f, [this]() { FadeTo(0.f, 3.f); });
	float T = 2.4f;
	T = Say(TEXT("d_arrive1"), T);
	T = Say(TEXT("r_arrive1"), T);
	After(4.f, [this]()
	{
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		ShowHint(TEXT("WASD move    Mouse look    F flashlight    E use    Shift run    C crouch"), 9.f);
	});
	T = Say(TEXT("d_arrive2"), T);
	T = Say(TEXT("r_arrive2"), T);
	T = Say(TEXT("d_arrive3"), T);
	T = Say(TEXT("r_arrive3"), T);
	T = Say(TEXT("d_arrive4"), T);
	After(T, [this]() { SetObjective(TEXT("Check on Edith Harrow")); Set(TEXT("briefed")); });
}''', '''	AWCCharacter* P = Player();
	if (P) { P->SetInputLocked(true); P->SetFlashlight(false, false); }
	const bool bWantDrive = !FParse::Param(FCommandLine::Get(), TEXT("WCNoDrive")) && (!bAuto || FParse::Param(FCommandLine::Get(), TEXT("WCDrive")));
	if (bWantDrive) BeginDrive();
	if (bDriving)
	{
		// the road in: title, then the call that sends him here
		After(1.0f, [this]() { FadeTo(0.f, 3.5f); });
		After(3.5f, [this]() { BigText = TEXT("EDITH'S LAST CALL"); BigSub = TEXT(""); BigTarget = 1.f; });
		After(9.0f, [this]() { BigTarget = 0.f; });
		float T = 12.f;
		T = Say(TEXT("d_arrive1"), T);
		T = Say(TEXT("r_arrive1"), T + 0.3f);
		T = Say(TEXT("r_arrive2"), T + 2.2f);
		T = Say(TEXT("d_arrive3"), T + 0.6f);
		return;
	}
	Play2D(TEXT("car_door"), 0.8f);
	After(1.2f, [this]() { FadeTo(0.f, 3.f); });
	After(3.f, [this]()
	{
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		ShowHint(TEXT("WASD move    Mouse look    F flashlight    E use / examine    Shift hurry    C crouch"), 9.f);
		DriveDone();
	});
}

/** Out of the car, standing in the yard: the last of the radio traffic, then the house is his problem. */
void AWCDirector::DriveDone()
{
	float T = Say(TEXT("d_arrive2"), 1.2f);
	T = Say(TEXT("r_arrive3"), T + 0.3f);
	T = Say(TEXT("d_arrive4"), T + 0.2f);
	After(bAuto ? 0.5f : T, [this]() { SetObjective(TEXT("Check on Edith Harrow")); Set(TEXT("briefed")); });
}'''),
    # events: the house first
    ('''	AWCCharacter* P = Player();
	if (!P) return;

	// ================================================================= act 1: arrival''', '''	AWCCharacter* P = Player();
	if (!P) return;
	if (HouseEvent(Id)) return;

	// ================================================================= act 1: arrival'''),
    # front door: knocking, and after it has shut behind him
    ('''				After(2.2f, [this]() { ShowTagged(TEXT("L_Welcome"), false); });
				float T = Say(TEXT("d_knock"), 0.9f);''', '''				float T = Say(TEXT("d_knock"), 0.9f);'''),
    ('''			else if (Has(TEXT("want_leave")) && !Has(TEXT("lockin_started")))
			{
				if (!Has(TEXT("door_stuck"))) { Set(TEXT("door_stuck")); Say(TEXT("d_doorstuck")); }
				else if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Think(TEXT("It will not open.")); }
			}''', '''			else if (Has(TEXT("locked_in")) && !Has(TEXT("door_stuck")))
			{
				// locked in, minutes after he walked through it
				Set(TEXT("door_stuck"));
				float T = Say(TEXT("d_doorstuck"));
				T = Say(TEXT("d_end1"), T + 1.0f);
				After(T, [this]() { Play2D(TEXT("radio_static"), 0.8f, EWCSnd::Voice); });
				After(T + 2.6f, [this]() { Think(TEXT("Nothing but static. It worked fine in the car.")); SetObjective(TEXT("Find Edith Harrow. Find another way out.")); Checkpoint(TEXT("locked_in")); });
			}'''),
    ('''			else if (Has(TEXT("want_leave")) && !Has(TEXT("lockin_started")) && Has(TEXT("door_stuck")) && Gate())
			{
				ScareLockIn();        // back in the front hall after finding the door stuck: now she comes
			}
			return;''', '''			return;'''),
    # the thump that calls him upstairs: only after a long quiet build-up
    ('''		&& !Has(TEXT("heard_upstairs")) && Has(TEXT("inside")) && Has(TEXT("seen_kitchen")) && Has(TEXT("seen_living")) && Has(TEXT("seen_dining"))
		&& (NotesRead.Num() >= 4 || PlaySeconds - InsideAt > 420.f * TestPace) && PlaySeconds - InsideAt > 150.f * TestPace)''',
     '''		&& !Has(TEXT("heard_upstairs")) && Has(TEXT("inside")) && !bBusy
		&& ((BuildStep >= 7 && PlaySeconds - InsideAt > 450.f * TestPace && NotesRead.Num() + LooksSeen.Num() >= 6) || PlaySeconds - InsideAt > 570.f * TestPace))'''),
    ('''	if ((Is(Id, TEXT("trig:t_kitchen")) || Is(Id, TEXT("trig:t_foyer")) || Is(Id, TEXT("trig:t_living")) || Is(Id, TEXT("trig:t_dining")) || Is(Id, TEXT("trig:t_sitting")))''',
     '''	if (Id.ToString().StartsWith(TEXT("trig:t_")) && P->GetActorLocation().Z < 250.f && P->GetActorLocation().Z > -50.f'''),
    ('''		if (Has(TEXT("heard_upstairs")) && !Has(TEXT("peek_started")) && UpstairsAt > 0.0 && Clock - UpstairsAt > 45.0 * TestPace) ScarePeek();''',
     '''		if (Has(TEXT("heard_upstairs")) && !Has(TEXT("peek_started")) && UpstairsAt > 0.0 && Clock - UpstairsAt > 12.0 * TestPace) ScarePeek();'''),
    # after the empty room: the radio dies; the front door is already shut
    ('''		After(T - 0.6f, [this]()
		{
			if (AWCDoor* D = Door(TEXT("front"))) { D->Slam(); D->SetLocked(true); }
		});
		T = Say(TEXT("d_radio2"), T + 0.9f);
		After(T, [this]() { SetObjective(TEXT("Go back to the cruiser and radio it in")); Set(TEXT("want_leave")); Checkpoint(TEXT("want_leave")); });
		return;''', '''		T = Say(TEXT("d_radio2"), T + 0.9f);
		After(T, [this]() { SetObjective(TEXT("Get out. Try the back door.")); Set(TEXT("want_leave")); Checkpoint(TEXT("want_leave")); });
		return;'''),
    ('''	if (Is(Id, TEXT("shot_her"))) { ++ShotsAtHer; return; }''', '''	if (Is(Id, TEXT("shot_her"))) { ++ShotsAtHer; return; }
	if (Is(Id, TEXT("trig:t_backhall")) && Has(TEXT("want_leave")) && !Has(TEXT("lockin_started")) && Gate()) { ScareLockIn(); return; }'''),
    ('''				float T = Say(TEXT("d_getup1"), 0.4f);
				if (ShotsAtHer > 0) T = Say(TEXT("d_getup1b"), T + 0.3f);
				T = Say(TEXT("d_wayout"), T + 0.8f);
				After(T, [this]() { SetObjective(TEXT("Find another way out")); Checkpoint(TEXT("lockin_done")); });''', '''				float T = Say(TEXT("d_getup1"), 0.4f);
				if (ShotsAtHer > 0)
				{
					T = Say(TEXT("d_getup1b"), T + 0.3f);
					After(T + 0.6f, [this]() { Think(TEXT("But she flinched. Every shot, she flinched.")); });
					T += 3.f;
				}
				After(T + 0.8f, [this]() { SetObjective(TEXT("Find another way out")); Checkpoint(TEXT("lockin_done")); });'''),
    ('''	if (Is(Id, TEXT("locked:back")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Think(TEXT("Nailed shut from the inside. Every board.")); }''', '''	if (Is(Id, TEXT("locked:back")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Think(TEXT("Nailed shut from the inside. Every board.")); }
		if (Has(TEXT("want_leave")) && !Has(TEXT("lockin_started")) && Gate()) { After(1.5f, [this]() { ScareLockIn(); }); return; }'''),
    ('''	if (Is(Id, TEXT("take:key_prayer"))) { SetObjective(TEXT("Upstairs: the locked room")); return; }''',
     '''	if (Is(Id, TEXT("take:key_prayer"))) { SetObjective(TEXT("Upstairs: the locked room")); return; }
	if (Is(Id, TEXT("unlock:up_ell"))) { Checkpoint(TEXT("ell")); return; }
	if (Is(Id, TEXT("closed:note_prayer")) && !Has(TEXT("placed"))) { SetObjective(TEXT("Find what was theirs, and something to cut with")); return; }'''),
    ('''		float T = Say(TEXT("d_ring"), 0.4f);
		Say(TEXT("m_whisper2"), T + 1.5f);
		After(T + 1.5f, [this]() { if (AWCCharacter* Pl = Player()) Pl->FlickerLight(1.2f, 0.7f); });
		return;''', '''		Think(TEXT("A wedding ring. W.H. to E.H., 1942."));
		After(1.5f, [this]() { if (AWCCharacter* Pl = Player()) Pl->FlickerLight(1.2f, 0.7f); });
		return;'''),
    ('''	if (Is(Id, TEXT("take:key_attic"))) { SetObjective(TEXT("The attic")); return; }
''', ''''''),
    ('''			if (Id == FName(*Use) && !Has(Flag) && !bBusy)
			{''', '''			if (Id == FName(*Use) && !Has(Flag) && !bBusy)
			{
				if (!HasItem(TEXT("shears")))
				{
					if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Think(TEXT("Nothing to cut it with. She said scissors. The sewing room.")); }
					return;
				}'''),
    # S3: she is at the far end of the long hall; the house goes dark; shots make her flinch, they do not stop her
    ('''	Set(TEXT("lockin_started"));
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S3_lockin"), PlaySeconds);
	ShotsAtHer = 0;''', '''	Set(TEXT("lockin_started"));
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S3_lockin"), PlaySeconds);
	ShotsAtHer = 0;
	Set(TEXT("power_out"));
	bPowerOut = true;
	KillLights(0.f, true);
	if (AWCCharacter* Pl = Player()) Pl->FlickerLight(0.8f, 0.8f);'''),
    ('''			// a hit only makes her skip closer
			const FVector Dir = (P->GetActorLocation() - H->GetActorLocation()).GetSafeNormal2D();
			H->SetActorLocation(H->GetActorLocation() + Dir * FMath::Min(110.f, FMath::Max(0.f, H->DistToPlayer() - 190.f)));
			P->FlickerLight(0.3f, 0.9f);''', '''			// she flinches from every shot, and keeps coming
			if (!bLockInRun)
			{
				H->StopMoving();
				H->Play(TEXT("Idle"));
				HerNextStep = Clock + 0.75;
				PlayAt(TEXT("her_flinch"), H->HeadLocation(), 1.f, 1.f, 3500.f);
			}
			P->FlickerLight(0.3f, 0.9f);'''),
    ('''			if (!bLockInRun && (H->DistToPlayer() < LockInDist0 * 0.52f || Elapsed > 26.0))''', '''			if (!bLockInRun && (H->DistToPlayer() < LockInDist0 * 0.52f || Elapsed > 30.0 || H->DistToPlayer() < 600.f))'''),
])
edit("WCStory.cpp", [('#include "Kismet/GameplayStatics.h"', '#include "Kismet/GameplayStatics.h"\n#include "Misc/CommandLine.h"')])
edit("WCCharacter.h", [("float WalkSpeed = 112.f;", "float WalkSpeed = 100.f;"), ("float SprintSpeed = 215.f;", "float SprintSpeed = 190.f;"), ("float CrouchSpeed = 70.f;", "float CrouchSpeed = 62.f;")])
edit("WCGame.cpp", [
    ('''{ TEXT("keep_daniel"), TEXT("Daniel's dog tags") } };''', '''{ TEXT("keep_daniel"), TEXT("Daniel's dog tags") }, { TEXT("key_desk"), TEXT("Small desk key") },
		{ TEXT("key_ell"), TEXT("Walter's keys (upstairs back rooms)") }, { TEXT("fuse"), TEXT("Spare fuse") }, { TEXT("shears"), TEXT("Sewing shears") } };'''),
    ('''for (const FName& It : D->Items) { Text(ItemName(It), Px(60.f), Y, Px(22.f), Ink); Y += Px(30.f); }''',
     '''for (const FName& It : D->Items) { if (It.ToString().StartsWith(TEXT("ammo"))) continue; Text(ItemName(It), Px(60.f), Y, Px(22.f), Ink); Y += Px(30.f); }'''),
    ('''TEXT("#Environment and props"), TEXT("Assets from Fab, used under the Fab Standard License"), TEXT(""),''',
     '''TEXT("#Sound"), TEXT("Sonniss GDC Game Audio Bundle"), TEXT("Kenney (CC0)"), TEXT(""),
		TEXT("#Environment and props"), TEXT("Assets from Fab, used under the Fab Standard License"), TEXT("Megascans and Megaplants by Quixel"), TEXT(""),'''),
])
print("ok")
