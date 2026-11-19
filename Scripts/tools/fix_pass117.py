"""Pass 117: the book scare has to be seen (Cheyenne 2026-11-19 20:09 UTC: "the game needs to make sure the player is directly
in front of the hole ... the eye was missed completely").
  - the book only comes out when he is standing square in front of it, close (within 30 cm to either side, 35 to 115 cm back)
  - as it comes out his view settles onto the hole (his hands are on the book for that half second anyway; this is not the
    camera being taken away from him: it ends before she is seen and he is looking where he was already looking)"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
p = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/WCHouse.cpp"
edit(p, [
    ('''		// (it used to wait until he had read her scrap about the hollow book.''', '''		// he has to be standing square in front of it, and close, for what is behind it to be seen at all
		if (AWCInteractable* Bk = Thing(TEXT("book_settlers")))
		{
			const FVector Rel = P->GetActorLocation() - Bk->GetActorLocation();
			const float Back = -Rel.Y, Aside = FMath::Abs(Rel.X);                 // the bookcase is on the hall-side wall: the room is toward -Y
			if (Aside > 30.f || Back < 35.f || Back > 115.f)
			{
				if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 2.5; Feedback(TEXT("Stand right in front of it.")); }
				return true;
			}
		}
		// (it used to wait until he had read her scrap about the hollow book.'''),
    ('''	if (EyeW) EyeW->Reveal();
	// a cold glimmer on her eye''', '''	if (EyeW) EyeW->Reveal();
	// while his hands are on the book his eyes settle on the gap it is leaving
	{
		const FVector Gap = EyeW ? EyeW->GetActorLocation() : From;
		for (int32 i = 1; i <= 16; ++i) After(i * 0.035f, [this, Gap]()
		{
			AWCCharacter* Q = Player();
			if (!Q || !Q->GetController()) return;
			const FRotator Want = (Gap - Q->EyeLocation()).Rotation();
			Q->GetController()->SetControlRotation(FMath::RInterpTo(Q->GetController()->GetControlRotation(), Want, 0.035f, 9.f));
		});
	}
	// a cold glimmer on her eye'''),
])
edit("C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/WCAuto.cpp", [
    ('''			At(TEXT("at:592,-296,92,124,0")); Wait(1.0f);
			At(TEXT("book"));''', '''			At(TEXT("at:560,-292,92,112,-9")); Wait(1.0f);            // a little off to one side and looking down: the game has to bring his eyes to the gap
			At(TEXT("book"));'''),
])
print("pass 117 applied")
