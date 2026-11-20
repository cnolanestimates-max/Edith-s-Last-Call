// The story director. One per level (spawned by the game mode).
// Owns: story state (flags, items, objective), scripted scares, dialogue + subtitles, sound, checkpoints,
// menus' game flow, and the automatic play-through used for testing.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameFramework/SaveGame.h"
#include "WCDirector.generated.h"

class AWCCharacter;
class AWCEntity;
class AWCNote;
class AWCDoor;
class AWCInteractable;
class AWCTrigger;
class USoundBase;
class UAudioComponent;
class USoundAttenuation;

UENUM()
enum class EWCMode : uint8 { Menu, Playing, Ending, Credits };

enum class EWCSnd : uint8 { SFX, Music, Voice };

/** Player options. Stored in the user's GameUserSettings.ini under [WellnessCheck]. */
struct FWCSettings
{
	float Sensitivity = 1.f;
	bool bInvertY = false;
	float FOV = 85.f;
	float Gamma = 2.2f;
	static constexpr int32 BeamChoices = 5;
	int32 BeamChoice = 4;       // E: 60% wider than the original flashlight.
	int32 BeamWidthPercent() const { return 20 + 10 * BeamChoice; }
	FString BeamLabel() const { return FString::Printf(TEXT("%c  (+%d%%)"), 'A' + BeamChoice, BeamWidthPercent()); }
	float VolMaster = 1.f;
	float VolSFX = 1.f;
	float VolMusic = 0.8f;
	float VolVoice = 1.f;
	bool bSubtitles = true;
	bool bHeadBob = true;
	bool bCameraShake = true;
	int32 Filter = 1;           // picture: 0 clean, 1 VHS camcorder (Cheyenne's pick), 2 old film, 3 cold, 4 fisheye bodycam, 5 night vision
	int32 Quality = 2;          // 0 low .. 3 epic
	bool bFullscreen = true;
	bool bVSync = true;
	void Load();
	void Save() const;
	void Apply(UObject* WorldContext) const;
	void ApplyDisplayMode(UWorld* World) const;
};

UCLASS()
class WELLNESSCHECK_API UWCSave : public USaveGame
{
	GENERATED_BODY()
public:
	UPROPERTY() int32 Version = 1;
	UPROPERTY() int32 YardCawsLeft = -1;
	UPROPERTY() TArray<FName> Flags;
	UPROPERTY() TArray<FName> Items;
	UPROPERTY() TArray<FName> NotesRead;
	UPROPERTY() TArray<FName> OpenDoors;
	UPROPERTY() TArray<FName> UnlockedDoors;
	UPROPERTY() FString Objective;
	UPROPERTY() FVector PlayerLoc = FVector::ZeroVector;
	UPROPERTY() float PlayerYaw = 0.f;
	UPROPERTY() int32 Ammo = 8;
	UPROPERTY() int32 Reserve = 16;
	UPROPERTY() float PlaySeconds = 0.f;
	UPROPERTY() FName Checkpoint;
	UPROPERTY() bool bLightOn = true;
};

struct FWCSubtitle
{
	FString Speaker;
	FString Text;
	double Until = 0.0;
};

UCLASS()
class WELLNESSCHECK_API AWCDirector : public AActor
{
	GENERATED_BODY()
public:
	AWCDirector();
	static AWCDirector* Get(const UObject* WorldContext);
	virtual void Tick(float Dt) override;

	// ------------------------------------------------------------------ flow
	EWCMode Mode = EWCMode::Menu;
	bool IsPlaying() const { return Mode == EWCMode::Playing; }
	void StartNewGame();
	void ContinueGame();
	bool HasSave() const;
	void RestartFromCheckpoint();
	void QuitToMenu();
	static FWCSettings Settings;
	/** What to do after the level (re)loads: 0 menu, 1 new game, 2 continue. */
	static int32 PendingStart;

