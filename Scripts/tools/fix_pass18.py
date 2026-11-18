import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(L + "build_house.py", [
    ('''    bc.set_skeletal_mesh_asset(her_mesh)''', '''    bc.set_skeletal_mesh_asset(her_mesh)
    bc.set_editor_property("lighting_channels", LC_IN)'''),
])
edit(R + "WCEntity.cpp", [
    ('''	Body->SetAnimationMode(EAnimationMode::AnimationSingleNode);''', '''	Body->SetAnimationMode(EAnimationMode::AnimationSingleNode);
	Body->SetLightingChannels(true, true, false);'''),
    ('''		Iris->SetRelativeScale3D(FVector(R * 0.30f / 50.f, R * 0.40f / 50.f, R * 0.40f / 50.f));''', '''		Iris->SetRelativeScale3D(FVector(R * 0.30f / 50.f, R * 0.34f / 50.f, R * 0.34f / 50.f));'''),
    ('''		Pupil->SetRelativeScale3D(FVector(R * 0.14f / 50.f, R * 0.17f / 50.f, R * 0.17f / 50.f));''', '''		Pupil->SetRelativeScale3D(FVector(R * 0.14f / 50.f, R * 0.16f / 50.f, R * 0.16f / 50.f));'''),
])
print("ok")
