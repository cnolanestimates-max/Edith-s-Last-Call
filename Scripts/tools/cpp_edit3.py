import io
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"


def sub(f, old, new, count=1):
    s = io.open(R + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(R + f, "w", encoding="utf-8", newline="\n").write(s)


# ---------------------------------------------------------------- hands: flashlight (left) and pistol (right) view models
sub("WCCharacter.h", '''	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UStaticMeshComponent> Gun;''',
    '''	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<USceneComponent> GunPivot;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UStaticMeshComponent> Gun;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UStaticMeshComponent> FlashHand;''')
sub("WCCharacter.cpp", '''	Flash->SetRelativeLocation(FVector(12.f, 16.f, -14.f));''', '''	Flash->SetRelativeLocation(FVector(26.f, -19.f, -17.f));''')
sub("WCCharacter.cpp", '''	Gun = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Gun"));
	Gun->SetupAttachment(Cam);
	Gun->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Gun->SetCastShadow(false);
	Gun->SetVisibility(false);''', '''	GunPivot = CreateDefaultSubobject<USceneComponent>(TEXT("GunPivot"));
	GunPivot->SetupAttachment(Cam);
	Gun = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Gun"));
	Gun->SetupAttachment(GunPivot);
	Gun->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Gun->SetCastShadow(false);
	Gun->SetVisibility(false);
	Gun->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));
	Gun->SetRelativeLocation(FVector(-14.f, 0.f, 0.f));
	FlashHand = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("FlashHand"));
	FlashHand->SetupAttachment(Flash);
	FlashHand->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	FlashHand->SetCastShadow(false);
	FlashHand->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));
	FlashHand->SetRelativeLocation(FVector(-19.f, 0.f, -1.f));''')
sub("WCCharacter.cpp", '''LoadObject<UStaticMesh>(nullptr, TEXT("/Game/WC/Props/SM_Pistol.SM_Pistol"))''', '''LoadObject<UStaticMesh>(nullptr, TEXT("/Game/WC/Props/SM_HandPistol.SM_HandPistol"))''')
sub("WCCharacter.cpp", '''	UStaticMesh* Mote = LoadObject<UStaticMesh>''', '''	if (UStaticMesh* HandMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/WC/Props/SM_HandFlashlight.SM_HandFlashlight")))
	{
		FlashHand->SetStaticMesh(HandMesh);
	}
	{
		// view-model tuning from the command line while dialling in: -WCHand=x,y,z,yaw,pitch,roll  -WCGun=...
		FString V;
		auto Apply = [](USceneComponent* C, const FString& S)
		{
			TArray<FString> P; S.ParseIntoArray(P, TEXT(","));
			if (P.Num() >= 3) C->SetRelativeLocation(FVector(FCString::Atof(*P[0]), FCString::Atof(*P[1]), FCString::Atof(*P[2])));
			if (P.Num() >= 6) C->SetRelativeRotation(FRotator(FCString::Atof(*P[4]), FCString::Atof(*P[3]), FCString::Atof(*P[5])));
		};
		if (FParse::Value(FCommandLine::Get(), TEXT("WCHand="), V, false)) Apply(FlashHand, V);
		if (FParse::Value(FCommandLine::Get(), TEXT("WCGun="), V, false)) Apply(Gun, V);
	}
	UStaticMesh* Mote = LoadObject<UStaticMesh>''')
sub("WCCharacter.cpp", '''	Gun->SetRelativeLocation(FMath::Lerp(Low, High, FMath::InterpEaseOut(0.f, 1.f, GunAlpha, 2.f)) + FVector(-5.f * Recoil, 0.f, 1.5f * Recoil - 16.f * ReloadDip));
	Gun->SetRelativeRotation(FRotator(-28.f * (1.f - GunAlpha) + 7.f * Recoil - 30.f * ReloadDip, 0.f, 0.f));''',
    '''	GunPivot->SetRelativeLocation(FMath::Lerp(Low, High, FMath::InterpEaseOut(0.f, 1.f, GunAlpha, 2.f)) + FVector(-5.f * Recoil, 0.f, 1.5f * Recoil - 16.f * ReloadDip));
	GunPivot->SetRelativeRotation(FRotator(-28.f * (1.f - GunAlpha) + 7.f * Recoil - 30.f * ReloadDip, 0.f, 0.f));
	FlashHand->SetVisibility(FlashHand->GetStaticMesh() != nullptr && KDTime < 0.f);''')
sub("WCCharacter.cpp", '#include "Materials/MaterialInterface.h"', '#include "Materials/MaterialInterface.h"\n#include "Misc/CommandLine.h"\n#include "Misc/Parse.h"')

# ---------------------------------------------------------------- flies
sub("WCDirector.h", '''	void TickLights(float Dt);''', '''	void TickLights(float Dt);
	void TickFlies(float Dt);
	UPROPERTY(VisibleAnywhere) TObjectPtr<class UInstancedStaticMeshComponent> Flies;
	struct FFly { FVector Centre; FVector Radii; FVector Freq; FVector Phase; };
	TArray<FFly> FlyData;''')
sub("WCDirector.cpp", '''	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
}''', '''	SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("Root")));
	Flies = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Flies"));
	Flies->SetupAttachment(GetRootComponent());
	Flies->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Flies->SetCastShadow(false);
	Flies->bAffectDistanceFieldLighting = false;
	Flies->bAffectDynamicIndirectLighting = false;
}''')
sub("WCDirector.cpp", '''	for (TActorIterator<AWCTrigger> It(GetWorld()); It; ++It) Triggers.Add(*It);''', '''	for (TActorIterator<AWCTrigger> It(GetWorld()); It; ++It) Triggers.Add(*It);
	// flies over everything that rots
	if (UStaticMesh* FlyMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")))
	{
		Flies->SetStaticMesh(FlyMesh);
		if (UMaterialInterface* FlyMat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Fly.M_Fly"))) Flies->SetMaterial(0, FlyMat);
		for (TActorIterator<AActor> It(GetWorld()); It; ++It)
		{
			if (!It->ActorHasTag(TEXT("Flies"))) continue;
			const FVector C = It->GetActorLocation();
			for (int32 i = 0; i < 12; ++i)
			{
				FFly F;
				F.Centre = C + FVector(Rng.FRandRange(-12.f, 12.f), Rng.FRandRange(-12.f, 12.f), Rng.FRandRange(-10.f, 10.f));
				F.Radii = FVector(Rng.FRandRange(14.f, 46.f), Rng.FRandRange(14.f, 46.f), Rng.FRandRange(6.f, 26.f));
				F.Freq = FVector(Rng.FRandRange(1.6f, 4.2f), Rng.FRandRange(1.6f, 4.2f), Rng.FRandRange(2.2f, 5.f));
				F.Phase = FVector(Rng.FRandRange(0.f, 6.28f), Rng.FRandRange(0.f, 6.28f), Rng.FRandRange(0.f, 6.28f));
				FlyData.Add(F);
				Flies->AddInstance(FTransform(FQuat::Identity, F.Centre, FVector(0.0055f, 0.0035f, 0.0035f)), true);
			}
			PlayAt(TEXT("flies_buzz"), C, 0.5f, Rng.FRandRange(0.94f, 1.06f), 700.f);
		}
	}''')
sub("WCDirector.cpp", '''	TickLights(Dt);
}''', '''	TickLights(Dt);
	TickFlies(Dt);
}

void AWCDirector::TickFlies(float Dt)
{
	const int32 N = FlyData.Num();
	if (N == 0) return;
	const float T = (float)Clock;
	for (int32 i = 0; i < N; ++i)
	{
		const FFly& F = FlyData[i];
		// two layered wobbles per axis: darting, never a clean orbit
		const FVector P = F.Centre + FVector(
			F.Radii.X * (FMath::Sin(T * F.Freq.X + F.Phase.X) * 0.7f + FMath::Sin(T * F.Freq.Y * 2.3f + F.Phase.Z) * 0.3f),
			F.Radii.Y * (FMath::Sin(T * F.Freq.Y + F.Phase.Y) * 0.7f + FMath::Sin(T * F.Freq.Z * 1.9f + F.Phase.X) * 0.3f),
			F.Radii.Z * FMath::Sin(T * F.Freq.Z + F.Phase.Z));
		Flies->UpdateInstanceTransform(i, FTransform(FQuat::Identity, P, FVector(0.0055f, 0.0035f, 0.0035f)), true, i == N - 1, true);
	}
}''')
sub("WCDirector.cpp", '#include "Components/AudioComponent.h"', '#include "Components/AudioComponent.h"\n#include "Components/InstancedStaticMeshComponent.h"\n#include "Engine/StaticMesh.h"\n#include "Materials/MaterialInterface.h"')
# PlayAt radius was unused: honour it loosely by scaling volume falloff (keeps one shared attenuation asset)
# ---------------------------------------------------------------- the lit window that goes dark when you knock
sub("WCStory.cpp", '''	ShowTagged(TEXT("Show_drawer"), Has(TEXT("phone_done")));''', '''	ShowTagged(TEXT("Show_drawer"), Has(TEXT("phone_done")));
	ShowTagged(TEXT("L_Welcome"), !Has(TEXT("knocked")));''')
sub("WCStory.cpp", '''			Set(TEXT("knocked"));
			PlayAt(TEXT("knock"), Pos(TEXT("FrontDoorPoint")), 1.f);''', '''			Set(TEXT("knocked"));
			PlayAt(TEXT("knock"), Pos(TEXT("FrontDoorPoint")), 1.f);
			After(2.2f, [this]() { ShowTagged(TEXT("L_Welcome"), false); });''')
print("ok")
