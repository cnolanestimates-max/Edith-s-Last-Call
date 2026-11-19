"""Cheyenne 04:10 UTC:
 - the demon is not Edith's outline and is not solid: it is black smoke in the shape of a tall man, flowing and
   undulating (a new actor, AWCSmokeMan: a few dozen soft-edged spheres in one drifting material).  Used for the thing on
   the road, the Company in the house, and the figure in the third memory;
 - the thin black pole with a little base that sat on screen through the drive was part of the generated car body (its
   aerial).  The body is hidden while he is inside it; the windscreen pillars are drawn as part of the cabin instead;
 - the phonograph's timings shrink in fast test runs, and test runs photograph her in the doorway by themselves."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
P = "C:/GameDev/Unreal/WellnessCheck/"
R = P + "Source/WellnessCheck/"

# ================================================================= the smoke man
edit(R + "WCWorld.h", [
    ('''class UBoxComponent;''', '''class UBoxComponent;
class UInstancedStaticMeshComponent;'''),
])
s = io.open(R + "WCWorld.h", encoding="utf-8").read()
if "AWCSmokeMan" not in s:
    s = s.rstrip() + '''

/** The Company: black smoke in the shape of a tall man. It has no face and nothing about it is solid. */
UCLASS()
class WELLNESSCHECK_API AWCSmokeMan : public AActor
{
	GENERATED_BODY()
public:
	AWCSmokeMan();
	/** Height in cm. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WC") float Tall = 300.f;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WC") TObjectPtr<UInstancedStaticMeshComponent> Smoke;
	/** Fill an instanced-mesh component with the figure (it faces the component's +X). */
	static void Build(UInstancedStaticMeshComponent* C, float Height, int32 Seed);
protected:
	virtual void BeginPlay() override;
};
'''
    io.open(R + "WCWorld.h", "w", encoding="utf-8", newline="\n").write(s)

s = io.open(R + "WCWorld.cpp", encoding="utf-8").read()
if "AWCSmokeMan::Build" not in s:
    s = s.rstrip() + r'''

// ================================================================================================ the Company, as smoke
AWCSmokeMan::AWCSmokeMan()
{
	PrimaryActorTick.bCanEverTick = false;
	Smoke = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Smoke"));
	RootComponent = Smoke;
	Smoke->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Smoke->SetCastShadow(false);
	Smoke->bAffectDynamicIndirectLighting = false;
	Smoke->bAffectDistanceFieldLighting = false;
}

void AWCSmokeMan::BeginPlay()
{
	Super::BeginPlay();
	Build(Smoke, Tall, GetTypeHash(GetName()));
}

void AWCSmokeMan::Build(UInstancedStaticMeshComponent* C, float Height, int32 Seed)
{
	if (!C) return;
	UStaticMesh* Sphere = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	UMaterialInterface* Mat = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Smoke.M_Smoke"));
	if (!Sphere) return;
	C->SetStaticMesh(Sphere);
	if (Mat) C->SetMaterial(0, Mat);
	C->ClearInstances();
	const float K = Height / 300.f;
	FRandomStream Rs(Seed);
	// (centre x forward, y left, z up; size across, deep, high), all in cm for a 3 m figure
	auto Blob = [C, K](float X, float Y, float Z, float W, float D, float H)
	{
		C->AddInstance(FTransform(FRotator::ZeroRotator, FVector(X, Y, Z) * K, FVector(D, W, H) * K / 100.f));
	};
	// a long head with nothing on it, a thick neck, shoulders far too wide, a narrow waist
	Blob(4, 0, 274, 30, 32, 50);
	Blob(2, 0, 246, 22, 22, 26);
	Blob(0, 0, 216, 104, 40, 50);
	Blob(0, 0, 184, 78, 38, 54);
	Blob(-2, 0, 150, 58, 34, 52);
	Blob(-2, 0, 118, 54, 34, 44);
	for (int32 Side = -1; Side <= 1; Side += 2)
	{
		// arms that hang past the knee and end in nothing
		Blob(0, Side * 56.f, 196, 22, 22, 66);
		Blob(4, Side * 62.f, 142, 18, 18, 72);
		Blob(8, Side * 65.f, 92, 15, 15, 56);
		Blob(10, Side * 66.f, 58, 11, 12, 34);
		// legs that thin out and never reach the floor
		Blob(-2, Side * 17.f, 84, 26, 26, 62);
		Blob(-4, Side * 16.f, 44, 20, 22, 54);
		Blob(-8, Side * 14.f, 14, 13, 18, 34);
	}
	// what drifts off it: behind, above the shoulders, round the feet
	for (int32 i = 0; i < 22; ++i)
	{
		const float Z = Rs.FRandRange(6.f, 286.f);
		const float Wide = Z > 170.f && Z < 240.f ? 62.f : 36.f;
		const float S = Rs.FRandRange(14.f, 34.f);
		Blob(Rs.FRandRange(-34.f, -6.f), Rs.FRandRange(-Wide, Wide), Z, S, S * Rs.FRandRange(0.9f, 1.6f), S * Rs.FRandRange(1.1f, 2.2f));
	}
	for (int32 i = 0; i < 8; ++i)
	{
		const float S = Rs.FRandRange(16.f, 30.f);
		Blob(Rs.FRandRange(-30.f, 16.f), Rs.FRandRange(-34.f, 34.f), Rs.FRandRange(0.f, 26.f), S * 1.4f, S * 1.4f, S * 0.8f);
	}
}
'''
    io.open(R + "WCWorld.cpp", "w", encoding="utf-8", newline="\n").write(s)

edit(R + "WCWorld.cpp", [
    ('''		// the thing she asked in: her own outline, drawn longer and thinner, with no light on it at all
		USkeletalMesh* SK = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/WC/Her/SK_Her.SK_Her"));
		UAnimSequence* Pose = LoadObject<UAnimSequence>(nullptr, TEXT("/Game/WC/Her/A_Her_Tall.A_Her_Tall"));
		UMaterialInterface* Void = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Void.M_Void"));
		if (SK)
		{
			USkeletalMeshComponent* C = NewObject<USkeletalMeshComponent>(this);
			C->SetupAttachment(Turn);
			C->SetSkeletalMeshAsset(SK);
			C->SetRelativeRotation(FRotator(0.f, -90.f, 0.f));
			C->SetRelativeScale3D(FVector(0.74f, 0.74f, 1.2f * (Radius / 5.2f)));
			C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			C->SetCastShadow(false);
			for (int32 i = 0; i < C->GetNumMaterials(); ++i) if (Void) C->SetMaterial(i, Void);
			C->SetAnimationMode(EAnimationMode::AnimationSingleNode);
			C->RegisterComponent();
			if (Pose) { C->PlayAnimation(Pose, true); C->SetPlayRate(0.25f); }
		}''', '''		// the thing she asked in: not her outline, and not solid.  Black smoke standing like a man.
		UInstancedStaticMeshComponent* C = NewObject<UInstancedStaticMeshComponent>(this);
		C->SetupAttachment(Turn);
		C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		C->SetCastShadow(false);
		C->RegisterComponent();
		AWCSmokeMan::Build(C, 300.f * (Radius / 5.2f), GetTypeHash(WCId));'''),
    ('''#include "Components/BoxComponent.h"''', '''#include "Components/BoxComponent.h"
#include "Components/InstancedStaticMeshComponent.h"'''),
])

# ================================================================= the car body is hidden while he is in it
edit(R + "WCHouse.cpp", [
    ('''	ShowTagged(TEXT("CabinOnly"), true);          // the inside of the car exists only while he is in it''',
     '''	ShowTagged(TEXT("CabinOnly"), true);          // the inside of the car exists only while he is in it
	if (Car.IsValid()) Car->SetActorHiddenInGame(true);      // and the outside does not (its aerial stood in the windscreen like a black pole)'''),
    ('''	Set(TEXT("arrived"));
	ShowTagged(TEXT("CabinOnly"), false);''', '''	Set(TEXT("arrived"));
	ShowTagged(TEXT("CabinOnly"), false);
	if (Car.IsValid()) Car->SetActorHiddenInGame(false);'''),
])
# ================================================================= phonograph: test-run timings and its own photograph
edit(R + "WCEvents.cpp", [
    ('''	const double In = Clock - RecordAt;
	auto Go = [this](int32 Phase)''', '''	const double In = (Clock - RecordAt) / FMath::Max(TestPace, 0.2f);          // waits shrink in fast test runs
	auto Go = [this](int32 Phase)'''),
    ('''				H->FacePlayer(true);
				H->SetGlow(1.4f);
			}
			Go(8);''', '''				H->FacePlayer(true);
				H->SetGlow(1.4f);
			}
			if (bAuto && !AutoShotDir.IsEmpty())
			{
				// test runs: turn to the door and photograph her
				if (AController* Ct = P->GetController()) Ct->SetControlRotation((Pos(TEXT("Her_RecordDoor")) + FVector(0, 0, 170) - P->EyeLocation()).Rotation());
				const FString File = AutoShotDir / TEXT("S11_record_doorway.png");
				After(0.25f, [File]() { FScreenshotRequest::RequestScreenshot(File, false, false); });
			}
			Go(8);'''),
    ('''		if ((RecordSeenAt > 0.0 && Clock - RecordSeenAt > 0.5) || In > 7.0)''', '''		if ((RecordSeenAt > 0.0 && Clock - RecordSeenAt > 0.5) || Clock - RecordAt > 7.0)'''),
    ('''#include "Sound/SoundBase.h"''', '''#include "Sound/SoundBase.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"
#include "GameFramework/Controller.h"'''),
])

# ================================================================= level
edit(P + "Scripts/level/build_house.py", [
    ('''for cls in ("WCDoor", "WCNote", "WCPickup", "WCUsable", "WCTrigger", "WCEntity", "WCLook", "WCWatcher"):''',
     '''for cls in ("WCDoor", "WCNote", "WCPickup", "WCUsable", "WCTrigger", "WCEntity", "WCLook", "WCWatcher", "WCSmokeMan"):'''),
])
edit(P + "Scripts/level/memory.py", [
    ('''def mem_light(name, x, y, z, lumens, group, col=(1.0, 0.78, 0.5), radius=900.0):''', '''def smoke_man(name, x, y, z, yaw, tall, group):
    """The Company: black smoke in the shape of a man (AWCSmokeMan), hidden until the story shows it."""
    a = actors.spawn_actor_from_class(WC["WCSmokeMan"], V(x, y, z), R(yaw))
    a.set_actor_label(name)
    a.set_editor_property("tall", float(tall))
    a.set_actor_hidden_in_game(True)
    tag(a, [group])
    a.set_folder_path("House/" + MF)
    return a


def mem_light(name, x, y, z, lumens, group, col=(1.0, 0.78, 0.5), radius=900.0):'''),
    ('''figure("Mem3_Company", 1520, 545, UZ, 205, 0.86, "Tall", "Mem3", void=True, at=3.0)''', '''smoke_man("Mem3_Company", 1520, 545, UZ, 205, 290, "Mem3")'''),
])
edit(P + "Scripts/level/forest.py", [
    ('''_fig = figure("RoadShadow", _shx, _shy, -41, math.degrees(math.atan2(-_suy, -_sux)), 0.98, "Tall", "RoadShadow", void=True, at=3.0)''',
     '''_fig = smoke_man("RoadShadow", _shx, _shy, -41, math.degrees(math.atan2(-_suy, -_sux)), 310, "RoadShadow")'''),
    ('''cab("PillarBR", -30, -18, -80, -74, 100, 150)''', '''cab("PillarBR", -30, -18, -80, -74, 100, 150)
# the windscreen pillars (the car body itself is hidden while he sits in it)
for _sgn in (-1, 1):
    cpart(beam(f"PillarA_{_sgn}", (CRX + 100, CRY - _sgn * 74, -40 + 102), (CRX + 44, CRY - _sgn * 70, -40 + 150), 7, 6, DASH, wdir=(0, 1, 0), shadow=False, folder=CAB, tags=["CabinOnly"]))
cab("Hood", 110, 250, -82, 82, 86, 96)'''),
])

# ================================================================= the smoke material and its noise
edit(P + "Scripts/level/import_assets.py", [
    ('''    flat_material("M_Hair", (0.36, 0.33, 0.27), 0.55)''', '''    flat_material("M_Hair", (0.36, 0.33, 0.27), 0.55)
    smoke_material()'''),
    ('''def step_mats():''', '''def smoke_material():
    """Black smoke: unlit, see-through at the edge of every blob, with noise drifting up through it and the whole shape swaying."""
    src = SRC + "/Textures/misc/T_SmokeNoise.png"
    if not os.path.exists(src):
        log("no smoke noise texture (run Scripts/art/gen_noise.py)")
        return None
    import_files([src], G + "/Materials")
    nt = eal.load_asset(G + "/Materials/T_SmokeNoise")
    try:
        nt.set_editor_property("srgb", False)
        nt.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_GRAYSCALE)
        eal.save_loaded_asset(nt, False)
    except Exception as exc:
        log(f"smoke noise settings: {exc}")
    m = new_material("M_Smoke")
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided", False)
    usage(m, "INSTANCED_STATIC_MESHES")
    mel.connect_material_property(const3(m, (0.0, 0.0, 0.0), -300, -200), "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    wp = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1300, 0)
    tm = mel.create_material_expression(m, unreal.MaterialExpressionTime, -1300, 200)
    uv1 = _custom(m, "return WP.yz * 0.0052 + WP.x * 0.0021 + float2(0.0, T * 0.09);", ["WP", "T"], unreal.CustomMaterialOutputType.CMOT_FLOAT2, -1000, 0)
    uv2 = _custom(m, "return WP.xz * 0.0125 + float2(T * 0.04, T * 0.21);", ["WP", "T"], unreal.CustomMaterialOutputType.CMOT_FLOAT2, -1000, 200)
    for u_ in (uv1, uv2):
        mel.connect_material_expressions(wp, "", u_, "WP")
        mel.connect_material_expressions(tm, "", u_, "T")
    n1 = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 0)
    n2 = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 200)
    for n_, u_ in ((n1, uv1), (n2, uv2)):
        n_.set_editor_property("texture", nt)
        n_.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE)
        mel.connect_material_expressions(u_, "", n_, "UVs")
    fr = mel.create_material_expression(m, unreal.MaterialExpressionFresnel, -700, 420)
    fr.set_editor_property("exponent", 1.0)
    fr.set_editor_property("base_reflect_fraction", 0.0)
    op = _custom(m, "float edge = pow(saturate(1.0 - F), 1.8); float n = saturate(N1 * 1.25 + N2 * 0.55 - 0.3); return saturate(edge * (0.22 + 1.0 * n)) * 0.92;",
                 ["F", "N1", "N2"], unreal.CustomMaterialOutputType.CMOT_FLOAT1, -350, 200)
    mel.connect_material_expressions(fr, "", op, "F")
    mel.connect_material_expressions(n1, "R", op, "N1")
    mel.connect_material_expressions(n2, "R", op, "N2")
    mel.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
    wo = _custom(m, "float a = T * 1.25 + WP.z * 0.021; return float3(sin(a) * 4.5 + sin(T * 0.7 + WP.z * 0.05) * 2.5, cos(a * 0.83) * 4.5, sin(T * 0.9 + WP.x * 0.03) * 2.0);",
                 ["WP", "T"], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -350, 500)
    mel.connect_material_expressions(wp, "", wo, "WP")
    mel.connect_material_expressions(tm, "", wo, "T")
    mel.connect_material_property(wo, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    log("M_Smoke made")
    return m


def step_mats():'''),
])
print("ok")
