"""Pass 84:
  - the television glass: the mirror camera gets its own exposure (it was rendering about six stops darker than the game view,
    so she was there but could not be seen); the test saves two exposures
  - S14, the eye in the dark (Cheyenne 05:08 UTC): every light dies, flashlight too; down the hall, up by the ceiling, only her
    eye; the flashlight comes back and nothing is there; when he takes the light off that spot the eye is back; it goes out in
    the dark.  Quiet, eerie sound, no sting."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('void TickTV(float Dt);', '''void TickTV(float Dt);
	// the eye in the dark (S14)
	void TickEye(float Dt);
	bool EyeTry(bool bForce);
	void EyeEnd(bool bSeenTwice);
	int32 EyePhase = 0;                         // 0 waiting, 1 black, 2 the eye, 3 light back and nothing there, 4 the eye again, 5 going out
	double EyeAt = 0.0, EyeNextAt = -1.0;
	FVector EyeSpot = FVector::ZeroVector;
	bool bEyeLooked = false;'''),
])

edit(R + "Source/WellnessCheck/WCHouse.cpp", [
    ('''TickTV(Dt);''', '''TickTV(Dt);
	TickEye(Dt);'''),
])

edit(R + "Source/WellnessCheck/WCEvents.cpp", [
    ('''TVCapture->bCaptureOnMovement = false;''', '''TVCapture->bCaptureOnMovement = false;
		// its own exposure: with the room's grade alone the mirror came out about six stops darker than the game view
		float Ev = -1.5f;
		FParse::Value(FCommandLine::Get(), TEXT("WCTVEV="), Ev);
		TVCapture->PostProcessSettings.bOverride_AutoExposureMethod = true;
		TVCapture->PostProcessSettings.AutoExposureMethod = EAutoExposureMethod::AEM_Manual;
		TVCapture->PostProcessSettings.bOverride_AutoExposureBias = true;
		TVCapture->PostProcessSettings.AutoExposureBias = Ev;
		TVCapture->PostProcessSettings.bOverride_VignetteIntensity = true;
		TVCapture->PostProcessSettings.VignetteIntensity = 0.f;
		TVCapture->PostProcessSettings.bOverride_FilmGrainIntensity = true;
		TVCapture->PostProcessSettings.FilmGrainIntensity = 0.f;
		TVCapture->PostProcessBlendWeight = 1.f;
		TVCapture->bAlwaysPersistRenderingState = true;'''),
    ('''After(1.0f, [this, D0]() { if (TVTarget) UKismetRenderingLibrary::ExportRenderTarget(this, TVTarget, D0, TEXT("S13_what_the_glass_sees_standing.png")); });''',
     '''After(0.8f, [this, D0]() { if (TVTarget) UKismetRenderingLibrary::ExportRenderTarget(this, TVTarget, D0, TEXT("S13_what_the_glass_sees_standing.png")); });
			After(0.85f, [this]() { if (TVCapture) TVCapture->PostProcessSettings.AutoExposureBias += 2.5f; });
			After(1.5f, [this, D0]() { if (TVTarget) UKismetRenderingLibrary::ExportRenderTarget(this, TVTarget, D0, TEXT("S13_what_the_glass_sees_standing_plus2.png")); });
			After(1.55f, [this]() { if (TVCapture) TVCapture->PostProcessSettings.AutoExposureBias -= 2.5f; });'''),
])

# ---- S14 at the end of WCEvents.cpp
p = R + "Source/WellnessCheck/WCEvents.cpp"
s = open(p, encoding="utf-8").read()
assert "TickEye" not in s
s += r'''
// ================================================================================================ the eye in the dark (S14)
// Cheyenne: "all of a sudden all lights go out ... flashlight, lights in the house, everything, but then down the hall in the air
// close to the ceiling there's just her eye ... then your flashlight comes back on only and the player can shine it on her, she
// won't be there. Then when the player goes to move the light away from that spot the eye will reappear, then it will disappear
// in the dark" and "not crazy: very eerie and creepy sound design".
bool AWCDirector::EyeTry(bool bForce)
{
	AWCCharacter* P = Player();
	if (!P || !Her()) return false;
	// a long level look the way he is facing: a hall
	const FVector Eye = P->EyeLocation();
	const FVector Fwd = P->EyeForward().GetSafeNormal2D();
	FHitResult Hit;
	FCollisionQueryParams Q(FName(TEXT("WCEye")), false, P);
	const bool bHit = GetWorld()->LineTraceSingleByChannel(Hit, Eye, Eye + Fwd * 1500.f, ECC_Visibility, Q);
	const float Free = bHit ? Hit.Distance : 1500.f;
	if (Free < 720.f && !bForce) return false;
	EyeSpot = P->GetActorLocation() - FVector(0, 0, 88.f) + Fwd * FMath::Clamp(Free - 80.f, 300.f, 1150.f);
	Set(TEXT("eye_done"));
	bEventBusy = true;
	bEyeLooked = false;
	EyePhase = 1;
	EyeAt = Clock;
	UE_LOG(LogWCEvents, Display, TEXT("WCSCARE t=%.1f S14_eye (%.0f cm of hall ahead)"), PlaySeconds, Free);
	// everything goes: the house and his own light.  No bang; the bulbs just stop.
	KillLights(45.f, false);
	P->SetLightScale(0.f);
	Play2D(TEXT("bulb_die"), 0.4f, EWCSnd::SFX, 0.8f);
	SetLoop(TEXT("amb"), TEXT("amb_house"), 0.03f, 1.2f);
	SetLoop(TEXT("music"), TEXT(""), 0.f, 1.2f);
	Tension = 0.55f;
	return true;
}

void AWCDirector::EyeEnd(bool bSeenTwice)
{
	if (AWCEntity* H = Her()) H->Vanish();
	if (AWCCharacter* P = Player()) P->SetLightScale(1.f);
	SetLoop(TEXT("eye"), TEXT(""), 0.f, 3.f);
	EyePhase = 0;
	bEventBusy = false;
	Rest(170.f);
	Tension = 0.6f;
	ApplyWorldState();
	UE_LOG(LogWCEvents, Display, TEXT("WCSCARE t=%.1f S14_eye over (seen twice %d)"), PlaySeconds, bSeenTwice ? 1 : 0);
	After(2.2f, [this]() { Think(TEXT("Up by the ceiling. It was up by the ceiling.")); });
}

void AWCDirector::TickEye(float Dt)
{
	AWCCharacter* P = Player();
	AWCEntity* H = Her();
	if (!P || !H) return;
	if (EyePhase == 0)
	{
		if (Has(TEXT("eye_done")) || !Has(TEXT("peek_done")) || Has(TEXT("dawn")) || Has(TEXT("sprint_started")) || bBusy || P->IsDown()) return;
		if (EyeNextAt < 0.0) EyeNextAt = Clock + 260.0 * FMath::Max(TestPace, 0.25f);
		if (Clock < EyeNextAt || !Gate()) return;
		if (!EyeTry(false)) EyeNextAt = Clock + 3.0;                 // not a hall: look again in a moment
		return;
	}
	const float T = (float)(Clock - EyeAt);
	const FVector EyePoint = EyeSpot + FVector(0, 0, 252.f);                    // where her eye is, up by the ceiling
	const float Dot = FVector::DotProduct(P->EyeForward(), (EyePoint - P->EyeLocation()).GetSafeNormal());
	auto Show = [this, H, P]()
	{
		H->Appear(EyeSpot, (P->GetActorLocation() - EyeSpot).Rotation().Yaw, TEXT("Tall"));
		H->SetGlow(4.f);
	};
	switch (EyePhase)
	{
	case 1:                     // black.  Nothing at all for a while.
		P->SetLightScale(0.f);
		if (T > 2.8f)
		{
			Show();
			SetLoop(TEXT("eye"), TEXT("music_low"), 0.16f, 4.f, EWCSnd::Music);
			PlayAt(TEXT("her_breath"), EyePoint, 0.45f, 0.75f, 3000.f);
			EyePhase = 2; EyeAt = Clock;
		}
		break;
	case 2:                     // only the eye
		P->SetLightScale(0.f);
		if (T > 2.2f && T - Dt <= 2.2f) PlayAt(TEXT("whisper_far"), EyePoint, 0.35f, 0.9f, 3000.f);
		if (T > 5.0f)
		{
			H->Vanish();                                           // gone in the same instant the light comes back
			P->SetLightScale(1.f);
			P->FlickerLight(0.6f, 0.8f);
			Play2D(TEXT("flashlight_click"), 0.5f);
			EyePhase = 3; EyeAt = Clock;
		}
		break;
	case 3:                     // his light is back, and the hall is empty
		if (Dot > 0.94f) bEyeLooked = true;
		if ((bEyeLooked && Dot < 0.80f && T > 1.5f) || (T > 10.f && Dot < 0.80f))
		{
			Show();                                                // the light is off that spot: it is there again
			PlayAt(TEXT("VO/m_whisper1"), EyePoint, 0.4f, 0.95f, 3000.f);
			EyePhase = 4; EyeAt = Clock;
		}
		else if (T > 18.f) EyeEnd(false);                          // he never looked away: let it go
		break;
	case 4:                     // at the edge of his sight
		if (Dot > 0.86f || T > 6.f) { EyePhase = 5; EyeAt = Clock; }
		break;
	case 5:                     // it goes out in the dark before the light can find it
		H->SetGlow(4.f * FMath::Clamp(1.f - T / 0.3f, 0.f, 1.f));
		if (T > 0.3f) EyeEnd(true);
		break;
	default: break;
	}
}
'''
open(p, "w", encoding="utf-8", newline="\n").write(s)

edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''else if (FParse::Param(FCommandLine::Get(), TEXT("WCTVOnly")))''',
     '''else if (FParse::Param(FCommandLine::Get(), TEXT("WCEyeOnly")))
		{
			Set(TEXT("locked_in")); Set(TEXT("peek_done"));
			AutoSteps.Add({ A_Do, TEXT("at:320,0,92,0,0"), 0.f }); Wait(1.5f); Shot(TEXT("eye_0_hall_before"));
			AutoSteps.Add({ A_Do, TEXT("eye"), 0.f }); Wait(1.8f); Shot(TEXT("eye_1_black"));
			Wait(3.2f); Shot(TEXT("eye_2_the_eye")); Wait(1.6f); Shot(TEXT("eye_2b_the_eye"));
			Wait(2.4f); Shot(TEXT("eye_3_light_back_nothing")); Wait(1.2f);
			AutoSteps.Add({ A_Do, TEXT("at:320,0,92,40,-6"), 0.f }); Wait(1.6f); Shot(TEXT("eye_4_light_away_eye_back")); Wait(1.0f); Shot(TEXT("eye_4b_still_there"));
			AutoSteps.Add({ A_Do, TEXT("at:320,0,92,0,0"), 0.f }); Wait(0.7f); Shot(TEXT("eye_5_gone")); Wait(4.0f); Shot(TEXT("eye_6_after"));
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCTVOnly")))'''),
    ('''else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }''',
     '''else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }
		else if (S.Arg == TEXT("eye")) { bBusy = false; EyeTry(true); }'''),
])
print("pass 84 applied")
