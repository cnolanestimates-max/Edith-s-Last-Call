# Pass 118 (Cheyenne, 20:12 UTC): the hole behind the settlers book goes through to the stairwell.  Her eye is on the
# stair side; when she pulls away she runs up the stairs and he hears it.  The game also puts him square to the hole.
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

ROOT = r"C:\GameDev\Unreal\WellnessCheck"
H = ROOT + r"\Source\WellnessCheck\WCHouse.cpp"
W = ROOT + r"\Scripts\level\watchers.py"
A = ROOT + r"\Source\WellnessCheck\WCAuto.cpp"

edit(H, [
    # he is drawn square to the gap while the book comes out, so the books either side cannot hide her
    ("""		const FVector Gap = EyeW ? EyeW->GetActorLocation() : From;
		for (int32 i = 1; i <= 16; ++i) After(i * 0.035f, [this, Gap]()
		{
			AWCCharacter* Q = Player();
			if (!Q || !Q->GetController()) return;
""",
     """		const FVector Gap = EyeW ? EyeW->GetActorLocation() : From;
		const FVector Side = EyeW ? EyeW->GetActorRightVector() : FVector::ZeroVector;
		for (int32 i = 1; i <= 16; ++i) After(i * 0.035f, [this, Gap, Side]()
		{
			AWCCharacter* Q = Player();
			if (!Q || !Q->GetController()) return;
			// a half step to the side, no more: he ends up square to the hole
			const float Off = FVector::DotProduct(Q->GetActorLocation() - Gap, Side);
			Q->SetActorLocation(Q->GetActorLocation() - Side * (Off - FMath::FInterpTo(Off, 0.f, 0.035f, 9.f)), true);
"""),
    # she is on the stairs, the other side of this wall: she goes up them at a run
    ("""		// she holds his eye for two seconds, then she is away along the inside of the wall
		After(2.1f, [this, EyeW, Glim]()
		{
			if (Glim.IsValid()) Glim->SetIntensity(0.f);
			if (EyeW)
			{
				const FVector At = EyeW->GetActorLocation();
				const FVector Along = EyeW->GetActorRightVector();
				EyeW->Withdraw(true);
				for (int32 k = 0; k < 6; ++k) After(k * 0.28f, [this, At, Along, k]() { PlayAt(k % 2 ? TEXT("skitter") : TEXT("scratch_wall"), At + Along * (120.f * k) + FVector(0, 0, 30.f * k), 1.f, 1.1f, 1600.f); });
			}
		});
""",
     """		// she holds his eye for two seconds; then she is gone from the hole and running up the stairs behind the wall
		After(2.1f, [this, EyeW, Glim]()
		{
			if (Glim.IsValid()) Glim->SetIntensity(0.f);
			if (EyeW) EyeW->Withdraw(true);
			const FVector A = Pos(TEXT("StairRunA")), B = Pos(TEXT("StairRunB")), C = Pos(TEXT("StairRunC"));
			if (A.IsNearlyZero() || B.IsNearlyZero()) return;
			UE_LOG(LogWCHouse, Display, TEXT("WCSCARE t=%.1f S10_book she runs up the stairs"), PlaySeconds);
			// seven treads at a run, then away along the landing overhead
			for (int32 k = 0; k < 7; ++k) After(0.12f + k * 0.19f, [this, A, B, k]() { PlayAt(TEXT("step_stairs"), FMath::Lerp(A, B, k / 6.f), 1.f, Rng.FRandRange(0.82f, 0.92f), 2600.f); });
			for (int32 k = 0; k < 4; ++k) After(0.12f + 7 * 0.19f + k * 0.24f, [this, B, C, k]() { PlayAt(TEXT("her_step"), FMath::Lerp(B, C, (k + 1) / 4.f), 0.9f - 0.12f * k, Rng.FRandRange(0.9f, 1.f), 3000.f); });
		});
"""),
    ("""		Think(TEXT("She's in the walls."));
		Checkpoint(TEXT("book"));""",
     """		Think(TEXT("She was on the stairs."));
		Checkpoint(TEXT("book"));"""),
])

edit(W, [
    # her eye is set back in the hole, not standing proud of the wall; and the stair behind it is marked for the run
    ("""watcher("book_eye", SETTLERS_X, BKY - 1.2, BKZ + 13, -90.0, 0.0, 0, 5.6, scripted=True)
""",
     """watcher("book_eye", SETTLERS_X, BKY + 1.0, BKZ + 13, -90.0, 0.0, 0, 5.6, scripted=True)
# The wall behind this bookcase is the stair tower's: she is crouched on the main flight with her eye to the hole.
# When she goes, she goes up it: from the tread behind the hole to the head of the flight, then along the landing.
point("StairRunA", SETTLERS_X, (SY0 + SY1) / 2, GZ + (SETTLERS_X - SX0) / (SX1 - SX0) * 350.0 + 10.0)
point("StairRunB", SX1 - 10.0, (SY0 + SY1) / 2, UZ + 10.0)
point("StairRunC", 1040.0, 40.0, UZ + 10.0)
log(f"bookcase: settlers book at x {SETTLERS_X:.1f}; the stair tread behind the hole is at z {GZ + (SETTLERS_X - SX0) / (SX1 - SX0) * 350.0:.0f}, the hole at z {BKZ + 13:.0f}")
"""),
])

edit(A, [
    ("at:560,-292,92,112,-9", "at:572,-292,92,112,-9"),
])
print("pass 118 applied")
