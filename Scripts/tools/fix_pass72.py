"""Stair photographs also say what he is looking at and what is straight above him (which actor, how far)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCAuto.cpp", [
    ('''				if (AController* C = P->GetController()) C->SetControlRotation(FRotator(FCString::Atof(*V[4]), FCString::Atof(*V[3]), 0.f));
				P->SetFlashlight(true, false);''', '''				if (AController* C = P->GetController()) C->SetControlRotation(FRotator(FCString::Atof(*V[4]), FCString::Atof(*V[3]), 0.f));
				P->SetFlashlight(true, false);
				{
					// anything, whether or not it has collision: trace against the visible meshes themselves
					const FVector Eye(FCString::Atof(*V[0]), FCString::Atof(*V[1]), FCString::Atof(*V[2]) + 66.f);
					const FVector Fwd = FRotator(FCString::Atof(*V[4]), FCString::Atof(*V[3]), 0.f).Vector();
					auto What = [this, &Eye](const FVector& Dir, float Len) -> FString
					{
						FString Out; float Best = Len;
						for (TActorIterator<AActor> It(GetWorld()); It; ++It)
						{
							if (It->IsHidden()) continue;
							TArray<UStaticMeshComponent*> Comps; It->GetComponents(Comps);
							for (UStaticMeshComponent* C2 : Comps)
							{
								if (!C2->IsVisible() || !C2->GetStaticMesh()) continue;
								const FBox B = C2->Bounds.GetBox();
								FVector HitLoc, HitNorm; float HitT;
								if (FMath::LineExtentBoxIntersection(B, Eye, Eye + Dir * Len, FVector::ZeroVector, HitLoc, HitNorm, HitT) && HitT * Len < Best && HitT > 0.001f)
								{
									// bounds of a tilted board are loose: only believe thin or small things
									if (B.GetExtent().GetMin() < 30.f) { Best = HitT * Len; Out = FString::Printf(TEXT("%s at %.0f cm"), *It->GetActorNameOrLabel(), Best); }
								}
							}
						}
						return Out.IsEmpty() ? FString(TEXT("nothing")) : Out;
					};
					UE_LOG(LogWCAuto, Display, TEXT("WCVIEW %s: ahead = %s; straight up = %s"), *S.Arg.ToString(), *What(Fwd, 900.f), *What(FVector(0, 0, 1), 900.f));
				}'''),
])
print("ok")
