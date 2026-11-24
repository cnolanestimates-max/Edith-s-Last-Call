// S3, rebuilt as the stairwell (Cheyenne, 2026-11-24: "a grudge type ... slower is better all the way up until you get to run
// from her and shoot and the chase is on").  It replaces the walk-at-you lock-in, and keeps its place in the story: the back
// door is nailed shut, he turns for the front of the house, the power dies, and:
//   1. Listen.  The game takes him.  He looks slowly up at the ceiling while it happens overhead: a thump, something large
//      dragged across the floor, more thumps, bones cracking, then a long high moan.  Then nothing.  He has control back.
//   2. The stairs.  When he sets foot on the first steps, he is taken again.  He looks up the flight into the dark.  One long
//      arm comes down out of it onto a step, then the other, a step lower.  "Mrs. Harrow?"  The pistol comes up.  Her face
//      comes into the light, head first down the stairs, and she screams at him with her tongue out.
//   3. Run or shoot.  She comes down the stairs and after him with everything she has; when she reaches him, the first memory.
// Everything up to the chase is slow.
#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

DEFINE_LOG_CATEGORY_STATIC(LogWCStairs, Log, All);

namespace
{
	enum class EStairs : uint8 { Idle, Listening, Waiting, Reveal, Chase, Done };
	EStairs GStairs = EStairs::Idle;
	double GStairsAt = 0.0;               // when the current phase began
	double GNextLure = 0.0;
	double GChaseStep = 0.0;
	int32 GChaseShots = 0;
	FVector GLookAt = FVector::ZeroVector;
	float GLookRate = 6.f;                // degrees a second the game turns his head while it has him
	bool GLookHead = false;               // follow her face instead of a fixed point

	// the ground flight: foot at X 400 (Z 0), head at X 800 (Z 350), Y -184..8; she comes down it head first
	const float StairPitch = -41.2f;
	FVector OnFlight(float S)            // S cm down the slope from the head of the stairs
	{
		const float C = FMath::Cos(FMath::DegreesToRadians(41.2f)), Sn = FMath::Sin(FMath::DegreesToRadians(41.2f));
		return FVector(800.f - S * C, -88.f, 350.f - S * Sn);
	}
}

void AWCDirector::StairsReset()
{
	GStairs = EStairs::Idle;
}

void AWCDirector::StairsListen()
{
	AWCCharacter* P = Player();
	if (!P) return;
	GStairs = EStairs::Listening;
	GStairsAt = Clock;
	Set(TEXT("stairs_listen"));
	UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs listen"), PlaySeconds);
	bBusy = true;
	P->SetInputLocked(true);
	P->SetAiming(false);
	// the power goes as he turns for the front door (the fuse he will need later)
	Set(TEXT("power_out"));
	bPowerOut = true;
	KillLights(0.f, true);
	P->FlickerLight(0.9f, 0.8f);
	SetLoop(TEXT("amb"), TEXT("amb_house"), 0.06f, 2.5f);
	Tension = 0.7f;
	// his eyes go up to the ceiling over the stairs, slowly, and stay there
	GLookAt = FVector(FMath::Clamp(P->GetActorLocation().X - 140.f, 820.f, 1250.f), -90.f, 560.f);
	GLookRate = 5.f;
	const FVector A(1180.f, -330.f, 362.f), B(1000.f, -230.f, 362.f), C(860.f, -120.f, 362.f);
	GLookHead = false;
	// his eyes follow it across the ceiling: the thump, the drag toward the stairs, the bones, the moan from the stairwell
	auto LookToward = [this](const FVector& At) { GLookAt = FVector(At.X, At.Y * 0.6f, 350.f); };
	After(2.4f, [this, A, LookToward]() { PlayAt(TEXT("thump_heavy"), A, 1.f, 0.9f, 4000.f); if (AWCCharacter* Q = Player()) Q->AddShake(0.15f); LookToward(A); });
	After(3.9f, [this, B, LookToward]() { PlayAt(TEXT("drag_floor"), B, 1.f, 0.85f, 4000.f); LookToward(B); GLookRate = 3.f; });
	After(8.0f, [this, C, LookToward]() { LookToward(C); });
	After(4.6f, [this, B]() { PlayAt(TEXT("creak"), B + FVector(40, 0, 0), 0.8f, 0.8f, 3500.f); });
	After(6.8f, [this, B]() { PlayAt(TEXT("creak"), B - FVector(90, 0, 0), 0.7f, 0.75f, 3500.f); });
	After(8.6f, [this, C]() { PlayAt(TEXT("thump_far"), C, 1.f, 0.95f, 4000.f); });
	After(9.3f, [this, C]() { PlayAt(TEXT("thump_far"), C + FVector(30, 20, 0), 0.9f, 0.88f, 4000.f); });
	// bones, one after another, as something unfolds itself
	const float Cracks[] = { 10.6f, 11.15f, 11.4f, 12.2f, 12.55f };
	for (int32 i = 0; i < 5; ++i)
		After(Cracks[i], [this, C, i]() { PlayAt(TEXT("bone_crack"), C + FVector(-20.f * i, 10.f, 0.f), 0.95f, FMath::FRandRange(0.82f, 1.12f), 3600.f); });
	// and then the sound she makes: high, long, drawn out
	After(14.0f, [this]() { PlayAt(TEXT("stair_moan"), OnFlight(-40.f) + FVector(0, 0, 60), 1.f, 1.f, 5000.f); Tension = 0.85f; GLookAt = FVector(830.f, -40.f, 330.f); GLookRate = 4.f; });
	// silence.  He has himself back.
	After(24.0f, [this]()
	{
		if (AWCCharacter* Q = Player()) Q->SetInputLocked(false);
		bBusy = false;
		Set(TEXT("stairs_waiting"));
		GStairs = EStairs::Waiting;
		GStairsAt = Clock;
		GNextLure = Clock + 28.0;
		UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs waiting at the stairs"), PlaySeconds);
	});
}

