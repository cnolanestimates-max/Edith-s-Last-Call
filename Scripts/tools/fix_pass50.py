"""Bot: when it cannot focus something, say what is in the way."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCAuto.cpp", [
    ('''			UE_LOG(LogWCAuto, Error, TEXT("WCAUTO FAIL could not focus %s (dist %.0f, enabled %d)%s"), *S.Arg.ToString(), FVector::Dist(P->EyeLocation(), Origin), T->CanInteract() ? 1 : 0, bForce ? TEXT(" -> forced") : TEXT(""));''',
     '''			{
				FHitResult Hit;
				FCollisionQueryParams Q(SCENE_QUERY_STAT(WCAutoWhy), false, P);
				const FVector Eye = P->EyeLocation();
				const bool bHit = GetWorld()->LineTraceSingleByChannel(Hit, Eye, Eye + (Origin - Eye).GetSafeNormal() * 400.f, ECC_Visibility, Q);
				UE_LOG(LogWCAuto, Error, TEXT("WCAUTO WHY %s: in the way = %s (%s) at %.0f cm; target at (%.0f,%.0f,%.0f) half (%.0f,%.0f,%.0f); eye (%.0f,%.0f,%.0f)"), *S.Arg.ToString(),
					bHit && Hit.GetActor() ? *Hit.GetActor()->GetActorNameOrLabel() : TEXT("nothing"), bHit && Hit.GetComponent() ? *Hit.GetComponent()->GetName() : TEXT("-"), bHit ? Hit.Distance : -1.f,
					Origin.X, Origin.Y, Origin.Z, Ext.X, Ext.Y, Ext.Z, Eye.X, Eye.Y, Eye.Z);
			}
			UE_LOG(LogWCAuto, Error, TEXT("WCAUTO FAIL could not focus %s (dist %.0f, enabled %d)%s"), *S.Arg.ToString(), FVector::Dist(P->EyeLocation(), Origin), T->CanInteract() ? 1 : 0, bForce ? TEXT(" -> forced") : TEXT(""));'''),
])
print("ok")
