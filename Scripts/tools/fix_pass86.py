"""Pass 86: S14 is pitch black with only her eye.
  - the player's camera can be stopped down (the house still had moonlit arches and showed her outline)
  - her iris can glow (a parameter on its own material), and the little eye light shows a hint of the socket
  - she stands nearer (8 m at most) so the eye is more than a dot"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

edit(R + "Scripts/level/import_assets.py", [
    ('''flat_material("M_EyeIris", (0.30, 0.36, 0.40), 0.3, emissive=0.06)''',
     '''flat_material("M_EyeIris", (0.30, 0.36, 0.40), 0.3, emissive=0.06)
    # the same iris with its glow on a dial (the eye in the dark, S14)
    mg = new_material("M_EyeIrisGlow")
    cg = const3(mg, (0.30, 0.36, 0.40), -600, 0)
    mel.connect_material_property(cg, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(const1(mg, 0.3, -600, 200), "", unreal.MaterialProperty.MP_ROUGHNESS)
    gg = sparam(mg, "Glow", 0.06, -600, 400)
    mu = mel.create_material_expression(mg, unreal.MaterialExpressionMultiply, -300, 400)
    mel.connect_material_expressions(cg, "", mu, "A")
    mel.connect_material_expressions(gg, "", mu, "B")
    mel.connect_material_property(mu, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mg)
    eal.save_loaded_asset(mg, False)'''),
])

edit(R + "Source/WellnessCheck/WCEntity.h", [
    ('void SetGlow(float Lumens);', '''void SetGlow(float Lumens);
	/** How brightly her iris shines by itself (0.06 is the ordinary faint gleam). */
	void SetEyeShine(float Glow);
	UPROPERTY(Transient) TObjectPtr<class UMaterialInstanceDynamic> IrisMID;'''),
])
edit(R + "Source/WellnessCheck/WCEntity.cpp", [
    ('#include "Materials/MaterialInterface.h"', '#include "Materials/MaterialInterface.h"\n#include "Materials/MaterialInstanceDynamic.h"'),
    ('''void AWCEntity::SetGlow(float Lumens)
{
	EyeGlint->SetIntensity(Lumens);
}''', '''void AWCEntity::SetGlow(float Lumens)
{
	EyeGlint->SetIntensity(Lumens);
}

void AWCEntity::SetEyeShine(float Glow)
{
	if (!IrisMID)
	{
		UMaterialInterface* M = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_EyeIrisGlow.M_EyeIrisGlow"));
		if (!M || !Iris) return;
		IrisMID = UMaterialInstanceDynamic::Create(M, this);
		Iris->SetMaterial(0, IrisMID);
	}
	IrisMID->SetScalarParameterValue(TEXT("Glow"), Glow);
}'''),
    ('''EyeGlint->SetIntensity(0.f);
	ScreamTarget = ScreamAlpha = 0.f;''', '''EyeGlint->SetIntensity(0.f);
	if (IrisMID) IrisMID->SetScalarParameterValue(TEXT("Glow"), 0.06f);
	ScreamTarget = ScreamAlpha = 0.f;'''),
])

edit(R + "Source/WellnessCheck/WCCharacter.h", [
    ('void SetLightScale(float Scale) { LightScale = Scale; }', '''void SetLightScale(float Scale) { LightScale = Scale; }
	/** Stops the camera down by so many stops (0 = normal): real black, when the house lights are meant to be out. */
	void SetDarkAdapt(float Stops);'''),
])
p = R + "Source/WellnessCheck/WCCharacter.cpp"
s = open(p, encoding="utf-8").read()
assert "SetDarkAdapt" not in s
s += '''
void AWCCharacter::SetDarkAdapt(float Stops)
{
	const bool bOn = Stops > 0.01f;
	Cam->PostProcessSettings.bOverride_AutoExposureMethod = bOn;
	Cam->PostProcessSettings.AutoExposureMethod = EAutoExposureMethod::AEM_Manual;
	Cam->PostProcessSettings.bOverride_AutoExposureBias = bOn;
	Cam->PostProcessSettings.AutoExposureBias = -5.f - Stops;            // the night grade is -5 (lighting.py NIGHT_EV)
	Cam->PostProcessBlendWeight = bOn ? 1.f : 0.f;
}
'''
open(p, "w", encoding="utf-8", newline="\n").write(s)

edit(R + "Source/WellnessCheck/WCEvents.cpp", [
    ('Fwd * FMath::Clamp(Free - 80.f, 300.f, 1150.f);', 'Fwd * FMath::Clamp(Free - 80.f, 300.f, 800.f);'),
    ('''KillLights(45.f, false);
	P->SetLightScale(0.f);''', '''KillLights(45.f, false);
	P->SetLightScale(0.f);
	P->SetDarkAdapt(4.5f);                       // truly black: no moonlit doorway, no outline'''),
    ('''if (AWCCharacter* P = Player()) P->SetLightScale(1.f);
	SetLoop(TEXT("eye"), TEXT(""), 0.f, 3.f);''', '''if (AWCCharacter* P = Player()) { P->SetLightScale(1.f); P->SetDarkAdapt(0.f); }
	SetLoop(TEXT("eye"), TEXT(""), 0.f, 3.f);'''),
    ('''auto Show = [this, H, P]()
	{
		H->Appear(EyeSpot, (P->GetActorLocation() - EyeSpot).Rotation().Yaw, TEXT("Tall"));
		H->SetGlow(4.f);
	};''', '''// Dark = the camera is stopped down 4.5 stops, so everything of hers has to be about 22 times brighter to show the same
	auto Show = [this, H, P](bool bDark)
	{
		H->Appear(EyeSpot, (P->GetActorLocation() - EyeSpot).Rotation().Yaw, TEXT("Tall"));
		H->SetGlow(bDark ? 55.f : 2.5f);
		H->SetEyeShine(bDark ? 2600.f : 120.f);
	};'''),
    ('''Show();
			SetLoop(TEXT("eye"), TEXT("music_low"), 0.16f, 4.f, EWCSnd::Music);''', '''Show(true);
			SetLoop(TEXT("eye"), TEXT("music_low"), 0.16f, 4.f, EWCSnd::Music);'''),
    ('''if (T > 5.0f)
		{
			H->Vanish();                                           // gone in the same instant the light comes back''',
     '''if (T > 5.0f || FVector::Dist2D(P->GetActorLocation(), EyeSpot) < 380.f)
		{
			H->Vanish();                                           // gone in the same instant the light comes back
			P->SetDarkAdapt(0.f);'''),
    ('''Show();                                                // the light is off that spot: it is there again''',
     '''Show(false);                                           // the light is off that spot: it is there again'''),
    ('H->SetGlow(4.f * FMath::Clamp(1.f - T / 0.3f, 0.f, 1.f));', '''H->SetGlow(2.5f * FMath::Clamp(1.f - T / 0.3f, 0.f, 1.f));
		H->SetEyeShine(120.f * FMath::Clamp(1.f - T / 0.3f, 0.f, 1.f));'''),
])
print("pass 86 applied")
