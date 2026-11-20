// The story of Wellness Check, as code: dialogue lines, objectives, the eight major scares, the finale and ending.
// World actors are found by WCId / tag; the level build script (Scripts/level/build_house.py) creates them.
#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"

#include "Components/AudioComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Camera/CameraActor.h"
#include "Camera/CameraComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/SpotLightComponent.h"
#include "Components/PointLightComponent.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Materials/MaterialInterface.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "Engine/PostProcessVolume.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Sound/SoundBase.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"

DEFINE_LOG_CATEGORY_STATIC(LogWCStory, Log, All);

// ---------------------------------------------------------------------------------------------- lines
// Kind: 0 deputy (close), 1 dispatch over the radio, 2 Edith heard everywhere, 3 Edith from where she stands, 4 Edith on the phone
struct FWCLine { const TCHAR* Id; const TCHAR* Speaker; const TCHAR* Text; int32 Kind; };

static const FWCLine GLines[] = {
	{ TEXT("d_arrive1"), TEXT("Deputy Brandt"), TEXT("Dispatch, Fourteen. I'm out on County Road Nine, coming up on the Harrow place."), 0 },
	{ TEXT("r_arrive1"), TEXT("Dispatch"), TEXT("Copy, Fourteen. Caller asked for a welfare check on an Edith Harrow, seventy-two, lives alone. Family's out of state. Nobody's laid eyes on her in months."), 1 },
	{ TEXT("d_arrive2"), TEXT("Deputy Brandt"), TEXT("Copy. House is dark. No lights, no vehicle."), 0 },
	{ TEXT("r_arrive2"), TEXT("Dispatch"), TEXT("Caller didn't leave a name, Fourteen. Gave the address, said she needs company, and hung up."), 1 },
	{ TEXT("d_arrive3"), TEXT("Deputy Brandt"), TEXT("...Needs company. Copy."), 0 },
	{ TEXT("r_arrive3"), TEXT("Dispatch"), TEXT("Check on her and call it in."), 1 },
	{ TEXT("d_arrive4"), TEXT("Deputy Brandt"), TEXT("Ten-four. Going to the door."), 0 },
	{ TEXT("d_leave_early"), TEXT("Deputy Brandt"), TEXT("Not until I've laid eyes on her."), 0 },
	{ TEXT("d_knock"), TEXT("Deputy Brandt"), TEXT("Sheriff's office! Mrs. Harrow? Your daughter asked us to check on you."), 0 },
	{ TEXT("d_dooropen"), TEXT("Deputy Brandt"), TEXT("...Door's open. Mrs. Harrow, I'm coming in."), 0 },
	{ TEXT("d_side"), TEXT("Deputy Brandt"), TEXT("It's locked. ...Maybe I'll check around the side."), 0 },
	{ TEXT("d_openup"), TEXT("Deputy Brandt"), TEXT("Mrs. Harrow, people are worried about you. We're just trying to see if you're okay. ...Can you please open up?"), 0 },

	{ TEXT("d_call1"), TEXT("Deputy Brandt"), TEXT("Mrs. Harrow?"), 0 },
	{ TEXT("d_call2"), TEXT("Deputy Brandt"), TEXT("Hello? ...Anybody home?"), 0 },
	{ TEXT("d_call3"), TEXT("Deputy Brandt"), TEXT("Mrs. Harrow, it's the sheriff's office. Can you hear me?"), 0 },
	{ TEXT("d_shedcall"), TEXT("Deputy Brandt"), TEXT("Jesus Christ! ...Who's there?! Sheriff's department! ...Mrs. Harrow? ...Is that you?"), 0 },
	{ TEXT("d_foyer"), TEXT("Deputy Brandt"), TEXT("God, that smell. ...Mrs. Harrow? Deputy Brandt, sheriff's office."), 0 },
	{ TEXT("d_table"), TEXT("Deputy Brandt"), TEXT("Table's set for four. This food's been sitting here for months."), 0 },
	{ TEXT("d_phonecord"), TEXT("Deputy Brandt"), TEXT("Cord's cut clean through. Nobody called anybody on this."), 0 },
	{ TEXT("d_photos"), TEXT("Deputy Brandt"), TEXT("Every face scratched out. Every one but hers."), 0 },
	{ TEXT("d_cellar_locked"), TEXT("Deputy Brandt"), TEXT("Padlocked. From this side."), 0 },
	{ TEXT("d_locked"), TEXT("Deputy Brandt"), TEXT("Locked."), 0 },
	{ TEXT("d_thump"), TEXT("Deputy Brandt"), TEXT("Mrs. Harrow? ...I'm coming upstairs. Stay where you are."), 0 },
	{ TEXT("m_whisper1"), TEXT(""), TEXT("[a whisper] ...who's there?"), 3 },
	{ TEXT("d_peek"), TEXT("Deputy Brandt"), TEXT("Ma'am? It's alright. I'm here to help you."), 0 },
	{ TEXT("d_getout"), TEXT("Deputy Brandt"), TEXT("Screw this. I'm getting out of here."), 0 },
	{ TEXT("d_masterempty"), TEXT("Deputy Brandt"), TEXT("She was right here. I saw her. There's nowhere to go in here."), 0 },
	{ TEXT("d_radio1"), TEXT("Deputy Brandt"), TEXT("Dispatch, Fourteen. I've got movement in the house. No contact yet."), 0 },
	{ TEXT("r_trace"), TEXT("Dispatch"), TEXT("Fourteen, be advised. We ran the number on that welfare call. It came from Mrs. Harrow's own telephone. From inside that house."), 1 },
	{ TEXT("d_trace"), TEXT("Deputy Brandt"), TEXT("...Say again? That phone's cut off at the wall."), 0 },
	{ TEXT("r_static"), TEXT("Radio"), TEXT("[static] ...stay..."), 1 },
	{ TEXT("d_radio2"), TEXT("Deputy Brandt"), TEXT("Dispatch? ...Dispatch. ...Dead."), 0 },
	{ TEXT("d_doorstuck"), TEXT("Deputy Brandt"), TEXT("It won't... It was open. It was just open!"), 0 },
	{ TEXT("d_stop"), TEXT("Deputy Brandt"), TEXT("Sheriff's office! Ma'am, stop right there!"), 0 },
	{ TEXT("d_stop2"), TEXT("Deputy Brandt"), TEXT("I said stop!"), 0 },
	{ TEXT("d_getup1"), TEXT("Deputy Brandt"), TEXT("What the hell. What the hell was that."), 0 },
	{ TEXT("d_getup1b"), TEXT("Deputy Brandt"), TEXT("Went right through her. Every round."), 0 },
	{ TEXT("d_wayout"), TEXT("Deputy Brandt"), TEXT("Okay. Okay. Back door. There's another way out of here."), 0 },
	{ TEXT("d_backdoor"), TEXT("Deputy Brandt"), TEXT("Nailed shut. From the inside. Every board."), 0 },
	{ TEXT("d_window"), TEXT("Deputy Brandt"), TEXT("Nailed. From the inside."), 0 },
	{ TEXT("d_phone_ring"), TEXT("Deputy Brandt"), TEXT("That phone has no line."), 0 },
	{ TEXT("m_phone1"), TEXT("Edith"), TEXT("You came."), 4 },
	{ TEXT("m_phone2"), TEXT("Edith"), TEXT("Nobody comes. Nobody comes to see me anymore."), 4 },
	{ TEXT("m_phone3"), TEXT("Edith"), TEXT("Sit down. Supper's getting cold."), 4 },
	{ TEXT("d_light_dead"), TEXT("Deputy Brandt"), TEXT("No, no, no. Come on. Come on!"), 0 },
	{ TEXT("d_after_kitchen"), TEXT("Deputy Brandt"), TEXT("Jesus Christ!"), 0 },
	{ TEXT("d_drawer"), TEXT("Deputy Brandt"), TEXT("That drawer was shut."), 0 },
	{ TEXT("d_sitting"), TEXT("Deputy Brandt"), TEXT("Her drawings. The same figure in every one. It gets taller each time."), 0 },
	{ TEXT("d_ceiling"), TEXT("Deputy Brandt"), TEXT("...Edith?"), 0 },
	{ TEXT("d_getup2"), TEXT("Deputy Brandt"), TEXT("She doesn't want me dead. She wants me here."), 0 },
	{ TEXT("d_kidsdoor"), TEXT("Deputy Brandt"), TEXT("That door was locked a minute ago."), 0 },
	{ TEXT("d_musicbox"), TEXT("Deputy Brandt"), TEXT("Ruth's. Her name's scratched in the bottom."), 0 },
	{ TEXT("d_underbed"), TEXT("Deputy Brandt"), TEXT("God!"), 0 },
	{ TEXT("d_prayer"), TEXT("Deputy Brandt"), TEXT("Hair. She tied knots in her own hair. Three of them."), 0 },
	{ TEXT("m_whisper2"), TEXT(""), TEXT("[a whisper] ...is that you, Danny?"), 2 },
	{ TEXT("d_ring"), TEXT("Deputy Brandt"), TEXT("Walter's ring."), 0 },
	{ TEXT("d_attic"), TEXT("Deputy Brandt"), TEXT("A footlocker. Army issue."), 0 },
	{ TEXT("d_tags"), TEXT("Deputy Brandt"), TEXT("Dog tags. Harrow, Daniel W. ...He didn't leave her. He never came home."), 0 },
	{ TEXT("d_after_attic"), TEXT("Deputy Brandt"), TEXT("Padlock key. The cellar. That's where she is."), 0 },
	{ TEXT("d_cellar_open"), TEXT("Deputy Brandt"), TEXT("Okay, Edith. Let's finish this."), 0 },
	{ TEXT("d_cellar"), TEXT("Deputy Brandt"), TEXT("Colder down here."), 0 },
	{ TEXT("d_shelf"), TEXT("Deputy Brandt"), TEXT("There's a draft behind this. And scratches on the floor."), 0 },
	{ TEXT("d_body"), TEXT("Deputy Brandt"), TEXT("Oh, Edith. How long have you been sitting down here."), 0 },
	{ TEXT("d_need"), TEXT("Deputy Brandt"), TEXT("Not yet. I need what was theirs. All three."), 0 },
	{ TEXT("d_place"), TEXT("Deputy Brandt"), TEXT("Walter. Ruth. Daniel. They're here, Edith. They're all here."), 0 },
	{ TEXT("m_fin1"), TEXT("Edith"), TEXT("Don't."), 3 },
	{ TEXT("d_knot1"), TEXT("Deputy Brandt"), TEXT("One."), 0 },
	{ TEXT("m_fin2"), TEXT("Edith"), TEXT("Don't you leave me too."), 3 },
	{ TEXT("d_knot2"), TEXT("Deputy Brandt"), TEXT("Two."), 0 },
	{ TEXT("m_fin3"), TEXT("Edith"), TEXT("Everybody leaves. Everybody leaves!"), 3 },
	{ TEXT("d_knot3"), TEXT("Deputy Brandt"), TEXT("It's alright, Edith. You're not alone. You can let go."), 0 },
	{ TEXT("m_fin4"), TEXT("Edith"), TEXT("STAY!"), 2 },
	{ TEXT("m_end"), TEXT("Edith"), TEXT("...thank you."), 2 },
	{ TEXT("m_left"), TEXT(""), TEXT("You left me. You left me. You left me. You left me."), 2 },
	{ TEXT("m_whyleave"), TEXT("Edith"), TEXT("WHY DID YOU LEAVE ME!"), 3 },
	{ TEXT("m_laugh1"), TEXT(""), TEXT("Heh heh heh heh... hee hee hee."), 2 },
	{ TEXT("m_laugh2"), TEXT(""), TEXT("Hm hm hm hm hm. Ha... ha ha ha."), 2 },
	{ TEXT("m_cry1"), TEXT(""), TEXT("Ohh... oh... oh no... ohh."), 2 },
	{ TEXT("m_cry2"), TEXT(""), TEXT("Hnnh... hh... hh... mmm... hh."), 2 },
	{ TEXT("m_ear1"), TEXT(""), TEXT("Stay."), 2 },
	{ TEXT("m_ear2"), TEXT(""), TEXT("I see you."), 2 },
	{ TEXT("m_ear3"), TEXT(""), TEXT("Don't go."), 2 },
	{ TEXT("m_hum"), TEXT(""), TEXT("Mm mm mmm, mm mm mmm, mmm mm, mmm."), 2 },
	{ TEXT("m_moan1"), TEXT(""), TEXT("Ohhhhhhhhh... ohhhhhhh..."), 2 },
	{ TEXT("m_moan2"), TEXT(""), TEXT("Mmmmmmmmmhhhh... hhhhhnnnnn..."), 2 },
	{ TEXT("m_mem1"), TEXT("Edith"), TEXT("Ruthie. Don't go. Stay for supper. Please. I've set your place."), 2 },
	{ TEXT("m_mem2"), TEXT("Edith"), TEXT("Grandmother Wren's book. ...It will sit with you. It will never go."), 2 },
	{ TEXT("m_mem3"), TEXT("Edith"), TEXT("I only want company. Please. Never let me be alone again."), 2 },
	{ TEXT("d_dawn"), TEXT("Deputy Brandt"), TEXT("It's morning."), 0 },
	{ TEXT("d_end1"), TEXT("Deputy Brandt"), TEXT("Dispatch, Fourteen."), 0 },
	{ TEXT("r_end1"), TEXT("Dispatch"), TEXT("Fourteen, dispatch! Where have you been? You've been off the air almost five hours."), 1 },
	{ TEXT("d_end2"), TEXT("Deputy Brandt"), TEXT("I found her. She's been gone a long time. Send the coroner, and call the daughter."), 0 },
	{ TEXT("r_end2"), TEXT("Dispatch"), TEXT("Copy, Fourteen. ...Stand by. I've got a call coming in on the emergency line."), 1 },
	{ TEXT("r_end3"), TEXT("Dispatch"), TEXT("Fourteen... it's the Harrow number again."), 1 },
	{ TEXT("d_end3"), TEXT("Deputy Brandt"), TEXT("...That's not possible. I'm looking right at the house."), 0 },
	{ TEXT("m_post"), TEXT("Radio"), TEXT("[static] ...come back and visit."), 1 },
};

