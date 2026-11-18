"""Bot: only shoot at her when she is actually in view (it was emptying the magazine into walls)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCAuto.cpp", [
    ('''else if (P->IsGunUp() && Clock > NextShot && StalkState == 2) { NextShot = Clock + 0.65; P->DoFire(); }''',
     '''else if (P->IsGunUp() && Clock > NextShot && StalkState == 2 && PlayerSees(Her()->HeadLocation() - FVector(0, 0, 60), 0.95f, 2200.f)) { NextShot = Clock + 0.6; P->DoFire(); }'''),
])
print("ok")
