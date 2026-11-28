#include "WCDirector.h"
#include "WCWorld.h"
#include "WCCharacter.h"
#include "Components/PointLightComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Engine/StaticMesh.h"

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

void SetBathChain(AWCInteractable& Dresser, bool bReleased, bool bDrained)
{
    static const FName Paths[] = { TEXT("TrappedChain"), TEXT("ReleasedChain"), TEXT("DrainedChain") };
    const FVector Catch = Dresser.GetActorLocation() + FVector(-13, -9, -6);
    const FVector Trapped[] = {{1046,-516,404}, {1061,-506,413}, {1073,-488,421},
        {1090,-482,418}, {1105,-487,414}, Catch};
    const FVector Released[] = {{1046,-516,404}, {1061,-506,413}, {1073,-488,421},
        {1086,-484,418}, {1095,-486,411}, {1099,-489,399}, {1099,-490,388}};
    const FVector Drained[] = {{1046,-516,374}, {1055,-510,378}, {1066,-500,402}, {1073,-488,421},
        {1086,-484,418}, {1094,-486,412}};
    const TConstArrayView<FVector> ChainPositions[] = { Trapped, Released, Drained };
    const int32 VisiblePath = bDrained ? 2 : bReleased ? 1 : 0;
    for (int32 State = 0; State < UE_ARRAY_COUNT(Paths); ++State)
    {
        UInstancedStaticMeshComponent* Links = FindObjectFast<UInstancedStaticMeshComponent>(&Dresser, Paths[State]);
        if (!Links)
        {
            Links = NewObject<UInstancedStaticMeshComponent>(&Dresser, Paths[State]);
            Links->SetupAttachment(Dresser.Root);
            Links->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));
            Links->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WC/Materials/MI_Brass.MI_Brass")));
            Links->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            Links->SetCastShadow(false);
            Links->RegisterComponent();
            TArray<FTransform> Segments;
            const auto AddLinks = [&](TConstArrayView<FVector> Points)
            {
                constexpr float Spacing = 2.8f;
                float Distance = .5f;
                int32 Link = 0;
                for (int32 Span = 1; Span < Points.Num(); ++Span)
                {
                    const FVector Axis = Points[Span] - Points[Span - 1];
                    const float Length = Axis.Size();
                    const FVector Along = Axis.GetSafeNormal();
                    const FVector Across = FVector::CrossProduct(Along, FVector::UpVector).GetSafeNormal();
                    for (; Distance <= Length; Distance += Spacing, ++Link)
                    {
                        const FVector Center = Points[Span-1] + Along * Distance;
                        const FVector AcrossLink = Link % 2 ? FVector::CrossProduct(Across,Along) : Across;
                        FVector Previous = Center + Along * 1.9;
                        for (int32 Side = 1; Side <= 8; ++Side)
                        {
                            const float Angle = Side * UE_TWO_PI / 8;
                            const FVector End = Center + Along * (1.9f * FMath::Cos(Angle)) + AcrossLink * (.86f * FMath::Sin(Angle));
                            const FVector Delta = End - Previous;
                            Segments.Emplace(FRotationMatrix::MakeFromZ(Delta).Rotator(), (Previous + End) * .5,
                                FVector(.0042f,.0042f,(Delta.Size() + .24f) / 100.f));
                            Previous = End;
                        }
                    }
                    Distance -= Length;
                }
            };
            AddLinks(ChainPositions[State]);
            Links->AddInstances(Segments, false, true, false);
        }
        Links->SetVisibility(State == VisiblePath);
    }
}
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
    const bool ChainFree = Has(TEXT("bath_chain_released")) || Has(TEXT("bath_drained"));
    if (AWCInteractable* A = Thing(TEXT("bath_dresser")))
    {
        SetBathChain(*A, ChainFree, Has(TEXT("bath_drained")));
        A->Prompt = ChainFree ? TEXT("Inspect the bath dresser") :
            HasItem(TEXT("screwdriver")) ? TEXT("Pry open the jammed drawer") : TEXT("Inspect the jammed drawer");
    }
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
        if (Has(TEXT("bath_drained"))) { Feedback(TEXT("The wet chain hangs free beside the bath.")); return true; }
        if (!Has(TEXT("bath_chain_released")))
        {
            if (!HasItem(TEXT("screwdriver")))
            {
                Feedback(TEXT("The chain is pinched in the drawer. A flat-head screwdriver could pry it open."));
                if (Has(TEXT("peek_done"))) SetObjective(TEXT("Find the screwdriver on the desk in Edith's room"));
                return true;
            }
            Set(TEXT("bath_chain_released"));
            if (const AWCInteractable* Dresser = Thing(TEXT("bath_dresser")))
            {
                PlayAt(TEXT("shelf_scrape"), Dresser->GetActorLocation(), .48f);
                PlayAt(TEXT("switch_click"), Dresser->GetActorLocation(), .42f, .74f);
            }
            SetObjective(TEXT("Pull the plug in the upstairs bath"));
            ApplyWorldState();
            Checkpoint(TEXT("bath_chain"));
        }
        Feedback(TEXT("The chain is free. There is a brass tag just below the surface."));
        return true;
    }
    if (Id == TEXT("look:look_upbath_tub"))
    {
        if (Has(TEXT("bath_drained"))) { Feedback(TEXT("Only the ring of black sediment remains.")); return true; }
        if (!Has(TEXT("bath_chain_released")))
        {
            Feedback(TEXT("The brass chain runs from the plug into the jammed drawer. Its handle won't budge."));
            if (Has(TEXT("peek_done"))) SetObjective(TEXT("Free the plug chain at the front bathroom dresser"));
            return true;
        }
        Set(TEXT("bath_drained"));
        if (AWCInteractable* Dresser = Thing(TEXT("bath_dresser"))) SetBathChain(*Dresser, true, true);
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
        SetObjective(TEXT("Play Recording II on the living-room television")); Checkpoint(TEXT("recording_II")); return true;
    }
    if (Id == TEXT("closed:note_deskkey") && !Has(TEXT("book_done")))
    {
        SetObjective(TEXT("Pull the settlers' book from the living-room shelf beside the stairs")); return true;
    }
    return false;
}