static const FWCLine* FindLine(FName Id)
{
	for (const FWCLine& L : GLines) if (Id == L.Id) return &L;
	return nullptr;
}

float AWCDirector::LineSeconds(FName LineId)
{
	const FWCLine* L = FindLine(LineId);
	if (!L) return 0.f;
	if (USoundBase* S = Snd(FString::Printf(TEXT("VO/%s"), *LineId.ToString())))
	{
		const float D = S->GetDuration();
		if (D > 0.1f && D < 60.f) return D;
	}
	return 1.0f + 0.062f * FCString::Strlen(L->Text);
}

// Lines that are no longer spoken (Cheyenne: he talks to dispatch and reacts to her, not to every locked door).
static bool IsMuted(FName Id)
{
	// 2026-11-19: only what he says to dispatch and to Edith is left.  Remarks to himself, about what he finds or what it
	// means, are all gone (voice and subtitle).
	static const TSet<FName> Muted = { TEXT("d_locked"), TEXT("d_cellar_locked"), TEXT("d_window"), TEXT("d_backdoor"), TEXT("d_table"),
		TEXT("d_wayout"), TEXT("d_drawer"), TEXT("d_sitting"), TEXT("d_kidsdoor"), TEXT("d_musicbox"), TEXT("d_prayer"), TEXT("d_ring"),
		TEXT("d_attic"), TEXT("d_after_attic"), TEXT("d_cellar"), TEXT("d_shelf"), TEXT("d_dawn"), TEXT("d_need"), TEXT("d_leave_early"), TEXT("d_phone_ring"),
		TEXT("d_phonecord"), TEXT("d_masterempty"), TEXT("d_getup1b"), TEXT("d_getup2"), TEXT("d_tags") };
	return Muted.Contains(Id);
}

void AWCDirector::Think(const FString& Text, float Seconds)
{
	// not shown any more: the player works it out without him pointing at it
}

void AWCDirector::Feedback(const FString& Text, float Seconds)
{
	FWCSubtitle Sub;
	Sub.Text = Text;
	Sub.Until = Clock + (Seconds > 0.f ? Seconds : 2.2f + 0.055f * Text.Len());
	Subtitles.Reset();
	Subtitles.Add(Sub);
}

float AWCDirector::Say(FName LineId, float Delay)
{
	if (IsMuted(LineId)) return Delay;
	const FWCLine* L = FindLine(LineId);
	if (!L) { UE_LOG(LogWCStory, Warning, TEXT("WC: unknown line %s"), *LineId.ToString()); return Delay; }
	const float Len = LineSeconds(LineId);
	const FWCLine Line = *L;
	After(Delay, [this, Line, Len, LineId]()
	{
		DialogueUntil = FMath::Max(DialogueUntil, Clock + Len + .6);
		const FString Asset = FString::Printf(TEXT("VO/%s"), *LineId.ToString());
		if (Line.Kind == 1) Play2D(TEXT("radio_click"), 0.5f);
		if (Line.Kind == 3 && Her() && Her()->IsShown())
		{
			if (USoundBase* S = Snd(Asset)) UGameplayStatics::SpawnSoundAtLocation(this, S, Her()->HeadLocation(), FRotator::ZeroRotator, FMath::Max(Vol(EWCSnd::Voice) * 1.2f, 0.0001f), 1.f, 0.f, Atten);
			Her()->Talk(Len);
			// what she is saying is on her face
			if (LineId == TEXT("m_fin1") || LineId == TEXT("m_fin2")) Her()->SetMood(TEXT("grief"), Len + 1.5f);
			else if (LineId == TEXT("m_fin3") || LineId == TEXT("m_whyleave")) Her()->SetMood(TEXT("rage"), Len + 1.f);
		}

		else Play2D(Asset, 1.f, EWCSnd::Voice);
		FWCSubtitle Sub;
		Sub.Speaker = Line.Speaker;
		Sub.Text = Line.Text;
		Sub.Until = Clock + Len + 0.6f;
		Subtitles.Reset();
		Subtitles.Add(Sub);
		UE_LOG(LogWCStory, Display, TEXT("WCLINE t=%.1f %s"), PlaySeconds, *LineId.ToString());
	});
	return Delay + Len + 0.35f;
}

// ---------------------------------------------------------------------------------------------- begin / world state
void AWCDirector::ApplyWorldState()
{
	// Restore the box to the correct side of the bed edge on Continue as well.
	if (AWCInteractable* Box = Thing(TEXT("pick_keep_ruth")); Box && !BedCamera.IsValid())
	{
		const bool bTaken = HasItem(TEXT("keep_ruth"));
		Box->bEnabled = Has(TEXT("underbed_done")) && !bTaken;
		if (!bTaken) Box->SetActorLocation(Pos(TEXT("Her_Under")) + FVector(0, Has(TEXT("underbed_done")) ? -15.f : 150.f, 1.f));
	}
	ShowTagged(TEXT("Show_drawer"), Has(TEXT("phone_done")));
	UpdateFurniture(0.f, Furniture.IsEmpty());
	RefreshFurnitureLoot();
	ShowTagged(TEXT("Hide_shears"), !HasItem(TEXT("shears")));
	ShowTagged(TEXT("Show_bookkey"), Has(TEXT("book_done")) && !HasItem(TEXT("key_desk")) && !Has(TEXT("desk_open")));
	// The moving desk drawer exposes its keys only once it has cleared the apron.
	ShowTagged(TEXT("Show_jewel"), Has(TEXT("box_open")));
	ShowTagged(TEXT("Show_vent"), Has(TEXT("vent_open")));
	ShowTagged(TEXT("Show_trash"), Has(TEXT("tape1_taken")));
	ShowTagged(TEXT("Hide_trash"), !Has(TEXT("tape1_taken")));
	ShowTagged(TEXT("Show_framefall"), Has(TEXT("frame_fell")));
	ShowTagged(TEXT("Hide_framefall"), !Has(TEXT("frame_fell")));
	if (AWCInteractable* Fr = Thing(TEXT("frame"))) Fr->bEnabled = Has(TEXT("frame_fell")) && !Has(TEXT("frame_seen"));
	ShowTagged(TEXT("Show_ventkey"), Has(TEXT("vent_open")) && !HasItem(TEXT("doll")) && !HasItem(TEXT("doll_empty")) && !Has(TEXT("doll_opened")));
	if (AWCInteractable* Vt = Thing(TEXT("vent"))) { Vt->SetActorHiddenInGame(Has(TEXT("vent_open"))); Vt->SetActorEnableCollision(!Has(TEXT("vent_open"))); Vt->bEnabled = !Has(TEXT("vent_open")); }
	ShowTagged(TEXT("Show_jeweleye"), Has(TEXT("box_open")) && !HasItem(TEXT("keep_eye")) && !Has(TEXT("eye_given")));
	ShowTagged(TEXT("Show_eyegiven"), Has(TEXT("eye_given")));
	if (AWCInteractable* Jb = Thing(TEXT("jewelbox"))) { Jb->SetActorHiddenInGame(Has(TEXT("box_open"))); Jb->SetActorEnableCollision(!Has(TEXT("box_open"))); Jb->bEnabled = !Has(TEXT("box_open")); }
	ShowTagged(TEXT("Show_deskammo"), Has(TEXT("desk_open")) && !Has(TEXT("desk_ammo")));
	ShowTagged(TEXT("Show_trunktags"), Has(TEXT("attic_started")) && !HasItem(TEXT("keep_daniel")));
	ShowTagged(TEXT("Show_trunkkey"), Has(TEXT("attic_started")) && !HasItem(TEXT("key_cellar")));
	if (AWCInteractable* Bk = Thing(TEXT("book_settlers"))) Bk->bEnabled = !Has(TEXT("book_done"));
	ShowTagged(TEXT("SettlersBook"), !Has(TEXT("book_done")) || LastCheckpoint == TEXT("book"));
	ShowTagged(TEXT("L_Welcome"), !Has(TEXT("knocked")));
	if (AWCInteractable* Desk = Thing(TEXT("desk"))) Desk->bEnabled = !Has(TEXT("desk_open"));
	bPowerOut = Has(TEXT("power_out")) && !Has(TEXT("fuse_done"));
	ShowTagged(TEXT("Hide_drawer"), !Has(TEXT("phone_done")));
	for (TActorIterator<APostProcessVolume> It(GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(TEXT("PP_Dawn"))) It->bEnabled = Has(TEXT("dawn"));
	}
	ShowTagged(TEXT("Show_placed"), Has(TEXT("placed")));
	ShowTagged(TEXT("Show_dawn"), Has(TEXT("dawn")));
	ShowTagged(TEXT("Hide_dawn"), !Has(TEXT("dawn")));
	ShowTagged(TEXT("Show_knot1"), !Has(TEXT("knot1")));
	ShowTagged(TEXT("Show_knot2"), !Has(TEXT("knot2")));
	ShowTagged(TEXT("Show_knot3"), !Has(TEXT("knot3")));
	if (Has(TEXT("shelf_moved")))
	{
		if (AWCInteractable* Shelf = Thing(TEXT("shelf")))
		{
			Shelf->SetActorLocation(Pos(TEXT("ShelfOpen")));
			Shelf->bEnabled = false;
		}
	}
	if (AWCInteractable* Phone = Thing(TEXT("phone"))) Phone->bEnabled = !Has(TEXT("phone_done"));
	if (!bDriving && Player()) RefreshRoomTone(SpaceAt(Player()->GetActorLocation()));
	SetLoop(TEXT("wind"), TEXT(""), 0.f, 2.f);          // the chimney-wind loop had a bump in it every few seconds: gone
	SetLoop(TEXT("music"), TEXT(""), 0.f, 2.f, EWCSnd::Music);
	if (AWCCharacter* P = Player()) P->SetGunAllowed(true);
}

