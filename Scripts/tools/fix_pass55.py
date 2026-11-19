"""When she is close and in front of him the flashlight goes to her face, not her chest (the grab pictures were a lit
nightgown under a dark head)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCCharacter.cpp", [
    ('''		float Want = GetWorld()->LineTraceSingleByChannel(FH, CS, CS + CFwd * 1200.f, ECC_Visibility, FQ) ? FMath::Max(FH.Distance, 100.f) : 1200.f;
		if (AWCDirector* DD = AWCDirector::Get(this))
		{
			AWCEntity* E = DD->Her();
			if (E && E->IsShown())
			{
				const FVector Head = E->HeadLocation();
				const float T = FVector::DotProduct(Head - CS, CFwd);
				if (T > 30.f && T < Want && FVector::Dist(CS + CFwd * T, Head) < 95.f) Want = FMath::Max(T, 100.f);
			}
		}
		AimDist = FMath::FInterpTo(AimDist, Want, Dt, 7.f);
	}
	const FQuat Target = ((Cam->GetComponentLocation() + Cam->GetForwardVector() * AimDist) - Flash->GetComponentLocation()).ToOrientationQuat();''',
     '''		float Want = GetWorld()->LineTraceSingleByChannel(FH, CS, CS + CFwd * 1200.f, ECC_Visibility, FQ) ? FMath::Max(FH.Distance, 100.f) : 1200.f;
		float FaceWant = 0.f;
		if (AWCDirector* DD = AWCDirector::Get(this))
		{
			AWCEntity* E = DD->Her();
			if (E && E->IsShown())
			{
				const FVector Head = E->HeadLocation();
				const float T = FVector::DotProduct(Head - CS, CFwd);
				const float Off = FVector::Dist(CS + CFwd * T, Head);
				if (T > 30.f && T < Want && Off < 95.f) Want = FMath::Max(T, 100.f);
				// close and in front of him: the light finds her face
				if (T > 20.f && T < 330.f && Off < 0.75f * T + 40.f) { FaceWant = 1.f; FacePoint = Head + FVector(0, 0, -6.f); }
			}
		}
		AimDist = FMath::FInterpTo(AimDist, Want, Dt, 7.f);
		FaceAim = FMath::FInterpTo(FaceAim, FaceWant, Dt, 6.f);
	}
	const FVector AimPoint = FMath::Lerp(Cam->GetComponentLocation() + Cam->GetForwardVector() * AimDist, FacePoint, FaceAim * 0.9f);
	const FQuat Target = (AimPoint - Flash->GetComponentLocation()).ToOrientationQuat();'''),
])
edit(R + "WCCharacter.h", [
    ('''	float AimDist = 600.f;''', '''	float AimDist = 600.f;
	float FaceAim = 0.f;
	FVector FacePoint = FVector::ZeroVector;'''),
])
print("ok")
