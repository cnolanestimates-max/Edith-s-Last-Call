"""Pass 112: seeing further (Cheyenne 2026-11-19 16:47 UTC: "It's getting harder and harder for me to see stuff ... It's harder
to see her when she's super far away ... Maybe we need to tone up the flashlight even more on distance.  Width wise, I think
we're fine").
  - the flashlight gets a tight centre beam (the throw of a real torch): about a quarter of the light in an 11 degree cone
    that carries to 10 m, so the middle of the picture reaches roughly twice as far; the wide beam is unchanged in width and
    brightness and reaches a little further (6.4 m, was 5.1)
  - Edith's cold glow grows with distance: the same as before out to 6 m, then up to 2.6 times as strong at 15 m"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Source/WellnessCheck/WCCharacter.cpp", [
    ('''	Flash->SetAttenuationRadius(510.f);             // 30% longer''', '''	Flash->SetAttenuationRadius(640.f);             // longer again (was 510, before that 390)'''),
    ('''	GunPivot = CreateDefaultSubobject<USceneComponent>(TEXT("GunPivot"));''', '''	// the throw: a tight, far-reaching centre to the beam, so the middle of what he looks at carries about twice as far
	Throw = CreateDefaultSubobject<USpotLightComponent>(TEXT("Throw"));
	Throw->SetupAttachment(Flash);
	Throw->SetIntensityUnits(ELightUnits::Lumens);
	Throw->SetIntensity(0.f);
	Throw->SetInnerConeAngle(4.f);
	Throw->SetOuterConeAngle(11.f);
	Throw->SetAttenuationRadius(1000.f);
	Throw->SetLightColor(FLinearColor(1.f, 0.92f, 0.80f));
	Throw->SetSourceRadius(1.f);
	Throw->SetCastShadows(true);
	Throw->SetVolumetricScatteringIntensity(1.2f);

	GunPivot = CreateDefaultSubobject<USceneComponent>(TEXT("GunPivot"));'''),
    ('''	Spill->SetIntensity(FlashLumens * 0.11f * Level);''', '''	Spill->SetIntensity(FlashLumens * 0.11f * Level);
	Throw->SetIntensity(FlashLumens * 0.24f * Level);'''),
])
edit(R + "Source/WellnessCheck/WCEntity.cpp", [
    ('''	FarLight->SetAttenuationRadius(460.f);''', '''	FarLight->SetAttenuationRadius(560.f);'''),
    ('''	FarLight->SetIntensity(FarGlow * FMath::Clamp((DistToPlayer() - 230.f) / 260.f, 0.f, 1.f));''',
     '''	FarLight->SetIntensity(FarGlow * FMath::Clamp((DistToPlayer() - 230.f) / 260.f, 0.f, 1.f) * (1.f + 1.6f * FMath::Clamp((DistToPlayer() - 600.f) / 900.f, 0.f, 1.f)));       // further off, she has to be brighter to be seen at all'''),
])
import re
p = R + "Source/WellnessCheck/WCCharacter.h"
s = open(p, encoding="utf-8").read()
m = re.search(r"\n(\s*UPROPERTY\([^\n]*\)\s*TObjectPtr<USpotLightComponent> Spill;)", s) or re.search(r"\n([^\n]*Spill;)", s)
line = m.group(1)
s = s.replace(line, line + "\n" + line.replace("Spill", "Throw"), 1)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("pass 112 applied:", line.strip())
