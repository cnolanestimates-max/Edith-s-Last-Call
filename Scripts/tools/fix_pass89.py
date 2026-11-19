"""Pass 89 (Cheyenne 06:08 UTC): "you can pick up items from damn near across the room, that needs to change".
He has to be right up to a thing to use it: within about a metre on the floor plan (it was 2.3 m along the line of sight).
The test bot walks up to things to match."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Source/WellnessCheck/WCCharacter.h", [
    ('float InteractRange = 230.f;', '''float InteractRange = 190.f;        // along the line of sight: long enough to reach the floor at his feet
	/** ... but the thing itself has to be this close to him on the floor plan (arm's length). */
	UPROPERTY(EditAnywhere, Category = "WC") float InteractReach = 105.f;'''),
])
edit(R + "Source/WellnessCheck/WCCharacter.cpp", [
    ('''AWCInteractable* T = Cast<AWCInteractable>(Hit.GetActor());
			if (T && T->CanInteract()) Focus = T;''', '''AWCInteractable* T = Cast<AWCInteractable>(Hit.GetActor());
			if (T && T->CanInteract() && FVector::Dist2D(Hit.ImpactPoint, GetActorLocation()) <= InteractReach) Focus = T;'''),
])
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''const float D2 = FVector::Dist2D(Loc, Goal);
		if (bToUse && FVector::Dist(P->EyeLocation(), Goal) < P->InteractRange - 45.f)
		{''', '''const float D2 = FVector::Dist2D(Loc, Goal);
		// near enough to use = within arm's length of the thing's box on the floor plan (the player's own rule)
		float BoxGap = 1e6f;
		if (bToUse)
		{
			FVector BO, BE; T->GetActorBounds(true, BO, BE);
			BoxGap = FVector2D(FMath::Max(FMath::Abs(Loc.X - BO.X) - BE.X, 0.f), FMath::Max(FMath::Abs(Loc.Y - BO.Y) - BE.Y, 0.f)).Size();
		}
		if (bToUse && BoxGap < P->InteractReach - 30.f && FVector::Dist(P->EyeLocation(), Goal) < P->InteractRange + 60.f)
		{'''),
])
print("pass 89 applied")
