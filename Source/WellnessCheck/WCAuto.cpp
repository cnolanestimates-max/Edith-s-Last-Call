// Automatic play-through for testing (-WCAuto, optional -WCShots=<dir>, -WCAutoForce).
// It drives the real pawn: walks with movement input along nav paths, aims the camera, presses "use" through the
// same trace the player uses, raises and fires the pistol. It is a route check and evidence recorder, not a
// substitute for a person playing: it knows the solution and never gets lost.
#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"

#include "EngineUtils.h"
#include "AudioMixerBlueprintLibrary.h"
#include "Components/AudioComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "HAL/IConsoleManager.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Components/CapsuleComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Paths.h"
#include "NavigationPath.h"
#include "NavigationSystem.h"
#include "UnrealClient.h"

DEFINE_LOG_CATEGORY_STATIC(LogWCAuto, Log, All);

enum { A_Go, A_Use, A_Wait, A_WaitFlag, A_Shot, A_Fire, A_Look, A_Light, A_LookHer, A_WaitHer, A_Crouch, A_Tele, A_Her, A_FaceItem, A_Aim, A_Do };

void AWCDirector::AutoBegin()
{
	auto Go = [this](const TCHAR* T) { AutoSteps.Add({ A_Go, T, 0.f }); };
	auto Use = [this](const TCHAR* T) { AutoSteps.Add({ A_Go, T, 1.f }); AutoSteps.Add({ A_Use, T, 0.f }); };
	auto Wait = [this](float S) { AutoSteps.Add({ A_Wait, NAME_None, S }); };
	auto Flag = [this](const TCHAR* F, float Timeout = 60.f) { AutoSteps.Add({ A_WaitFlag, F, Timeout }); };
	auto Shot = [this](const TCHAR* N) { AutoSteps.Add({ A_Shot, N, 0.f }); };
	auto Look = [this](const TCHAR* T) { AutoSteps.Add({ A_Look, T, 0.f }); };
	auto LookHer = [this](float S) { AutoSteps.Add({ A_LookHer, NAME_None, S }); };
	auto WaitHer = [this](float Timeout) { AutoSteps.Add({ A_WaitHer, NAME_None, Timeout }); };
	auto Fire = [this](int32 N) { AutoSteps.Add({ A_Fire, NAME_None, (float)N }); };

	if (FParse::Param(FCommandLine::Get(), TEXT("WCListeningCheck")))
	{
		Steps.Reset();
		Fade = FadeTarget = 0.f;
		Player()->SetInputLocked(false);
		Set(TEXT("inside")); Set(TEXT("briefed"));
		auto Do = [this](const TCHAR* Cmd) { AutoSteps.Add({A_Do, Cmd, 0.f}); };
		Do(TEXT("at:380,82,94,0,0")); Wait(1.f);
		Do(TEXT("snicker_checkpoint")); Do(TEXT("at:680,83,94,0,0")); Wait(1.f);
		Flag(TEXT("heard_listening_snicker"), 100.f);
		Wait(.30f); Do(TEXT("snicker_turn")); Wait(2.4f); Do(TEXT("snicker_reload"));
		AutoIndex=0; AutoStepStart=Clock; return;
	}
	const bool bBedCheck = FParse::Param(FCommandLine::Get(), TEXT("WCUnderBedCheck"));
	if (bBedCheck || FParse::Param(FCommandLine::Get(), TEXT("WCHouseMixCheck")))
	{
		// An offscreen capture needs the focused game's mix, even with the window hidden.
		if (IConsoleVariable* V = IConsoleManager::Get().FindConsoleVariable(TEXT("au.DisableAppVolume")))
			V->Set(1, ECVF_SetByCode);
		Steps.Reset();
		Fade = FadeTarget = 0.f;
		Player()->SetInputLocked(false);
		Player()->SetFlashlight(true,false);
		AutoShotDir = FPaths::ConvertRelativePathToFull(AutoShotDir);
		IFileManager::Get().MakeDirectory(*AutoShotDir,true);
		auto Do = [this](const TCHAR* Cmd) { AutoSteps.Add({A_Do,Cmd,0.f}); };
		Set(TEXT("inside")); Set(TEXT("briefed"));
		if (bBedCheck)
		{
			Do(TEXT("at:489,-263,444,-15,-29")); Wait(.6f);
			if (FParse::Param(FCommandLine::Get(), TEXT("WCEnterCrouched")))
				AutoSteps.Add({ A_Crouch, NAME_None, 1.f });
			Wait(.6f); Do(TEXT("record_mix")); Do(TEXT("arm_bed_trigger"));
			for (int32 I=0; I<94; ++I)
			{
				AutoSteps.Add({A_Shot, FName(*FString::Printf(TEXT("bed_%03d"),I)), 0.f});
				Wait(.075f);
			}
			Do(TEXT("finish_bed_mix")); Do(TEXT("bed_result"));
			AutoSteps.Add({ A_Crouch, NAME_None, 1.f });
			Wait(.35f); Do(TEXT("at:638,-307,402,-90,-34"));
			AutoSteps.Add({ A_Look, TEXT("pick_keep_ruth"), -1.f });
			Wait(.5f); Do(TEXT("bed_pickup"));
		}
		else
		{
			Do(TEXT("at:182,71,94,0,-5")); Wait(4.f); Do(TEXT("mix_check"));
			Do(TEXT("record_mix")); Wait(2.f); Go(TEXT("N_hallB")); Wait(1.5f);
			Go(TEXT("A_Kitchen")); Wait(1.f); Do(TEXT("mix_check")); Go(TEXT("N_kitchen2")); Wait(2.f);
			Do(TEXT("finish_house_mix"));
			Do(TEXT("at:330,64,94,2,-6")); Wait(2.f);
			for (int32 I=0; I<18; ++I)
			{
				AutoSteps.Add({A_Shot, FName(*FString::Printf(TEXT("dust_%02d"),I)), 0.f});
				Wait(.12f);
			}
			Do(TEXT("dust_reference")); Wait(.3f); Shot(TEXT("without_dust")); Do(TEXT("dust_restore"));
			Do(TEXT("audition_haunts")); Wait(13.f); Do(TEXT("finish_haunts")); Wait(.6f);
		}
		AutoIndex=0; AutoStepStart=Clock; return;
	}
	if (FParse::Param(FCommandLine::Get(), TEXT("WCYardCrowCheck")))
	{
		Steps.Reset();
		Fade = FadeTarget = 0.f;
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		UGameplayStatics::SetGlobalTimeDilation(this, 5.f);
		auto Do = [this](const TCHAR* Cmd) { AutoSteps.Add({A_Do,Cmd,0.f}); };
		Do(TEXT("at:-1430,220,52,0,0")); Wait(16.f); Do(TEXT("crow_briefed")); Wait(240.f);
		Do(TEXT("crow_budget")); Do(TEXT("at:330,30,94,0,0")); Wait(3.f); Do(TEXT("crow_inside"));
		AutoIndex=0; AutoStepStart=Clock; return;
	}
	if (FParse::Param(FCommandLine::Get(), TEXT("WCRoomCheck")))
	{
		Steps.Reset();
		if (AWCCharacter* Pl = Player()) { Pl->SetInputLocked(false); Pl->SetFlashlight(true, false); }
		Fade = FadeTarget = 0.f;
		AutoShotDir = FPaths::ConvertRelativePathToFull(AutoShotDir);
		IFileManager::Get().MakeDirectory(*AutoShotDir, true);
		auto Do = [this](const TCHAR* Cmd) { AutoSteps.Add({A_Do, Cmd, 0.f}); };
		Do(TEXT("at:692,381,442,-90,-42")); AutoSteps.Add({A_Look,TEXT("pick_screwdriver"),-1.f});
		Wait(.5f); Do(TEXT("use_screwdriver_pickup"));
		Do(TEXT("at:851,419,92,82,-42")); AutoSteps.Add({A_Look,TEXT("phone"),-1.f});
		Wait(1.7f); Shot(TEXT("Telephone_flashlight")); Do(TEXT("room_use_phone"));
		Do(TEXT("at:980,-50,92,-42,-3")); Wait(57.f);
		AutoIndex=0; AutoStepStart=Clock; return;
	}
	if (FParse::Param(FCommandLine::Get(), TEXT("WCArrivalCheck")))
	{
		Steps.Reset();
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		Fade = FadeTarget = 0.f;
		AutoShotDir = FPaths::ConvertRelativePathToFull(AutoShotDir);
		IFileManager::Get().MakeDirectory(*AutoShotDir, true);
		auto Do = [this](const TCHAR* Cmd) { AutoSteps.Add({A_Do, Cmd, 0.f}); };
		Do(TEXT("check_yard_paths")); Do(TEXT("record_mix")); Do(TEXT("at:-535,-653,52,-38,-19")); Wait(2.f); Shot(TEXT("left_approach"));
		Do(TEXT("at:-280,992,52,0,-18")); Wait(1.f); Shot(TEXT("right_approach"));
		Do(TEXT("at:3770,-743,59,0,-27")); Wait(1.f); Do(TEXT("take_tape")); Wait(3.95f); Shot(TEXT("bin_turn")); Wait(1.65f);
		Do(TEXT("at:3066,-413,51,122,-35")); Wait(.7f); Shot(TEXT("flies_a")); Wait(.15f); Shot(TEXT("flies_b"));
		Do(TEXT("at:-90,0,94,0,0")); Wait(.6f); Do(TEXT("mix_check"));
		Do(TEXT("at:100,0,94,0,0")); Wait(.8f); Do(TEXT("mix_check"));
		Do(TEXT("at:-90,0,94,0,0")); Wait(.3f); Do(TEXT("mix_check"));
		Do(TEXT("at:330,30,94,0,0")); Wait(1.f); Do(TEXT("mix_check"));
		Do(TEXT("at:692,381,442,-90,-42")); AutoSteps.Add({A_Look,TEXT("pick_screwdriver"),-1.f}); Wait(.35f);
		Shot(TEXT("screwdriver_focus")); Do(TEXT("use_screwdriver_pickup")); Wait(1.f);
		Do(TEXT("finish_mix")); Wait(.5f);
		Do(TEXT("at:1400,310,92,-90,-12")); Do(TEXT("vent_test")); Wait(.7f); Shot(TEXT("vent_driver")); Wait(1.5f);
		Do(TEXT("return_key")); Wait(7.1f); Do(TEXT("at:960,96,442,174,-5")); Do(TEXT("switch_test")); Wait(.5f);
		Shot(TEXT("dark_landing")); Do(TEXT("at:475,114,442,163,-1")); Wait(.16f); Shot(TEXT("doorway_glimpse")); Wait(1.5f);
		Do(TEXT("at:716,373,442,-90,-40")); Do(TEXT("box_test")); Wait(1.2f); Shot(TEXT("jewelry_box")); Wait(.3f);
		Use(TEXT("pick_keep_eye"));
		Do(TEXT("haunt_test")); Wait(.3f); Do(TEXT("light_test")); Wait(.3f);
		Do(TEXT("ceiling_music_test")); Wait(8.4f);
		AutoIndex=0; AutoStepStart=Clock; return;
	}
	if (FParse::Param(FCommandLine::Get(), TEXT("WCTour")))
	{
		// screenshot tour: stand at every point tagged "Tour" with the flashlight on
		TArray<FName> Names;
		for (TActorIterator<AActor> It(GetWorld()); It; ++It)
		{
			if (!It->ActorHasTag(TEXT("Tour"))) continue;
			for (const FName& T : It->Tags) if (T != TEXT("Tour")) Names.Add(T);
		}
		Names.Sort([](const FName& A, const FName& B) { return A.ToString() < B.ToString(); });
		Steps.Reset();
		Subtitles.Reset();
		if (AWCCharacter* Pl = Player()) { Pl->SetInputLocked(false); Pl->SetFlashlight(true, false); }
		Fade = 0.f; FadeTarget = 0.f;
		const bool Props = FParse::Param(FCommandLine::Get(), TEXT("WCPropReview"));
		if (FParse::Param(FCommandLine::Get(), TEXT("WCBright")))
		{
			if (AWCCharacter* Pl = Player())
			{
				UPointLightComponent* L = NewObject<UPointLightComponent>(Pl);
				L->ComponentTags.Add(TEXT("PropReviewLight"));
				L->SetupAttachment(Pl->GetRootComponent());
				L->SetRelativeLocation(FVector(0, 0, 60));
				L->RegisterComponent();
				L->SetIntensityUnits(ELightUnits::Lumens);
				L->SetIntensity(Props ? 14000.f : 1800.f);
				L->SetAttenuationRadius(2500.f);
				L->SetCastShadows(false);
			}
		}
		if (FParse::Param(FCommandLine::Get(), TEXT("WCLights")))
		{
			for (TPair<FName, FRoomLights>& Rm : Rooms) SwitchRoom(Rm.Key, true, false);
			if (AWCCharacter* Pl = Player()) Pl->SetFlashlight(false, false);
		}
		if (Props) bBusy = true;
		Wait(3.f);
		for (const FName& N : Names)
		{
			if (Props && N == TEXT("Tour_31_master")) AutoSteps.Add({ A_Do, TEXT("at:362,302,442,18,-12"), 0.f });
			else AutoSteps.Add({ A_Tele, N, 0.f });
			Wait(Props ? 1.f : 2.6f);
			Shot(*N.ToString());
		}
		if (Props)
		{
			auto Photo = [&](const TCHAR* Stand,const TCHAR* Name) { AutoSteps.Add({A_Do,Stand,0.f}); Wait(1.f); Shot(Name); };
			Photo(TEXT("at:1261,524,92,-94,-57"),TEXT("Detail_Kitchen_drawing"));
			Photo(TEXT("at:1440,324,92,-111,-15"),TEXT("Detail_Kitchen_vent"));
			Photo(TEXT("at:208,219,442,87,-24"),TEXT("Detail_Master_entry"));
			Photo(TEXT("at:702,400,442,-88,-36"),TEXT("Detail_Master_jewelry"));
			Photo(TEXT("at:515,-376,92,-150,-4"),TEXT("Detail_Living_seating"));
			Photo(TEXT("at:556,-340,92,145,-3"),TEXT("Detail_Living_shelves"));
			Photo(TEXT("at:3695,-743,59,0,-12"),TEXT("Detail_Shed_workbench"));
			Photo(TEXT("at:3270,-535,60,145,-15"),TEXT("Detail_Back_yard_bin"));
			Photo(TEXT("at:268,-30,92,7,12"),TEXT("Detail_Foyer_stairs"));
			AutoSteps.Add({A_Do,TEXT("detail_lens"),0.f});
			Photo(TEXT("at:852,419,92,83,-44"),TEXT("Detail_Kitchen_phone"));
			AutoSteps.Add({A_Do,TEXT("normal_lens"),0.f});
			Photo(TEXT("at:1924,-440,92,-97,-38"),TEXT("Detail_Den_letters"));
			Photo(TEXT("at:1917,426,92,84,-14"),TEXT("Detail_Pantry_jars"));
			AutoSteps.Add({A_Do,TEXT("at:490,-105,198,-53,-32"),0.f}); Wait(.5f);
			AutoSteps.Add({A_Look,TEXT("W_book_eye"),-1.f}); Wait(.5f); Shot(TEXT("Detail_Stair_opening"));
		}
		AutoIndex = 0;
		AutoStepStart = Clock;
		if (!AutoShotDir.IsEmpty()) { AutoShotDir = FPaths::ConvertRelativePathToFull(AutoShotDir); IFileManager::Get().MakeDirectory(*AutoShotDir, true); }
		UE_LOG(LogWCAuto, Display, TEXT("WCAUTO tour, %d points"), Names.Num());
		return;
	}
	if (FParse::Param(FCommandLine::Get(), TEXT("WCHerLook")) || FParse::Param(FCommandLine::Get(), TEXT("WCItems")))
	{
		Steps.Reset();
		Subtitles.Reset();
		Set(TEXT("heard_upstairs")); Set(TEXT("peek_started")); Set(TEXT("peek_done")); Set(TEXT("briefed"));
		NotesRead.AddUnique(TEXT("note_deskkey"));
		bBusy = true;                      // no story triggers during the test
		if (AWCCharacter* Pl = Player()) { Pl->SetInputLocked(false); Pl->SetFlashlight(true, false); }
		Fade = 0.f; FadeTarget = 0.f;
		SwitchRoom(TEXT("hall"), true, false);
		Wait(4.f);
		if (FParse::Param(FCommandLine::Get(), TEXT("WCAlbumShots")))
		{
			auto Frame = [&](const TCHAR* At, const TCHAR* Name)
			{
				AutoSteps.Add({ A_Do, At, 0.f }); Wait(1.4f); Shot(Name);
			};
			Frame(TEXT("at:1400,20,92,90,11"), TEXT("01_porch"));
			Frame(TEXT("at:1250,-36,92,-90,14"), TEXT("02_scratched"));
			Frame(TEXT("at:250,-556,92,-90,18"), TEXT("03_claw_frame"));
			Frame(TEXT("at:1300,-38,442,-90,10"), TEXT("04_silver_anniversary"));
			Frame(TEXT("at:2000,-38,442,-90,10"), TEXT("05_edith_garden"));
			Frame(TEXT("at:2200,-420,92,-90,28"), TEXT("06_walter"));
			Frame(TEXT("at:1890,68,92,83,-58"), TEXT("07_fallen"));
			Wait(1.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCBeamShots")))
		{
			AutoSteps.Add({ A_Do, TEXT("at:3760,-720,59,-90,-6"), 0.f });
			UE_LOG(LogWCAuto, Display, TEXT("WCBEAM selected %s"), *Settings.BeamLabel());
			Wait(1.5f); Shot(TEXT("beam_selected"));
			for (int32 Choice = 0; Choice < FWCSettings::BeamChoices; ++Choice)
			{
				AutoSteps.Add({ A_Do, TEXT("beam"), static_cast<float>(Choice) });
				Wait(1.5f);
				Shot(*FString::Printf(TEXT("beam_%c"), 'A' + Choice));
			}
			AutoSteps.Add({ A_Do, TEXT("at:548,-288,92,90,-3"), 0.f });
			Wait(1.f);
			AutoSteps.Add({ A_Do, TEXT("check_book_focus"), 0.f });
			Shot(TEXT("living_book"));
			AutoSteps.Add({ A_Do, TEXT("at:220,-307,92,-65,-7"), 0.f });
			Wait(1.f); Shot(TEXT("living_room")); Wait(1.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCSmokeOnly")))
		{
			AutoSteps.Add({ A_Tele, TEXT("A_UpEll"), 0.f }); Wait(1.0f); AutoSteps.Add({ A_Look, TEXT("W_company_uprear"), -1.f }); Wait(0.15f); Shot(TEXT("smoke_1_hall_far"));
			AutoSteps.Add({ A_Do, TEXT("at:2330,10,442,0,4"), 0.f }); Wait(0.25f); Shot(TEXT("smoke_2_hall_near")); Wait(0.5f); Shot(TEXT("smoke_3_hall_near_later"));
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCOutsideOnly")))
		{
			AutoSteps.Add({ A_Do, TEXT("filter:0"), 0.f });
			AutoSteps.Add({ A_Do, TEXT("at:2950,-800,52,3,2"), 0.f }); Wait(1.5f); Shot(TEXT("out_1_side_of_house_to_shed"));
			AutoSteps.Add({ A_Tele, TEXT("A_Shed"), 0.f }); Wait(1.0f); AutoSteps.Add({ A_Look, TEXT("A_ShedIn"), 0.f }); Wait(0.6f); Shot(TEXT("out_2_shed_door"));
			AutoSteps.Add({ A_Do, TEXT("at:3760,-720,59,-90,-6"), 0.f }); Wait(1.0f); Shot(TEXT("out_3_shed_tools_wall"));
			AutoSteps.Add({ A_Do, TEXT("at:3700,-740,59,0,-10"), 0.f }); Wait(0.8f); Shot(TEXT("out_4_shed_bench"));
			AutoSteps.Add({ A_Do, TEXT("at:3740,-770,59,90,2"), 0.f }); Wait(0.8f); Shot(TEXT("out_5_shed_shelf"));
			AutoSteps.Add({ A_Do, TEXT("at:3470,-745,52,168,7"), 0.f }); Wait(1.0f); Shot(TEXT("out_6_turn_round_house_from_the_back"));
			AutoSteps.Add({ A_Do, TEXT("at:3180,0,60,180,2"), 0.f }); Wait(1.0f); Shot(TEXT("out_7_back_door"));
			AutoSteps.Add({ A_Do, TEXT("at:3900,300,52,20,4"), 0.f }); Wait(1.0f); Shot(TEXT("out_8_back_fence_and_trees"));
			AutoSteps.Add({ A_Do, TEXT("at:1400,-900,52,0,3"), 0.f }); Wait(1.0f); Shot(TEXT("out_9_left_side_yard"));
			AutoSteps.Add({ A_Do, TEXT("filter:1"), 0.f }); AutoSteps.Add({ A_Do, TEXT("at:3470,-745,52,168,7"), 0.f }); Wait(1.0f); Shot(TEXT("out_10_house_from_the_back_vhs"));
			Wait(1.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCFilterShots")))
		{
			Set(TEXT("inside")); Set(TEXT("locked_in")); Set(TEXT("tv_first")); Set(TEXT("tv_test"));
			static const TCHAR* Names[6] = { TEXT("0_off"), TEXT("1_vhs"), TEXT("2_oldfilm"), TEXT("3_cold"), TEXT("4_bodycam"), TEXT("5_nightvision") };
			static FString Keep[40];
			int32 KeepN = 0;
			auto Looks = [&](const TCHAR* Spot)
			{
				for (int32 L = 0; L < 6; ++L)
				{
					AutoSteps.Add({ A_Do, FName(*FString::Printf(TEXT("filter:%d"), L)), 0.f }); Wait(0.45f);
					Keep[KeepN] = FString::Printf(TEXT("%s_%s"), Spot, Names[L]);
					AutoSteps.Add({ A_Shot, FName(*Keep[KeepN]), 0.f }); ++KeepN;
				}
				AutoSteps.Add({ A_Do, TEXT("filter:0"), 0.f });
			};
			// 1 the front hall with its lamp on   2 the television playing   3 Edith in the hall   4 the house from the yard
			AutoSteps.Add({ A_Do, TEXT("at:230,40,92,0,-2"), 0.f }); Wait(1.2f); Looks(TEXT("a_hall"));
			AutoSteps.Add({ A_Do, TEXT("at:366,-550,92,-90,-14"), 0.f }); Wait(0.4f); AutoSteps.Add({ A_Do, TEXT("tvon"), 0.f }); Wait(6.5f); Looks(TEXT("b_television"));
			AutoSteps.Add({ A_Do, TEXT("at:1500,0,92,180,6"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Her, TEXT("Idle"), 300.f }); Wait(0.8f); Looks(TEXT("c_edith"));
			AutoSteps.Add({ A_Do, TEXT("at:-1500,60,144,0,8"), 0.f }); Wait(1.5f); Looks(TEXT("d_house"));
			Wait(1.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCFaceOnly")))
		{
			// every face she can make, close, by his own flashlight
			Set(TEXT("inside")); Set(TEXT("locked_in")); Set(TEXT("tv_first"));
			AutoSteps.Add({ A_Do, TEXT("at:1500,0,92,180,10"), 0.f }); Wait(0.8f);
			AutoSteps.Add({ A_Her, TEXT("Idle"), 115.f }); Wait(0.5f); AutoSteps.Add({ A_LookHer, NAME_None, 0.8f });
			static const TCHAR* Ms[] = { TEXT("rest"), TEXT("watch"), TEXT("grin"), TEXT("snarl"), TEXT("rage"), TEXT("wince"), TEXT("grief"), TEXT("hush"), TEXT("scream") };
			for (const TCHAR* M : Ms)
			{
				AutoSteps.Add({ A_Do, FName(*FString::Printf(TEXT("mood:%s"), M)), 0.f }); Wait(0.9f); AutoSteps.Add({ A_LookHer, NAME_None, 0.2f }); Shot(*FString::Printf(TEXT("face_%s"), M));
			}
			AutoSteps.Add({ A_Do, TEXT("mood:watch"), 0.f }); Wait(0.6f);
			AutoSteps.Add({ A_Her, TEXT("Idle"), 230.f }); Wait(0.6f); AutoSteps.Add({ A_LookHer, NAME_None, 0.6f });
			AutoSteps.Add({ A_Do, TEXT("mood:scream"), 0.f }); Wait(0.9f); Shot(TEXT("face_scream_from_2m"));
			AutoSteps.Add({ A_Do, TEXT("mood:grin"), 0.f }); Wait(0.9f); Shot(TEXT("face_grin_from_2m"));
			Wait(1.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCSpotOnly")))
		{

			Set(TEXT("inside")); Set(TEXT("locked_in")); Set(TEXT("tv_first"));
			auto At = [this](const TCHAR* S) { AutoSteps.Add({ A_Do, S, 0.f }); };
			At(TEXT("at:1400,335,92,-90,-4")); Wait(1.2f); Shot(TEXT("spot_1_vent_shut"));
			At(TEXT("at:1400,300,92,-90,-8")); Wait(0.8f); Shot(TEXT("spot_1b_vent_shut_close"));
			At(TEXT("flag:vent_open")); Wait(0.8f); Shot(TEXT("spot_2_vent_open_doll"));
			At(TEXT("at:1400,335,92,-90,-14")); Wait(0.8f); Shot(TEXT("spot_2b_vent_open_from_further"));
			At(TEXT("at:625,330,442,-20,-28")); Wait(1.2f); Shot(TEXT("spot_3_jewelry_box_and_screwdriver"));
			At(TEXT("flag:box_open")); Wait(0.8f); Shot(TEXT("spot_4_box_open_letter_eye"));
			At(TEXT("flag:phone_done")); At(TEXT("at:1380,-372,442,90,-24")); Wait(1.2f); Shot(TEXT("spot_5_drawer_key_upstairs_bath"));
			At(TEXT("at:1130,-312,92,143,-26")); Wait(1.2f); Shot(TEXT("spot_6_fuse_in_sitting_room"));
			At(TEXT("flag:desk_open")); At(TEXT("at:2222,-300,92,-31,-24")); Wait(1.2f); Shot(TEXT("spot_7_desk_open_keys_cartridges"));
			At(TEXT("at:2215,-352,92,0,-22")); Wait(0.8f); Shot(TEXT("spot_7b_desk_from_the_front"));
			At(TEXT("at:640,-330,92,128,2")); Wait(1.2f); Shot(TEXT("spot_8_bookcase"));
			At(TEXT("at:592,-296,92,124,0")); Wait(1.0f); Shot(TEXT("spot_8b_at_the_book"));
			At(TEXT("at:3790,-745,59,-22,-28")); Wait(1.2f); Shot(TEXT("spot_10_shed_tape_on_bench"));
			At(TEXT("at:3580,-745,59,149,-4")); Wait(1.0f); Shot(TEXT("spot_11_trash_can_standing"));
			At(TEXT("flag:tape1_taken")); Wait(0.8f); Shot(TEXT("spot_11b_trash_can_over"));
			At(TEXT("at:3140,-470,59,140,-18")); Wait(1.0f); Shot(TEXT("spot_11c_trash_close"));
			At(TEXT("at:366,-520,92,-90,-24")); Wait(1.2f); Shot(TEXT("spot_12_television_with_tape_slot"));
			At(TEXT("at:1500,0,92,180,4")); Wait(0.6f); AutoSteps.Add({ A_Her, TEXT("Idle"), 300.f }); Wait(0.9f); Shot(TEXT("spot_15_edith_skin_3m"));
			AutoSteps.Add({ A_Her, TEXT("Idle"), 170.f }); Wait(0.9f); Shot(TEXT("spot_15b_edith_skin_close"));
			At(TEXT("at:820,60,92,151,-4")); Wait(1.0f); Shot(TEXT("spot_13_frame_on_the_wall"));
			At(TEXT("flag:frame_fell")); Wait(0.8f); Shot(TEXT("spot_13b_frame_fallen"));
			At(TEXT("at:1320,470,92,-70,-6")); Wait(1.0f); Shot(TEXT("spot_14_kitchen_sink_side"));
			At(TEXT("at:572,-292,92,112,-9")); Wait(1.0f);            // a little off to one side and looking down: the game has to bring his eyes to the gap
			At(TEXT("book")); Wait(0.55f); Shot(TEXT("spot_9_book_coming_out")); Wait(0.75f); Shot(TEXT("spot_9b_her_eye")); Wait(0.8f); Shot(TEXT("spot_9c_her_eye_still")); Wait(2.6f); Shot(TEXT("spot_9d_after"));
			Wait(2.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCPeekOnly")))
		{
			// the first sight of her, from the stairs (nothing), from half way (nothing or next to nothing), and close (gone)
			Set(TEXT("inside")); Set(TEXT("locked_in")); Set(TEXT("heard_upstairs")); Set(TEXT("tv_first"));
			// the look test marks the peek as already over so the story leaves it alone: this test is the peek, so put it back
			Flags.Remove(TEXT("peek_started")); Flags.Remove(TEXT("peek_done")); bBusy = false;
			AutoSteps.Add({ A_Tele, TEXT("A_StairsTop"), 0.f }); Wait(1.0f);
			AutoSteps.Add({ A_Do, TEXT("peek"), 0.f }); Wait(1.2f);
			AutoSteps.Add({ A_Do, TEXT("at:900,60,442,174,2"), 0.f }); Wait(1.0f); Shot(TEXT("peek_1_from_the_stairs"));
			AutoSteps.Add({ A_Do, TEXT("at:640,80,442,165,4"), 0.f }); Wait(1.0f); Shot(TEXT("peek_2_from_4m"));
			AutoSteps.Add({ A_Do, TEXT("at:520,90,442,160,5"), 0.f }); Wait(0.12f); Shot(TEXT("peek_3_from_3m_first_instant")); Wait(0.35f); Shot(TEXT("peek_4_sliding_away")); Wait(1.2f); Shot(TEXT("peek_5_gone"));
			Wait(3.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCEyeOnly")))
		{
			Set(TEXT("locked_in")); Set(TEXT("peek_done")); Set(TEXT("lockin_done")); Set(TEXT("tv_first"));
			AutoSteps.Add({ A_Do, TEXT("at:2600,0,92,180,0"), 0.f }); Wait(1.5f); Shot(TEXT("eye_0_hall_before"));
			AutoSteps.Add({ A_Do, TEXT("eye"), 0.f }); Wait(1.8f); Shot(TEXT("eye_1_black"));
			Wait(3.2f); Shot(TEXT("eye_2_the_eye")); Wait(1.6f); Shot(TEXT("eye_2b_the_eye"));
			Wait(2.4f); Shot(TEXT("eye_3_light_back_nothing")); Wait(1.2f);
			AutoSteps.Add({ A_Do, TEXT("at:2600,0,92,146,-8"), 0.f }); Wait(1.6f); Shot(TEXT("eye_4_light_away_eye_back")); Wait(1.0f); Shot(TEXT("eye_4b_still_there"));
			AutoSteps.Add({ A_Do, TEXT("at:2600,0,92,180,0"), 0.f }); Wait(0.7f); Shot(TEXT("eye_5_gone")); Wait(4.0f); Shot(TEXT("eye_6_after"));
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCTVOnly")))
		{
			Set(TEXT("locked_in")); Set(TEXT("tv_first")); Set(TEXT("tv_test"));
			AutoSteps.Add({ A_Tele, TEXT("A_Living"), 0.f }); Wait(1.0f); AutoSteps.Add({ A_Look, TEXT("tv"), 0.f }); Wait(0.5f); Shot(TEXT("tv_0_off"));
			AutoSteps.Add({ A_Do, TEXT("tvon"), 0.f }); Wait(1.6f); Shot(TEXT("tv_1_title")); Wait(3.0f); Shot(TEXT("tv_2_playing")); Wait(3.0f); Shot(TEXT("tv_3_playing"));
			AutoSteps.Add({ A_Do, TEXT("tvgain:90"), 0.f }); Wait(0.5f); Shot(TEXT("tv_3b_gain90"));
			AutoSteps.Add({ A_Do, TEXT("tvgain:1000"), 0.f }); Wait(0.5f); Shot(TEXT("tv_3c_gain1000"));
			AutoSteps.Add({ A_Do, TEXT("tvgain:420"), 0.f });
			AutoSteps.Add({ A_Do, TEXT("at:250,-215,92,-70,-10"), 0.f }); Wait(1.2f); Shot(TEXT("tv_4_room_lit_by_it"));
			AutoSteps.Add({ A_Do, TEXT("at:366,-570,92,-90,-8"), 0.f }); Wait(0.5f); AutoSteps.Add({ A_Crouch, NAME_None, 1.f }); Wait(0.8f);
			AutoSteps.Add({ A_Look, TEXT("tv"), 0.f }); Wait(0.6f); Shot(TEXT("tv_4b_crouched_at_the_set"));
			if (FParse::Param(FCommandLine::Get(), TEXT("WCTVDebug"))) { AutoSteps.Add({ A_Do, TEXT("at:372,-620,92,97,4"), 0.f }); Wait(0.5f); }
			AutoSteps.Add({ A_Do, TEXT("tvoff"), 0.f }); Wait(0.9f); Shot(TEXT("tv_5_dead_glass")); Wait(5.0f); Shot(TEXT("tv_6_after")); Wait(2.0f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCCarOnly")))
		{
			static const TCHAR* Views[][2] = {
				{ TEXT("at:-1180,60,52,141,-6"), TEXT("car_1_front_quarter") }, { TEXT("at:-1480,-60,52,90,-6"), TEXT("car_2_side") },
				{ TEXT("at:-1800,520,52,-35,-6"), TEXT("car_3_rear_quarter") }, { TEXT("at:-1250,560,110,-131,-14"), TEXT("car_4_high_quarter") },
				{ TEXT("at:-1130,300,52,180,-4"), TEXT("car_5_front") } };
			for (const auto& Vw : Views) { AutoSteps.Add({ A_Do, Vw[0], 0.f }); Wait(1.2f); Shot(Vw[1]); }
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCStairOnly")))
		{
			if (AWCDoor* Cd = Door(TEXT("cellar"))) { Cd->SetLocked(false); Cd->SetOpen(true, 0.1f, true); }
			if (AWCDoor* Ad = Door(TEXT("up_attic"))) { Ad->SetLocked(false); Ad->SetOpen(true, 0.1f, true); }
			static const TCHAR* Views[][2] = {
				{ TEXT("at:150,-88,-258,0,8"), TEXT("view_01_cellar_hall_to_stairs") }, { TEXT("at:440,-88,-225,0,30"), TEXT("view_02_cellar_flight_foot_up") },
				{ TEXT("at:600,-88,-83,0,22"), TEXT("view_03_cellar_flight_mid_up") }, { TEXT("at:770,-88,62,180,-34"), TEXT("view_04_cellar_flight_top_down") },
				{ TEXT("at:930,70,92,-133,-4"), TEXT("view_05_hall_to_cellar_door") }, { TEXT("at:330,-88,92,0,24"), TEXT("view_06_main_flight_foot_up") },
				{ TEXT("at:600,-88,267,0,22"), TEXT("view_07_main_flight_mid_up") }, { TEXT("at:770,-88,412,180,-34"), TEXT("view_08_main_flight_top_down") },
				{ TEXT("at:330,-88,442,0,24"), TEXT("view_09_attic_flight_foot_up") }, { TEXT("at:600,-88,617,0,22"), TEXT("view_10_attic_flight_mid_up") },
				{ TEXT("at:770,-88,762,180,-34"), TEXT("view_11_attic_flight_top_down") }, { TEXT("at:1040,120,792,-140,-22"), TEXT("view_12_attic_to_stair_opening") },
				{ TEXT("at:600,-88,442,0,60"), TEXT("view_13_upstairs_in_well_look_up") }, { TEXT("at:600,-88,-258,0,60"), TEXT("view_14_cellar_in_well_look_up") } };
			for (const auto& Vw : Views) { AutoSteps.Add({ A_Do, Vw[0], 0.f }); Wait(0.9f); Shot(Vw[1]); }
			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f }); Wait(1.5f);
			AutoSteps.Add({ A_Go, TEXT("N_up_land"), 0.f }); Shot(TEXT("stairs_1_up_landing"));
			AutoSteps.Add({ A_Go, TEXT("N_attic_top"), 0.f }); Shot(TEXT("stairs_2_attic_top"));
			AutoSteps.Add({ A_Go, TEXT("N_c_bot"), 0.f }); Shot(TEXT("stairs_3_cellar_foot"));
			AutoSteps.Add({ A_Go, TEXT("A_Foyer"), 0.f }); Shot(TEXT("stairs_4_back_in_foyer")); Wait(1.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCGrabOnly")))
		{
			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f }); Wait(1.0f); AutoSteps.Add({ A_Her, TEXT("Idle"), 400.f }); Wait(0.5f);
			AutoSteps.Add({ A_Do, TEXT("grab"), 0.f }); Wait(0.75f); Shot(TEXT("grab_face_1")); Wait(0.45f); Shot(TEXT("grab_face_2")); Wait(2.5f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCHerLook")))
		{
			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f });
			Wait(1.f);
			static const TCHAR* Clips[] = { TEXT("Idle"), TEXT("Walk"), TEXT("Run"), TEXT("Tall"), TEXT("Peek"), TEXT("Crawl"), TEXT("Sit") };
			for (const TCHAR* Cn : Clips)
			{
				AutoSteps.Add({ A_Her, Cn, 330.f });
				Wait(0.8f); AutoSteps.Add({ A_LookHer, NAME_None, 0.3f }); Shot(*FString::Printf(TEXT("her_%s_a"), Cn));
				Wait(0.35f); Shot(*FString::Printf(TEXT("her_%s_b"), Cn));
			}
			AutoSteps.Add({ A_Her, TEXT("Idle"), 105.f });
			Wait(0.8f); AutoSteps.Add({ A_LookHer, NAME_None, 0.6f }); Shot(TEXT("her_face_close"));
			AutoSteps.Add({ A_Her, TEXT("Tall"), 150.f });
			Wait(0.8f); AutoSteps.Add({ A_LookHer, NAME_None, 0.6f }); Shot(TEXT("her_tall_close"));
			AutoSteps.Add({ A_Her, TEXT("Run"), 135.f });
			Wait(0.9f); AutoSteps.Add({ A_LookHer, NAME_None, 0.5f }); Shot(TEXT("her_scream_close"));
			AutoSteps.Add({ A_Her, TEXT("Lunge"), 240.f });
			Wait(0.5f); AutoSteps.Add({ A_LookHer, NAME_None, 0.2f }); Shot(TEXT("her_scream_mid"));
			AutoSteps.Add({ A_Her, TEXT("Idle"), 420.f });
			AutoSteps.Add({ A_Aim, NAME_None, 1.f }); Wait(1.4f); Shot(TEXT("gun_up"));
			AutoSteps.Add({ A_Look, TEXT("A_Living"), 0.f }); Wait(0.4f); Shot(TEXT("gun_up_turn"));
			AutoSteps.Add({ A_Aim, NAME_None, 0.f }); Wait(0.8f); Shot(TEXT("gun_down_hand"));
			// she was there the whole time
			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Her, TEXT("Idle"), 3000.f }); AutoSteps.Add({ A_Look, TEXT("W_hall_stair"), -1.f }); Wait(0.3f); Shot(TEXT("watch_hall_eye"));
			AutoSteps.Add({ A_Tele, TEXT("A_Kitchen"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("W_kitchen_fridge"), -1.f }); Wait(0.3f); Shot(TEXT("watch_kitchen_eye"));
			AutoSteps.Add({ A_Tele, TEXT("A_Living"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("W_fireplace"), -1.f }); Wait(0.3f); Shot(TEXT("watch_fireplace_eye"));
			AutoSteps.Add({ A_Tele, TEXT("A_Sitting"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("W_hair_sitting"), -1.f }); Wait(0.3f); Shot(TEXT("watch_hair_sitting"));
			AutoSteps.Add({ A_Tele, TEXT("N_hallF"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("W_hair_backhall"), -1.f }); Wait(0.3f); Shot(TEXT("watch_hair_hall"));
			AutoSteps.Add({ A_Tele, TEXT("N_den_shelf"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("SettlersBook"), -1.f }); Wait(0.3f); Shot(TEXT("book_before"));
			AutoSteps.Add({ A_Use, TEXT("book_settlers"), 0.f }); Wait(0.7f); Shot(TEXT("book_eye")); Wait(0.5f); Shot(TEXT("book_eye2")); Wait(2.4f); Shot(TEXT("book_after"));
			AutoSteps.Add({ A_Tele, TEXT("Tour_00_yard"), 0.f }); Wait(1.5f); AutoSteps.Add({ A_Look, TEXT("A_Cruiser"), 0.f }); Wait(1.f); Shot(TEXT("cruiser"));
			// the Company, her drawings, the hand under the bed, the three memories
			AutoSteps.Add({ A_Her, TEXT("Idle"), 3000.f });
			AutoSteps.Add({ A_Tele, TEXT("A_UpEll"), 0.f }); Wait(0.8f); AutoSteps.Add({ A_Look, TEXT("W_company_uprear"), -1.f }); Wait(0.2f); Shot(TEXT("company_uprear"));
			AutoSteps.Add({ A_Tele, TEXT("A_Sitting"), 0.f }); Wait(0.8f); AutoSteps.Add({ A_Do, TEXT("drawings"), 0.f }); Wait(0.8f); Shot(TEXT("drawings_wall"));
			AutoSteps.Add({ A_Tele, TEXT("A_Kids"), 0.f }); Wait(1.0f); AutoSteps.Add({ A_Do, TEXT("s7"), 0.f });
			Wait(3.6f); Shot(TEXT("hand_1_coming")); Wait(1.7f); Shot(TEXT("hand_2_on_box")); Wait(1.6f); Shot(TEXT("hand_3_taking")); Wait(3.6f);
			AutoSteps.Add({ A_Crouch, NAME_None, 1.f }); AutoSteps.Add({ A_Look, TEXT("pick_keep_ruth"), -1.f }); Wait(0.3f); Shot(TEXT("hand_4_box_under_bed")); AutoSteps.Add({ A_Crouch, NAME_None, 0.f });
			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f }); Wait(1.0f); AutoSteps.Add({ A_Her, TEXT("Idle"), 400.f }); Wait(0.5f);
			AutoSteps.Add({ A_Do, TEXT("grab"), 0.f }); Wait(0.75f); Shot(TEXT("grab_face_1")); Wait(0.45f); Shot(TEXT("grab_face_2")); Wait(3.f);
			AutoSteps.Add({ A_Do, TEXT("mem1"), 0.f }); Wait(10.5f);
			AutoSteps.Add({ A_Do, TEXT("mem2"), 0.f }); Wait(10.5f);
			AutoSteps.Add({ A_Do, TEXT("mem3"), 0.f }); Wait(10.5f);
		}
		else
		{
			TArray<FName> Ids;
			for (TActorIterator<AWCInteractable> It(GetWorld()); It; ++It) if (!It->WCId.IsNone() && !It->IsA(AWCDoor::StaticClass())) Ids.Add(It->WCId);
			Ids.Sort([](const FName& A, const FName& B) { return A.ToString() < B.ToString(); });
			for (const FName& Id : Ids) { AutoSteps.Add({ A_FaceItem, Id, 0.f }); Wait(1.3f); Shot(*FString::Printf(TEXT("item_%s"), *Id.ToString())); }
		}
		AutoIndex = 0;
		AutoStepStart = Clock;
		if (!AutoShotDir.IsEmpty()) { AutoShotDir = FPaths::ConvertRelativePathToFull(AutoShotDir); IFileManager::Get().MakeDirectory(*AutoShotDir, true); }
		return;
	}
	auto Close = [this]() { AutoSteps.Add({ A_Use, TEXT("__close"), 0.f }); };
	const float Slow = 1.f / FMath::Max(TestPace, 0.05f) > 2.f ? 1.f : 12.f;       // real pacing needs real patience
	// ---- arrival (the drive, when it is on, ends by setting "briefed")
	Flag(TEXT("briefed"), 150.f);
	Wait(2.f); AutoSteps.Add({ A_Light, NAME_None, 0.f });
	Look(TEXT("FrontDoorPoint")); Wait(1.f); Shot(TEXT("01_arrival"));
	Go(TEXT("A_Porch")); Shot(TEXT("02_porch"));
	if (FParse::Param(FCommandLine::Get(), TEXT("WCOutside")))
	{
		Use(TEXT("front")); Flag(TEXT("knocked_first"), 10.f); Wait(14.f); Shot(TEXT("02b_no_answer"));
		AutoSteps.Add({ A_Do, TEXT("at:3230,-560,59,146,-8"), 0.f }); Wait(2.f); Shot(TEXT("02b2_bin_full_upright"));
		AutoSteps.Add({ A_Do, TEXT("at:3030,-420,59,150,-6"), 0.f }); Wait(1.5f); Shot(TEXT("02b3_bin_close"));

		AutoSteps.Add({ A_Tele, TEXT("A_Shed"), 0.f }); Wait(2.5f); Shot(TEXT("02c_at_the_shed"));
		AutoSteps.Add({ A_Do, TEXT("at:3790,-745,59,-22,-28"), 0.f }); Wait(1.5f); Shot(TEXT("02d_shed_tape"));
		Use(TEXT("pick_tape1")); Flag(TEXT("tape1_taken"), 15.f); Wait(8.f);
		AutoSteps.Add({ A_Do, TEXT("at:3480,-560,59,152,-12"), 0.f }); Wait(1.5f); Shot(TEXT("02e_trash_can_over"));
		AutoSteps.Add({ A_Do, TEXT("at:3230,-470,59,160,-30"), 0.f }); Wait(1.2f); Shot(TEXT("02f_trash_close"));
		AutoSteps.Add({ A_Do, TEXT("at:3120,-300,59,-120,-38"), 0.f }); Wait(1.2f); Shot(TEXT("02g_trash_closer"));

		AutoSteps.Add({ A_Tele, TEXT("A_Porch"), 0.f }); Wait(1.5f);
	}
	Use(TEXT("front")); Flag(TEXT("door_opened"), 30.f); Wait(4.f); Shot(TEXT("03_door_ajar"));

	Use(TEXT("front")); Wait(2.f);
	Go(TEXT("A_Foyer")); Flag(TEXT("inside"), 10.f); Wait(3.f); Shot(TEXT("04_foyer"));
	Use(TEXT("sw_hall")); Wait(1.6f); Shot(TEXT("04b_hall_light"));
	Flag(TEXT("locked_in"), 60.f); Wait(2.f); Use(TEXT("front")); Flag(TEXT("door_stuck"), 10.f); Wait(9.f);
	// ---- ground floor, front
	Go(TEXT("A_Living")); Use(TEXT("sw_living")); Wait(2.f); Shot(TEXT("05_living")); Use(TEXT("note_letter1")); Wait(1.f); Shot(TEXT("06_note")); Close();
	Use(TEXT("look_piano")); Wait(1.6f); Shot(TEXT("06b_look"));
	Go(TEXT("A_Dining")); Wait(2.f); Shot(TEXT("07_dining")); Use(TEXT("look_dining_table")); Wait(1.5f);
	Go(TEXT("A_Kitchen")); Use(TEXT("sw_kitchen")); Wait(2.f); Shot(TEXT("08_kitchen")); Use(TEXT("phone")); Wait(3.f); Use(TEXT("vent")); Flag(TEXT("vent_seen"), 4.f); Shot(TEXT("08a_vent_screwed_shut"));
	// ---- ground floor, rear wing
	Go(TEXT("A_Pantry")); Wait(1.5f); Shot(TEXT("08b_pantry")); Use(TEXT("fusebox")); Wait(1.5f);
	Go(TEXT("A_Den")); Use(TEXT("sw_den")); Wait(2.f); Shot(TEXT("08c_den")); Use(TEXT("desk")); Wait(1.5f); Use(TEXT("note_doctor")); Wait(1.f); Close();
	Go(TEXT("A_BathG")); Wait(1.5f); Shot(TEXT("08d_bath"));
	Go(TEXT("A_Sickroom")); Use(TEXT("sw_sickroom")); Wait(2.f); Shot(TEXT("08e_sickroom")); Use(TEXT("note_aide1")); Wait(1.f); Close(); Use(TEXT("look_sick_bed")); Wait(1.5f);
	// ---- the long quiet, then the thump
	Go(TEXT("A_StairsTop")); Go(TEXT("A_Master")); Use(TEXT("jewelbox")); Wait(1.f); Shot(TEXT("08f_box_locked_screwdriver")); Use(TEXT("pick_screwdriver")); Wait(0.5f);
	Go(TEXT("A_StairsTop")); Go(TEXT("A_Kitchen")); Use(TEXT("vent")); Flag(TEXT("vent_open"), 6.f); Wait(2.4f); Shot(TEXT("08g_vent_open_doll"));
	Use(TEXT("pick_doll")); Wait(0.6f); AutoSteps.Add({ A_Do, TEXT("inspectdoll"), 0.f }); Flag(TEXT("heard_upstairs"), 10.f); Wait(14.f);
	// ---- upstairs: S1
	Go(TEXT("A_StairsTop")); Go(TEXT("N_up_hallA")); AutoSteps.Add({ A_Look, TEXT("Her_Peek"), 0.f }); Flag(TEXT("peek_started"), 8.f); Shot(TEXT("09_S1_peek"));
	Go(TEXT("Her_Peek"));                       // she is only found close to: walk to the doorway with the light on it
	Flag(TEXT("peek_done"), 40.f); Wait(5.f);
	Go(TEXT("A_Master")); Flag(TEXT("master_seen"), 10.f); Shot(TEXT("10_master")); Use(TEXT("jewelbox")); Flag(TEXT("box_open"), 4.f); Wait(0.8f); Shot(TEXT("10b_jewelry_box_open")); Use(TEXT("pick_keep_eye")); Flag(TEXT("want_leave"), 60.f);
	// ---- S3: the long hall
	Go(TEXT("A_BackDoor")); Flag(TEXT("lockin_started"), 20.f);
	WaitHer(15.f); LookHer(3.5f); Shot(TEXT("11_S3_hall")); Fire(3); LookHer(4.f); Shot(TEXT("12_S3_mid")); LookHer(40.f);
	Flag(TEXT("lockin_done"), 80.f); Wait(10.f); Shot(TEXT("13_after_S3"));
	// ---- the fuse
	Go(TEXT("A_Pantry")); Use(TEXT("fusebox")); Wait(2.f); Shot(TEXT("13b_fuse"));
	// ---- S2: the phone
	Use(TEXT("back")); Flag(TEXT("phone_ringing"), 30.f * Slow); Wait(3.f);
	Use(TEXT("phone")); Flag(TEXT("phone_seat"), 40.f); LookHer(1.2f); Shot(TEXT("14_S2_table")); LookHer(6.f);
	Wait(10.f); Shot(TEXT("15_after_S2"));
	Go(TEXT("A_StairsTop")); Go(TEXT("A_UpBath")); Wait(1.f); Shot(TEXT("15b_drawer_open_upstairs")); Use(TEXT("pick_key_sitting"));
	Go(TEXT("A_StairsTop")); Go(TEXT("A_HallSit")); Use(TEXT("sitting")); Wait(3.f);
	Go(TEXT("A_Sitting")); Wait(3.f); Shot(TEXT("16_sitting")); Use(TEXT("note_diary2")); Wait(1.f); Close();
	Use(TEXT("pick_key_prayer")); Use(TEXT("note_deskkey")); Wait(1.f); Close(); Use(TEXT("pick_fuse"));
	Go(TEXT("A_Pantry")); Use(TEXT("fusebox")); Flag(TEXT("fuse_done"), 4.f); Wait(2.f); Shot(TEXT("16a_fuse_in"));
	Go(TEXT("A_Book")); Use(TEXT("book_settlers")); Flag(TEXT("book_done"), 6.f); Wait(0.9f); Shot(TEXT("16b_S10_book_eye")); Wait(3.f); Shot(TEXT("16c_S10_after"));
	Use(TEXT("pick_key_desk")); Go(TEXT("A_Den")); Use(TEXT("desk")); Flag(TEXT("desk_open"), 6.f); Wait(2.f); Shot(TEXT("16b_desk_open_keys")); Use(TEXT("pick_key_ell")); Use(TEXT("pick_ammo_desk")); Wait(1.f);
	// ---- S4: the head by the ceiling
	Go(TEXT("A_StairsTop")); Flag(TEXT("ceiling_started"), 20.f * Slow); LookHer(2.5f); Shot(TEXT("17_S4_ceiling")); LookHer(7.5f); Shot(TEXT("18_S4_sprint")); LookHer(3.f);
	Flag(TEXT("ceiling_done"), 40.f); Wait(8.f);
	// ---- S7: under the bed
	Flag(TEXT("kids_open"), 20.f * Slow); Go(TEXT("A_Kids")); Wait(3.9f); Shot(TEXT("19_S7_hand_out")); Wait(2.6f); Shot(TEXT("20_S7_hand_takes")); Flag(TEXT("underbed_done"), 30.f);
	AutoSteps.Add({ A_Crouch, NAME_None, 1.f }); Use(TEXT("pick_keep_ruth")); AutoSteps.Add({ A_Crouch, NAME_None, 0.f }); Wait(1.f);
	// ---- prayer room
	Use(TEXT("up_prayer")); Go(TEXT("A_Prayer")); Wait(3.f); Shot(TEXT("21_prayer")); Use(TEXT("pick_keep_walter")); Wait(3.f); Use(TEXT("note_prayer")); Wait(1.f); Close();
	// ---- upstairs rear wing: Daniel's room, the aide's room, the sewing room (S9)
	Use(TEXT("up_ell")); Go(TEXT("A_UpEll")); Wait(2.f); Shot(TEXT("21b_up_rear"));
	Go(TEXT("A_Daniel")); Use(TEXT("sw_daniel")); Wait(2.f); Shot(TEXT("21c_daniel")); Use(TEXT("pick_key_attic")); Wait(9.f);
	Go(TEXT("A_Aide")); Wait(2.f); Shot(TEXT("21d_aide"));
	Go(TEXT("A_Bath2")); Wait(2.f); Shot(TEXT("21e_bath2"));
	Go(TEXT("A_Sewing")); Wait(2.f); Shot(TEXT("21f_sewing")); Use(TEXT("pick_shears")); Flag(TEXT("sewing_done"), 6.f); Wait(3.4f); LookHer(1.4f); Shot(TEXT("21g_S9_rocker")); LookHer(4.5f); Wait(5.f);
	// ---- attic: S5
	Use(TEXT("up_attic")); Go(TEXT("A_Attic")); Wait(2.f); Shot(TEXT("22_attic")); Use(TEXT("trunk")); Flag(TEXT("attic_started"), 5.f); Wait(1.2f); Shot(TEXT("22b_footlocker_tags_key")); Use(TEXT("pick_key_cellar")); Use(TEXT("pick_keep_daniel"));
	WaitHer(25.f); LookHer(1.2f); Shot(TEXT("23_S5_crawl")); LookHer(2.2f); Shot(TEXT("24_S5_rise")); Flag(TEXT("attic_done"), 30.f); Wait(8.f);
	// ---- S6: the cellar door
	Use(TEXT("cellar")); Flag(TEXT("sprint_started"), 10.f); WaitHer(40.f); LookHer(0.7f); Shot(TEXT("25_S6_sprint")); LookHer(4.f);
	Flag(TEXT("sprint_done"), 40.f); Wait(5.f); Shot(TEXT("26_cellar"));
	// ---- finale
	Go(TEXT("A_CellarShelf")); Use(TEXT("shelf")); Wait(5.f); Go(TEXT("A_Root")); Flag(TEXT("seen_body"), 10.f); Wait(6.f); Shot(TEXT("27_body"));
	Use(TEXT("place")); Flag(TEXT("placed"), 5.f); Wait(9.f); LookHer(1.f); Shot(TEXT("28_S8_far"));
	Use(TEXT("knot1")); Flag(TEXT("knot1"), 8.f); Wait(3.f); LookHer(1.f); Shot(TEXT("29_S8_mid"));
	Use(TEXT("knot2")); Flag(TEXT("knot2"), 8.f); Wait(4.5f); LookHer(1.f); Shot(TEXT("30_S8_near"));
	Use(TEXT("knot3")); Flag(TEXT("finale_done"), 8.f); Wait(2.2f); Shot(TEXT("31_S8_face")); Flag(TEXT("eye_wanted"), 12.f); Wait(3.5f); Shot(TEXT("31b_give_her_eye_back")); Use(TEXT("place")); Flag(TEXT("eye_given"), 6.f);
	Flag(TEXT("dawn"), 40.f); Wait(9.f); Shot(TEXT("32_dawn_cellar"));
	// ---- ending
	Go(TEXT("A_Foyer")); Shot(TEXT("33_dawn_foyer")); Go(TEXT("A_Porch")); Shot(TEXT("34_dawn_porch"));
	Go(TEXT("A_Cruiser")); Flag(TEXT("ended"), 20.f); Wait(30.f); Shot(TEXT("35_ending")); Wait(20.f); Shot(TEXT("36_credits"));

	AutoIndex = 0;
	AutoStepStart = Clock;
	AutoStuckAt = Clock;
	if (!AutoShotDir.IsEmpty())
	{
		AutoShotDir = FPaths::ConvertRelativePathToFull(AutoShotDir);
		IFileManager::Get().MakeDirectory(*AutoShotDir, true);
	}
	UE_LOG(LogWCAuto, Display, TEXT("WCAUTO begin, %d steps"), AutoSteps.Num());
}

void AWCDirector::AutoRoute(const FVector& From, const FVector& Goal, TArray<FVector>& Out)
{
	Out.Reset();
	struct FNode { FName Name; FVector P; TArray<FName> To; };
	static TArray<FNode> Nodes;
	static TWeakObjectPtr<UWorld> ForWorld;
	if (ForWorld.Get() != GetWorld())
	{
		ForWorld = GetWorld();
		Nodes.Reset();
		for (TActorIterator<AActor> It(GetWorld()); It; ++It)
		{
			if (!It->ActorHasTag(TEXT("NavNode"))) continue;
			FNode N; N.P = It->GetActorLocation();
			for (const FName& T : It->Tags)
			{
				const FString S = T.ToString();
				if (S.StartsWith(TEXT("N_"))) N.Name = FName(*S.Mid(2));
				else if (S.StartsWith(TEXT("E_"))) N.To.Add(FName(*S.Mid(2)));
			}
			Nodes.Add(N);
		}
		UE_LOG(LogWCAuto, Display, TEXT("WCAUTO route graph: %d nodes"), Nodes.Num());
	}
	auto Nearest = [](const FVector& P) -> int32
	{
		int32 Best = INDEX_NONE; float BestD = 1e12f;
		for (int32 i = 0; i < Nodes.Num(); ++i)
		{
			if (FMath::Abs(Nodes[i].P.Z - P.Z) > 130.f) continue;
			const float D = FVector::DistSquared2D(Nodes[i].P, P);
			if (D < BestD) { BestD = D; Best = i; }
		}
		return Best;
	};
	const FVector Feet = From - FVector(0, 0, 88);
	const int32 A = Nearest(Feet), B = Nearest(Goal);
	bool bDirect = FVector::Dist2D(Feet, Goal) < 260.f && FMath::Abs(Feet.Z - Goal.Z) < 130.f;
	if (bDirect)
	{
		// only if nothing stands between him and it
		FHitResult Hit;
		FCollisionQueryParams Q(SCENE_QUERY_STAT(WCAutoDirect), false, Player());
		const FVector To(Goal.X, Goal.Y, FMath::Max(Goal.Z, Feet.Z + 60.f));
		if (GetWorld()->LineTraceSingleByChannel(Hit, From, To, ECC_Visibility, Q) && Hit.Distance < FVector::Dist(From, To) - 45.f) bDirect = false;
	}
	if (A == INDEX_NONE || B == INDEX_NONE || bDirect) { Out.Add(Goal); return; }
	// Dijkstra
	TArray<float> Cost; Cost.Init(1e12f, Nodes.Num());
	TArray<int32> Prev; Prev.Init(INDEX_NONE, Nodes.Num());
	TArray<bool> Done; Done.Init(false, Nodes.Num());
	Cost[A] = 0.f;
	for (int32 Iter = 0; Iter < Nodes.Num(); ++Iter)
	{
		int32 U = INDEX_NONE; float Best = 1e12f;
		for (int32 i = 0; i < Nodes.Num(); ++i) if (!Done[i] && Cost[i] < Best) { Best = Cost[i]; U = i; }
		if (U == INDEX_NONE || U == B) break;
		Done[U] = true;
		for (const FName& To : Nodes[U].To)
		{
			const int32 V = Nodes.IndexOfByPredicate([&To](const FNode& N) { return N.Name == To; });
			if (V == INDEX_NONE) continue;
			const float C = Cost[U] + FVector::Dist(Nodes[U].P, Nodes[V].P);
			if (C < Cost[V]) { Cost[V] = C; Prev[V] = U; }
		}
	}
	TArray<FVector> Rev;
	for (int32 i = B; i != INDEX_NONE; i = Prev[i]) Rev.Add(Nodes[i].P);
	if (Rev.Num() == 0 || Cost[B] > 1e11f) { Out.Add(Goal); return; }
	for (int32 i = Rev.Num() - 1; i >= 0; --i) Out.Add(Rev[i]);
	// skip the first node if we are already past it on the way to the second
	if (Out.Num() >= 2 && FVector::Dist2D(Feet, Out[1]) < FVector::Dist2D(Out[0], Out[1])) Out.RemoveAt(0);
	Out.Add(Goal);
}

static AActor* AutoTarget(AWCDirector* D, FName Name)
{
	for (TActorIterator<AWCInteractable> It(D->GetWorld()); It; ++It) if (It->WCId == Name) return *It;
	for (TActorIterator<AActor> It(D->GetWorld()); It; ++It) if (It->ActorHasTag(Name)) return *It;
	for (TActorIterator<AWCTrigger> It(D->GetWorld()); It; ++It) if (It->WCId == Name) return *It;
	return nullptr;
}

static void AimAt(AWCCharacter* P, const FVector& Point, float Dt, float Speed = 9.f)
{
	if (AController* C = P->GetController())
	{
		const FRotator Want = (Point - P->EyeLocation()).Rotation();
		C->SetControlRotation(FMath::RInterpTo(C->GetControlRotation(), FRotator(Want.Pitch, Want.Yaw, 0.f), Dt, Speed));
	}
}

void AWCDirector::PerfReport(const TCHAR* Label, bool bReset)
{
	if (PerfFrames.Num() < 10) return;
	TArray<float> S = PerfFrames;
	S.Sort();
	double Sum = 0.0;
	for (float F : S) Sum += F;
	const float Avg = (float)(Sum / S.Num());
	const float P99 = S[FMath::Clamp(FMath::FloorToInt(S.Num() * 0.99f), 0, S.Num() - 1)];
	UE_LOG(LogWCAuto, Display, TEXT("WCPERF %s frames=%d avg=%.1f ms (%.0f fps) p99=%.1f ms (%.0f fps) worst=%.1f ms"), Label, S.Num(), Avg * 1000.f, 1.f / Avg, P99 * 1000.f, 1.f / P99, S.Last() * 1000.f);
	if (bReset) PerfFrames.Reset();
}

void AWCDirector::AutoTick(float Dt)
{
	{
		const double Now = FPlatformTime::Seconds();
		if (PerfLast > 0.0 && PlaySeconds > 20.f) PerfFrames.Add((float)(Now - PerfLast));
		PerfLast = Now;
		if (PerfFrames.Num() >= 3600) PerfReport(TEXT("window"), true);
	}
	AWCCharacter* P = Player();
	if (!P || AutoIndex < 0) return;
	{
		// a short check: stop a few seconds after a given point in the story
		static FString StopFlag;
		static bool bStopRead = false, bStopping = false;
		if (!bStopRead) { bStopRead = true; FParse::Value(FCommandLine::Get(), TEXT("WCAutoStop="), StopFlag); }
		if (!StopFlag.IsEmpty() && !bStopping && Has(FName(*StopFlag)))
		{
			bStopping = true;
			UE_LOG(LogWCAuto, Display, TEXT("WCAUTO stop point %s reached at t=%.1f"), *StopFlag, PlaySeconds);
			After(6.f, [this]() { UKismetSystemLibrary::QuitGame(this, UGameplayStatics::GetPlayerController(this, 0), EQuitPreference::Quit, false); });
		}
	}

	const bool bForce = FParse::Param(FCommandLine::Get(), TEXT("WCAutoForce"));
	if (AutoIndex >= AutoSteps.Num())
	{
		PerfReport(TEXT("final"), true);
		UE_LOG(LogWCAuto, Display, TEXT("WCAUTO DONE t=%.1f stuck=%d ended=%d"), PlaySeconds, AutoStuckCount, Has(TEXT("ended")) ? 1 : 0);
		AutoIndex = -1;
		UKismetSystemLibrary::QuitGame(this, UGameplayStatics::GetPlayerController(this, 0), EQuitPreference::Quit, false);
		return;
	}
	if (PlaySeconds > 60.f * 75.f)
	{
		UE_LOG(LogWCAuto, Error, TEXT("WCAUTO TIMEOUT at step %d"), AutoIndex);
		AutoIndex = -1;
		UKismetSystemLibrary::QuitGame(this, UGameplayStatics::GetPlayerController(this, 0), EQuitPreference::Quit, false);
		return;
	}
	if (StalkState > 0 && Her() && Her()->IsShown() && !P->IsDown() && !P->IsInputLocked())
	{
		AutoStepStart += Dt; AutoStuckAt = Clock;
		P->SetAiming(true);
		AimAt(P, Her()->HeadLocation() - FVector(0, 0, 60), Dt, 14.f);
		static double NextShot = 0.0;
		if (P->Ammo <= 0) P->DoReload();
		else if (P->IsGunUp() && Clock > NextShot && StalkState == 2 && PlayerSees(Her()->HeadLocation() - FVector(0, 0, 60), 0.95f, 2200.f)) { NextShot = Clock + 0.6; P->DoFire(); }
		bAutoDefending = true;
		return;
	}
	if (bAutoDefending) { bAutoDefending = false; P->SetAiming(false); AutoPath.Reset(); }
	const FAuto& S = AutoSteps[AutoIndex];
	const double In = Clock - AutoStepStart;
	auto Next = [this]()
	{
		++AutoIndex; AutoStepStart = Clock; AutoPath.Reset(); AutoStuckAt = Clock;
		if (AWCCharacter* Pl = Player()) AutoStuckLoc = Pl->GetActorLocation();
	};
	if (In < 0.02) { UE_LOG(LogWCAuto, Display, TEXT("WCAUTO step %d type %d %s %.1f (t=%.1f)"), AutoIndex, S.Type, *S.Arg.ToString(), S.F, PlaySeconds); }

	// always: keep looking at her if she is in a scare and we are flat on our back etc.
	switch (S.Type)
	{
	case A_Wait: if (In >= S.F) Next(); return;
	case A_WaitFlag:
		if (Has(S.Arg)) { Next(); return; }
		if (In > S.F) { UE_LOG(LogWCAuto, Error, TEXT("WCAUTO FAIL flag %s not set after %.0f s (step %d)"), *S.Arg.ToString(), S.F, AutoIndex); Next(); }
		return;
	case A_Her:
		if (AWCEntity* E = Her())
		{
			const FVector Fwd = FRotator(0.f, P->GetControlRotation().Yaw, 0.f).Vector();
			E->Appear(P->GetActorLocation() - FVector(0, 0, 88) + Fwd * S.F, (-Fwd).Rotation().Yaw, S.Arg);
			E->SetGlow(S.F < 200.f ? 0.f : 0.f);
		}
		Next(); return;
	case A_FaceItem:
		if (AActor* T = AutoTarget(this, S.Arg))
		{
			FVector O, E; T->GetActorBounds(true, O, E);
			// stand 1.2 m away on whichever side is open
			FVector Best = O + FVector(-120, 0, 0);
			for (float Yaw = 0.f; Yaw < 360.f; Yaw += 45.f)
			{
				const FVector Cand = O + FRotator(0.f, Yaw, 0.f).Vector() * 125.f;
				FHitResult Hit;
				FCollisionQueryParams Q(SCENE_QUERY_STAT(WCItems), false, P);
				Q.AddIgnoredActor(T);
				if (!GetWorld()->LineTraceSingleByChannel(Hit, Cand + FVector(0, 0, 60), O + FVector(0, 0, 20), ECC_Visibility, Q)) { Best = Cand; break; }
			}
			const float Floor = FMath::RoundToFloat((O.Z + 40.f) / 350.f - 0.5f) * 350.f;
			P->TeleportToCheckpoint(FVector(Best.X, Best.Y, Floor + 96.f), (O - Best).Rotation().Yaw);
			if (AController* Ct = P->GetController()) Ct->SetControlRotation((O - (FVector(Best.X, Best.Y, Floor + 152.f))).Rotation());
		}
		Next(); return;
	case A_Aim: P->SetAiming(S.F > 0.5f); Next(); return;
	case A_Crouch: if (S.F > 0.5f) P->Crouch(); else P->UnCrouch(); Next(); return;
	case A_Do:
		if (S.Arg == TEXT("beam"))
		{
			Settings.BeamChoice = FMath::RoundToInt(S.F);
			P->ApplyBeamWidth();
		}
		else if (S.Arg == TEXT("check_yard_paths"))
		{
			FCollisionQueryParams Query(SCENE_QUERY_STAT(WCYardAccess), false, P);
			for (TActorIterator<AStaticMeshActor> It(GetWorld()); It; ++It)
			{
				if (!It->ActorHasTag(TEXT("YardTrail"))) continue;
				const FVector Mid = It->GetActorLocation() + FVector(0, 0, 93);
				const FVector Along = It->GetActorForwardVector() * FMath::Max(1., It->GetActorScale3D().X * 50. - 26.);
				FHitResult Hit;
				const bool Blocked = GetWorld()->SweepSingleByChannel(Hit, Mid-Along, Mid+Along, FQuat::Identity, ECC_Pawn,
					FCollisionShape::MakeCapsule(30.f, 88.f), Query);
				UE_LOG(LogWCAuto, Display, TEXT("WCWALK %s hit=%s"), *It->Tags.Last().ToString(), Blocked && Hit.GetActor() ? *Hit.GetActor()->GetActorNameOrLabel() : TEXT("clear"));
			}
		}
		else if (S.Arg == TEXT("vent_test"))
		{
			SwitchRoom(TEXT("master"),true,false); SwitchRoom(TEXT("uphall"),true,false);
			Event(TEXT("use:vent"));
		}
		else if (S.Arg == TEXT("return_key"))
		{
			GiveItem(TEXT("doll"), TEXT("Rag doll"));
			Event(TEXT("inspect:doll"));
			UE_LOG(LogWCAuto, Display, TEXT("WCRETURN key=%d vent=%d"),HasItem(TEXT("key_box")),Has(TEXT("vent_open")));
		}
		else if (S.Arg == TEXT("haunt_test"))
		{
			for (int32 k=0;k<7;++k)
			{
				DialogueUntil=Clock; WhisperAt=Clock; CueFreeAt=Clock;
				TickCues(0.f);
			}
		}
		else if (S.Arg == TEXT("light_test"))
		{
			InsideAt=PlaySeconds-100.f;
			for (const FName Name : {FName(TEXT("living")),FName(TEXT("master")),FName(TEXT("uphall"))})
			{
				SwitchRoom(Name,true,false);
				Rooms.FindChecked(Name).KillAt=Clock-1.;
			}
			for (int32 k=0;k<3;++k) { NextLightKill=Clock-1.; TickHouseLights(.016f); }
		}
		else if (S.Arg == TEXT("ceiling_music_test"))
		{
			UE_LOG(LogWCAuto, Display, TEXT("WCRETURN recoveredEye=%d"), HasItem(TEXT("keep_eye")));
			ScareCeiling();
		}
		else if (S.Arg == TEXT("switch_test"))
		{
			Event(TEXT("use:sw_uphall")); Event(TEXT("use:sw_master"));
			UE_LOG(LogWCAuto, Display, TEXT("WCRETURN hall=%d master=%d visibleFromLanding=%d"),Rooms.FindChecked(TEXT("uphall")).bOn,Rooms.FindChecked(TEXT("master")).bOn, Her() && Her()->IsShown());
		}
		else if (S.Arg == TEXT("box_test"))
		{
			Event(TEXT("use:jewelbox"));
			UE_LOG(LogWCAuto, Display, TEXT("WCRETURN peekDone=%d exitLocked=%d boxOpen=%d eyeVisible=%d"),Has(TEXT("peek_done")),
				Door(TEXT("front")) && Door(TEXT("front"))->bLocked,Has(TEXT("box_open")),Thing(TEXT("pick_keep_eye")) && !Thing(TEXT("pick_keep_eye"))->IsHidden());
		}
		else if (S.Arg == TEXT("snicker_checkpoint"))
		{
			Checkpoint(TEXT("snicker_test"));
			Set(TEXT("qa_after_snicker_checkpoint"));
		}
		else if (S.Arg == TEXT("snicker_turn"))
		{
			const TWeakObjectPtr<UAudioComponent> Voice = ListeningSnicker;
			if (Voice.IsValid() && Voice->IsPlaying())
			{
				const bool bTurnToward = FParse::Param(FCommandLine::Get(), TEXT("WCTurnToward"));
				const float SourceYaw = (Voice->GetComponentLocation()-P->EyeLocation()).Rotation().Yaw;
				FRotator View = P->GetControlRotation();
				const float Side = FMath::Sign(FMath::FindDeltaAngleDegrees(View.Yaw, SourceYaw));
				View.Yaw += Side * (bTurnToward ? 60.f : -55.f);
				P->GetController()->SetControlRotation(View);
				After(.30f, [Voice,bTurnToward] {
					const bool Playing = Voice.IsValid() && Voice->IsPlaying();
					UE_LOG(LogWCAuto,Display,TEXT("WCLISTEN toward=%d playingAfterTurn=%d"),bTurnToward,Playing);
					if (Playing == bTurnToward) UE_LOG(LogWCAuto,Error,TEXT("WCAUTO FAIL listening reaction"));
				});
				After(2.15f, [Voice] {
					if (Voice.IsValid() && Voice->IsPlaying()) UE_LOG(LogWCAuto,Error,TEXT("WCAUTO FAIL listening voice still active"));
				});
			}
			else UE_LOG(LogWCAuto,Error,TEXT("WCAUTO FAIL no listening voice at reaction time"));
		}
		else if (S.Arg == TEXT("snicker_reload"))
		{
			Flags.Remove(TEXT("heard_listening_snicker")); // prove the marker is read from disk
			const bool Loaded = DoLoad();
			UE_LOG(LogWCAuto,Display,TEXT("WCLISTEN reload=%d remembered=%d checkpointX=%.0f"), Loaded,
				Has(TEXT("heard_listening_snicker")),P->GetActorLocation().X);
			if (!Loaded || !Has(TEXT("heard_listening_snicker")) || Has(TEXT("qa_after_snicker_checkpoint")) ||
				FMath::Abs(P->GetActorLocation().X - 380.f) > 4.f)
				UE_LOG(LogWCAuto,Error,TEXT("WCAUTO FAIL listening checkpoint"));
			WhisperAt = CueFreeAt = Clock;
			TickCues(0.f);
			if (ListeningSnicker.IsValid()) UE_LOG(LogWCAuto,Error,TEXT("WCAUTO FAIL listening encounter repeated"));
		}
		else if (S.Arg == TEXT("arm_bed_trigger"))
		{
			Set(TEXT("kids_open")); bBusy=false; NextScareAt=Clock;
		}
		else if (S.Arg == TEXT("bed_result"))
		{
			const AWCInteractable* Box = Thing(TEXT("pick_keep_ruth"));
			UE_LOG(LogWCAuto,Display,TEXT("WCBED done=%d unlocked=%d pickup=%d loc=%s cameraReturned=%d"),
				Has(TEXT("underbed_done")), !P->IsInputLocked(), Box && Box->CanInteract(),
				Box ? *Box->GetActorLocation().ToCompactString() : TEXT("missing"), UGameplayStatics::GetPlayerController(this,0)->GetViewTarget()==P);
		}
		else if (S.Arg == TEXT("bed_pickup"))
		{
			const AWCInteractable* Focused = P->GetFocus();
			P->DoInteract();
			UE_LOG(LogWCAuto,Display,TEXT("WCBED focus=%s recovered=%d"), Focused ? *Focused->WCId.ToString() : TEXT("none"),HasItem(TEXT("keep_ruth")));
		}
		else if (S.Arg == TEXT("dust_reference") || S.Arg == TEXT("dust_restore"))
			P->Dust->SetVisibility(S.Arg == TEXT("dust_restore"));
		else if (S.Arg == TEXT("finish_bed_mix"))
			UAudioMixerBlueprintLibrary::StopRecordingOutputToAnyPath(this,EAudioRecordingExportType::WavFile,TEXT("under_bed"),AutoShotDir);
		else if (S.Arg == TEXT("finish_house_mix"))
			UAudioMixerBlueprintLibrary::StopRecordingOutputToAnyPath(this,EAudioRecordingExportType::WavFile,TEXT("house_walk"),AutoShotDir);
		else if (S.Arg == TEXT("finish_haunts"))
			UAudioMixerBlueprintLibrary::StopRecordingOutputToAnyPath(this,EAudioRecordingExportType::WavFile,TEXT("edith_one_shots"),AutoShotDir);
		else if (S.Arg == TEXT("audition_haunts"))
		{
			UAudioMixerBlueprintLibrary::StartRecordingOutput(this,14.f);
			const int32 Groups[] = {1,7,8,5};
			for (int32 I=0; I<4; ++I) After(.45f+3.f*I, [this,Group=Groups[I]] { PlayHouseHaunt(Group); });
		}
		else if (S.Arg == TEXT("record_mix")) UAudioMixerBlueprintLibrary::StartRecordingOutput(this, 30.f);
		else if (S.Arg == TEXT("finish_mix")) UAudioMixerBlueprintLibrary::StopRecordingOutputToAnyPath(this, EAudioRecordingExportType::WavFile, TEXT("arrival_mix"), AutoShotDir);
		else if (S.Arg == TEXT("take_tape")) Event(TEXT("take:tape1"));
		else if (S.Arg == TEXT("mix_check"))
		{
			int32 Active = 0;
			for (TObjectIterator<UAudioComponent> It; It; ++It)
				if (It->GetWorld() == GetWorld() && It->IsPlaying() && It->ComponentHasTag(TEXT("HouseAudio"))) ++Active;
			const FLoop* Bed = Loops.Find(TEXT("amb"));
			const FLoop* Score = Loops.Find(TEXT("drone"));
			UE_LOG(LogWCAuto, Display, TEXT("WCSCORE house=%s playing=%d"), Score ? *Score->Name : TEXT("none"),
				Score && Score->Audio.IsValid() && Score->Audio->IsPlaying());
			UE_LOG(LogWCAuto, Display, TEXT("WCARRIVAL x=%.0f bed=%s houseSources=%d smellPending=%d"), P->GetActorLocation().X,
				Bed ? *Bed->Name : TEXT("none"), Active, Has(TEXT("smell_pending")));
		}
		else if (S.Arg == TEXT("use_screwdriver_pickup"))
		{
			const AWCInteractable* Target = P->GetFocus();
			if (Target && Target->WCId == TEXT("pick_screwdriver")) P->DoInteract();
			UE_LOG(LogWCAuto, Display, TEXT("WCARRIVAL standing pickup focus=%s inventory=%d"), Target ? *Target->WCId.ToString() : TEXT("none"), HasItem(TEXT("screwdriver")));
		}
		else if (S.Arg == TEXT("detail_lens") || S.Arg == TEXT("normal_lens"))
		{
			for (UActorComponent* Source : P->GetComponentsByTag(UPointLightComponent::StaticClass(), TEXT("PropReviewLight")))
				if (auto* Lamp = Cast<UPointLightComponent>(Source)) Lamp->SetIntensity(S.Arg == TEXT("detail_lens") ? 420.f : 14000.f);
			if (APlayerCameraManager* Camera = UGameplayStatics::GetPlayerCameraManager(this, 0))
			{
				if (S.Arg == TEXT("detail_lens")) Camera->SetFOV(34.f);
				else Camera->UnlockFOV();
			}
		}
		else if (S.Arg == TEXT("crow_briefed"))
		{
			UE_LOG(LogWCAuto, Display, TEXT("WCCROW before briefing remaining=%d"), YardCawsLeft);
			Set(TEXT("briefed"));
		}
		else if (S.Arg == TEXT("crow_budget"))
		{
			UE_LOG(LogWCAuto, Display, TEXT("WCCROW finished remaining=%d"),YardCawsLeft);
		}
		else if (S.Arg == TEXT("crow_inside"))
		{
			YardCawsLeft = 2;
			NextYardCaw = Clock;
			TickYardCrows();
			UE_LOG(LogWCAuto, Display, TEXT("WCCROW indoors remaining=%d audible=%d"),YardCawsLeft,YardCrowVoice.IsValid() && YardCrowVoice->IsPlaying());
		}
		else if (S.Arg == TEXT("room_use_phone"))
		{
			const AWCInteractable* Target = P->GetFocus();
			Set(TEXT("phone_ringing"));
			if (Target && Target->WCId == TEXT("phone")) P->DoInteract();
			UE_LOG(LogWCAuto, Display, TEXT("WCROOM phone focus=%s answered=%d"),Target ? *Target->WCId.ToString() : TEXT("none"),Has(TEXT("phone_done")));
		}
		else if (S.Arg == TEXT("check_book_focus"))
		{
			const AWCInteractable* Focused = P->GetFocus();
			UE_LOG(LogWCAuto, Display, TEXT("WCSHELF standing focus=%s"), Focused ? *Focused->WCId.ToString() : TEXT("none"));
		}
		else if (S.Arg == TEXT("drawings"))
		{
			if (AController* C = P->GetController()) C->SetControlRotation((FVector(818.f, -430.f, P->GetActorLocation().Z + 72.f) - P->EyeLocation()).Rotation());
		}
		else if (S.Arg.ToString().StartsWith(TEXT("at:")))
		{
			TArray<FString> V;
			S.Arg.ToString().Mid(3).ParseIntoArray(V, TEXT(","));
			if (V.Num() >= 5)
			{
				P->TeleportToCheckpoint(FVector(FCString::Atof(*V[0]), FCString::Atof(*V[1]), FCString::Atof(*V[2])), FCString::Atof(*V[3]));
				if (AController* C = P->GetController()) C->SetControlRotation(FRotator(FCString::Atof(*V[4]), FCString::Atof(*V[3]), 0.f));
				P->SetFlashlight(true, false);
				{
					// anything, whether or not it has collision: trace against the visible meshes themselves
					const FVector Eye(FCString::Atof(*V[0]), FCString::Atof(*V[1]), FCString::Atof(*V[2]) + 66.f);
					const FVector Fwd = FRotator(FCString::Atof(*V[4]), FCString::Atof(*V[3]), 0.f).Vector();
					auto What = [this, &Eye](const FVector& Dir, float Len) -> FString
					{
						FString Out; float Best = Len;
						for (TActorIterator<AActor> It(GetWorld()); It; ++It)
						{
							if (It->IsHidden()) continue;
							TArray<UStaticMeshComponent*> Comps; It->GetComponents(Comps);
							for (UStaticMeshComponent* C2 : Comps)
							{
								if (!C2->IsVisible() || !C2->GetStaticMesh()) continue;
								// in the piece's own space, so a tilted board is tested as the board it is
								const FTransform Tm = C2->GetComponentTransform();
								const FBox B = C2->GetStaticMesh()->GetBoundingBox();
								FVector HitLoc, HitNorm; float HitT;
								if (FMath::LineExtentBoxIntersection(B, Tm.InverseTransformPosition(Eye), Tm.InverseTransformPosition(Eye + Dir * Len), FVector::ZeroVector, HitLoc, HitNorm, HitT) && HitT * Len < Best && HitT > 0.001f)
								{
									Best = HitT * Len;
									Out = FString::Printf(TEXT("%s at %.0f cm"), *It->GetActorNameOrLabel(), Best);
								}
							}
						}
						return Out.IsEmpty() ? FString(TEXT("nothing")) : Out;
					};
					UE_LOG(LogWCAuto, Display, TEXT("WCVIEW %s: ahead = %s; straight up = %s"), *S.Arg.ToString(), *What(Fwd, 900.f), *What(FVector(0, 0, 1), 900.f));
				}
			}
		}
		else if (S.Arg == TEXT("inspectdoll")) Event(TEXT("inspect:doll"));
		else if (S.Arg.ToString().StartsWith(TEXT("flag:"))) { Set(FName(*S.Arg.ToString().Mid(5))); ApplyWorldState(); }
		else if (S.Arg == TEXT("book")) { bBusy = false; ScareBook(); }
		else if (S.Arg.ToString().StartsWith(TEXT("mood:")))
		{
			const FName M(*S.Arg.ToString().Mid(5));
			if (AWCEntity* E = Her()) { E->SetScream(M == TEXT("scream") ? 1.f : 0.f); E->SetMood(M == TEXT("scream") ? FName(TEXT("rage")) : M); }
		}

		else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }
		else if (S.Arg.ToString().StartsWith(TEXT("filter:"))) { SetFilter(FCString::Atoi(*S.Arg.ToString().Mid(7))); }
		else if (S.Arg == TEXT("peek")) { bBusy = false; ScarePeek(); }
		else if (S.Arg == TEXT("eye")) { bBusy = false; EyeTry(true); }
		else if (S.Arg.ToString().StartsWith(TEXT("tvgain:"))) { if (TVScreen) TVScreen->SetScalarParameterValue(TEXT("Gain"), FCString::Atof(*S.Arg.ToString().Mid(7))); }
		else if (S.Arg == TEXT("tvoff")) { TVOff(true, true); }
		else if (S.Arg == TEXT("s7")) { bBusy = false; ScareUnderBed(); }
		else if (S.Arg == TEXT("grab"))
		{
			Set(TEXT("mem1")); Set(TEXT("mem2")); Set(TEXT("mem3"));
			Grab(1.35f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); Flags.Remove(TEXT("mem1")); Flags.Remove(TEXT("mem2")); Flags.Remove(TEXT("mem3")); bBusy = true; });
		}
		else if (S.Arg == TEXT("mem1")) PlayMemory(1, [this]() { bBusy = true; });
		else if (S.Arg == TEXT("mem2")) PlayMemory(2, [this]() { bBusy = true; });
		else if (S.Arg == TEXT("mem3")) PlayMemory(3, [this]() { bBusy = true; });
		Next(); return;
	case A_Tele:
		if (AActor* T = AutoTarget(this, S.Arg)) P->TeleportToCheckpoint(T->GetActorLocation(), T->GetActorRotation().Yaw);
		Next(); return;
	case A_Light: if (!P->IsFlashlightOn()) P->ToggleFlashlight(); Next(); return;
	case A_Shot:
		if (S.Arg == TEXT("dust_08"))
		{
			APlayerController* PC = UGameplayStatics::GetPlayerController(this,0);
			const FVector Eye=P->EyeLocation();
			int32 Width,Height; PC->GetViewportSize(Width,Height);
			for (int32 I=0; I<P->Dust->GetInstanceCount(); ++I)
			{
				FTransform M; P->Dust->GetInstanceTransform(I,M,true);
				const FVector V=M.GetLocation()-Eye;
				FVector2D Pixel;
				if (V.SizeSquared() > FMath::Square(480.) || FVector::DotProduct(V.GetSafeNormal(),P->GetControlRotation().Vector()) < .90f ||
					!PC->ProjectWorldLocationToScreen(M.GetLocation(),Pixel) || Pixel.X <= 0 || Pixel.Y <= 0 || Pixel.X >= Width || Pixel.Y >= Height) continue;
				FCollisionQueryParams Query(SCENE_QUERY_STAT(WCDustView),false,P);
				if (!GetWorld()->LineTraceTestByChannel(Eye,M.GetLocation(),ECC_Visibility,Query))
					UE_LOG(LogWCAuto,Display,TEXT("WCDUST mote=%d pixel=%.0f,%.0f range=%.0f visible=%d"),I,Pixel.X,Pixel.Y,V.Size(),P->Dust->IsVisible() && !P->Dust->bHiddenInGame);
			}
		}
		if (S.Arg == TEXT("flies_a") || S.Arg == TEXT("flies_b") || S.Arg == TEXT("vent_driver"))
		{
			TArray<UInstancedStaticMeshComponent*> Clouds;
			P->GetComponents(Clouds);
			Clouds.Add(Flies);
			for (UInstancedStaticMeshComponent* Cloud : Clouds)
			{
				if (!Cloud || !Cloud->GetStaticMesh() || !Cloud->GetInstanceCount()) continue;
				int32 NearbyInView = 0;
				FTransform T, First;
				Cloud->GetInstanceTransform(0, First, true);
				for (int32 i = 0; i < Cloud->GetInstanceCount(); ++i)
				{
					Cloud->GetInstanceTransform(i, T, true);
					const FVector Delta = T.GetLocation() - P->EyeLocation();
					if (Delta.SizeSquared() < FMath::Square(250.f) && FVector::DotProduct(Delta.GetSafeNormal(), P->EyeForward()) > .85f) ++NearbyInView;
				}
				UE_LOG(LogWCAuto, Display, TEXT("WCPARTICLES %s mesh=%s instances=%d visible=%d nearbyInView=%d first=%s"), *S.Arg.ToString(), *Cloud->GetStaticMesh()->GetName(), Cloud->GetInstanceCount(), Cloud->IsVisible() && !Cloud->bHiddenInGame, NearbyInView, *First.GetLocation().ToCompactString());
			}
		}
		if (!AutoShotDir.IsEmpty())
		{
			FScreenshotRequest::RequestScreenshot(AutoShotDir / (S.Arg.ToString() + TEXT(".png")), false, false);
		}
		UE_LOG(LogWCAuto, Display, TEXT("WCAUTO shot %s t=%.1f her=%d dist=%.0f"), *S.Arg.ToString(), PlaySeconds, Her() && Her()->IsShown() ? 1 : 0, Her() ? Her()->DistToPlayer() : -1.f);
		Next(); return;
	case A_Look:
		if (AActor* T = AutoTarget(this, S.Arg)) AimAt(P, T->GetActorLocation() + FVector(0, 0, S.F < -0.5f ? 0.f : 60.f), Dt);
		if (In > 1.2) Next();
		return;
	case A_LookHer:
		if (Her() && Her()->IsShown()) AimAt(P, Her()->HeadLocation(), Dt, 12.f);
		if (In >= S.F) Next();
		return;
	case A_WaitHer:
		if (Her() && Her()->IsShown()) { Next(); return; }
		if (In > S.F) { UE_LOG(LogWCAuto, Error, TEXT("WCAUTO FAIL she never appeared (step %d)"), AutoIndex); Next(); }
		return;
	case A_Fire:
	{
		P->SetAiming(true);
		if (Her() && Her()->IsShown()) AimAt(P, Her()->GetActorLocation() + FVector(0, 0, 150), Dt, 14.f);
		const int32 Want = (int32)S.F;
		const int32 Fired = AWCCharacter::MagSize - P->Ammo;
		if (In > 0.9 && P->IsGunUp() && Fired < Want) P->DoFire();
		if (Fired >= Want || In > 8.0) { P->SetAiming(false); Next(); }
		return;
	}
	default: break;
	}

	if (P->IsDown() || P->IsInputLocked()) { AutoStuckAt = Clock; return; }

	if (S.Type == A_Use)
	{
		if (S.Arg == TEXT("__close")) { if (ActiveNote.IsValid()) CloseNote(); Next(); return; }
		AWCInteractable* T = Cast<AWCInteractable>(AutoTarget(this, S.Arg));
		if (!T) { UE_LOG(LogWCAuto, Error, TEXT("WCAUTO FAIL nothing to use called %s"), *S.Arg.ToString()); Next(); return; }
		FVector Origin, Ext;
		T->GetActorBounds(true, Origin, Ext);
		AimAt(P, Origin, Dt, 14.f);
		if (In > 0.5 && P->GetFocus() == T)
		{
			P->DoInteract();
			UE_LOG(LogWCAuto, Display, TEXT("WCAUTO used %s"), *S.Arg.ToString());
			Next();
		}
		else if (In > 4.0)
		{
			{
				FHitResult Hit;
				FCollisionQueryParams Q(SCENE_QUERY_STAT(WCAutoWhy), false, P);
				const FVector Eye = P->EyeLocation();
				const bool bHit = GetWorld()->LineTraceSingleByChannel(Hit, Eye, Eye + (Origin - Eye).GetSafeNormal() * 400.f, ECC_Visibility, Q);
				UE_LOG(LogWCAuto, Error, TEXT("WCAUTO WHY %s: in the way = %s (%s) at %.0f cm; target at (%.0f,%.0f,%.0f) half (%.0f,%.0f,%.0f); eye (%.0f,%.0f,%.0f)"), *S.Arg.ToString(),
					bHit && Hit.GetActor() ? *Hit.GetActor()->GetActorNameOrLabel() : TEXT("nothing"), bHit && Hit.GetComponent() ? *Hit.GetComponent()->GetName() : TEXT("-"), bHit ? Hit.Distance : -1.f,
					Origin.X, Origin.Y, Origin.Z, Ext.X, Ext.Y, Ext.Z, Eye.X, Eye.Y, Eye.Z);
			}
			UE_LOG(LogWCAuto, Error, TEXT("WCAUTO FAIL could not focus %s (dist %.0f, enabled %d)%s"), *S.Arg.ToString(), FVector::Dist(P->EyeLocation(), Origin), T->CanInteract() ? 1 : 0, bForce ? TEXT(" -> forced") : TEXT(""));
			if (bForce && T->CanInteract()) T->Interact(P);
			Next();
		}
		return;
	}

	if (S.Type == A_Go)
	{
		AActor* T = AutoTarget(this, S.Arg);
		if (!T) { UE_LOG(LogWCAuto, Error, TEXT("WCAUTO FAIL no target %s"), *S.Arg.ToString()); Next(); return; }
		FVector Goal = T->GetActorLocation();
		const bool bToUse = S.F > 0.5f;
		if (bToUse) { FVector O, E; T->GetActorBounds(true, O, E); Goal = O; }
		const FVector Loc = P->GetActorLocation();
		const float Reach = bToUse ? 150.f : 70.f;
		const float D2 = FVector::Dist2D(Loc, Goal);
		// near enough to use = within arm's length of the thing's box on the floor plan (the player's own rule)
		float BoxGap = 1e6f;
		if (bToUse)
		{
			FVector BO, BE; T->GetActorBounds(true, BO, BE);
			BoxGap = FVector2D(FMath::Max(FMath::Abs(Loc.X - BO.X) - BE.X, 0.f), FMath::Max(FMath::Abs(Loc.Y - BO.Y) - BE.Y, 0.f)).Size();
		}
		if (bToUse && BoxGap < P->InteractReach - 62.f && FVector::Dist(P->EyeLocation(), Goal) < P->InteractRange + 60.f)
		{
			FHitResult Hit;
			FCollisionQueryParams Q(SCENE_QUERY_STAT(WCAutoSee), false, P);
			const FVector Eye = P->EyeLocation();
			const bool bBlocked = GetWorld()->LineTraceSingleByChannel(Hit, Eye, Goal, ECC_Visibility, Q) && Hit.GetActor() != T && Hit.Distance < FVector::Dist(Eye, Goal) - 14.f;
			static int32 NearStep = -1, RoundStep = -1;
			static double NearAt = 0.0;
			if (NearStep != AutoIndex) { NearStep = AutoIndex; NearAt = Clock; }
			if (!bBlocked || D2 < 55.f || Clock - NearAt > 14.0) { Next(); return; }
			if (Clock - NearAt > 2.5 && RoundStep != AutoIndex)
			{
				// it is hidden from here: find a side it can be seen from, and go and stand there
				RoundStep = AutoIndex;
				Q.AddIgnoredActor(T);
				for (int32 k = 0; k < 16; ++k)
				{
					const FVector Side = FRotator(0.f, 45.f * (k % 8), 0.f).Vector() * (k < 8 ? 105.f : 150.f);
					const FVector Stand(Goal.X + Side.X, Goal.Y + Side.Y, Loc.Z);
					const FVector StandEye = Stand + FVector(0, 0, 66.f);
					FHitResult H2;
					if (GetWorld()->LineTraceSingleByChannel(H2, StandEye, Goal, ECC_Visibility, Q)) continue;                         // cannot see it from there
					if (GetWorld()->SweepSingleByChannel(H2, Loc, Stand, FQuat::Identity, ECC_Pawn, FCollisionShape::MakeSphere(26.f), Q)) continue;   // cannot walk straight there
					AutoPath.Reset(); AutoPath.Add(Stand - FVector(0, 0, 88.f)); AutoPathIndex = 0;
					UE_LOG(LogWCAuto, Display, TEXT("WCAUTO stepping round to see %s"), *S.Arg.ToString());
					break;
				}
			}
		}
		if (!bToUse && D2 < Reach && FMath::Abs(Loc.Z - 88.f - Goal.Z) < 160.f) { Next(); return; }

		if (AutoPath.Num() == 0)
		{
			AutoPathIndex = 0;
			AutoRoute(Loc, Goal, AutoPath);
		}
		while (AutoPathIndex < AutoPath.Num() - 1 && FVector::Dist2D(Loc, AutoPath[AutoPathIndex]) < 40.f && FMath::Abs(Loc.Z - 88.f - AutoPath[AutoPathIndex].Z) < 150.f) ++AutoPathIndex;
		const FVector Way = AutoPath[FMath::Min(AutoPathIndex, AutoPath.Num() - 1)];
		const FVector Dir = (Way - Loc).GetSafeNormal2D();
		if (AController* C = P->GetController())
		{
			const FRotator Want(FMath::Clamp((Way.Z - Loc.Z) * 0.05f, -25.f, 25.f) - 4.f, Dir.Rotation().Yaw, 0.f);
			C->SetControlRotation(FMath::RInterpTo(C->GetControlRotation(), Want, Dt, 6.f));
		}
		P->AddMovementInput(Dir, 1.f);

		// open what is in the way, the same way a player would (E on the door)
		for (TActorIterator<AWCDoor> It(GetWorld()); It; ++It)
		{
			if ((It->IsOpen() && !It->IsAjar()) || !It->CanInteract()) continue;
			FVector O, E; It->GetActorBounds(true, O, E);
			if (FVector::Dist2D(O, Loc) < 135.f && FMath::Abs(O.Z - Loc.Z) < 150.f && (!It->bLocked || HasItem(It->KeyId)))
			{
				It->Interact(P);
				UE_LOG(LogWCAuto, Display, TEXT("WCAUTO opened door %s"), *It->WCId.ToString());
			}
		}

		if (Clock - AutoStuckAt > 3.0)
		{
			if (FVector::Dist(Loc, AutoStuckLoc) < 35.f)
			{
				++AutoStuckCount;
				UE_LOG(LogWCAuto, Warning, TEXT("WCAUTO STUCK #%d at %s going to %s (step %d)"), AutoStuckCount, *Loc.ToString(), *S.Arg.ToString(), AutoIndex);
				AutoPath.Reset();
				if (In > 25.0)
				{
					{
						FHitResult Hit;
						FCollisionQueryParams Q(SCENE_QUERY_STAT(WCAutoWall), false, P);
						const FVector From = Loc - FVector(0, 0, 30.f);
						(void)From;
						// his own capsule, lifted a hand's breadth so the floor he stands on does not count, pushed the way he is trying to go
						const FCollisionShape Cap = FCollisionShape::MakeCapsule(P->GetCapsuleComponent()->GetScaledCapsuleRadius() - 1.f, P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() - 12.f);
						const FVector Up0 = Loc + FVector(0, 0, 14.f);
						const bool bHit = GetWorld()->SweepSingleByChannel(Hit, Up0, Up0 + Dir * 60.f + FVector(0, 0, 50.f), FQuat::Identity, ECC_Pawn, Cap, Q);
						UE_LOG(LogWCAuto, Error, TEXT("WCAUTO WHY %s: walking into %s (%s) %.0f cm ahead, touching at (%.0f,%.0f,%.0f)%s; he is at (%.0f,%.0f,%.0f) heading (%.2f,%.2f)"), *S.Arg.ToString(),
							bHit && Hit.GetActor() ? *Hit.GetActor()->GetActorNameOrLabel() : TEXT("nothing found"), bHit && Hit.GetComponent() ? *Hit.GetComponent()->GetName() : TEXT("-"), bHit ? Hit.Distance : -1.f,
							Hit.ImpactPoint.X, Hit.ImpactPoint.Y, Hit.ImpactPoint.Z, bHit && Hit.bStartPenetrating ? TEXT(" (already inside it)") : TEXT(""), Loc.X, Loc.Y, Loc.Z, Dir.X, Dir.Y);
					}
					UE_LOG(LogWCAuto, Error, TEXT("WCAUTO FAIL unreachable %s%s"), *S.Arg.ToString(), bForce ? TEXT(" -> teleported") : TEXT(""));
					if (bForce)
					{
						TArray<FVector> Route;
						AutoRoute(Goal + FVector(0, 0, 88), Goal, Route);      // nearest waypoint to the goal comes first
						const FVector Land = Route.Num() > 1 ? Route[0] : Goal;
						P->TeleportToCheckpoint(Land + FVector(0, 0, 96), P->GetControlRotation().Yaw);
					}
					Next();
					return;
				}
			}
			AutoStuckAt = Clock;
			AutoStuckLoc = Loc;
		}
	}
}
