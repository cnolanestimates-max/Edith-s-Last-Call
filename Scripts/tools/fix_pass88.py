"""Pass 88 (Cheyenne, 06:05 to 06:07 UTC, after watching a run):
  - the flashlight: far weaker and far shorter ("visibility maybe 5 foot in front of you ... everything else needs to be dark")
  - so that the far scares still read, she carries a faint cold light of her own while she is beyond the flashlight
  - the first peek: no glow, no far light; she is only there when he is already close, and she slides away the moment
    his light is on her
  - the television: already on when he first comes in; he has to crouch right up to it to switch it off, and nothing
    happens.  About the middle of the game (after the head by the ceiling) it is on again, and switching it off (crouched,
    close) is when she is in the glass.  No camera takeover.
  - the eye in the dark waits until after the long hall"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

# ---------------------------------------------------------------- flashlight
edit(R + "Source/WellnessCheck/WCCharacter.h", [
    ('float FlashLumens = 980.f;', 'float FlashLumens = 150.f;       // Cheyenne: about five feet of sight, the rest black (was 980 with a 26 m reach)'),
])
edit(R + "Source/WellnessCheck/WCCharacter.cpp", [
    ('Flash->SetAttenuationRadius(2600.f);', 'Flash->SetAttenuationRadius(390.f);'),
    ('Spill->SetAttenuationRadius(900.f);', 'Spill->SetAttenuationRadius(300.f);'),
    ('''Fill->SetIntensity(2.2f);
	Fill->SetAttenuationRadius(520.f);''', '''Fill->SetIntensity(1.2f);
	Fill->SetAttenuationRadius(260.f);'''),
])

# ---------------------------------------------------------------- her own faint light at a distance
edit(R + "Source/WellnessCheck/WCEntity.h", [
    ('void SetGlow(float Lumens);', '''void SetGlow(float Lumens);
	/** A faint cold light she carries while she is beyond the reach of his flashlight (0 = none: she is only found close to). */
	void SetFarGlow(float Lumens) { FarGlow = Lumens; }
	static constexpr float DefaultFarGlow = 320.f;
	float FarGlow = DefaultFarGlow;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> FarLight;'''),
])
edit(R + "Source/WellnessCheck/WCEntity.cpp", [
    ('''EyeGlint->SetCastShadows(false);''', '''EyeGlint->SetCastShadows(false);
	FarLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("FarLight"));
	FarLight->SetupAttachment(Root);
	FarLight->SetRelativeLocation(FVector(80.f, 0.f, 160.f));
	FarLight->SetIntensityUnits(ELightUnits::Lumens);
	FarLight->SetIntensity(0.f);
	FarLight->SetAttenuationRadius(460.f);
	FarLight->SetLightColor(FLinearColor(0.72f, 0.82f, 1.f));
	FarLight->SetCastShadows(false);'''),
    ('''Super::Tick(Dt);
	if (!bShown) return;
	{''', '''Super::Tick(Dt);
	if (!bShown) return;
	// beyond his flashlight she is a pale shape in the dark; inside it, his light does the work
	FarLight->SetIntensity(FarGlow * FMath::Clamp((DistToPlayer() - 230.f) / 260.f, 0.f, 1.f));
	{'''),
    ('''EyeGlint->SetIntensity(0.f);
	if (IrisMID)''', '''EyeGlint->SetIntensity(0.f);
	FarLight->SetIntensity(0.f);
	FarGlow = DefaultFarGlow;
	if (IrisMID)'''),
])

# ---------------------------------------------------------------- the first peek
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''H->Appear(Pos(TEXT("Her_Peek")), YawOf(TEXT("Her_Peek")), TEXT("Peek"));
	H->SetGlow(0.8f);''', '''H->Appear(Pos(TEXT("Her_Peek")), YawOf(TEXT("Her_Peek")), TEXT("Peek"));
	H->SetGlow(0.2f);
	H->SetFarGlow(0.f);                 // barely there: only his own light, close to, finds her'''),
    ('''if (PlayerSees(H->HeadLocation(), 0.80f, 1600.f)) Seen += Dt;
		const double Waited = Clock - Started;
		if (Waited > 9.0 && !Has(TEXT("peek_whisper"))) { Set(TEXT("peek_whisper")); Say(TEXT("m_whisper1")); }
		if (Seen > 1.25 || H->DistToPlayer() < 380.f || Waited > 26.0)
		{
			Set(TEXT("peek_leaving"));
			if (Seen > 0.2) Play2D(TEXT("sting_soft"), 0.8f, EWCSnd::Music);
			H->Slide(Pos(TEXT("Her_PeekBack")), 0.85f, [this]()''',
     '''// "as soon as your light hits her, she goes poof": lit means inside the beam and inside its short reach
		AWCCharacter* Pk = Player();
		if (Pk && Pk->IsFlashlightOn() && PlayerSees(H->HeadLocation(), 0.86f, 360.f)) Seen += Dt;
		const double Waited = Clock - Started;
		if (Waited > 9.0 && !Has(TEXT("peek_whisper"))) { Set(TEXT("peek_whisper")); Say(TEXT("m_whisper1")); }
		if (Seen > 0.16 || H->DistToPlayer() < 210.f || Waited > 45.0)
		{
			Set(TEXT("peek_leaving"));
			if (Seen > 0.1) Play2D(TEXT("sting_soft"), 0.8f, EWCSnd::Music);
			H->Slide(Pos(TEXT("Her_PeekBack")), 0.5f, [this]()'''),
])

# ---------------------------------------------------------------- the television
edit(R + "Source/WellnessCheck/WCEvents.cpp", [
    # crouch right up to it to switch it off
    ('''if (TVPhase == 1) TVOff(true);
		else if (TVPhase == 0) Think(''', '''if (TVPhase == 1)
		{
			AWCCharacter* Pl = Player();
			AWCInteractable* Tv = Thing(TEXT("tv"));
			const bool bClose = Pl && Tv && FVector::Dist2D(Pl->GetActorLocation(), Tv->GetActorLocation()) < 175.f;
			if (Pl && Pl->bIsCrouched && bClose) TVOff(true);
			else
			{
				Think(TEXT("The switch is low on the front. I have to get right down to it."));
				ShowHint(TEXT("C: crouch, close to the set, then E to switch it off"), 6.f);
			}
		}
		else if (TVPhase == 0) Think('''),
    ('''if (!Has(TEXT("tv_seen"))) { Set(TEXT("tv_seen")); After(2.5f, [this]() { Think(TEXT("That set was not on.")); }); }''',
     '''if (!Has(TEXT("tv_seen"))) Set(TEXT("tv_seen"));
	else if (!Has(TEXT("tv_again"))) { Set(TEXT("tv_again")); After(2.5f, [this]() { Think(TEXT("I switched that off.")); }); }'''),
    # the first time he switches it off nothing happens; she is in the glass from the second showing on
    ('''const bool bScare = P && (bForceScare || (bByHim && !Has(TEXT("tv_scare")) && Clock >= NextScareAt''',
     '''const bool bScare = P && (bForceScare || (bByHim && TVTape >= 2 && !Has(TEXT("tv_scare")) && Clock >= NextScareAt'''),
    ('''if (!Has(TEXT("locked_in")) || Has(TEXT("dawn")) || Has(TEXT("sprint_started"))) return;
		if (TVNextAt < 0.0) TVNextAt = Clock + 150.0 * FMath::Max(TestPace, 0.25f);
		// he is near enough to see it come on, and nothing else is happening
		if (Clock >= TVNextAt''', '''if (Has(TEXT("dawn")) || Has(TEXT("sprint_started"))) return;
		// already on when he first comes in ("he turns it off, but that's the first time and nothing happens")
		if (Has(TEXT("inside")) && !Has(TEXT("tv_first"))) { Set(TEXT("tv_first")); TVOn(); After(6.f, [this]() { Think(TEXT("Somebody left the television on.")); }); return; }
		// the second time is about the middle of the game: not before the head by the ceiling
		if (!Has(TEXT("ceiling_done")) && !Has(TEXT("tv_test"))) { TVNextAt = -1.0; return; }
		if (TVNextAt < 0.0) TVNextAt = Clock + 100.0 * FMath::Max(TestPace, 0.25f);
		// he is near enough to see it come on, and nothing else is happening
		if (Clock >= TVNextAt'''),
    # the first showing plays until he deals with it (a long while); later ones a minute
    ('''if (TVAudio.IsValid() && !TVAudio->IsPlaying() && T < 58.f) TVAudio->Play();          // the tape comes round again
		if (T > 60.f) TVOff(false);''', '''const float Runs = TVTape <= 1 ? 420.f : 75.f;
		if (TVAudio.IsValid() && !TVAudio->IsPlaying() && T < Runs - 2.f) TVAudio->Play();          // the tape comes round again
		if (T > Runs) TVOff(false);'''),
    ('''H->Appear(Far, (P->GetActorLocation() - Far).Rotation().Yaw, TEXT("Idle"));
		TInlineComponentArray<UPrimitiveComponent*> Prims(H);''', '''H->Appear(Far, (P->GetActorLocation() - Far).Rotation().Yaw, TEXT("Idle"));
		H->SetFarGlow(0.f);
		TInlineComponentArray<UPrimitiveComponent*> Prims(H);'''),
    # S14
    ('''H->Appear(EyeSpot, (P->GetActorLocation() - EyeSpot).Rotation().Yaw, TEXT("Tall"));
		H->SetGlow(bDark ? 55.f : 2.5f);''', '''H->Appear(EyeSpot, (P->GetActorLocation() - EyeSpot).Rotation().Yaw, TEXT("Tall"));
		H->SetFarGlow(0.f);
		H->SetGlow(bDark ? 55.f : 2.5f);'''),
    ('''if (Has(TEXT("eye_done")) || !Has(TEXT("peek_done")) ||''', '''if (Has(TEXT("eye_done")) || !Has(TEXT("lockin_done")) ||'''),
])

# ---------------------------------------------------------------- tests
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''else if (FParse::Param(FCommandLine::Get(), TEXT("WCEyeOnly")))
		{
			Set(TEXT("locked_in")); Set(TEXT("peek_done"));''', '''else if (FParse::Param(FCommandLine::Get(), TEXT("WCPeekOnly")))
		{
			// the first sight of her, from the stairs (nothing), from half way (nothing or next to nothing), and close (gone)
			Set(TEXT("locked_in")); Set(TEXT("heard_upstairs")); Set(TEXT("tv_first"));
			AutoSteps.Add({ A_Tele, TEXT("A_StairsTop"), 0.f }); Wait(1.0f);
			AutoSteps.Add({ A_Do, TEXT("peek"), 0.f }); Wait(1.2f);
			AutoSteps.Add({ A_Do, TEXT("at:900,60,442,174,2"), 0.f }); Wait(1.0f); Shot(TEXT("peek_1_from_the_stairs"));
			AutoSteps.Add({ A_Do, TEXT("at:640,80,442,165,4"), 0.f }); Wait(1.0f); Shot(TEXT("peek_2_from_4m"));
			AutoSteps.Add({ A_Do, TEXT("at:520,90,442,160,5"), 0.f }); Wait(0.12f); Shot(TEXT("peek_3_from_3m_first_instant")); Wait(0.35f); Shot(TEXT("peek_4_sliding_away")); Wait(1.2f); Shot(TEXT("peek_5_gone"));
			Wait(3.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCEyeOnly")))
		{
			Set(TEXT("locked_in")); Set(TEXT("peek_done")); Set(TEXT("lockin_done")); Set(TEXT("tv_first"));'''),
    ('''else if (FParse::Param(FCommandLine::Get(), TEXT("WCTVOnly")))
		{
			Set(TEXT("locked_in"));''', '''else if (FParse::Param(FCommandLine::Get(), TEXT("WCTVOnly")))
		{
			Set(TEXT("locked_in")); Set(TEXT("tv_first")); Set(TEXT("tv_test"));'''),
    ('''AutoSteps.Add({ A_Tele, TEXT("A_Living"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("tv"), 0.f }); Wait(0.6f);
			if (FParse::Param(FCommandLine::Get(), TEXT("WCTVDebug")))''', '''AutoSteps.Add({ A_Do, TEXT("at:366,-420,92,-90,-8"), 0.f }); Wait(0.5f); AutoSteps.Add({ A_Crouch, NAME_None, 1.f }); Wait(0.8f);
			AutoSteps.Add({ A_Look, TEXT("tv"), 0.f }); Wait(0.6f); Shot(TEXT("tv_4b_crouched_at_the_set"));
			if (FParse::Param(FCommandLine::Get(), TEXT("WCTVDebug")))'''),
    ('''else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }''',
     '''else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }
		else if (S.Arg == TEXT("peek")) { bBusy = false; ScarePeek(); }'''),
])
print("pass 88 applied")
