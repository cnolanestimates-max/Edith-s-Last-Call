"""Bot can crouch (the step existed but did nothing, so the look test hung); the flashlight also converges on her when she is
in front of him (she has no collision for the aim trace, so her face stayed dark up close)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCAuto.cpp", [
    ('''	case A_Aim: P->SetAiming(S.F > 0.5f); Next(); return;''', '''	case A_Aim: P->SetAiming(S.F > 0.5f); Next(); return;
	case A_Crouch: if (S.F > 0.5f) P->Crouch(); else P->UnCrouch(); Next(); return;'''),
])
edit(R + "WCCharacter.cpp", [
    ('''		const float Want = GetWorld()->LineTraceSingleByChannel(FH, CS, CS + Cam->GetForwardVector() * 1200.f, ECC_Visibility, FQ) ? FMath::Max(FH.Distance, 100.f) : 1200.f;
		AimDist = FMath::FInterpTo(AimDist, Want, Dt, 7.f);''', '''		const FVector CFwd = Cam->GetForwardVector();
		float Want = GetWorld()->LineTraceSingleByChannel(FH, CS, CS + CFwd * 1200.f, ECC_Visibility, FQ) ? FMath::Max(FH.Distance, 100.f) : 1200.f;
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
		AimDist = FMath::FInterpTo(AimDist, Want, Dt, 7.f);'''),
])
print("ok")
