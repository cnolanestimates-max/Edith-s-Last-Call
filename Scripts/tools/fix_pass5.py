import io
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"


def sub(f, old, new, count=1):
    s = io.open(R + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(R + f, "w", encoding="utf-8", newline="\n").write(s)


# 1. moving the player mid knock-down must not cancel the knock-down
sub("WCCharacter.h", "	void TeleportToCheckpoint(const FVector& Loc, float Yaw);", "	void TeleportToCheckpoint(const FVector& Loc, float Yaw);\n	/** Move the player without touching any state (used while they are down and the screen is black). */\n	void Relocate(const FVector& Loc, float Yaw);")
sub("WCCharacter.cpp", "bool AWCCharacter::Blocked() const", '''void AWCCharacter::Relocate(const FVector& Loc, float Yaw)
{
	SetActorLocation(Loc, false, nullptr, ETeleportType::TeleportPhysics);
	if (AController* C = GetController()) C->SetControlRotation(FRotator(0.f, Yaw, 0.f));
	LastLoc = Loc;
	AimQuat = FRotator(0.f, Yaw, 0.f).Quaternion();
}

bool AWCCharacter::Blocked() const''')
sub("WCStory.cpp", '''				if (AWCCharacter* Pl = Player()) Pl->TeleportToCheckpoint(Pos(TEXT("P_CellarBottom")), YawOf(TEXT("P_CellarBottom")));''',
    '''				if (AWCCharacter* Pl = Player()) Pl->Relocate(Pos(TEXT("P_CellarBottom")), YawOf(TEXT("P_CellarBottom")));''')

# 2. lock-in has its own clock; the finale clock starts when the keepsakes go down
sub("WCDirector.h", "	double FinaleStart = -1.0;", "	double FinaleStart = -1.0;\n	double LockInStart = -1.0;\n	double SprintStart = -1.0;\n	double SprintRetarget = 0.0;")
sub("WCStory.cpp", '''			const double Elapsed = Clock - FinaleStart;
			TArray<FVector> Pts; Pts.Add(FVector(P->GetActorLocation().X, P->GetActorLocation().Y, H->GetActorLocation().Z));''',
    '''			const double Elapsed = Clock - LockInStart;
			TArray<FVector> Pts; Pts.Add(FVector(P->GetActorLocation().X, P->GetActorLocation().Y, H->GetActorLocation().Z));''')
sub("WCStory.cpp", '''			bLockInActive = true;
			FinaleStart = Clock;''', '''			bLockInActive = true;
			LockInStart = Clock;''')
sub("WCStory.cpp", '''		Set(TEXT("placed"));
		ApplyWorldState();''', '''		Set(TEXT("placed"));
		FinaleStart = Clock;
		ApplyWorldState();''')

# 3. sprints follow you if you run, and always resolve
sub("WCStory.cpp", '''	// ---- S4 / S6: sprint at the player
	if (bSprintActive && H->IsShown() && H->DistToPlayer() < 175.f)
	{''', '''	// ---- S4 / S6: sprint at the player.  She follows if you run; if she somehow cannot reach you, the scare still ends.
	if (bSprintActive && H->IsShown())
	{
		if (SprintStart < 0.0) SprintStart = Clock;
		if (Clock > SprintRetarget)
		{
			SprintRetarget = Clock + 0.25;
			TArray<FVector> Pts; Pts.Add(FVector(P->GetActorLocation().X, P->GetActorLocation().Y, P->GetActorLocation().Z - 88.f));
			H->MoveAlong(Pts, 640.f, TEXT("Run"));
		}
	}
	if (bSprintActive && H->IsShown() && (H->DistToPlayer() < 175.f || Clock - SprintStart > 9.0))
	{
		SprintStart = -1.0;''')
sub("WCStory.cpp", '''			Pl->SetLightScale(0.55f);
			Pl->FlickerLight(2.f, 0.95f);
			bSprintActive = true;''', '''			Pl->SetLightScale(0.55f);
			Pl->FlickerLight(2.f, 0.95f);
			SprintStart = -1.0;
			bSprintActive = true;''')
sub("WCStory.cpp", '''		P->FlickerLight(1.6f, 0.8f);
		bSprintActive = true;''', '''		P->FlickerLight(1.6f, 0.8f);
		SprintStart = -1.0;
		bSprintActive = true;''')

# 4. the bot continues from the checkpoint after a fail instead of starting over; forced moves land on a waypoint
sub("WCDirector.cpp", '''	if (bAuto || FParse::Param(FCommandLine::Get(), TEXT("WCNewGame"))) PendingStart = 1;''',
    '''	if ((bAuto && PendingStart == 0) || FParse::Param(FCommandLine::Get(), TEXT("WCNewGame"))) PendingStart = 1;''')
sub("WCAuto.cpp", '''					if (bForce) P->TeleportToCheckpoint(Goal + FVector(0, 0, 100), P->GetControlRotation().Yaw);''',
    '''					if (bForce)
					{
						TArray<FVector> Route;
						AutoRoute(Goal + FVector(0, 0, 88), Goal, Route);      // nearest waypoint to the goal comes first
						const FVector Land = Route.Num() > 1 ? Route[0] : Goal;
						P->TeleportToCheckpoint(Land + FVector(0, 0, 96), P->GetControlRotation().Yaw);
					}''')
print("ok")