void AWCDirector::StoryBegin(bool bFromSave)
{
	if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
	{
		if (APawn* P = PC->GetPawn()) PC->SetViewTargetWithBlend(P, 0.f);
		PC->SetShowMouseCursor(false);
		PC->SetInputMode(FInputModeGameOnly());
	}
	ApplyWorldState();
	Fade = 1.f;
	if (bFromSave)
	{
		RestoreHarrowHints();
		if (Has(TEXT("tape2_played")) && !Has(TEXT("tv_scare"))) Items.Add(TEXT("tape2"));
		UpdateFurniture(0.f,true);
		if (Has(TEXT("phone_ringing")) && !Has(TEXT("phone_done"))) Flags.Remove(TEXT("phone_ringing"));
		if (Has(TEXT("heard_upstairs")) && !Has(TEXT("peek_done")))
		{
			Flags.Remove(TEXT("peek_started"));
			Flags.Remove(TEXT("peek_leaving"));
			SetReturnBlackout(true);
		}
		FadeTo(0.f, 1.5f);
		return;
	}
		AWCCharacter* P = Player();
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
	After(bAuto ? 0.5f : T, [this]()
	{
		// the test bot goes straight in; a person looks round the outside first
		if (bAuto && !FParse::Param(FCommandLine::Get(), TEXT("WCOutside"))) { Set(TEXT("shed_seen")); Set(TEXT("back_tried")); Set(TEXT("knocked_first")); Set(TEXT("tape1_taken")); SetObjective(TEXT("Check on Edith Harrow")); }
		else SetObjective(TEXT("Check on Edith Harrow. Take a look round the outside first."));
		Set(TEXT("briefed"));
	});
}

// ---------------------------------------------------------------------------------------------- events
static bool Is(FName Id, const TCHAR* S) { return Id == S; }

void AWCDirector::TickVentTool()
{
	UStaticMeshComponent* Driver = VentTool.Get();
	if (!Driver) return;
	const float Strokes = FMath::Clamp(float(Clock - VentToolAt) / .42f, 0.f, 3.99f);
	const int32 Screw = FMath::FloorToInt(Strokes);
	const float Phase = FMath::Frac(Strokes);
	const FVector Screws[] = {FVector(-16,3.8,24), FVector(16,3.8,24), FVector(16,3.8,2), FVector(-16,3.8,2)};
	const FVector Current = Screws[Screw];
	const FVector Next = Screws[FMath::Min(Screw+1,3)];
	const FVector Tip = FMath::Lerp(Current, Next, FMath::SmoothStep(.72f, 1.f, Phase));
	const float Lift = Phase > .7f ? 3.f * FMath::Sin(PI*(Phase-.7f)/.3f) : 0.f;
	Driver->SetRelativeLocationAndRotation(Tip + FVector(0,13.f+Lift,0), FRotator(0,-90,360.f*FMath::Min(Phase/.70f,1.f)));
}

/** Something heavy goes over upstairs, a few seconds after he pockets the key. */
void AWCDirector::UpstairsThump()
{
	if (Has(TEXT("heard_upstairs"))) return;
	Set(TEXT("heard_upstairs"));
	SetReturnBlackout(true);
	UE_LOG(LogWCStory, Display, TEXT("WCTHUMP t=%.1f (%.0f s after coming in)"), PlaySeconds, PlaySeconds - InsideAt);
	// Inspect pauses the world. Start the buildup on the first gameplay tick after the key.
	After(0.f, [this]() { PlayScareLead(3.2f); });
	After(3.2f, [this]()
	{
		const FVector Up = Pos(TEXT("Snd_UpstairsThump"));
		PlayAt(TEXT("thump_heavy"), Up, 1.f, 1.f);
		if (AWCCharacter* Pl = Player()) Pl->AddShake(0.53f);
		After(1.25f, [this, Up]()
		{
			if (Has(TEXT("peek_started"))) return;
			PlayAt(TEXT("drag_floor"), Up, .85f);
			if (Player() && Player()->GetActorLocation().Z < 320.f)
			{
				Say(TEXT("d_thump"));
				SetObjective(TEXT("Check upstairs"));
			}
		});
		Tension = 0.3f;
	});
}

/** Outside, before he goes in: what is left to look at (the shed, the back door), then round to the front. */
void AWCDirector::OutsideProgress()
{
	if (Has(TEXT("inside"))) return;
	const bool bShed = Has(TEXT("shed_seen")), bBack = Has(TEXT("back_tried"));
	if (Has(TEXT("tape1_taken"))) SetObjective(TEXT("Go back round to the front door"));
	else if (bShed) SetObjective(TEXT("Search the shed"));
	else if (Has(TEXT("knocked_first"))) SetObjective(bBack ? TEXT("Look in the shed") : TEXT("No answer. Look round the back of the house."));
	UE_LOG(LogWCStory, Display, TEXT("WCOUTSIDE t=%.1f shed %d back door %d"), PlaySeconds, bShed ? 1 : 0, bBack ? 1 : 0);
}

