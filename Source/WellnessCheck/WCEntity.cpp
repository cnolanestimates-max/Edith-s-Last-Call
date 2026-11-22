#include "WCEntity.h"
#include "WCEdithMouth.h"
#include "WCCharacter.h"
#include "WCDirector.h"
#include "Animation/AnimSequence.h"
#include "Components/PointLightComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "ReferenceSkeleton.h"

DEFINE_LOG_CATEGORY_STATIC(LogWCHer, Log, All);

AWCEntity::AWCEntity()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PrePhysics;
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);
	Body = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Body"));
	Body->SetupAttachment(Root);
	Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		Body->SetAnimationMode(EAnimationMode::AnimationSingleNode);
	Body->SetLightingChannels(true, true, false);
	Body->VisibilityBasedAnimTickOption = EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
	Body->bCastDynamicShadow = true;
	Body->SetBoundsScale(2.f);

	Mouth = CreateDefaultSubobject<UWCEdithMouth>(TEXT("Mouth"));
	Mouth->SetupAttachment(Body);
	Mouth->SetVisibility(false);
	Eye = CreateDefaultSubobject<USceneComponent>(TEXT("Eye"));
	Eye->SetupAttachment(Body);
	Eye->SetUsingAbsoluteRotation(true);
	auto MakeBall = [this](const TCHAR* Name)
	{
		UStaticMeshComponent* C = CreateDefaultSubobject<UStaticMeshComponent>(Name);
		C->SetupAttachment(Eye);
		C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		C->SetCastShadow(false);
		return C;
	};
	EyeBall = MakeBall(TEXT("EyeBall"));
	Iris = MakeBall(TEXT("Iris"));
	Pupil = MakeBall(TEXT("Pupil"));
	EyeGlint = CreateDefaultSubobject<UPointLightComponent>(TEXT("EyeGlint"));
	EyeGlint->SetupAttachment(Eye);
	EyeGlint->SetRelativeLocation(FVector(14.f, 0.f, 6.f));
	EyeGlint->SetIntensityUnits(ELightUnits::Lumens);
	EyeGlint->SetIntensity(0.f);
	EyeGlint->SetAttenuationRadius(90.f);
	EyeGlint->SetLightColor(FLinearColor(0.75f, 0.85f, 1.f));
	EyeGlint->SetCastShadows(false);
	FarLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("FarLight"));
	FarLight->SetupAttachment(Root);
	FarLight->SetRelativeLocation(FVector(80.f, 0.f, 160.f));
	FarLight->SetIntensityUnits(ELightUnits::Lumens);
	FarLight->SetIntensity(0.f);
	FarLight->SetAttenuationRadius(560.f);
	FarLight->SetLightColor(FLinearColor(0.72f, 0.82f, 1.f));
	FarLight->SetCastShadows(false);
	SetActorHiddenInGame(true);
}

FVector AWCEntity::RefPos(FName Bone) const
{
	const USkeletalMesh* SK = Body->GetSkeletalMeshAsset();
	if (!SK) return FVector::ZeroVector;
	const FReferenceSkeleton& Ref = SK->GetRefSkeleton();
	FTransform T = FTransform::Identity;
	for (int32 B = Ref.FindBoneIndex(Bone); B != INDEX_NONE; B = Ref.GetParentIndex(B)) T = T * Ref.GetRefBonePose()[B];
	return T.GetLocation();
}

