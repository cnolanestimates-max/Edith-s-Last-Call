# Pass 124: the opening shot, third look.  From 110 m and more the forest was not there (the trees are culled past
# 100 m for the game's sake: forest_meshes.py), so the cruiser drove over a bare field.  While the camera is in the air
# the trees are drawn at any distance; the limit is put back as it enters the car.  The high, long-lens framing is the
# default now (the car and the light it pushes ahead read from up there; at 55 m the picture was all branches).
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

S = r"C:\GameDev\Unreal\WellnessCheck\Source\WellnessCheck"

edit(S + r"\WCDirector.h", [
    ("""	TArray<TPair<TWeakObjectPtr<class ULightComponent>, float>> AirHeads;
""",
     """	TArray<TPair<TWeakObjectPtr<class ULightComponent>, float>> AirHeads;
	TArray<TPair<TWeakObjectPtr<class UStaticMeshComponent>, float>> AirTrees;
"""),
])

edit(S + r"\WCHouse.cpp", [
    ("""static float GAirMoon = 10.f, GAirSky = 5.f;  // the moon and the sky, while the camera is high: times the game's own night
static float GAirHi = 11000.f, GAirLo = 6500.f, GAirFov = 30.f, GAirHead = 3.f;
""",
     """static float GAirMoon = 7.f, GAirSky = 5.f;   // the moon and the sky, while the camera is high: times the game's own night
static float GAirHi = 14000.f, GAirLo = 8000.f, GAirFov = 26.f, GAirHead = 6.f;
"""),
    ("""	for (const auto& H : AirHeads) if (H.Key.IsValid()) H.Key->SetIntensity(H.Value);
""",
     """	for (const auto& H : AirHeads) if (H.Key.IsValid()) H.Key->SetIntensity(H.Value);
	for (const auto& T : AirTrees) if (T.Key.IsValid()) T.Key->SetCullDistance(T.Value);
	AirTrees.Reset();
"""),
    ("""		AirHeads.Reset();
""",
     """		// the forest is culled at 100 m for the game's sake; from the air it has to be there as far as the eye goes
		AirTrees.Reset();
		for (TActorIterator<AStaticMeshActor> It(GetWorld()); It; ++It)
		{
			UStaticMeshComponent* C = It->GetStaticMeshComponent();
			if (C && C->LDMaxDrawDistance >= 9000.f) { AirTrees.Add(TPair<TWeakObjectPtr<UStaticMeshComponent>, float>(C, C->LDMaxDrawDistance)); C->SetCullDistance(0.f); }
		}
		UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE from the air: %d trees drawn at any distance"), AirTrees.Num());
		AirHeads.Reset();
"""),
])

p = S + r"\WCHouse.cpp"
s = open(p, encoding="utf-8", newline="").read()
if '"Engine/StaticMeshActor.h"' not in s:
    nl = "\r\n" if "\r\n" in s else "\n"
    s = s.replace('#include "Engine/Light.h"', '#include "Engine/StaticMeshActor.h"' + nl + '#include "Engine/Light.h"', 1)
    open(p, "w", encoding="utf-8", newline="").write(s)
print("pass 124 applied")