void AWCDirector::SetPostFuseObjective()
{
    if (!Has(TEXT("book_done")))
        SetObjective(TEXT("Find the settlers' book on the living-room shelf beside the stairs"));
    else if (!Has(TEXT("desk_open")))
        SetObjective(TEXT("Use the book's small key on Walter's desk in the downstairs den"));
    else if (!HasItem(TEXT("key_ell")) && !Has(TEXT("walter_keys_taken")))
        SetObjective(TEXT("Take Walter's keys from his desk in the downstairs den"));
    else if (const AWCDoor* RearHall = Door(TEXT("up_ell")); RearHall && RearHall->bLocked)
        SetObjective(TEXT("Unlock the rear upstairs hall. Check the aide's room for her videotape."));
    else if (Has(TEXT("attic_done")))
        SetCellarRouteObjective();
    else
        SetObjective(TEXT("Search the house for Edith Harrow"));
}

void AWCDirector::RestoreHarrowHints()
{
    if (Objective == TEXT("Find what the key opens")) SetObjective(TEXT("Unlock the downstairs sitting room opposite the kitchen"));
    else if (Objective == TEXT("Find what the iron key opens")) SetObjective(TEXT("Unlock the upstairs prayer room"));
    else if (Objective == TEXT("Find what Walter's keys open")) SetObjective(TEXT("Unlock the rear upstairs hall. Check the aide's room for her videotape."));
    else if (!Has(TEXT("bath_drained")) && !Has(TEXT("bath_chain_released")) &&
        (Objective == TEXT("Something slid open upstairs") || Objective.Contains(TEXT("open dresser drawer")) ||
        Objective.Contains(TEXT("Pull the plug"))))
        SetObjective(TEXT("Free the plug chain at the front upstairs bathroom dresser"));
    else if (Has(TEXT("peek_done")) && !Has(TEXT("sitting_open")) && !HasItem(TEXT("key_sitting")) &&
        (Objective == TEXT("Answer the phone in the kitchen") || Objective == TEXT("Check the back hall downstairs")))
        SetObjective(Has(TEXT("bath_drained")) ? TEXT("Take the brass key from the upstairs bath") :
            Has(TEXT("bath_chain_released")) ? TEXT("Pull the plug in the upstairs bath") :
            TEXT("Check the dresser in the front upstairs bathroom"));
    else if (Objective == TEXT("Find what the long key opens")) SetObjective(TEXT("Take the long key to the attic door upstairs"));
    else if ((LastCheckpoint == TEXT("hand") && Has(TEXT("underbed_done")) && !HasItem(TEXT("keep_ruth"))) ||
        (LastCheckpoint == TEXT("attic_done") && Objective == TEXT("Unlock the cellar")))
        SetCellarRouteObjective();
    else if (Has(TEXT("fuse_done")) && Objective == TEXT("Search the house for Edith Harrow") &&
        (LastCheckpoint == TEXT("fuse_done") || !Has(TEXT("book_done"))))
        SetPostFuseObjective();
}
