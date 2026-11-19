# Pass 128: at the shed bench the game offered "Look" (the bench's description) and never "Take" for the VHS tape lying
# on it, because the description's box is in front of the tape (found by the yard check: WCAUTO WHY pick_tape1: in the
# way = Look_shed_bench).  Without the tape the front door never opens.  Two fixes: the bench's description covers only
# the far half of the bench (looks.py), and, for every such place in the house, a description never stands in front of
# something that can be taken or used: the eye looks on through it.
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

edit(r"C:\GameDev\Unreal\WellnessCheck\Source\WellnessCheck\WCCharacter.cpp", [
    ("""			AWCInteractable* T = Cast<AWCInteractable>(Hit.GetActor());
			if (T && T->CanInteract() && FVector::Dist2D(Hit.ImpactPoint, GetActorLocation()) <= InteractReach) Focus = T;
""",
     """			AWCInteractable* T = Cast<AWCInteractable>(Hit.GetActor());
			if (T && T->CanInteract() && FVector::Dist2D(Hit.ImpactPoint, GetActorLocation()) <= InteractReach) Focus = T;
			// a description never stands in front of something he can take or use: look on through it
			AWCInteractable* Through = T;
			for (int32 k = 0; k < 3 && Through && Through->IsA<AWCLook>(); ++k)
			{
				P.AddIgnoredActor(Through);
				FHitResult H2;
				if (!GetWorld()->LineTraceSingleByChannel(H2, Start, End, ECC_Visibility, P)) break;
				Through = Cast<AWCInteractable>(H2.GetActor());
				if (Through && !Through->IsA<AWCLook>() && Through->CanInteract() && FVector::Dist2D(H2.ImpactPoint, GetActorLocation()) <= InteractReach) { Focus = Through; break; }
			}
"""),
])
print("pass 128 applied")