void AWCDirector::StoryEvent(FName Id)
{
		AWCCharacter* P = Player();
	if (!P) return;
	if (HouseEvent(Id)) return;

	// ================================================================= act 1: arrival
	if (Is(Id, TEXT("trig:t_yard_edge")))
	{
		if (!Has(TEXT("dawn")) && Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 12.0; Feedback(TEXT("Not yet.")); }
		return;
	}
	// the tape on the shed bench: taking it is what brings the trash can over behind him, and what opens the house
	if (Is(Id, TEXT("take:tape1")) && !Has(TEXT("tape1_taken")))
	{
		Set(TEXT("tape1_taken"));
		Set(TEXT("shed_seen"));
		UE_LOG(LogWCStory, Display, TEXT("WCTAPE t=%.1f the shed tape is taken"), PlaySeconds);
		PlayScareLead(1.85f);
		After(1.85f, [this]()
		{
			ApplyWorldState();                                   // the bin is over now, everything in it across the yard
			// One hollow impact at the bin, followed by retreating footsteps on the yard gravel.
			const FVector Bin = Pos(TEXT("TrashPoint")) + FVector(0, 0, 24);
			PlayAt(TEXT("trash_crash"), Bin, 1.f, 1.f, 2400.f, true);
			if (AWCCharacter* Deputy = Player())
			{
				Deputy->SetFlashlight(true, false);
				FCollisionQueryParams Query(SCENE_QUERY_STAT(WCBinSight), false, Deputy);
				FHitResult Hit;
				bStepToShedDoor = GetWorld()->LineTraceSingleByChannel(Hit, Deputy->EyeLocation(), Bin, ECC_Visibility, Query) &&
				                   Hit.Distance + 115.f < FVector::Dist(Deputy->EyeLocation(), Bin);
				BinTurnStarted = Clock;
				BinViewStart = Deputy->GetControlRotation();
				BinStartPos = Deputy->GetActorLocation();
				BinTargetYaw = BinViewStart.Yaw;
			}
			if (AWCCharacter* Pl = Player()) Pl->AddShake(.48f);
			Tension = 1.f;
			// and whatever did it goes: heavy feet, fast, away along the back of the house and gone
			const FVector From = Pos(TEXT("TrashPoint")), To = Pos(TEXT("TrashRunTo"));
			if (!From.IsNearlyZero() && !To.IsNearlyZero())
			{
				const float Footfalls[] = {1.30f, 1.56f, 1.80f, 2.08f, 2.42f};
				for (int32 k = 0; k < UE_ARRAY_COUNT(Footfalls); ++k)
				{
					const FVector At = FMath::Lerp(From, To, k / 4.f) + FVector(0, 0, 10);
					After(Footfalls[k], [this, At, k]() { PlayAt(TEXT("step_gravel"), At, 1.f - .105f * k, .94f + .035f * k, 2400.f, true); });
				}
			}
			UE_LOG(LogWCStory, Display, TEXT("WCTRASH t=%.1f the bin goes over; something runs"), PlaySeconds);
			const float T = Say(TEXT("d_shedcall"), 2.9f);
			After(T + 1.2f, [this]() { OutsideProgress(); });

		});
		return;
	}
	if (Is(Id, TEXT("use:frame")))
	{
		if (!Has(TEXT("frame_seen")))
		{
			Set(TEXT("frame_seen"));
			Play2D(TEXT("pickup"), 0.5f, EWCSnd::SFX, 0.8f);
			Say(TEXT("d_photos"), 0.7f);
			ApplyWorldState();
		}
		return;
	}
	if (Is(Id, TEXT("trig:t_shed")) && !Has(TEXT("shed_seen")))
	{
		Set(TEXT("shed_seen"));
		OutsideProgress();
		return;
	}
	if (Is(Id, TEXT("locked:back")) && !Has(TEXT("inside")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Feedback(TEXT("Locked.")); }
		if (!Has(TEXT("back_tried")))
		{
			Set(TEXT("back_tried"));
			// the house is not empty: one slow board, somewhere inside, after he lets go of the handle
			After(2.6f, [this]() { PlayAt(TEXT("creak"), Pos(TEXT("FrontDoorPoint")) + FVector(1900, 0, 120), 0.8f, 0.8f, 2600.f); });
			OutsideProgress();
		}
		return;
	}
	if (Is(Id, TEXT("locked:front")) && !Has(TEXT("inside")) && !Has(TEXT("tape1_taken")))
	{
		// the first knock: nobody comes.  The one lit window goes dark.
		if (!Has(TEXT("knocked_first")))
		{
			Set(TEXT("knocked_first"));
			PlayAt(TEXT("knock"), Pos(TEXT("FrontDoorPoint")), 1.f);
			After(2.4f, [this]() { ShowTagged(TEXT("L_Welcome"), false); });
			float T = Say(TEXT("d_knock"), 0.9f);
			// nobody comes.  He tries the handle, says so, and says where he is going
			After(T + 1.6f, [this]() { PlayAt(TEXT("door_locked"), Pos(TEXT("FrontDoorPoint")), 0.9f); });
			T = Say(TEXT("d_side"), T + 2.4f);
			After(T + 0.6f, [this]() { OutsideProgress(); });
		}
		else if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; PlayAt(TEXT("knock"), Pos(TEXT("FrontDoorPoint")), 0.9f); Feedback(TEXT("No answer.")); }

		return;
	}
	if (Is(Id, TEXT("locked:front")))
	{
		if (!Has(TEXT("knocked")))
		{
			Set(TEXT("knocked"));
			PlayAt(TEXT("knock"), Pos(TEXT("FrontDoorPoint")), 1.f);
							After(2.4f, [this]() { ShowTagged(TEXT("L_Welcome"), false); });      // the one lit window goes dark
				// (Cheyenne: "when he says, can you please open up, the door will open")
				float T = Say(TEXT("d_openup"), 0.9f);
			After(T - 0.35f, [this]()
			{

				if (AWCDoor* D = Door(TEXT("front"))) { D->SetLocked(false); if (AWCCharacter* Pl = Player()) D->OpenAwayFrom(Pl->GetActorLocation(), 3.4f); D->SetAngle(D->OpenAngle * 0.32f, 3.4f); PlayAt(TEXT("door_creak_long"), D->GetActorLocation() + FVector(0, 0, 110), 1.f); }
				Say(TEXT("d_dooropen"), 3.2f);
				Set(TEXT("door_opened"));
			});
		}
					else if (Has(TEXT("locked_in")) && !Has(TEXT("door_stuck")))
			{
				// locked in, minutes after he walked through it
				Set(TEXT("door_stuck"));
				float T = Say(TEXT("d_doorstuck"));
				T = Say(TEXT("d_end1"), T + 1.0f);
				After(T, [this]() { Play2D(TEXT("radio_static"), 0.8f, EWCSnd::Voice); });
				After(T + 2.6f, [this]() { Think(TEXT("Nothing but static. It worked fine in the car.")); SetObjective(TEXT("Find Edith Harrow. Find another way out.")); Checkpoint(TEXT("locked_in")); });
			}
		else if (Clock > SpeechFreeAt)
		{
			SpeechFreeAt = Clock + 4.0;
			Feedback(TEXT("It will not open."));
		}
		return;
	}
	if (Is(Id, TEXT("trig:t_foyer")))
	{
		if (!Has(TEXT("inside")))
		{
			Set(TEXT("inside"));
			InsideAt = PlaySeconds;
			ApplyWorldState();
			Set(TEXT("smell_pending"));
			After(5.f, [this]() { SetObjective(TEXT("Search the house for Edith Harrow")); });
			Checkpoint(TEXT("inside"));
		}
					return;
	}
	if (Is(Id, TEXT("trig:t_dining")) && !Has(TEXT("seen_dining"))) { Set(TEXT("seen_dining")); Say(TEXT("d_table"), 1.5f); return; }
	if (Is(Id, TEXT("trig:t_living")) && !Has(TEXT("seen_living"))) { Set(TEXT("seen_living")); return; }       // (his line about the photographs is said over the fallen frame now)
	if (Is(Id, TEXT("use:phone")) && !Has(TEXT("phone_ringing")) && !Has(TEXT("phone_done")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 8.0; Say(TEXT("d_phonecord")); Set(TEXT("seen_phone")); }
		return;
	}
	if (Is(Id, TEXT("locked:cellar"))) { if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Feedback(TEXT("Padlocked.")); } return; }
	if (Is(Id, TEXT("locked:up_ell")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Feedback(TEXT("Locked.")); }
		return;
	}
	if (Is(Id, TEXT("locked:up_attic")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Feedback(TEXT("Locked.")); }
		return;
	}
	if (Is(Id, TEXT("locked:sitting")) || Is(Id, TEXT("locked:up_prayer")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Feedback(TEXT("Locked.")); }
		return;
	}
	if (Id.ToString().StartsWith(TEXT("locked:")) && !Is(Id, TEXT("locked:back")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 3.0; Feedback(TEXT("Locked.")); }
		return;
	}
	if (Id.ToString().StartsWith(TEXT("use:window")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Feedback(TEXT("Nailed shut.")); }
		return;
	}
	if (Is(Id, TEXT("trig:t_kitchen"))) Set(TEXT("seen_kitchen"));
		// the first scare is set off by the player: taking the small key is what brings the thump (no clock)
	if (Is(Id, TEXT("take:key_box"))) { UpstairsThump(); return; }
	// the kitchen wall vent: screwed shut until he brings the screwdriver down from her bedroom
	if (Is(Id, TEXT("use:vent")))
	{
		if (Has(TEXT("vent_open"))) return;
		if (!HasItem(TEXT("screwdriver")))
		{
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 3.0; Feedback(TEXT("Screwed shut. Something has been pushed in behind the slats.")); PlayAt(TEXT("door_locked"), P->GetActorLocation(), 0.4f, 1.7f, 600.f); }
			if (!Has(TEXT("vent_seen"))) { Set(TEXT("vent_seen")); if (!Has(TEXT("heard_upstairs"))) SetObjective(TEXT("Search the house. Something is behind the kitchen vent.")); }
			return;
		}
		AWCInteractable* Vent = Thing(TEXT("vent"));
		if (Vent)
		{
			UStaticMeshComponent* Driver = NewObject<UStaticMeshComponent>(Vent);
			Driver->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/WC/Props/SM_Item_Screwdriver.SM_Item_Screwdriver")));
			Driver->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			Driver->SetupAttachment(Vent->Mesh);
			Driver->RegisterComponent();
			VentTool = Driver;
			VentToolAt = Clock;
			TickVentTool();
		}
		Items.Remove(TEXT("screwdriver"));
		Set(TEXT("vent_seen"));
		Set(TEXT("vent_open"));
		UE_LOG(LogWCStory, Display, TEXT("WCVENT t=%.1f opened (%.0f s after coming in)"), PlaySeconds, PlaySeconds - InsideAt);
		for (int32 i = 0; i < 4; ++i) After(0.1f + i * 0.38f, [this, i]() { Play2D(TEXT("switch_click"), 0.45f, EWCSnd::SFX, 0.62f + 0.05f * i); });
		After(1.75f, [this]() { if (VentTool.IsValid()) { VentTool->DestroyComponent(); VentTool.Reset(); } Play2D(TEXT("door_unlock"), 0.5f, EWCSnd::SFX, 0.75f); ApplyWorldState(); });
		return;
	}
	// the doll from the vent: the small key is sewn inside her, and comes out in Inspect (WCGame.cpp, GWCHidden)
	if (Is(Id, TEXT("take:doll")))
	{
		Feedback(TEXT("Something hard is sewn inside her."));
		if (!Has(TEXT("heard_upstairs"))) SetObjective(TEXT("Look the doll over (Tab, Inspect)"));
		return;
	}
	if (Is(Id, TEXT("inspect:doll")))
	{
		if (!HasItem(TEXT("doll"))) return;
		Items.Remove(TEXT("doll"));
		Items.Add(TEXT("doll_empty"));
		Set(TEXT("doll_opened"));
		if (!HasItem(TEXT("key_box")) && !Has(TEXT("box_open"))) GiveItem(TEXT("key_box"), TEXT("Heart-shaped jewelry box key"));
		SetObjective(TEXT("Use the heart-shaped key on the upstairs jewelry box"));
		UE_LOG(LogWCStory, Display, TEXT("WCDOLL t=%.1f the small key comes out of the doll"), PlaySeconds);
		UpstairsThump();
		return;
	}
	if (Is(Id, TEXT("take:screwdriver")))
	{
		if (Has(TEXT("vent_seen")) && !Has(TEXT("vent_open")) && !Has(TEXT("heard_upstairs"))) SetObjective(TEXT("Search the house. The kitchen vent."));
		return;
	}
	if (Is(Id, TEXT("use:jewelbox")))
	{
		if (Has(TEXT("box_open"))) return;
		if (!HasItem(TEXT("key_box"))) { if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 3.0; Feedback(TEXT("Locked.")); PlayAt(TEXT("door_locked"), P->GetActorLocation(), 0.5f, 1.4f, 600.f); } return; }
		Items.Remove(TEXT("key_box"));
		Set(TEXT("box_open"));
		Play2D(TEXT("door_unlock"), 0.6f, EWCSnd::SFX, 1.3f);
		ApplyWorldState();
		return;
	}

	// ================================================================= act 2: the peek, the empty room, locked in
	if (Is(Id, TEXT("trig:t_up_landing")))
	{
		if (HasItem(TEXT("key_prayer")) && Has(TEXT("peek_done")) && !Has(TEXT("ceiling_started")) && !HasActiveEncounter()) ScareCeiling();
		return;
	}
	if (Is(Id, TEXT("trig:t_master")) && Has(TEXT("peek_done")) && !Has(TEXT("master_seen")) &&
		Clock >= SpeechFreeAt && Clock >= DialogueUntil)
	{
		Set(TEXT("master_seen"));
		float T = Say(TEXT("d_masterempty"), 1.2f);
		T = Say(TEXT("d_radio1"), T + 1.2f);
		T = Say(TEXT("r_trace"), T + 0.5f);
		T = Say(TEXT("d_trace"), T + 0.4f);
		After(T, [this]() { Play2D(TEXT("radio_static"), 0.8f, EWCSnd::Voice); });
		T = Say(TEXT("r_static"), T + 0.2f);
				T = Say(TEXT("d_radio2"), T + 0.9f);
		After(T, [this]() { SetObjective(TEXT("Get out. Try the back door.")); Set(TEXT("want_leave")); Checkpoint(TEXT("want_leave")); });
		return;
	}
		if (Is(Id, TEXT("shot_her"))) { ++ShotsAtHer; return; }
	if (Is(Id, TEXT("shot"))) { if (bLockInActive) ++LockInShots; return; }
	if (Is(Id, TEXT("trig:t_backhall")) && Has(TEXT("want_leave")) && !Has(TEXT("lockin_started")) && !bBusy && !bEventBusy && StalkState == 0) { ScareLockIn(); return; }
	if (Is(Id, TEXT("gotup")))
	{
		bBusy = false;
		if (Has(TEXT("lockin_started")) && !Has(TEXT("lockin_done")))
		{
			Set(TEXT("lockin_done"));
			Rest(200.f);
							float T = Say(TEXT("d_getup1"), 0.4f);
				if (ShotsAtHer > 0)
				{
					T = Say(TEXT("d_getup1b"), T + 0.3f);
					After(T + 0.6f, [this]() { Think(TEXT("But she flinched. Every shot, she flinched.")); });
					T += 3.f;
				}
				After(T + 0.8f, [this]() { if (!Has(TEXT("phone_done")) && !Has(TEXT("phone_ringing"))) SetObjective(TEXT("Check the back hall downstairs")); Checkpoint(TEXT("lockin_done")); });
			Tension = 0.45f;
		}
		else if (Has(TEXT("ceiling_started")) && !Has(TEXT("ceiling_done")))
		{
			Set(TEXT("ceiling_done"));
			Rest(120.f);
			float T = Say(TEXT("d_getup2"), 0.6f);
			After(T + 1.f, [this]() { Set(TEXT("kids_pending")); SetObjective(TEXT("Find what was theirs")); Checkpoint(TEXT("ceiling_done")); });
		}
		else if (Has(TEXT("sprint_started")) && !Has(TEXT("sprint_done")))
		{
			Set(TEXT("sprint_done"));
			ApplyWorldState();
			Say(TEXT("d_cellar"), 1.f);
			SetObjective(TEXT("Find her"));
			Checkpoint(TEXT("cellar"));
		}
		return;
	}
		if (Is(Id, TEXT("locked:back")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Feedback(TEXT("Nailed shut.")); }
		if (Has(TEXT("want_leave")) && !Has(TEXT("lockin_started")) && !bBusy && !bEventBusy && StalkState == 0) { After(1.5f, [this]() { ScareLockIn(); }); return; }
		if (Has(TEXT("lockin_done"))) Set(TEXT("backdoor_tried"));      // the phone rings later, when things have gone quiet (StoryTick)
		return;
	}
	if (Is(Id, TEXT("use:phone")) && Has(TEXT("phone_ringing")) && !Has(TEXT("phone_done"))) { ScarePhone(); return; }
	if (Is(Id, TEXT("take:key_sitting"))) { SetObjective(TEXT("Unlock the downstairs sitting room across the hall from the kitchen")); Checkpoint(TEXT("sitting_key")); return; }
	if (Is(Id, TEXT("take:keep_daniel"))) { AtticTagsTaken(); return; }
	if (Is(Id, TEXT("unlock:sitting"))) { Set(TEXT("sitting_open")); Say(TEXT("d_sitting"), 3.f); Checkpoint(TEXT("sitting")); return; }
		if (Is(Id, TEXT("take:key_prayer"))) { SetObjective(TEXT("Take the piano drawer's iron key to the upstairs prayer room")); Checkpoint(TEXT("prayer_key")); return; }
	if (Is(Id, TEXT("unlock:up_ell"))) { Checkpoint(TEXT("ell")); return; }
	if (Is(Id, TEXT("closed:note_prayer")) && !Has(TEXT("placed"))) { SetObjective(TEXT("Find what was theirs, and something to cut with")); return; }

	// ================================================================= act 3: upstairs again, the attic
	if (Is(Id, TEXT("trig:t_kids")) && Has(TEXT("ceiling_done")) && !Has(TEXT("seen_kids")))
	{
		Set(TEXT("seen_kids"));
		Say(TEXT("d_kidsdoor"), 0.8f);
		return;
	}
	if (Is(Id, TEXT("take:keep_ruth"))) { Think(TEXT("Ruth's. Her name is scratched in the bottom.")); Checkpoint(TEXT("underbed")); return; }
	
	if (Is(Id, TEXT("unlock:up_prayer"))) { Say(TEXT("d_prayer"), 3.f); Checkpoint(TEXT("prayer")); return; }
	if (Is(Id, TEXT("take:keep_walter")))
	{
				Think(TEXT("A wedding ring. W.H. to E.H., 1942."));
		After(1.5f, [this]() { if (AWCCharacter* Pl = Player()) Pl->FlickerLight(1.2f, 0.7f); });
		return;
	}
	
	if (Is(Id, TEXT("unlock:up_attic"))) { Checkpoint(TEXT("attic")); return; }
	if (Is(Id, TEXT("use:trunk")) && !Has(TEXT("attic_started"))) { ScareAttic(); return; }

	// ================================================================= act 4: the cellar
	if (Is(Id, TEXT("unlock:cellar")) && !Has(TEXT("sprint_started"))) { ScareCellarDoor(); return; }
	if (Is(Id, TEXT("use:shelf")) && !Has(TEXT("shelf_moved")))
	{
		Set(TEXT("shelf_moved"));
		AWCInteractable* Shelf = Thing(TEXT("shelf"));
		if (Shelf)
		{
			Shelf->bEnabled = false;
			PlayAt(TEXT("shelf_scrape"), Shelf->GetActorLocation(), 1.f);
			P->AddShake(0.2f);
			const FVector From = Shelf->GetActorLocation(), To = Pos(TEXT("ShelfOpen"));
			for (int32 i = 1; i <= 60; ++i)
			{
				After(i * 0.05f, [Shelf, From, To, i]() { if (IsValid(Shelf)) Shelf->SetActorLocation(FMath::Lerp(From, To, FMath::InterpEaseInOut(0.f, 1.f, i / 60.f, 2.f))); });
			}
		}
		return;
	}
	if (Is(Id, TEXT("trig:t_cellar_shelf")) && Has(TEXT("sprint_done")) && !Has(TEXT("seen_shelf"))) { Set(TEXT("seen_shelf")); Say(TEXT("d_shelf"), 0.5f); return; }
	if (Is(Id, TEXT("trig:t_root")) && Has(TEXT("shelf_moved")) && !Has(TEXT("seen_body")))
	{
		Set(TEXT("seen_body"));
		float T = Say(TEXT("d_body"), 1.2f);
		After(T, [this]() { SetObjective(TEXT("Lay their keepsakes at her feet")); });
		return;
	}
	// the last thing: her eye goes back, and that is what lets her go
	if (Is(Id, TEXT("use:place")) && Has(TEXT("eye_wanted")) && !Has(TEXT("eye_given")))
	{
		Set(TEXT("eye_given"));
		Items.Remove(TEXT("keep_eye"));
		bBusy = true;
		P->SetInputLocked(true);
		if (AWCInteractable* Pl = Thing(TEXT("place"))) Pl->bEnabled = false;
		Play2D(TEXT("pickup"), 0.5f, EWCSnd::SFX, 0.8f);
		ApplyWorldState();
		UE_LOG(LogWCStory, Display, TEXT("WCENDING t=%.1f her eye is given back"), PlaySeconds);
		After(2.0f, [this]() { FadeTo(1.f, 2.5f); });
		const float T2 = Say(TEXT("m_end"), 3.2f);
		After(T2 + 1.5f, [this]() { FinaleDawn(); });
		return;
	}
	if (Is(Id, TEXT("use:place")) && !Has(TEXT("placed")))
	{
		if (!(HasItem(TEXT("keep_ruth")) && HasItem(TEXT("keep_walter")) && HasItem(TEXT("keep_daniel")) && HasItem(TEXT("keep_eye"))))
		{
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Feedback(TEXT("Not yet.")); }
			// he has come down without everything: the door at the top of the stairs lets go, so he can fetch it
			if (AWCDoor* Cd = Door(TEXT("cellar"))) if (Cd->bLocked) { Cd->SetLocked(false); PlayAt(TEXT("door_unlock"), Cd->GetActorLocation() + FVector(0, 0, 100), 1.f, 0.8f, 3000.f); }
			return;
		}
		Set(TEXT("placed"));
		FinaleStart = Clock;
		ApplyWorldState();
		Play2D(TEXT("pickup"), 0.7f);
		if (AWCInteractable* Pl = Thing(TEXT("place"))) Pl->bEnabled = false;
		float T = Say(TEXT("d_place"), 0.5f);
		After(T, [this]() { SetObjective(TEXT("Cut the three knots")); FinaleStep(0); });
		return;
	}
	if (Has(TEXT("placed")) && !Has(TEXT("finale_done")))
	{
		for (int32 k = 1; k <= 3; ++k)
		{
			const FString Use = FString::Printf(TEXT("use:knot%d"), k);
			const FName Flag(*FString::Printf(TEXT("knot%d"), k));
						if (Id == FName(*Use) && !Has(Flag) && !bBusy)
			{
				if (!HasItem(TEXT("shears")))
				{
					if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Feedback(TEXT("Nothing to cut it with.")); }
					return;
				}
				// cutting takes a moment; she keeps coming
				bBusy = true;
				P->SetInputLocked(true);
				Play2D(TEXT("cut_rope"), 1.f);
				After(2.0f, [this, Flag]()
				{
					Set(Flag);
					ApplyWorldState();
					if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
					bBusy = false;
					FinaleStep(++KnotsCut);
				});
				return;
			}
		}
	}

	// ================================================================= ending
	if ((Is(Id, TEXT("use:cruiser")) || Is(Id, TEXT("trig:t_cruiser"))) && Has(TEXT("dawn")) && !Has(TEXT("ended")))
	{
		BeginEnding();
		return;
	}
}

