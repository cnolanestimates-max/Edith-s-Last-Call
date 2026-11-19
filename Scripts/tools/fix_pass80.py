"""The television (Cheyenne 03:54 UTC).  An old console set in the living room, facing the hall doors.
 - Some time when he comes near, it switches itself on and plays one of the tapes (a different one each time), lighting
   the room.  Left alone it plays three times through and clicks off.  He can switch it off.
 - The first time HE switches it off in a quiet stretch: the dead screen shows the room behind him, and in it she is at
   the far door, then running at him, screaming, the picture shaking.  She exists only in the glass: when he turns round
   there is nothing.  (She is drawn only for the camera that feeds the screen.)
 - Test: -WCHerLook -WCTVOnly photographs the set playing and the reflection."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
P = "C:/GameDev/Unreal/WellnessCheck/"
R = P + "Source/WellnessCheck/"

edit(R + "WCDirector.h", [
    ('''	void LeftScare();''', '''	void LeftScare();
	// the television
	int32 TVPhase = 0, TVTape = 0;              // 0 off, 1 playing, 2 the reflection
	double TVAt = 0.0, TVNextAt = -1.0, TVHerAt = -1.0;
	TWeakObjectPtr<UAudioComponent> TVAudio;
	UPROPERTY(Transient) TObjectPtr<class UMaterialInstanceDynamic> TVScreen;
	UPROPERTY(Transient) TObjectPtr<class UPointLightComponent> TVGlow;
	UPROPERTY(Transient) TObjectPtr<class UPointLightComponent> TVHerLight;
	UPROPERTY(Transient) TObjectPtr<class USceneCaptureComponent2D> TVCapture;
	UPROPERTY(Transient) TObjectPtr<class UTextureRenderTarget2D> TVTarget;
	void TickTV(float Dt);
	void TVOn();
	void TVOff(bool bByHim, bool bForceScare = false);
	void TVReflectionEnd();'''),
])
edit(R + "WCHouse.cpp", [
    ('''	TickRecord(Dt);''', '''	TickRecord(Dt);
	TickTV(Dt);'''),
])
s = io.open(R + "WCEvents.cpp", encoding="utf-8").read()
s = s.replace('''#include "GameFramework/Controller.h"''', '''#include "GameFramework/Controller.h"
#include "Components/PointLightComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Components/SceneCaptureComponent2D.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/Texture2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Materials/MaterialInstanceDynamic.h"''', 1)
s = s.replace('''	if (Id == TEXT("use:phonograph"))''', '''	if (Id == TEXT("use:tv"))
	{
		if (TVPhase == 1) TVOff(true);
		else if (TVPhase == 0) Think(TEXT("An old console set. The screen is grey with dust, except where a hand has wiped it."));
		return true;
	}
	if (Id == TEXT("use:phonograph"))''', 1)
if "AWCDirector::TickTV" not in s:
    s = s.rstrip() + r'''

// ================================================================================================ the television (S13)
static const int32 GTapeFrames = 240;        // 20 s at 12 a second, 16 across and 15 down
static const float GTapeFps = 12.f;

void AWCDirector::TVOn()
{
	AWCInteractable* Tv = Thing(TEXT("tv"));
	if (!Tv || !Tv->Mesh) return;
	if (!TVScreen)
	{
		// the picture is whichever material slot is called Screen
		const int32 Slot = FMath::Max(0, Tv->Mesh->GetMaterialIndex(TEXT("Screen")));
		TVScreen = Tv->Mesh->CreateDynamicMaterialInstance(Slot);
		TVGlow = NewObject<UPointLightComponent>(Tv);
		TVGlow->SetupAttachment(Tv->GetRootComponent());
		TVGlow->RegisterComponent();
		TVGlow->SetIntensityUnits(ELightUnits::Lumens);
		TVGlow->SetAttenuationRadius(700.f);
		TVGlow->SetLightColor(FLinearColor(0.62f, 0.74f, 1.f));
		TVGlow->SetCastShadows(true);
		TVGlow->SetIntensity(0.f);
	}
	int32 Tapes = 0;
	for (int32 i = 1; i <= 8; ++i) if (LoadObject<UTexture2D>(nullptr, *FString::Printf(TEXT("/Game/WC/TV/T_Tape_%d.T_Tape_%d"), i, i), nullptr, LOAD_NoWarn | LOAD_Quiet)) Tapes = i; else break;
	if (Tapes == 0 || !TVScreen) { UE_LOG(LogWCEvents, Warning, TEXT("WCTV no tapes imported")); TVNextAt = Clock + 600.0; return; }
	const int32 N = 1 + (TVTape % Tapes);
	++TVTape;
	TVScreen->SetTextureParameterValue(TEXT("Atlas"), LoadObject<UTexture2D>(nullptr, *FString::Printf(TEXT("/Game/WC/TV/T_Tape_%d.T_Tape_%d"), N, N)));
	TVScreen->SetScalarParameterValue(TEXT("Mode"), 1.f);
	TVScreen->SetScalarParameterValue(TEXT("Frame"), 0.f);
	const FVector At = Tv->GetActorLocation() + FVector(0, 0, 55);
	// in front of the glass, wherever the set faces
	TVGlow->SetWorldLocation(At + (Player() ? (Player()->GetActorLocation() - At).GetSafeNormal2D() * 45.f : FVector(0, 45, 0)));
	PlayAt(TEXT("switch_click"), At, 1.f, 0.8f, 1500.f);
	if (TVAudio.IsValid()) TVAudio->Stop();
	TVAudio = PlayAt(FString::Printf(TEXT("tv_tape_%d"), N), At, 1.f, 1.f, 2400.f);
	Tv->Prompt = TEXT("Switch the television off");
	TVPhase = 1;
	TVAt = Clock;
	Tension = FMath::Max(Tension, 0.6f);
	UE_LOG(LogWCEvents, Display, TEXT("WCTV t=%.1f switched itself on, tape %d of %d"), PlaySeconds, N, Tapes);
	if (!Has(TEXT("tv_seen"))) { Set(TEXT("tv_seen")); After(2.5f, [this]() { Think(TEXT("That set was not on.")); }); }
}

void AWCDirector::TVOff(bool bByHim, bool bForceScare)
{
	AWCInteractable* Tv = Thing(TEXT("tv"));
	AWCCharacter* P = Player();
	if (!Tv || !TVScreen) return;
	const FVector At = Tv->GetActorLocation() + FVector(0, 0, 55);
	if (TVAudio.IsValid()) { TVAudio->Stop(); TVAudio = nullptr; }
	PlayAt(TEXT("switch_click"), At, 1.f, 0.7f, 1500.f);
	PlayAt(TEXT("bulb_die"), At, 0.5f, 1.3f, 1200.f);
	if (TVGlow) TVGlow->SetIntensity(0.f);
	Tv->Prompt = TEXT("Look at the television");
	const bool bScare = P && (bForceScare || (bByHim && !Has(TEXT("tv_scare")) && Clock >= NextScareAt && StalkState == 0 && !bEventBusy && !bBusy));
	if (!bScare)
	{
		TVScreen->SetScalarParameterValue(TEXT("Mode"), 0.f);
		TVPhase = 0;
		TVNextAt = Clock + 420.0 * FMath::Max(TestPace, 0.25f);
		return;
	}
	// ---- the dead glass shows the room behind him
	UE_LOG(LogWCEvents, Display, TEXT("WCSCARE t=%.1f S13_tv_reflection"), PlaySeconds);
	Set(TEXT("tv_scare"));
	bEventBusy = true;
	if (!TVTarget)
	{
		TVTarget = NewObject<UTextureRenderTarget2D>(this);
		TVTarget->RenderTargetFormat = RTF_RGBA8;
		TVTarget->InitAutoFormat(512, 384);
		TVTarget->UpdateResourceImmediate(true);
		TVCapture = NewObject<USceneCaptureComponent2D>(Tv);
		TVCapture->SetupAttachment(Tv->GetRootComponent());
		TVCapture->RegisterComponent();
		TVCapture->TextureTarget = TVTarget;
		TVCapture->CaptureSource = ESceneCaptureSource::SCS_FinalColorLDR;
		TVCapture->FOVAngle = 78.f;
		TVCapture->bCaptureOnMovement = false;
	}
	const FVector Out = (P->GetActorLocation() - At).GetSafeNormal2D();
	TVCapture->SetWorldLocationAndRotation(At + Out * 34.f + FVector(0, 0, 8), FRotator(9.f, Out.Rotation().Yaw, 0.f));
	TVCapture->bCaptureEveryFrame = true;
	TVCapture->SetActive(true);
	TVScreen->SetTextureParameterValue(TEXT("Reflect"), TVTarget);
	TVScreen->SetScalarParameterValue(TEXT("Mode"), 2.f);
	SetLoop(TEXT("amb"), TEXT("amb_house"), 0.05f, 0.4f);
	TVPhase = 2;
	TVAt = Clock;
	TVHerAt = -1.0;
}

void AWCDirector::TVReflectionEnd()
{
	if (AWCEntity* H = Her())
	{
		TInlineComponentArray<UPrimitiveComponent*> Prims(H);
		for (UPrimitiveComponent* C : Prims) { C->bVisibleInSceneCaptureOnly = false; C->MarkRenderStateDirty(); }
		H->Vanish();
	}
	if (TVHerLight) { TVHerLight->DestroyComponent(); TVHerLight = nullptr; }
	if (TVCapture) { TVCapture->bCaptureEveryFrame = false; TVCapture->SetActive(false); }
	if (TVScreen) TVScreen->SetScalarParameterValue(TEXT("Mode"), 0.f);
	for (TObjectIterator<UAudioComponent> It; It; ++It) if (It->GetWorld() == GetWorld() && It->Sound && It->Sound->GetName().Contains(TEXT("her_scream"))) It->FadeOut(0.12f, 0.f);
	TVPhase = 0;
	TVNextAt = Clock + 420.0 * FMath::Max(TestPace, 0.25f);
	bEventBusy = false;
	Rest(170.f);
	Tension = 0.7f;
	ApplyWorldState();
	After(1.6f, [this]() { Think(TEXT("...Nothing. Nothing behind me.")); });
	Checkpoint(TEXT("tv"));
}

void AWCDirector::TickTV(float Dt)
{
	AWCCharacter* P = Player();
	AWCInteractable* Tv = Thing(TEXT("tv"));
	if (!P || !Tv) return;
	const FVector At = Tv->GetActorLocation() + FVector(0, 0, 55);
	if (TVPhase == 0)
	{
		if (!Has(TEXT("locked_in")) || Has(TEXT("dawn")) || Has(TEXT("sprint_started"))) return;
		if (TVNextAt < 0.0) TVNextAt = Clock + 150.0 * FMath::Max(TestPace, 0.25f);
		// he is near enough to see it come on, and nothing else is happening
		if (Clock >= TVNextAt && Gate() && !bBusy && !P->IsDown() && FVector::Dist(P->GetActorLocation(), At) < 760.f && FMath::Abs(P->GetActorLocation().Z - 88.f - Tv->GetActorLocation().Z) < 120.f) TVOn();
		return;
	}
	if (TVPhase == 1)
	{
		const float T = (float)(Clock - TVAt);
		if (TVScreen) TVScreen->SetScalarParameterValue(TEXT("Frame"), (float)(FMath::FloorToInt(T * GTapeFps) % GTapeFrames));
		if (TVGlow) TVGlow->SetIntensity(520.f * (0.72f + 0.2f * FMath::Sin(T * 23.f) * FMath::Sin(T * 7.1f) + 0.08f * FMath::Sin(T * 61.f)));
		if (TVAudio.IsValid() && !TVAudio->IsPlaying() && T < 58.f) TVAudio->Play();          // the tape comes round again
		if (T > 60.f) TVOff(false);
		return;
	}
	// ---- the reflection
	const float T = (float)(Clock - TVAt);
	AWCEntity* H = Her();
	const FVector ToTv = (At - P->GetActorLocation()).GetSafeNormal2D();
	const bool bTurned = FVector::DotProduct(P->EyeForward().GetSafeNormal2D(), ToTv) < -0.05f;
	if (TVHerAt < 0.0 && T > 1.3f && H)
	{
		// at the far door, behind him: only the glass can see her
		const FVector Far = Pos(TEXT("Her_TVFar"));
		H->Appear(Far, (P->GetActorLocation() - Far).Rotation().Yaw, TEXT("Run"));
		TInlineComponentArray<UPrimitiveComponent*> Prims(H);
		for (UPrimitiveComponent* C : Prims) { C->bVisibleInSceneCaptureOnly = true; C->MarkRenderStateDirty(); }
		TVHerLight = NewObject<UPointLightComponent>(H);
		TVHerLight->SetupAttachment(H->GetRootComponent());
		TVHerLight->RegisterComponent();
		TVHerLight->SetRelativeLocation(FVector(70.f, 0.f, 190.f));
		TVHerLight->SetIntensityUnits(ELightUnits::Lumens);
		TVHerLight->SetIntensity(340.f);
		TVHerLight->SetAttenuationRadius(520.f);
		TVHerLight->SetLightColor(FLinearColor(0.8f, 0.86f, 1.f));
		TVHerLight->SetCastShadows(false);
		TArray<FVector> Pts; Pts.Add(P->GetActorLocation() - FVector(0, 0, 88.f));
		H->MoveAlong(Pts, 880.f, TEXT("Run"));
		H->SetScream(1.f);
		Play2D(TEXT("her_scream"), 1.f);
		Play2D(TEXT("sting_hit"), 0.9f, EWCSnd::Music);
		TVHerAt = Clock;
		Tension = 1.f;
		if (bAuto && !AutoShotDir.IsEmpty())
		{
			const FString D0 = AutoShotDir;
			After(0.30f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_1.png"), false, false); });
			After(0.62f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_2.png"), false, false); });
		}
	}
	if (TVHerAt > 0.0)
	{
		P->AddShake(0.75f);
		const bool bReached = H && H->IsShown() && H->DistToPlayer() < 175.f;
		if (bTurned || bReached || Clock - TVHerAt > 1.5) TVReflectionEnd();
	}
	else if (bTurned && T > 0.4f) TVReflectionEnd();            // he turned before she came: the room is empty
}
'''
io.open(R + "WCEvents.cpp", "w", encoding="utf-8", newline="\n").write(s)

# ---- bot test
edit(R + "WCAuto.cpp", [
    ('''		if (FParse::Param(FCommandLine::Get(), TEXT("WCCarOnly")))
		{''', '''		if (FParse::Param(FCommandLine::Get(), TEXT("WCTVOnly")))
		{
			Set(TEXT("locked_in"));
			AutoSteps.Add({ A_Tele, TEXT("A_Living"), 0.f }); Wait(1.0f); AutoSteps.Add({ A_Look, TEXT("tv"), 0.f }); Wait(0.5f); Shot(TEXT("tv_0_off"));
			AutoSteps.Add({ A_Do, TEXT("tvon"), 0.f }); Wait(3.2f); Shot(TEXT("tv_1_title")); Wait(4.0f); Shot(TEXT("tv_2_playing")); Wait(6.0f); Shot(TEXT("tv_3_playing"));
			AutoSteps.Add({ A_Do, TEXT("at:330,-250,92,-84,-8"), 0.f }); Wait(1.2f); Shot(TEXT("tv_4_room_lit_by_it"));
			AutoSteps.Add({ A_Do, TEXT("at:352,-455,92,-90,-14"), 0.f }); Wait(1.0f);
			AutoSteps.Add({ A_Do, TEXT("tvoff"), 0.f }); Wait(0.9f); Shot(TEXT("tv_5_dead_glass")); Wait(3.0f); Shot(TEXT("tv_6_after")); Wait(2.0f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCCarOnly")))
		{'''),
    ('''		else if (S.Arg == TEXT("s7")) { bBusy = false; ScareUnderBed(); }''', '''		else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }
		else if (S.Arg == TEXT("tvoff")) { TVOff(true, true); }
		else if (S.Arg == TEXT("s7")) { bBusy = false; ScareUnderBed(); }'''),
])

# ---- level: the set, and where she starts from
edit(P + "Scripts/level/build_house.py", [
    ('''place("Portrait_Slashed", 300, -581, GZ + 150, 0, L, collide=False)
place("Portrait_Small", 430, -581, GZ + 170, 0, L, collide=False)''', '''place("Portrait_Slashed", 250, -581, GZ + 165, 0, L, collide=False)
place("Portrait_Small", 470, -581, GZ + 175, 0, L, collide=False)
# the television: against the south wall between the portraits, facing the hall doors
if ITEM("TV"):
    interact("WCUsable", "tv", ITEM("TV"), 360, -548, GZ, float(os.environ.get("WC_TV_YAW", "0")), "Look at the television", (48, 28, 44), (0, 0, 52))
    point("Her_TVFar", 205, 235, GZ, -80)'''),
])

# ---- import: the screen material, the tapes
s = io.open(P + "Scripts/level/import_items.py", encoding="utf-8").read()
if "def tv_material" not in s:
    s = s.replace('''def step_items():''', '''def tv_material():
    """The television picture: one frame out of a sheet of 240, or the dead glass showing a mirror of the room."""
    D = G + "/TV"
    eal.make_directory(D)
    tdir = SRC + "/TV"
    files = [f"{tdir}/{f}" for f in sorted(os.listdir(tdir))] if os.path.isdir(tdir) else []
    files = [f for f in files if os.path.basename(f).startswith("T_Tape_") and f.endswith(".png")]
    if files:
        import_files(files, D)
    first = None
    for f in files:
        t = eal.load_asset(f"{D}/{os.path.basename(f)[:-4]}")
        if not t:
            continue
        first = first or t
        for prop, val in (("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS), ("never_stream", True), ("srgb", True),
                          ("filter", unreal.TextureFilter.TF_BILINEAR)):
            try:
                t.set_editor_property(prop, val)
            except Exception as exc:
                log(f"tape texture {prop}: {exc}")
        eal.save_loaded_asset(t, False)
    first = first or eal.load_asset(G + "/Drawings/draw_1")
    F1, F2, F3 = unreal.CustomMaterialOutputType.CMOT_FLOAT1, unreal.CustomMaterialOutputType.CMOT_FLOAT2, unreal.CustomMaterialOutputType.CMOT_FLOAT3
    m = new_material("M_TV")
    tc = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1700, 0)
    prm = {n: sparam(m, n, d, -1700, 160 + 110 * i) for i, (n, d) in enumerate((("Frame", 0.0), ("Cols", 16.0), ("Rows", 15.0), ("Flip", 0.0), ("Mode", 0.0), ("Gain", 2.2), ("RGain", 1.3)))}
    uv = _custom(m, "float2 uv = UV; uv.x = lerp(uv.x, 1.0 - uv.x, Flip); float f = floor(Frame + 0.5); float c = fmod(f, Cols); float r = floor(f / Cols); "
                    "return (float2(c, r) + clamp(uv, 0.004, 0.996)) / float2(Cols, Rows);", ["UV", "Frame", "Cols", "Rows", "Flip"], F2, -1300, 0)
    mel.connect_material_expressions(tc, "", uv, "UV")
    for n in ("Frame", "Cols", "Rows", "Flip"):
        mel.connect_material_expressions(prm[n], "", uv, n)
    ruv = _custom(m, "float2 uv = UV; uv.x = lerp(1.0 - uv.x, uv.x, Flip); return uv;", ["UV", "Flip"], F2, -1300, 320)
    mel.connect_material_expressions(tc, "", ruv, "UV")
    mel.connect_material_expressions(prm["Flip"], "", ruv, "Flip")
    atlas = mel.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -1000, 0)
    atlas.set_editor_property("parameter_name", "Atlas")
    atlas.set_editor_property("texture", first)
    mel.connect_material_expressions(uv, "", atlas, "UVs")
    refl = mel.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -1000, 320)
    refl.set_editor_property("parameter_name", "Reflect")
    refl.set_editor_property("texture", first)
    mel.connect_material_expressions(ruv, "", refl, "UVs")
    out = _custom(m, "float w1 = saturate(1.0 - abs(Mode - 1.0)); float w2 = saturate(Mode - 1.0); float sl = 0.84 + 0.16 * sin(UV.y * 1500.0); "
                     "float3 c = V * Gain * w1 * sl + Rf * RGain * w2; float2 d = UV - 0.5; return c * saturate(1.12 - dot(d, d) * 1.5);",
                  ["V", "Rf", "UV", "Mode", "Gain", "RGain"], F3, -600, 100)
    mel.connect_material_expressions(atlas, "RGB", out, "V")
    mel.connect_material_expressions(refl, "RGB", out, "Rf")
    mel.connect_material_expressions(tc, "", out, "UV")
    for n in ("Mode", "Gain", "RGain"):
        mel.connect_material_expressions(prm[n], "", out, n)
    mel.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.connect_material_property(const3(m, (0.012, 0.015, 0.015), -600, -200), "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(const1(m, 0.14, -600, -80), "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    log(f"M_TV made, {len(files)} tapes")
    return m


def step_items():''', 1)
    s = s.replace('''        "Gunmetal": item_material("M_ItemGunmetal", (0.075, 0.075, 0.08), 0.36, 1.0),''', '''        "Gunmetal": item_material("M_ItemGunmetal", (0.075, 0.075, 0.08), 0.36, 1.0),
        "Wood": item_material("M_ItemWood", (0.13, 0.07, 0.04), 0.55, 0.0),
        "Screen": tv_material(),''', 1)
    io.open(P + "Scripts/level/import_items.py", "w", encoding="utf-8", newline="\n").write(s)
    compile(s, "import_items.py", "exec")
print("ok")
