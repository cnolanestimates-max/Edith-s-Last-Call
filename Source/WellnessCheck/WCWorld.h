// World pieces the player touches: doors, notes, pickups, generic "use" spots and trigger boxes.
// Every one has a stable WCId; the story (AWCDirector) reacts to events named after it.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "WCWorld.generated.h"

class AWCCharacter;
class UStaticMeshComponent;
class UBoxComponent;

UCLASS()
class WELLNESSCHECK_API AWCInteractable : public AActor
{
	GENERATED_BODY()
public:
	AWCInteractable();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FName WCId;
	/** Verb shown next to the key hint, e.g. "Open", "Read". */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FString Prompt = TEXT("Use");
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") bool bEnabled = true;

	/** Half-size of an invisible "easy to aim at" box around the origin (0 = just the mesh). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FVector GrabExtent = FVector::ZeroVector;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FVector GrabOffset = FVector::ZeroVector;

	virtual FString GetPrompt() const { return Prompt; }
	virtual void Interact(AWCCharacter* By);
	virtual bool CanInteract() const { return bEnabled && !IsHidden(); }

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<USceneComponent> Root;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<UStaticMeshComponent> Mesh;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<UBoxComponent> Grab;
protected:
	virtual void BeginPlay() override;
};

/** Hinged door. The actor origin is the hinge; the mesh hangs off it. */
UCLASS()
class WELLNESSCHECK_API AWCDoor : public AWCInteractable
{
	GENERATED_BODY()
public:
	AWCDoor();
	virtual void Tick(float Dt) override;
	virtual void Interact(AWCCharacter* By) override;
	virtual FString GetPrompt() const override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") bool bLocked = false;
	/** Item that unlocks it. None = can only be unlocked by the story. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FName KeyId;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") float OpenAngle = 95.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") float SwingSeconds = 1.6f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") bool bStartOpen = false;

	bool IsOpen() const { return bOpen; }
	bool IsAjar() const { return bOpen && FMath::Abs(Target) < FMath::Abs(OpenAngle) * 0.7f; }
	void OpenAwayFrom(const FVector& From, float Seconds = -1.f);
	void SetOpen(bool bNewOpen, float Seconds = -1.f, bool bSilent = false);
	void SetAngle(float Degrees, float Seconds);
	void Slam();
	void SetLocked(bool bNewLocked) { bLocked = bNewLocked; }
	void Snap();

protected:
	virtual void BeginPlay() override;
	bool bOpen = false;
	float Angle = 0.f;
	float Target = 0.f;
	float Rate = 60.f;
	float BaseYaw = 0.f;
	bool bWasSolid = true;
};

UCLASS()
class WELLNESSCHECK_API AWCNote : public AWCInteractable
{
	GENERATED_BODY()
public:
	AWCNote();
	virtual void Interact(AWCCharacter* By) override;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FString Title;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC", meta = (MultiLine = true)) FString Body;
	/** 0 = typed/printed, 1 = her handwriting, 2 = child's writing. Only changes the look. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") int32 Style = 1;
};

UCLASS()
class WELLNESSCHECK_API AWCPickup : public AWCInteractable
{
	GENERATED_BODY()
public:
	AWCPickup();
	virtual void Interact(AWCCharacter* By) override;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FName ItemId;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FString DisplayName;
};

/** Something to look at. Shows a line of on-screen text (no voice) and raises "look:<WCId>". */
UCLASS()
class WELLNESSCHECK_API AWCLook : public AWCInteractable
{
	GENERATED_BODY()
public:
	AWCLook();
	virtual void Interact(AWCCharacter* By) override;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC", meta = (MultiLine = true)) FString Text;
};

/** Anything else you press E on. Raises the story event "use:<WCId>". */
UCLASS()
class WELLNESSCHECK_API AWCUsable : public AWCInteractable
{
	GENERATED_BODY()
public:
	virtual void Interact(AWCCharacter* By) override;
};

/** Box the player walks into. Raises "trig:<WCId>". */
UCLASS()
class WELLNESSCHECK_API AWCTrigger : public AActor
{
	GENERATED_BODY()
public:
	AWCTrigger();
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") FName WCId;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<UBoxComponent> Box;
	/** True while the point is inside the box. The director polls this; it decides what an entry means. */
	bool Contains(const FVector& P) const;
};

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