// ---------------------------------------------------------------------------------------------- per-frame story logic
void AWCDirector::StoryTick(float Dt)
{
	AWCCharacter* P = Player();
	AWCEntity* H = Her();
	if (!P) return;

	const EListeningSpace Space = SpaceAt(P->GetActorLocation());
	const bool bIndoors = Space != EListeningSpace::Exterior;
	if (!bDriving && Space != ListeningSpace) RefreshRoomTone(Space);
	if (Has(TEXT("smell_pending")) && bIndoors && P->GetActorLocation().X >= 305.f && !bBusy)
	{
		Flags.Remove(TEXT("smell_pending"));
		Say(TEXT("d_foyer"));
	}
	// (the house's own noises are no longer on a timer: each is set off by something he does.  WCEvents.cpp, TickCues)
	// he calls out to her while he looks round, three times, before he has seen anything
	if (bIndoors && Has(TEXT("inside")) && !Has(TEXT("heard_upstairs")) && !bBusy && CallStep < 3 && Clock > SpeechFreeAt)
	{
		static const float CallAt[3] = { 100.f, 235.f, 380.f };
		static const TCHAR* CallId[3] = { TEXT("d_call1"), TEXT("d_call2"), TEXT("d_call3") };
		if (PlaySeconds - InsideAt > CallAt[CallStep] * TestPace) { Say(CallId[CallStep]); SpeechFreeAt = Clock + 8.0; ++CallStep; }
	}
	// a door that opens by itself: twice in the whole game at most, minutes apart, never over anything else
	if (Has(TEXT("peek_done")) && !Has(TEXT("dawn")) && !Has(TEXT("sprint_started")) && DoorEvents < 2 && !bBusy)
	{
		if (NextDoorAt < 0.0) NextDoorAt = Clock + 230.0 * TestPace;
		if (Clock >= NextDoorAt && Gate())
		{
			if (DoorOpensByItself()) { ++DoorEvents; NextDoorAt = Clock + 700.0 * TestPace; Rest(45.f); }
			else NextDoorAt = Clock + 6.0;
		}
	}
	if (FLoop* Drone = Loops.Find(TEXT("drone"))) Drone->Target = bIndoors && !Has(TEXT("dawn")) ? 0.53f + 0.13f * Tension : 0.f;
	// tension eases back toward a floor that rises as the night goes on
	{
		const float Floor = Has(TEXT("sprint_done")) ? 0.6f : (Has(TEXT("lockin_done")) ? 0.45f : (Has(TEXT("peek_done")) ? 0.3f : (Has(TEXT("heard_upstairs")) ? 0.2f : 0.08f)));
		Tension = FMath::FInterpConstantTo(Tension, Floor, Dt, 0.012f);
	}

	for (int32 i = Deferred.Num() - 1; i >= 0; --i)
	{
		if (Deferred[i].Valid && !Deferred[i].Valid()) { FDeferred D = Deferred[i]; Deferred.RemoveAt(i); if (D.Skip) D.Skip(); }
		else if (!bBusy && (Gate() || Clock >= Deferred[i].Deadline)) { FDeferred D = Deferred[i]; Deferred.RemoveAt(i); if (D.Go) D.Go(); }
	}
	if (Has(TEXT("kids_pending")) && !Has(TEXT("kids_open")) && !HasActiveEncounter())
	{
		// a quiet while after the hallway, a door that was locked creaks open and a music box starts
		Set(TEXT("kids_open"));
		if (AWCDoor* D = Door(TEXT("up_kids"))) { D->SetLocked(false); D->SetOpen(true, 4.5f, true); PlayAt(TEXT("door_creak_long"), D->GetActorLocation() + FVector(0, 0, 110), 1.f); }
		PlayAt(TEXT("musicbox"), Pos(TEXT("MusicBoxPoint")), 1.f);
	}
	if (Has(TEXT("kids_open")) && !Has(TEXT("underbed_done")) && !HasActiveEncounter())
	{
		// he has to be looking into the room, with the box in plain sight
		AWCCharacter* Pl = Player();
		AWCInteractable* Box = Thing(TEXT("pick_keep_ruth"));
		if (Pl && Box && !Pl->IsDown())
		{
			const FVector Eye = Pl->EyeLocation(), At = Box->GetActorLocation() + FVector(0, 0, 9);
			FHitResult Hit;
			FCollisionQueryParams Q(SCENE_QUERY_STAT(WCBoxSeen), false, Pl);
			Q.AddIgnoredActor(Box);
			if (FVector::Dist(Eye, At) < 420.f && FMath::Abs(Eye.Z - At.Z) < 220.f && !GetWorld()->LineTraceSingleByChannel(Hit, Eye, At, ECC_Visibility, Q)) ScareUnderBed();
		}
	}
	if (Has(TEXT("lockin_done")) && !Has(TEXT("phone_ringing")) && !Has(TEXT("phone_done")) && !bBusy && !bEventBusy && StalkState == 0 && !P->IsDown() && Clock > DialogueUntil + 0.5 && IsInsideHouse(P->GetActorLocation()) && P->GetActorLocation().Z < 200.f && P->GetActorLocation().Z > -50.f)
	{
		Set(TEXT("phone_ringing"));
		PhoneRingAgainAt = Clock;
		if (AWCInteractable* Ph = Thing(TEXT("phone"))) { Ph->Prompt = TEXT("Answer"); Ph->bEnabled = true; }
		After(3.f, [this]() { Think(TEXT("That phone has no line.")); });
		SetObjective(TEXT("Answer the phone in the kitchen"));
	}
	if (Has(TEXT("phone_ringing")) && !Has(TEXT("phone_done")) && Clock >= PhoneRingAgainAt)
	{
		PhoneRingAgainAt = Clock + 7.;
		if (UAudioComponent* A = PlayAt(TEXT("phone_ring"), Pos(TEXT("PhonePoint")), .87f))
		{
			A->ComponentTags.Add(TEXT("ring"));
			if (A->Sound && A->Sound->IsLooping()) PhoneRingAgainAt = TNumericLimits<double>::Max();
		}
	}
	if (!H) return;

	// Wait in darkness until the deputy rounds the corner with a real sightline.
	const FVector Doorway = Pos(TEXT("Her_Peek"));
	if (Has(TEXT("heard_upstairs")) && !Has(TEXT("peek_started")) && !bBusy &&
		P->GetActorLocation().Z >= Doorway.Z - 100.f && FVector::Dist2D(P->GetActorLocation(), Doorway) <= 730.f)
	{
		ScarePeek();
	}
	// ---- S1: the peek is watching you back
	if (Has(TEXT("peek_started")) && !Has(TEXT("peek_done")) && H->IsShown() && !Has(TEXT("peek_leaving")))
	{
		const bool bInView = PlayerSees(H->GetActorLocation()+FVector(0,0,145), .64f, 355.f);
		if (bInView && PeekLightAt < 0.)
		{
			PeekLightAt = Clock;
			P->SetFlashlight(false, false);
			P->SetLightScale(0.f);
			Play2D(TEXT("flashlight_click"), .5f);
		}
		if (PeekLightAt >= 0. && Clock - PeekLightAt >= .85 && !bPeekRelit)
		{
			P->SetLightScale(1.f);
			P->SetFlashlight(true, false);
			H->SetActorHiddenInGame(false);
			bPeekRelit = true;
		}
		if (bPeekRelit && PeekSeenAt < 0. && bInView && P->IsFlashlightOn()) PeekSeenAt = Clock;
		if (PeekSeenAt >= 0. && Clock - PeekSeenAt >= 1.0)
		{
			Set(TEXT("peek_leaving"));
			PlayAt(TEXT("step_wood"), H->GetActorLocation(), .50f, .9f);
			H->Slide(Pos(TEXT("Her_PeekBack")) - FVector(0,0,22), .36f, [this]()
			{
				if (AWCEntity* E = Her()) E->Vanish();
				SetReturnBlackout(false);
				if (AWCDoor* Front = Door(TEXT("front")))
				{
					if (!Front->bLocked) Front->Slam();
					Front->SetLocked(true);
					Set(TEXT("locked_in"));
				}
				Set(TEXT("peek_done"));
				Rest(150.f);
				const float Delay = FMath::Max(.65f, float(DialogueUntil - Clock + .1));
				const float T = Say(TEXT("d_getout"), Delay);
				SpeechFreeAt = FMath::Max(SpeechFreeAt, Clock + T + .3);
				After(T, [this]() { if (!Has(TEXT("box_open")) && !Has(TEXT("door_stuck"))) SetObjective(TEXT("Try the front door, or check the jewelry box")); });
				Tension = 0.4f;
			});
		}
	}

	// ---- S3: locked in. She walks straight at you.
	if (bLockInActive && H->IsShown())
	{
		if (Clock > HerNextStep)
		{
			HerNextStep = Clock + (bLockInRun ? 0.15 : 0.4);
			const double Elapsed = Clock - LockInStart;
			if (LockInDist0 <= 0.f) LockInDist0 = H->DistToPlayer();
						if (!bLockInRun && (LockInShots >= 3 || H->DistToPlayer() < LockInDist0 * 0.5f || Elapsed > 9.0 || H->DistToPlayer() < 600.f))
			{
				// halfway: she stops being slow
				bLockInRun = true;
				Play2D(TEXT("her_scream"), 1.f);
				Play2D(TEXT("sting_rise"), 0.9f, EWCSnd::Music);
				P->FlickerLight(1.2f, 0.85f);
				P->AddShake(0.5f);
			}
			TArray<FVector> Pts; Pts.Add(FVector(P->GetActorLocation().X, P->GetActorLocation().Y, H->GetActorLocation().Z));
			H->MoveAlong(Pts, bLockInRun ? 1500.f : 125.f, bLockInRun ? TEXT("Run") : TEXT("Walk"));
		}
		static int32 LastShots = 0;
		if (ShotsAtHer != LastShots)
		{
			LastShots = ShotsAtHer;
						// she flinches from every shot, and keeps coming
			if (!bLockInRun)
			{
				H->StopMoving();
				H->Play(TEXT("Idle"));
				HerNextStep = Clock + 0.45;
				PlayAt(TEXT("her_flinch"), H->HeadLocation(), 1.f, 1.f, 3500.f);
			}
			P->FlickerLight(0.3f, 0.9f);
			if (ShotsAtHer == 2) Say(TEXT("d_stop2"));
		}
		if (H->DistToPlayer() < 165.f)
		{
			bLockInActive = false;
			Grab(1.3f, [this]()
			{
				if (AWCCharacter* Pl = Player()) Pl->Knockdown(3.0f);
				FadeTo(1.f, 0.3f);
				After(0.7f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); });
				After(2.8f, [this]() { FadeTo(0.f, 1.6f); });
			});
		}
	}

	// ---- S4 / S6: sprint at the player.  She follows if you run; if she somehow cannot reach you, the scare still ends.
	if (bSprintActive && H->IsShown())
	{
		if (SprintStart < 0.0) SprintStart = Clock;
		if (Clock > SprintRetarget)
		{
			SprintRetarget = Clock + 0.25;
			TArray<FVector> Pts; Pts.Add(FVector(P->GetActorLocation().X, P->GetActorLocation().Y, P->GetActorLocation().Z - 88.f));
			H->MoveAlong(Pts, 1875.f, TEXT("Run"));
		}
	}
	if (bSprintActive && H->IsShown() && (H->DistToPlayer() < 175.f || Clock - SprintStart > 9.0))
	{
		SprintStart = -1.0;
		bSprintActive = false;
		const bool bCellar = Has(TEXT("sprint_started")) && !Has(TEXT("sprint_done"));
		Grab(1.25f, [this, bCellar]()
		{
			if (AWCCharacter* Pl = Player()) Pl->Knockdown(bCellar ? 3.6f : 3.0f);
			FadeTo(1.f, 0.3f);
			After(0.7f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); if (AWCCharacter* Pl = Player()) Pl->SetLightScale(1.f); });
			if (bCellar)
			{
				After(1.2f, [this]()
				{
					if (AWCCharacter* Pl = Player()) Pl->Relocate(Pos(TEXT("P_CellarBottom")), YawOf(TEXT("P_CellarBottom")));
					Play2D(TEXT("body_fall"), 1.f);
					if (AWCDoor* D = Door(TEXT("cellar"))) { D->Slam(); D->SetLocked(true); D->KeyId = NAME_None; }
				});
			}
			After(3.2f, [this]() { FadeTo(0.f, 1.8f); });
		});
	}

	// ---- finale clock: take too long and she keeps you
	if (FinaleStart > 0.0 && Has(TEXT("placed")) && !Has(TEXT("finale_done")) && !Has(TEXT("caught")))
	{
		const double Elapsed = Clock - FinaleStart;
		Tension = FMath::Clamp(0.6f + (float)Elapsed / 150.f, 0.f, 1.f);
		if (Elapsed > 95.0) FinaleCaught();
	}
}

