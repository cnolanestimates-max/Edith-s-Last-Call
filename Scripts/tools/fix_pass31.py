"""Pistol view model (Cheyenne: 'the gun hand, arm ... looks kind of weird'): the forearm model is cut off behind the wrist and
its flat end was in view.  Bring it closer and turn it in, so the sleeve leaves by the bottom-right corner like an arm does."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCCharacter.cpp", [
    ('''	Gun->SetRelativeRotation(FRotator(0.f, 0.f, 0.f));
	Gun->SetRelativeLocation(FVector(4.f, 0.f, 0.f));''', '''	Gun->SetRelativeRotation(FRotator(2.5f, -7.5f, -4.f));
	Gun->SetRelativeLocation(FVector(4.f, 0.f, 0.f));'''),
    ('''	const FVector Low(40.f, 24.f, -60.f), High(52.f, 15.f, -19.f);''', '''	const FVector Low(30.f, 27.f, -62.f), High(39.f, 14.5f, -15.5f);'''),
])
print("ok")
