"""Cheyenne, 03:14 UTC:
 - a portrait hung in the kitchen doorway (it was placed at the middle of the wall piece that holds the door): moved to the
   plain wall beside it;
 - the cruiser from outside: the dash, door panels, pillars, roof liner and mirror that make up the driver's-seat view are
   separate boxes that stick out of the car body.  They are shown only while he is driving.
 - test: -WCHerLook -WCCarOnly photographs the car from four sides."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
P = "C:/GameDev/Unreal/WellnessCheck/"
R = P + "Source/WellnessCheck/"
edit(P + "Scripts/level/build_house.py", [
    ('''place("Portrait_Large", 1000, 181, GZ + 130, 180, D + "Hall", collide=False)''', '''place("Portrait_Large", 1400, 181, GZ + 130, 180, D + "Hall", collide=False)        # was at x 1000: the middle of the kitchen doorway'''),
])
edit(P + "Scripts/level/forest.py", [
    ('''    return cpart(box(name, CRX + f0, CRX + f1, CRY - l1, CRY - l0, -40 + u0, -40 + u1, mat, CAB, collide=False, shadow=False))''',
     '''    return cpart(box(name, CRX + f0, CRX + f1, CRY - l1, CRY - l0, -40 + u0, -40 + u1, mat, CAB, collide=False, shadow=False, tags=["CabinOnly"]))'''),
])
edit(R + "WCHouse.cpp", [
    ('''void AWCDirector::BeginDrive()
{''', '''void AWCDirector::BeginDrive()
{
	ShowTagged(TEXT("CabinOnly"), true);          // the inside of the car exists only while he is in it'''),
    ('''	if (!bDriving) return;
	bDriving = false;
	Set(TEXT("arrived"));''', '''	if (!bDriving) return;
	bDriving = false;
	Set(TEXT("arrived"));
	ShowTagged(TEXT("CabinOnly"), false);'''),
    ('''void AWCDirector::HouseBegin()
{''', '''void AWCDirector::HouseBegin()
{
	ShowTagged(TEXT("CabinOnly"), false);'''),
])
edit(R + "WCAuto.cpp", [
    ('''		if (FParse::Param(FCommandLine::Get(), TEXT("WCStairOnly")))
		{''', '''		if (FParse::Param(FCommandLine::Get(), TEXT("WCCarOnly")))
		{
			static const TCHAR* Views[][2] = {
				{ TEXT("at:-1180,60,52,141,-6"), TEXT("car_1_front_quarter") }, { TEXT("at:-1480,-60,52,90,-6"), TEXT("car_2_side") },
				{ TEXT("at:-1800,520,52,-35,-6"), TEXT("car_3_rear_quarter") }, { TEXT("at:-1250,560,110,-131,-14"), TEXT("car_4_high_quarter") },
				{ TEXT("at:-1130,300,52,180,-4"), TEXT("car_5_front") } };
			for (const auto& Vw : Views) { AutoSteps.Add({ A_Do, Vw[0], 0.f }); Wait(1.2f); Shot(Vw[1]); }
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCStairOnly")))
		{'''),
])
print("ok")
