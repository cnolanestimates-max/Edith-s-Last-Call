# Pass 121 (Cheyenne, 20:27 UTC): the opening shot.  "From a drone view ... the cop car driving through the forest,
# from way above, bird's eye view ... it follows the car, weaving through the windy roads in the forest for a little
# while, and then finally it flies down and into the car as you being the player, first person."
# The drive is the same drive; for its first 18 seconds the camera is not in the seat but high over the trees.
#   -WCNoAir  : start in the seat as before        -WCAirOnly : (tests) quit three seconds after the camera is in the car
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

S = r"C:\GameDev\Unreal\WellnessCheck\Source\WellnessCheck"

edit(S + r"\WCDirector.h", [
    ("""	TWeakObjectPtr<class ACameraActor> DriveCam;
""",
     """	TWeakObjectPtr<class ACameraActor> DriveCam;
	// the opening shot from the air: seconds into it, whether the outside of the car has been swapped for the inside yet
	bool bAir = false, bAirDip = false, bAirSwapped = true;
	float AirT = 0.f, CabinFov = 66.f;
	void AirIntoCar();
"""),
])

edit(S + r"\WCHouse.cpp", [
    ("""void AWCDirector::BeginDrive()
{
""",
     """static const float GAirDur = 18.f;            // how long the camera is outside the car at the start of the drive

void AWCDirector::AirIntoCar()
{
	// the camera is through the roof: the outside of the car goes, the inside is there, the night is shut out
	if (bAirSwapped) return;
	bAirSwapped = true;
	ShowTagged(TEXT("CabinOnly"), true);
	if (Car.IsValid()) Car->SetActorHiddenInGame(true);
	SetLoop(TEXT("amb"), TEXT(""), 0.f, 0.8f);
}

void AWCDirector::BeginDrive()
{
"""),
    ("""			Cam->GetCameraComponent()->SetFieldOfView(FMath::Min(Settings.FOV - 8.f, 66.f));      // tighter, so the windscreen fills the picture
""",
     """			CabinFov = FMath::Min(Settings.FOV - 8.f, 66.f);
			Cam->GetCameraComponent()->SetFieldOfView(CabinFov);      // tighter, so the windscreen fills the picture
"""),
    ("""	SetLoop(TEXT("amb"), TEXT(""), 0.f, 1.f);              // windows up: the night is not heard until he gets out
		TickDrive(0.f);
	After(5.f, [this]() { if (bDriving) ShowHint(TEXT("Mouse: look around        Space: skip the drive"), 6.f); });
""",
     """	SetLoop(TEXT("amb"), TEXT(""), 0.f, 1.f);              // windows up: the night is not heard until he gets out
	// the opening shot: high over the forest, his headlights threading the road, then down and into the car
	bAir = !FParse::Param(FCommandLine::Get(), TEXT("WCNoAir"));
	AirT = 0.f; bAirDip = false; bAirSwapped = !bAir;
	if (bAir)
	{
		ShowTagged(TEXT("CabinOnly"), false);
		Car->SetActorHiddenInGame(false);
		SetLoop(TEXT("amb"), TEXT("amb_night"), 0.5f, 1.5f);        // out here the night is all there is to hear
	}
		TickDrive(0.f);
	After(bAir ? GAirDur + 2.f : 5.f, [this]() { if (bDriving) ShowHint(TEXT("Mouse: look around        Space: skip the drive"), 6.f); });
"""),
    ("""		DriveDist = DriveTotal - 3000.f;
		ShadowPhase = 3;
""",
     """		DriveDist = DriveTotal - 3000.f;
		if (bAir) { bAir = false; AirIntoCar(); if (DriveCam.IsValid()) DriveCam->GetCameraComponent()->SetFieldOfView(CabinFov); }
		ShadowPhase = 3;
"""),
    ("""	if (DriveCam.IsValid() && Seat.IsValid())
	{
		DriveCam->SetActorLocationAndRotation(Seat->GetActorLocation() + FVector(0, 0, Bump * 0.8f), FRotator(Rel.Pitch + Bump * 0.12f, Heading + Rel.Yaw, Roll));
	}
	if (FLoop* Eng = Loops.Find(TEXT("car"))) Eng->Target = 0.55f + 0.4f * Rough;
""",
     """	float AirS = 1.f;
	if (DriveCam.IsValid() && Seat.IsValid())
	{
		const FVector SeatPos = Seat->GetActorLocation() + FVector(0, 0, Bump * 0.8f);
		const FRotator SeatRot(Rel.Pitch + Bump * 0.12f, Heading + Rel.Yaw, Roll);
		if (bAir)
		{
			AirT += Dt;
			const float U = FMath::Clamp(AirT / GAirDur, 0.f, 1.f);
			// the first half and a little more it stays up and follows; then it comes down a long curve to the seat
			AirS = FMath::SmoothStep(0.f, 1.f, (U - 0.55f) / 0.45f);
			const float Up = FMath::Clamp(U / 0.55f, 0.f, 1.f);
			const FVector CarPos(Pos0.X, Pos0.Y, CarHome.Z);
			const FVector Fwd = FRotator(0.f, Heading, 0.f).Vector();
			const float Orbit = Heading + 180.f + 42.f * FMath::Sin(AirT * 0.21f + 0.6f);
			const FVector High = CarPos + FRotator(0.f, Orbit, 0.f).Vector() * FMath::Lerp(700.f, 1900.f, Up) + FVector(0, 0, FMath::Lerp(5600.f, 3300.f, Up));
			const FVector Chase = CarPos - Fwd * 1000.f + FVector(0, 0, 420.f);
			const FVector Cp = FMath::Square(1.f - AirS) * High + 2.f * AirS * (1.f - AirS) * Chase + AirS * AirS * SeatPos;
			const FVector LookAt = CarPos + Fwd * FMath::Lerp(0.f, 2600.f, AirS) + FVector(0, 0, 90.f);
			const FQuat Q = FQuat::Slerp((LookAt - Cp).Rotation().Quaternion(), SeatRot.Quaternion(), FMath::SmoothStep(0.f, 1.f, (AirS - 0.72f) / 0.28f));
			DriveCam->SetActorLocationAndRotation(Cp, Q);
			DriveCam->GetCameraComponent()->SetFieldOfView(FMath::Lerp(46.f, CabinFov, AirS));
			if (!bAirDip && AirS > 0.80f) { bAirDip = true; FadeTo(0.85f, 0.3f); }
			if (!bAirSwapped && AirS > 0.88f) { AirIntoCar(); After(0.12f, [this]() { FadeTo(0.f, 0.7f); }); }
			if (bAuto && !AutoShotDir.IsEmpty())
			{
				static int32 AirShotN = -1;
				const int32 N = (int32)(AirT / 1.5f);
				if (N != AirShotN) { AirShotN = N; FScreenshotRequest::RequestScreenshot(AutoShotDir / FString::Printf(TEXT("air_%02d.png"), N), false, false); }
			}
			if (U >= 1.f)
			{
				bAir = false;
				AirIntoCar();
				DriveCam->GetCameraComponent()->SetFieldOfView(CabinFov);
				UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE t=%.1f the camera is in the car, %.0f m in"), PlaySeconds, DriveDist / 100.f);
				if (FParse::Param(FCommandLine::Get(), TEXT("WCAirOnly")))
				{
					const FString Dir0 = AutoShotDir;
					After(2.f, [Dir0]() { if (!Dir0.IsEmpty()) FScreenshotRequest::RequestScreenshot(Dir0 / TEXT("air_in_the_seat.png"), false, false); });
					After(3.5f, [this]() { UKismetSystemLibrary::QuitGame(this, UGameplayStatics::GetPlayerController(this, 0), EQuitPreference::Quit, false); });
				}
			}
		}
		else DriveCam->SetActorLocationAndRotation(SeatPos, SeatRot);
	}
	if (FLoop* Eng = Loops.Find(TEXT("car"))) Eng->Target = (0.55f + 0.4f * Rough) * (0.10f + 0.90f * AirS * AirS);      // from the air the engine is a long way down
"""),
])
print("pass 121 applied")