void AWCEntity::BeginPlay()
{
	Super::BeginPlay();
	SetActorHiddenInGame(true);
	bShown = false;
	if (!Body->GetSkeletalMeshAsset()) return;

	// Work out which way the model faces from its own skeleton, so nothing depends on import conventions:
	// toes are in front of ankles, and her left arm is on her left.
	FVector Fwd = (RefPos(TEXT("LeftToeBase")) - RefPos(TEXT("LeftFoot"))) + (RefPos(TEXT("RightToeBase")) - RefPos(TEXT("RightFoot")));
	Fwd.Z = 0.f;
	if (!Fwd.Normalize()) Fwd = FVector(0, 1, 0);
	FVector Left = RefPos(TEXT("LeftArm")) - RefPos(TEXT("RightArm"));
	Left.Z = 0.f;
	Left -= Fwd * FVector::DotProduct(Left, Fwd);
	if (!Left.Normalize()) Left = FVector(1, 0, 0);
	const float MeshYaw = FMath::RadiansToDegrees(FMath::Atan2(Fwd.Y, Fwd.X));
	Body->SetRelativeRotation(FRotator(0.f, -MeshYaw, 0.f));
	UE_LOG(LogWCHer, Display, TEXT("WCHER mesh forward %s left %s -> body yaw %.1f"), *Fwd.ToString(), *Left.ToString(), -MeshYaw);

	// the eye: a glossy black ball where the modelled eye is, with a small pale iris and a pupil on its front
	UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	UMaterialInterface* Black = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_EyeBlack.M_EyeBlack"));
	UMaterialInterface* Pale = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_EyeIris.M_EyeIris"));
	const int32 HeadIdx = Body->GetBoneIndex(HeadBone);
	if (Sphere && HeadIdx != INDEX_NONE)
	{
		const FVector EyeMesh = Left * EyeRef.X + Fwd * EyeRef.Y + FVector(0, 0, EyeRef.Z);
		const USkeletalMesh* SK = Body->GetSkeletalMeshAsset();
		const FReferenceSkeleton& Ref = SK->GetRefSkeleton();
		FTransform RefHead = FTransform::Identity;
		for (int32 B = HeadIdx; B != INDEX_NONE; B = Ref.GetParentIndex(B)) RefHead = RefHead * Ref.GetRefBonePose()[B];
		Eye->AttachToComponent(Body, FAttachmentTransformRules::KeepRelativeTransform, HeadBone);
		Eye->SetRelativeLocation(RefHead.InverseTransformPosition(EyeMesh));
		Mouth->Fit(Body, HeadBone, RefHead, Left, Fwd);
		const float R = EyeRadius;
		EyeBall->SetStaticMesh(Sphere);
		EyeBall->SetRelativeScale3D(FVector(R / 50.f));
		Iris->SetStaticMesh(Sphere);
		Iris->SetRelativeLocation(FVector(R * 0.80f, 0.f, 0.f));
				Iris->SetRelativeScale3D(FVector(R * 0.30f / 50.f, R * 0.34f / 50.f, R * 0.34f / 50.f));
		Pupil->SetStaticMesh(Sphere);
		Pupil->SetRelativeLocation(FVector(R * 0.985f, 0.f, 0.f));
				Pupil->SetRelativeScale3D(FVector(R * 0.14f / 50.f, R * 0.16f / 50.f, R * 0.16f / 50.f));
		if (Black) { EyeBall->SetMaterial(0, Black); Pupil->SetMaterial(0, Black); }
		if (Pale) Iris->SetMaterial(0, Pale);
		bEyeReady = true;
	}
}

// ---- her face: twenty shape keys (Scripts/her/build_her.py makes them; keep the two lists alike)
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

	UAnimSequence* Seq = Anims.FindRef(Anim);
	if (!Seq) { UE_LOG(LogWCHer, Warning, TEXT("WCHER no clip %s"), *Anim.ToString()); return; }
	if (CurrentAnim != Anim || !Body->IsPlaying())
	{
		Body->PlayAnimation(Seq, bLoop);
		CurrentAnim = Anim;
	}
	Body->SetPlayRate(Rate);
	// the mouth: wide open whenever she is coming for you
	static const TMap<FName, float> Mouths = { { TEXT("Run"), 1.f }, { TEXT("Lunge"), 1.f }, { TEXT("Rise"), 1.f }, { TEXT("Crawl"), 0.9f }, { TEXT("Under"), 0.35f } };
	const float* M = Mouths.Find(Anim);
	SetScream(M ? *M : 0.f);
	// and the rest of her face
	static const TMap<FName, FName> Faces = { { TEXT("Idle"), TEXT("watch") }, { TEXT("Peek"), TEXT("watch") }, { TEXT("Walk"), TEXT("snarl") }, { TEXT("Tall"), TEXT("grin") },
		{ TEXT("Sit"), TEXT("grief") }, { TEXT("Under"), TEXT("hush") }, { TEXT("Crawl"), TEXT("snarl") }, { TEXT("Rise"), TEXT("rage") }, { TEXT("Run"), TEXT("rage") }, { TEXT("Lunge"), TEXT("rage") } };
	const FName* F = Faces.Find(Anim);
	ClipMood = F ? *F : FName(TEXT("watch"));
	if (MoodLeft <= 0.f) Mood = ClipMood;
}


