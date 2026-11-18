"""Gun arm: the model's barrel runs along +Y, not +X (it was pointing off to the right); darker sleeve.  Look test aims exactly."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(R + "WCCharacter.cpp", [
    ('''	Gun->SetRelativeRotation(FRotator(2.5f, -7.5f, -4.f));''', '''	Gun->SetRelativeRotation(FRotator(0.f, -96.f, 0.f));      // the model's barrel is its +Y; turned to point ahead and a touch inward'''),
])
edit(R + "WCWorld.cpp", [
    ('''		D->Event(FName(*FString::Printf(TEXT("watcher:%s"), *WCId.ToString())));''', '''if (!bScripted) D->Event(FName(*FString::Printf(TEXT("watcher:%s"), *WCId.ToString())));'''),
])
edit(R + "WCAuto.cpp", [
    ('''		if (AActor* T = AutoTarget(this, S.Arg)) AimAt(P, T->GetActorLocation() + FVector(0, 0, 60), Dt);''', '''if (AActor* T = AutoTarget(this, S.Arg)) AimAt(P, T->GetActorLocation() + FVector(0, 0, S.F < -0.5f ? 0.f : 60.f), Dt);'''),
    ('''AutoSteps.Add({ A_Look, TEXT("W_hall_stair"), 0.f });''', '''AutoSteps.Add({ A_Her, TEXT("Idle"), 3000.f }); AutoSteps.Add({ A_Look, TEXT("W_hall_stair"), -1.f });'''),
    ('''AutoSteps.Add({ A_Look, TEXT("W_kitchen_fridge"), 0.f });''', '''AutoSteps.Add({ A_Look, TEXT("W_kitchen_fridge"), -1.f });'''),
    ('''AutoSteps.Add({ A_Look, TEXT("W_fireplace"), 0.f });''', '''AutoSteps.Add({ A_Look, TEXT("W_fireplace"), -1.f });'''),
    ('''AutoSteps.Add({ A_Look, TEXT("W_hair_sitting"), 0.f });''', '''AutoSteps.Add({ A_Look, TEXT("W_hair_sitting"), -1.f });'''),
    ('''AutoSteps.Add({ A_Look, TEXT("W_hair_backhall"), 0.f });''', '''AutoSteps.Add({ A_Look, TEXT("W_hair_backhall"), -1.f });'''),
    ('''AutoSteps.Add({ A_Look, TEXT("SettlersBook"), 0.f }); Wait(0.3f); Shot(TEXT("book_before"));
			AutoSteps.Add({ A_Use, TEXT("book_settlers"), 0.f }); Wait(0.75f); Shot(TEXT("book_eye")); Wait(2.6f); Shot(TEXT("book_after"));''',
     '''AutoSteps.Add({ A_Look, TEXT("SettlersBook"), -1.f }); Wait(0.3f); Shot(TEXT("book_before"));
			AutoSteps.Add({ A_Use, TEXT("book_settlers"), 0.f }); Wait(0.7f); Shot(TEXT("book_eye")); Wait(0.5f); Shot(TEXT("book_eye2")); Wait(2.4f); Shot(TEXT("book_after"));'''),
])
edit(L + "import_more.py", [
    ('''        eal.save_loaded_asset(mi, False)
        sm.set_material(0, mi)''', '''if short.startswith("Hand"):
            # the deputy's sleeve and glove: the generated texture is too orange under a flashlight
            mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(0.50, 0.46, 0.44, 1))
        eal.save_loaded_asset(mi, False)
        sm.set_material(0, mi)'''),
])
print("ok")
