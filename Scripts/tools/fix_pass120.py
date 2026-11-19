# Pass 120: her twenty face keys are driven in the game.  Nine faces (rest, watch, grin, snarl, rage, scream, wince,
# grief, hush) are mixes of the keys; each clip has its own face, the scream mixes in over whatever she is doing, her
# lines pick a face, and a random key twitches every few seconds.  -WCHerLook -WCFaceOnly photographs every face.
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

S = r"C:\GameDev\Unreal\WellnessCheck\Source\WellnessCheck"

edit(S + r"\WCEntity.h", [
    ("""	void SetScream(float Amount) { ScreamTarget = FMath::Clamp(Amount, 0.f, 1.f); }
""",
     """	void SetScream(float Amount) { ScreamTarget = FMath::Clamp(Amount, 0.f, 1.f); }
	/** The face she makes: rest, watch, grin, snarl, rage, scream, wince, grief, hush.  Seconds > 0: for that long, then back to the clip's own face. */
	void SetMood(FName NewMood, float Seconds = 0.f);
"""),
    ("""	float FaceT = 0.f, TalkLeft = 0.f, NextTwitch = 2.f, TwitchLeft = 0.f, StepAcc = 0.f;
""",
     """	float FaceT = 0.f, TalkLeft = 0.f, NextTwitch = 2.f, TwitchLeft = 0.f, StepAcc = 0.f;
	FName Mood = TEXT("watch"), ClipMood = TEXT("watch");
	float MoodLeft = 0.f;
	int32 TwitchKey = 1;
	float FaceNow[20] = {};
"""),
])