// ---------------------------------------------------------------------------------------------- S1 corner peek
void AWCDirector::ScarePeek()
{
	Set(TEXT("peek_started"));
	UpstairsAt = Clock;
	PeekLightAt = PeekSeenAt = -1.;
	bPeekRelit = false;
	AWCEntity* H = Her();
	if (!H) { Set(TEXT("peek_done")); SetReturnBlackout(false); return; }
	if (AWCDoor* D = Door(TEXT("up_master"))) D->SetOpen(true, 0.01f, true);
	H->Appear(Pos(TEXT("Her_Peek")), YawOf(TEXT("Her_Peek")), TEXT("Peek"));
	H->SetGlow(0.f);
	H->SetFarGlow(0.f);
	H->SetActorHiddenInGame(true); // Already posed in the doorway; let the returning beam reveal her.
	if (AWCCharacter* Deputy = Player()) Deputy->FlickerLight(.36f,.85f);
	SetReturnBlackout(true);
	PlayAt(TEXT("creak"), H->GetActorLocation(), .50f, .8f);
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S1_peek"), PlaySeconds);
}

// ---------------------------------------------------------------------------------------------- S3 locked in
void AWCDirector::ScareLockIn()
{
	if (Has(TEXT("lockin_started"))) return;
		Set(TEXT("lockin_started"));
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S3_lockin"), PlaySeconds);
	ShotsAtHer = 0;
	LockInShots = 0;
	Set(TEXT("power_out"));
	bPowerOut = true;
	KillLights(0.f, true);
	if (AWCCharacter* Pl = Player()) Pl->FlickerLight(0.8f, 0.8f);
	After(1.0f, [this]()
	{
		AWCEntity* H = Her();
		if (!H) return;
		SetLoop(TEXT("amb"), TEXT("amb_house"), 0.15f, 1.5f);
		H->Appear(Pos(TEXT("Her_Hall0")), YawOf(TEXT("Her_Hall0")), TEXT("Idle"));
		H->SetStutter(11.f);
		PlayAt(TEXT("creak"), H->GetActorLocation(), 1.f, 0.7f);
		Play2D(TEXT("sting_low"), 0.9f, EWCSnd::Music);
		Tension = 0.8f;
		After(2.6f, [this]()
		{
			Say(TEXT("d_stop"));
			ShowHint(TEXT("Hold Right Mouse to raise your pistol    Left Mouse to fire    R reload"), 7.f);
			bLockInActive = true;
			bLockInRun = false;
			LockInDist0 = 0.f;
			LockInStart = Clock;
			HerNextStep = 0.0;
		});
	});
}

// ---------------------------------------------------------------------------------------------- S2 the phone
void AWCDirector::ScarePhone()
{
	Set(TEXT("phone_done"));
	Flags.Remove(TEXT("phone_ringing"));
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S2_phone"), PlaySeconds);
	// stop the ring
	TArray<UAudioComponent*> All;
	for (TObjectIterator<UAudioComponent> It; It; ++It) if (It->GetWorld() == GetWorld() && It->ComponentHasTag(TEXT("ring"))) It->Stop();
	if (AWCInteractable* Ph = Thing(TEXT("phone"))) Ph->bEnabled = false;
	Play2D(TEXT("phone_pickup"), 0.9f);
	AWCCharacter* P = Player();
	bBusy = true;
	float T = Say(TEXT("m_phone1"), 1.4f);
	T = Say(TEXT("m_phone2"), T + 0.8f);
	After(T, [this]() { if (AWCCharacter* Pl = Player()) Pl->FlickerLight(2.5f, 0.9f); });
	T = Say(TEXT("m_phone3"), T + 0.7f);
	After(T - 0.4f, [this]()
	{
		if (AWCCharacter* Pl = Player()) { Pl->SetLightScale(0.f); }
		Play2D(TEXT("bulb_die"), 0.9f);
		SetLoop(TEXT("amb"), TEXT("amb_house"), 0.05f, 0.5f);
		Play2D(TEXT("her_breath"), 0.9f);
	});
	T = Say(TEXT("d_light_dead"), T + 1.6f);
	After(T + 1.2f, [this]()
	{
		AWCEntity* H = Her();
		AWCCharacter* Pl = Player();
		if (!H || !Pl) return;
		H->Appear(Pos(TEXT("Her_KitchenSeat")), YawOf(TEXT("Her_KitchenSeat")), TEXT("Sit"));
		Pl->SetLightScale(1.f);
		Pl->FlickerLight(0.5f, 0.8f);
		PlayAt(TEXT("chair_scrape"), H->GetActorLocation(), 1.f);
		Set(TEXT("phone_seat"));
		// she waits to be seen, but not for long
		for (int32 i = 1; i <= 50; ++i)
		{
			After(i * 0.1f, [this, i]()
			{
				AWCEntity* E = Her();
				AWCCharacter* Q = Player();
				if (!E || !Q || !Has(TEXT("phone_seat"))) return;
				const bool bSeen = PlayerSees(E->HeadLocation(), 0.82f, 1400.f);
				if ((bSeen && i > 9) || i == 50)
				{
					Flags.Remove(TEXT("phone_seat"));
					After(bSeen ? 0.9f : 0.0f, [this]()
					{
						AWCEntity* E2 = Her();
						AWCCharacter* Q2 = Player();
						if (!E2 || !Q2) return;
						Play2D(TEXT("her_scream"), 1.f);
						Play2D(TEXT("sting_hit"), 1.f, EWCSnd::Music);
						E2->SetStutter(14.f);
						TArray<FVector> Pts; Pts.Add(FVector(Q2->GetActorLocation().X, Q2->GetActorLocation().Y, E2->GetActorLocation().Z));
						E2->MoveAlong(Pts, 1950.f, TEXT("Run"), [this]()
						{
							Grab(1.3f, [this]()
							{
							if (AWCCharacter* Q3 = Player()) { Q3->AddShake(1.f); Q3->SetLightScale(0.f); }
							if (AWCEntity* E3 = Her()) E3->Vanish();
							After(0.9f, [this]()
							{
								if (AWCCharacter* Q4 = Player()) { Q4->SetLightScale(1.f); Q4->FlickerLight(0.8f, 0.8f); }
								ApplyWorldState();
								bBusy = false;
								Rest(170.f);
								float T2 = Say(TEXT("d_after_kitchen"), 0.3f);
								T2 = Say(TEXT("d_drawer"), T2 + 2.2f);
								After(T2, [this]()
								{
									// somewhere above him a drawer is pulled open (its key is no longer in the kitchen)
									PlayAt(TEXT("drag_floor"), Pos(TEXT("DrawerPoint")), 1.f, 1.5f, 4500.f);
									SetObjective(TEXT("Search the open dresser drawer in the front upstairs bathroom"));
									Checkpoint(TEXT("phone_done"));
								});
								Tension = 0.55f;
							});
							});
						});
					});
				}
			});
		}
	});
}

