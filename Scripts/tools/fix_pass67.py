"""Grab framing can be tried from the command line (-WCGrabDist=, -WCGrabSink=), and -WCHerLook -WCGrabOnly photographs just
the grab."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCHouse.cpp", [
    ('''	H->SetActorLocation(Feet + Dir * 112.f - FVector(0, 0, GrabSink));''', '''	H->SetActorLocation(Feet + Dir * GrabDist - FVector(0, 0, GrabSink));'''),
    ('''static float GrabSink = 58.f;       // how far she stoops to him (cm); -WCGrabSink=<n> to try others''',
     '''static float GrabSink = 58.f;       // how far she stoops to him (cm); -WCGrabSink=<n> to try others
static float GrabDist = 112.f;      // how far her feet are from his; -WCGrabDist=<n>'''),
    ('''	FParse::Value(FCommandLine::Get(), TEXT("WCGrabSink="), GrabSink);''', '''	FParse::Value(FCommandLine::Get(), TEXT("WCGrabSink="), GrabSink);
	FParse::Value(FCommandLine::Get(), TEXT("WCGrabDist="), GrabDist);'''),
])
edit(R + "WCAuto.cpp", [
    ('''		if (FParse::Param(FCommandLine::Get(), TEXT("WCHerLook")))
		{
			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f });''', '''		if (FParse::Param(FCommandLine::Get(), TEXT("WCGrabOnly")))
		{
			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f }); Wait(1.0f); AutoSteps.Add({ A_Her, TEXT("Idle"), 400.f }); Wait(0.5f);
			AutoSteps.Add({ A_Do, TEXT("grab"), 0.f }); Wait(0.75f); Shot(TEXT("grab_face_1")); Wait(0.45f); Shot(TEXT("grab_face_2")); Wait(2.5f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCHerLook")))
		{
			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f });'''),
])
print("ok")
