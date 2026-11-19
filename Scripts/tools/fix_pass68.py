"""1. Bot diagnostics: when it cannot get somewhere, sweep its own capsule forward and name what it hits (and where).
   -WCHerLook -WCStairOnly walks the cellar stairs from the bottom, which no run has ever done on foot.
2. Bot routing: the 'close enough, walk straight at it' shortcut only when nothing is between him and the thing (it walked
   into the wall beside the attic and cellar doors)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCAuto.cpp", [
    ('''						const bool bHit = GetWorld()->SweepSingleByChannel(Hit, From, From + Dir * 90.f, FQuat::Identity, ECC_Pawn, FCollisionShape::MakeSphere(22.f), Q);
						UE_LOG(LogWCAuto, Error, TEXT("WCAUTO WHY %s: walking into %s (%s) %.0f cm ahead, at (%.0f,%.0f,%.0f) heading (%.2f,%.2f)"), *S.Arg.ToString(),
							bHit && Hit.GetActor() ? *Hit.GetActor()->GetActorNameOrLabel() : TEXT("nothing found"), bHit && Hit.GetComponent() ? *Hit.GetComponent()->GetName() : TEXT("-"), bHit ? Hit.Distance : -1.f, Loc.X, Loc.Y, Loc.Z, Dir.X, Dir.Y);''',
     '''						(void)From;
						// his own capsule, lifted a hand's breadth so the floor he stands on does not count, pushed the way he is trying to go
						const FCollisionShape Cap = FCollisionShape::MakeCapsule(P->GetCapsuleComponent()->GetScaledCapsuleRadius() - 1.f, P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() - 12.f);
						const FVector Up0 = Loc + FVector(0, 0, 14.f);
						const bool bHit = GetWorld()->SweepSingleByChannel(Hit, Up0, Up0 + Dir * 60.f + FVector(0, 0, 50.f), FQuat::Identity, ECC_Pawn, Cap, Q);
						UE_LOG(LogWCAuto, Error, TEXT("WCAUTO WHY %s: walking into %s (%s) %.0f cm ahead, touching at (%.0f,%.0f,%.0f)%s; he is at (%.0f,%.0f,%.0f) heading (%.2f,%.2f)"), *S.Arg.ToString(),
							bHit && Hit.GetActor() ? *Hit.GetActor()->GetActorNameOrLabel() : TEXT("nothing found"), bHit && Hit.GetComponent() ? *Hit.GetComponent()->GetName() : TEXT("-"), bHit ? Hit.Distance : -1.f,
							Hit.ImpactPoint.X, Hit.ImpactPoint.Y, Hit.ImpactPoint.Z, bHit && Hit.bStartPenetrating ? TEXT(" (already inside it)") : TEXT(""), Loc.X, Loc.Y, Loc.Z, Dir.X, Dir.Y);'''),
    ('''		if (FParse::Param(FCommandLine::Get(), TEXT("WCGrabOnly")))
		{''', '''		if (FParse::Param(FCommandLine::Get(), TEXT("WCStairOnly")))
		{
			bForce = true;
			if (AWCDoor* Cd = Door(TEXT("cellar"))) { Cd->SetLocked(false); Cd->SetOpen(true, 0.1f, true); }
			AutoSteps.Add({ A_Tele, TEXT("N_c_bot"), 0.f }); Wait(1.5f); Shot(TEXT("stairs_cellar_foot"));
			AutoSteps.Add({ A_Go, TEXT("A_Foyer"), 0.f }); Shot(TEXT("stairs_after"));
			AutoSteps.Add({ A_Tele, TEXT("N_stairs_g"), 0.f }); Wait(1.f); AutoSteps.Add({ A_Go, TEXT("N_up_land"), 0.f }); Shot(TEXT("stairs_up_land"));
			AutoSteps.Add({ A_Go, TEXT("N_c_bot"), 0.f }); Shot(TEXT("stairs_down_to_cellar")); Wait(1.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCGrabOnly")))
		{'''),
    ('''	if (A == INDEX_NONE || B == INDEX_NONE || (FVector::Dist2D(Feet, Goal) < 260.f && FMath::Abs(Feet.Z - Goal.Z) < 130.f)) { Out.Add(Goal); return; }''',
     '''	bool bDirect = FVector::Dist2D(Feet, Goal) < 260.f && FMath::Abs(Feet.Z - Goal.Z) < 130.f;
	if (bDirect)
	{
		// only if nothing stands between him and it
		FHitResult Hit;
		FCollisionQueryParams Q(SCENE_QUERY_STAT(WCAutoDirect), false, Player());
		const FVector To(Goal.X, Goal.Y, FMath::Max(Goal.Z, Feet.Z + 60.f));
		if (GetWorld()->LineTraceSingleByChannel(Hit, From, To, ECC_Visibility, Q) && Hit.Distance < FVector::Dist(From, To) - 45.f) bDirect = false;
	}
	if (A == INDEX_NONE || B == INDEX_NONE || bDirect) { Out.Add(Goal); return; }'''),
])
print("ok")