edit(S + r"\WCEntity.cpp", [
    ("""void AWCEntity::Play(FName Anim, bool bLoop, float Rate)
{
""",
     """// ---- her face: twenty shape keys (Scripts/her/build_her.py makes them; keep the two lists alike)
namespace
{
	enum EFace { F_Scream, F_Sneer, F_Brow, F_BrowUp, F_BrowKnit, F_BrowDown, F_EyeWide, F_Squint, F_Snarl, F_SneerR, F_Grin, F_Frown, F_JawSide, F_Pucker,
		F_CheekSuck, F_Stretch, F_Unhinge, F_CheekL, F_CheekR, F_CheekRaise, F_Num };
	const TCHAR* GFaceNames[F_Num] = { TEXT("Scream"), TEXT("Sneer"), TEXT("Brow"), TEXT("BrowUp"), TEXT("BrowKnit"), TEXT("BrowDown"), TEXT("EyeWide"), TEXT("Squint"),
		TEXT("Snarl"), TEXT("SneerR"), TEXT("Grin"), TEXT("Frown"), TEXT("JawSide"), TEXT("Pucker"), TEXT("CheekSuck"), TEXT("Stretch"), TEXT("Unhinge"), TEXT("CheekL"),
		TEXT("CheekR"), TEXT("CheekRaise") };
	struct FFaceW { EFace Key; float V; };
	struct FFaceMood { const TCHAR* Name; TArray<FFaceW> W; };
	const TArray<FFaceMood>& FaceMoods()
	{
		static const TArray<FFaceMood> M = {
			{ TEXT("rest"), {} },
			{ TEXT("watch"), { { F_EyeWide, 0.8f }, { F_BrowUp, 0.35f }, { F_CheekSuck, 0.5f } } },
			{ TEXT("grin"), { { F_Grin, 1.f }, { F_Squint, 0.6f }, { F_Sneer, 0.4f }, { F_SneerR, 0.4f }, { F_BrowUp, 0.25f } } },
			{ TEXT("snarl"), { { F_Snarl, 1.f }, { F_Sneer, 0.8f }, { F_SneerR, 0.55f }, { F_BrowKnit, 0.8f }, { F_BrowDown, 0.7f }, { F_JawSide, 0.35f }, { F_Scream, 0.18f } } },
			{ TEXT("rage"), { { F_Scream, 0.7f }, { F_BrowKnit, 1.f }, { F_BrowDown, 0.8f }, { F_Snarl, 1.f }, { F_Stretch, 0.45f }, { F_CheekRaise, 0.5f } } },
			// down and wide: the jaw past its hinge, the cheeks drawn out to the sides and hollow
			{ TEXT("scream"), { { F_Scream, 1.f }, { F_Unhinge, 1.f }, { F_Stretch, 1.f }, { F_BrowKnit, 0.8f }, { F_Snarl, 0.8f }, { F_EyeWide, 1.f }, { F_CheekSuck, 0.5f } } },
			{ TEXT("wince"), { { F_CheekL, 1.f }, { F_Sneer, 0.8f }, { F_Squint, 0.7f }, { F_JawSide, 0.5f }, { F_BrowKnit, 0.5f } } },
			{ TEXT("grief"), { { F_BrowUp, 1.f }, { F_BrowKnit, 0.5f }, { F_Frown, 1.f }, { F_Squint, 0.45f }, { F_Scream, 0.14f }, { F_CheekSuck, 0.4f }, { F_Brow, 0.6f } } },
			{ TEXT("hush"), { { F_Pucker, 1.f }, { F_BrowKnit, 0.4f }, { F_Squint, 0.3f }, { F_EyeWide, 0.2f } } },
		};
		return M;
	}
	void FacePose(FName Mood, float* Out)
	{
		for (int32 k = 0; k < F_Num; ++k) Out[k] = 0.f;
		for (const FFaceMood& M : FaceMoods()) if (Mood == M.Name) { for (const FFaceW& W : M.W) Out[W.Key] = W.V; return; }
	}
}

void AWCEntity::SetMood(FName NewMood, float Seconds)
{
	Mood = NewMood;
	MoodLeft = Seconds;
	if (Seconds <= 0.f) ClipMood = NewMood;
}

void AWCEntity::Play(FName Anim, bool bLoop, float Rate)
{
"""),
    ("""	const float* M = Mouths.Find(Anim);
	SetScream(M ? *M : 0.f);
}
""",
     """	const float* M = Mouths.Find(Anim);
	SetScream(M ? *M : 0.f);
	// and the rest of her face
	static const TMap<FName, FName> Faces = { { TEXT("Idle"), TEXT("watch") }, { TEXT("Peek"), TEXT("watch") }, { TEXT("Walk"), TEXT("snarl") }, { TEXT("Tall"), TEXT("grin") },
		{ TEXT("Sit"), TEXT("grief") }, { TEXT("Under"), TEXT("hush") }, { TEXT("Crawl"), TEXT("snarl") }, { TEXT("Rise"), TEXT("rage") }, { TEXT("Run"), TEXT("rage") }, { TEXT("Lunge"), TEXT("rage") } };
	const FName* F = Faces.Find(Anim);
	ClipMood = F ? *F : FName(TEXT("watch"));
	if (MoodLeft <= 0.f) Mood = ClipMood;
}
"""),
    ("""	ScreamTarget = ScreamAlpha = 0.f;
	Body->SetMorphTarget(TEXT("Scream"), 0.f);
	Body->Stop();
""",
     """	ScreamTarget = ScreamAlpha = 0.f;
	for (int32 k = 0; k < F_Num; ++k) { FaceNow[k] = 0.f; Body->SetMorphTarget(GFaceNames[k], 0.f); }
	MoodLeft = 0.f;
	Body->Stop();
"""),
    ("""		if (FaceT > NextTwitch) { TwitchLeft = FMath::FRandRange(0.12f, 0.3f); NextTwitch = FaceT + FMath::FRandRange(1.2f, 5.5f); }
		float Jaw = 0.03f + 0.03f * FMath::Sin(FaceT * 1.4f);
		if (TalkLeft > 0.f) Jaw = 0.10f + 0.24f * FMath::Abs(FMath::Sin(FaceT * 17.f) * 0.6f + FMath::Sin(FaceT * 29.f + 1.f) * 0.4f);
		Jaw = FMath::Max(Jaw, ScreamAlpha);
		const float Sneer = TwitchLeft > 0.f ? 1.f : 0.18f + 0.16f * FMath::Sin(FaceT * 0.7f + 2.f) + 0.5f * ScreamAlpha;
		const float Brow = FMath::Clamp(0.35f + 0.35f * FMath::Sin(FaceT * 0.45f) + 0.6f * ScreamAlpha + (TwitchLeft > 0.f ? 0.3f : 0.f), 0.f, 1.f);
		Body->SetMorphTarget(TEXT("Scream"), Jaw);
		Body->SetMorphTarget(TEXT("Sneer"), FMath::Clamp(Sneer, 0.f, 1.f));
		Body->SetMorphTarget(TEXT("Brow"), Brow);
""",
     """		if (FaceT > NextTwitch)
		{
			// one part of her face jumps by itself: a lip, a cheek, the lid, the jaw
			static const int32 Tw[] = { F_Sneer, F_SneerR, F_CheekL, F_CheekR, F_Snarl, F_Squint, F_JawSide, F_BrowKnit, F_Sneer };
			TwitchKey = Tw[FMath::RandHelper(UE_ARRAY_COUNT(Tw))];
			TwitchLeft = FMath::FRandRange(0.12f, 0.3f);
			NextTwitch = FaceT + FMath::FRandRange(1.2f, 5.5f);
		}
		if (MoodLeft > 0.f) { MoodLeft -= Dt; if (MoodLeft <= 0.f) Mood = ClipMood; }
		float Want[F_Num], Scr[F_Num];
		FacePose(Mood, Want);
		FacePose(TEXT("scream"), Scr);
		// never still: she breathes through her mouth, her lip rides up off her teeth, the lid under her eye sags and lifts
		Want[F_Scream] += 0.03f + 0.03f * FMath::Sin(FaceT * 1.4f);
		Want[F_Sneer] += 0.12f + 0.10f * FMath::Sin(FaceT * 0.7f + 2.f);
		Want[F_Brow] += 0.25f + 0.25f * FMath::Sin(FaceT * 0.45f);
		Want[F_CheekSuck] += 0.12f + 0.12f * FMath::Sin(FaceT * 0.9f + 1.f);
		Want[F_EyeWide] += 0.15f * FMath::Sin(FaceT * 0.31f + 0.5f);
		if (TalkLeft > 0.f)
		{
			// speaking: the jaw works, and the mouth goes between narrow and wide
			Want[F_Scream] = FMath::Max(Want[F_Scream], 0.10f + 0.24f * FMath::Abs(FMath::Sin(FaceT * 17.f) * 0.6f + FMath::Sin(FaceT * 29.f + 1.f) * 0.4f));
			Want[F_Pucker] += 0.45f * FMath::Abs(FMath::Sin(FaceT * 9.f));
			Want[F_Stretch] += 0.22f * FMath::Abs(FMath::Sin(FaceT * 6.f + 1.f));
		}
		if (TwitchLeft > 0.f) Want[TwitchKey] = FMath::Max(Want[TwitchKey], 0.9f);
		for (int32 k = 0; k < F_Num; ++k)
		{
			const float T = FMath::Clamp(FMath::Lerp(Want[k], FMath::Max(Scr[k], Want[k] * 0.6f), ScreamAlpha), 0.f, 1.f);
			FaceNow[k] = FMath::FInterpTo(FaceNow[k], T, Dt, T > FaceNow[k] ? 16.f : 6.f);
			Body->SetMorphTarget(GFaceNames[k], FaceNow[k]);
		}
"""),
])

