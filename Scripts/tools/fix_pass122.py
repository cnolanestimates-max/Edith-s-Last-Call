# Pass 122: the opening shot from the air was black (photo check air1: nothing but a speck of headlight).  While the
# camera is high the moon and the sky are let in; they are back to the game's own night before it is down in the trees.
#   -WCAirMoon=<x>  -WCAirSky=<x> : how many times brighter than the game's night (to try values without a rebuild)
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

S = r"C:\GameDev\Unreal\WellnessCheck\Source\WellnessCheck"

edit(S + r"\WCDirector.h", [
    ("""	float AirT = 0.f, CabinFov = 66.f;
""",
     """	float AirT = 0.f, CabinFov = 66.f;
	TWeakObjectPtr<class ADirectionalLight> AirMoon;
	TWeakObjectPtr<class ASkyLight> AirSky;
	float AirMoonBase = 0.f, AirSkyBase = 0.f;
"""),
])

edit(S + r"\WCHouse.cpp", [
    ("""static const float GAirDur = 18.f;            // how long the camera is outside the car at the start of the drive

void AWCDirector::AirIntoCar()
{
""",
     """static const float GAirDur = 18.f;            // how long the camera is outside the car at the start of the drive
static float GAirMoon = 10.f, GAirSky = 5.f;  // the moon and the sky, while the camera is high: times the game's own night

void AWCDirector::AirIntoCar()
{
	if (AirMoon.IsValid()) AirMoon->GetLightComponent()->SetIntensity(AirMoonBase);
	if (AirSky.IsValid()) AirSky->GetLightComponent()->SetIntensity(AirSkyBase);
"""),
    ("""		SetLoop(TEXT("amb"), TEXT("amb_night"), 0.5f, 1.5f);        // out here the night is all there is to hear
""",
     """		SetLoop(TEXT("amb"), TEXT("amb_night"), 0.5f, 1.5f);        // out here the night is all there is to hear
		FParse::Value(FCommandLine::Get(), TEXT("WCAirMoon="), GAirMoon);
		FParse::Value(FCommandLine::Get(), TEXT("WCAirSky="), GAirSky);
		AirMoon = nullptr; AirSky = nullptr;
		for (TActorIterator<ADirectionalLight> It(GetWorld()); It; ++It) if (It->ActorHasTag(TEXT("Hide_dawn"))) { AirMoon = *It; AirMoonBase = It->GetLightComponent()->Intensity; }
		for (TActorIterator<ASkyLight> It(GetWorld()); It; ++It) { AirSky = *It; AirSkyBase = It->GetLightComponent()->Intensity; }
		UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE from the air: moon %.1f x%.1f, sky %.2f x%.1f"), AirMoonBase, GAirMoon, AirSkyBase, GAirSky);
"""),
    ("""			DriveCam->GetCameraComponent()->SetFieldOfView(FMath::Lerp(46.f, CabinFov, AirS));
""",
     """			DriveCam->GetCameraComponent()->SetFieldOfView(FMath::Lerp(46.f, CabinFov, AirS));
			// from up here there is only the moon to see by: it is let in while the camera is high, and gone again by the time it is in the trees
			const float Night = FMath::SmoothStep(0.f, 1.f, (AirS - 0.2f) / 0.5f);
			if (AirMoon.IsValid()) AirMoon->GetLightComponent()->SetIntensity(AirMoonBase * FMath::Lerp(GAirMoon, 1.f, Night));
			if (AirSky.IsValid()) AirSky->GetLightComponent()->SetIntensity(AirSkyBase * FMath::Lerp(GAirSky, 1.f, Night));
"""),
])

# includes
p = S + r"\WCHouse.cpp"
s = open(p, encoding="utf-8", newline="").read()
if "Engine/DirectionalLight.h" not in s:
    i = s.index("#include")
    j = s.index("\n", s.rindex("#include", 0, s.index("DEFINE_LOG_CATEGORY") if "DEFINE_LOG_CATEGORY" in s else len(s)))
    add = '\n#include "Engine/DirectionalLight.h"\n#include "Engine/SkyLight.h"\n#include "Components/LightComponent.h"\n#include "Components/SkyLightComponent.h"\n#include "EngineUtils.h"'
    s = s[:j] + add.replace("\n", "\r\n" if "\r\n" in s else "\n") + s[j:]
    open(p, "w", encoding="utf-8", newline="").write(s)
print("pass 122 applied")