void AWCEntity::Appear(const FVector& Loc, float Yaw, FName Anim, bool bLoop, float Rate)
{
	Mouth->Close();
	TongueExtension = 0.f;
	AccusationAge = -1.f;
	StopMoving();
	SetActorLocationAndRotation(Loc, FRotator(0.f, Yaw, 0.f));
	CurrentAnim = NAME_None;
	SetActorHiddenInGame(false);
	bShown = true;
	Play(Anim, bLoop, Rate);
	Body->TickAnimation(0.f, false);
	Body->RefreshBoneTransforms();
	EyeQuat = GetActorQuat();
}

bool AWCEntity::IsMouthOpen() const { return Mouth->IsOpen(); }

void AWCEntity::Vanish()
{
	Mouth->Close();
	TongueExtension = 0.f;
	AccusationAge = -1.f;
	GazeTarget.Reset();
	StopMoving();
	SetActorHiddenInGame(true);
	bShown = false;
	bFacePlayer = false;
	EyeGlint->SetIntensity(0.f);
	FarLight->SetIntensity(0.f);
	FarGlow = DefaultFarGlow;
	FarLight->SetLightColor(FLinearColor(.72f,.82f,1.f));
	if (IrisMID) IrisMID->SetScalarParameterValue(TEXT("Glow"), 0.06f);
	Eye->SetRelativeScale3D(FVector(1.f));
	ScreamTarget = ScreamAlpha = 0.f;
	for (int32 k = 0; k < F_Num; ++k) { FaceNow[k] = 0.f; Body->SetMorphTarget(GFaceNames[k], 0.f); }
	MoodLeft = 0.f;
	Body->Stop();

	CurrentAnim = NAME_None;
}

void AWCEntity::SetGlow(float Lumens)
{
	EyeGlint->SetIntensity(Lumens);
}

void AWCEntity::SetEyeShine(float Glow, float Swell)
{
	Eye->SetRelativeScale3D(FVector(Swell));
	if (!IrisMID)
	{
		UMaterialInterface* M = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_EyeIrisGlow.M_EyeIrisGlow"));
		if (!M || !Iris) return;
		IrisMID = UMaterialInstanceDynamic::Create(M, this);
		Iris->SetMaterial(0, IrisMID);
	}
	IrisMID->SetScalarParameterValue(TEXT("Glow"), Glow);
}

void AWCEntity::StopMoving()
{
	Path.Reset();
	MoveDone = nullptr;
	SlideT = -1.f;
	SlideDone = nullptr;
}

void AWCEntity::SetYaw(float Yaw)
{
	SetActorRotation(FRotator(0.f, Yaw, 0.f));
}

void AWCEntity::MoveAlong(const TArray<FVector>& Points, float Speed, FName Anim, TFunction<void()> OnDone)
{
	Path = Points;
	PathIndex = 0;
	MoveSpeed = Speed;
	MoveDone = MoveTemp(OnDone);
	const float Authored = AnimSpeeds.FindRef(Anim);
	Play(Anim, true, Authored > 1.f ? FMath::Clamp(Speed / Authored, 0.4f, 2.5f) : 1.f);
}

void AWCEntity::Slide(const FVector& To, float Seconds, TFunction<void()> OnDone)
{
	SlideFrom = GetActorLocation();
	SlideTo = To;
	SlideT = 0.f;
	SlideDur = FMath::Max(Seconds, 0.01f);
	SlideDone = MoveTemp(OnDone);
}

FVector AWCEntity::HeadLocation() const
{
	const int32 Bone = Body->GetBoneIndex(HeadBone);
	return Bone != INDEX_NONE ? Body->GetBoneLocation(HeadBone) + FVector(0, 0, 14) : GetActorLocation() + FVector(0, 0, 200);
}

