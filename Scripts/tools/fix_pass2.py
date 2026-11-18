import io
R = "C:/GameDev/Unreal/WellnessCheck/"


def sub(f, old, new, count=1):
    s = io.open(R + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(R + f, "w", encoding="utf-8", newline="\n").write(s)


C = "Source/WellnessCheck/"
# her mesh faces -Y in mesh space (same as Blender): turn it to the actor's +X
sub(C + "WCEntity.cpp", "Body->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));", "Body->SetRelativeRotation(FRotator(0.f, 90.f, 0.f));")
# view models: Blender -X (muzzle / lens) arrives as +X
sub(C + "WCCharacter.cpp", "	Gun->SetRelativeRotation(FRotator(0.f, 180.f, 0.f));", "	Gun->SetRelativeRotation(FRotator(0.f, 0.f, 0.f));")
sub(C + "WCCharacter.cpp", "	FlashHand->SetRelativeRotation(FRotator(0.f, 180.f, 0.f));", "	FlashHand->SetRelativeRotation(FRotator(0.f, 0.f, 0.f));")
sub(C + "WCCharacter.cpp", "	Flash->SetRelativeLocation(FVector(26.f, -19.f, -17.f));", "	Flash->SetRelativeLocation(FVector(50.f, -23.f, -22.f));")
sub(C + "WCCharacter.cpp", "	Gun->SetRelativeLocation(FVector(-14.f, 0.f, 0.f));", "	Gun->SetRelativeLocation(FVector(4.f, 0.f, 0.f));")
sub(C + "WCCharacter.cpp", "	const FVector Low(26.f, 20.f, -46.f), High(44.f, 13.f, -15.5f);", "	const FVector Low(40.f, 24.f, -60.f), High(52.f, 15.f, -19.f);")
# a wider, softer beam and a breath of fill so the dark is readable, not blind
sub(C + "WCCharacter.cpp", "	Flash->SetInnerConeAngle(8.f);\n	Flash->SetOuterConeAngle(27.f);", "	Flash->SetInnerConeAngle(10.f);\n	Flash->SetOuterConeAngle(31.f);")
sub(C + "WCCharacter.cpp", "	Spill->SetIntensity(FlashLumens * 0.05f * Level);", "	Spill->SetIntensity(FlashLumens * 0.11f * Level);")
sub(C + "WCCharacter.cpp", '''	Dust = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Dust"));''', '''	Fill = CreateDefaultSubobject<UPointLightComponent>(TEXT("Fill"));
	Fill->SetupAttachment(Cam);
	Fill->SetIntensityUnits(ELightUnits::Lumens);
	Fill->SetIntensity(2.2f);
	Fill->SetAttenuationRadius(520.f);
	Fill->SetLightColor(FLinearColor(0.55f, 0.66f, 1.f));
	Fill->SetCastShadows(false);
	Fill->SetVolumetricScatteringIntensity(0.f);
	Fill->bUseInverseSquaredFalloff = true;

	Dust = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Dust"));''')
sub(C + "WCCharacter.h", '''	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> Muzzle;''', '''	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> Muzzle;
	UPROPERTY(VisibleAnywhere, Category = "WC") TObjectPtr<UPointLightComponent> Fill;''')
# level
L = "Scripts/level/"
sub(L + "build_house.py", '    h.set_editor_property("eye_ref", V(e[0], -e[1], e[2]))', '    h.set_editor_property("eye_ref", V(-e[0], e[1], e[2]))')
sub(L + "build_house.py", "b = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(1400, 556, CZ), R(-90))", "b = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(1400, 556, CZ), R(0))")
sub(L + "build_house.py", '("sitting", 880, -240, 92, -40)', '("sitting", 1000, -400, 92, -20)')
sub(L + "build_house.py", '("bath", 880, -260, UZ + 92, -45)', '("bath", 1350, -250, UZ + 92, -140)')
sub(L + "decay.py", 'WALL_POOL = ["mold_01", "mold_02", "mold_03", "water_01", "water_01", "filth_01", "filth_02", "filth_03", "rust_01", "crack_01", "mold_03", "water_02"]',
    'WALL_POOL = ["mold_01", "mold_02", "mold_03", "water_01", "water_01", "filth_01", "filth_02", "filth_03", "rust_01", "crack_01", "mold_03", "mold_01"]')
sub(L + "import_more.py", '"water": (0.6, 0.5, 0.36)', '"water": (0.34, 0.27, 0.19)')
print("ok")
