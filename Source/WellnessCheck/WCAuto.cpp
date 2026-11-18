// Automatic play-through for testing (-WCAuto, optional -WCShots=<dir>, -WCAutoForce).
// It drives the real pawn: walks with movement input along nav paths, aims the camera, presses "use" through the
// same trace the player uses, raises and fires the pistol. It is a route check and evidence recorder, not a
// substitute for a person playing: it knows the solution and never gets lost.
#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"

#include "EngineUtils.h"
#include "Components/PointLightComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "HAL/FileManager.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Misc/CommandLine.h"
#include "Misc/Paths.h"
#include "NavigationPath.h"
#include "NavigationSystem.h"
#include "UnrealClient.h"

DEFINE_LOG_CATEGORY_STATIC(LogWCAuto, Log, All);

enum { A_Go, A_Use, A_Wait, A_WaitFlag, A_Shot, A_Fire, A_Look, A_Light, A_LookHer, A_WaitHer, A_Crouch, A_Tele, A_Her, A_FaceItem, A_Aim };

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
		if (FParse::Param(FCommandLine::Get(), TEXT("WCBright")))
		{
			if (AWCCharacter* Pl = Player())
			{
				UPointLightComponent* L = NewObject<UPointLightComponent>(Pl);
				L->SetupAttachment(Pl->GetRootComponent());
				L->SetRelativeLocation(FVector(0, 0, 60));
				L->RegisterComponent();
				L->SetIntensityUnits(ELightUnits::Lumens);
				L->SetIntensity(1800.f);
				L->SetAttenuationRadius(2500.f);
				L->SetCastShadows(false);
			}
		}
		if (FParse::Param(FCommandLine::Get(), TEXT("WCLights")))
		{
			for (TPair<FName, FRoomLights>& Rm : Rooms) SwitchRoom(Rm.Key, true, false);
			if (AWCCharacter* Pl = Player()) Pl->SetFlashlight(false, false);
		}
		Wait(4.f);
		for (const FName& N : Names) { AutoSteps.Add({ A_Tele, N, 0.f }); Wait(2.6f); Shot(*N.ToString()); }
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
		if (FParse::Param(FCommandLine::Get(), TEXT("WCHerLook")))
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
	Use(TEXT("front")); Flag(TEXT("door_opened"), 30.f); Wait(4.f); Shot(TEXT("03_door_ajar"));
	Use(TEXT("front")); Wait(2.f);
	Go(TEXT("A_Foyer")); Flag(TEXT("inside"), 10.f); Wait(3.f); Shot(TEXT("04_foyer"));
	Use(TEXT("sw_hall")); Wait(1.6f); Shot(TEXT("04b_hall_light"));
	Flag(TEXT("locked_in"), 60.f); Wait(2.f); Use(TEXT("front")); Flag(TEXT("door_stuck"), 10.f); Wait(9.f);
	// ---- ground floor, front
	Go(TEXT("A_Living")); Use(TEXT("sw_living")); Wait(2.f); Shot(TEXT("05_living")); Use(TEXT("note_letter1")); Wait(1.f); Shot(TEXT("06_note")); Close();
	Use(TEXT("look_piano")); Wait(1.6f); Shot(TEXT("06b_look"));
	Go(TEXT("A_Dining")); Wait(2.f); Shot(TEXT("07_dining")); Use(TEXT("look_dining_table")); Wait(1.5f);
	Go(TEXT("A_Kitchen")); Use(TEXT("sw_kitchen")); Wait(2.f); Shot(TEXT("08_kitchen")); Use(TEXT("phone")); Wait(3.f);
	// ---- ground floor, rear wing
	Go(TEXT("A_Pantry")); Wait(1.5f); Shot(TEXT("08b_pantry")); Use(TEXT("fusebox")); Wait(1.5f);
	Go(TEXT("A_Den")); Use(TEXT("sw_den")); Wait(2.f); Shot(TEXT("08c_den")); Use(TEXT("pick_fuse")); Use(TEXT("desk")); Wait(1.5f); Use(TEXT("note_doctor")); Wait(1.f); Close();
	Go(TEXT("A_BathG")); Wait(1.5f); Shot(TEXT("08d_bath"));
	Go(TEXT("A_Sickroom")); Use(TEXT("sw_sickroom")); Wait(2.f); Shot(TEXT("08e_sickroom")); Use(TEXT("note_aide1")); Wait(1.f); Close(); Use(TEXT("look_sick_bed")); Wait(1.5f);
	// ---- the long quiet, then the thump
	Flag(TEXT("heard_upstairs"), 55.f * Slow); Wait(14.f);
	// ---- upstairs: S1
	Go(TEXT("A_StairsTop")); Go(TEXT("N_up_hallB")); Flag(TEXT("peek_started"), 30.f); LookHer(1.0f); Shot(TEXT("09_S1_peek")); LookHer(2.5f);
	Flag(TEXT("peek_done"), 40.f); Wait(5.f);
	Go(TEXT("A_Master")); Flag(TEXT("master_seen"), 10.f); Shot(TEXT("10_master")); Flag(TEXT("want_leave"), 60.f);
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
	Use(TEXT("pick_key_sitting")); Use(TEXT("sitting")); Wait(3.f);
	Go(TEXT("A_Sitting")); Wait(3.f); Shot(TEXT("16_sitting")); Use(TEXT("note_diary2")); Wait(1.f); Close();
	Use(TEXT("pick_key_prayer")); Use(TEXT("note_deskkey")); Wait(1.f); Close();
	Go(TEXT("A_Den")); Use(TEXT("book_settlers")); Flag(TEXT("book_done"), 6.f); Wait(0.9f); Shot(TEXT("16b_S10_book_eye")); Wait(3.f); Shot(TEXT("16c_S10_after"));
	Use(TEXT("pick_key_desk")); Use(TEXT("desk")); Flag(TEXT("desk_open"), 6.f); Wait(2.f);
	// ---- S4: the head by the ceiling
	Go(TEXT("A_StairsTop")); Flag(TEXT("ceiling_started"), 20.f * Slow); LookHer(2.5f); Shot(TEXT("17_S4_ceiling")); LookHer(7.5f); Shot(TEXT("18_S4_sprint")); LookHer(3.f);
	Flag(TEXT("ceiling_done"), 40.f); Wait(8.f);
	// ---- S7: under the bed
	Flag(TEXT("kids_open"), 20.f * Slow); Go(TEXT("A_Kids")); Flag(TEXT("underbed_done"), 30.f); Wait(4.6f); Shot(TEXT("19_S7_hand_out")); Wait(2.6f); Shot(TEXT("20_S7_hand_takes")); Wait(4.f);
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
	Use(TEXT("up_attic")); Go(TEXT("A_Attic")); Wait(2.f); Shot(TEXT("22_attic")); Use(TEXT("trunk")); Flag(TEXT("attic_started"), 5.f);
	WaitHer(25.f); LookHer(1.2f); Shot(TEXT("23_S5_crawl")); LookHer(2.2f); Shot(TEXT("24_S5_rise")); Flag(TEXT("attic_done"), 30.f); Wait(8.f);
	// ---- S6: the cellar door
	Use(TEXT("cellar")); Flag(TEXT("sprint_started"), 10.f); WaitHer(12.f); LookHer(0.7f); Shot(TEXT("25_S6_sprint")); LookHer(4.f);
	Flag(TEXT("sprint_done"), 40.f); Wait(5.f); Shot(TEXT("26_cellar"));
	// ---- finale
	Go(TEXT("A_CellarShelf")); Use(TEXT("shelf")); Wait(5.f); Go(TEXT("A_Root")); Flag(TEXT("seen_body"), 10.f); Wait(6.f); Shot(TEXT("27_body"));
	Use(TEXT("place")); Flag(TEXT("placed"), 5.f); Wait(9.f); LookHer(1.f); Shot(TEXT("28_S8_far"));
	Use(TEXT("knot1")); Flag(TEXT("knot1"), 8.f); Wait(3.f); LookHer(1.f); Shot(TEXT("29_S8_mid"));
	Use(TEXT("knot2")); Flag(TEXT("knot2"), 8.f); Wait(4.5f); LookHer(1.f); Shot(TEXT("30_S8_near"));
	Use(TEXT("knot3")); Flag(TEXT("finale_done"), 8.f); Wait(2.2f); Shot(TEXT("31_S8_face"));
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
	if (A == INDEX_NONE || B == INDEX_NONE || (FVector::Dist2D(Feet, Goal) < 260.f && FMath::Abs(Feet.Z - Goal.Z) < 130.f)) { Out.Add(Goal); return; }
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
	case A_Tele:
		if (AActor* T = AutoTarget(this, S.Arg)) P->TeleportToCheckpoint(T->GetActorLocation(), T->GetActorRotation().Yaw);
		Next(); return;
	case A_Light: if (!P->IsFlashlightOn()) P->ToggleFlashlight(); Next(); return;
	case A_Shot:
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
		if (bToUse && FVector::Dist(P->EyeLocation(), Goal) < P->InteractRange - 45.f) { Next(); return; }
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
