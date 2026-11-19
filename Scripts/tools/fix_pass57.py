"""Inventory polish after its first photographs:
 - the held-up thing and its black backdrop sit much closer to the eye (15 cm, near clip pulled in while the bag is open),
   so nothing in the room can poke through in front of them;
 - each thing shows its broad side (the pistol and radio were seen end-on);
 - the flashlight, pistol and radio get proper models of their own instead of the first-person hand meshes."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCCharacter.h", [
    ('''	bool IsInspectFlat() const;''', '''	bool IsInspectFlat() const;
	/** How the thing is turned so its broad side faces him. */
	FQuat InspectBase() const;'''),
])
edit(R + "WCCharacter.cpp", [
    ('''	InspectBack->SetHiddenInGame(false);
	GunPivot->SetHiddenInGame(true, true);
	FlashHand->SetHiddenInGame(true, true);''', '''	// everything is held small and very close, so the room cannot come between the eye and the black card
	InspectBack->SetRelativeLocation(FVector(33.f * InspectK, 0.f, 0.f));
	InspectBack->SetRelativeScale3D(FVector(0.004f, 6.f * InspectK, 6.f * InspectK));
	InspectKey->SetRelativeLocation(FVector(3.f, -15.f, 13.f) * InspectK);
	InspectFill->SetRelativeLocation(FVector(6.f, 17.f, -9.f) * InspectK);
	InspectKey->SetAttenuationRadius(90.f * InspectK);
	InspectFill->SetAttenuationRadius(90.f * InspectK);
	if (GEngine) GEngine->Exec(GetWorld(), TEXT("r.SetNearClipPlane 2"));
	InspectBack->SetHiddenInGame(false);
	GunPivot->SetHiddenInGame(true, true);
	FlashHand->SetHiddenInGame(true, true);
	Dust->SetHiddenInGame(true);'''),
    ('''	InspectKey->SetIntensity(InMesh ? 150.f : 0.f);
	InspectFill->SetIntensity(InMesh ? 45.f : 0.f);
}''', '''	InspectKey->SetIntensity(InMesh ? 150.f * InspectK * InspectK : 0.f);
	InspectFill->SetIntensity(InMesh ? 45.f * InspectK * InspectK : 0.f);
}

FQuat AWCCharacter::InspectBase() const
{
	const UStaticMesh* M = InspectMesh->GetStaticMesh();
	if (!M) return FQuat::Identity;
	const FVector E = M->GetBounds().BoxExtent * InspectPart;
	const float Big = E.GetMax();
	if (E.Z <= E.X && E.Z <= E.Y && E.Z < 0.45f * Big) return FQuat(FRotator(68.f, 0.f, 0.f));        // lies flat: tip its top toward him
	if (E.Y <= E.X && E.Y <= E.Z && E.Y < 0.45f * Big) return FQuat(FRotator(0.f, -90.f, 0.f));       // thin from side to side: show the side
	if (E.X < 0.45f * Big) return FQuat::Identity;
	return FQuat(FRotator(8.f, 180.f, 0.f));
}'''),
    ('''	const FVector Scale = InspectPart * (6.2f * Zoom / Radius);
	InspectMesh->SetRelativeScale3D(Scale);
	InspectMesh->SetRelativeRotation(Rot);
	InspectMesh->SetRelativeLocation(FVector(21.f, 0.f, 1.4f) - Rot.RotateVector(B.Origin * Scale));''',
     '''	const FVector Scale = InspectPart * (6.2f * InspectK * Zoom / Radius);
	InspectMesh->SetRelativeScale3D(Scale);
	InspectMesh->SetRelativeRotation(Rot);
	InspectMesh->SetRelativeLocation(FVector(21.f, 0.f, 1.4f) * InspectK - Rot.RotateVector(B.Origin * Scale));'''),
    ('''	GunPivot->SetHiddenInGame(false, true);
	FlashHand->SetHiddenInGame(false, true);
}''', '''	GunPivot->SetHiddenInGame(false, true);
	FlashHand->SetHiddenInGame(false, true);
	Dust->SetHiddenInGame(false);
	if (GEngine) GEngine->Exec(GetWorld(), TEXT("r.SetNearClipPlane 10"));
}'''),
    ('''// ---------------------------------------------------------------------------------------------- inventory: the thing held up''',
     '''// ---------------------------------------------------------------------------------------------- inventory: the thing held up
static const float InspectK = 0.45f;'''),
    ('''#include "Engine/StaticMesh.h"''', '''#include "Engine/StaticMesh.h"
#include "Engine/Engine.h"'''),
])
edit(R + "WCGame.cpp", [
    ('''		const FQuat Base = P->IsInspectFlat() ? FQuat(FRotator(68.f, 0.f, 0.f)) : FQuat(FRotator(8.f, 180.f, 0.f));''', '''		const FQuat Base = P->InspectBase();'''),
    ('''TEXT("/Game/WC/Props/SM_HandFlashlight.SM_HandFlashlight") },''', '''TEXT("/Game/HorrorHouseKit/Meshes/Lights_Ambience/SM_Flashlight_Off.SM_Flashlight_Off") },'''),
    ('''TEXT("/Game/WC/Props/SM_HandPistol.SM_HandPistol") },''', '''TEXT("/Game/WC/Props/SM_Item_Pistol.SM_Item_Pistol") },'''),
    ('''TEXT("Clear as a bell in the car. Inside this house it gives nothing but static."), TEXT("") },''', '''TEXT("Clear as a bell in the car. Inside this house it gives nothing but static."), TEXT("/Game/WC/Props/SM_Item_Radio.SM_Item_Radio") },'''),
])
print("ok")