FVector AWCEntity::EyeLocation() const
{
	return bEyeReady ? Eye->GetComponentLocation() : HeadLocation();
}

float AWCEntity::DistToPlayer() const
{
	const APawn* P = UGameplayStatics::GetPlayerPawn(this, 0);
	return P ? FVector::Dist2D(P->GetActorLocation(), GetActorLocation()) : 1e6f;
}

bool AWCEntity::SegmentHits(const FVector& A, const FVector& B) const
{
	const FVector Feet = GetActorLocation();
	const FVector Top = HeadLocation();
	FVector P1, P2;
	FMath::SegmentDistToSegment(A, B, Feet, Top, P1, P2);
	return FVector::Dist(P1, P2) < 42.f;
}

// Aperture of the recorded vowels, the consonant before "me", and the final release.
static float AccusationJaw(float T)
{
	static constexpr float Keys[][2] = {{0,.19f},{.19f,.14f},{.31f,.30f},{.4f,.63f},{.53f,.45f},{.69f,.58f},
		{.86f,.69f},{1.02f,.27f},{1.12f,.12f},{1.23f,.49f},{1.40f,.88f},{1.58f,1.f},{2.18f,.94f},
		{2.70f,.99f},{3.05f,.94f},{3.33f,.85f},{3.48f,.59f},{3.70f,.24f},{4.05f,.055f},{4.28f,0.f}};
	for (int32 I = 1; I < UE_ARRAY_COUNT(Keys); ++I)
		if (T <= Keys[I][0]) return FMath::Lerp(Keys[I-1][1], Keys[I][1], FMath::SmoothStep(Keys[I-1][0], Keys[I][0], T));
	return 0.f;
}