void AWCDirector::StairsReveal()
{
	AWCCharacter* P = Player();
	AWCEntity* H = Her();
	if (!P || !H) return;
	GStairs = EStairs::Reveal;
	GStairsAt = Clock;
	Set(TEXT("lockin_started"));              // the story's S3: "gotup" after her grab finishes it as the lock-in did
	ShotsAtHer = 0;
	UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs reveal"), PlaySeconds);
	bBusy = true;
	P->SetInputLocked(true);
	GLookAt = OnFlight(150.f) + FVector(0, 0, 50);
	GLookRate = 7.f;
	GLookHead = false;
	// up there in the dark, on her front, head first down the flight; only her reach comes into the light at first
	H->Appear(OnFlight(40.f), 180.f, TEXT("Crawl"), true, 0.32f);
	H->SetActorRotation(FRotator(StairPitch, 180.f, 0.f));
	H->FacePlayer(false);
	H->SetScream(0.f);
	H->SetGlow(0.f);
	H->SetFarGlow(110.f);                     // barely there: pale hands and a shape, at the edge of his light
	Tension = 0.9f;
	After(0.6f, [this]() { if (AWCEntity* E = Her()) E->Slide(OnFlight(120.f), 4.2f); PlayAt(TEXT("her_breath"), OnFlight(60.f), 0.7f, 0.9f, 2500.f); });
	After(3.2f, [this]() { PlayAt(TEXT("crawl_knocks"), OnFlight(200.f), 0.9f, 0.85f, 3000.f); });      // the first hand on a step
	After(5.0f, [this]() { if (AWCEntity* E = Her()) E->Slide(OnFlight(165.f), 3.0f); });
	After(6.6f, [this]() { PlayAt(TEXT("crawl_knocks"), OnFlight(250.f), 1.f, 0.8f, 3000.f); });       // the other, a step lower
	After(7.2f, [this]()
	{
		const float T = Say(TEXT("d_call1"), 0.f);
		After(T + 0.3f, [this]() { if (AWCCharacter* Q = Player()) { Q->SetAiming(true); Q->AddShake(0.1f); } });
	});
	// her face comes down into the light
	After(10.4f, [this]() { if (AWCEntity* E = Her()) { E->Slide(OnFlight(290.f), 2.6f); E->SetEyeShine(1.f); E->SetGlow(0.35f); E->SetFarGlow(380.f); } PlayAt(TEXT("her_breath"), OnFlight(260.f), 1.f, 0.8f, 2500.f); GLookHead = true; GLookRate = 5.f; });
	// and she screams at him, tongue out
	After(13.4f, [this]()
	{
		if (AWCEntity* E = Her()) { E->SetScream(1.f); E->SetGlow(1.2f); E->SetFarGlow(900.f); }
		Play2D(TEXT("her_scream"), 1.f);
		Play2D(TEXT("sting_hit"), 1.f, EWCSnd::Music);
		// his light holds on her face while she screams (no flicker: this is the moment to see her)
		if (AWCCharacter* Q = Player()) { Q->AddShake(0.8f); Q->SetFaceLight(85.f); }
		Tension = 1.f;
		UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs scream"), PlaySeconds);
	});
	// then she comes.  He has himself back, and a breath to use it: she hangs there screaming, then comes down the flight
	// head first in a rush and stands up at the bottom.  Run, or stand and shoot.
	After(15.2f, [this]()
	{
		if (AWCCharacter* Q = Player()) Q->SetInputLocked(false);
		bBusy = false;
		Play2D(TEXT("sting_rise"), 0.9f, EWCSnd::Music);
		if (AWCEntity* E = Her()) { E->Play(TEXT("Crawl"), true, 1.4f); E->SetScream(1.f); }
	});
	After(16.2f, [this]()
	{
		AWCEntity* E = Her();
		if (!E) return;
		E->Play(TEXT("Crawl"), true, 2.6f);
		E->SetScream(1.f);
		PlayAt(TEXT("crawl_knocks"), E->GetActorLocation(), 1.f, 1.15f, 3200.f);
		E->Slide(OnFlight(532.f) + FVector(-25.f, 0.f, 0.f), 1.6f, [this]()
		{
			if (AWCEntity* E2 = Her())
			{
				E2->SetActorRotation(FRotator(0.f, E2->GetActorRotation().Yaw, 0.f));
				E2->Play(TEXT("Rise"), false, 2.4f);
				E2->SetScream(1.f);
			}
			After(0.35f, [this]()
			{
				GStairs = EStairs::Chase;
				GStairsAt = Clock;
				if (AWCEntity* E3 = Her()) E3->SetFarGlow(AWCEntity::DefaultFarGlow);
				if (AWCCharacter* Q = Player()) { Q->SetFaceLight(0.f); Q->FlickerLight(0.5f, 0.5f); }
				GChaseStep = 0.0;
				GChaseShots = ShotsAtHer;
				Play2D(TEXT("her_scream"), 0.9f);
				UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs chase"), PlaySeconds);
			});
		});
	});
}

