"""Pass 91: whole-game picture filters to try (Cheyenne 2026-11-19 06:27 and 14:18 UTC), as ONE switchable layer on top of the
game: a post-process material M_Filter with a "Look" dial, held by an unbound volume the director spawns.  Nothing else in the
game changes.   -WCFilter=N starts the game with look N;   -WCHerLook -WCFilterShots photographs every look at four spots.
   0 off   1 VHS camcorder   2 old film   3 cold, drained   4 fisheye bodycam   5 black-and-white night vision"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

# ---------------------------------------------------------------- the material (import step "items")
p = R + "Scripts/level/import_items.py"
s = open(p, encoding="utf-8").read()
assert "def filter_material" not in s
FILTER = r'''
FILTER_CODE = """
#define WCH(p) frac(sin(dot((p), float2(12.9898, 78.233))) * 43758.5453)
#define WCS(u) SceneTextureLookup(ViewportUVToSceneTextureUV(saturate(u), 14), 14, false).rgb
float2 uv = GetViewportUV(Parameters);
float2 vs = View.ViewSizeAndInvSize.xy;
float aspect = vs.x / max(vs.y, 1.0);
const float3 lum = float3(0.30, 0.59, 0.11);
int look = (int)(Look + 0.5);
float t = T;
float3 c = WCS(uv) + Dummy.rgb * 0.0;
if (look == 1)
{
    // VHS camcorder: lines that jitter, colours that slip sideways, a tracking band crawling up, snow, washed blacks
    float ln = floor(uv.y * 240.0);
    float jit = (WCH(float2(ln, floor(t * 30.0))) - 0.5) * 0.0016;
    float bar = frac(uv.y + t * 0.11);
    float band = smoothstep(0.0, 0.015, bar) * (1.0 - smoothstep(0.02, 0.07, bar));
    float2 u = uv + float2(jit + band * 0.010 * (WCH(float2(ln, floor(t * 24.0))) - 0.3), 0.0);
    u.x += step(0.972, uv.y) * (WCH(float2(ln, floor(t * 60.0))) - 0.5) * 0.06;
    float3 a = WCS(u + float2(0.0035, 0.0));
    float3 b = WCS(u);
    float3 d = WCS(u - float2(0.0035, 0.0));
    c = float3(a.r, (b.g * 2.0 + a.g + d.g) * 0.25, d.b);
    c = lerp(c, (a + b + d) / 3.0, 0.35);
    c = lerp(dot(c, lum), c, 0.72);
    c = c * 0.92 + 0.030;
    c *= 0.93 + 0.07 * sin(uv.y * 480.0 * 3.14159);
    c += (WCH(uv * vs * 0.5 + frac(t) * 91.7) - 0.5) * 0.10;
    c += band * 0.05;
    float2 dv = uv - 0.5;
    c *= saturate(1.10 - dot(dv, dv) * 0.9);
}
else if (look == 2)
{
    // old film: weave in the gate, flicker, sepia, scratches, dust, heavy grain, dark corners
    float fr = floor(t * 18.0);
    float2 u = uv + (float2(WCH(float2(fr, 1.3)), WCH(float2(fr, 7.1))) - 0.5) * 0.004;
    c = WCS(u);
    float l = pow(saturate(dot(c, lum) * 1.25), 0.9);
    c = l * float3(1.05, 0.93, 0.74);
    c *= 0.84 + 0.16 * WCH(float2(fr, 3.7));
    for (int k = 0; k < 3; ++k)
    {
        float sx = WCH(float2(floor(t * 2.0) + k * 3.1, k * 17.3));
        float on = step(0.45, WCH(float2(floor(t * 3.0) + k, 5.5)));
        c += on * (1.0 - smoothstep(0.0, 0.0011, abs(uv.x - sx - 0.002 * sin(uv.y * 9.0 + fr)))) * 0.30 * (0.4 + 0.6 * WCH(float2(floor(uv.y * 30.0), fr)));
    }
    float2 g = floor(uv * float2(70.0, 40.0));
    c *= 1.0 - step(0.9988, WCH(g + fr * 0.37)) * 0.85;
    c += (WCH(uv * vs * 0.6 + fr * 13.1) - 0.5) * 0.15;
    float2 dv = uv - 0.5;
    c *= saturate(1.16 - dot(dv, dv) * 2.0);
}
else if (look == 3)
{
    // cold and drained: most of the colour gone, blue in the shadows, harder contrast, a little grain
    float l = dot(c, lum);
    c = lerp(l, c, 0.30);
    c = pow(saturate(c), 1.14) * 1.10;
    c *= lerp(float3(0.74, 0.94, 1.22), float3(1.0, 1.0, 1.0), smoothstep(0.0, 0.55, l));
    c += (WCH(uv * vs * 0.5 + frac(t) * 37.0) - 0.5) * 0.035;
}
else if (look == 4)
{
    // bodycam: a fisheye lens with black corners, colour fringes toward the edge, a hard digital look
    float2 d = uv - 0.5;
    d.x *= aspect;
    float r2 = dot(d, d);
    float2 w = d * (1.0 + 0.62 * r2 + 0.50 * r2 * r2) * 0.74;
    w.x /= aspect;
    float2 u = w + 0.5;
    float ca = 0.012 * r2;
    c = float3(WCS(u + (u - 0.5) * ca).r, WCS(u).g, WCS(u - (u - 0.5) * ca).b);
    float inside = smoothstep(0.0, 0.012, min(min(u.x, 1.0 - u.x), min(u.y, 1.0 - u.y)));
    c *= inside;
    c *= saturate(1.30 - r2 * 2.3);
    c = lerp(dot(c, lum), c, 0.78) * float3(0.96, 1.0, 0.97);
    c = pow(saturate(c), 0.94);
    c += (WCH(floor(uv * vs * 0.5) + floor(t * 30.0) * 7.3) - 0.5) * 0.045;
}
else if (look == 5)
{
    // night vision in black and white: the dark lifted a long way, snow, lines, a round falloff like a scope
    float l = dot(c, lum);
    l = pow(saturate(l * 3.4), 0.60);
    l += (WCH(uv * vs * 0.5 + frac(t) * 53.0) - 0.5) * 0.20;
    l *= 0.90 + 0.10 * sin(uv.y * vs.y * 1.5708);
    float2 d = uv - 0.5;
    d.x *= aspect;
    l *= saturate(1.40 - dot(d, d) * 3.1);
    c = saturate(l) * float3(0.86, 0.95, 1.0);
}
return c;
"""


def filter_material():
    """The whole-game picture filter (see FILTER_CODE): a post-process material applied after tone mapping."""
    m = new_material("M_Filter")
    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_POST_PROCESS)
    for nm in ("BL_SCENE_COLOR_AFTER_TONEMAPPING", "BL_AFTER_TONEMAPPING"):
        loc = getattr(unreal.BlendableLocation, nm, None)
        if loc is not None:
            m.set_editor_property("blendable_location", loc)
            log("filter blend location " + nm)
            break
    st = mel.create_material_expression(m, unreal.MaterialExpressionSceneTexture, -900, 0)
    for nm in ("PPI_POST_PROCESS_INPUT0", "PPI_POSTPROCESS_INPUT0"):
        sid = getattr(unreal.SceneTextureId, nm, None)
        if sid is not None:
            st.set_editor_property("scene_texture_id", sid)
            break
    look = sparam(m, "Look", 0.0, -900, 260)
    tm = mel.create_material_expression(m, unreal.MaterialExpressionTime, -900, 380)
    out = _custom(m, FILTER_CODE, ["Dummy", "Look", "T"], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 100)
    mel.connect_material_expressions(st, "Color", out, "Dummy")
    mel.connect_material_expressions(look, "", out, "Look")
    mel.connect_material_expressions(tm, "", out, "T")
    mel.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    log("M_Filter made")


'''
s = s.replace("def step_items():", FILTER + "def step_items():\n    filter_material()", 1)
open(p, "w", encoding="utf-8", newline="\n").write(s)
compile(s, p, "exec")

# ---------------------------------------------------------------- the director holds the layer
edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('void TickEye(float Dt);', '''void TickEye(float Dt);
	/** Whole-game picture filter: 0 off, 1 VHS camcorder, 2 old film, 3 cold and drained, 4 fisheye bodycam, 5 black-and-white night vision. */
	void SetFilter(int32 Look);
	int32 FilterLook = 0;
	bool bFilterInit = false;
	UPROPERTY(Transient) TObjectPtr<class APostProcessVolume> FilterVolume;
	UPROPERTY(Transient) TObjectPtr<class UMaterialInstanceDynamic> FilterMID;'''),
])
edit(R + "Source/WellnessCheck/WCHouse.cpp", [
    ('''TickEye(Dt);''', '''TickEye(Dt);
	if (!bFilterInit) { bFilterInit = true; int32 L = 0; if (FParse::Value(FCommandLine::Get(), TEXT("WCFilter="), L)) SetFilter(L); }'''),
])
p = R + "Source/WellnessCheck/WCEvents.cpp"
s = open(p, encoding="utf-8").read()
assert "SetFilter" not in s
s = s.replace('#include "Kismet/KismetRenderingLibrary.h"', '#include "Kismet/KismetRenderingLibrary.h"\n#include "Engine/PostProcessVolume.h"', 1)
s += r'''
// ================================================================================================ the picture filter
// One layer over the finished picture, switched by a number.  It changes nothing in the game itself.
void AWCDirector::SetFilter(int32 Look)
{
	FilterLook = FMath::Clamp(Look, 0, 5);
	if (!FilterVolume)
	{
		UMaterialInterface* M = LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/WC/Materials/M_Filter.M_Filter"));
		if (!M) { UE_LOG(LogWCEvents, Warning, TEXT("WCFILTER no M_Filter (import step items)")); return; }
		FilterVolume = GetWorld()->SpawnActor<APostProcessVolume>();
		if (!FilterVolume) return;
		FilterVolume->bUnbound = true;
		FilterVolume->Priority = 100.f;
		FilterMID = UMaterialInstanceDynamic::Create(M, this);
		FilterVolume->Settings.AddBlendable(FilterMID, 1.f);
	}
	FilterMID->SetScalarParameterValue(TEXT("Look"), (float)FilterLook);
	FilterVolume->bEnabled = FilterLook > 0;
	FilterVolume->BlendWeight = FilterLook > 0 ? 1.f : 0.f;
	UE_LOG(LogWCEvents, Display, TEXT("WCFILTER look %d"), FilterLook);
}
'''
open(p, "w", encoding="utf-8", newline="\n").write(s)

# ---------------------------------------------------------------- photographs of every look at the same four spots
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''else if (FParse::Param(FCommandLine::Get(), TEXT("WCPeekOnly")))''',
     '''else if (FParse::Param(FCommandLine::Get(), TEXT("WCFilterShots")))
		{
			Set(TEXT("inside")); Set(TEXT("locked_in")); Set(TEXT("tv_first")); Set(TEXT("tv_test"));
			static const TCHAR* Names[6] = { TEXT("0_off"), TEXT("1_vhs"), TEXT("2_oldfilm"), TEXT("3_cold"), TEXT("4_bodycam"), TEXT("5_nightvision") };
			static FString Keep[40];
			int32 KeepN = 0;
			auto Looks = [&](const TCHAR* Spot)
			{
				for (int32 L = 0; L < 6; ++L)
				{
					AutoSteps.Add({ A_Do, FName(*FString::Printf(TEXT("filter:%d"), L)), 0.f }); Wait(0.45f);
					Keep[KeepN] = FString::Printf(TEXT("%s_%s"), Spot, Names[L]);
					AutoSteps.Add({ A_Shot, FName(*Keep[KeepN]), 0.f }); ++KeepN;
				}
				AutoSteps.Add({ A_Do, TEXT("filter:0"), 0.f });
			};
			// 1 the front hall with its lamp on   2 the television playing   3 Edith in the hall   4 the house from the yard
			AutoSteps.Add({ A_Do, TEXT("at:230,40,92,0,-2"), 0.f }); Wait(1.2f); Looks(TEXT("a_hall"));
			AutoSteps.Add({ A_Do, TEXT("at:366,-400,92,-90,-14"), 0.f }); Wait(0.4f); AutoSteps.Add({ A_Do, TEXT("tvon"), 0.f }); Wait(6.5f); Looks(TEXT("b_television"));
			AutoSteps.Add({ A_Do, TEXT("at:1500,0,92,180,6"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Her, TEXT("Idle"), 300.f }); Wait(0.8f); Looks(TEXT("c_edith"));
			AutoSteps.Add({ A_Do, TEXT("at:-1500,60,144,0,8"), 0.f }); Wait(1.5f); Looks(TEXT("d_house"));
			Wait(1.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCPeekOnly")))'''),
    ('''else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }''',
     '''else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }
		else if (S.Arg.ToString().StartsWith(TEXT("filter:"))) { SetFilter(FCString::Atoi(*S.Arg.ToString().Mid(7))); }'''),
])
print("pass 91 applied")