// ---------------------------------------------------------------------------------------------- S4 the head by the ceiling
void AWCDirector::ScareCeiling()
{
	Set(TEXT("ceiling_started"));
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S4_ceiling"), PlaySeconds);
	AWCEntity* H = Her();
	AWCCharacter* P = Player();
	if (!H || !P) { Set(TEXT("ceiling_done")); return; }
	H->Appear(Pos(TEXT("Her_UpFar")), YawOf(TEXT("Her_UpFar")), TEXT("Tall"));
	H->SetGlow(1.6f);
	P->SetLightScale(0.3f);
	P->FlickerLight(1.2f, 0.6f);
	Play2D(TEXT("bulb_die"), 0.5f);
	PlayScareLead(8.f);
	SetLoop(TEXT("amb"), TEXT("amb_house"), 0.1f, 1.f);
	Tension = 0.9f;
	Say(TEXT("d_ceiling"), 2.4f);
	After(4.6f, [this]()
	{
		// she draws back into the dark and the light goes
		if (AWCEntity* E = Her()) E->Slide(Pos(TEXT("Her_UpBack")), 1.6f);
		After(1.2f, [this]() { if (AWCCharacter* Pl = Player()) Pl->SetLightScale(0.f); });
		After(3.4f, [this]()
		{
			AWCEntity* E = Her();
			AWCCharacter* Pl = Player();
			if (!E || !Pl) return;
			Play2D(TEXT("her_scream"), 1.f);
			Pl->AddShake(.72f);
			E->SetStutter(0.f);
			TArray<FVector> Pts; Pts.Add(FVector(Pl->GetActorLocation().X, Pl->GetActorLocation().Y, E->GetActorLocation().Z));
			E->MoveAlong(Pts, 1875.f, TEXT("Run"));
			Pl->SetLightScale(0.55f);
			Pl->FlickerLight(2.f, 0.95f);
			SprintStart = -1.0;
			bSprintActive = true;
		});
	});
}

// ---------------------------------------------------------------------------------------------- S7 the hand under the bed
// Ruth's music box. The shot owns its view independently of the deputy's stance.
void AWCDirector::ScareUnderBed()
{
	if (BedCamera.IsValid() || Has(TEXT("underbed_done")) || HasItem(TEXT("keep_ruth"))) return;
	AWCCharacter* P = Player();
	APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
	AWCInteractable* Box = Thing(TEXT("pick_keep_ruth"));
	USkeletalMesh* Mesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/WC/Her/SK_BedArm.SK_BedArm"));
	if (!P || !PC || !Box || !Mesh) return;

	BedBoxStart = Box->GetActorLocation();
	const FVector View = BedBoxStart + FVector(-123, 54, 150);
	const FVector Aim = BedBoxStart + FVector(0,-53,13);
	ACameraActor* Camera = GetWorld()->SpawnActor<ACameraActor>(View, (Aim-View).Rotation());
	if (!Camera) return;
	BedCamera = Camera;
	Camera->GetCameraComponent()->SetFieldOfView(59.f);
	Camera->GetCameraComponent()->bConstrainAspectRatio = false;

	USkeletalMeshComponent* Arm = NewObject<USkeletalMeshComponent>(Camera);
	Arm->SetupAttachment(Camera->GetRootComponent());
	Arm->SetAbsolute(true,true,true);
	Arm->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Arm->SetSkeletalMeshAsset(Mesh);
	Arm->SetMaterial(0, LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Her/MI_HerDead.MI_HerDead")));
	Arm->SetLightingChannels(true, true, true);
	Arm->SetVisibility(false);
	Arm->RegisterComponent();
	BedArm = Arm;
	const FBox Bounds = Box->Mesh->Bounds.GetBox();
	BedWristAtBox = FVector(Bounds.GetCenter().X, Bounds.GetCenter().Y - 36.f, Bounds.Max.Z + 3.f);

	// A practical beam follows this fixed camera, including when the player
	// entered looking away or with the flashlight held below the mattress.
	USpotLightComponent* Beam = NewObject<USpotLightComponent>(Camera);
	Beam->SetupAttachment(Camera->GetRootComponent());
	Beam->SetRelativeLocation(FVector(3,-12,-9));
	Beam->SetIntensityUnits(ELightUnits::Lumens);
	Beam->SetIntensity(500.f);
	Beam->SetLightingChannels(true,true,false);
	Beam->SetInnerConeAngle(24.f);
	Beam->SetOuterConeAngle(42.f);
	Beam->SetLightColor(FLinearColor(1.f,.91f,.78f));
	Beam->SetAttenuationRadius(560.f);
	Beam->RegisterComponent();
	// Rake a little reflected light across the knuckles. Only the arm receives it.
	UPointLightComponent* Bounce = NewObject<UPointLightComponent>(Camera);
	Bounce->SetupAttachment(Camera->GetRootComponent());
	Bounce->SetAbsolute(true,false,false);
	Bounce->SetWorldLocation(BedBoxStart + FVector(-45,-28,52));
	Bounce->SetLightingChannels(false,false,true);
	Bounce->SetIntensityUnits(ELightUnits::Lumens);
	Bounce->SetIntensity(235.f);
	Bounce->SetLightColor(FLinearColor(.81f,.86f,.92f));
	Bounce->SetAttenuationRadius(220.f);
	Bounce->SetSourceRadius(13.f);
	Bounce->SetCastShadows(false);
	Bounce->RegisterComponent();

	if (AWCEntity* E = Her()) E->Vanish();
	for (TObjectIterator<UAudioComponent> It; It; ++It)
		if (It->GetWorld() == GetWorld() && It->Sound && It->Sound->GetName().Contains(TEXT("musicbox")))
			It->FadeOut(2.5f, 0.f);
	bBusy = true;
	BedElapsed = 0.f;
	Box->bEnabled = false;
	P->SetInputLocked(true);
	P->GetCharacterMovement()->StopMovementImmediately();
	P->ConsumeMovementInputVector();
	PC->SetViewTargetWithBlend(Camera,.25f,VTBlend_EaseInOut,2.f,true);
	Tension = .8f;
	SetLoop(TEXT("amb"), TEXT("amb_house"), .1f, 1.5f);
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S7_hand stance=%s view=%s box=%s lid=%.1f"), PlaySeconds,
		P->bIsCrouched ? TEXT("crouched") : TEXT("standing"), *View.ToCompactString(), *BedBoxStart.ToCompactString(), Bounds.Max.Z);
}

void AWCDirector::TickUnderBed(float Dt)
{
	ACameraActor* Camera = BedCamera.Get();
	AWCInteractable* Box = Thing(TEXT("pick_keep_ruth"));
	USkeletalMeshComponent* Arm = BedArm.Get();
	AWCCharacter* P = Player();
	if (!Camera || !Arm || !Box || !P) return;
	const float Previous = BedElapsed;
	BedElapsed += Dt;
	const float T = BedElapsed;
	const float Reach = FMath::SmoothStep(1.75f, 4.6f, T);
	const float Grip = FMath::SmoothStep(4.6f, 5.15f, T);
	const float Pull = FMath::SmoothStep(5.45f, 7.85f, T);
	const float Withdraw = FMath::SmoothStep(7.95f, 8.7f, T);
	const FVector Under = Pos(TEXT("Her_Under"));
	const FVector HideAt(Under.X, Under.Y - 15.f, BedBoxStart.Z);
	const FVector Drag = (HideAt - BedBoxStart) * Pull;
	Arm->SetWorldLocation(BedWristAtBox + FVector(0,-165.f*(1.f-Reach)-78.f*Withdraw, 2.f*FMath::Sin(PI*Reach)-1.5f*Grip) + Drag);
	const float Searching = FMath::Sin(Reach * PI);
	Arm->SetWorldRotation(FRotator(1.5f*Searching, 90.f - 4.f*Searching, 4.f*Searching));
	Arm->SetMorphTarget(TEXT("Grip"), Grip*(1.f-Withdraw));
	Arm->SetVisibility(T >= 1.75f && T < 8.7f);
	Box->SetActorLocation(BedBoxStart + Drag);
	if (Previous < 1.75f && T >= 1.75f)
	{
		PlayAt(TEXT("scratch_wall"), Under, .8f, .7f, 1500.f);
		Play2D(TEXT("sting_low"), .6f, EWCSnd::Music);
	}
	if (Previous < 5.45f && T >= 5.45f)
	{
		PlayAt(TEXT("pickup"), BedBoxStart, .9f, .7f, 1200.f);
		PlayAt(TEXT("drag_floor"), BedBoxStart, .5f, 1.3f, 1200.f);
	}
	if (T < 9.1f) return;

	if (APlayerController* PC = UGameplayStatics::GetPlayerController(this,0))
	{
		PC->SetControlRotation((HideAt - P->EyeLocation()).Rotation());
		PC->SetViewTargetWithBlend(P,.3f,VTBlend_EaseInOut,2.f,true);
	}
	BedCamera.Reset();
	BedArm.Reset();
	Camera->SetLifeSpan(.35f);
	Set(TEXT("underbed_done"));
	P->SetInputLocked(false);
	bBusy = false;
	Rest(140.f);
	ApplyWorldState();
	Think(TEXT("...It took it. It's under the bed."));
	ShowHint(TEXT("C: crouch"), 6.f);
	Checkpoint(TEXT("hand"));
}


// ---------------------------------------------------------------------------------------------- S5 the attic
void AWCDirector::ScareAttic()
{
	Set(TEXT("attic_started"));
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S5_attic"), PlaySeconds);
	if (AWCInteractable* Trunk = Thing(TEXT("trunk"))) Trunk->bEnabled = false;
	Play2D(TEXT("trunk_open"), 0.9f);
	// the tags and the padlock key are lying on it now, for him to take; taking the tags is what she cannot bear
	After(0.5f, [this]() { ApplyWorldState(); });
}

void AWCDirector::AtticTagsTaken()
{
	if (Has(TEXT("attic_tags"))) return;
	Set(TEXT("attic_tags"));
	After(1.4f, [this]()
	{
		const float AtticZ = Pos(TEXT("Her_AtticFar")).Z;
		WhenQuiet([this]() { AtticCrawl(); },
			[this, AtticZ]() { AWCCharacter* Pl = Player(); return Pl && Pl->GetActorLocation().Z > AtticZ - 40.f; },
			[this]() { Set(TEXT("attic_done")); Rest(60.f); SetObjective(TEXT("Unlock the cellar")); Checkpoint(TEXT("attic_done")); }, 50.f);
	});
}

void AWCDirector::AtticCrawl()
{
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S5_crawl"), PlaySeconds);
	{
		AWCEntity* H = Her();
		AWCCharacter* P = Player();
		if (!H || !P) { Set(TEXT("attic_done"));
						Rest(120.f); return; }
		PlayAt(TEXT("thump_heavy"), Pos(TEXT("Her_AtticFar")), 1.f);
		After(1.6f, [this]()
		{
			AWCEntity* E = Her();
			AWCCharacter* Pl = Player();
			if (!E || !Pl) return;
			E->Appear(Pos(TEXT("Her_AtticFar")), YawOf(TEXT("Her_AtticFar")), TEXT("Crawl"));
			E->SetStutter(15.f);
			Play2D(TEXT("crawl_knocks"), 1.f);
			Play2D(TEXT("sting_rise"), 0.9f, EWCSnd::Music);
			Tension = 1.f;
			TArray<FVector> Pts;
			const FVector Dir = (Pl->GetActorLocation() - E->GetActorLocation()).GetSafeNormal2D();
			Pts.Add(FVector(Pl->GetActorLocation().X, Pl->GetActorLocation().Y, E->GetActorLocation().Z) - Dir * 150.f);
			E->MoveAlong(Pts, 1250.f, TEXT("Crawl"), [this]()
			{
				AWCEntity* E2 = Her();
				AWCCharacter* Q = Player();
				if (!E2 || !Q) return;
				E2->SetStutter(0.f);
				E2->FacePlayer(true);
				E2->Play(TEXT("Rise"), false, 3.2f);
				Play2D(TEXT("her_scream"), 1.f);
				Play2D(TEXT("sting_hit"), 1.f, EWCSnd::Music);
				Q->AddShake(1.f);
				Q->FlickerLight(1.0f, 0.95f);
				After(1.0f, [this]()
				{
					if (AWCCharacter* Q2 = Player()) Q2->SetLightScale(0.f);
					After(1.3f, [this]()
					{
						if (AWCEntity* E3 = Her()) E3->Vanish();
						if (AWCCharacter* Q3 = Player()) { Q3->SetLightScale(1.f); Q3->FlickerLight(0.6f, 0.8f); }
						Set(TEXT("attic_done"));
						float T2 = Say(TEXT("d_after_attic"), 1.6f);
						After(T2, [this]() { SetObjective(TEXT("Unlock the cellar")); Checkpoint(TEXT("attic_done")); });
						Tension = 0.6f;
					});
				});
			});
		});
	}
}

