import io
R="C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
def sub(f, old, new, count=1):
    s=io.open(R+f,encoding="utf-8").read()
    assert old in s, (f, old[:60])
    s=s.replace(old,new,count)
    io.open(R+f,"w",encoding="utf-8",newline="\n").write(s)
sub("WCAuto.cpp","enum { A_Go, A_Use, A_Wait, A_WaitFlag, A_Shot, A_Fire, A_Look, A_Light, A_LookHer, A_WaitHer, A_Crouch };",
    "enum { A_Go, A_Use, A_Wait, A_WaitFlag, A_Shot, A_Fire, A_Look, A_Light, A_LookHer, A_WaitHer, A_Crouch, A_Tele };")
sub("WCAuto.cpp",'''	// ---- arrival
	Wait(5.f);''','''	if (FParse::Param(FCommandLine::Get(), TEXT("WCTour")))
	{
		// screenshot tour: stand at every point tagged "Tour" with the flashlight on
		TArray<FName> Names;
		for (TActorIterator<AActor> It(GetWorld()); It; ++It)
		{
			if (!It->ActorHasTag(TEXT("Tour"))) continue;
			for (const FName& T : It->Tags) if (T != TEXT("Tour")) Names.Add(T);
		}
		Names.Sort([](const FName& A, const FName& B) { return A.ToString() < B.ToString(); });
		Steps.Reset();
		Subtitles.Reset();
		if (AWCCharacter* Pl = Player()) { Pl->SetInputLocked(false); Pl->SetFlashlight(true, false); }
		Fade = 0.f; FadeTarget = 0.f;
		if (FParse::Param(FCommandLine::Get(), TEXT("WCBright")))
		{
			if (AWCCharacter* Pl = Player())
			{
				UPointLightComponent* L = NewObject<UPointLightComponent>(Pl);
				L->SetupAttachment(Pl->GetRootComponent());
				L->SetRelativeLocation(FVector(0, 0, 60));
				L->RegisterComponent();
				L->SetIntensityUnits(ELightUnits::Lumens);
				L->SetIntensity(1800.f);
				L->SetAttenuationRadius(2500.f);
				L->SetCastShadows(false);
			}
		}
		Wait(4.f);
		for (const FName& N : Names) { AutoSteps.Add({ A_Tele, N, 0.f }); Wait(2.6f); Shot(*N.ToString()); }
		AutoIndex = 0;
		AutoStepStart = Clock;
		if (!AutoShotDir.IsEmpty()) { AutoShotDir = FPaths::ConvertRelativePathToFull(AutoShotDir); IFileManager::Get().MakeDirectory(*AutoShotDir, true); }
		UE_LOG(LogWCAuto, Display, TEXT("WCAUTO tour, %d points"), Names.Num());
		return;
	}
	// ---- arrival
	Wait(5.f);''')
sub("WCAuto.cpp",'''	case A_Light: if''','''	case A_Tele:
		if (AActor* T = AutoTarget(this, S.Arg)) P->TeleportToCheckpoint(T->GetActorLocation(), T->GetActorRotation().Yaw);
		Next(); return;
	case A_Light: if''')
sub("WCAuto.cpp",'#include "EngineUtils.h"','#include "EngineUtils.h"\n#include "Components/PointLightComponent.h"')
sub("WCDirector.cpp",'''	bAuto = FParse::Param(FCommandLine::Get(), TEXT("WCAuto"));''','''	bAuto = FParse::Param(FCommandLine::Get(), TEXT("WCAuto")) || FParse::Param(FCommandLine::Get(), TEXT("WCTour"));''')
print("ok")
