import io
R = "C:/GameDev/Unreal/WellnessCheck/"


def sub(f, old, new, count=1):
    s = io.open(R + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(R + f, "w", encoding="utf-8", newline="\n").write(s)


C = "Source/WellnessCheck/"
# ---- frame-time bookkeeping for the test bot (reported at every screenshot and at the end)
sub(C + "WCDirector.h", "	bool bAuto = false;", "	bool bAuto = false;\n	TArray<float> PerfFrames;\n	double PerfLast = 0.0;\n	void PerfReport(const TCHAR* Label, bool bReset);")
sub(C + "WCAuto.cpp", "void AWCDirector::AutoTick(float Dt)\n{", '''void AWCDirector::PerfReport(const TCHAR* Label, bool bReset)
{
	if (PerfFrames.Num() < 10) return;
	TArray<float> S = PerfFrames;
	S.Sort();
	double Sum = 0.0;
	for (float F : S) Sum += F;
	const float Avg = (float)(Sum / S.Num());
	const float P99 = S[FMath::Clamp(FMath::FloorToInt(S.Num() * 0.99f), 0, S.Num() - 1)];
	UE_LOG(LogWCAuto, Display, TEXT("WCPERF %s frames=%d avg=%.1f ms (%.0f fps) p99=%.1f ms (%.0f fps) worst=%.1f ms"), Label, S.Num(), Avg * 1000.f, 1.f / Avg, P99 * 1000.f, 1.f / P99, S.Last() * 1000.f);
	if (bReset) PerfFrames.Reset();
}

void AWCDirector::AutoTick(float Dt)
{
	{
		const double Now = FPlatformTime::Seconds();
		if (PerfLast > 0.0 && PlaySeconds > 20.f) PerfFrames.Add((float)(Now - PerfLast));
		PerfLast = Now;
		if (PerfFrames.Num() >= 3600) PerfReport(TEXT("window"), true);
	}''')
sub(C + "WCAuto.cpp", '''		UE_LOG(LogWCAuto, Display, TEXT("WCAUTO DONE t=%.1f stuck=%d ended=%d"), PlaySeconds, AutoStuckCount, Has(TEXT("ended")) ? 1 : 0);''',
    '''		PerfReport(TEXT("final"), true);
		UE_LOG(LogWCAuto, Display, TEXT("WCAUTO DONE t=%.1f stuck=%d ended=%d"), PlaySeconds, AutoStuckCount, Has(TEXT("ended")) ? 1 : 0);''')
# ---- packaging
p = R + "Config/DefaultGame.ini"
s = io.open(p, encoding="utf-8").read()
if "ProjectPackagingSettings" not in s:
    s += '''
[/Script/UnrealEd.ProjectPackagingSettings]
BuildConfiguration=PPBC_Shipping
bShareMaterialShaderCode=True
bSharedMaterialNativeLibraries=True
UsePakFile=True
bUseIoStore=True
bCompressed=True
IncludePrerequisites=True
+MapsToCook=(FilePath="/Game/WC/Maps/House")
+DirectoriesToAlwaysCook=(Path="/Game/WC")

[/Script/Engine.GameSession]
MaxPlayers=1
'''
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
