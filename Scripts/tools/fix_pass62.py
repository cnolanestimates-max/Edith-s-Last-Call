"""In a grab her face is closer than the flashlight in his outstretched hand, so the beam lit her nightgown and left the
face black.  While she has him, a light at his own eye (the torch flaring back off her) lights the face, stuttering with
the torch."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCCharacter.h", [
    ('''	void SetAiming(bool bAim) { bAiming = bAim; }''', '''	void SetAiming(bool bAim) { bAiming = bAim; }
	/** Light at his own eye, for when something is closer than the torch in his hand. Lumens; 0 = off. */
	void SetFaceLight(float Lumens) { FaceLumens = Lumens; }'''),
    ('''	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> Fill;''', '''	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> Fill;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> FaceLight;'''),
    ('''	float AimDist = 600.f;''', '''	float AimDist = 600.f;
	float FaceLumens = 0.f;'''),
])
edit(R + "WCCharacter.cpp", [
    ('''	Fill = CreateDefaultSubobject<UPointLightComponent>(TEXT("Fill"));''', '''	FaceLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("FaceLight"));
	FaceLight->SetupAttachment(Cam);
	FaceLight->SetRelativeLocation(FVector(4.f, -6.f, -4.f));
	FaceLight->SetIntensityUnits(ELightUnits::Lumens);
	FaceLight->SetIntensity(0.f);
	FaceLight->SetAttenuationRadius(260.f);
	FaceLight->SetLightColor(FLinearColor(1.f, 0.9f, 0.76f));
	FaceLight->SetCastShadows(false);
	FaceLight->SetVolumetricScatteringIntensity(0.f);

	Fill = CreateDefaultSubobject<UPointLightComponent>(TEXT("Fill"));'''),
    ('''	Spill->SetIntensity(FlashLumens * 0.11f * Level);''', '''	Spill->SetIntensity(FlashLumens * 0.11f * Level);
	FaceLight->SetIntensity(FaceLumens * FMath::Clamp(Level, 0.25f, 1.f));'''),
])
edit(R + "WCHouse.cpp", [
    ('''	P->SetLightScale(1.f);
	P->FlickerLight(Hold, 0.45f);
	P->SetInputLocked(true);
	GrabHoldUntil = Clock + Hold;''', '''	P->SetLightScale(1.f);
	P->FlickerLight(Hold, 0.45f);
	P->SetFaceLight(260.f);
	P->SetInputLocked(true);
	GrabHoldUntil = Clock + Hold;'''),
    ('''		const int32 N = !Has(TEXT("mem1")) ? 1 : (!Has(TEXT("mem2")) ? 2 : (!Has(TEXT("mem3")) ? 3 : 0));
		if (N > 0 && !Has(TEXT("placed"))''', '''		const int32 N = !Has(TEXT("mem1")) ? 1 : (!Has(TEXT("mem2")) ? 2 : (!Has(TEXT("mem3")) ? 3 : 0));
		if (AWCCharacter* Pl0 = Player()) Pl0->SetFaceLight(0.f);
		if (N > 0 && !Has(TEXT("placed"))'''),
])
print("ok")
