# Pass 126: the crash a second after the cruiser stops (Cheyenne, 21:10 UTC).
# Call stack (from the minidump and the engine's exported names): UWorld::SendAllEndOfFrameUpdates ->
# CreateRenderState_Concurrent -> UInstancedStaticMeshComponent::CreateSceneProxy -> assertion in
# InstanceDataSceneProxy.h:400 (the instance buffers read while their update task is still writing).
# Cause: the dust motes and the flies moved their instances every frame with bMarkRenderStateDirty = true, which in
# this engine throws the whole scene proxy away and builds a new one each frame.  When the machine is busy (as it is
# when the car stops and both start up again) the last frame's instance update has not finished when the new proxy
# reads it.  The engine tracks moved instances by itself (TransformChanged -> MarkRenderInstancesDirty), so the flag is
# simply not passed: no proxy is rebuilt, and nothing is read while it is being written.
#   -WCAutoStop=<flag> : (tests) the bot's run ends six seconds after that story flag is set
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

S = r"C:\GameDev\Unreal\WellnessCheck\Source\WellnessCheck"

edit(S + r"\WCCharacter.cpp", [
    ("""		Dust->UpdateInstanceTransform(i, T, true, k == Slice - 1, bWrap);
""",
     """		// (never bMarkRenderStateDirty here: it rebuilds the whole proxy every frame, and that crashed; see fix_pass126.py)
		Dust->UpdateInstanceTransform(i, T, true, false, bWrap);
"""),
])

edit(S + r"\WCDirector.cpp", [
    ("""		Flies->UpdateInstanceTransform(i, FTransform(FQuat::Identity, P, FVector(0.0055f, 0.0035f, 0.0035f)), true, i == N - 1, true);
""",
     """		// (never bMarkRenderStateDirty here: it rebuilds the whole proxy every frame, and that crashed; see fix_pass126.py)
		Flies->UpdateInstanceTransform(i, FTransform(FQuat::Identity, P, FVector(0.0055f, 0.0035f, 0.0035f)), true, false, true);
"""),
])

edit(S + r"\WCAuto.cpp", [
    ("""	if (!P || AutoIndex < 0) return;
""",
     """	if (!P || AutoIndex < 0) return;
	{
		// a short check: stop a few seconds after a given point in the story
		static FString StopFlag;
		static bool bStopRead = false, bStopping = false;
		if (!bStopRead) { bStopRead = true; FParse::Value(FCommandLine::Get(), TEXT("WCAutoStop="), StopFlag); }
		if (!StopFlag.IsEmpty() && !bStopping && Has(FName(*StopFlag)))
		{
			bStopping = true;
			UE_LOG(LogWCAuto, Display, TEXT("WCAUTO stop point %s reached at t=%.1f"), *StopFlag, PlaySeconds);
			After(6.f, [this]() { UKismetSystemLibrary::QuitGame(this, UGameplayStatics::GetPlayerController(this, 0), EQuitPreference::Quit, false); });
		}
	}
"""),
])
print("pass 126 applied")
