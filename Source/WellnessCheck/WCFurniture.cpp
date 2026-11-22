#include "WCDirector.h"
#include "WCWorld.h"
#include "WCCharacter.h"
#include "Components/PointLightComponent.h"

namespace
{
struct FFixture
{
    FName Id, Flag;
    FVector Travel;
    float Swing, Duration;
};

// Travel is in the furniture's own axes. Only the moving piece has this transform.
const FFixture Fixtures[] = {
    { TEXT("fridge_door"), TEXT("fridge_open"), FVector::ZeroVector, 100.f, .83f },
    { TEXT("sitting_drawer"), TEXT("writing_open"), FVector(33,0,0), 0.f, .65f },
    { TEXT("daniel_drawer"), TEXT("daniel_drawer_open"), FVector(33,0,0), 0.f, .65f },
    { TEXT("walter_drawer"), TEXT("desk_open"), FVector(34,0,0), 0.f, .78f },
    { TEXT("piano_drawer"), TEXT("piano_repaired"), FVector(33,0,0), 0.f, .92f },
    { TEXT("bath_water"), TEXT("bath_drained"), FVector(0,0,-31), 0.f, 2.8f }
};
}

void AWCDirector::UpdateFurniture(float Dt, bool bSnap)
{
    bool bChanged = false;
    for (const FFixture& Def : Fixtures)
    {
        FMovingProp* Moving = Furniture.Find(Def.Id);
        if (!Moving)
        {
            AWCInteractable* Actor = Thing(Def.Id);
            if (!Actor) continue;
            Moving = &Furniture.Add(Def.Id);
            Moving->Actor = Actor;
            Moving->Closed = Actor->GetActorTransform();
        }
        AWCInteractable* Piece = Moving->Actor.Get();
        if (!Piece) continue;
        const float Target = Has(Def.Flag) ? 1.f : 0.f;
        if (!bSnap && Moving->Alpha == Target) continue;
        Moving->Alpha = bSnap ? Target : FMath::FInterpConstantTo(Moving->Alpha, Target, Dt, 1.f / Def.Duration);
        const float U = FMath::SmoothStep(0.f,1.f,Moving->Alpha);
        const FTransform& Home = Moving->Closed;
        Piece->SetActorLocationAndRotation(Home.TransformPosition(Def.Travel * U),
            Home.GetRotation() * FQuat(FVector::UpVector, FMath::DegreesToRadians(Def.Swing * U)));
        if (Def.Id == TEXT("fridge_door") && (U > 0.f || FridgeBulb.IsValid()))
        {
            if (!FridgeBulb.IsValid())
            {
                auto* Bulb = NewObject<UPointLightComponent>(this);
                Bulb->RegisterComponent(); Bulb->SetWorldLocation(Home.TransformPosition(FVector(-36,-73,119)));
                Bulb->SetIntensityUnits(ELightUnits::Lumens); Bulb->SetLightColor(FLinearColor(1.f,.76f,.47f));
                Bulb->SetAttenuationRadius(155.f); Bulb->SetSourceRadius(3.f); Bulb->SetCastShadows(true);
                FridgeBulb=Bulb;
            }
            FridgeBulb->SetIntensity(65.f * U);
            FridgeBulb->SetVisibility(U > .01f);
        }
        if (Def.Id == TEXT("bath_water"))
        {
            Piece->SetActorScale3D(FVector(1.f-.29f*U,1.f-.37f*U,1.f));
            Piece->SetActorHiddenInGame(Moving->Alpha == 1.f);
        }
        bChanged |= Moving->Alpha == Target;
    }
    if (bChanged) RefreshFurnitureLoot();
}

