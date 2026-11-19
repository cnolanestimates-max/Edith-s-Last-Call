"""Cheyenne 03:54 to 04:04 UTC:
 - every rush of hers half as fast again;
 - fear that is not her body: the horn phonograph in her sitting room plays by itself.  He lifts the needle; a few steps
   away it starts again; he lifts it again; the third time the flashlight dies and he stands in the dark with the music;
   the light comes back, he stops it, turns away, and she is in the doorway for an instant;
 - "you left me": whispers far off, then closer and fast in her own old voice, a beat of nothing, then her many-voiced
   scream right behind him with a church bell and a shake of the screen (in Daniel's room);
 - house lights go out sooner and more often."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
P = "C:/GameDev/Unreal/WellnessCheck/"
R = P + "Source/WellnessCheck/"

edit(R + "WCDirector.h", [
    ('''		bool Gate() const { return Clock >= NextScareAt && StalkState == 0 && !bDriving; }''',
     '''		bool Gate() const { return Clock >= NextScareAt && StalkState == 0 && !bDriving && !bEventBusy; }'''),
    ('''	float ShadowDist = -1.f, ShadowT = 0.f;''', '''	// things that act by themselves (WCEvents.cpp)
	bool bEventBusy = false;                  // one of them is playing: no other scare and no hunt starts
	int32 RecordPhase = 0;
	double RecordAt = 0.0, RecordSeenAt = -1.0;
	TWeakObjectPtr<UAudioComponent> RecordAudio;
	void TickRecord(float Dt);
	void RecordPlay(bool bOn);
	bool EventsEvent(FName Id);
	void LeftScare();
	float ShadowDist = -1.f, ShadowT = 0.f;'''),
])
edit(R + "WCHouse.cpp", [
    ('''bool AWCDirector::HouseEvent(FName Id)
{
	AWCCharacter* P = Player();
	if (!P) return false;''', '''bool AWCDirector::HouseEvent(FName Id)
{
	AWCCharacter* P = Player();
	if (!P) return false;
	if (EventsEvent(Id)) return true;'''),
    ('''	TickStalk(Dt);''', '''	TickStalk(Dt);
	TickRecord(Dt);'''),
    ('''&& Clock >= NextScareAt && Clock >= NextStalkAt && StalksDone < 4 &&''', '''&& Clock >= NextScareAt && Clock >= NextStalkAt && StalksDone < 4 && !bEventBusy &&'''),
    ('''			if (bAmbush || bClose) H->MoveAlong(Route, bAmbush ? 1350.f : 1150.f, TEXT("Run"));''', '''			if (bAmbush || bClose) H->MoveAlong(Route, bAmbush ? 2000.f : 1725.f, TEXT("Run"));      // half as fast again (Cheyenne, 03:54)'''),
    ('''		const float Patience = FMath::Lerp(95.f, 28.f, FMath::Clamp(Tension * 1.3f, 0.f, 1.f));''', '''		const float Patience = FMath::Lerp(58.f, 18.f, FMath::Clamp(Tension * 1.3f, 0.f, 1.f));          // lights go out often, for no reason'''),
])
edit(R + "WCStory.cpp", [
    ('''			H->MoveAlong(Pts, bLockInRun ? 1000.f : 125.f, bLockInRun ? TEXT("Run") : TEXT("Walk"));''', '''			H->MoveAlong(Pts, bLockInRun ? 1500.f : 125.f, bLockInRun ? TEXT("Run") : TEXT("Walk"));'''),
    ('''			H->MoveAlong(Pts, 1250.f, TEXT("Run"));
		}
	}
	if (bSprintActive && H->IsShown() && (H->DistToPlayer() < 175.f''', '''			H->MoveAlong(Pts, 1875.f, TEXT("Run"));
		}
	}
	if (bSprintActive && H->IsShown() && (H->DistToPlayer() < 175.f'''),
    ('''						E2->MoveAlong(Pts, 1300.f, TEXT("Run"), [this]()''', '''						E2->MoveAlong(Pts, 1950.f, TEXT("Run"), [this]()'''),
    ('''			E->MoveAlong(Pts, 1250.f, TEXT("Run"));''', '''			E->MoveAlong(Pts, 1875.f, TEXT("Run"));'''),
    ('''			E->MoveAlong(Pts, 860.f, TEXT("Crawl"), [this]()''', '''			E->MoveAlong(Pts, 1250.f, TEXT("Crawl"), [this]()'''),
    ('''		H->MoveAlong(Pts, 1200.f, TEXT("Run"));
		P->FlickerLight(1.6f, 0.8f);''', '''		H->MoveAlong(Pts, 1800.f, TEXT("Run"));
		P->FlickerLight(1.6f, 0.8f);'''),
    ('''		H->MoveAlong(Pts, 760.f, TEXT("Run"), [this]()''', '''		H->MoveAlong(Pts, 1140.f, TEXT("Run"), [this]()'''),
    ('''	H->MoveAlong(Pts, 1100.f, TEXT("Run"), [this]()''', '''	H->MoveAlong(Pts, 1650.f, TEXT("Run"), [this]()'''),
    ('''	{ TEXT("m_laugh1"), TEXT(""), TEXT("Heh heh heh heh... hee hee hee."), 2 },''', '''	{ TEXT("m_left"), TEXT(""), TEXT("You left me. You left me. You left me. You left me."), 2 },
	{ TEXT("m_whyleave"), TEXT("Edith"), TEXT("WHY DID YOU LEAVE ME!"), 3 },
	{ TEXT("m_laugh1"), TEXT(""), TEXT("Heh heh heh heh... hee hee hee."), 2 },'''),
])
edit(R + "WCGame.cpp", [
    ('''TEXT("#Music"), TEXT("Kevin MacLeod (incompetech.com)"),''', '''TEXT("#Music"), TEXT("Kevin MacLeod (incompetech.com)"), TEXT("Darren Curtis (darrencurtismusic.com)"),'''),
])

io.open(R + "WCEvents.cpp", "w", encoding="utf-8", newline="\n").write(r'''// Things in the house that act by themselves: the phonograph that will not stay off, and her voice coming closer.
// (Cheyenne: "fear can be cultivated by sounds, and by other stuff too ... stuff that can turn on by itself".)
#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"

#include "Components/AudioComponent.h"

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
	const double In = Clock - RecordAt;
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
			Go(8);
		}
		break;
	}
	case 8:      // gone in an instant
	{
		AWCEntity* H = Her();
		if (H && H->IsShown() && RecordSeenAt < 0.0 && PlayerSees(H->HeadLocation(), 0.5f, 2600.f)) { RecordSeenAt = Clock; Play2D(TEXT("sting_soft"), 0.7f, EWCSnd::Music); }
		if ((RecordSeenAt > 0.0 && Clock - RecordSeenAt > 0.5) || In > 7.0)
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
	SetLoop(TEXT("tick"), TEXT("clock_tick"), 0.55f, 4.f);
	PlayAt(TEXT("whisper_far"), Behind(1300.f, 0.f), 0.6f, 1.f, 2600.f);
	After(4.5f, [this, Behind]() { PlayAt(TEXT("whisper_far"), Behind(800.f, 0.f), 0.8f, 1.05f, 2200.f); });
	After(8.0f, [this, Behind]() { PlayAt(TEXT("VO/m_left"), Behind(520.f, 20.f), 0.55f, 1.f, 1800.f); });
	After(11.0f, [this, Behind]() { PlayAt(TEXT("VO/m_left"), Behind(260.f, 30.f), 0.8f, 1.06f, 1200.f); });
	After(12.4f, [this, Behind]() { PlayAt(TEXT("VO/m_left"), Behind(130.f, 40.f), 1.f, 1.12f, 900.f); });
	// the beat: everything stops, even the clock
	After(14.8f, [this]()
	{
		SetLoop(TEXT("tick"), TEXT(""), 0.f, 0.15f);
		SetLoop(TEXT("amb"), TEXT(""), 0.f, 0.3f);
		SetLoop(TEXT("music"), TEXT(""), 0.f, 0.3f);
		for (TObjectIterator<UAudioComponent> It; It; ++It) if (It->GetWorld() == GetWorld() && It->Sound && It->Sound->GetName().Contains(TEXT("m_left"))) It->FadeOut(0.1f, 0.f);
		Tension = 0.15f;
	});
	// then all at once
	After(18.0f, [this]()
	{
		Play2D(TEXT("bell_toll"), 1.f);
		Say(TEXT("m_whyleave"));
		if (AWCCharacter* Pl = Player()) { Pl->AddShake(1.f); Pl->FlickerLight(1.6f, 0.9f); }
		Tension = 1.f;
	});
	After(22.5f, [this]()
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
	if (Id == TEXT("use:phonograph"))
	{
		if (RecordPhase == 1 || RecordPhase == 3 || RecordPhase == 6)
		{
			RecordPlay(false);
			RecordPhase = RecordPhase == 6 ? 7 : RecordPhase + 1;
			RecordAt = Clock;
			UE_LOG(LogWCEvents, Display, TEXT("WCRECORD t=%.1f he lifted the needle, phase %d"), PlaySeconds, RecordPhase);
		}
		else Think(TEXT("The record is worn white in one groove. One song. I can almost hear which."));
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
''')

# ---------------------------------------------------------------- level: the phonograph can be used; where she stands
edit(P + "Scripts/level/build_house.py", [
    ('''place("Phonograph", 880, -540, GZ, 20, S)''', '''interact("WCUsable", "phonograph", "Phonograph", 880, -540, GZ, 20, "Look at the phonograph", (32, 32, 46), (0, 0, 62))
point("Her_RecordDoor", 1392, -188, GZ, -144)'''),
])
edit(P + "Scripts/level/looks.py", [
    ('''    ("phonograph", 880, -540, 100, "The record is worn white in one groove. One song. I can almost hear which.", (30, 30, 40)),''', ''''''),
])
# ---------------------------------------------------------------- voice: the two new lines
edit(P + "Scripts/audio/gen_vo.py", [
    ('''    "m_laugh1": "No words at all: only laughter.''', '''    "m_left": "Whispered very fast, breathless, the same three words over and over without a pause, hurt and accusing, getting more urgent. An old woman, close to the microphone.",
    "m_whyleave": "Not a whisper: SCREAMED at full force, raw, furious and heartbroken, right in the listener's face, the last word drawn out into a shriek.",
    "m_laugh1": "No words at all: only laughter.'''),
])
edit(P + "Scripts/audio/demon_vo.py", [
    ('''HUMAN = ("m_mem", "m_end")''', '''HUMAN = ("m_mem", "m_end", "m_left")'''),
])
print("ok")
