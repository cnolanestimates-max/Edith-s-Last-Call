"""The flashlight beam converges on what he is looking at (it used to run parallel to the view from the hand, 30 cm low and
to the left, so anything examined up close sat in the dark above the lit patch: notes on desks, the eye behind the book)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCCharacter.h", [
    ('''	bool bLightOn = false;''', '''	bool bLightOn = false;
	float AimDist = 600.f;'''),
])
edit(R + "WCCharacter.cpp", [
    ('''	const FQuat Target = Cam->GetComponentQuat();
	AimQuat = FQuat::Slerp(AimQuat, Target, 1.f - FMath::Exp(-13.f * Dt)).GetNormalized();''',
     '''	{
		FHitResult FH;
		FCollisionQueryParams FQ(SCENE_QUERY_STAT(WCFlashAim), false, this);
		const FVector CS = Cam->GetComponentLocation();
		const float Want = GetWorld()->LineTraceSingleByChannel(FH, CS, CS + Cam->GetForwardVector() * 1200.f, ECC_Visibility, FQ) ? FMath::Max(FH.Distance, 100.f) : 1200.f;
		AimDist = FMath::FInterpTo(AimDist, Want, Dt, 7.f);
	}
	const FQuat Target = ((Cam->GetComponentLocation() + Cam->GetForwardVector() * AimDist) - Flash->GetComponentLocation()).ToOrientationQuat();
	AimQuat = FQuat::Slerp(AimQuat, Target, 1.f - FMath::Exp(-13.f * Dt)).GetNormalized();'''),
])
print("ok")