void AWCDirector::RefreshFurnitureLoot()
{
    auto Open = [this](FName Id) { const FMovingProp* P = Furniture.Find(Id); return P && P->Alpha == 1.f; };
    auto Visible = [this](FName Id, bool Show)
    {
        if (AWCInteractable* A = Thing(Id)) { A->SetActorHiddenInGame(!Show); A->SetActorEnableCollision(Show); }
    };
    const bool Repaired = Has(TEXT("piano_repaired"));
    Visible(TEXT("ivory_fitted"), Repaired);
    Visible(TEXT("note_tape_receipt"), Has(TEXT("daniel_drawer_open")) && Open(TEXT("daniel_drawer")));
    Visible(TEXT("note_fridge"), Has(TEXT("fridge_open")) && Open(TEXT("fridge_door")));
    Visible(TEXT("pick_ivory"), Has(TEXT("writing_open")) && Open(TEXT("sitting_drawer")) && !HasItem(TEXT("piano_ivory")) && !Repaired);
    Visible(TEXT("pick_key_prayer"), Open(TEXT("piano_drawer")) && !HasItem(TEXT("key_prayer")) && !Has(TEXT("prayer_key_taken")));
    Visible(TEXT("pick_key_ell"), Open(TEXT("walter_drawer")) && !HasItem(TEXT("key_ell")) && !Has(TEXT("walter_keys_taken")));
    Visible(TEXT("pick_key_sitting"), Open(TEXT("bath_water")) && !HasItem(TEXT("key_sitting")) && !Has(TEXT("sitting_open")));
    const bool BathOpen = Has(TEXT("peek_done")) || Has(TEXT("phone_done"));
    const bool ChainFree = Has(TEXT("bath_chain_released")) || Has(TEXT("phone_done"));
    Visible(TEXT("bath_dresser"), BathOpen);
    if (AWCInteractable* A = Thing(TEXT("bath_dresser"))) A->Prompt = ChainFree ? TEXT("Inspect the bath dresser") : TEXT("Free the trapped chain");
    if (AWCInteractable* A = Thing(TEXT("fridge_door"))) A->Prompt = Has(TEXT("fridge_open")) ? TEXT("Close the refrigerator") : TEXT("Open the refrigerator");
    if (AWCInteractable* A = Thing(TEXT("sitting_drawer"))) A->Prompt = Has(TEXT("writing_open")) ? TEXT("Close the writing-desk drawer") : TEXT("Open the writing-desk drawer");
    if (AWCInteractable* A = Thing(TEXT("daniel_drawer"))) A->Prompt = Has(TEXT("daniel_drawer_open")) ? TEXT("Close Daniel's desk drawer") : TEXT("Open Daniel's desk drawer");
    if (AWCInteractable* A = Thing(TEXT("look_piano"))) A->Prompt = HasItem(TEXT("piano_ivory")) ? TEXT("Replace the missing ivory key") : TEXT("Inspect the piano keyboard");
    if (AWCInteractable* A = Thing(TEXT("look_upbath_tub")))
        A->Prompt = Has(TEXT("bath_drained")) ? TEXT("Inspect the empty bath") :
            (ChainFree ? TEXT("Pull the bath plug") : TEXT("Inspect the bath plug"));
}

