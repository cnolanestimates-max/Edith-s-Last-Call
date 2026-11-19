"""Inventory (Cheyenne 23:46 UTC): Tab or I opens it and pauses the game.  A list of what he carries; each thing can be
Used, Inspected (it turns in front of you, lit, against black: drag to turn it, wheel to zoom) or Dropped (only things the
story no longer needs).  A second page lists every paper he has read, to read again.  Nothing new to save: it shows the
same Items and NotesRead that checkpoints already keep."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"

# ================================================================= the player: the thing held up in front of the camera
edit(R + "WCCharacter.h", [
    ('''	void SetAiming(bool bAim) { bAiming = bAim; }''', '''	void SetAiming(bool bAim) { bAiming = bAim; }

	// inventory: one thing held up in front of the camera, lit by its own lamps, against black
	void ShowInspect(UStaticMesh* InMesh, const TArray<UMaterialInterface*>& Mats, const FVector& PartScale);
	void SetInspectView(const FQuat& Rot, float Zoom);
	void HideInspect();
	bool IsInspectFlat() const;'''),
    ('''	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UInstancedStaticMeshComponent> Dust;''', '''	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UInstancedStaticMeshComponent> Dust;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UStaticMeshComponent> InspectMesh;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UStaticMeshComponent> InspectBack;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> InspectKey;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> InspectFill;'''),
    ('''	float AimDist = 600.f;''', '''	float AimDist = 600.f;
	FVector InspectPart = FVector::OneVector;'''),
    ('''class UStaticMeshComponent;''', '''class UStaticMeshComponent;
class UStaticMesh;
class UMaterialInterface;'''),
])
edit(R + "WCCharacter.cpp", [
    ('''	Dust = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Dust"));''', '''	InspectBack = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("InspectBack"));
	InspectBack->SetupAttachment(Cam);
	InspectBack->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	InspectBack->SetCastShadow(false);
	InspectBack->SetRelativeLocation(FVector(33.f, 0.f, 0.f));
	InspectBack->SetRelativeScale3D(FVector(0.01f, 6.f, 6.f));
	InspectBack->SetHiddenInGame(true);
	InspectBack->bAffectDynamicIndirectLighting = false;
	InspectBack->bAffectDistanceFieldLighting = false;
	InspectMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("InspectMesh"));
	InspectMesh->SetupAttachment(Cam);
	InspectMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	InspectMesh->SetCastShadow(false);
	InspectMesh->SetLightingChannels(false, false, true);
	InspectMesh->SetHiddenInGame(true);
	InspectMesh->bAffectDynamicIndirectLighting = false;
	InspectMesh->bAffectDistanceFieldLighting = false;
	for (int32 i = 0; i < 2; ++i)
	{
		UPointLightComponent* L = CreateDefaultSubobject<UPointLightComponent>(i == 0 ? TEXT("InspectKey") : TEXT("InspectFill"));
		L->SetupAttachment(Cam);
		L->SetRelativeLocation(i == 0 ? FVector(3.f, -15.f, 13.f) : FVector(6.f, 17.f, -9.f));
		L->SetIntensityUnits(ELightUnits::Lumens);
		L->SetIntensity(0.f);
		L->SetAttenuationRadius(90.f);
		L->SetLightColor(i == 0 ? FLinearColor(1.f, 0.9f, 0.76f) : FLinearColor(0.6f, 0.7f, 1.f));
		L->SetCastShadows(false);
		L->SetVolumetricScatteringIntensity(0.f);
		L->SetLightingChannels(false, false, true);
		(i == 0 ? InspectKey : InspectFill) = L;
	}

	Dust = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Dust"));'''),
])
s = io.open(R + "WCCharacter.cpp", encoding="utf-8").read()
if "AWCCharacter::ShowInspect" not in s:
    s = s.rstrip() + '''

// ---------------------------------------------------------------------------------------------- inventory: the thing held up
void AWCCharacter::ShowInspect(UStaticMesh* InMesh, const TArray<UMaterialInterface*>& Mats, const FVector& PartScale)
{
	if (!InspectBack->GetStaticMesh())
	{
		InspectBack->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
		InspectBack->SetMaterial(0, LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Void.M_Void")));
	}
	InspectBack->SetHiddenInGame(false);
	GunPivot->SetHiddenInGame(true, true);
	FlashHand->SetHiddenInGame(true, true);
	InspectPart = PartScale;
	InspectMesh->SetStaticMesh(InMesh);
	InspectMesh->EmptyOverrideMaterials();
	for (int32 i = 0; i < Mats.Num(); ++i) if (Mats[i]) InspectMesh->SetMaterial(i, Mats[i]);
	InspectMesh->SetHiddenInGame(InMesh == nullptr);
	InspectKey->SetIntensity(InMesh ? 150.f : 0.f);
	InspectFill->SetIntensity(InMesh ? 45.f : 0.f);
}

bool AWCCharacter::IsInspectFlat() const
{
	const UStaticMesh* M = InspectMesh->GetStaticMesh();
	if (!M) return false;
	const FVector E = M->GetBounds().BoxExtent * InspectPart;
	return E.Z < 0.42f * FMath::Min(E.X, E.Y) || E.Z < 0.16f * FMath::Max(E.X, E.Y);
}

void AWCCharacter::SetInspectView(const FQuat& Rot, float Zoom)
{
	const UStaticMesh* M = InspectMesh->GetStaticMesh();
	if (!M) return;
	const FBoxSphereBounds B = M->GetBounds();
	const float Radius = FMath::Max((B.BoxExtent * InspectPart).Size(), 0.3f);
	const FVector Scale = InspectPart * (6.2f * Zoom / Radius);
	InspectMesh->SetRelativeScale3D(Scale);
	InspectMesh->SetRelativeRotation(Rot);
	InspectMesh->SetRelativeLocation(FVector(21.f, 0.f, 1.4f) - Rot.RotateVector(B.Origin * Scale));
}

void AWCCharacter::HideInspect()
{
	InspectBack->SetHiddenInGame(true);
	InspectMesh->SetHiddenInGame(true);
	InspectKey->SetIntensity(0.f);
	InspectFill->SetIntensity(0.f);
	GunPivot->SetHiddenInGame(false, true);
	FlashHand->SetHiddenInGame(false, true);
}
'''
    io.open(R + "WCCharacter.cpp", "w", encoding="utf-8", newline="\n").write(s)

# ================================================================= story side: what using a thing from the bag does
edit(R + "WCDirector.cpp", [
    ('''	if (!DisplayName.IsEmpty()) ShowToast(FString::Printf(TEXT("Taken: %s"), *DisplayName));''',
     '''	if (!DisplayName.IsEmpty()) ShowToast(FString::Printf(TEXT("Taken: %s"), *DisplayName));
	if (!Item.ToString().StartsWith(TEXT("ammo")) && !Has(TEXT("inv_hint"))) { Set(TEXT("inv_hint")); ShowHint(TEXT("Tab: what you are carrying"), 7.f); }'''),
])
edit(R + "WCHouse.cpp", [
    ('''	if (Id == TEXT("use:fusebox"))''', '''	if (Id == TEXT("invuse:radio"))
	{
		Play2D(TEXT("radio_static"), 0.6f);
		Think(Has(TEXT("locked_in")) ? TEXT("Static. Nothing gets out of this house.") : TEXT("Dispatch reads me fine out here."));
		return true;
	}
	if (Id == TEXT("invuse:keep_ruth"))
	{
		// it still plays; and somewhere in the house something hums along
		TWeakObjectPtr<UAudioComponent> Box = Play2D(TEXT("musicbox"), 0.55f);
		After(6.5f, [Box]() { if (Box.IsValid()) Box->FadeOut(1.5f, 0.f); });
		Think(TEXT("It still plays."));
		if (Has(TEXT("locked_in")) && !bBusy)
		{
			After(4.6f, [this]()
			{
				AWCCharacter* Pl = Player();
				if (!Pl || bBusy) return;
				PlayAt(TEXT("VO/m_hum"), Pl->GetActorLocation() + FRotator(0.f, Rng.FRandRange(0.f, 360.f), 0.f).Vector() * 650.f, 0.6f, 1.f, 2600.f);
				Tension = FMath::Min(1.f, Tension + 0.2f);
			});
		}
		return true;
	}
	if (Id == TEXT("use:fusebox"))'''),
])

# ================================================================= the HUD
edit(R + "WCGame.h", [
    ('''enum class EWCScreen : uint8 { None, Main, Pause, Settings, Controls };''', '''enum class EWCScreen : uint8 { None, Main, Pause, Settings, Controls, Inventory };'''),
    ('''	void DrawCredits(AWCDirector* D);''', '''	void DrawCredits(AWCDirector* D);

	// inventory
	struct FInvItem { FName Id; FString Name; FString Desc; };
	void DrawInventory(AWCDirector* D);
	void DrawNotePage(const class AWCNote* N, const TCHAR* Footer);
	void OpenInventory(AWCDirector* D);
	void CloseInventory(AWCDirector* D);
	void BuildInventory(AWCDirector* D, TArray<FInvItem>& Out) const;
	void ShowInvItem(AWCDirector* D, FName Id);
	void InvUse(AWCDirector* D, FName Id);
	bool InvCanDrop(AWCDirector* D, FName Id, FString& Why) const;
	void InvDrop(AWCDirector* D, FName Id);
	void InvSay(const FString& Line) { InvMsg = Line; InvMsgUntil = RealNow + 3.5; }
	int32 InvSel = 0, InvAct = 0, InvTab = 0, InvPaper = 0;
	bool bInvInspect = false;
	float InvYaw = 0.f, InvPitch = 0.f, InvZoom = 1.f, InvMX = 0.f, InvMY = 0.f;
	double InvLast = 0.0, InvMsgUntil = 0.0, InvTouchedAt = -10.0;
	FName InvShown;
	FString InvMsg;
	TWeakObjectPtr<class AWCInteractable> InvFocus;
	TWeakObjectPtr<class AWCNote> InvNote;
	FString InvTestDir;
	int32 InvTestStage = 0;
	double InvTestAt = 0.0;'''),
])
edit(R + "WCGame.cpp", [
    ('''#include "UnrealClient.h"''', '''#include "UnrealClient.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "Materials/MaterialInterface.h"'''),
    ('''		MenuTestAt = FPlatformTime::Seconds() + 9.0;
	}''', '''		MenuTestAt = FPlatformTime::Seconds() + 9.0;
	}
	if (FParse::Value(FCommandLine::Get(), TEXT("WCInvTest="), InvTestDir))
	{
		InvTestDir = FPaths::ConvertRelativePathToFull(InvTestDir);
		IFileManager::Get().MakeDirectory(*InvTestDir, true);
	}'''),
    ('''	if (D->Mode == EWCMode::Playing && bEsc)
	{
		if (D->ActiveNote.IsValid()) D->CloseNote();''', '''	const bool bInvKey = PC->WasInputKeyJustPressed(EKeys::Tab) || PC->WasInputKeyJustPressed(EKeys::I) || PC->WasInputKeyJustPressed(EKeys::Gamepad_Special_Left);
	if (D->Mode == EWCMode::Playing && bInvKey)
	{
		AWCCharacter* Pl = D->Player();
		if (Screen == EWCScreen::Inventory) CloseInventory(D);
		else if (Screen == EWCScreen::None && !D->ActiveNote.IsValid() && D->Fade < 0.5f && !D->bBusy && !D->IsDriving() && Pl && !Pl->IsDown() && !Pl->IsInputLocked()) OpenInventory(D);
	}
	if (D->Mode != EWCMode::Playing && Screen == EWCScreen::Inventory) CloseInventory(D);
	if (D->Mode == EWCMode::Playing && bEsc && Screen == EWCScreen::Inventory)
	{
		if (InvNote.IsValid()) InvNote = nullptr;
		else if (bInvInspect) bInvInspect = false;
		else CloseInventory(D);
	}
	else if (D->Mode == EWCMode::Playing && bEsc)
	{
		if (D->ActiveNote.IsValid()) D->CloseNote();'''),
    ('''	if (Screen != EWCScreen::None) DrawMenu(D);''', '''	if (Screen == EWCScreen::Inventory) DrawInventory(D);
	else if (Screen != EWCScreen::None) DrawMenu(D);
	if (!InvTestDir.IsEmpty() && D->Mode == EWCMode::Playing)
	{
		// -WCInvTest=<dir>: fill the bag, open it, photograph each page, quit
		static const TCHAR* Give[] = { TEXT("key_sitting"), TEXT("key_prayer"), TEXT("key_ell"), TEXT("fuse"), TEXT("shears"), TEXT("keep_ruth"), TEXT("keep_walter"), TEXT("keep_daniel") };
		static const TCHAR* Shots[] = { TEXT("inv_1_list"), TEXT("inv_2_iron_key"), TEXT("inv_3_keyring_inspect"), TEXT("inv_4_shears_inspect"), TEXT("inv_5_tags"), TEXT("inv_6_music_box"), TEXT("inv_7_pistol"), TEXT("inv_8_papers") };
		if (InvTestStage == 0 && D->PlaySeconds > 7.f && Screen == EWCScreen::None)
		{
			for (const TCHAR* G : Give) D->Items.Add(G);
			int32 n = 0;
			for (TActorIterator<AWCNote> It(GetWorld()); It && n < 9; ++It, ++n) D->NotesRead.AddUnique(It->WCId);
			D->bBusy = false;
			OpenInventory(D);
			InvTestStage = 1;
			InvTestAt = RealNow + 2.5;
		}
		else if (InvTestStage >= 1 && InvTestStage <= 8 && RealNow > InvTestAt && Screen == EWCScreen::Inventory)
		{
			FScreenshotRequest::RequestScreenshot(InvTestDir / (FString(Shots[InvTestStage - 1]) + TEXT(".png")), true, false);
			++InvTestStage;
			InvTestAt = RealNow + 2.2;
		}
		else if (InvTestStage >= 2 && InvTestStage <= 8 && RealNow > InvTestAt - 1.7 && Screen == EWCScreen::Inventory)
		{
			// set up the next picture a moment after the last one was taken
			static const int32 SelFor[] = { 0, 0, 4, 5, 7, 10, 8, 1, 0 };
			InvTouchedAt = RealNow;
			InvSel = SelFor[InvTestStage];
			bInvInspect = InvTestStage == 3 || InvTestStage == 4;
			InvTab = InvTestStage == 8 ? 1 : 0;
			InvYaw = InvTestStage == 4 ? 35.f : 0.f;
			InvPitch = InvTestStage == 4 ? 18.f : 0.f;
		}
		else if (InvTestStage == 9 && RealNow > InvTestAt)
		{
			++InvTestStage;
			UKismetSystemLibrary::QuitGame(this, PC, EQuitPreference::Quit, false);
		}
	}'''),
    ('''	const bool bTab = PC && PC->IsInputKeyDown(EKeys::Tab);''', '''	const bool bTab = false;       // Tab opens the inventory now, which shows all of this'''),
    ('''void AWCHUD::DrawNote(AWCDirector* D)
{
	const AWCNote* N = D->ActiveNote.Get();
	const float W = Canvas->SizeX, H = Canvas->SizeY;''', '''void AWCHUD::DrawNote(AWCDirector* D)
{
	DrawNotePage(D->ActiveNote.Get(), TEXT("[E] Put it back"));
}

void AWCHUD::DrawNotePage(const AWCNote* N, const TCHAR* Footer)
{
	if (!N) return;
	const float W = Canvas->SizeX, H = Canvas->SizeY;'''),
    ('''	Text(TEXT("[E] Put it back"), W * 0.5f, Y + PH + Px(18.f), Px(21.f), Dim, 1);''', '''	Text(Footer, W * 0.5f, Y + PH + Px(18.f), Px(21.f), Dim, 1);'''),
    ('''			{ TEXT("Objective and items"), TEXT("Hold Tab") }, { TEXT("Pause"), TEXT("Esc") } };''',
     '''			{ TEXT("Inventory and objective"), TEXT("Tab or I") }, { TEXT("Pause"), TEXT("Esc") } };'''),
])

s = io.open(R + "WCGame.cpp", encoding="utf-8").read()
if "AWCHUD::DrawInventory" not in s:
    s = s.rstrip() + r'''

// ---------------------------------------------------------------------------------------------- inventory
namespace
{
	struct FItemInfo { const TCHAR* Id; const TCHAR* Name; const TCHAR* Desc; const TCHAR* Mesh; };
	const FItemInfo GItemInfo[] = {
		{ TEXT("flashlight"), TEXT("Flashlight"), TEXT("County issue, three cells. It goes dim when she is close, and out when she is closer."), TEXT("/Game/WC/Props/SM_HandFlashlight.SM_HandFlashlight") },
		{ TEXT("pistol"), TEXT("Service pistol"), TEXT("Eight to the magazine. It does not hurt her. She cannot stand the noise and the flash: three or four shots and she goes, for a while."), TEXT("/Game/WC/Props/SM_HandPistol.SM_HandPistol") },
		{ TEXT("radio"), TEXT("Radio"), TEXT("Clear as a bell in the car. Inside this house it gives nothing but static."), TEXT("") },
		{ TEXT("key_sitting"), TEXT("Small brass key"), TEXT("From the kitchen drawer that was shut a minute before. Worn smooth. Her sitting room is the only door downstairs that is locked."), TEXT("/Game/WC/Props/SM_Item_Key.SM_Item_Key") },
		{ TEXT("key_prayer"), TEXT("Iron key on a ribbon"), TEXT("Heavy and old, on a faded red ribbon. For the locked room upstairs, the one she prayed in."), TEXT("/Game/WC/Props/SM_Item_KeyIron.SM_Item_KeyIron") },
		{ TEXT("key_desk"), TEXT("Small desk key"), TEXT("It was inside a hollow book. Walter's desk, in the den."), TEXT("/Game/WC/Props/SM_Item_Key.SM_Item_Key") },
		{ TEXT("key_ell"), TEXT("Walter's keys"), TEXT("Three on a ring, from his desk. The door across the upstairs hall, and the rooms behind it."), TEXT("/Game/WC/Props/SM_Item_Keyring.SM_Item_Keyring") },
		{ TEXT("key_attic"), TEXT("Attic key"), TEXT("It was in Daniel's room, kept where a boy keeps things. The attic door."), TEXT("/Game/WC/Props/SM_Item_Key.SM_Item_Key") },
		{ TEXT("key_cellar"), TEXT("Padlock key"), TEXT("From the bottom of Daniel's footlocker. The padlock on the cellar door."), TEXT("/Game/WC/Props/SM_Item_KeyIron.SM_Item_KeyIron") },
		{ TEXT("fuse"), TEXT("Spare fuse"), TEXT("A screw-in plug fuse, the old kind. The fuse box is in the pantry."), TEXT("/Game/WC/Props/SM_Item_Fuse.SM_Item_Fuse") },
		{ TEXT("shears"), TEXT("Sewing shears"), TEXT("Heavy tailor's shears, still sharp. Her hands could not close on them any more. Mine can."), TEXT("/Game/WC/Props/SM_Item_Shears.SM_Item_Shears") },
		{ TEXT("keep_ruth"), TEXT("Ruth's music box"), TEXT("Her name is scratched into the bottom in a child's capitals. It still plays."), TEXT("") },
		{ TEXT("keep_walter"), TEXT("Walter's wedding ring"), TEXT("Worn thin. It was lying with her knots."), TEXT("/Game/WC/Props/SM_Item_Ring.SM_Item_Ring") },
		{ TEXT("keep_daniel"), TEXT("Daniel's dog tags"), TEXT("HARROW, DANIEL. He went, and in March of 1969 a telegram came instead of him."), TEXT("/Game/WC/Props/SM_Item_Tags.SM_Item_Tags") },
	};
	const FItemInfo* FindItemInfo(FName Id)
	{
		for (const FItemInfo& I : GItemInfo) if (Id == I.Id) return &I;
		return nullptr;
	}
}

void AWCHUD::BuildInventory(AWCDirector* D, TArray<FInvItem>& Out) const
{
	auto Add = [&Out](FName Id)
	{
		const FItemInfo* I = FindItemInfo(Id);
		FInvItem It; It.Id = Id; It.Name = I ? I->Name : ItemName(Id); It.Desc = I ? I->Desc : TEXT("");
		Out.Add(It);
	};
	Add(TEXT("flashlight")); Add(TEXT("pistol")); Add(TEXT("radio"));
	for (const FName& It : D->Items) if (!It.ToString().StartsWith(TEXT("ammo"))) Add(It);
}

void AWCHUD::OpenInventory(AWCDirector* D)
{
	AWCCharacter* P = D->Player();
	InvFocus = P ? P->GetFocus() : nullptr;
	Open(EWCScreen::Inventory);
	SetPaused(true);
	InvAct = 0; InvTab = 0; bInvInspect = false; InvNote = nullptr;
	InvYaw = 0.f; InvPitch = 0.f; InvZoom = 1.f; InvShown = NAME_None; InvMsgUntil = 0.0; InvLast = RealNow; InvTouchedAt = -10.0;
	D->Play2D(TEXT("paper"), 0.4f);
}

void AWCHUD::CloseInventory(AWCDirector* D)
{
	if (AWCCharacter* P = D->Player()) P->HideInspect();
	InvShown = NAME_None; InvNote = nullptr; bInvInspect = false;
	Open(EWCScreen::None);
	SetPaused(false);
}

void AWCHUD::ShowInvItem(AWCDirector* D, FName Id)
{
	AWCCharacter* P = D->Player();
	if (!P) return;
	InvShown = Id;
	InvYaw = 0.f; InvPitch = 0.f; InvZoom = 1.f;
	UStaticMesh* Mesh = nullptr;
	TArray<UMaterialInterface*> Mats;
	FVector Part = FVector::OneVector;
	const FItemInfo* I = FindItemInfo(Id);
	if (I && I->Mesh[0]) Mesh = LoadObject<UStaticMesh>(nullptr, I->Mesh, nullptr, LOAD_NoWarn | LOAD_Quiet);
	if (!Mesh)
	{
		// the thing itself, as it lay in the house
		for (TActorIterator<AWCPickup> It(GetWorld()); It; ++It)
		{
			if (It->ItemId != Id || !It->Mesh || !It->Mesh->GetStaticMesh()) continue;
			Mesh = It->Mesh->GetStaticMesh();
			Part = It->Mesh->GetRelativeScale3D();
			for (int32 m = 0; m < It->Mesh->GetNumMaterials(); ++m) Mats.Add(It->Mesh->GetMaterial(m));
			break;
		}
	}
	P->ShowInspect(Mesh, Mats, Part);
}

bool AWCHUD::InvCanDrop(AWCDirector* D, FName Id, FString& Why) const
{
	if (Id == TEXT("flashlight") || Id == TEXT("pistol") || Id == TEXT("radio")) { Why = TEXT("Not in this house."); return false; }
	const FString S = Id.ToString();
	if (S.StartsWith(TEXT("key_")))
	{
		bool bAnyDoor = false;
		for (TActorIterator<AWCDoor> It(GetWorld()); It; ++It)
		{
			if (It->KeyId != Id) continue;
			bAnyDoor = true;
			if (It->bLocked) { Why = TEXT("I still need this."); return false; }
		}
		if (!bAnyDoor && !(Id == TEXT("key_desk") && D->Has(TEXT("desk_open")))) { Why = TEXT("I still need this."); return false; }
		return true;                       // every lock it fits is open
	}
	Why = TEXT("I still need this.");
	return false;
}

void AWCHUD::InvDrop(AWCDirector* D, FName Id)
{
	FString Why;
	if (!InvCanDrop(D, Id, Why)) { InvSay(Why); return; }
	D->Items.Remove(Id);
	AWCCharacter* P = D->Player();
	for (TActorIterator<AWCPickup> It(GetWorld()); It && P; ++It)
	{
		if (It->ItemId != Id) continue;
		// set it down on the floor in front of him, where it can be picked up again
		const FVector From = P->GetActorLocation() + FRotator(0.f, P->GetControlRotation().Yaw, 0.f).Vector() * 62.f;
		FHitResult Hit;
		FCollisionQueryParams Q(SCENE_QUERY_STAT(WCDrop), false, P);
		Q.AddIgnoredActor(*It);
		const bool bFloor = GetWorld()->LineTraceSingleByChannel(Hit, From + FVector(0, 0, 30), From - FVector(0, 0, 220), ECC_Visibility, Q);
		It->SetActorLocation((bFloor ? Hit.ImpactPoint : From - FVector(0, 0, 88)) + FVector(0, 0, 1.f));
		It->SetActorHiddenInGame(false);
		It->SetActorEnableCollision(true);
		break;
	}
	InvShown = NAME_None;
	InvSay(TEXT("Left it here."));
	D->Play2D(TEXT("pickup"), 0.5f, EWCSnd::SFX, 0.8f);
}

void AWCHUD::InvUse(AWCDirector* D, FName Id)
{
	AWCCharacter* P = D->Player();
	if (!P) return;
	AWCInteractable* F = InvFocus.Get();
	if (F && !F->CanInteract()) F = nullptr;
	auto OnWhatHeFaces = [this, D, P]() { CloseInventory(D); P->DoInteract(); };
	const FString S = Id.ToString();
	if (Id == TEXT("flashlight")) { CloseInventory(D); P->SetFlashlight(!P->IsFlashlightOn()); return; }
	if (Id == TEXT("pistol")) { InvSay(TEXT("Hold the right mouse button to raise it. Left fires. R reloads.")); return; }
	if (Id == TEXT("radio")) { CloseInventory(D); D->Event(TEXT("invuse:radio")); return; }
	if (S.StartsWith(TEXT("key_")))
	{
		AWCDoor* Door = Cast<AWCDoor>(F);
		if (Door && Door->KeyId == Id) { OnWhatHeFaces(); return; }
		if (Id == TEXT("key_desk") && F && F->WCId == TEXT("desk")) { OnWhatHeFaces(); return; }
		InvSay(Door ? TEXT("It does not fit this lock.") : TEXT("Nothing here it fits. I have to be standing at the lock."));
		return;
	}
	if (Id == TEXT("fuse")) { if (F && F->WCId == TEXT("fusebox")) OnWhatHeFaces(); else InvSay(TEXT("It goes in the fuse box.")); return; }
	if (Id == TEXT("shears")) { if (F && F->WCId.ToString().StartsWith(TEXT("knot"))) OnWhatHeFaces(); else InvSay(TEXT("Nothing here to cut.")); return; }
	if (S.StartsWith(TEXT("keep_")) && F && F->WCId == TEXT("place")) { OnWhatHeFaces(); return; }
	if (Id == TEXT("keep_ruth")) { CloseInventory(D); D->Event(TEXT("invuse:keep_ruth")); return; }
	if (S.StartsWith(TEXT("keep_"))) { InvSay(TEXT("Not here. Where she lies.")); return; }
	InvSay(TEXT("I can't use that here."));
}

void AWCHUD::DrawInventory(AWCDirector* D)
{
	APlayerController* PC = GetOwningPlayerController();
	AWCCharacter* P = D->Player();
	if (!PC || !P) return;
	const float W = Canvas->SizeX, H = Canvas->SizeY;
	const float Dt = (float)FMath::Clamp(RealNow - InvLast, 0.0, 0.1);
	InvLast = RealNow;
	const bool bFresh = RealNow - ScreenOpenedAt < 0.15;

	// a paper being read again covers everything
	if (const AWCNote* Note = InvNote.Get())
	{
		DrawNotePage(Note, TEXT("[E] or [Esc]  Back"));
		if (!bFresh && (PC->WasInputKeyJustPressed(EKeys::E) || PC->WasInputKeyJustPressed(EKeys::Enter) || PC->WasInputKeyJustPressed(EKeys::LeftMouseButton))) { InvNote = nullptr; ScreenOpenedAt = RealNow; }
		return;
	}

	TArray<FInvItem> Items;
	BuildInventory(D, Items);
	InvSel = FMath::Clamp(InvSel, 0, Items.Num() - 1);

	// ---- input
	int32 Move = 0, Side = 0;
	bool bGo = false;
	float MX = 0.f, MY = 0.f;
	const bool bMouse = PC->GetMousePosition(MX, MY);
	const float DX = MX - InvMX, DY = MY - InvMY;
	const bool bMouseMoved = bMouse && (FMath::Abs(DX) > 0.5f || FMath::Abs(DY) > 0.5f);
	InvMX = MX; InvMY = MY;
	const bool bClick = !bFresh && PC->WasInputKeyJustPressed(EKeys::LeftMouseButton);
	const bool bHeld = PC->IsInputKeyDown(EKeys::LeftMouseButton);
	if (!bFresh)
	{
		if (PC->WasInputKeyJustPressed(EKeys::Down) || PC->WasInputKeyJustPressed(EKeys::S) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Down)) Move = 1;
		if (PC->WasInputKeyJustPressed(EKeys::Up) || PC->WasInputKeyJustPressed(EKeys::W) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Up)) Move = -1;
		if (PC->WasInputKeyJustPressed(EKeys::Left) || PC->WasInputKeyJustPressed(EKeys::A) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Left)) Side = -1;
		if (PC->WasInputKeyJustPressed(EKeys::Right) || PC->WasInputKeyJustPressed(EKeys::D) || PC->WasInputKeyJustPressed(EKeys::Gamepad_DPad_Right)) Side = 1;
		bGo = PC->WasInputKeyJustPressed(EKeys::Enter) || PC->WasInputKeyJustPressed(EKeys::SpaceBar) || PC->WasInputKeyJustPressed(EKeys::E) || PC->WasInputKeyJustPressed(EKeys::Gamepad_FaceButton_Bottom);
		if (!bInvInspect)
		{
			if (PC->WasInputKeyJustPressed(EKeys::One)) InvTab = 0;
			if (PC->WasInputKeyJustPressed(EKeys::Two)) InvTab = 1;
		}
	}
	auto Hover = [&](float X0, float Y0, float X1, float Y1) { return bMouse && MX >= X0 && MX <= X1 && MY >= Y0 && MY <= Y1; };

	// ---- the thing itself
	const FName WantShown = InvTab == 0 && Items.IsValidIndex(InvSel) ? Items[InvSel].Id : FName(TEXT("__none"));
	if (WantShown != InvShown) ShowInvItem(D, WantShown);
	if (bInvInspect)
	{
		if (bHeld && !bFresh) { InvYaw -= DX * 0.45f; InvPitch = FMath::Clamp(InvPitch + DY * 0.45f, -85.f, 85.f); InvTouchedAt = RealNow; }
		const float Turn = 110.f * Dt;
		if (PC->IsInputKeyDown(EKeys::A) || PC->IsInputKeyDown(EKeys::Left)) { InvYaw += Turn; InvTouchedAt = RealNow; }
		if (PC->IsInputKeyDown(EKeys::D) || PC->IsInputKeyDown(EKeys::Right)) { InvYaw -= Turn; InvTouchedAt = RealNow; }
		if (PC->IsInputKeyDown(EKeys::W) || PC->IsInputKeyDown(EKeys::Up)) { InvPitch = FMath::Clamp(InvPitch - Turn, -85.f, 85.f); InvTouchedAt = RealNow; }
		if (PC->IsInputKeyDown(EKeys::S) || PC->IsInputKeyDown(EKeys::Down)) { InvPitch = FMath::Clamp(InvPitch + Turn, -85.f, 85.f); InvTouchedAt = RealNow; }
		if (PC->WasInputKeyJustPressed(EKeys::MouseScrollUp) || PC->IsInputKeyDown(EKeys::Q)) InvZoom = FMath::Min(1.5f, InvZoom + (PC->IsInputKeyDown(EKeys::Q) ? Dt : 0.1f));
		if (PC->WasInputKeyJustPressed(EKeys::MouseScrollDown) || PC->IsInputKeyDown(EKeys::Z)) InvZoom = FMath::Max(0.65f, InvZoom - (PC->IsInputKeyDown(EKeys::Z) ? Dt : 0.1f));
	}
	if (RealNow - InvTouchedAt > 2.5) InvYaw += 22.f * Dt;                 // left alone, it turns slowly
	{
		const FQuat Base = P->IsInspectFlat() ? FQuat(FRotator(68.f, 0.f, 0.f)) : FQuat(FRotator(8.f, 180.f, 0.f));
		const FQuat Q = FQuat(FRotator(InvPitch, 0.f, 0.f)) * FQuat(FRotator(0.f, InvYaw, 0.f)) * Base;
		static float ZoomShown = 1.f;
		ZoomShown = FMath::FInterpTo(ZoomShown, InvZoom * (bInvInspect ? 1.3f : 0.92f), Dt, 9.f);
		P->SetInspectView(Q, ZoomShown);
	}

	const FInvItem* Cur = InvTab == 0 && Items.IsValidIndex(InvSel) ? &Items[InvSel] : nullptr;

	// ---- inspecting: just the thing, its name and what he makes of it
	if (bInvInspect && Cur)
	{
		Text(Cur->Name, W * 0.5f, Px(70.f), Px(40.f), Hot, 1, true);
		Wrapped(Cur->Desc, W * 0.24f, H - Px(210.f), W * 0.52f, Px(25.f), Ink, 1);
		Text(TEXT("Drag, or W A S D: turn it      Wheel, or Q / Z: closer, further      Esc: back"), W * 0.5f, H - Px(64.f), Px(19.f), Dim, 1);
		if (!bFresh && (PC->WasInputKeyJustPressed(EKeys::RightMouseButton) || PC->WasInputKeyJustPressed(EKeys::BackSpace))) bInvInspect = false;
		return;
	}

	// ---- frame
	const float Left = Px(70.f);
	Text(TEXT("CARRYING"), Left, Px(58.f), Px(52.f), Ink, 0, true);
	{
		// two pages
		static const TCHAR* Tabs[] = { TEXT("[1]  THINGS"), TEXT("[2]  PAPERS") };
		float X = Left;
		for (int32 t = 0; t < 2; ++t)
		{
			const FString Label = t == 1 ? FString::Printf(TEXT("%s  (%d)"), Tabs[t], D->NotesRead.Num()) : FString(Tabs[t]);
			const float Tw = Measure(Label, Px(21.f)).X;
			const bool bOver = Hover(X - Px(8.f), Px(132.f), X + Tw + Px(8.f), Px(166.f));
			Text(Label, X, Px(136.f), Px(21.f), InvTab == t ? Hot : (bOver ? Ink : Dim));
			if (InvTab == t) Box(X, Px(164.f), Tw, Px(2.f), Hot);
			if (bOver && bClick) { InvTab = t; return; }
			X += Tw + Px(46.f);
		}
	}
	// right-hand side: what he is doing, what he has left in the gun, what he is looking for
	{
		const float RX = W * 0.735f, RW = W * 0.225f;
		float Y = Px(136.f);
		if (!D->Objective.IsEmpty())
		{
			Text(TEXT("OBJECTIVE"), RX, Y, Px(17.f), Dim); Y += Px(26.f);
			Y += Wrapped(D->Objective, RX, Y, RW, Px(24.f), Ink) + Px(26.f);
		}
		Text(TEXT("CARTRIDGES"), RX, Y, Px(17.f), Dim); Y += Px(26.f);
		Text(FString::Printf(TEXT("%d in the pistol, %d spare"), P->Ammo, P->Reserve), RX, Y, Px(24.f), Ink); Y += Px(54.f);
		if (D->NotesRead.Contains(TEXT("note_prayer")) || D->NotesRead.Contains(TEXT("note_cellar")))
		{
			Text(TEXT("WHAT WAS THEIRS"), RX, Y, Px(17.f), Dim); Y += Px(26.f);
			static const TCHAR* Keep[][2] = { { TEXT("keep_ruth"), TEXT("Ruth's music box") }, { TEXT("keep_walter"), TEXT("Walter's ring") }, { TEXT("keep_daniel"), TEXT("Daniel's tags") }, { TEXT("shears"), TEXT("Something to cut with") } };
			for (const auto& K : Keep)
			{
				const bool bHave = D->Items.Contains(K[0]);
				Text(FString::Printf(TEXT("%s  %s"), bHave ? TEXT("[x]") : TEXT("[  ]"), K[1]), RX, Y, Px(22.f), bHave ? Ink : Dim); Y += Px(30.f);
			}
			Y += Px(6.f);
			Wrapped(TEXT("Bring them to where she lies. Cut the three knots."), RX, Y, RW, Px(19.f), Dim);
		}
	}

	if (InvTab == 1)
	{
		// ---- papers he has read
		TArray<const AWCNote*> Notes;
		for (const FName& Id : D->NotesRead) if (const AWCNote* N = Cast<AWCNote>(D->Thing(Id))) Notes.Add(N);
		if (Notes.Num() == 0) { Text(TEXT("Nothing read yet."), Left, Px(200.f), Px(24.f), Dim); }
		InvPaper = FMath::Clamp(InvPaper, 0, FMath::Max(Notes.Num() - 1, 0));
		if (Move != 0 && Notes.Num() > 0) { InvPaper = (InvPaper + Move + Notes.Num()) % Notes.Num(); D->Play2D(TEXT("ui_tick"), 0.35f); }
		const int32 PerCol = 13;
		const float RowH = Px(38.f), ColW = W * 0.31f;
		for (int32 i = 0; i < Notes.Num() && i < PerCol * 2; ++i)
		{
			const float X = Left + (i / PerCol) * ColW, Y = Px(200.f) + (i % PerCol) * RowH;
			FString Title = Notes[i]->Title;
			if (Title.IsEmpty()) Title = Notes[i]->Body.Left(34).Replace(TEXT("\n"), TEXT(" ")) + TEXT("...");
			if (Title.Len() > 40) Title = Title.Left(38) + TEXT("...");
			const bool bOver = Hover(X - Px(14.f), Y - Px(3.f), X + ColW - Px(30.f), Y + RowH - Px(5.f));
			if (bOver && bMouseMoved) InvPaper = i;
			const bool bSel = InvPaper == i;
			if (bSel) Box(X - Px(18.f), Y + Px(5.f), Px(4.f), Px(22.f), Hot);
			Text(Title, X, Y, Px(23.f), bSel ? Hot : Ink);
			if (bOver && bClick) { InvNote = const_cast<AWCNote*>(Notes[i]); ScreenOpenedAt = RealNow; return; }
		}
		if (bGo && Notes.IsValidIndex(InvPaper)) { InvNote = const_cast<AWCNote*>(Notes[InvPaper]); ScreenOpenedAt = RealNow; return; }
		Text(TEXT("W / S: choose      Enter: read it again      1: things      Tab: close"), W * 0.5f, H - Px(64.f), Px(19.f), Dim, 1);
		return;
	}

	// ---- things: the list
	if (Move != 0 && Items.Num() > 0) { InvSel = (InvSel + Move + Items.Num()) % Items.Num(); InvMsgUntil = 0.0; D->Play2D(TEXT("ui_tick"), 0.35f); }
	{
		const float RowH = Px(41.f);
		float Y = Px(200.f);
		for (int32 i = 0; i < Items.Num(); ++i)
		{
			const bool bOver = Hover(Left - Px(22.f), Y - Px(3.f), Left + Px(330.f), Y + RowH - Px(5.f));
			if (bOver && bMouseMoved && InvSel != i) { InvSel = i; InvMsgUntil = 0.0; }
			if (bOver && bClick) InvSel = i;
			const bool bSel = InvSel == i;
			if (bSel) Box(Left - Px(20.f), Y + Px(6.f), Px(4.f), Px(24.f), Hot);
			Text(Items[i].Name, Left, Y, Px(25.f), bSel ? Hot : Ink);
			if (i == 2) { Y += Px(14.f); Box(Left, Y + RowH - Px(8.f), Px(250.f), Px(1.f), FLinearColor(1, 1, 1, 0.12f)); }
			Y += RowH;
		}
	}
	Cur = Items.IsValidIndex(InvSel) ? &Items[InvSel] : nullptr;
	if (!Cur) return;

	// ---- name, what he makes of it, and what can be done with it
	Text(Cur->Name, W * 0.5f, H * 0.655f, Px(36.f), Hot, 1, true);
	Wrapped(Cur->Desc, W * 0.29f, H * 0.655f + Px(56.f), W * 0.42f, Px(22.f), Ink, 1);
	if (RealNow < InvMsgUntil) Text(InvMsg, W * 0.5f, H - Px(176.f), Px(23.f), Hot, 1);

	FString Why;
	const bool bCanDrop = InvCanDrop(D, Cur->Id, Why);
	static const TCHAR* Acts[] = { TEXT("USE"), TEXT("INSPECT"), TEXT("DROP") };
	if (Side != 0) { InvAct = (InvAct + Side + 3) % 3; D->Play2D(TEXT("ui_tick"), 0.35f); }
	const float BW = Px(190.f), BH = Px(48.f), Gap = Px(22.f);
	const float BX0 = W * 0.5f - (BW * 3 + Gap * 2) * 0.5f, BY = H - Px(134.f);
	int32 Do = -1;
	for (int32 a = 0; a < 3; ++a)
	{
		const float X = BX0 + a * (BW + Gap);
		const bool bOver = Hover(X, BY, X + BW, BY + BH);
		if (bOver && bMouseMoved) InvAct = a;
		const bool bSel = InvAct == a;
		const bool bOff = a == 2 && !bCanDrop;
		Box(X, BY, BW, BH, FLinearColor(1, 1, 1, bSel ? 0.10f : 0.04f));
		Box(X, BY + BH - Px(2.f), BW, Px(2.f), bSel ? Hot : FLinearColor(1, 1, 1, 0.16f));
		Text(Acts[a], X + BW * 0.5f, BY + Px(11.f), Px(24.f), bOff ? FLinearColor(Dim.R, Dim.G, Dim.B, 0.45f) : (bSel ? Hot : Ink), 1);
		if (bOver && bClick) Do = a;
	}
	if (bGo) Do = InvAct;
	Text(TEXT("W / S: choose      A / D: what to do      Enter: do it      2: papers      Tab: close"), W * 0.5f, H - Px(64.f), Px(19.f), Dim, 1);

	if (Do == 0) InvUse(D, Cur->Id);
	else if (Do == 1) { if (InvShown == Cur->Id && P->IsInspectFlat() || true) { bInvInspect = true; InvTouchedAt = RealNow - 1.0; ScreenOpenedAt = RealNow; } }
	else if (Do == 2) InvDrop(D, Cur->Id);
}
'''
    io.open(R + "WCGame.cpp", "w", encoding="utf-8", newline="\n").write(s)
print("ok")