bool AWCDirector::IsStairsChase() const
{
	return GStairs == EStairs::Chase;
}

void AWCDirector::TickStairs(float Dt)
{
	AWCCharacter* P = Player();
	if (!P) return;
	// a checkpoint load can put the story back before (or past) this scene: follow the flags
	if (GStairs != EStairs::Idle && !Has(TEXT("stairs_listen")) && !Has(TEXT("lockin_started"))) GStairs = EStairs::Idle;
	if (GStairs != EStairs::Done && Has(TEXT("lockin_done"))) GStairs = EStairs::Done;
	if (GStairs == EStairs::Idle && Has(TEXT("stairs_listen")) && !Has(TEXT("lockin_started")) && !bBusy) { GStairs = EStairs::Waiting; GNextLure = Clock + 8.0; }
	if (GStairs == EStairs::Idle)
	{
		if (Has(TEXT("lockin_started")) || Has(TEXT("stairs_listen")) || !Has(TEXT("stairs_armed"))) return;
		if (bBusy || bEventBusy || StalkState != 0 || P->IsDown()) return;
		const FVector L = P->GetActorLocation();
		// heading back toward the front of the house, along the ground-floor hall, short of the stairwell's far end
		if (L.Z > 40.f && L.Z < 200.f && FMath::Abs(L.Y) < 230.f && L.X > 820.f && L.X < 1350.f) StairsListen();
		return;
	}
	// while the game has him, it turns his head, slowly
	if ((GStairs == EStairs::Listening || GStairs == EStairs::Reveal) && P->IsInputLocked())
	{
		if (AController* C = P->GetController())
		{
			// slow, but never so slow that a big turn takes forever: the rate grows with how far there is to go
			if (GLookHead) if (AWCEntity* E = Her()) GLookAt = E->HeadLocation();
			const FRotator Want = (GLookAt - P->EyeLocation()).Rotation();
			const FRotator Cur = C->GetControlRotation();
			const float Far = FMath::Max(FMath::Abs(FRotator::NormalizeAxis(Want.Yaw - Cur.Yaw)), FMath::Abs(FRotator::NormalizeAxis(Want.Pitch - Cur.Pitch)));
			C->SetControlRotation(FMath::RInterpConstantTo(Cur, FRotator(Want.Pitch, Want.Yaw, 0.f), Dt, GLookRate + 0.55f * Far));
		}
	}
	if (GStairs == EStairs::Waiting)
	{
		const FVector L = P->GetActorLocation();
		// the first few steps of the flight
		if (L.X > 330.f && L.X < 600.f && L.Y > -200.f && L.Y < 20.f && L.Z < 260.f && !bBusy && !P->IsDown()) { StairsReveal(); return; }
		// if he keeps away, the stairwell calls him: a step creaks up there, the moan again, softer
		if (Clock > GNextLure)
		{
			GNextLure = Clock + 26.0;
			PlayAt(TEXT("creak"), OnFlight(-30.f), 0.7f, 0.8f, 3500.f);
			After(2.2f, [this]() { PlayAt(TEXT("bone_crack"), OnFlight(-40.f), 0.6f, 0.9f, 3500.f); });
		}
		return;
	}
	if (GStairs == EStairs::Chase)
	{
		AWCEntity* H = Her();
		if (!H || !H->IsShown()) { GStairs = EStairs::Done; return; }
		const double In = Clock - GStairsAt;
		if (ShotsAtHer != GChaseShots)
		{
			// every shot, she jerks back and stops, and then comes on
			GChaseShots = ShotsAtHer;
			H->StopMoving();
			H->Play(TEXT("Rise"), false, 2.f);
			GChaseStep = Clock + 0.6;
			PlayAt(TEXT("her_flinch"), H->HeadLocation(), 1.f, 1.f, 3500.f);
			P->FlickerLight(0.25f, 0.9f);
		}
		if (Clock > GChaseStep)
		{
			GChaseStep = Clock + 0.25;
			// fury, in lurches: she surges and checks and surges, faster the longer it goes, and when she is close enough
			// she throws herself at him.  He walks at 1 m/s and runs at 1.3: she gains a little at first, then quickly.
			const float Base = FMath::Min(130.f + 14.f * (float)In, 320.f);
			const float Surge = 1.f + 0.55f * FMath::Sin((float)In * 2.f * PI / 0.85f);
			const float Speed = H->DistToPlayer() < 175.f ? 480.f : Base * Surge;
			TArray<FVector> Route;
			AutoRoute(H->GetActorLocation() + FVector(0, 0, 88), P->GetActorLocation() - FVector(0, 0, 88), Route);
			for (FVector& V : Route) V.Z = FMath::RoundToFloat(V.Z / 350.f) * 350.f;
			if (Route.Num() == 0) Route.Add(P->GetActorLocation() - FVector(0, 0, 88));
			H->MoveAlong(Route, Speed, TEXT("Run"));
			H->SetScream(1.f);
			if (FMath::Fmod((float)In, 2.6f) < 0.25f) PlayAt(TEXT("her_scream_short"), H->HeadLocation(), 0.8f, FMath::FRandRange(0.95f, 1.1f), 3500.f);
		}
		if (H->DistToPlayer() < 165.f && FMath::Abs(H->GetActorLocation().Z - (P->GetActorLocation().Z - 88.f)) < 140.f)
		{
			GStairs = EStairs::Done;
			UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs caught after %.1f s, %d shots"), PlaySeconds, In, ShotsAtHer);
			// the grab: the first time she has him, he sees the first memory (Grab), then he wakes on the floor ("gotup")
			Grab(1.3f, [this]()
			{
				if (AWCCharacter* Pl = Player()) Pl->Knockdown(3.0f);
				FadeTo(1.f, 0.3f);
				After(0.7f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); });
				After(2.8f, [this]() { FadeTo(0.f, 1.6f); });
			});
		}
	}
}
