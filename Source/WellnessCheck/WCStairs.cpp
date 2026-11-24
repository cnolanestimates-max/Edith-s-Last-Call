// S3, rebuilt as the stairwell (Cheyenne, 2026-11-24: "a grudge type ... slower is better all the way up until you get to run
// from her and shoot and the chase is on").  It replaces the walk-at-you lock-in, and keeps its place in the story: the back
// door is nailed shut, he turns for the front of the house, the power dies, and:
//   1. Listen.  The game takes him.  He looks slowly up at the ceiling while it happens overhead: a thump, something large
//      dragged across the floor, more thumps, bones cracking, then a long high moan.  Then nothing.  He has control back.
//   2. The stairs.  When he sets foot on the first steps, he is taken again.  He looks up the flight into the dark.  One long
//      arm comes down out of it onto a step, then the other, a step lower.  "Mrs. Harrow?"  The pistol comes up.  Her face
//      comes into the light, head first down the stairs, and she screams at him with her tongue out.
//   2b. (2026-11-24, fourth pass) Nothing shows on the stairs.  The game walks him slowly up calling "Mrs. ......
//      Harrow?"; just before his light reaches the upstairs hall it dies.  He goes on up in the dark.  The light comes
//      back: at the far end of the hall she is standing, looking at him.  It dies again; "Shit... shit..." as he beats
//      it against his hand; in the black, perfectly clear, her whisper: "You should never have come here."  A second of
//      silence, then loud thumping, and his light flickers on her coming down the hall at him on all fours; she has him.
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
	enum class EStairs : uint8 { Idle, Listening, Waiting, Reveal, Crawl, Lunge, Chase, Done };
	EStairs GStairs = EStairs::Idle;
	double GStairsAt = 0.0;               // when the current phase began
	double GNextLure = 0.0;
	double GChaseStep = 0.0;
	int32 GChaseShots = 0;
	FVector GLookAt = FVector::ZeroVector;
	float GLookRate = 6.f;                // degrees a second the game turns his head while it has him
	bool GLookHead = false;               // follow her face instead of a fixed point
	float GClimbToX = 0.f;                // while the game has him on the stairs: walk him up to here (0 = stand)
	float GClimbScale = 0.4f;

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
	// he whispers, to himself, staring up at it
	After(12.9f, [this]() { Say(TEXT("d_stairs_wtf"), 0.f); });
	After(16.6f, [this]() { PlayAt(TEXT("stair_moan"), OnFlight(-40.f) + FVector(0, 0, 60), 1.f, 1.f, 5000.f); Tension = 0.85f; GLookAt = FVector(830.f, -40.f, 330.f); GLookRate = 4.f; });
	// silence.  He has himself back.
	After(26.6f, [this]()
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
	GLookAt = OnFlight(190.f) + FVector(0, 0, 35);
	GLookRate = 7.f;
	GLookHead = false;
	// (Cheyenne, 2026-11-24: "make the cop come up the stairs a little ... as soon as his flashlight is about to crest the
	//  hallway make it go out ... after he gets up a little more it comes back on and she lunges in front of him and grabs
	//  him instantly")  Nothing on the stairs while he climbs: an empty flight and the dark at the top.  She is put in
	//  front of him only while his light is dead.
	H->Vanish();
	GLookAt = OnFlight(-60.f) + FVector(0, 0, 150);            // up the flight, to where the upstairs hall opens
	GLookRate = 5.f;
	GLookHead = false;
	GClimbToX = 520.f;                                       // a few slow steps up
	GClimbScale = 0.42f;
	Tension = 0.85f;
	After(1.2f, [this]() { Say(TEXT("d_stairs_call"), 0.f); });             // "Mrs. ...... Harrow?" up into the dark
	After(3.0f, [this]() { PlayAt(TEXT("creak"), OnFlight(-20.f), 0.5f, 0.75f, 3500.f); });
	// just before his light reaches the top, it dies
	After(6.6f, [this]() { if (AWCCharacter* Q = Player()) Q->FlickerLight(0.9f, 0.85f); });
	After(7.5f, [this]()
	{
		if (AWCCharacter* Q = Player()) { Q->SetLightScale(0.f); Q->AddShake(0.08f); }
		Play2D(TEXT("bulb_die"), 0.8f);
		GClimbToX = 0.f;                                     // he stops dead
		Tension = 0.95f;
		UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs light out"), PlaySeconds);
	});
	// in the dark, something up there moves away from him along the hall
	After(8.8f, [this]() { PlayAt(TEXT("steps_above"), FVector(1200.f, 40.f, 360.f), 0.7f, 0.9f, 3000.f); });
	// he goes on up anyway, until his eyes are over the top step
	After(9.6f, [this]() { GClimbToX = 720.f; GClimbScale = 0.5f; GLookAt = FVector(1560.f, 40.f, 500.f); });
	// the light comes back: the hall, and at the far end of it, her, standing, looking at him
	After(13.6f, [this]() { StairsHallStand(); });
	// it goes again
	After(17.4f, [this]()
	{
		if (AWCCharacter* Q = Player()) { Q->FlickerLight(0.5f, 0.9f); }
		After(0.45f, [this]()
		{
			if (AWCCharacter* Q = Player()) Q->SetLightScale(0.f);
			if (AWCEntity* E = Her()) E->Vanish();
			Play2D(TEXT("bulb_die"), 0.7f);
			UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs light out again"), PlaySeconds);
		});
	});
	// "Shit... shit..." and he shakes the dead flashlight and beats it against his other hand
	After(18.3f, [this]() { Say(TEXT("d_stairs_shit"), 0.f); });
	auto AtHands = [this]() { AWCCharacter* Q = Player(); return Q ? Q->EyeLocation() + Q->GetControlRotation().Vector() * 30.f + FVector(0, 0, -45.f) : FVector::ZeroVector; };
	After(18.5f, [this, AtHands]() { PlayAt(TEXT("flashlight_shake"), AtHands(), 1.f, 1.f, 900.f); });
	After(19.9f, [this, AtHands]() { PlayAt(TEXT("flashlight_smack"), AtHands(), 1.f, 1.f, 900.f); if (AWCCharacter* Q = Player()) Q->AddShake(0.05f); });
	After(20.9f, [this, AtHands]() { PlayAt(TEXT("flashlight_smack"), AtHands(), 0.9f, 1.07f, 900.f); if (AWCCharacter* Q = Player()) Q->AddShake(0.05f); });
	// then, in the black, a whisper right in his ear
	After(22.2f, [this]()
	{
		AWCCharacter* Q = Player();
		if (!Q) return;
		const FRotator Yaw(0.f, Q->GetControlRotation().Yaw, 0.f);
		const FVector Ear = Q->EyeLocation() - Yaw.Vector() * 14.f + FRotationMatrix(Yaw).GetUnitAxis(EAxis::Y) * 16.f;
		PlayAt(TEXT("VO/m_never"), Ear, 1.f, 1.f, 350.f);                 // "You should never have come here."
		FWCSubtitle Sub;
		Sub.Text = TEXT("You should never have come here.");
		Sub.Until = Clock + 3.5;
		Subtitles.Reset();
		Subtitles.Add(Sub);
		SetLoop(TEXT("amb"), TEXT(""), 0.f, 0.4f);
		UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs whisper"), PlaySeconds);
	});
	// two full seconds of nothing in the dark; then, still in the dark, her on all fours coming at him, loud; the light
	// only comes back when she is nearly on him
	After(27.2f, [this]() { StairsHallRush(); });
}

