import io
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"


def sub(f, old, new, count=1):
    s = io.open(R + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(R + f, "w", encoding="utf-8", newline="\n").write(s)


# ================================================================ things you can look at: a line of what he notices, no voice
sub("WCWorld.h", '''/** Anything else you press E on. Raises the story event "use:<WCId>". */''', '''/** Something to look at. Shows a line of on-screen text (no voice) and raises "look:<WCId>". */
UCLASS()
class WELLNESSCHECK_API AWCLook : public AWCInteractable
{
	GENERATED_BODY()
public:
	AWCLook();
	virtual void Interact(AWCCharacter* By) override;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC", meta = (MultiLine = true)) FString Text;
};

/** Anything else you press E on. Raises the story event "use:<WCId>". */''')
sub("WCWorld.cpp", '''void AWCUsable::Interact(AWCCharacter* By)''', '''AWCLook::AWCLook()
{
	Prompt = TEXT("Look");
	Mesh->SetCollisionProfileName(TEXT("NoCollision"));
}

void AWCLook::Interact(AWCCharacter* By)
{
	if (AWCDirector* D = AWCDirector::Get(this))
	{
		D->Think(Text);
		D->Event(FName(*FString::Printf(TEXT("look:%s"), *WCId.ToString())));
	}
}

void AWCUsable::Interact(AWCCharacter* By)''')

# ================================================================ test pace switch (-WCFast shortens rests so the bot does not have to wait minutes)
sub("WCDirector.h", "	void Rest(float Seconds) { NextScareAt = FMath::Max(NextScareAt, Clock + Seconds); }", "	void Rest(float Seconds) { NextScareAt = FMath::Max(NextScareAt, Clock + Seconds * TestPace); }\n	float TestPace = 1.f;")
sub("WCDirector.cpp", '''	bAuto = FParse::Param(FCommandLine::Get(), TEXT("WCAuto")) || FParse::Param(FCommandLine::Get(), TEXT("WCTour"));''',
    '''	bAuto = FParse::Param(FCommandLine::Get(), TEXT("WCAuto")) || FParse::Param(FCommandLine::Get(), TEXT("WCTour")) || FParse::Param(FCommandLine::Get(), TEXT("WCHerLook")) || FParse::Param(FCommandLine::Get(), TEXT("WCItems"));
	if (FParse::Param(FCommandLine::Get(), TEXT("WCFast"))) TestPace = 0.08f;''')
sub("WCStory.cpp", "		&& (NotesRead.Num() >= 4 || PlaySeconds - InsideAt > 420.f) && PlaySeconds - InsideAt > 150.f)", "		&& (NotesRead.Num() >= 4 || PlaySeconds - InsideAt > 420.f * TestPace) && PlaySeconds - InsideAt > 150.f * TestPace)")
sub("WCStory.cpp", "UpstairsAt > 0.0 && Clock - UpstairsAt > 45.0) ScarePeek();", "UpstairsAt > 0.0 && Clock - UpstairsAt > 45.0 * TestPace) ScarePeek();")

# ================================================================ ambience: the house is never silent
s = io.open(R + "WCStory.cpp", encoding="utf-8").read()
a = s.index("	// ---- random house noises")
b = s.index("	if (Has(TEXT(\"backdoor_tried\")) && !Has(TEXT(\"phone_ringing\"))")
new = '''	// ---- the house is never silent: things in the walls, boards, wind, something moving on another floor
	if (Has(TEXT("inside")) && !Has(TEXT("dawn")) && !bBusy && Clock > NextCue)
	{
		NextCue = Clock + Rng.FRandRange(5.f, 13.f) * (1.25f - 0.6f * Tension);
		struct FCue { const TCHAR* Name; float Weight; float Near; float Far; float Vol; int32 Where; };   // Where: 0 around, 1 other floor, 2 in a wall close by
		static const FCue Cues[] = {
			{ TEXT("creak"), 3.f, 300.f, 900.f, 0.9f, 0 }, { TEXT("skitter"), 3.f, 150.f, 500.f, 0.9f, 2 }, { TEXT("scratch_wall"), 2.2f, 200.f, 600.f, 0.9f, 2 },
			{ TEXT("knock_far"), 1.2f, 600.f, 1200.f, 0.9f, 0 }, { TEXT("thump_far"), 1.4f, 500.f, 1200.f, 1.f, 1 }, { TEXT("house_groan"), 2.f, 500.f, 1200.f, 1.f, 0 },
			{ TEXT("steps_above"), 1.3f, 100.f, 500.f, 1.f, 1 }, { TEXT("wind_gust"), 1.6f, 800.f, 1400.f, 0.8f, 0 }, { TEXT("door_far"), 0.8f, 700.f, 1300.f, 0.9f, 1 },
			{ TEXT("whisper_far"), 0.7f, 400.f, 900.f, 0.8f, 0 }, { TEXT("breath_near"), 0.35f, 90.f, 160.f, 0.7f, 0 } };
		float Total = 0.f;
		for (const FCue& C : Cues) Total += C.Weight * (FCString::Strcmp(C.Name, TEXT("breath_near")) == 0 || FCString::Strcmp(C.Name, TEXT("whisper_far")) == 0 ? (0.3f + 2.f * Tension) : 1.f);
		float Pick = Rng.FRandRange(0.f, Total);
		const FCue* Chosen = &Cues[0];
		for (const FCue& C : Cues)
		{
			const float W = C.Weight * (FCString::Strcmp(C.Name, TEXT("breath_near")) == 0 || FCString::Strcmp(C.Name, TEXT("whisper_far")) == 0 ? (0.3f + 2.f * Tension) : 1.f);
			if (Pick <= W) { Chosen = &C; break; }
			Pick -= W;
		}
		FVector Off = FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * Rng.FRandRange(Chosen->Near, Chosen->Far);
		if (Chosen->Where == 1) Off.Z = (P->GetActorLocation().Z > 500.f ? -1.f : 1.f) * 330.f;
		else if (Chosen->Where == 2) Off.Z = Rng.FRandRange(-60.f, 120.f);
		else Off.Z = Rng.FRandRange(-80.f, 200.f);
		PlayAt(Chosen->Name, P->GetActorLocation() + Off, Chosen->Vol * Rng.FRandRange(0.75f, 1.f), Rng.FRandRange(0.92f, 1.07f));
	}
	if (FLoop* Drone = Loops.Find(TEXT("drone"))) Drone->Target = Has(TEXT("inside")) && !Has(TEXT("dawn")) ? 0.5f + 0.4f * Tension : 0.f;
	if (FLoop* Low = Loops.Find(TEXT("low"))) Low->Target = Has(TEXT("inside")) && !Has(TEXT("dawn")) ? 0.25f + 0.55f * Tension : 0.f;
	// tension eases back toward a floor that rises as the night goes on
	{
		const float Floor = Has(TEXT("sprint_done")) ? 0.6f : (Has(TEXT("lockin_done")) ? 0.45f : (Has(TEXT("peek_done")) ? 0.3f : (Has(TEXT("heard_upstairs")) ? 0.2f : 0.08f)));
		Tension = FMath::FInterpConstantTo(Tension, Floor, Dt, 0.012f);
	}

'''
s = s[:a] + new + s[b:]
s = s.replace('''	SetLoop(TEXT("amb"), Has(TEXT("dawn")) ? TEXT("amb_dawn") : (bCellar ? TEXT("amb_cellar") : (bIn ? TEXT("amb_house") : TEXT("amb_night"))), 0.6f, 3.f);
	SetLoop(TEXT("drone"), bIn ? TEXT("music_drone") : TEXT(""), 0.f, 3.f, EWCSnd::Music);''',
              '''	SetLoop(TEXT("amb"), Has(TEXT("dawn")) ? TEXT("amb_dawn") : (bCellar ? TEXT("amb_cellar") : (bIn ? TEXT("amb_house") : TEXT("amb_night"))), 1.f, 3.f);
	SetLoop(TEXT("drone"), bIn ? TEXT("music_drone") : TEXT(""), bIn ? 0.5f : 0.f, 4.f, EWCSnd::Music);
	SetLoop(TEXT("low"), bIn ? TEXT("music_low") : TEXT(""), bIn ? 0.25f : 0.f, 6.f, EWCSnd::Music);''')
io.open(R + "WCStory.cpp", "w", encoding="utf-8", newline="\n").write(s)
sub("WCDirector.cpp", '''		SetLoop(TEXT("amb"), TEXT("amb_night"), 0.55f, 2.f);
		SetLoop(TEXT("music"), TEXT("music_menu"), 0.5f, 4.f, EWCSnd::Music);''', '''		SetLoop(TEXT("amb"), TEXT("amb_night"), 0.9f, 2.f);
		SetLoop(TEXT("music"), TEXT("music_menu"), 0.7f, 4.f, EWCSnd::Music);''')

# ================================================================ bot: her look test (-WCHerLook) and item inspection sheet (-WCItems)
s = io.open(R + "WCAuto.cpp", encoding="utf-8").read()
s = s.replace("enum { A_Go, A_Use, A_Wait, A_WaitFlag, A_Shot, A_Fire, A_Look, A_Light, A_LookHer, A_WaitHer, A_Crouch, A_Tele };",
              "enum { A_Go, A_Use, A_Wait, A_WaitFlag, A_Shot, A_Fire, A_Look, A_Light, A_LookHer, A_WaitHer, A_Crouch, A_Tele, A_Her, A_FaceItem };")
a = s.index("	// ---- arrival\n	Wait(5.f);")
new = '''	if (FParse::Param(FCommandLine::Get(), TEXT("WCHerLook")) || FParse::Param(FCommandLine::Get(), TEXT("WCItems")))
	{
		Steps.Reset();
		Subtitles.Reset();
		Set(TEXT("inside")); Set(TEXT("heard_upstairs")); Set(TEXT("peek_started")); Set(TEXT("peek_done")); Set(TEXT("briefed"));
		bBusy = true;                      // no story triggers during the test
		if (AWCCharacter* Pl = Player()) { Pl->SetInputLocked(false); Pl->SetFlashlight(true, false); }
		Fade = 0.f; FadeTarget = 0.f;
		Wait(4.f);
		if (FParse::Param(FCommandLine::Get(), TEXT("WCHerLook")))
		{
			AutoSteps.Add({ A_Tele, TEXT("Nav_foyer"), 0.f });
			Wait(1.f);
			static const TCHAR* Clips[] = { TEXT("Idle"), TEXT("Walk"), TEXT("Run"), TEXT("Tall"), TEXT("Peek"), TEXT("Crawl"), TEXT("Sit") };
			for (const TCHAR* Cn : Clips)
			{
				AutoSteps.Add({ A_Her, Cn, 330.f });
				Wait(0.8f); AutoSteps.Add({ A_LookHer, NAME_None, 0.3f }); Shot(*FString::Printf(TEXT("her_%s_a"), Cn));
				Wait(0.35f); Shot(*FString::Printf(TEXT("her_%s_b"), Cn));
			}
			AutoSteps.Add({ A_Her, TEXT("Idle"), 105.f });
			Wait(0.8f); AutoSteps.Add({ A_LookHer, NAME_None, 0.6f }); Shot(TEXT("her_face_close"));
			AutoSteps.Add({ A_Her, TEXT("Tall"), 150.f });
			Wait(0.8f); AutoSteps.Add({ A_LookHer, NAME_None, 0.6f }); Shot(TEXT("her_tall_close"));
			AutoSteps.Add({ A_Fire, NAME_None, 0.f }); Wait(1.2f); Shot(TEXT("gun_up"));
			AutoSteps.Add({ A_Tele, TEXT("Nav_yard"), 0.f }); Wait(1.5f); AutoSteps.Add({ A_Look, TEXT("Cruiser"), 0.f }); Wait(1.f); Shot(TEXT("cruiser"));
		}
		else
		{
			TArray<FName> Ids;
			for (TActorIterator<AWCInteractable> It(GetWorld()); It; ++It) if (!It->WCId.IsNone() && !It->IsA(AWCDoor::StaticClass())) Ids.Add(It->WCId);
			Ids.Sort([](const FName& A, const FName& B) { return A.ToString() < B.ToString(); });
			for (const FName& Id : Ids) { AutoSteps.Add({ A_FaceItem, Id, 0.f }); Wait(1.3f); Shot(*FString::Printf(TEXT("item_%s"), *Id.ToString())); }
		}
		AutoIndex = 0;
		AutoStepStart = Clock;
		if (!AutoShotDir.IsEmpty()) { AutoShotDir = FPaths::ConvertRelativePathToFull(AutoShotDir); IFileManager::Get().MakeDirectory(*AutoShotDir, true); }
		return;
	}
'''
s = s[:a] + new + s[a:]
s = s.replace('''	case A_Tele:''', '''	case A_Her:
		if (AWCEntity* E = Her())
		{
			const FVector Fwd = FRotator(0.f, P->GetControlRotation().Yaw, 0.f).Vector();
			E->Appear(P->GetActorLocation() - FVector(0, 0, 88) + Fwd * S.F, (-Fwd).Rotation().Yaw, S.Arg);
			E->SetGlow(S.F < 200.f ? 0.f : 0.f);
		}
		Next(); return;
	case A_FaceItem:
		if (AActor* T = AutoTarget(this, S.Arg))
		{
			FVector O, E; T->GetActorBounds(true, O, E);
			// stand 1.2 m away on whichever side is open
			FVector Best = O + FVector(-120, 0, 0);
			for (float Yaw = 0.f; Yaw < 360.f; Yaw += 45.f)
			{
				const FVector Cand = O + FRotator(0.f, Yaw, 0.f).Vector() * 125.f;
				FHitResult Hit;
				FCollisionQueryParams Q(SCENE_QUERY_STAT(WCItems), false, P);
				Q.AddIgnoredActor(T);
				if (!GetWorld()->LineTraceSingleByChannel(Hit, Cand + FVector(0, 0, 60), O + FVector(0, 0, 20), ECC_Visibility, Q)) { Best = Cand; break; }
			}
			const float Floor = FMath::RoundToFloat((O.Z + 40.f) / 350.f - 0.5f) * 350.f;
			P->TeleportToCheckpoint(FVector(Best.X, Best.Y, Floor + 96.f), (O - Best).Rotation().Yaw);
			if (AController* Ct = P->GetController()) Ct->SetControlRotation((O - (FVector(Best.X, Best.Y, Floor + 152.f))).Rotation());
		}
		Next(); return;
	case A_Tele:''')
io.open(R + "WCAuto.cpp", "w", encoding="utf-8", newline="\n").write(s)
print("ok")
