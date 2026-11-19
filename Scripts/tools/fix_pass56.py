"""The hand under the bed starts when he can actually see the music box (within about 4 m, nothing in the way), not the
moment he steps through the door, where the rocking horse hid it.  The toys are moved off that line.  Test runs photograph
the moment by themselves."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(R + "WCStory.cpp", [
    ('''	if (Is(Id, TEXT("trig:t_kids")) && Has(TEXT("kids_open")) && !Has(TEXT("underbed_done")) && Gate()) { ScareUnderBed(); return; }''', ''''''),
    ('''	if (Has(TEXT("backdoor_tried")) && !Has(TEXT("phone_ringing"))''', '''	if (Has(TEXT("kids_open")) && !Has(TEXT("underbed_done")) && !bBusy && Gate())
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
	if (Has(TEXT("backdoor_tried")) && !Has(TEXT("phone_ringing"))'''),
    ('''	Tension = 0.8f;
	SetLoop(TEXT("amb"), TEXT("amb_house"), 0.1f, 1.5f);
	After(1.6f, [this, AtBox, BoxFrom, Dir]()''', '''	Tension = 0.8f;
	SetLoop(TEXT("amb"), TEXT("amb_house"), 0.1f, 1.5f);
	if (bAuto && !AutoShotDir.IsEmpty())
	{
		const FString Dir0 = AutoShotDir;
		After(3.6f, [Dir0]() { FScreenshotRequest::RequestScreenshot(Dir0 / TEXT("S7_auto_1_coming.png"), false, false); });
		After(5.2f, [Dir0]() { FScreenshotRequest::RequestScreenshot(Dir0 / TEXT("S7_auto_2_on_box.png"), false, false); });
		After(7.2f, [Dir0]() { FScreenshotRequest::RequestScreenshot(Dir0 / TEXT("S7_auto_3_taking.png"), false, false); });
	}
	After(1.6f, [this, AtBox, BoxFrom, Dir]()'''),
])
edit(L + "build_house.py", [
    ('''place("Rocking_Horse_Broken", 420, -300, UZ, 200, KD)''', '''place("Rocking_Horse_Broken", 440, -500, UZ, 200, KD)'''),
    ('''place("Jack_In_The_Box", 330, -250, UZ, 40, KD, collide=False)''', '''place("Jack_In_The_Box", 390, -560, UZ, 40, KD, collide=False)'''),
    ('''place("Toy_Train_Wind_Up", 560, -260, UZ, 130, KD, collide=False)''', '''place("Toy_Train_Wind_Up", 500, -545, UZ, 130, KD, collide=False)'''),
])
print("ok")
