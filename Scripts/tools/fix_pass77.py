"""The thing on the road (Cheyenne 03:39 UTC: "a dark ass shadow figure on the road ... he could stop after passing, look
back, not see anything and then keep going", and "everything needs to be slow").
Half way down the forest road the Company stands at the edge of the dirt in the headlights.  It does nothing.  He drives
past it; it is gone the moment it leaves the light.  He lets the car roll to a stop, turns slowly in his seat and looks
back down the road: nothing.  He turns back and drives on.  The whole drive is slower too."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
P = "C:/GameDev/Unreal/WellnessCheck/"
R = P + "Source/WellnessCheck/"

edit(R + "WCDirector.h", [
    ('''	float DriveTotal = 0.f, DriveDist = 0.f, DriveSpeed = 0.f, DriveHeading = 0.f;''', '''	float DriveTotal = 0.f, DriveDist = 0.f, DriveSpeed = 0.f, DriveHeading = 0.f;
	float ShadowDist = -1.f, ShadowT = 0.f;       // the thing on the road: how far along it stands; time in the present phase
	int32 ShadowPhase = 0;                        // 0 not reached, 1 rolling to a stop, 2 stopped and looking back, 3 driving on'''),
])
edit(R + "WCHouse.cpp", [
    ('''	DriveTotal = Acc;
	DriveDist = 0.f;
	DriveSpeed = 800.f;''', '''	DriveTotal = Acc;
	DriveDist = 0.f;
	DriveSpeed = 620.f;
	ShadowDist = -1.f; ShadowPhase = 0; ShadowT = 0.f;
	if (AActor* Sh = Find(TEXT("RoadShadow")))
	{
		float Best = 1e9f;
		for (float D0 = 0.f; D0 < DriveTotal; D0 += 100.f)
		{
			const float Dd = FVector::Dist2D(PathPoint(DrivePts, DriveLen, D0), Sh->GetActorLocation());
			if (Dd < Best) { Best = Dd; ShadowDist = D0; }
		}
		ShowTagged(TEXT("RoadShadow"), true);
		UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE the thing on the road stands %.0f m in"), ShadowDist / 100.f);
	}'''),
    ('''		BigTarget = 0.f;
		HintUntil = 0.0;
		FadeTo(0.f, 1.f);
		DriveDist = DriveTotal - 3000.f;''', '''		BigTarget = 0.f;
		HintUntil = 0.0;
		FadeTo(0.f, 1.f);
		DriveDist = DriveTotal - 3000.f;
		ShadowPhase = 3;
		ShowTagged(TEXT("RoadShadow"), false);'''),
    ('''	const float Want = Left < 2600.f ? FMath::Max(55.f, 800.f * FMath::Sqrt(FMath::Max(Left, 0.f) / 2600.f)) : 800.f;
	DriveSpeed = FMath::FInterpTo(DriveSpeed, Want, Dt, 2.5f);''', '''	const float Cruise = 620.f;                   // slow: a deputy on a dirt road at night he does not know
	float Want = Left < 2600.f ? FMath::Max(55.f, Cruise * FMath::Sqrt(FMath::Max(Left, 0.f) / 2600.f)) : Cruise;
	float Ease = 2.5f;
	float LookBack = 0.f;
	if (ShadowDist > 0.f && ShadowPhase < 3)
	{
		ShadowT += Dt;
		if (ShadowPhase == 0 && DriveDist > ShadowDist + 230.f)
		{
			// it has just left the headlights: and it is not there any more
			ShadowPhase = 1; ShadowT = 0.f;
			ShowTagged(TEXT("RoadShadow"), false);
			UE_LOG(LogWCHouse, Display, TEXT("WCEVENT t=%.1f passed the thing on the road"), PlaySeconds);
		}
		else if (ShadowPhase == 1)
		{
			if (ShadowT > 1.3f) { Want = 0.f; Ease = 0.75f; }
			if (ShadowT > 1.3f && DriveSpeed < 14.f) { ShadowPhase = 2; ShadowT = 0.f; DriveSpeed = 0.f; }
			if (ShadowT > 1.9f && ShadowT - Dt <= 1.9f) Think(TEXT("...Was somebody standing there?"), 4.5f);
		}
		else if (ShadowPhase == 2)
		{
			Want = 0.f; DriveSpeed = 0.f;
			// a slow turn in the seat, a long look down the road behind, a slow turn back
			if (ShadowT < 1.2f) LookBack = 0.f;
			else if (ShadowT < 5.0f) LookBack = FMath::InterpEaseInOut(0.f, 1.f, (ShadowT - 1.2f) / 3.8f, 2.f);
			else if (ShadowT < 9.0f) LookBack = 1.f;
			else if (ShadowT < 12.4f) LookBack = FMath::InterpEaseInOut(1.f, 0.f, (ShadowT - 9.0f) / 3.4f, 2.f);
			else { ShadowPhase = 3; ShadowT = 0.f; }
			if (ShadowT > 6.4f && ShadowT - Dt <= 6.4f) Think(TEXT("Nothing. Just the road."), 4.f);
		}
	}
	else if (ShadowPhase == 3 && ShadowDist > 0.f && DriveSpeed < Cruise * 0.9f && Left > 2600.f) Ease = 0.5f;      // and he pulls away gently
	DriveSpeed = FMath::FInterpTo(DriveSpeed, Want, Dt, Ease);'''),
    ('''	Rel.Yaw = FMath::Clamp(Rel.Yaw, -80.f, 80.f);
	Rel.Pitch = FMath::Clamp(Rel.Pitch, -30.f, 28.f);''', '''	Rel.Yaw = FMath::Clamp(Rel.Yaw, -80.f, 80.f);
	Rel.Pitch = FMath::Clamp(Rel.Pitch, -30.f, 28.f);
	if (ShadowPhase == 2) { Rel.Yaw = 154.f * LookBack; Rel.Pitch = -2.f * LookBack; }      // over his right shoulder, where it stood'''),
])

# ---------------------------------------------------------------- level: the figure, and the back of the cabin he looks through
p = P + "Scripts/level/forest.py"
s = io.open(p, encoding="utf-8").read()
old = '''cab("PillarBR", -30, -18, -80, -74, 100, 150)'''
new = '''cab("PillarBR", -30, -18, -80, -74, 100, 150)
# what he sees when he turns round in his seat: the seat backs, the cage, the rear shelf and the frame of the back window
cab("SeatBackDriver", -24, -13, 14, 62, 50, 116)
cab("SeatBackPass", -24, -13, -62, -14, 50, 112)
cab("CageBar", -34, -30, -74, 74, 118, 122)
cab("RearSeat", -122, -102, -66, 66, 40, 104)
cab("RearShelf", -200, -122, -70, 70, 94, 101)
cab("PillarCL", -208, -196, 62, 80, 100, 150)
cab("PillarCR", -208, -196, -80, -62, 100, 150)
cab("RearHeader", -208, -192, -72, 72, 141, 150)
cab("RearSill", -212, -200, -72, 72, 94, 103)'''
assert old in s
s = s.replace(old, new)
old = '''place("Sign_Turn_Back", -5200, 1010, -40, 200, FO + "/Under", collide=False)'''
new = '''# the thing on the road: half way in, at the right-hand edge of the dirt, facing the car that is coming
_si = int(len(SAMPLES) * 0.47)
(_sx0, _sy0), (_sx1, _sy1) = SAMPLES[_si], SAMPLES[_si + 1]
_sd = math.hypot(_sx1 - _sx0, _sy1 - _sy0)
_sux, _suy = (_sx1 - _sx0) / _sd, (_sy1 - _sy0) / _sd
_shx, _shy = _sx0 + _suy * 168, _sy0 - _sux * 168          # to the driver's right
_fig = figure("RoadShadow", _shx, _shy, -41, math.degrees(math.atan2(-_suy, -_sux)), 0.98, "Tall", "RoadShadow", void=True, at=3.0)
log(f"road shadow at ({_shx:.0f},{_shy:.0f}), sample {_si} of {len(SAMPLES)}")
place("Sign_Turn_Back", -5200, 1010, -40, 200, FO + "/Under", collide=False)'''
assert old in s
s = s.replace(old, new)
compile(s, p, "exec")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