	// ------------------------------------------------------------------ story state
	void Event(FName Id);
	bool Has(FName Flag) const { return Flags.Contains(Flag); }
	void Set(FName Flag) { Flags.Add(Flag); }
	bool HasItem(FName Item) const { return Items.Contains(Item); }
	void GiveItem(FName Item, const FString& DisplayName);
	void SetObjective(const FString& Text);
	void Checkpoint(FName Id);
	FString Objective;
	double ObjectiveShownAt = -100.0;
	TSet<FName> Flags;
	TSet<FName> Items;
	TArray<FName> NotesRead;
	float PlaySeconds = 0.f;

	// ------------------------------------------------------------------ notes / UI state read by the HUD
	void OpenNote(AWCNote* Note);
	void CloseNote();
	TWeakObjectPtr<AWCNote> ActiveNote;
	TArray<FWCSubtitle> Subtitles;
	FString Toast;
	double ToastUntil = 0.0;
	void ShowToast(const FString& Text, float Seconds = 3.f);
	FString Hint;
	double HintUntil = 0.0;
	void ShowHint(const FString& Text, float Seconds = 6.f);
	float Fade = 1.f;          // 1 = black
	float FadeTarget = 0.f;
	float FadeRate = 1.f;
	void FadeTo(float Target, float Seconds);
	FString BigText;           // title cards ("WELLNESS CHECK", "You stayed.")
	FString BigSub;
	float BigAlpha = 0.f;
	float BigTarget = 0.f;
	float CreditsScroll = -1.f;
	double Now() const { return Clock; }

	// ------------------------------------------------------------------ sound
	USoundBase* Snd(const FString& Name);
	UAudioComponent* Play2D(const FString& Name, float Volume = 1.f, EWCSnd Cat = EWCSnd::SFX, float Pitch = 1.f);
	UAudioComponent* PlayAt(const FString& Name, const FVector& Where, float Volume = 1.f, float Pitch = 1.f, float Radius = 1800.f, bool bShedImpact = false);
	/** Looping bed in a named slot; an empty name fades the slot out. */
	void SetLoop(FName Slot, const FString& Name, float Volume, float FadeSeconds = 2.f, EWCSnd Cat = EWCSnd::SFX);
	void Footstep(const FVector& Feet, float Loud, FName Surface);
	/** Speak a line (see WCStory.cpp line table). Returns the time offset at which it ends. */
	float Say(FName LineId, float Delay = 0.f);
	float LineSeconds(FName LineId);
	/** A line of on-screen text with no voice: what he notices. */
	void Think(const FString& Text, float Seconds = -1.f);      // his thoughts: no longer shown (kept in the code as a record of what each moment is)
	void Feedback(const FString& Text, float Seconds = -1.f);   // bare feedback on something he tried, and what he sees when the player chooses to look
		bool Gate() const { return Clock >= NextScareAt && StalkState == 0 && !bDriving && !bEventBusy; }
	void Rest(float Seconds) { NextScareAt = FMath::Max(NextScareAt, Clock + Seconds * 1.6f * TestPace); }       // 1.6: she asked for them further apart
	/** Run Go at the next quiet stretch (now, if it is quiet). If Valid turns false first, run Skip instead. */
	void WhenQuiet(TFunction<void()> Go, TFunction<bool()> Valid, TFunction<void()> Skip, float MaxWait);
	struct FDeferred { TFunction<void()> Go; TFunction<bool()> Valid; TFunction<void()> Skip; double Deadline = 0.0; };
	TArray<FDeferred> Deferred;
	void CellarSprint();
	void CellarQuiet();
	void AtticCrawl();
	float TestPace = 1.f;
	double NextScareAt = 0.0;
	float LockInDist0 = 0.f;
	bool bLockInRun = false;
	double UpstairsAt = -1.0;
	float InsideAt = 0.f;
	void ApplyVolumes();
	float Vol(EWCSnd Cat) const;

