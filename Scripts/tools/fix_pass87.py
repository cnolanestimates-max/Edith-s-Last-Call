"""Pass 87: in the blackout her eye was a single pixel.  It is shown larger (the whole eye swells while only it can be seen),
brighter, and from 6 m at most."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Source/WellnessCheck/WCEntity.h", [
    ('void SetEyeShine(float Glow);', 'void SetEyeShine(float Glow, float Swell = 1.f);'),
])
edit(R + "Source/WellnessCheck/WCEntity.cpp", [
    ('''void AWCEntity::SetEyeShine(float Glow)
{''', '''void AWCEntity::SetEyeShine(float Glow, float Swell)
{
	Eye->SetRelativeScale3D(FVector(Swell));'''),
    ('''if (IrisMID) IrisMID->SetScalarParameterValue(TEXT("Glow"), 0.06f);''',
     '''if (IrisMID) IrisMID->SetScalarParameterValue(TEXT("Glow"), 0.06f);
	Eye->SetRelativeScale3D(FVector(1.f));'''),
])
edit(R + "Source/WellnessCheck/WCEvents.cpp", [
    ('Fwd * FMath::Clamp(Free - 80.f, 300.f, 800.f);', 'Fwd * FMath::Clamp(Free - 80.f, 300.f, 600.f);'),
    ('''H->SetGlow(bDark ? 55.f : 2.5f);
		H->SetEyeShine(bDark ? 2600.f : 120.f);''', '''H->SetGlow(bDark ? 55.f : 2.5f);
		H->SetEyeShine(bDark ? 5200.f : 300.f, 2.3f);'''),
    ('H->SetEyeShine(120.f * FMath::Clamp(1.f - T / 0.3f, 0.f, 1.f));', 'H->SetEyeShine(300.f * FMath::Clamp(1.f - T / 0.3f, 0.f, 1.f), 2.3f);'),
])
print("pass 87 applied")
