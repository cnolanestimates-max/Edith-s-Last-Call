"""Memories: when she has hold of him he sees, in order, the three things that made her (one per grab).
The Company's silhouettes only start to appear after the first sight of her."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"

edit(R + "WCDirector.h", [
    ('''	double GrabHoldUntil = 0.0;''', '''	double GrabHoldUntil = 0.0;
	/** A memory of hers (1 family leaving, 2 the book in the attic, 3 the asking), shown from a fixed camera, then Then(). */
	void PlayMemory(int32 N, TFunction<void()> Then);'''),
])
edit(R + "WCHouse.cpp", [
    ('''	ShowTagged(TEXT("BulbOn"), false);''', '''	ShowTagged(TEXT("BulbOn"), false);
	for (const TCHAR* M : { TEXT("Mem1"), TEXT("Mem2"), TEXT("Mem3") }) ShowTagged(M, false);'''),
    ('''	After(Hold, [this, Then]()
	{
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		if (Then) Then();
	});''', '''	After(Hold, [this, Then]()
	{
		// the first three times she has him, he sees what made her
		const int32 N = !Has(TEXT("mem1")) ? 1 : (!Has(TEXT("mem2")) ? 2 : (!Has(TEXT("mem3")) ? 3 : 0));
		if (N > 0 && !Has(TEXT("placed")) && Find(FName(*FString::Printf(TEXT("Cam_Mem%d"), N)))) { PlayMemory(N, Then); return; }
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		if (Then) Then();
	});'''),
])
p = R + "WCHouse.cpp"
s = io.open(p, encoding="utf-8").read()
s = s.replace('#include "Kismet/GameplayStatics.h"', '#include "Kismet/GameplayStatics.h"\n#include "Engine/PostProcessVolume.h"', 1)
s = s.rstrip() + '''

// ================================================================================================ her memories
void AWCDirector::PlayMemory(int32 N, TFunction<void()> Then)
{
	const FName Group(*FString::Printf(TEXT("Mem%d"), N));
	Set(FName(*FString::Printf(TEXT("mem%d"), N)));
	UE_LOG(LogWCHouse, Display, TEXT("WCMEMORY t=%.1f %d"), PlaySeconds, N);
	bBusy = true;
	if (AWCCharacter* P = Player()) P->SetInputLocked(true);
	FadeTo(1.f, 0.22f);
	auto Grade = [this](bool bOn)
	{
		for (TActorIterator<APostProcessVolume> It(GetWorld()); It; ++It) if (It->ActorHasTag(TEXT("PP_Memory"))) It->bEnabled = bOn;
	};
	After(0.4f, [this, N, Group, Grade]()
	{
		if (AWCEntity* E = Her()) E->Vanish();
		ShowTagged(Group, true);
		Grade(true);
		if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
		{
			if (AActor* Cam = Find(FName(*FString::Printf(TEXT("Cam_Mem%d"), N)))) PC->SetViewTargetWithBlend(Cam, 0.f);
		}
		SetLoop(TEXT("mem"), TEXT("musicbox"), 0.5f, 1.2f);
		SetLoop(TEXT("amb"), TEXT(""), 0.f, 0.4f);
		FadeTo(0.f, 1.6f);
		static const TCHAR* Caption[] = { TEXT("The last Thanksgiving anyone came."), TEXT("The attic. Her grandmother's book, under Danny's things."), TEXT("The ninth. She asked. Something answered.") };
		Think(Caption[FMath::Clamp(N - 1, 0, 2)], 7.f);
		Say(FName(*FString::Printf(TEXT("m_mem%d"), N)), 1.8f);
	});
	After(8.2f, [this]() { FadeTo(1.f, 0.6f); });
	After(9.0f, [this, Group, Grade, Then]()
	{
		ShowTagged(Group, false);
		Grade(false);
		AWCCharacter* P = Player();
		if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0)) { if (P) PC->SetViewTargetWithBlend(P, 0.f); }
		SetLoop(TEXT("mem"), TEXT(""), 0.f, 0.2f);
		Subtitles.Reset();
		ApplyWorldState();
		Play2D(TEXT("her_scream_short"), 1.f);
		if (P) P->SetInputLocked(false);
		if (Then) Then();
	});
}
'''
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
edit(R + "WCWorld.cpp", [
    ('''	bOut = !bScripted;
	SetActorHiddenInGame(bScripted);''', '''	bOut = !bScripted && Kind != 2;            // the Company waits until she has been seen
	SetActorHiddenInGame(!bOut);'''),
    ('''	Super::Tick(Dt);
	if (!bOut) return;
	AWCDirector* D = AWCDirector::Get(this);''', '''	Super::Tick(Dt);
	if (Kind == 2 && !bOut && !bGone && !bScripted)
	{
		AWCDirector* Dir = AWCDirector::Get(this);
		if (Dir && Dir->Has(TEXT("peek_done")) && Dir->Player() && FVector::Dist(Dir->Player()->GetActorLocation(), Home) > 900.f) Reveal();
		return;
	}
	if (!bOut) return;
	AWCDirector* D = AWCDirector::Get(this);'''),
])
edit(R + "WCStory.cpp", [
    ('''	{ TEXT("m_end"), TEXT("Edith"), TEXT("...thank you."), 2 },''', '''	{ TEXT("m_end"), TEXT("Edith"), TEXT("...thank you."), 2 },
	{ TEXT("m_mem1"), TEXT("Edith"), TEXT("Ruthie. Don't go. Stay for supper. Please. I've set your place."), 2 },
	{ TEXT("m_mem2"), TEXT("Edith"), TEXT("Grandmother Wren's book. ...It will sit with you. It will never go."), 2 },
	{ TEXT("m_mem3"), TEXT("Edith"), TEXT("I only want company. Please. Never let me be alone again."), 2 },'''),
])
print("ok")
