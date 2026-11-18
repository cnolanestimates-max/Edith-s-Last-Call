"""Soft-lock guards and clearer leads for the longer errand chain."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCStory.cpp", [
    # the phone rings even if he never goes back to the nailed door
    ('''				After(T + 0.8f, [this]() { SetObjective(TEXT("Find another way out")); Checkpoint(TEXT("lockin_done")); });''',
     '''After(T + 0.8f, [this]() { SetObjective(TEXT("Find another way out")); Checkpoint(TEXT("lockin_done")); });
				After(250.f * TestPace, [this]() { Set(TEXT("backdoor_tried")); });'''),
    # doors that need a particular key say where to look
    ('''	if (Id.ToString().StartsWith(TEXT("locked:")) && !Is(Id, TEXT("locked:back")))
	{''', '''if (Is(Id, TEXT("locked:up_ell")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Think(TEXT("Locked. A newer lock than the others. The man of the house would have kept the key.")); }
		return;
	}
	if (Is(Id, TEXT("locked:up_attic")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Think(TEXT("The attic. Locked. Danny's things are up there.")); }
		return;
	}
	if (Is(Id, TEXT("locked:sitting")) || Is(Id, TEXT("locked:up_prayer")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Think(TEXT("Locked. Scratches round the keyhole, from the inside.")); }
		return;
	}
	if (Id.ToString().StartsWith(TEXT("locked:")) && !Is(Id, TEXT("locked:back")))
	{'''),
])
edit(R + "WCHouse.cpp", [
    # if he is already upstairs when the quiet runs out, the house still makes its move
    ('''	// the rocking chair
	if (RockActor.IsValid() && Clock < RockUntil)''', '''if (!Has(TEXT("heard_upstairs")) && T > 640.f && L.Z > 300.f && L.Z < 650.f)
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
	if (RockActor.IsValid() && Clock < RockUntil)'''),
])
edit(R + "WCGame.cpp", [
    ('''{ TEXT("keep_daniel"), TEXT("Daniel's tags (his footlocker, attic)") } };''', '''{ TEXT("keep_daniel"), TEXT("Daniel's tags (his footlocker, attic)") }, { TEXT("shears"), TEXT("Something to cut the knots (her sewing shears)") } };'''),
])
print("ok")
