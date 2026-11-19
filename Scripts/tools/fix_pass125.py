# Pass 125: the opening shot, fourth look.  The forest is only planted along the road, so from the air it was a hedge
# of trees across a bare field.  While the camera is in the air a wood is stood either side of it (instanced copies of
# the road's own pines, no shadows, no collision); it is taken away again as the camera enters the car.
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

S = r"C:\GameDev\Unreal\WellnessCheck\Source\WellnessCheck"

edit(S + r"\WCDirector.h", [
    ("""	TArray<TPair<TWeakObjectPtr<class UStaticMeshComponent>, float>> AirTrees;
""",
     """	TArray<TPair<TWeakObjectPtr<class UStaticMeshComponent>, float>> AirTrees;
	TWeakObjectPtr<AActor> AirWood;
"""),
])

edit(S + r"\WCHouse.cpp", [
    ("""static float GAirHi = 14000.f, GAirLo = 8000.f, GAirFov = 26.f, GAirHead = 6.f;
""",
     """static float GAirHi = 12000.f, GAirLo = 7000.f, GAirFov = 28.f, GAirHead = 6.f;
"""),
    ("""	for (const auto& T : AirTrees) if (T.Key.IsValid()) T.Key->SetCullDistance(T.Value);
	AirTrees.Reset();
""",
     """	for (const auto& T : AirTrees) if (T.Key.IsValid()) T.Key->SetCullDistance(T.Value);
	AirTrees.Reset();
	if (AirWood.IsValid()) AirWood->Destroy();
"""),
    ("""		UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE from the air: %d trees drawn at any distance"), AirTrees.Num());
""",
     """		UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE from the air: %d trees drawn at any distance"), AirTrees.Num());
		// a road through a wood, not a hedge across a field: from the air the forest has to go on to the edge of the picture
		{
			TArray<UStaticMesh*> Kinds;
			float TreeZ = -44.f;
			for (const auto& T : AirTrees)
			{
				UStaticMesh* M = T.Key.IsValid() ? T.Key->GetStaticMesh() : nullptr;
				if (!M || !M->GetName().Contains(TEXT("Pine")) || M->GetName().Contains(TEXT("Sapling")) || Kinds.Contains(M)) continue;
				if (Kinds.Num() == 0) TreeZ = T.Key->GetComponentLocation().Z;
				Kinds.Add(M);
				if (Kinds.Num() >= 4) break;
			}
			AActor* Wood = Kinds.Num() > 0 ? GetWorld()->SpawnActor<AActor>(AActor::StaticClass(), FTransform::Identity) : nullptr;
			if (Wood)
			{
				USceneComponent* Root = NewObject<USceneComponent>(Wood);
				Wood->SetRootComponent(Root);
				Root->RegisterComponent();
				TArray<UInstancedStaticMeshComponent*> Ism;
				for (UStaticMesh* M : Kinds)
				{
					UInstancedStaticMeshComponent* C = NewObject<UInstancedStaticMeshComponent>(Wood);
					C->SetStaticMesh(M);
					C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
					C->SetCastShadow(false);
					C->SetupAttachment(Root);
					C->RegisterComponent();
					Ism.Add(C);
				}
				FRandomStream Rs(7741);
				const FVector Gate = PathPoint(DrivePts, DriveLen, DriveTotal);
				int32 N = 0;
				for (int32 i = 0; i < 5000 && N < 2200; ++i)
				{
					const float D = Rs.FRandRange(-10000.f, 21000.f);
					const float Dc = FMath::Clamp(D, 0.f, DriveTotal);
					const FVector Dir = (PathPoint(DrivePts, DriveLen, FMath::Min(Dc + 300.f, DriveTotal)) - PathPoint(DrivePts, DriveLen, FMath::Max(Dc - 300.f, 0.f))).GetSafeNormal2D();
					FVector Q = PathPoint(DrivePts, DriveLen, Dc) + Dir * (D - Dc);
					Q += FVector(-Dir.Y, Dir.X, 0.f) * Rs.FRandRange(1500.f, 17000.f) * (Rs.FRand() < 0.5f ? -1.f : 1.f);
					if (FVector::Dist2D(Q, Gate) < 9000.f) continue;                    // not in her yard
					bool bOnRoad = false;
					for (float D0 = 0.f; D0 <= DriveTotal && !bOnRoad; D0 += 500.f) bOnRoad = FVector::Dist2D(PathPoint(DrivePts, DriveLen, D0), Q) < 1400.f;
					if (bOnRoad) continue;
					const float Sc = Rs.FRandRange(0.9f, 1.3f);
					Ism[Rs.RandRange(0, Ism.Num() - 1)]->AddInstance(FTransform(FRotator(0.f, Rs.FRandRange(0.f, 360.f), 0.f), FVector(Q.X, Q.Y, TreeZ), FVector(Sc, Sc, Sc * Rs.FRandRange(0.92f, 1.1f))), true);
					++N;
				}
				AirWood = Wood;
				UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE from the air: a wood of %d more trees either side of the road (%d kinds)"), N, Kinds.Num());
			}
		}
"""),
])

p = S + r"\WCHouse.cpp"
s = open(p, encoding="utf-8", newline="").read()
if '"Components/InstancedStaticMeshComponent.h"' not in s:
    nl = "\r\n" if "\r\n" in s else "\n"
    s = s.replace('#include "Engine/Light.h"', '#include "Components/InstancedStaticMeshComponent.h"' + nl + '#include "Engine/Light.h"', 1)
    open(p, "w", encoding="utf-8", newline="").write(s)
print("pass 125 applied")
