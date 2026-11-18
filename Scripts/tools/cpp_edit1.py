import io
R="C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
def sub(f, old, new, count=1):
    s=io.open(R+f,encoding="utf-8").read()
    assert old in s, (f, old[:60])
    s=s.replace(old,new,count)
    io.open(R+f,"w",encoding="utf-8",newline="\n").write(s)
# world state extras
sub("WCStory.cpp",'''	ShowTagged(TEXT("Show_drawer"), Has(TEXT("phone_done")));''','''	ShowTagged(TEXT("Show_drawer"), Has(TEXT("phone_done")));
	ShowTagged(TEXT("Hide_drawer"), !Has(TEXT("phone_done")));
	for (TActorIterator<APostProcessVolume> It(GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(TEXT("PP_Dawn"))) It->bEnabled = Has(TEXT("dawn"));
	}''')
sub("WCStory.cpp",'#include "EngineUtils.h"','#include "EngineUtils.h"\n#include "Engine/PostProcessVolume.h"')
# flicker + light bar
sub("WCDirector.h",'''	void TickAudio(float Dt);''','''	void TickAudio(float Dt);
	void TickLights(float Dt);
	struct FLive { TWeakObjectPtr<class ULightComponent> Light; float Base = 0.f; float Seed = 0.f; int32 Kind = 0; };
	TArray<FLive> LiveLights;
	TArray<TWeakObjectPtr<AActor>> BarMeshes[2];''')
sub("WCDirector.cpp",'''	for (TActorIterator<AWCTrigger> It(GetWorld()); It; ++It) Triggers.Add(*It);''','''	for (TActorIterator<AWCTrigger> It(GetWorld()); It; ++It) Triggers.Add(*It);
	for (TActorIterator<AActor> It(GetWorld()); It; ++It)
	{
		const int32 Kind = It->ActorHasTag(TEXT("Flicker")) ? 0 : (It->ActorHasTag(TEXT("BarRed")) ? 1 : (It->ActorHasTag(TEXT("BarBlue")) ? 2 : -1));
		if (It->ActorHasTag(TEXT("BarRedMesh"))) BarMeshes[0].Add(*It);
		if (It->ActorHasTag(TEXT("BarBlueMesh"))) BarMeshes[1].Add(*It);
		if (Kind < 0) continue;
		TArray<ULightComponent*> Ls;
		It->GetComponents(Ls);
		for (ULightComponent* L : Ls) { FLive X; X.Light = L; X.Base = L->Intensity; X.Seed = Rng.FRandRange(0.f, 100.f); X.Kind = Kind; LiveLights.Add(X); }
	}''')
sub("WCDirector.cpp",'''	TickAudio(Dt);
}''','''	TickAudio(Dt);
	TickLights(Dt);
}

void AWCDirector::TickLights(float Dt)
{
	const float T = (float)Clock;
	// light bar: red and blue trade double flashes
	const float Ph = FMath::Fmod(T, 0.9f);
	const bool bRed = Ph < 0.09f || (Ph > 0.16f && Ph < 0.25f);
	const bool bBlue = (Ph > 0.45f && Ph < 0.54f) || (Ph > 0.61f && Ph < 0.70f);
	for (FLive& L : LiveLights)
	{
		ULightComponent* C = L.Light.Get();
		if (!C || !C->IsVisible()) continue;
		if (L.Kind == 0)
		{
			const float N = 0.82f + 0.12f * FMath::Sin(T * 9.1f + L.Seed) + 0.06f * FMath::Sin(T * 23.7f + L.Seed * 2.f) + (FMath::Sin(T * 1.3f + L.Seed) > 0.96f ? -0.25f : 0.f);
			C->SetIntensity(L.Base * N);
		}
		else C->SetIntensity((L.Kind == 1 ? bRed : bBlue) ? L.Base : L.Base * 0.02f);
	}
	for (int32 k = 0; k < 2; ++k) for (TWeakObjectPtr<AActor>& A : BarMeshes[k])
	{
		if (A.IsValid() && !Has(TEXT("dawn"))) A->SetActorHiddenInGame(!(k == 0 ? bRed : bBlue));
	}
}''')
print("ok")