	// ------------------------------------------------------------------ helpers for the story script
	void After(float Delay, TFunction<void()> Fn);
	AWCCharacter* Player() const;
	AWCEntity* Her() const { return HerActor.Get(); }
	AActor* Find(FName Tag) const;
	FVector Pos(FName Tag) const;
	float YawOf(FName Tag) const;
	AWCDoor* Door(FName Id) const;
	AWCInteractable* Thing(FName Id) const;
	void ShowTagged(FName Tag, bool bShow);
	void SetLightsTagged(FName Tag, float Scale);
	bool PlayerSees(const FVector& Point, float MinDot = 0.6f, float MaxDist = 3000.f) const;
		float Tension = 0.f;      // 0 calm .. 1 frantic; drives ambience, breathing, random cues

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
	bool IsInsideHouse(const FVector& At) const { return SpaceAt(At) != EListeningSpace::Exterior; }
	bool IsBinTurnActive() const { return BinTurnStarted >= 0.; }
	bool IsDriving() const { return bDriving; }
	bool bPowerOut = false;
	int32 StalkState = 0;     // 0 none, 1 she has appeared, 2 she is coming
	TSet<FName> LooksSeen;
	bool bBusy = false;       // a scripted sequence owns the player; triggers wait

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;

private:
	// story (WCStory.cpp)
	void StoryBegin(bool bFromSave);
	void StartFromMenu(bool bContinue);
	void StoryEvent(FName Id);
	void StoryTick(float Dt);
	void ApplyWorldState();
	void BeginEnding();
	// scares
	void ScarePeek();
	void ScareLockIn();
	void ScarePhone();
	void ScareCeiling();
	void ScareUnderBed();
	void ScareAttic();
	void ScareCellarDoor();
		void FinaleStep(int32 Knot);
	void FinaleCaught();
	void ScareSewing();
	void ScareBook();
	/** She has him: she screams in his face for Hold seconds (the view is pulled to her), then Then() runs. */
	void Grab(float Hold, TFunction<void()> Then);
	double GrabHoldUntil = 0.0;
	FVector LookAtPoint = FVector::ZeroVector;
	double LookAtUntil = 0.0;
	double BinTurnStarted = -1.;
	bool bStepToShedDoor = false;
	void TickBinTurn(float Dt);
	void SetReturnBlackout(bool bActive);
	TWeakObjectPtr<class UStaticMeshComponent> VentTool;
	double VentToolAt = 0.;
	void TickVentTool();
	/** A memory of hers (1 family leaving, 2 the book in the attic, 3 the asking), shown from a fixed camera, then Then(). */
	void PlayMemory(int32 N, TFunction<void()> Then);
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
	bool bParkedCarCollision = false;
	TArray<FVector> DrivePts;
	TArray<float> DriveLen;
	float DriveTotal = 0.f, DriveDist = 0.f, DriveSpeed = 0.f, DriveHeading = 0.f;
	// things that act by themselves (WCEvents.cpp)
	bool bEventBusy = false;                  // one of them is playing: no other scare and no hunt starts
	int32 RecordPhase = 0;
	double RecordAt = 0.0, RecordSeenAt = -1.0;
	TWeakObjectPtr<UAudioComponent> RecordAudio;
	void TickRecord(float Dt);
	void RecordPlay(bool bOn);
	bool EventsEvent(FName Id);
	void LeftScare();
	// the television
	int32 TVPhase = 0, TVTape = 0, TVLoop = -1, TVTapeNow = 1;              // 0 off, 1 playing, 2 the reflection
	double TVAt = 0.0, TVNextAt = -1.0, TVHerAt = -1.0, TVRunAt = -1.0;
	TWeakObjectPtr<UAudioComponent> TVAudio;
	UPROPERTY(Transient) TObjectPtr<class UMaterialInstanceDynamic> TVScreen;
	UPROPERTY(Transient) TObjectPtr<class UPointLightComponent> TVGlow;
	UPROPERTY(Transient) TObjectPtr<class UPointLightComponent> TVHerLight;
	UPROPERTY(Transient) TObjectPtr<class USceneCaptureComponent2D> TVCapture;
	UPROPERTY(Transient) TObjectPtr<class UTextureRenderTarget2D> TVTarget;
	void TickTV(float Dt);
	void AtticTagsTaken();
	void OutsideProgress();
	bool DoorOpensByItself();
	void UpstairsThump();
	void CueEvent(FName Id);
	void TickCues(float Dt);
	void TickHallClock();
	void TickYardCrows();
	int32 YardCawsLeft = -1;
	double NextYardCaw = -1.;
	TWeakObjectPtr<UAudioComponent> YardCrowVoice;
	double NextHallTick = -1.;
	int32 ExtraHallTicks = 0;
	TMap<FName, int32> CueCount;
	TSet<int32> CueFired;
	TSet<FName> TrigInside;
	double CueFreeAt = 0.0, WhisperAt = -1.0, NextFlyBuzz = 0., DialogueUntil = 0.;
	int32 LastHaunt = -1;
	TWeakObjectPtr<UAudioComponent> FlyVoice;
	void FinaleDawn();
	int32 DoorEvents = 0, CallStep = 0;
	int32 TVWant = 0;                                          // the tape he has just put in (0 = none)
	// (the recorder is part of the television's own model)
	double NextDoorAt = -1.0;
	bool bDev = false;
	// the eye in the dark (S14)
	void TickEye(float Dt);
	/** Whole-game picture filter: 0 off, 1 VHS camcorder, 2 old film, 3 cold and drained, 4 fisheye bodycam, 5 black-and-white night vision. */
	public:
	void SetFilter(int32 Look);
private:
	int32 FilterLook = 0;
	bool bFilterInit = false;
	UPROPERTY(Transient) TObjectPtr<class APostProcessVolume> FilterVolume;
	UPROPERTY(Transient) TObjectPtr<class UMaterialInstanceDynamic> FilterMID;
	bool EyeTry(bool bForce);
	void EyeEnd(bool bSeenTwice);
	int32 EyePhase = 0;                         // 0 waiting, 1 black, 2 the eye, 3 light back and nothing there, 4 the eye again, 5 going out
	double EyeAt = 0.0, EyeNextAt = -1.0;
	FVector EyeSpot = FVector::ZeroVector;
	bool bEyeLooked = false;
	void TVOn();
	void TVOff(bool bByHim, bool bForceScare = false);
	void TVReflectionEnd();
	float ShadowDist = -1.f, ShadowT = 0.f;       // the thing on the road: how far along it stands; time in the present phase
	int32 ShadowPhase = 0;                        // 0 not reached, 1 rolling to a stop, 2 stopped and looking back, 3 driving on
	TWeakObjectPtr<AActor> Car;
	TWeakObjectPtr<AActor> Seat;
	TWeakObjectPtr<class ACameraActor> DriveCam;
	// the opening shot from the air: seconds into it, whether the outside of the car has been swapped for the inside yet
	bool bAir = false, bAirDip = false, bAirSwapped = true;
	float AirT = 0.f, CabinFov = 66.f;
	TWeakObjectPtr<class ADirectionalLight> AirMoon;
	TWeakObjectPtr<class ASkyLight> AirSky;
	float AirMoonBase = 0.f, AirSkyBase = 0.f;
	TArray<TPair<TWeakObjectPtr<class ULightComponent>, float>> AirHeads;
	TArray<TPair<TWeakObjectPtr<class UStaticMeshComponent>, float>> AirTrees;
	TWeakObjectPtr<AActor> AirWood;




