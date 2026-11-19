"""Pass 95: sound, first curation pass (Cheyenne 2026-11-19 14:45 UTC: "it needs to be curated ... do not overwhelm the scene with
sound ... very low droning music, and every now and then a scuffle, a scratching, feet above you ... and then that's it";
"light switches flicking on and off completely off screen ... literally every 2 seconds").
  - the house's own noises: one every 35 to 80 s (it was every 5 to 13), never during a scare or a hunt, a little quieter;
    every one is logged (WCCUE) so the density of a run can be counted
  - she turns a light off at most every two to three and a half minutes (it was every 12 s)
  - the drone and the low bed sit lower"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''if (Has(TEXT("inside")) && !Has(TEXT("dawn")) && !bBusy && Clock > NextCue)
	{
		NextCue = Clock + Rng.FRandRange(5.f, 13.f) * (1.25f - 0.6f * Tension);''',
     '''if (Has(TEXT("inside")) && !Has(TEXT("dawn")) && !bBusy && Clock > NextCue && (bEventBusy || StalkState != 0))
	{
		NextCue = Clock + 20.0;                    // something staged is happening: the house keeps out of it
	}
	if (Has(TEXT("inside")) && !Has(TEXT("dawn")) && !bBusy && !bEventBusy && StalkState == 0 && Clock > NextCue)
	{
		// sound in moderation: one small thing, then a long quiet
		NextCue = Clock + Rng.FRandRange(35.f, 80.f) * (1.2f - 0.4f * Tension);'''),
    ('''if (Has(TEXT("locked_in")) && Rng.FRand() < 0.13f + 0.1f * Tension)
		{''', '''UE_LOG(LogWCStory, Display, TEXT("WCCUE t=%.1f %s"), PlaySeconds, Chosen->Name);
		if (Has(TEXT("locked_in")) && Rng.FRand() < 0.08f + 0.06f * Tension)
		{'''),
    ('''else PlayAt(Chosen->Name, P->GetActorLocation() + Off, Chosen->Vol * Rng.FRandRange(0.75f, 1.f), Rng.FRandRange(0.92f, 1.07f));''',
     '''else PlayAt(Chosen->Name, P->GetActorLocation() + Off, 0.8f * Chosen->Vol * Rng.FRandRange(0.75f, 1.f), Rng.FRandRange(0.92f, 1.07f));'''),
    ('''Drone->Target = Has(TEXT("inside")) && !Has(TEXT("dawn")) ? 0.5f + 0.4f * Tension : 0.f;''',
     '''Drone->Target = Has(TEXT("inside")) && !Has(TEXT("dawn")) ? 0.30f + 0.30f * Tension : 0.f;'''),
    ('''Low->Target = Has(TEXT("inside")) && !Has(TEXT("dawn")) ? 0.25f + 0.55f * Tension : 0.f;''',
     '''Low->Target = Has(TEXT("inside")) && !Has(TEXT("dawn")) ? 0.14f + 0.40f * Tension : 0.f;'''),
])
edit(R + "Source/WellnessCheck/WCHouse.cpp", [
    ('''// she turns it off
			NextLightKill = Clock + 12.0;''', '''// she turns it off: a staged thing, minutes apart, not a tic
			NextLightKill = Clock + Rng.FRandRange(120.f, 210.f) * FMath::Max(TestPace, 0.25f);'''),
    ('''Think(Room == TEXT("dining") ? TEXT("Nothing. The chandelier is on the floor.") : (Room == TEXT("prayer") ? TEXT("Nothing. Somebody took the bulb out.") : TEXT("Nothing.")));''',
     '''Feedback(TEXT("Nothing."));'''),
    ('''Think(Has(TEXT("seen_fusebox")) ? TEXT("Dead. It needs that fuse.") : TEXT("Dead. The whole house is dead. There'll be a fuse box somewhere off the kitchen."));''',
     '''Feedback(TEXT("Dead."));'''),
])
print("pass 95 applied")
