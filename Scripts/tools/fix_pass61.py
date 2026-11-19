"""Bot: when walking up to something to use it, 'close enough' also means nothing is in the way (it used to stop on the
far side of a wall from the attic and cellar doors, or behind a desk from a note, and then fail to focus)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCAuto.cpp", [
    ('''		if (bToUse && FVector::Dist(P->EyeLocation(), Goal) < P->InteractRange - 45.f) { Next(); return; }''',
     '''		if (bToUse && FVector::Dist(P->EyeLocation(), Goal) < P->InteractRange - 45.f)
		{
			FHitResult Hit;
			FCollisionQueryParams Q(SCENE_QUERY_STAT(WCAutoSee), false, P);
			const FVector Eye = P->EyeLocation();
			const bool bBlocked = GetWorld()->LineTraceSingleByChannel(Hit, Eye, Goal, ECC_Visibility, Q) && Hit.GetActor() != T && Hit.Distance < FVector::Dist(Eye, Goal) - 14.f;
			if (!bBlocked || D2 < 55.f || In > 22.0) { Next(); return; }
		}'''),
])
print("ok")
