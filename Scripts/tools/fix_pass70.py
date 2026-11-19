"""Bot, walking up to something to use it: the 'give up' clock now starts when he arrives (it was counting from the start of
the walk, so a long walk gave up the moment it arrived), and if the thing is hidden from where he stands he steps round to a
side from which it can be seen, as a person would."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCAuto.cpp", [
    ('''			const bool bBlocked = GetWorld()->LineTraceSingleByChannel(Hit, Eye, Goal, ECC_Visibility, Q) && Hit.GetActor() != T && Hit.Distance < FVector::Dist(Eye, Goal) - 14.f;
			if (!bBlocked || D2 < 55.f || In > 22.0) { Next(); return; }''',
     '''			const bool bBlocked = GetWorld()->LineTraceSingleByChannel(Hit, Eye, Goal, ECC_Visibility, Q) && Hit.GetActor() != T && Hit.Distance < FVector::Dist(Eye, Goal) - 14.f;
			static int32 NearStep = -1, RoundStep = -1;
			static double NearAt = 0.0;
			if (NearStep != AutoIndex) { NearStep = AutoIndex; NearAt = Clock; }
			if (!bBlocked || D2 < 55.f || Clock - NearAt > 14.0) { Next(); return; }
			if (Clock - NearAt > 2.5 && RoundStep != AutoIndex)
			{
				// it is hidden from here: find a side it can be seen from, and go and stand there
				RoundStep = AutoIndex;
				Q.AddIgnoredActor(T);
				for (int32 k = 0; k < 16; ++k)
				{
					const FVector Side = FRotator(0.f, 45.f * (k % 8), 0.f).Vector() * (k < 8 ? 105.f : 150.f);
					const FVector Stand(Goal.X + Side.X, Goal.Y + Side.Y, Loc.Z);
					const FVector StandEye = Stand + FVector(0, 0, 66.f);
					FHitResult H2;
					if (GetWorld()->LineTraceSingleByChannel(H2, StandEye, Goal, ECC_Visibility, Q)) continue;                         // cannot see it from there
					if (GetWorld()->SweepSingleByChannel(H2, Loc, Stand, FQuat::Identity, ECC_Pawn, FCollisionShape::MakeSphere(26.f), Q)) continue;   // cannot walk straight there
					AutoPath.Reset(); AutoPath.Add(Stand - FVector(0, 0, 88.f)); AutoPathIndex = 0;
					UE_LOG(LogWCAuto, Display, TEXT("WCAUTO stepping round to see %s"), *S.Arg.ToString());
					break;
				}
			}'''),
])
print("ok")