bool AWCDirector::FurnitureEvent(FName Id)
{
    auto Toggle = [this](FName Flag, FName Prop, const TCHAR* Sound)
    {
        if (Has(Flag)) Flags.Remove(Flag); else Set(Flag);
        if (AWCInteractable* A = Thing(Prop)) PlayAt(Sound,A->GetActorLocation()+FVector(0,0,20),.48f,1.f,1100.f);
        RefreshFurnitureLoot();
    };
    if (Id == TEXT("use:fridge_door")) { Toggle(TEXT("fridge_open"),TEXT("fridge_door"),TEXT("creak")); return true; }
    if (Id == TEXT("use:sitting_drawer")) { Toggle(TEXT("writing_open"),TEXT("sitting_drawer"),TEXT("shelf_scrape")); return true; }
    if (Id == TEXT("use:daniel_drawer"))
    {
        Toggle(TEXT("daniel_drawer_open"),TEXT("daniel_drawer"),TEXT("shelf_scrape"));
        if (Has(TEXT("daniel_drawer_open"))) Feedback(TEXT("There is a folded slip at the back of the drawer."));
        return true;
    }
    if (Id == TEXT("use:walter_drawer"))
    {
        if (!Has(TEXT("desk_open"))) Event(TEXT("use:desk"));
        else Feedback(TEXT("Walter's key ring belonged to the rear upstairs hall."));
        return true;
    }
    if (Id == TEXT("use:bath_dresser"))
    {
        if (Has(TEXT("bath_drained"))) { Feedback(TEXT("The last links of the wet chain lie across the drawer.")); return true; }
        if (!Has(TEXT("bath_chain_released")) && !Has(TEXT("phone_done")))
        {
            Set(TEXT("bath_chain_released"));
            if (const AWCInteractable* Dresser = Thing(TEXT("bath_dresser")))
                PlayAt(TEXT("shelf_scrape"), Dresser->GetActorLocation(), .48f);
            SetObjective(TEXT("Pull the plug in the black bathwater"));
            ApplyWorldState();
            Checkpoint(TEXT("bath_chain"));
        }
        Feedback(TEXT("The chain is free. There is a brass tag just below the surface."));
        return true;
    }
    if (Id == TEXT("look:look_upbath_tub"))
    {
        if (Has(TEXT("bath_drained"))) { Feedback(TEXT("Only the ring of black sediment remains.")); return true; }
        if (!Has(TEXT("bath_chain_released")) && !Has(TEXT("phone_done")))
        {
            Feedback(TEXT("The chain is caught in the dresser beside the bath."));
            if (Has(TEXT("peek_done"))) SetObjective(TEXT("Free the plug chain at the front bathroom dresser"));
            return true;
        }
        Set(TEXT("bath_drained"));
        if (const AWCInteractable* Water = Thing(TEXT("bath_water"))) PlayAt(TEXT("bath_drain"),Water->GetActorLocation(),.74f);
        SetObjective(TEXT("Take the brass key from the bottom of the bath")); Checkpoint(TEXT("bath_drained"));
        return true;
    }
    if (Id == TEXT("take:piano_ivory"))
    {
        SetObjective(TEXT("Fit the loose ivory into the living-room piano")); RefreshFurnitureLoot(); Checkpoint(TEXT("loose_ivory")); return true;
    }
    if (Id == TEXT("look:look_piano") || Id == TEXT("use:piano_drawer"))
    {
        if (Has(TEXT("piano_repaired"))) { Feedback(TEXT("The replaced key is still warm.")); return true; }
        if (!HasItem(TEXT("piano_ivory")))
        {
            Feedback(TEXT("One ivory key is missing. The lesson card on the nearby chair is in Ruth's handwriting."));
            return true;
        }
        Items.Remove(TEXT("piano_ivory")); Set(TEXT("piano_repaired"));
        Feedback(TEXT("The ivory seats with a click. The drawer slides out beneath the keyboard."));
        RefreshFurnitureLoot();
        if (const AWCInteractable* Drawer = Thing(TEXT("piano_drawer"))) PlayAt(TEXT("piano_answer"),Drawer->GetActorLocation(),.82f);
        SetObjective(TEXT("Take the iron door key from the piano drawer")); Checkpoint(TEXT("piano_open"));
        return true;
    }
    if (Id == TEXT("take:key_prayer")) Set(TEXT("prayer_key_taken"));
    if (Id == TEXT("take:key_ell")) Set(TEXT("walter_keys_taken"));
    if (Id == TEXT("take:tape2"))
    {
        SetObjective(TEXT("Play recording II on the living-room television")); Checkpoint(TEXT("recording_II")); return true;
    }
    if (Id == TEXT("closed:note_deskkey") && !Has(TEXT("book_done")))
    {
        SetObjective(TEXT("Pull the settlers' book from the living-room shelf beside the stairs")); return true;
    }
    return false;
}

void AWCDirector::RestoreHarrowHints()
{
    if (Objective == TEXT("Find what the key opens")) SetObjective(TEXT("Unlock the downstairs sitting room opposite the kitchen"));
    else if (Objective == TEXT("Find what the iron key opens")) SetObjective(TEXT("Unlock the upstairs prayer room"));
    else if (Objective == TEXT("Find what Walter's keys open")) SetObjective(TEXT("Unlock the rear upstairs hall. Check the aide's room for her videotape."));
    else if (Objective == TEXT("Something slid open upstairs")) SetObjective(TEXT("Search the dresser in the front upstairs bathroom"));
    else if (Has(TEXT("peek_done")) && !Has(TEXT("sitting_open")) && !HasItem(TEXT("key_sitting")) &&
        (Objective == TEXT("Answer the phone in the kitchen") || Objective == TEXT("Check the back hall downstairs")))
        SetObjective(Has(TEXT("bath_drained")) ? TEXT("Take the brass key from the upstairs bath") :
            Has(TEXT("bath_chain_released")) || Has(TEXT("phone_done")) ? TEXT("Pull the plug in the upstairs bath") :
            TEXT("Check the dresser in the front upstairs bathroom"));
    else if (Objective == TEXT("Find what the long key opens")) SetObjective(TEXT("Take the long key to the attic door upstairs"));
}
