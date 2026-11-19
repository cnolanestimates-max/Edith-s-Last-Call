# Pass 123: the opening shot, second look (photo check air1 with the moon in: a thicket of branches filling the picture,
# the car a speck under it).  Higher and on a longer lens, so the forest is a texture and the road a seam in it, and his
# headlights are turned up while the camera is high so the light he pushes down the road is what the eye follows.
#   -WCAirHi= -WCAirLo= (cm above the car at the start and before the descent)  -WCAirFov=  -WCAirHead= (headlights, times)
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

S = r"C:\GameDev\Unreal\WellnessCheck\Source\WellnessCheck"

edit(S + r"\WCDirector.h", [
    ("""	float AirMoonBase = 0.f, AirSkyBase = 0.f;
""",
     """	float AirMoonBase = 0.f, AirSkyBase = 0.f;
	TArray<TPair<TWeakObjectPtr<class ULightComponent>, float>> AirHeads;
"""),
])

edit(S + r"\WCHouse.cpp", [
    ("""static float GAirMoon = 10.f, GAirSky = 5.f;  // the moon and the sky, while the camera is high: times the game's own night

void AWCDirector::AirIntoCar()
{
""",
     """static float GAirMoon = 10.f, GAirSky = 5.f;  // the moon and the sky, while the camera is high: times the game's own night
static float GAirHi = 11000.f, GAirLo = 6500.f, GAirFov = 30.f, GAirHead = 3.f;

void AWCDirector::AirIntoCar()
{
	for (const auto& H : AirHeads) if (H.Key.IsValid()) H.Key->SetIntensity(H.Value);
"""),
    ("""		AirMoon = nullptr; AirSky = nullptr;
""",
     """		FParse::Value(FCommandLine::Get(), TEXT("WCAirHi="), GAirHi);
		FParse::Value(FCommandLine::Get(), TEXT("WCAirLo="), GAirLo);
		FParse::Value(FCommandLine::Get(), TEXT("WCAirFov="), GAirFov);
		FParse::Value(FCommandLine::Get(), TEXT("WCAirHead="), GAirHead);
		AirHeads.Reset();
		for (TActorIterator<ALight> It(GetWorld()); It; ++It)
			if (It->ActorHasTag(TEXT("Headlight")) && It->GetLightComponent()) AirHeads.Add(TPair<TWeakObjectPtr<ULightComponent>, float>(It->GetLightComponent(), It->GetLightComponent()->Intensity));
		AirMoon = nullptr; AirSky = nullptr;
"""),
    ("""			const FVector High = CarPos + FRotator(0.f, Orbit, 0.f).Vector() * FMath::Lerp(700.f, 1900.f, Up) + FVector(0, 0, FMath::Lerp(5600.f, 3300.f, Up));
""",
     """			const FVector High = CarPos + FRotator(0.f, Orbit, 0.f).Vector() * FMath::Lerp(GAirHi * 0.12f, GAirLo * 0.5f, Up) + FVector(0, 0, FMath::Lerp(GAirHi, GAirLo, Up));
"""),
    ("""			DriveCam->GetCameraComponent()->SetFieldOfView(FMath::Lerp(46.f, CabinFov, AirS));
""",
     """			DriveCam->GetCameraComponent()->SetFieldOfView(FMath::Lerp(GAirFov, CabinFov, AirS));
"""),
    ("""			if (AirSky.IsValid()) AirSky->GetLightComponent()->SetIntensity(AirSkyBase * FMath::Lerp(GAirSky, 1.f, Night));
""",
     """			if (AirSky.IsValid()) AirSky->GetLightComponent()->SetIntensity(AirSkyBase * FMath::Lerp(GAirSky, 1.f, Night));
			for (const auto& H : AirHeads) if (H.Key.IsValid()) H.Key->SetIntensity(H.Value * FMath::Lerp(GAirHead, 1.f, Night));
"""),
])

p = S + r"\WCHouse.cpp"
s = open(p, encoding="utf-8", newline="").read()
if '"Engine/Light.h"' not in s:
    s = s.replace('#include "Engine/DirectionalLight.h"', '#include "Engine/Light.h"\r\n#include "Engine/DirectionalLight.h"' if "\r\n" in s else '#include "Engine/Light.h"\n#include "Engine/DirectionalLight.h"', 1)
    open(p, "w", encoding="utf-8", newline="").write(s)
print("pass 123 applied")
