"""Cheyenne 21:27-21:29: 'something has been there the whole time and you just didn't know it'.
AWCWatcher: her eye in a hole in the wall (it follows you; if you look straight at it, it is gone), or a hank of her hair hanging
from a gap overhead (it is drawn back up when you notice it or come close).  No sting, no scream.
And the bookshelf scare: the settlers book holds Walter's desk key; pull it out and her eye is in the hole behind it."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"

# ---------------------------------------------------------------- WCWorld.h
p = R + "WCWorld.h"
s = io.open(p, encoding="utf-8").read()
assert "AWCWatcher" not in s
s = s.rstrip() + '''

/** She has been there the whole time.  Kind 0: an eye in a hole (follows you; withdraws when you look straight at it).
 *  Kind 1: her hair hanging from a gap overhead (drawn back up when noticed or approached).  Raises "watcher:<WCId>". */
UCLASS()
class WELLNESSCHECK_API AWCWatcher : public AActor
{
	GENERATED_BODY()
public:
	AWCWatcher();
	virtual void Tick(float Dt) override;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FName WCId;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") int32 Kind = 0;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") float Radius = 5.2f;
	/** Scripted watchers (the one behind the book) stay hidden until the story shows them, and never leave by themselves. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") bool bScripted = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<USceneComponent> Root;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<USceneComponent> Turn;
	void Reveal();
	void Withdraw(bool bQuiet = false);
	bool IsOut() const { return bOut; }

protected:
	virtual void BeginPlay() override;

private:
	bool bOut = false;          // visible and watching
	bool bGone = false;         // has withdrawn for good
	float Seen = 0.f;
	float LeaveT = -1.f;
	FVector Home = FVector::ZeroVector;
	FQuat HomeQuat = FQuat::Identity;
};
'''
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# ---------------------------------------------------------------- WCWorld.cpp
p = R + "WCWorld.cpp"
s = io.open(p, encoding="utf-8").read()
s = s.replace('#include "Components/StaticMeshComponent.h"', '#include "Components/StaticMeshComponent.h"\n#include "Engine/StaticMesh.h"\n#include "Materials/MaterialInterface.h"', 1)
s = s.rstrip() + '''

// ---------------------------------------------------------------------------------------------- watcher
AWCWatcher::AWCWatcher()
{
	PrimaryActorTick.bCanEverTick = true;
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);
	Turn = CreateDefaultSubobject<USceneComponent>(TEXT("Turn"));
	Turn->SetupAttachment(Root);
}

void AWCWatcher::BeginPlay()
{
	Super::BeginPlay();
	Home = GetActorLocation();
	HomeQuat = GetActorQuat();
	UMaterialInterface* Black = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_EyeBlack.M_EyeBlack"));
	UMaterialInterface* Pale = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_EyeIris.M_EyeIris"));
	UMaterialInterface* Hair = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Hair.M_Hair"));
	auto Part = [this](UStaticMesh* Mesh, const FVector& Loc, const FVector& Scale, UMaterialInterface* Mat, const FRotator& Rot = FRotator::ZeroRotator)
	{
		UStaticMeshComponent* C = NewObject<UStaticMeshComponent>(this);
		C->SetupAttachment(Turn);
		C->SetStaticMesh(Mesh);
		C->SetRelativeLocation(Loc);
		C->SetRelativeRotation(Rot);
		C->SetRelativeScale3D(Scale);
		C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		C->SetCastShadow(false);
		C->SetLightingChannels(true, true, false);
		if (Mat) C->SetMaterial(0, Mat);
		C->RegisterComponent();
	};
	if (Kind == 0)
	{
		if (UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")))
		{
			const float R = Radius;
			Part(Sphere, FVector::ZeroVector, FVector(R / 50.f), Black);
			Part(Sphere, FVector(R * 0.80f, 0.f, 0.f), FVector(R * 0.30f / 50.f, R * 0.34f / 50.f, R * 0.34f / 50.f), Pale);
			Part(Sphere, FVector(R * 0.985f, 0.f, 0.f), FVector(R * 0.14f / 50.f, R * 0.16f / 50.f, R * 0.16f / 50.f), Black);
		}
	}
	else if (UStaticMesh* Cyl = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")))
	{
		// a hank of long grey-blonde hair: a few dozen strands of uneven length hanging from the actor's origin
		FRandomStream Rs(GetTypeHash(WCId) + 7);
		for (int32 i = 0; i < 46; ++i)
		{
			const float Len = Rs.FRandRange(55.f, 150.f) * (Radius / 5.2f);
			const float Thick = Rs.FRandRange(0.35f, 0.9f);
			const FVector Off(Rs.FRandRange(-9.f, 9.f), Rs.FRandRange(-5.f, 5.f), -Len * 0.5f);
			Part(Cyl, Off, FVector(Thick / 100.f, Thick / 100.f, Len / 100.f), Hair, FRotator(Rs.FRandRange(-2.5f, 2.5f), 0.f, Rs.FRandRange(-2.5f, 2.5f)));
		}
	}
	bOut = !bScripted;
	SetActorHiddenInGame(bScripted);
}

void AWCWatcher::Reveal()
{
	if (bGone) return;
	SetActorLocationAndRotation(Home, HomeQuat);
	SetActorHiddenInGame(false);
	bOut = true;
	LeaveT = -1.f;
}

void AWCWatcher::Withdraw(bool bQuiet)
{
	if (!bOut || LeaveT >= 0.f) return;
	LeaveT = 0.f;
	if (AWCDirector* D = AWCDirector::Get(this))
	{
		if (!bQuiet) D->PlayAt(Kind == 0 ? TEXT("skitter") : TEXT("scratch_wall"), Home, 0.9f, Kind == 0 ? 1.f : 1.2f, 1400.f);
		D->Event(FName(*FString::Printf(TEXT("watcher:%s"), *WCId.ToString())));
	}
}

void AWCWatcher::Tick(float Dt)
{
	Super::Tick(Dt);
	if (!bOut) return;
	AWCDirector* D = AWCDirector::Get(this);
	AWCCharacter* P = D ? D->Player() : nullptr;
	if (!P) return;
	if (LeaveT >= 0.f)
	{
		// going: the eye sinks back into the dark; the hair is drawn up out of sight
		LeaveT += Dt;
		const float Dur = Kind == 0 ? 0.22f : 1.5f;
		const float U = FMath::Clamp(LeaveT / Dur, 0.f, 1.f);
		const FVector Away = Kind == 0 ? -HomeQuat.GetForwardVector() * (Radius * 3.2f) : FVector(0, 0, 190.f * (Radius / 5.2f));
		SetActorLocation(Home + Away * (Kind == 0 ? U : U * U));
		if (U >= 1.f) { bOut = false; bGone = !bScripted; SetActorHiddenInGame(true); }
		return;
	}
	const FVector Eye = P->EyeLocation();
	const float Dist = FVector::Dist(Eye, Home);
	if (Kind == 0)
	{
		// it follows you, as far as an eye can turn in its socket
		const FVector Local = HomeQuat.UnrotateVector((Eye - Home).GetSafeNormal());
		FRotator Want = Local.Rotation();
		Want.Yaw = FMath::Clamp(Want.Yaw, -52.f, 52.f);
		Want.Pitch = FMath::Clamp(Want.Pitch, -45.f, 45.f);
		Turn->SetRelativeRotation(FMath::RInterpTo(Turn->GetRelativeRotation(), Want, Dt, 5.f));
	}
	else
	{
		// the faintest sway
		Turn->SetRelativeRotation(FRotator(FMath::Sin(GetWorld()->GetTimeSeconds() * 0.9f + Home.X) * 1.6f, 0.f, FMath::Sin(GetWorld()->GetTimeSeconds() * 0.7f + Home.Y) * 1.3f));
	}
	if (bScripted || !D->Has(TEXT("inside"))) return;
	const FVector Mid = Kind == 0 ? Home : Home - FVector(0, 0, 55.f);
	const bool bLooked = Dist < 1100.f && D->PlayerSees(Mid, Kind == 0 ? 0.988f : 0.965f, 1100.f) && P->IsFlashlightOn();
	Seen = bLooked ? Seen + Dt : FMath::Max(0.f, Seen - Dt * 0.5f);
	if (Seen > (Kind == 0 ? 0.55f : 0.9f) || Dist < (Kind == 0 ? 120.f : 230.f)) Withdraw();
}
'''
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# ---------------------------------------------------------------- the bookshelf scare
edit(R + "WCDirector.h", [('''	void ScareSewing();''', '''	void ScareSewing();
	void ScareBook();''')])
edit(R + "WCHouse.cpp", [
    ('''	if (Id == TEXT("take:key_desk")) { Think(TEXT("Too small for a door. A desk, maybe.")); return true; }''',
     '''if (Id == TEXT("take:key_desk")) { Think(TEXT("The key was in the book. Walter's desk.")); return true; }
	if (Id == TEXT("use:book_settlers"))
	{
		if (Has(TEXT("book_done"))) return true;
		if (!NotesRead.Contains(TEXT("note_deskkey")))
		{
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Think(TEXT("County histories. One spine is cleaner than the rest: 'Customs of the First Settlers'.")); }
			return true;
		}
		ScareBook();
		return true;
	}
	if (S.StartsWith(TEXT("watcher:")))
	{
		// nothing happens.  That is the point.  (The house just breathes a little closer.)
		Tension = FMath::Min(1.f, Tension + 0.12f);
		if (!Has(TEXT("watcher_seen"))) { Set(TEXT("watcher_seen")); After(1.8f, [this]() { Think(TEXT("...Was that")); }); }
		return true;
	}'''),
])
p = R + "WCHouse.cpp"
s = io.open(p, encoding="utf-8").read()
s = s.rstrip() + '''

// ================================================================================================ S10: the book
void AWCDirector::ScareBook()
{
	Set(TEXT("book_done"));
	UE_LOG(LogWCHouse, Display, TEXT("WCSCARE t=%.1f S10_book"), PlaySeconds);
	AWCCharacter* P = Player();
	AActor* Book = Find(TEXT("SettlersBook"));
	AWCWatcher* EyeW = nullptr;
	for (TActorIterator<AWCWatcher> It(GetWorld()); It; ++It) if (It->WCId == TEXT("book_eye")) EyeW = *It;
	if (AWCInteractable* U = Thing(TEXT("book_settlers"))) U->bEnabled = false;
	if (!P || !Book) { GiveItem(TEXT("key_desk"), TEXT("Small desk key")); return; }
	bBusy = true;
	P->SetInputLocked(true);
	Play2D(TEXT("paper"), 0.8f, EWCSnd::SFX, 0.7f);
	const FVector From = Book->GetActorLocation();
	const FVector Out = (P->GetActorLocation() - From).GetSafeNormal2D();
	// he draws the book out...
	for (int32 i = 1; i <= 14; ++i) After(i * 0.035f, [Book, From, Out, i]() { if (IsValid(Book)) Book->SetActorLocation(From + Out * (26.f * i / 14.f)); });
	if (EyeW) EyeW->Reveal();
	// ...and she is looking at him through the wall
	After(0.95f, [this, EyeW, Book, From, Out]()
	{
		AWCCharacter* Pl = Player();
		Play2D(TEXT("sting_hit"), 0.9f, EWCSnd::Music);
		Play2D(TEXT("breath_near"), 0.9f);
		if (Pl) { Pl->AddShake(0.9f); Pl->FlickerLight(0.5f, 0.85f); }
		Tension = 1.f;
		// the book goes out of his hand
		const FVector Start = From + Out * 26.f;
		const float FloorZ = FMath::FloorToFloat((From.Z + 20.f) / 350.f) * 350.f + 3.f;
		for (int32 i = 1; i <= 16; ++i)
		{
			After(i * 0.03f, [Book, Start, Out, FloorZ, i]()
			{
				if (!IsValid(Book)) return;
				const float U = i / 16.f;
				Book->SetActorLocation(FVector(Start.X + Out.X * 22.f * U, Start.Y + Out.Y * 22.f * U, FMath::Lerp(Start.Z, FloorZ, U * U)));
				Book->SetActorRotation(FRotator(70.f * U, Book->GetActorRotation().Yaw + 9.f, 80.f * U));
			});
		}
		After(0.5f, [this, Start, Out, FloorZ]()
		{
			PlayAt(TEXT("thump_far"), FVector(Start.X, Start.Y, FloorZ), 1.f, 1.5f, 900.f);
			ShowTagged(TEXT("Show_bookkey"), true);
		});
		// she is away along the inside of the wall
		After(0.55f, [this, EyeW]()
		{
			if (EyeW)
			{
				const FVector At = EyeW->GetActorLocation();
				const FVector Along = EyeW->GetActorRightVector();
				EyeW->Withdraw(true);
				for (int32 k = 0; k < 6; ++k) After(k * 0.28f, [this, At, Along, k]() { PlayAt(k % 2 ? TEXT("skitter") : TEXT("scratch_wall"), At + Along * (120.f * k) + FVector(0, 0, 30.f * k), 1.f, 1.1f, 1600.f); });
			}
		});
	});
	After(2.9f, [this]()
	{
		if (AWCCharacter* Pl = Player()) Pl->SetInputLocked(false);
		bBusy = false;
		Rest(120.f);
		Tension = 0.6f;
		Think(TEXT("She's in the walls."));
		Checkpoint(TEXT("book"));
	});
}
'''
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
edit(R + "WCStory.cpp", [
    ('''	ShowTagged(TEXT("Hide_shears"), !HasItem(TEXT("shears")));''', '''	ShowTagged(TEXT("Hide_shears"), !HasItem(TEXT("shears")));
	ShowTagged(TEXT("Show_bookkey"), Has(TEXT("book_done")) && !HasItem(TEXT("key_desk")) && !Has(TEXT("desk_open")));
	if (AWCInteractable* Bk = Thing(TEXT("book_settlers"))) Bk->bEnabled = !Has(TEXT("book_done"));
	ShowTagged(TEXT("SettlersBook"), !Has(TEXT("book_done")) || LastCheckpoint == TEXT("book"));'''),
])
print("ok")