	void AirIntoCar();

	FVector CarHome = FVector::ZeroVector;
	FRotator CarHomeRot = FRotator::ZeroRotator;
	TArray<FVector> NavPts;
	double NextLightKill = 0.0;
	double NextBoardCreak = 0.0;
	int32 BuildStep = 0;
	TWeakObjectPtr<AActor> RockActor;
	double RockUntil = 0.0;
	FRotator RockBase = FRotator::ZeroRotator;
	double StalkAt = 0.0, NextStalkAt = 0.0, StalkLostAt = 0.0, StalkRepath = 0.0, StalkPauseUntil = 0.0;
	int32 StalkHits = 0, StalkNeed = 4, StalksDone = 0, Catches = 0;
	bool bAmbush = false;
	// auto play (WCAuto.cpp)
	void AutoBegin();
	void AutoTick(float Dt);
	void AutoRoute(const FVector& From, const FVector& Goal, TArray<FVector>& Out);

	enum class EListeningSpace : uint8 { Exterior, House, Cellar };
	EListeningSpace ListeningSpace = EListeningSpace::Exterior;
	static EListeningSpace SpaceAt(const FVector& Position);
	void RefreshRoomTone(EListeningSpace Space);
	void PlayScareLead(float Seconds);
	TWeakObjectPtr<UAudioComponent> ScareLead;
	void TickAudio(float Dt);
	void TickLights(float Dt);
	void TickFlies(float Dt);
	UPROPERTY(VisibleAnywhere) TObjectPtr<class UInstancedStaticMeshComponent> Flies;
	struct FFly { FVector Centre; FVector Radii; FVector Freq; FVector Phase; };
	TArray<FFly> FlyData;
	struct FLive { TWeakObjectPtr<class ULightComponent> Light; float Base = 0.f; float Seed = 0.f; int32 Kind = 0; };
	TArray<FLive> LiveLights;
	TArray<TWeakObjectPtr<AActor>> BarMeshes[2];
	void TickTriggers();
	void DoSave(FName Id);
	bool DoLoad();

