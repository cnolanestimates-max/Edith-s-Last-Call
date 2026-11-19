"""Pass 83: finding out why she is not seen in the television glass.
  - she stands further back, across the hall, so the run lasts long enough to see (it was over in 0.16 s)
  - log where she and her light are; -WCTVDebug shows her to the ordinary camera from the set's side of the room
  - a pin-point glare on the tube instead of a wide bloom"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

edit(R + "Scripts/level/import_items.py", [
    ('const1(m, 0.32, -600, -80)', 'const1(m, 0.07, -600, -80)'),
    ('const1(m, 0.22, -600, -140)', 'const1(m, 0.35, -600, -140)'),
])

edit(R + "Scripts/level/build_house.py", [
    ('point("Her_TVFar", 200, -212, GZ, -60)', 'point("Her_TVFar", 200, -110, GZ, -60)'),
])

edit(R + "Source/WellnessCheck/WCEvents.cpp", [
    ('''const bool bTurned = FVector::DotProduct(P->EyeForward().GetSafeNormal2D(), ToTv) < -0.05f;''',
     '''const bool bDbg = FParse::Param(FCommandLine::Get(), TEXT("WCTVDebug"));
	const bool bTurned = !bDbg && FVector::DotProduct(P->EyeForward().GetSafeNormal2D(), ToTv) < -0.05f;'''),
    ('''for (UPrimitiveComponent* C : Prims) { C->bVisibleInSceneCaptureOnly = true; C->MarkRenderStateDirty(); }''',
     '''for (UPrimitiveComponent* C : Prims) { C->bVisibleInSceneCaptureOnly = !bDbg; C->MarkRenderStateDirty(); }'''),
    ('''TVHerAt = Clock;
		Tension = 0.9f;''', '''TVHerAt = Clock;
		Tension = 0.9f;
		UE_LOG(LogWCEvents, Display, TEXT("WCTV she stands at %s (shown %d, %d parts), her light at %s, he is at %s, the glass looks from %s toward %s"),
			*H->GetActorLocation().ToCompactString(), H->IsShown() ? 1 : 0, Prims.Num(), *TVHerLight->GetComponentLocation().ToCompactString(),
			*P->GetActorLocation().ToCompactString(), *TVCapture->GetComponentLocation().ToCompactString(), *TVCapture->GetComponentRotation().ToCompactString());'''),
    ('H->MoveAlong(Pts, 760.f, TEXT("Run"));', 'H->MoveAlong(Pts, 600.f, TEXT("Run"));'),
    ('''const bool bReached = H && H->IsShown() && H->DistToPlayer() < 150.f;
		if (bTurned || bReached || Clock - TVRunAt > 1.5) TVReflectionEnd();''',
     '''const bool bReached = H && H->IsShown() && H->DistToPlayer() < 120.f;
		if (bTurned || bReached || Clock - TVRunAt > 1.5)
		{
			UE_LOG(LogWCEvents, Display, TEXT("WCTV the reflection ends %.2f s after she ran (turned %d, reached %d)"), (float)(Clock - TVRunAt), bTurned ? 1 : 0, bReached ? 1 : 0);
			TVReflectionEnd();
		}'''),
])

edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''AutoSteps.Add({ A_Tele, TEXT("A_Living"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("tv"), 0.f }); Wait(0.6f);
			AutoSteps.Add({ A_Do, TEXT("tvoff"), 0.f }); Wait(0.9f); Shot(TEXT("tv_5_dead_glass")); Wait(5.0f); Shot(TEXT("tv_6_after")); Wait(2.0f);''',
     '''AutoSteps.Add({ A_Tele, TEXT("A_Living"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("tv"), 0.f }); Wait(0.6f);
			if (FParse::Param(FCommandLine::Get(), TEXT("WCTVDebug"))) { AutoSteps.Add({ A_Do, TEXT("at:372,-470,92,97,4"), 0.f }); Wait(0.5f); }
			AutoSteps.Add({ A_Do, TEXT("tvoff"), 0.f }); Wait(0.9f); Shot(TEXT("tv_5_dead_glass")); Wait(5.0f); Shot(TEXT("tv_6_after")); Wait(2.0f);'''),
])
print("pass 83 applied")