void AWCDirector::StairsHallStand()
{
	AWCCharacter* P = Player();
	AWCEntity* H = Her();
	if (!P || !H || GStairs == EStairs::Done) return;
	GClimbToX = 0.f;
	H->Appear(FVector(1520.f, 40.f, 350.f), 180.f, TEXT("Idle"), true, 0.6f);
	H->FacePlayer(true);
	H->SetScream(0.f);
	H->SetGlow(2.5f);                        // one eye catches his light: the thing you see first
	H->SetEyeShine(80.f, 2.6f);                 // bright enough to read at the far end of the hall
	H->SetFarGlow(240.f);                    // only just there: a pale shape at the end of the hall
	P->SetLightScale(1.f);
	P->FlickerLight(0.6f, 0.6f);
	GLookHead = true;
	GLookRate = 6.f;
	Play2D(TEXT("sting_low"), 0.7f, EWCSnd::Music);
	UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs she stands at the end of the hall"), PlaySeconds);
}

void AWCDirector::StairsHallRush()
{
	AWCCharacter* P = Player();
	AWCEntity* H = Her();
	if (!P || !H || GStairs == EStairs::Done) return;
	// in the dark: she is coming, loud, heavy and fast, on her hands and knees down the boards at him
	H->Appear(FVector(1460.f, 40.f, 350.f), 180.f, TEXT("Crawl"), true, 2.4f);
	H->FacePlayer(false);
	H->SetScream(1.f);
	H->SetGlow(0.f);
	H->SetEyeShine(1.f, 1.f);
	H->SetFarGlow(0.f);
	TArray<FVector> Path;
	Path.Add(FVector(860.f, -60.f, 350.f));
	Path.Add(P->GetActorLocation() - FVector(0, 0, 88) + FVector(70.f, 0, 0));
	H->MoveAlong(Path, 300.f, TEXT("Crawl"), [this]() { StairsCatch(0.f); });      // ~2.3 s of her coming in the dark
	H->SetScream(1.f);
	GStairs = EStairs::Lunge;
	GLookHead = true;
	GLookRate = 90.f;
	Play2D(TEXT("allfours_rush"), 1.f);
	UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs she comes, in the dark"), PlaySeconds);
	// his light catches her when she is nearly on him
	After(2.05f, [this]()
	{
		if (AWCCharacter* Q = Player()) { Q->SetLightScale(1.f); Q->FlickerLight(0.5f, 0.5f); Q->SetFaceLight(300.f); Q->AddShake(0.5f); }
		if (AWCEntity* E = Her()) { E->SetFarGlow(500.f); E->SetGlow(0.6f); }
		Play2D(TEXT("her_scream"), 1.f);
		Play2D(TEXT("sting_hit"), 1.f, EWCSnd::Music);
		UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs light on her"), PlaySeconds);
	});
}