	struct FStep { double At; TFunction<void()> Fn; };
	TArray<FStep> Steps;
	struct FLoop { TWeakObjectPtr<UAudioComponent> Audio; float Vol = 0.f; float Target = 0.f; float Rate = 1.f; EWCSnd Cat = EWCSnd::SFX; FString Name; };
	TMap<FName, FLoop> Loops;
	struct FVoice { TWeakObjectPtr<UAudioComponent> Audio; EWCSnd Cat; float Base; };
	TArray<FVoice> Live;
	UPROPERTY(Transient) TMap<FString, TObjectPtr<USoundBase>> SoundCache;
	TMap<FString, TArray<FString>> SoundVariants;
	UPROPERTY(Transient) TObjectPtr<USoundAttenuation> Atten;
	UPROPERTY(Transient) TObjectPtr<USoundAttenuation> BinAtten;
	UPROPERTY(Transient) TObjectPtr<USoundAttenuation> FlyAtten;
	UPROPERTY(Transient) TObjectPtr<USoundAttenuation> CrowAtten;
	TWeakObjectPtr<AWCEntity> HerActor;
	TArray<TWeakObjectPtr<AWCTrigger>> Triggers;
	TMap<FName, TWeakObjectPtr<AActor>> TagCache;
	double Clock = 0.0;
	double NextCue = 20.0;
	double NextTrigPoll = 0.0;
	double SpeechFreeAt = 0.0;
	FName LastCheckpoint;
	FRandomStream Rng;

	// story scratch
	int32 KnotsCut = 0;
	double FinaleStart = -1.0;
	double LockInStart = -1.0;
	double SprintStart = -1.0;
	double SprintRetarget = 0.0;
	double HerNextStep = 0.0;
	int32 ShotsAtHer = 0;
	int32 LockInShots = 0;
	bool bLockInActive = false;
	bool bSprintActive = false;
	TFunction<void()> OnHerArrive;

	// auto play
	struct FAuto { int32 Type; FName Arg; float F; };
	TArray<FAuto> AutoSteps;
	int32 AutoIndex = -1;
	double AutoStepStart = 0.0;
	double AutoStuckAt = 0.0;
	FVector AutoStuckLoc = FVector::ZeroVector;
	TArray<FVector> AutoPath;
	int32 AutoPathIndex = 0;
	FString AutoShotDir;
	int32 AutoStuckCount = 0;
		bool bAuto = false;
	bool bAutoDefending = false;
	TArray<float> PerfFrames;
	double PerfLast = 0.0;
	void PerfReport(const TCHAR* Label, bool bReset);
	friend class AWCHUD;
};
