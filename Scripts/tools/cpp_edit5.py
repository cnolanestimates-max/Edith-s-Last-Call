import io
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"


def sub(f, old, new, count=1):
    s = io.open(R + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(R + f, "w", encoding="utf-8", newline="\n").write(s)


# ---------------------------------------------------------------- doors: swing away from whoever opens them, never trap the player
sub("WCWorld.h", "	bool IsOpen() const { return bOpen; }", "	bool IsOpen() const { return bOpen; }\n	bool IsAjar() const { return bOpen && FMath::Abs(Target) < FMath::Abs(OpenAngle) * 0.7f; }\n	void OpenAwayFrom(const FVector& From, float Seconds = -1.f);")
sub("WCWorld.cpp", '''void AWCDoor::Slam()''', '''void AWCDoor::OpenAwayFrom(const FVector& From, float Seconds)
{
	// the leaf runs along the closed door's +X; its face normal is +Y.  Positive yaw swings the leaf toward +Y.
	const FRotator Closed(0.f, BaseYaw, 0.f);
	const FVector Normal = FRotationMatrix(Closed).GetUnitAxis(EAxis::Y);
	const float Side = FVector::DotProduct(From - GetActorLocation(), Normal);
	OpenAngle = FMath::Abs(OpenAngle) * (Side > 0.f ? -1.f : 1.f);
	SetOpen(true, Seconds);
}

void AWCDoor::Slam()''')
sub("WCWorld.cpp", '''	const bool bAjar = bOpen && FMath::Abs(Target) < FMath::Abs(OpenAngle) * 0.7f;
	SetOpen(bAjar ? true : !bOpen);''', '''	if (IsAjar() || !bOpen)
	{
		if (IsAjar()) { bOpen = false; }
		OpenAwayFrom(By ? By->GetActorLocation() : GetActorLocation());
	}
	else SetOpen(false);''')
sub("WCWorld.cpp", '''			D->Event(FName(*FString::Printf(TEXT("unlock:%s"), *WCId.ToString())));
			SetOpen(true);''', '''			D->Event(FName(*FString::Printf(TEXT("unlock:%s"), *WCId.ToString())));
			OpenAwayFrom(By ? By->GetActorLocation() : GetActorLocation());''')
sub("WCWorld.cpp", '''	if (FMath::IsNearlyEqual(Angle, Target, 0.01f)) return;
	Angle = FMath::FInterpConstantTo(Angle, Target, Dt, Rate);''', '''	// a door only stops you when it is shut; an open leaf never pins you in a doorway
	const bool bSolid = FMath::Abs(Angle) < 2.f && FMath::Abs(Target) < 2.f;
	if (bSolid != bWasSolid)
	{
		bWasSolid = bSolid;
		Mesh->SetCollisionResponseToChannel(ECC_Pawn, bSolid ? ECR_Block : ECR_Ignore);
	}
	if (FMath::IsNearlyEqual(Angle, Target, 0.01f)) return;
	Angle = FMath::FInterpConstantTo(Angle, Target, Dt, Rate);''')
sub("WCWorld.h", "	float BaseYaw = 0.f;", "	float BaseYaw = 0.f;\n	bool bWasSolid = true;")
sub("WCWorld.cpp", '''	if (bNewOpen == bOpen && FMath::IsNearlyEqual(Target, bNewOpen ? OpenAngle : 0.f, 0.5f)) return;''', '''	if (bNewOpen == bOpen && FMath::IsNearlyEqual(Target, bNewOpen ? OpenAngle : 0.f, 0.5f)) return;
	if (bNewOpen) { /* keep an already-chosen swing side when re-opening an ajar door */ if (FMath::Abs(Angle) > 3.f && (Angle > 0.f) != (OpenAngle > 0.f)) OpenAngle = -OpenAngle; }''')

# ---------------------------------------------------------------- bot: its own waypoint graph (nodes tagged NavNode / N_<name> / E_<neighbour>)
s = io.open(R + "WCAuto.cpp", encoding="utf-8").read()
a = s.index("		if (AutoPath.Num() == 0 || In > 0.0 && FMath::Fmod(In, 2.0) < Dt)")
b = s.index("		while (AutoPathIndex < AutoPath.Num() - 1")
new = '''		if (AutoPath.Num() == 0)
		{
			AutoPathIndex = 0;
			AutoRoute(Loc, Goal, AutoPath);
		}
'''
s = s[:a] + new + s[b:]
s = s.replace('''		while (AutoPathIndex < AutoPath.Num() - 1 && FVector::Dist2D(Loc, AutoPath[AutoPathIndex]) < 45.f) ++AutoPathIndex;''',
              '''		while (AutoPathIndex < AutoPath.Num() - 1 && FVector::Dist2D(Loc, AutoPath[AutoPathIndex]) < 40.f && FMath::Abs(Loc.Z - 88.f - AutoPath[AutoPathIndex].Z) < 150.f) ++AutoPathIndex;''')
s = s.replace('''			if (It->IsOpen() || !It->CanInteract()) continue;''', '''			if ((It->IsOpen() && !It->IsAjar()) || !It->CanInteract()) continue;''')
s = s.replace('''static AActor* AutoTarget(AWCDirector* D, FName Name)''', '''void AWCDirector::AutoRoute(const FVector& From, const FVector& Goal, TArray<FVector>& Out)
{
	Out.Reset();
	struct FNode { FName Name; FVector P; TArray<FName> To; };
	static TArray<FNode> Nodes;
	static TWeakObjectPtr<UWorld> ForWorld;
	if (ForWorld.Get() != GetWorld())
	{
		ForWorld = GetWorld();
		Nodes.Reset();
		for (TActorIterator<AActor> It(GetWorld()); It; ++It)
		{
			if (!It->ActorHasTag(TEXT("NavNode"))) continue;
			FNode N; N.P = It->GetActorLocation();
			for (const FName& T : It->Tags)
			{
				const FString S = T.ToString();
				if (S.StartsWith(TEXT("N_"))) N.Name = FName(*S.Mid(2));
				else if (S.StartsWith(TEXT("E_"))) N.To.Add(FName(*S.Mid(2)));
			}
			Nodes.Add(N);
		}
		UE_LOG(LogWCAuto, Display, TEXT("WCAUTO route graph: %d nodes"), Nodes.Num());
	}
	auto Nearest = [](const FVector& P) -> int32
	{
		int32 Best = INDEX_NONE; float BestD = 1e12f;
		for (int32 i = 0; i < Nodes.Num(); ++i)
		{
			if (FMath::Abs(Nodes[i].P.Z - P.Z) > 130.f) continue;
			const float D = FVector::DistSquared2D(Nodes[i].P, P);
			if (D < BestD) { BestD = D; Best = i; }
		}
		return Best;
	};
	const FVector Feet = From - FVector(0, 0, 88);
	const int32 A = Nearest(Feet), B = Nearest(Goal);
	if (A == INDEX_NONE || B == INDEX_NONE || (FVector::Dist2D(Feet, Goal) < 260.f && FMath::Abs(Feet.Z - Goal.Z) < 130.f)) { Out.Add(Goal); return; }
	// Dijkstra
	TArray<float> Cost; Cost.Init(1e12f, Nodes.Num());
	TArray<int32> Prev; Prev.Init(INDEX_NONE, Nodes.Num());
	TArray<bool> Done; Done.Init(false, Nodes.Num());
	Cost[A] = 0.f;
	for (int32 Iter = 0; Iter < Nodes.Num(); ++Iter)
	{
		int32 U = INDEX_NONE; float Best = 1e12f;
		for (int32 i = 0; i < Nodes.Num(); ++i) if (!Done[i] && Cost[i] < Best) { Best = Cost[i]; U = i; }
		if (U == INDEX_NONE || U == B) break;
		Done[U] = true;
		for (const FName& To : Nodes[U].To)
		{
			const int32 V = Nodes.IndexOfByPredicate([&To](const FNode& N) { return N.Name == To; });
			if (V == INDEX_NONE) continue;
			const float C = Cost[U] + FVector::Dist(Nodes[U].P, Nodes[V].P);
			if (C < Cost[V]) { Cost[V] = C; Prev[V] = U; }
		}
	}
	TArray<FVector> Rev;
	for (int32 i = B; i != INDEX_NONE; i = Prev[i]) Rev.Add(Nodes[i].P);
	if (Rev.Num() == 0 || Cost[B] > 1e11f) { Out.Add(Goal); return; }
	for (int32 i = Rev.Num() - 1; i >= 0; --i) Out.Add(Rev[i]);
	// skip the first node if we are already past it on the way to the second
	if (Out.Num() >= 2 && FVector::Dist2D(Feet, Out[1]) < FVector::Dist2D(Out[0], Out[1])) Out.RemoveAt(0);
	Out.Add(Goal);
}

static AActor* AutoTarget(AWCDirector* D, FName Name)''')
io.open(R + "WCAuto.cpp", "w", encoding="utf-8", newline="\n").write(s)
sub("WCDirector.h", "	void AutoTick(float Dt);", "	void AutoTick(float Dt);\n	void AutoRoute(const FVector& From, const FVector& Goal, TArray<FVector>& Out);")
print("ok")
