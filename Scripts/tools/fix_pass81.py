"""Pass 81: the television can be seen and its picture lights up.
  - the sofa was standing in front of the set: it now faces it from the middle of the room
  - the tube is far brighter (the picture was about a tenth of what the flashlight throws on the glass) and the glass darker
  - the cabinet is dark wood, not cream
  - the reflection scare: his flashlight sinks while the glass is dead, she carries more light, the mirror is brighter;
    the test saves what the glass sees
  - her skin material is allowed on morph targets (the log said the default material would be used)"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

edit(R + "Scripts/level/import_assets.py", [
    ('''usage(m, "SKELETAL_MESH")
    tb = mel''', '''usage(m, "SKELETAL_MESH")
    usage(m, "MORPH_TARGETS")
    tb = mel'''),
])

edit(R + "Scripts/level/import_items.py", [
    ('("Gain", 26.0), ("RGain", 9.0)', '("Gain", 300.0), ("RGain", 30.0)'),
    ('const3(m, (0.012, 0.015, 0.015), -600, -200)', 'const3(m, (0.002, 0.0025, 0.0025), -600, -200)'),
    ('''    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".fbx"):
            continue
        name = f[:-4]''', '''    # the television's own cabinet: dark old wood and black fittings (plain item colours go cream under the flashlight)
    tvm = dict(mats)
    wood = G + "/Materials/MI_WoodDark"
    tvm["Wood"] = eal.load_asset(wood) if eal.does_asset_exist(wood) else item_material("M_TVWood", (0.02, 0.011, 0.006), 0.5, 0.0)
    tvm["Polymer"] = item_material("M_TVBezel", (0.004, 0.004, 0.0045), 0.35, 0.0)
    tvm["Gunmetal"] = item_material("M_TVPanel", (0.028, 0.026, 0.022), 0.5, 0.0)
    tvm["Brass"] = item_material("M_TVKnob", (0.16, 0.11, 0.04), 0.4, 1.0)
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".fbx"):
            continue
        name = f[:-4]'''),
    ('''key = next((k for k in mats if slot.lower().startswith(k.lower())), None)
            if key:
                sm.set_material(i, mats[key])''', '''key = next((k for k in mats if slot.lower().startswith(k.lower())), None)
            if key:
                sm.set_material(i, (tvm if name == "SM_Item_TV" else mats)[key])'''),
])

edit(R + "Scripts/level/build_house.py", [
    ('''place("Sofa_Sagging_Broken", 420, -540, GZ, 0, L)
place("Armchair_Wingback_Torn", 230, -330, GZ, 60, L)
place("Armchair_Tipped", 620, -330, GZ, 120, L)''',
     '''place("Sofa_Sagging_Broken", 370, -300, GZ, 180, L)          # in the middle of the room, facing the television on the south wall
place("Armchair_Wingback_Torn", 545, -265, GZ, 205, L)
place("Armchair_Tipped", 615, -415, GZ, 120, L)'''),
    ('("A_Living", 380, -330, GZ, 200)', '("A_Living", 372, -425, GZ, 270)'),
])

edit(R + "Source/WellnessCheck/WCEvents.cpp", [
    ('#include "Materials/MaterialInstanceDynamic.h"', '#include "Materials/MaterialInstanceDynamic.h"\n#include "Kismet/KismetRenderingLibrary.h"\n#include "Misc/CommandLine.h"\n#include "Misc/Parse.h"'),
    ('''TVScreen = Tv->Mesh->CreateDynamicMaterialInstance(Slot);''',
     '''TVScreen = Tv->Mesh->CreateDynamicMaterialInstance(Slot);
		UE_LOG(LogWCEvents, Display, TEXT("WCTV screen slot %d of %d, material %s, parent %s"), Slot, Tv->Mesh->GetNumMaterials(), *GetNameSafe(Tv->Mesh->GetMaterial(Slot)), TVScreen ? *GetNameSafe(TVScreen->Parent) : TEXT("none"));
		float G = 0.f;
		if (TVScreen && FParse::Value(FCommandLine::Get(), TEXT("WCTVGain="), G)) TVScreen->SetScalarParameterValue(TEXT("Gain"), G);
		if (TVScreen && FParse::Value(FCommandLine::Get(), TEXT("WCTVRGain="), G)) TVScreen->SetScalarParameterValue(TEXT("RGain"), G);'''),
    ('TVGlow->SetIntensity(2600.f * (0.72f', 'TVGlow->SetIntensity(1500.f * (0.72f'),
    ('''TVScreen->SetScalarParameterValue(TEXT("Mode"), 2.f);
	SetLoop(''', '''TVScreen->SetScalarParameterValue(TEXT("Mode"), 2.f);
	P->SetLightScale(0.07f);                     // his own light sinks with the tube: the dead glass is the brightest thing left
	SetLoop('''),
    ('''if (TVScreen) TVScreen->SetScalarParameterValue(TEXT("Mode"), 0.f);
	for (TObjectIterator<UAudioComponent> It;''', '''if (TVScreen) TVScreen->SetScalarParameterValue(TEXT("Mode"), 0.f);
	if (AWCCharacter* Pl = Player()) { Pl->SetLightScale(1.f); Pl->FlickerLight(0.5f, 0.7f); }
	for (TObjectIterator<UAudioComponent> It;'''),
    ('TVHerLight->SetIntensity(340.f);', 'TVHerLight->SetIntensity(1500.f);'),
    ('TVHerLight->SetAttenuationRadius(520.f);', 'TVHerLight->SetAttenuationRadius(700.f);'),
    ('''After(0.62f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_2.png"), false, false); });''',
     '''After(0.62f, [D0]() { FScreenshotRequest::RequestScreenshot(D0 / TEXT("S13_tv_reflection_2.png"), false, false); });
			After(0.45f, [this, D0]() { if (TVTarget) UKismetRenderingLibrary::ExportRenderTarget(this, TVTarget, D0, TEXT("S13_what_the_glass_sees.png")); });'''),
])

edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''AutoSteps.Add({ A_Do, TEXT("tvon"), 0.f }); Wait(3.2f); Shot(TEXT("tv_1_title")); Wait(4.0f); Shot(TEXT("tv_2_playing")); Wait(6.0f); Shot(TEXT("tv_3_playing"));
			AutoSteps.Add({ A_Do, TEXT("at:330,-250,92,-84,-8"), 0.f }); Wait(1.2f); Shot(TEXT("tv_4_room_lit_by_it"));
			AutoSteps.Add({ A_Do, TEXT("at:352,-400,92,-90,-36"), 0.f }); Wait(1.0f);''',
     '''AutoSteps.Add({ A_Do, TEXT("tvon"), 0.f }); Wait(1.6f); Shot(TEXT("tv_1_title")); Wait(3.0f); Shot(TEXT("tv_2_playing")); Wait(3.0f); Shot(TEXT("tv_3_playing"));
			AutoSteps.Add({ A_Do, TEXT("tvgain:90"), 0.f }); Wait(0.5f); Shot(TEXT("tv_3b_gain90"));
			AutoSteps.Add({ A_Do, TEXT("tvgain:1000"), 0.f }); Wait(0.5f); Shot(TEXT("tv_3c_gain1000"));
			AutoSteps.Add({ A_Do, TEXT("tvgain:300"), 0.f });
			AutoSteps.Add({ A_Do, TEXT("at:250,-215,92,-70,-10"), 0.f }); Wait(1.2f); Shot(TEXT("tv_4_room_lit_by_it"));
			AutoSteps.Add({ A_Do, TEXT("at:372,-425,92,-90,-12"), 0.f }); Wait(1.0f);'''),
    ('''else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }''',
     '''else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }
		else if (S.Arg.ToString().StartsWith(TEXT("tvgain:"))) { if (TVScreen) TVScreen->SetScalarParameterValue(TEXT("Gain"), FCString::Atof(*S.Arg.ToString().Mid(7))); }'''),
])
print("pass 81 applied")
