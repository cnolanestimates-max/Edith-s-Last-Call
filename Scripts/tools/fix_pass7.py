import io
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"


def sub(f, old, new, count=1):
    s = io.open(R + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(R + f, "w", encoding="utf-8", newline="\n").write(s)


# ================================================================ A. pace: a slow, careful walk
sub("WCCharacter.h", "	UPROPERTY(EditAnywhere, Category = \"WC\") float WalkSpeed = 185.f;", "	UPROPERTY(EditAnywhere, Category = \"WC\") float WalkSpeed = 112.f;")
sub("WCCharacter.h", "	UPROPERTY(EditAnywhere, Category = \"WC\") float SprintSpeed = 330.f;", "	UPROPERTY(EditAnywhere, Category = \"WC\") float SprintSpeed = 215.f;")
sub("WCCharacter.h", "	UPROPERTY(EditAnywhere, Category = \"WC\") float CrouchSpeed = 95.f;", "	UPROPERTY(EditAnywhere, Category = \"WC\") float CrouchSpeed = 70.f;")
sub("WCCharacter.cpp", "		const float Stride = bIsCrouched ? 55.f : (Speed > WalkSpeed * 1.3f ? 105.f : 78.f);", "		const float Stride = bIsCrouched ? 50.f : (Speed > WalkSpeed * 1.3f ? 92.f : 66.f);")
sub("WCCharacter.cpp", "	if (Speed > 10.f && M->IsMovingOnGround()) BobTime += Dt * Speed / 46.f;", "	if (Speed > 10.f && M->IsMovingOnGround()) BobTime += Dt * Speed / 36.f;")

# ================================================================ B. the deputy says less; small on-screen text does the rest
sub("WCStory.cpp", '''float AWCDirector::Say(FName LineId, float Delay)
{''', '''// Lines that are no longer spoken (Cheyenne: he talks to dispatch and reacts to her, not to every locked door).
static bool IsMuted(FName Id)
{
	static const TSet<FName> Muted = { TEXT("d_locked"), TEXT("d_cellar_locked"), TEXT("d_window"), TEXT("d_backdoor"), TEXT("d_table"), TEXT("d_photos"),
		TEXT("d_foyer"), TEXT("d_wayout"), TEXT("d_drawer"), TEXT("d_sitting"), TEXT("d_kidsdoor"), TEXT("d_musicbox"), TEXT("d_prayer"), TEXT("d_ring"),
		TEXT("d_attic"), TEXT("d_after_attic"), TEXT("d_cellar"), TEXT("d_shelf"), TEXT("d_dawn"), TEXT("d_need"), TEXT("d_leave_early"), TEXT("d_phone_ring") };
	return Muted.Contains(Id);
}

void AWCDirector::Think(const FString& Text, float Seconds)
{
	FWCSubtitle Sub;
	Sub.Text = Text;
	Sub.Until = Clock + (Seconds > 0.f ? Seconds : 2.2f + 0.055f * Text.Len());
	Subtitles.Reset();
	Subtitles.Add(Sub);
}

float AWCDirector::Say(FName LineId, float Delay)
{
	if (IsMuted(LineId)) return Delay;''')
sub("WCDirector.h", "	float LineSeconds(FName LineId);", "	float LineSeconds(FName LineId);\n	/** A line of on-screen text with no voice: what he notices. */\n	void Think(const FString& Text, float Seconds = -1.f);\n	bool Gate() const { return Clock >= NextScareAt; }\n	void Rest(float Seconds) { NextScareAt = FMath::Max(NextScareAt, Clock + Seconds); }\n	double NextScareAt = 0.0;\n	float LockInDist0 = 0.f;\n	bool bLockInRun = false;\n	double UpstairsAt = -1.0;")
sub("WCStory.cpp", '''		if (!Has(TEXT("dawn")) && Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 12.0; Say(TEXT("d_leave_early")); }''',
    '''		if (!Has(TEXT("dawn")) && Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 12.0; Think(TEXT("Not until I've laid eyes on her.")); }''')
sub("WCStory.cpp", '''		else if (Has(TEXT("lockin_done")) && Clock > SpeechFreeAt)
		{
			SpeechFreeAt = Clock + 8.0;
			Say(TEXT("d_locked"));
		}''', '''		else if (Clock > SpeechFreeAt)
		{
			SpeechFreeAt = Clock + 4.0;
			Think(TEXT("It will not open."));
		}''')
sub("WCStory.cpp", '''	if (Is(Id, TEXT("locked:cellar"))) { if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 8.0; Say(TEXT("d_cellar_locked")); } return; }''',
    '''	if (Is(Id, TEXT("locked:cellar"))) { if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Think(TEXT("Padlocked from this side. The cellar.")); } return; }''')
sub("WCStory.cpp", '''		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 6.0; Say(TEXT("d_locked")); }
		return;
	}
	if (Id.ToString().StartsWith(TEXT("use:window")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 6.0; Say(TEXT("d_window")); }
		return;
	}''', '''		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 3.0; Think(TEXT("Locked.")); }
		return;
	}
	if (Id.ToString().StartsWith(TEXT("use:window")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Think(TEXT("Nailed shut. From the inside.")); }
		return;
	}''')
sub("WCStory.cpp", '''		if (!Has(TEXT("lockin_done"))) { if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 8.0; Say(TEXT("d_backdoor")); } return; }
		if (!Has(TEXT("backdoor_tried")))
		{
			Set(TEXT("backdoor_tried"));
			float T = Say(TEXT("d_backdoor"));
			After(T + 2.5f, [this]()
			{
				Set(TEXT("phone_ringing"));
				if (UAudioComponent* A = PlayAt(TEXT("phone_ring"), Pos(TEXT("PhonePoint")), 1.f)) { A->ComponentTags.Add(TEXT("ring")); }
				if (AWCInteractable* Ph = Thing(TEXT("phone"))) Ph->Prompt = TEXT("Answer");
				Say(TEXT("d_phone_ring"), 2.4f);
				SetObjective(TEXT("Answer the phone"));
			});
		}
		else if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 8.0; Say(TEXT("d_backdoor")); }
		return;''', '''		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Think(TEXT("Nailed shut from the inside. Every board.")); }
		if (Has(TEXT("lockin_done"))) Set(TEXT("backdoor_tried"));      // the phone rings later, when things have gone quiet (StoryTick)
		return;''')
sub("WCStory.cpp", '''			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 6.0; Say(TEXT("d_need")); }''', '''			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Think(TEXT("Not yet. She needs what was theirs. All three.")); }''')

# ================================================================ C. pacing: nothing is seen until the house has been walked; scares rest between each other
# the thump upstairs needs the kitchen AND some real looking around
sub("WCStory.cpp", '''	if (Is(Id, TEXT("trig:t_kitchen")) && !Has(TEXT("heard_upstairs")) && Has(TEXT("inside")))
	{
		Set(TEXT("heard_upstairs"));''', '''	if (Is(Id, TEXT("trig:t_kitchen"))) Set(TEXT("seen_kitchen"));
	if ((Is(Id, TEXT("trig:t_kitchen")) || Is(Id, TEXT("trig:t_foyer")) || Is(Id, TEXT("trig:t_living")) || Is(Id, TEXT("trig:t_dining")) || Is(Id, TEXT("trig:t_sitting")))
		&& !Has(TEXT("heard_upstairs")) && Has(TEXT("inside")) && Has(TEXT("seen_kitchen")) && Has(TEXT("seen_living")) && Has(TEXT("seen_dining"))
		&& (NotesRead.Num() >= 4 || PlaySeconds - InsideAt > 420.f) && PlaySeconds - InsideAt > 150.f)
	{
		Set(TEXT("heard_upstairs"));''')
sub("WCDirector.h", "	double UpstairsAt = -1.0;", "	double UpstairsAt = -1.0;\n	float InsideAt = 0.f;")
sub("WCStory.cpp", '''			Set(TEXT("inside"));
			ApplyWorldState();''', '''			Set(TEXT("inside"));
			InsideAt = PlaySeconds;
			ApplyWorldState();''')
# S1: not at the top of the stairs. She is at the bedroom door when you come along the corridor, after you have had time up here.
sub("WCStory.cpp", '''	if (Is(Id, TEXT("trig:t_up_landing")))
	{
		if (Has(TEXT("heard_upstairs")) && !Has(TEXT("peek_started"))) ScarePeek();
		else if (HasItem(TEXT("key_prayer")) && Has(TEXT("peek_done")) && !Has(TEXT("ceiling_started"))) ScareCeiling();
		return;
	}''', '''	if (Is(Id, TEXT("trig:t_up_landing")))
	{
		if (Has(TEXT("heard_upstairs")) && UpstairsAt < 0.0) { UpstairsAt = Clock; Tension = 0.35f; }
		if (HasItem(TEXT("key_prayer")) && Has(TEXT("peek_done")) && !Has(TEXT("ceiling_started")) && Gate()) ScareCeiling();
		return;
	}
	if (Is(Id, TEXT("trig:t_up_corridor")))
	{
		if (Has(TEXT("heard_upstairs")) && !Has(TEXT("peek_started")) && UpstairsAt > 0.0 && Clock - UpstairsAt > 45.0) ScarePeek();
		return;
	}''')
# rests after each scare
sub("WCStory.cpp", '''				Set(TEXT("peek_done"));''', '''				Set(TEXT("peek_done"));
				Rest(150.f);''')
sub("WCStory.cpp", '''			Set(TEXT("lockin_done"));''', '''			Set(TEXT("lockin_done"));
			Rest(200.f);''')
sub("WCStory.cpp", '''			Set(TEXT("ceiling_done"));''', '''			Set(TEXT("ceiling_done"));
			Rest(120.f);''')
# the phone waits for quiet
sub("WCStory.cpp", '''	if (!H) return;

	// ---- S1: the peek is watching you back''', '''	if (Has(TEXT("backdoor_tried")) && !Has(TEXT("phone_ringing")) && !Has(TEXT("phone_done")) && Gate() && P->GetActorLocation().Z < 200.f && P->GetActorLocation().Z > -50.f)
	{
		Set(TEXT("phone_ringing"));
		if (UAudioComponent* A = PlayAt(TEXT("phone_ring"), Pos(TEXT("PhonePoint")), 1.f)) { A->ComponentTags.Add(TEXT("ring")); }
		if (AWCInteractable* Ph = Thing(TEXT("phone"))) { Ph->Prompt = TEXT("Answer"); Ph->bEnabled = true; }
		After(3.f, [this]() { Think(TEXT("That phone has no line.")); });
		SetObjective(TEXT("Answer the phone"));
	}
	if (!H) return;

	// ---- S1: the peek is watching you back''')

# ================================================================ D. S3: she walks only halfway, then she runs
sub("WCStory.cpp", '''			const double Elapsed = Clock - LockInStart;
			TArray<FVector> Pts; Pts.Add(FVector(P->GetActorLocation().X, P->GetActorLocation().Y, H->GetActorLocation().Z));
			H->MoveAlong(Pts, Elapsed > 30.0 ? 420.f : 78.f, Elapsed > 30.0 ? TEXT("Run") : TEXT("Walk"));''',
    '''			const double Elapsed = Clock - LockInStart;
			if (LockInDist0 <= 0.f) LockInDist0 = H->DistToPlayer();
			if (!bLockInRun && (H->DistToPlayer() < LockInDist0 * 0.52f || Elapsed > 26.0))
			{
				// halfway: she stops being slow
				bLockInRun = true;
				Play2D(TEXT("her_scream"), 1.f);
				Play2D(TEXT("sting_rise"), 0.9f, EWCSnd::Music);
				P->FlickerLight(1.2f, 0.85f);
				P->AddShake(0.5f);
			}
			TArray<FVector> Pts; Pts.Add(FVector(P->GetActorLocation().X, P->GetActorLocation().Y, H->GetActorLocation().Z));
			H->MoveAlong(Pts, bLockInRun ? 660.f : 62.f, bLockInRun ? TEXT("Run") : TEXT("Walk"));''')
sub("WCStory.cpp", '''			HerNextStep = Clock + 0.4;''', '''			HerNextStep = Clock + (bLockInRun ? 0.15 : 0.4);''')
sub("WCStory.cpp", '''			bLockInActive = true;
			LockInStart = Clock;''', '''			bLockInActive = true;
			bLockInRun = false;
			LockInDist0 = 0.f;
			LockInStart = Clock;''')
sub("WCStory.cpp", '''			bLockInActive = false;
			bBusy = true;
			Play2D(TEXT("her_scream"), 1.f);''', '''			bLockInActive = false;
			bBusy = true;
			if (!bLockInRun) Play2D(TEXT("her_scream"), 1.f);''')
# lock-in waits for the rest period if it is still running: the door is simply stuck first
sub("WCStory.cpp", '''		else if (Has(TEXT("want_leave")) && !Has(TEXT("lockin_started")))
		{
			ScareLockIn();
		}''', '''		else if (Has(TEXT("want_leave")) && !Has(TEXT("lockin_started")))
		{
			if (!Has(TEXT("door_stuck"))) { Set(TEXT("door_stuck")); Say(TEXT("d_doorstuck")); }
			else if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Think(TEXT("It will not open.")); }
		}''')
sub("WCStory.cpp", '''		else if (Has(TEXT("want_leave")) && !Has(TEXT("lockin_started")) && !Has(TEXT("lockin_armed")))
		{
			// reached the front hall on the way out; if they never touch the door she comes anyway
			Set(TEXT("lockin_armed"));
			After(7.f, [this]() { if (!Has(TEXT("lockin_started"))) ScareLockIn(); });
		}''', '''		else if (Has(TEXT("want_leave")) && !Has(TEXT("lockin_started")) && Has(TEXT("door_stuck")) && Gate())
		{
			ScareLockIn();        // back in the front hall after finding the door stuck: now she comes
		}''')
sub("WCStory.cpp", '''	Set(TEXT("lockin_started"));
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S3_lockin"), PlaySeconds);
	ShotsAtHer = 0;
	float T = Say(TEXT("d_doorstuck"));
	After(T + 0.6f, [this]()''', '''	Set(TEXT("lockin_started"));
	UE_LOG(LogWCStory, Display, TEXT("WCSCARE t=%.1f S3_lockin"), PlaySeconds);
	ShotsAtHer = 0;
	After(1.0f, [this]()''')
print("ok")
