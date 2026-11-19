"""Pass 116: the eye behind the settlers book could not be seen (photo check spot2: the book came straight out along his line
of sight and hid the hole, then she was gone 0.55 s later, in the dark).  The book is now knocked aside, the eye is held on
him for two seconds with a cold glimmer on it, and only then does she go along the wall."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
p = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/WCHouse.cpp"
edit(p, [
    ('''	if (EyeW) EyeW->Reveal();
	// ...and she is looking at him through the wall
	After(0.95f, [this, EyeW, Book, From, Out]()
	{''', '''	if (EyeW) EyeW->Reveal();
	// a cold glimmer on her eye, so it reads in the dark of the gap whatever his own light is doing
	TWeakObjectPtr<UPointLightComponent> Glim;
	if (EyeW)
	{
		UPointLightComponent* G = NewObject<UPointLightComponent>(EyeW);
		G->SetupAttachment(EyeW->GetRootComponent());
		G->RegisterComponent();
		G->SetWorldLocation(EyeW->GetActorLocation() + Out * 10.f);
		G->SetIntensityUnits(ELightUnits::Lumens);
		G->SetIntensity(0.f);
		G->SetAttenuationRadius(48.f);
		G->SetLightColor(FLinearColor(0.75f, 0.85f, 1.f));
		G->SetCastShadows(false);
		Glim = G;
	}
	// ...and she is looking at him through the wall
	After(0.62f, [this, EyeW, Book, From, Out, Glim]()
	{
		if (Glim.IsValid()) Glim->SetIntensity(26.f);'''),
    ('''Book->SetActorLocation(FVector(Start.X + Out.X * 22.f * U, Start.Y + Out.Y * 22.f * U, FMath::Lerp(Start.Z, FloorZ, U * U)));''',
     '''Book->SetActorLocation(FVector(Start.X + (Out.X * 6.f - Out.Y * 34.f) * U, Start.Y + (Out.Y * 6.f + Out.X * 34.f) * U, FMath::Lerp(Start.Z, FloorZ, U * U)));      // knocked aside, out of his line of sight'''),
    ('''		// she is away along the inside of the wall
		After(0.55f, [this, EyeW]()
		{
			if (EyeW)
			{''', '''		// she holds his eye for two seconds, then she is away along the inside of the wall
		After(2.1f, [this, EyeW, Glim]()
		{
			if (Glim.IsValid()) Glim->SetIntensity(0.f);
			if (EyeW)
			{'''),
    ('''	After(2.9f, [this]()
	{
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		bBusy = false;
		Rest(120.f);''', '''	After(4.1f, [this]()
	{
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		bBusy = false;
		Rest(120.f);'''),
])
s = open(p, encoding="utf-8").read()
if '#include "Components/PointLightComponent.h"' not in s:
    s = s.replace('#include "Components/LightComponent.h"', '#include "Components/LightComponent.h"\n#include "Components/PointLightComponent.h"', 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
edit("C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/WCAuto.cpp", [
    ('''At(TEXT("book")); Wait(0.75f); Shot(TEXT("spot_9_book_coming_out")); Wait(0.3f); Shot(TEXT("spot_9b_her_eye")); Wait(0.5f); Shot(TEXT("spot_9c")); Wait(2.5f); Shot(TEXT("spot_9d_after"));''',
     '''At(TEXT("book")); Wait(0.55f); Shot(TEXT("spot_9_book_coming_out")); Wait(0.75f); Shot(TEXT("spot_9b_her_eye")); Wait(0.8f); Shot(TEXT("spot_9c_her_eye_still")); Wait(2.6f); Shot(TEXT("spot_9d_after"));'''),
])
print("pass 116 applied")