void AWCEntity::Tick(float Dt)
{
	Super::Tick(Dt);
	if (!bShown) return;
	// beyond his flashlight she is a pale shape in the dark; inside it, his light does the work
	FarLight->SetIntensity(FarGlow * FMath::Clamp((DistToPlayer() - 230.f) / 260.f, 0.f, 1.f) * (1.f + 1.6f * FMath::Clamp((DistToPlayer() - 600.f) / 900.f, 0.f, 1.f)));       // further off, she has to be brighter to be seen at all
	{
		// her face is never still: the jaw works when she speaks and hangs a little when she breathes, the brow
		// creeps, and one side of her mouth twitches up off the teeth
		ScreamAlpha = FMath::FInterpConstantTo(ScreamAlpha, ScreamTarget, Dt, ScreamTarget > ScreamAlpha ? 7.f : 2.2f);
		FaceT += Dt;
		TalkLeft = FMath::Max(0.f, TalkLeft - Dt);
		TwitchLeft = FMath::Max(0.f, TwitchLeft - Dt);
		if (FaceT > NextTwitch)
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
		}
		const bool SeatedReflection = CurrentAnim == TEXT("Wheelchair");
		const bool Performing = AccusationAge >= 0.f && !SeatedReflection;
		float Jaw = SeatedReflection ? 0.f : FMath::Clamp((FaceNow[F_Scream] - .07f) / .93f, 0.f, 1.f);
		if (Performing)
		{
			Jaw = AccusationJaw(AccusationAge);
			TongueExtension = .72f * FMath::SmoothStep(1.12f, 2.1f, AccusationAge) * (1.f - FMath::SmoothStep(2.86f, 3.52f, AccusationAge));
			AccusationAge += Dt;
			if (AccusationAge > 4.28f) AccusationAge = -1.f;
		}
		else
		{
			const float Reach = FMath::SmoothStep(.49f, .91f, Jaw) * (.85f + .15f * FMath::Sin(FaceT * 1.8f));
			TongueExtension = FMath::FInterpConstantTo(TongueExtension, Reach, Dt, Reach > TongueExtension ? 1.45f : 3.4f);
		}
		for (int32 K = 0; K < F_Num; ++K)
		{
			float V = FaceNow[K];
			if (K == F_Scream || K == F_Unhinge || K == F_Stretch) V = Jaw;
			Body->SetMorphTarget(GFaceNames[K], V);
		}
		Mouth->Pose(Jaw, TongueExtension, FaceT);

	}


	if (SlideT >= 0.f)
	{
		SlideT += Dt;
		const float U = FMath::Clamp(SlideT / SlideDur, 0.f, 1.f);
		SetActorLocation(FMath::Lerp(SlideFrom, SlideTo, FMath::InterpEaseInOut(0.f, 1.f, U, 2.f)));
		if (U >= 1.f)
		{
			SlideT = -1.f;
			TFunction<void()> Fn = MoveTemp(SlideDone);
			SlideDone = nullptr;
			if (Fn) Fn();
		}
	}
	else if (Path.Num() > 0)
	{
		float Budget = MoveSpeed * Dt;
		FVector Loc = GetActorLocation();
		while (Budget > 0.f && PathIndex < Path.Num())
		{
			const FVector To = Path[PathIndex] - Loc;
			const float D = To.Size();
			if (D <= Budget) { Loc = Path[PathIndex]; Budget -= D; ++PathIndex; }
			else
			{
				Loc += To / D * Budget;
				Budget = 0.f;
				const FRotator Want(0.f, To.Rotation().Yaw, 0.f);
				SetActorRotation(FMath::RInterpTo(GetActorRotation(), Want, Dt, 9.f));
			}
		}
		// her feet: bare, heavy, wet on old boards.  You hear her before you see her.
		StepAcc += MoveSpeed * Dt;
		const float Stride = FMath::Clamp(MoveSpeed * 0.42f, 62.f, 175.f);
		if (StepAcc >= Stride)
		{
			StepAcc = 0.f;
			if (AWCDirector* D = AWCDirector::Get(this))
			{
				D->PlayAt(TEXT("her_step"), Loc + FVector(0, 0, 10), 1.f, FMath::FRandRange(0.9f, 1.08f), 3400.f);
				if (FMath::FRand() < 0.55f) D->PlayAt(TEXT("creak"), Loc, 0.6f, FMath::FRandRange(0.8f, 1.0f), 2600.f);
			}
		}
		SetActorLocation(Loc);
		if (PathIndex >= Path.Num())
		{
			Path.Reset();
			TFunction<void()> Fn = MoveTemp(MoveDone);
			MoveDone = nullptr;
			if (Fn) Fn();
		}
	}
	if (bFacePlayer && Path.Num() == 0)
	{
		if (const APawn* P = UGameplayStatics::GetPlayerPawn(this, 0))
		{
			const FRotator Want(0.f, (P->GetActorLocation() - GetActorLocation()).Rotation().Yaw, 0.f);
			SetActorRotation(FMath::RInterpTo(GetActorRotation(), Want, Dt, 5.f));
		}
	}

	// the eye finds the player, but cannot turn further than an eye can
	if (bEyeReady)
	{
		// In the doorway performance the spine turns the whole body around a stationary root.
		const FQuat HeadFwd = CurrentAnim == TEXT("CeilingCorner")
			? (BoneWorld(TEXT("headfront")) - BoneWorld(HeadBone)).ToOrientationQuat() : GetActorQuat();
		FQuat Want = HeadFwd;
		if (const AWCCharacter* P = Cast<AWCCharacter>(UGameplayStatics::GetPlayerPawn(this, 0)))
		{
			const FVector To = (GazeTarget.Get(P->EyeLocation()) - Eye->GetComponentLocation()).GetSafeNormal();
			const FVector F = HeadFwd.GetForwardVector();
			const float Ang = FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(FVector::DotProduct(To, F), -1.f, 1.f)));
			const FVector Aim = Ang > 42.f ? FMath::VInterpNormalRotationTo(F, To, 1.f, 42.f) : To;
			Want = Aim.ToOrientationQuat();
		}
		EyeQuat = FQuat::Slerp(EyeQuat, Want, 1.f - FMath::Exp(-14.f * Dt)).GetNormalized();
		Eye->SetWorldRotation(EyeQuat);
	}
}

FVector AWCEntity::BoneWorld(FName Bone) const
{
	return Body && Body->GetBoneIndex(Bone) != INDEX_NONE ? Body->GetBoneLocation(Bone) : GetActorLocation();
}
