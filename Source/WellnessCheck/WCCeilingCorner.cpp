#include "WCDirector.h"
#include "WCCharacter.h"
#include "WCEntity.h"
#include "WCWorld.h"
#include "Animation/AnimSequence.h"
#include "Components/PointLightComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"

bool AWCDirector::IsCrawlingThroughRearBath() const
{
    return CornerEdith && bCornerMoving && CornerEdith->Body->IsPlaying();
}

bool AWCDirector::CornerEyeInView() const
{
    const APlayerController* PC = Cast<APlayerController>(Player()->GetController());
    if (!PC || !CornerEdith) return false;
    const FVector Eye = CornerEdith->EyeLocation();
    FVector2D Pixel;
    int32 W, H;
    PC->GetViewportSize(W,H);
    return PC->ProjectWorldLocationToScreen(Eye,Pixel) && Pixel.X > W*.04 && Pixel.X < W*.96 &&
        Pixel.Y > H*.03 && Pixel.Y < H*.97 && PlayerSees(Eye,.65f,1550.f);
}

namespace
{
    const FName CeilingCornerDone(TEXT("rear_bath_ceiling_seen"));
    const FString CeilingBootStep(TEXT("ceiling_boot_step"));
}

void AWCDirector::PrepareCeilingCorner()
{
    if (CornerEdith || Has(CeilingCornerDone) || Has(TEXT("dawn")) || !Has(TEXT("inside")) || !Her()) return;
    if (!CornerWing.IsValid()) CornerWing = Door(TEXT("up_ell"));
    if (!CornerBath.IsValid()) CornerBath = Door(TEXT("up_bath2"));
    const AWCDoor* Wing = CornerWing.Get();
    const AWCDoor* Bath = CornerBath.Get();
    if (!Wing || Wing->bLocked || !HasItem(Wing->KeyId) || !Bath) return;

    static const FName ClipName(TEXT("CeilingCorner"));
    UAnimSequence* Clip = LoadObject<UAnimSequence>(nullptr,TEXT("/Game/WC/Her/A_Her_CeilingCorner.A_Her_CeilingCorner"));
    if (!ensure(Clip)) return;
    // The hinge is 56.5 cm from the doorway centre. All four contact tracks are
    // baked in doorway space, including their travel onto the bathroom ceiling.
    const FVector Origin = Bath->GetActorLocation() + FVector(56.5,0,0);
    const FTransform Pose(FRotator::ZeroRotator,Origin);
    CornerEdith = GetWorld()->SpawnActorDeferred<AWCEntity>(AWCEntity::StaticClass(),Pose,this,nullptr,
        ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
    if (!CornerEdith) return;
    CornerEdith->Anims.Add(ClipName,Clip);
    CornerEdith->Body->SetSkeletalMeshAsset(Her()->Body->GetSkeletalMeshAsset());
    for (int32 I=0; I<Her()->Body->GetNumMaterials(); ++I)
        CornerEdith->Body->SetMaterial(I,Her()->Body->GetMaterial(I));
    CornerEdith->EyeRadius = Her()->EyeRadius;
    CornerEdith->EyeRef = Her()->EyeRef;
    CornerEdith->HeadBone = Her()->HeadBone;
    UGameplayStatics::FinishSpawningActor(CornerEdith,Pose);
    const float Yaw = 90.f - CornerEdith->Body->GetRelativeRotation().Yaw;
    CornerEdith->Appear(Origin,Yaw,ClipName,false,0.f);
    CornerEdith->SetMood(TEXT("watch"));
    CornerEdith->SetFarGlow(0.f);
    CornerEdith->Body->SetLightingChannels(true,true,true);
    CornerEdith->EyeGlint->SetLightingChannels(false,false,true);
    CornerEdith->EyeGlint->SetRelativeLocation(FVector(98,-38,4));
    CornerEdith->EyeGlint->SetLightColor(EdithMoonlight());
    CornerEdith->EyeGlint->SetAttenuationRadius(300.f);
    CornerEdith->EyeGlint->SetSpecularScale(.40f);
    CornerEdith->SetGlow(550.f);
    UMaterialInterface* Blue = LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/WC/Materials/M_HallEyeGlint.M_HallEyeGlint"));
    // Widen across the iris only; swelling its depth would bury the black pupil.
    CornerEdith->Iris->SetRelativeScale3D(CornerEdith->Iris->GetRelativeScale3D()*FVector(1.,1.20,1.20));
    CornerEdith->Pupil->SetRelativeLocation(FVector(1.024*CornerEdith->EyeRadius,0,0));
    if (UMaterialInstanceDynamic* Iris = CornerEdith->Iris->CreateDynamicMaterialInstance(0,Blue))
        Iris->SetScalarParameterValue(TEXT("Glow"),7.f);
    CornerWitness = 0.f;
    NextCornerFootfall = 0;
    Snd(CeilingBootStep);
    bCornerMoving = false;
    UE_LOG(LogTemp,Display,TEXT("WCCORNER24 perched before the door swings"));
}

void AWCDirector::TickCeilingCorner(float Dt)
{
    if (Has(CeilingCornerDone) || Has(TEXT("dawn")))
    {
        if (CornerEdith) CornerEdith->Destroy();
        CornerEdith = nullptr;
        bCornerMoving = false;
        return;
    }
    AWCCharacter* P = Player();
    if (!P) return;
    const FVector Eye = P->EyeLocation();
    const bool AtRearHall = Eye.X > 1490. && FMath::Abs(Eye.Y) < 195. && Eye.Z > 404. && Eye.Z < 625.;
    // An older checkpoint may already have the wing unlocked.
    if (!CornerEdith && AtRearHall) PrepareCeilingCorner();
    if (!CornerEdith) return;

    const AWCDoor* Wing = CornerWing.Get();
    const AWCDoor* Bath = CornerBath.Get();
    const bool InRearWing = AtRearHall && Wing && Bath && Eye.X > Wing->GetActorLocation().X &&
        Eye.X < Bath->GetActorLocation().X + 257.;
    const bool Interrupted = bBusy || bEventBusy || StalkState != 0 || P->IsDown() || P->IsInputLocked() ||
        ActiveNote.IsValid() || (Her() && Her()->IsShown());
    if (bCornerMoving)
    {
        // Right/left foot plants in clip_corner's 30 fps bake, including the last landing inside.
        static constexpr int32 PlantFrames[] = {19,25,32,38,46,52,59,65,73,79,86,92,100,106};
        const int32 Frame = FMath::FloorToInt(CornerEdith->Body->GetPosition()*30.f + .001f);
        const int32 FirstDue = NextCornerFootfall;
        while (NextCornerFootfall < UE_ARRAY_COUNT(PlantFrames) && PlantFrames[NextCornerFootfall] <= Frame)
            ++NextCornerFootfall;
        if (NextCornerFootfall > FirstDue)
        {
            // After a hitch, sound the latest contact at its current foot position.
            const bool Right = (NextCornerFootfall % 2) == 1;
            const FVector Foot = CornerEdith->BoneWorld(Right ? TEXT("RightFoot") : TEXT("LeftFoot"));
            const float IntoBath = FMath::SmoothStep(0.f,150.f,float(Foot.Y - CornerEdith->GetActorLocation().Y));
            const float Gain = (Right ? 2.05f : 1.78f) * FMath::Lerp(1.f,.68f,IntoBath);
            PlayAt(CeilingBootStep,Foot,Gain,Rng.FRandRange(.98f,1.02f));
        }
        if (CornerEdith->Body->IsPlaying()) return;
        // A player who sprints right up to the opening must not see her pop out of existence.
        for (const FName Bone : {FName(TEXT("Head")),FName(TEXT("Hips")),FName(TEXT("LeftFoot")),FName(TEXT("RightFoot"))})
            if (PlayerSees(CornerEdith->BoneWorld(Bone),.50f,1550.f)) return;
        RememberAtCheckpoint(CeilingCornerDone);
        UE_LOG(LogTemp,Display,TEXT("WCCORNER24 clear of the doorway"));
    }
    else if (!Interrupted && InRearWing && Bath && Bath->IsSwungClear())
    {
        const bool Seen = CornerEyeInView();
        constexpr float WitnessSeconds = 1.35f;
        CornerWitness = Seen ? FMath::Min(CornerWitness + Dt,WitnessSeconds) : 0.f;
        const double Distance = FVector::Dist(Eye,CornerEdith->EyeLocation());
        if (Seen && Distance <= 1000. && CornerWitness >= WitnessSeconds)
        {
            bCornerMoving = true;
            CornerEdith->Body->SetPlayRate(.96f);
            UE_LOG(LogTemp,Display,TEXT("WCCORNER24 witnessed retreat range=%.0f eye=%s"),Distance,*CornerEdith->EyeLocation().ToCompactString());
        }
        return;
    }
    else
    {
        CornerWitness = 0.f;
        return;
    }
    CornerEdith->Destroy();
    CornerEdith = nullptr;
    bCornerMoving = false;
}