edit(S + r"\WCStory.cpp", [
    ("""			Her()->Talk(Len);
		}
""",
     """			Her()->Talk(Len);
			// what she is saying is on her face
			if (LineId == TEXT("m_fin1") || LineId == TEXT("m_fin2")) Her()->SetMood(TEXT("grief"), Len + 1.5f);
			else if (LineId == TEXT("m_fin3") || LineId == TEXT("m_whyleave")) Her()->SetMood(TEXT("rage"), Len + 1.f);
		}
"""),
    ("""			E->Appear(Pl->GetActorLocation() - FVector(0, 0, 88) + Fwd * 115.f, (-Fwd).Rotation().Yaw, TEXT("Tall"));
			Pl->SetLightScale(1.f);
""",
     """			E->Appear(Pl->GetActorLocation() - FVector(0, 0, 88) + Fwd * 115.f, (-Fwd).Rotation().Yaw, TEXT("Tall"));
			E->SetScream(1.f);                      // "STAY!": the whole of her mouth, down and wide
			Pl->SetLightScale(1.f);
"""),
])

edit(S + r"\WCAuto.cpp", [
    ("""		else if (FParse::Param(FCommandLine::Get(), TEXT("WCSpotOnly")))
		{
""",
     """		else if (FParse::Param(FCommandLine::Get(), TEXT("WCFaceOnly")))
		{
			// every face she can make, close, by his own flashlight
			Set(TEXT("inside")); Set(TEXT("locked_in")); Set(TEXT("tv_first"));
			At(TEXT("at:1500,0,92,180,10")); Wait(0.8f);
			AutoSteps.Add({ A_Her, TEXT("Idle"), 115.f }); Wait(0.5f); AutoSteps.Add({ A_LookHer, NAME_None, 0.8f });
			static const TCHAR* Ms[] = { TEXT("rest"), TEXT("watch"), TEXT("grin"), TEXT("snarl"), TEXT("rage"), TEXT("wince"), TEXT("grief"), TEXT("hush"), TEXT("scream") };
			for (const TCHAR* M : Ms)
			{
				At(*FString::Printf(TEXT("mood:%s"), M)); Wait(0.9f); AutoSteps.Add({ A_LookHer, NAME_None, 0.2f }); Shot(*FString::Printf(TEXT("face_%s"), M));
			}
			At(TEXT("mood:watch")); Wait(0.6f);
			AutoSteps.Add({ A_Her, TEXT("Idle"), 230.f }); Wait(0.6f); AutoSteps.Add({ A_LookHer, NAME_None, 0.6f });
			At(TEXT("mood:scream")); Wait(0.9f); Shot(TEXT("face_scream_from_2m"));
			At(TEXT("mood:grin")); Wait(0.9f); Shot(TEXT("face_grin_from_2m"));
			Wait(1.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCSpotOnly")))
		{
"""),
    ("""		else if (S.Arg == TEXT("book")) { bBusy = false; ScareBook(); }
""",
     """		else if (S.Arg == TEXT("book")) { bBusy = false; ScareBook(); }
		else if (S.Arg.ToString().StartsWith(TEXT("mood:")))
		{
			const FName M(*S.Arg.ToString().Mid(5));
			if (AWCEntity* E = Her()) { E->SetScream(M == TEXT("scream") ? 1.f : 0.f); E->SetMood(M == TEXT("scream") ? FName(TEXT("rage")) : M); }
		}
"""),
])
print("pass 120 applied")