void AWCDirector::StairsStep(float ToS, float Seconds, float KnockVolume, bool bScreaming)
{
	// one reach: the crawl plays half its cycle (one arm) while she slides that far down the flight, then holds still
	AWCEntity* E = Her();
	if (!E || GStairs == EStairs::Done || GStairs == EStairs::Chase || GStairs == EStairs::Lunge) return;
	const UAnimSequence* Seq = E->Anims.FindRef(TEXT("Crawl"));
	const float Half = Seq ? Seq->GetPlayLength() * 0.5f : 0.6f;
	E->Play(TEXT("Crawl"), true, Half / FMath::Max(Seconds, 0.1f));
	E->SetScream(bScreaming ? 1.f : 0.f);
	E->Slide(OnFlight(ToS), Seconds, [this, ToS, KnockVolume, bScreaming]()
	{
		if (GStairs == EStairs::Done || GStairs == EStairs::Chase || GStairs == EStairs::Lunge) return;
		if (AWCEntity* E2 = Her()) { E2->Body->SetPlayRate(0.f); E2->SetScream(bScreaming ? 1.f : 0.f); }
		PlayAt(TEXT("crawl_knocks"), OnFlight(ToS + 70.f), KnockVolume, FMath::FRandRange(0.8f, 0.95f), 3000.f);
	});
}

