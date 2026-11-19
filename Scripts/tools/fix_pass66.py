"""The grab: he was looking up at the underside of her chin.  She comes down to him (her feet go through the floor, which the
close-up never shows) so her face is level with his and the open mouth fills the picture, and she is a little closer."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCHouse.cpp", [
    ('''	H->SetActorLocation(Feet + Dir * 118.f);
	H->SetYaw((-Dir).Rotation().Yaw);''', '''	H->SetActorLocation(Feet + Dir * 112.f - FVector(0, 0, GrabSink));
	H->SetYaw((-Dir).Rotation().Yaw);'''),
    ('''void AWCDirector::Grab(float Hold, TFunction<void()> Then)
{''', '''static float GrabSink = 58.f;       // how far she stoops to him (cm); -WCGrabSink=<n> to try others

void AWCDirector::Grab(float Hold, TFunction<void()> Then)
{
	FParse::Value(FCommandLine::Get(), TEXT("WCGrabSink="), GrabSink);'''),
])
print("ok")