// ---------------------------------------------------------------------------------------------- S6 the sprint down the hall
void AWCDirector::ScareCellarDoor()
{
	Set(TEXT("sprint_started"));
	float T = Say(TEXT("d_cellar_open"), 0.6f);
	After(T + 0.5f, [this]()
	{
		// she comes when it has been quiet for a while; if he is already at the bottom by then, the door just shuts on him
		WhenQuiet([this]() { CellarSprint(); },
			[this]() { AWCCharacter* Pl = Player(); return Pl && Pl->GetActorLocation().Z > -230.f; },
			[this]() { CellarQuiet(); }, 150.f);
	});
}

void AWCDirector::CellarQuiet()
{
	if (Has(TEXT("sprint_done"))) return;
	UE_LOG(LogWCStory, Display, TEXT("WCEVENT t=%.1f cellar door shuts behind him (no rush)"), PlaySeconds);
	if (AWCDoor* D = Door(TEXT("cellar")))
	{
		D->Slam(); D->SetLocked(true); D->KeyId = NAME_None;
		PlayAt(TEXT("door_slam"), D->GetActorLocation() + FVector(0, 0, 110), 1.f, 0.9f, 3000.f);
	}
	if (AWCCharacter* Pl = Player()) { Pl->FlickerLight(1.4f, 0.8f); Pl->AddShake(0.4f); }
	Tension = 0.8f;
	Set(TEXT("sprint_done"));
	ApplyWorldState();
	After(1.6f, [this]() { Think(TEXT("The door. She shut it.")); });
	Say(TEXT("d_cellar"), 4.f);
	SetObjective(TEXT("Find her"));
	Checkpoint(TEXT("cellar"));
}

void AWCDirector::CellarSprint()
{
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S6_sprint"), PlaySeconds);
	{
		AWCEntity* H = Her();
		AWCCharacter* P = Player();
		if (!H || !P) { Set(TEXT("sprint_done")); return; }
		H->Appear(Pos(TEXT("Her_SprintStart")), YawOf(TEXT("Her_SprintStart")), TEXT("Run"));
		Play2D(TEXT("her_scream"), 1.f);
		Play2D(TEXT("sting_rise"), 1.f, EWCSnd::Music);
		TArray<FVector> Pts; Pts.Add(FVector(P->GetActorLocation().X, P->GetActorLocation().Y, H->GetActorLocation().Z));
		H->MoveAlong(Pts, 1800.f, TEXT("Run"));
		P->FlickerLight(1.6f, 0.8f);
		SprintStart = -1.0;
		bSprintActive = true;
		Tension = 1.f;
	}
}

void AWCDirector::WhenQuiet(TFunction<void()> Go, TFunction<bool()> Valid, TFunction<void()> Skip, float MaxWait)
{
	if (Gate() && !bBusy) { Go(); return; }
	FDeferred D;
	D.Go = MoveTemp(Go); D.Valid = MoveTemp(Valid); D.Skip = MoveTemp(Skip);
	D.Deadline = Clock + MaxWait * FMath::Max(TestPace, 0.15f);
	Deferred.Add(MoveTemp(D));
}

// ---------------------------------------------------------------------------------------------- S8 finale
void AWCDirector::FinaleStep(int32 Knot)
{
	AWCEntity* H = Her();
	AWCCharacter* P = Player();
	if (!H || !P) return;
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S8_finale step %d"), PlaySeconds, Knot);
	if (Knot == 0)
	{
		FinaleStart = Clock;
		KnotsCut = 0;
		SetLoop(TEXT("music"), TEXT("music_finale"), 0.7f, 6.f, EWCSnd::Music);
		After(2.5f, [this]()
		{
			if (AWCEntity* E = Her()) { E->Appear(Pos(TEXT("Her_Fin0")), YawOf(TEXT("Her_Fin0")), TEXT("Idle")); E->SetStutter(10.f); E->FacePlayer(true); }
			Say(TEXT("m_fin1"), 0.6f);
			if (AWCCharacter* Pl = Player()) Pl->FlickerLight(1.2f, 0.7f);
		});
	}
	else if (Knot == 1)
	{
		Say(TEXT("d_knot1"));
		TArray<FVector> Pts; Pts.Add(Pos(TEXT("Her_Fin1")));
		H->MoveAlong(Pts, 95.f, TEXT("Walk"));
		Say(TEXT("m_fin2"), 1.2f);
		P->FlickerLight(1.5f, 0.8f);
	}
	else if (Knot == 2)
	{
		Say(TEXT("d_knot2"));
		TArray<FVector> Pts; Pts.Add(Pos(TEXT("Her_Fin2")));
		H->SetStutter(14.f);
		H->MoveAlong(Pts, 1140.f, TEXT("Run"), [this]()
		{
			if (AWCEntity* E = Her()) { E->SetStutter(0.f); E->Play(TEXT("Rise"), false, 1.f); E->FacePlayer(true); }
		});
		Play2D(TEXT("her_scream_short"), 0.9f);
		Say(TEXT("m_fin3"), 1.4f);
		P->SetLightScale(0.3f);
		P->FlickerLight(30.f, 0.6f);
		P->AddShake(0.5f);
	}
	else
	{
		Set(TEXT("finale_done"));
		bBusy = true;
		P->SetInputLocked(true);
		float T = Say(TEXT("d_knot3"));
		After(T - 0.3f, [this]()
		{
			AWCEntity* E = Her();
			AWCCharacter* Pl = Player();
			if (!E || !Pl) return;
			const FVector Fwd = FRotator(0.f, Pl->GetControlRotation().Yaw, 0.f).Vector();
			E->Appear(Pl->GetActorLocation() - FVector(0, 0, 88) + Fwd * 115.f, (-Fwd).Rotation().Yaw, TEXT("Tall"));
			E->SetScream(1.f);                      // "STAY!": the whole of her mouth, down and wide
			Pl->SetLightScale(1.f);

			Pl->FlickerLight(1.5f, 0.6f);
			Play2D(TEXT("her_scream"), 1.f);
			Play2D(TEXT("VO/m_fin4"), 1.f, EWCSnd::Voice);
			Play2D(TEXT("sting_hit"), 1.f, EWCSnd::Music);
			Pl->AddShake(1.f);
			SetLoop(TEXT("music"), TEXT(""), 0.f, 0.4f, EWCSnd::Music);
			After(1.25f, [this]()
			{
				FadeTo(1.f, 0.08f);
				if (AWCEntity* E2 = Her()) E2->Vanish();
				SetLoop(TEXT("amb"), TEXT(""), 0.f, 0.3f);
				SetLoop(TEXT("drone"), TEXT(""), 0.f, 0.3f, EWCSnd::Music);
				Tension = 0.f;
				// she is still here.  The dark lifts on the root cellar, quiet, and there is one thing left to do.
				After(3.5f, [this]()
				{
					FadeTo(0.f, 3.f);
					bBusy = false;
					if (AWCCharacter* Q = Player()) { Q->SetInputLocked(false); Q->SetLightScale(1.f); }
					Set(TEXT("eye_wanted"));
					if (AWCInteractable* Pl = Thing(TEXT("place"))) { Pl->Prompt = TEXT("Put her eye back"); Pl->bEnabled = true; }
					SetObjective(TEXT("Give her back her eye"));
					Checkpoint(TEXT("eye"));
				});
			});
		});
	}
}

/** Morning: the doors are open and the house is only a house. */
void AWCDirector::FinaleDawn()
{
	{
		{
			{
				{
					Set(TEXT("dawn"));
					if (AWCDoor* C = Door(TEXT("cellar"))) { C->SetLocked(false); C->SetOpen(true, 0.01f, true); C->Snap(); }
					if (AWCDoor* F = Door(TEXT("front"))) { F->SetLocked(false); F->SetOpen(true, 0.01f, true); F->Snap(); }
					ApplyWorldState();
					if (AWCCharacter* Q = Player()) { Q->SetInputLocked(false); Q->SetLightScale(1.f); }
					bBusy = false;
					FadeTo(0.f, 5.f);
					SetLoop(TEXT("music"), TEXT("music_dawn"), 0.6f, 6.f, EWCSnd::Music);
					Say(TEXT("d_dawn"), 6.f);
					After(8.f, [this]() { SetObjective(TEXT("Go back to the cruiser")); Checkpoint(TEXT("dawn")); });
				}
			}
		}
	}
}

void AWCDirector::FinaleCaught()
{
	Set(TEXT("caught"));
	UE_LOG(LogWCStory, Display, TEXT("WCFAIL t=%.1f caught in the finale"), PlaySeconds);
	AWCEntity* H = Her();
	AWCCharacter* P = Player();
	if (!H || !P) return;
	bBusy = true;
	P->SetInputLocked(true);
	Play2D(TEXT("her_scream"), 1.f);
	TArray<FVector> Pts; Pts.Add(FVector(P->GetActorLocation().X, P->GetActorLocation().Y, H->GetActorLocation().Z));
	if (!H->IsShown()) H->Appear(Pos(TEXT("Her_Fin1")), YawOf(TEXT("Her_Fin1")), TEXT("Run"));
	H->MoveAlong(Pts, 1650.f, TEXT("Run"), [this]()
	{
		if (AWCCharacter* Pl = Player()) { Pl->AddShake(1.f); Pl->Knockdown(8.f); }
		FadeTo(1.f, 0.3f);
		BigText = TEXT("You stayed.");
		BigSub = TEXT("");
		After(1.2f, [this]() { BigTarget = 1.f; });
		After(5.5f, [this]() { RestartFromCheckpoint(); });
	});
}

// ---------------------------------------------------------------------------------------------- ending
void AWCDirector::BeginEnding()
{
	Set(TEXT("ended"));
	UE_LOG(LogWCStory, Display, TEXT("WCENDING t=%.1f reached the ending"), PlaySeconds);
	if (AWCCharacter* P = Player()) P->SetInputLocked(true);
	Objective.Reset();
	float T = Say(TEXT("d_end1"), 0.8f);
	T = Say(TEXT("r_end1"), T + 0.4f);
	T = Say(TEXT("d_end2"), T + 0.6f);
	T = Say(TEXT("r_end2"), T + 0.5f);
	After(T + 0.4f, [this]() { PlayAt(TEXT("phone_ring"), Pos(TEXT("FrontDoorPoint")), 0.7f); });
	T = Say(TEXT("r_end3"), T + 2.4f);
	T = Say(TEXT("d_end3"), T + 1.1f);
	After(T - 0.3f, [this]() { FadeTo(1.f, 0.05f); SetLoop(TEXT("amb"), TEXT(""), 0.f, 0.05f); SetLoop(TEXT("music"), TEXT(""), 0.f, 0.05f, EWCSnd::Music); });
	T += 2.5f;
	After(T + 5.f, [this]()
	{
		Mode = EWCMode::Ending;
		BigText = TEXT("EDITH'S LAST CALL");
		BigSub = TEXT("");
		BigTarget = 1.f;
		UGameplayStatics::DeleteGameInSlot(TEXT("WellnessCheck"), 0);
	});
	After(T + 11.f, [this]() { BigTarget = 0.f; });
	After(T + 13.5f, [this]() { Mode = EWCMode::Credits; CreditsScroll = 0.f; });
	After(T + 13.5f + 38.f, [this]()
	{
		SetLoop(TEXT("music"), TEXT(""), 0.f, 3.f, EWCSnd::Music);
		Play2D(TEXT("radio_static"), 0.6f, EWCSnd::Voice);
		Mode = EWCMode::Playing;       // (so the line system runs; input stays locked)
		float T2 = Say(TEXT("m_post"), 1.5f);
		After(T2 + 2.5f, [this]() { QuitToMenu(); });
	});
}
