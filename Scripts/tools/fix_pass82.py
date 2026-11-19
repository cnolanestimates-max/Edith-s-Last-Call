"""Pass 82: the television reflection is staged so it can be read.
  - she first STANDS in the living-room doorway behind him, lit, seen only in the dead glass (slow), then screams and runs (all at once)
  - less flashlight glare on the tube, a darker control panel, a slightly brighter picture
  - the test looks at the screen during the scare and saves what the glass sees twice"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

edit(R + "Scripts/level/import_items.py", [
    ('("Gain", 300.0), ("RGain", 30.0)', '("Gain", 420.0), ("RGain", 30.0)'),
    ('mel.connect_material_property(const1(m, 0.14, -600, -80), "", unreal.MaterialProperty.MP_ROUGHNESS)',
     'mel.connect_material_property(const1(m, 0.32, -600, -80), "", unreal.MaterialProperty.MP_ROUGHNESS)\n'
     '    mel.connect_material_property(const1(m, 0.22, -600, -140), "", unreal.MaterialProperty.MP_SPECULAR)'),
    ('item_material("M_TVPanel", (0.028, 0.026, 0.022), 0.5, 0.0)', 'item_material("M_TVPanel", (0.007, 0.0065, 0.006), 0.5, 0.0)'),
])

edit(R + "Scripts/level/build_house.py", [
    ('point("Her_TVFar", 205, 235, GZ, -80)', 'point("Her_TVFar", 200, -212, GZ, -60)          # in the hall doorway, behind anyone at the set'),
])

edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('double TVAt = 0.0, TVNextAt = -1.0, TVHerAt = -1.0;', 'double TVAt = 0.0, TVNextAt = -1.0, TVHerAt = -1.0, TVRunAt = -1.0;'),
])

edit(R + "Source/WellnessCheck/WCEvents.cpp", [
    ('''TVPhase = 2;
	TVAt = Clock;
	TVHerAt = -1.0;''', '''TVPhase = 2;
	TVAt = Clock;
	TVHerAt = -1.0;
	TVRunAt = -1.0;'''),
    ('''if (TVHerAt < 0.0 && T > 1.3f && H)
	{
		// at the far door, behind him: only the glass can see her
		const FVector Far = Pos(TEXT("Her_TVFar"));
		H->Appear(Far, (P->GetActorLocation() - Far).Rotation().Yaw, TEXT("Run"));''',
     '''if (TVHerAt < 0.0 && T > 1.1f && H)
	{
		// in the doorway behind him, standing quite still: only the glass can see her
		const FVector Far = Pos(TEXT("Her_TVFar"));
		H->Appear(Far, (P->GetActorLocation() - Far).Rotation().Yaw, TEXT("Idle"));'''),
    ('TVHerLight->SetRelativeLocation(FVector(70.f, 0.f, 190.f));', 'TVHerLight->SetRelativeLocation(FVector(85.f, 0.f, 170.f));'),
    ('''TVHerLight->SetCastShadows(false);
		TArray<FVector> Pts; Pts.Add(P->GetActorLocation() - FVector(0, 0, 88.f));
		H->MoveAlong(Pts, 880.f, TEXT("Run"));
		H->SetScream(1.f);
		Play2D(TEXT("her_scream"), 1.f);
		Play2D(TEXT("sting_hit"), 0.9f, EWCSnd::Music);
		TVHerAt = Clock;
		Tension = 1.f;
		if (bAuto && !AutoShotDir.IsEmpty())
		{
			const FString D0 = AutoShotDir;
			After(0.30f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_1.png"), false, false); });
			After(0.62f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_2.png"), false, false); });
			After(0.45f, [this, D0]() { if (TVTarget) UKismetRenderingLibrary::ExportRenderTarget(this, TVTarget, D0, TEXT("S13_what_the_glass_sees.png")); });
		}
	}
	if (TVHerAt > 0.0)
	{
		P->AddShake(0.75f);
		const bool bReached = H && H->IsShown() && H->DistToPlayer() < 175.f;
		if (bTurned || bReached || Clock - TVHerAt > 1.5) TVReflectionEnd();
	}
	else if (bTurned && T > 0.4f) TVReflectionEnd();            // he turned before she came: the room is empty''',
     '''TVHerLight->SetCastShadows(false);
		TVHerAt = Clock;
		Tension = 0.9f;
		PlayAt(TEXT("her_breath"), Far + FVector(0, 0, 200), 0.8f, 0.8f, 1600.f);
		if (bAuto && !AutoShotDir.IsEmpty())
		{
			const FString D0 = AutoShotDir;
			After(1.1f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_0_standing.png"), false, false); });
			After(1.0f, [this, D0]() { if (TVTarget) UKismetRenderingLibrary::ExportRenderTarget(this, TVTarget, D0, TEXT("S13_what_the_glass_sees_standing.png")); });
		}
	}
	// slowly: she only stands there.  Then all at once.
	if (TVHerAt > 0.0 && TVRunAt < 0.0 && Clock - TVHerAt > 1.7 && H)
	{
		TArray<FVector> Pts;
		Pts.Add(FVector(218.f, -335.f, H->GetActorLocation().Z));          // round the end of the sofa
		Pts.Add(P->GetActorLocation() - FVector(0, 0, 88.f));
		H->MoveAlong(Pts, 760.f, TEXT("Run"));
		H->SetScream(1.f);
		Play2D(TEXT("her_scream"), 1.f);
		Play2D(TEXT("sting_hit"), 0.9f, EWCSnd::Music);
		TVRunAt = Clock;
		Tension = 1.f;
		if (bAuto && !AutoShotDir.IsEmpty())
		{
			const FString D0 = AutoShotDir;
			After(0.22f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_1.png"), false, false); });
			After(0.42f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_2.png"), false, false); });
			After(0.32f, [this, D0]() { if (TVTarget) UKismetRenderingLibrary::ExportRenderTarget(this, TVTarget, D0, TEXT("S13_what_the_glass_sees_running.png")); });
		}
	}
	if (TVRunAt > 0.0)
	{
		P->AddShake(0.75f);
		const bool bReached = H && H->IsShown() && H->DistToPlayer() < 150.f;
		if (bTurned || bReached || Clock - TVRunAt > 1.5) TVReflectionEnd();
	}
	else if (bTurned && T > 0.4f) TVReflectionEnd();            // he turned before she ran: the room is empty'''),
])

edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''AutoSteps.Add({ A_Do, TEXT("tvgain:300"), 0.f });
			AutoSteps.Add({ A_Do, TEXT("at:250,-215,92,-70,-10"), 0.f }); Wait(1.2f); Shot(TEXT("tv_4_room_lit_by_it"));
			AutoSteps.Add({ A_Do, TEXT("at:372,-425,92,-90,-12"), 0.f }); Wait(1.0f);
			AutoSteps.Add({ A_Do, TEXT("tvoff"), 0.f }); Wait(0.9f); Shot(TEXT("tv_5_dead_glass")); Wait(3.0f); Shot(TEXT("tv_6_after")); Wait(2.0f);''',
     '''AutoSteps.Add({ A_Do, TEXT("tvgain:420"), 0.f });
			AutoSteps.Add({ A_Do, TEXT("at:250,-215,92,-70,-10"), 0.f }); Wait(1.2f); Shot(TEXT("tv_4_room_lit_by_it"));
			AutoSteps.Add({ A_Tele, TEXT("A_Living"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("tv"), 0.f }); Wait(0.6f);
			AutoSteps.Add({ A_Do, TEXT("tvoff"), 0.f }); Wait(0.9f); Shot(TEXT("tv_5_dead_glass")); Wait(5.0f); Shot(TEXT("tv_6_after")); Wait(2.0f);'''),
])
print("pass 82 applied")