void AWCDirector::StairsLunge()
{
	AWCCharacter* P = Player();
	AWCEntity* H = Her();
	if (!P || !H || GStairs == EStairs::Done || GStairs == EStairs::Chase || GStairs == EStairs::Lunge) return;
	const FVector Feet = P->GetActorLocation() - FVector(0, 0, 88);
	const FVector From = H->GetActorLocation();
	FHitResult Hit;
	FCollisionQueryParams Q(SCENE_QUERY_STAT(WCStairsLunge), false, P);
	Q.AddIgnoredActor(H);
	const bool bSees = !GetWorld()->LineTraceSingleByChannel(Hit, H->HeadLocation(), P->EyeLocation(), ECC_Visibility, Q);
	const float Dist = FVector::Dist(From, Feet);
	if (Dist > 520.f || !bSees)
	{
		// he got clear away: she has to run him down first, and lunges when she is on him
		H->SetActorRotation(FRotator(0.f, (Feet - From).Rotation().Yaw, 0.f));
		H->Play(TEXT("Rise"), false, 2.4f);
		GStairs = EStairs::Chase;
		GStairsAt = Clock;
		GChaseStep = Clock + 0.35;
		GChaseShots = ShotsAtHer;
		P->SetFaceLight(0.f);
		H->SetFarGlow(AWCEntity::DefaultFarGlow);
		UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs chase (he got %.0f cm away)"), PlaySeconds, Dist);
		return;
	}
	// the lunge: up off the stairs and onto him
	GStairs = EStairs::Lunge;
	UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs lunge from %.0f cm"), PlaySeconds, Dist);
	const FVector To = Feet - (Feet - From).GetSafeNormal2D() * 95.f;      // her face fills his view; not inside it
	H->SetActorRotation(FRotator(0.f, (Feet - From).Rotation().Yaw, 0.f));
	H->Play(TEXT("Lunge"), false, 1.6f);
	H->SetScream(1.f);
	H->SetGlow(0.25f);
	Play2D(TEXT("her_scream_short"), 1.f);
	const float In = (float)(Clock - GStairsAt);
	H->Slide(To, FMath::Clamp(Dist / 750.f, 0.3f, 0.6f), [this, In]() { StairsCatch(In); });
}

void AWCDirector::StairsCatch(float In)
{
	if (GStairs == EStairs::Done) return;
	GStairs = EStairs::Done;
	GClimbToX = 0.f;
	if (AWCCharacter* Pl = Player()) { Pl->SetFaceLight(0.f); Pl->SetLightScale(1.f); }
	if (AWCEntity* E = Her()) E->SetFarGlow(AWCEntity::DefaultFarGlow);
	UE_LOG(LogWCStairs, Display, TEXT("WCSCARE t=%.1f S3_stairs caught (%d shots)"), PlaySeconds, ShotsAtHer);
	// the grab: the first time she has him, he sees the first memory (Grab), then he wakes on the floor ("gotup")
	Grab(1.3f, [this]()
	{
		if (AWCCharacter* Pl = Player()) Pl->Knockdown(3.0f);
		FadeTo(1.f, 0.3f);
		After(0.7f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); });
		After(2.8f, [this]() { FadeTo(0.f, 1.6f); });
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
	// the game walks him slowly up the flight
	if (GStairs == EStairs::Reveal && GClimbToX > 0.f && P->GetActorLocation().X < GClimbToX)
		P->AddMovementInput(FVector(1.f, 0.f, 0.f), GClimbScale);
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
	if (GStairs == EStairs::Crawl && ShotsAtHer != GChaseShots)
	{
		// shots while she crawls: she jerks at each one, and keeps coming
		GChaseShots = ShotsAtHer;
		if (AWCEntity* H = Her()) PlayAt(TEXT("her_flinch"), H->HeadLocation(), 1.f, 1.f, 3500.f);
		P->FlickerLight(0.2f, 0.6f);
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
		if (H->DistToPlayer() < 260.f)
		{
			// on him: the lunge
			H->StopMoving();
			GStairs = EStairs::Reveal;          // so StairsLunge takes her
			StairsLunge();
		}
	}
}
