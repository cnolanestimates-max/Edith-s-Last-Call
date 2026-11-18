import io
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"


def sub(f, old, new, count=1):
    s = io.open(R + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(R + f, "w", encoding="utf-8", newline="\n").write(s)


s = io.open(R + "WCDirector.cpp", encoding="utf-8").read()
a = s.index("USoundBase* AWCDirector::Snd(const FString& Name)")
b = s.index("UAudioComponent* AWCDirector::Play2D")
new = '''USoundBase* AWCDirector::Snd(const FString& Name)
{
	if (Name.IsEmpty()) return nullptr;
	if (TObjectPtr<USoundBase>* Hit = SoundCache.Find(Name)) return Hit->Get();
	if (const TArray<FString>* Vars = SoundVariants.Find(Name))
	{
		if (Vars->Num() == 0) return nullptr;
		return SoundCache.FindRef((*Vars)[Rng.RandHelper(Vars->Num())]);
	}
	const FString Leaf = FPaths::GetCleanFilename(Name);
	if (USoundBase* S = LoadObject<USoundBase>(nullptr, *FString::Printf(TEXT("/Game/WC/Audio/%s.%s"), *Name, *Leaf), nullptr, LOAD_NoWarn | LOAD_Quiet))
	{
		SoundCache.Add(Name, S);
		return S;
	}
	// variants: name_01 .. name_NN, one picked at random each call
	TArray<FString>& Vars = SoundVariants.Add(Name);
	for (int32 i = 1; i <= 12; ++i)
	{
		const FString V = FString::Printf(TEXT("%s_%02d"), *Name, i);
		const FString VLeaf = FPaths::GetCleanFilename(V);
		USoundBase* X = LoadObject<USoundBase>(nullptr, *FString::Printf(TEXT("/Game/WC/Audio/%s.%s"), *V, *VLeaf), nullptr, LOAD_NoWarn | LOAD_Quiet);
		if (!X) break;
		SoundCache.Add(V, X);
		Vars.Add(V);
	}
	if (Vars.Num() == 0)
	{
		UE_LOG(LogWC, Warning, TEXT("WC: missing sound %s"), *Name);
		return nullptr;
	}
	return SoundCache.FindRef(Vars[Rng.RandHelper(Vars.Num())]);
}

'''
s = s[:a] + new + s[b:]
io.open(R + "WCDirector.cpp", "w", encoding="utf-8", newline="\n").write(s)
sub("WCDirector.h", '''	UPROPERTY(Transient) TMap<FString, TObjectPtr<USoundBase>> SoundCache;''', '''	UPROPERTY(Transient) TMap<FString, TObjectPtr<USoundBase>> SoundCache;
	TMap<FString, TArray<FString>> SoundVariants;''')
print("ok")
