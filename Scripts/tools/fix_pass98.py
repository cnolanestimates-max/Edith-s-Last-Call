"""Pass 98: from Cheyenne's play-test of 2026-11-19 (15:26 to 15:31 UTC).
  - flashlight: 20% wider and 30% longer (her correction to "50% brighter")
  - the flashlight hand was a right hand on the left: mirrored
  - television: the tape's sound goes round with the picture (it played once and never again), and the first showing
    stays on until he switches it off
  - no outside ambience during the drive (the birds belong to the yard, after he gets out)
  - the house's "door somewhere" cue is gone from the random noises; instead, twice in the game at most, a door near him
    really opens by itself, with its creak
  - he calls out to her while he looks round, before the first sight of her ("Mrs. Harrow?" ... three times)
  - developer keys (only with -WCDev): F9 the upstairs thump is due now, F10 the quiet gap is over"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

edit(R + "Source/WellnessCheck/WCCharacter.cpp", [
    ('''Flash->SetInnerConeAngle(10.f);
	Flash->SetOuterConeAngle(31.f);
	Flash->SetAttenuationRadius(390.f);''', '''Flash->SetInnerConeAngle(12.f);
	Flash->SetOuterConeAngle(37.f);                 // 20% wider
	Flash->SetAttenuationRadius(510.f);             // 30% longer'''),
    ('''Spill->SetInnerConeAngle(20.f);
	Spill->SetOuterConeAngle(52.f);
	Spill->SetAttenuationRadius(300.f);''', '''Spill->SetInnerConeAngle(24.f);
	Spill->SetOuterConeAngle(60.f);
	Spill->SetAttenuationRadius(390.f);'''),
    ('''FlashHand->SetRelativeLocation(FVector(-19.f, 0.f, -1.f));''', '''FlashHand->SetRelativeLocation(FVector(-19.f, 0.f, -1.f));
	FlashHand->SetRelativeScale3D(FVector(1.f, -1.f, 1.f));          // the model is a right hand; it is held in the left'''),
])

edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('int32 TVPhase = 0, TVTape = 0;', 'int32 TVPhase = 0, TVTape = 0, TVLoop = -1, TVTapeNow = 1;'),
    ('void OutsideProgress();', '''void OutsideProgress();
	bool DoorOpensByItself();
	int32 DoorEvents = 0, CallStep = 0;
	double NextDoorAt = -1.0;
	bool bDev = false;'''),
])

edit(R + "Source/WellnessCheck/WCEvents.cpp", [
    ('''TVAudio = PlayAt(FString::Printf(TEXT("tv_tape_%d"), N), At, 1.f, 1.f, 2400.f);''',
     '''TVTapeNow = N;
	TVLoop = -1;                                    // the sound is started (and restarted each time round) in TickTV'''),
    ('''const float Runs = TVTape <= 1 ? 420.f : 75.f;
		if (TVAudio.IsValid() && !TVAudio->IsPlaying() && T < Runs - 2.f) TVAudio->Play();          // the tape comes round again
		if (T > Runs) TVOff(false);''', '''// the tape and its voices come round together, every twenty seconds
		const int32 LoopNow = FMath::FloorToInt(T / 20.f);
		if (LoopNow != TVLoop)
		{
			TVLoop = LoopNow;
			if (TVAudio.IsValid()) TVAudio->Stop();
			TVAudio = PlayAt(FString::Printf(TEXT("tv_tape_%d"), TVTapeNow), At, 1.5f, 1.f, 2000.f);
		}
		// the first showing (it is on when he comes in) plays until he switches it off; later ones for 75 s
		if (TVTape > 1 && T > 75.f) TVOff(false);'''),
])

edit(R + "Source/WellnessCheck/WCHouse.cpp", [
    ('''SetLoop(TEXT("amb"), TEXT("amb_night"), 0.25f, 1.f);
		TickDrive(0.f);''', '''SetLoop(TEXT("amb"), TEXT(""), 0.f, 1.f);              // windows up: the night is not heard until he gets out
		TickDrive(0.f);'''),
    ('''if (!bFilterInit) { bFilterInit = true;''', '''if (!bFilterInit) bDev = FParse::Param(FCommandLine::Get(), TEXT("WCDev"));
	if (bDev)
	{
		if (APlayerController* DevPC = GetWorld()->GetFirstPlayerController())
		{
			if (DevPC->WasInputKeyJustPressed(EKeys::F9) && Has(TEXT("inside")) && !Has(TEXT("heard_upstairs")))
			{
				InsideAt = PlaySeconds - 700.f;                      // as if he had been in the house long enough
				BuildStep = FMath::Max(BuildStep, 7);
				ShowToast(TEXT("DEV: the upstairs thump is due. Walk through a doorway downstairs."));
			}
			if (DevPC->WasInputKeyJustPressed(EKeys::F10))
			{
				NextScareAt = Clock; EyeNextAt = Clock; TVNextAt = Clock; NextDoorAt = Clock; NextLightKill = Clock;
				ShowToast(TEXT("DEV: the quiet gap is over. Whatever is waiting may happen now."));
			}
		}
	}
	if (!bFilterInit) { bFilterInit = true;'''),
])

edit(R + "Source/WellnessCheck/WCStory.cpp", [
    # the three call-outs
    ('''	{ TEXT("d_foyer"), TEXT("Deputy Brandt"),''', '''	{ TEXT("d_call1"), TEXT("Deputy Brandt"), TEXT("Mrs. Harrow?"), 0 },
	{ TEXT("d_call2"), TEXT("Deputy Brandt"), TEXT("Hello? ...Anybody home?"), 0 },
	{ TEXT("d_call3"), TEXT("Deputy Brandt"), TEXT("Mrs. Harrow, it's the sheriff's office. Can you hear me?"), 0 },
	{ TEXT("d_foyer"), TEXT("Deputy Brandt"),'''),
    ('''{ TEXT("steps_above"), 1.3f, 100.f, 500.f, 1.f, 1 }, { TEXT("wind_gust"), 1.6f, 800.f, 1400.f, 0.8f, 0 }, { TEXT("door_far"), 0.8f, 700.f, 1300.f, 0.9f, 1 },''',
     '''{ TEXT("steps_above"), 1.3f, 100.f, 500.f, 1.f, 1 }, { TEXT("wind_gust"), 1.6f, 800.f, 1400.f, 0.8f, 0 },'''),
    ('''	if (FLoop* Drone = Loops.Find(TEXT("drone")))''', '''	// he calls out to her while he looks round, three times, before he has seen anything
	if (Has(TEXT("inside")) && !Has(TEXT("heard_upstairs")) && !bBusy && CallStep < 3 && Clock > SpeechFreeAt)
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
	if (FLoop* Drone = Loops.Find(TEXT("drone")))'''),
])

p = R + "Source/WellnessCheck/WCEvents.cpp"
s = open(p, encoding="utf-8").read()
assert "DoorOpensByItself" not in s
s += r'''
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
		if (D->bLocked || D->IsOpen()) continue;
		const FVector At = D->GetActorLocation() + FVector(0, 0, 100);
		const float Dist = FVector::Dist(Eye, At);
		if (Dist < 260.f || Dist > 950.f || FMath::Abs(At.Z - Eye.Z) > 160.f) continue;
		FHitResult Hit;
		FCollisionQueryParams Q(FName(TEXT("WCDoorSelf")), false, P);
		Q.AddIgnoredActor(D);
		if (GetWorld()->LineTraceSingleByChannel(Hit, Eye, At, ECC_Visibility, Q)) continue;         // he has to be able to see it go
		const float Facing = FVector::DotProduct(P->EyeForward(), (At - Eye).GetSafeNormal());
		const float Score = Facing + 0.3f * (1.f - Dist / 950.f);
		if (Facing > 0.2f && Score > BestScore) { BestScore = Score; Best = D; }
	}
	if (!Best) return false;
	Best->SetOpen(true, 6.5f, true);                                          // slowly
	PlayAt(TEXT("door_creak_long"), Best->GetActorLocation() + FVector(0, 0, 110), 1.f, 0.9f, 2200.f);
	Tension = FMath::Max(Tension, 0.5f);
	UE_LOG(LogWCEvents, Display, TEXT("WCDOOR t=%.1f %s opened by itself"), PlaySeconds, *Best->GetActorNameOrLabel());
	return true;
}
'''
if '#include "EngineUtils.h"' not in s:
    s = s.replace('#include "Engine/PostProcessVolume.h"', '#include "Engine/PostProcessVolume.h"\n#include "EngineUtils.h"', 1)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("pass 98 applied")
