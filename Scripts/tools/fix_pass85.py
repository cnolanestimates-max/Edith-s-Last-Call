"""Pass 85: the mirror exposure is settled (the test sweep goes), the eye test stands in the long rear hall,
only the tapes Cheyenne approved are imported (stale tape assets are deleted)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

edit(R + "Source/WellnessCheck/WCEvents.cpp", [
    ('float Ev = -1.5f;', 'float Ev = -2.0f;'),
    ('''After(0.85f, [this]() { if (TVCapture) TVCapture->PostProcessSettings.AutoExposureBias += 2.5f; });
			After(1.5f, [this, D0]() { if (TVTarget) UKismetRenderingLibrary::ExportRenderTarget(this, TVTarget, D0, TEXT("S13_what_the_glass_sees_standing_plus2.png")); });
			After(1.55f, [this]() { if (TVCapture) TVCapture->PostProcessSettings.AutoExposureBias -= 2.5f; });''', ''''''),
])

edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('AutoSteps.Add({ A_Do, TEXT("at:320,0,92,0,0"), 0.f }); Wait(1.5f); Shot(TEXT("eye_0_hall_before"));',
     'AutoSteps.Add({ A_Do, TEXT("at:2600,0,92,180,0"), 0.f }); Wait(1.5f); Shot(TEXT("eye_0_hall_before"));'),
    ('AutoSteps.Add({ A_Do, TEXT("at:320,0,92,40,-6"), 0.f }); Wait(1.6f); Shot(TEXT("eye_4_light_away_eye_back"));',
     'AutoSteps.Add({ A_Do, TEXT("at:2600,0,92,146,-8"), 0.f }); Wait(1.6f); Shot(TEXT("eye_4_light_away_eye_back"));'),
    ('AutoSteps.Add({ A_Do, TEXT("at:320,0,92,0,0"), 0.f }); Wait(0.7f); Shot(TEXT("eye_5_gone"));',
     'AutoSteps.Add({ A_Do, TEXT("at:2600,0,92,180,0"), 0.f }); Wait(0.7f); Shot(TEXT("eye_5_gone"));'),
])

edit(R + "Scripts/level/import_items.py", [
    ('''    first = first or eal.load_asset(G + "/Drawings/draw_1")''',
     '''    for n in range(len(files) + 1, 9):                    # tapes that were retired must not stay playable
        for stale in (f"{D}/T_Tape_{n}", f"{G}/Audio/tv_tape_{n}"):
            if eal.does_asset_exist(stale):
                eal.delete_asset(stale)
                log(f"retired {stale}")
    first = first or eal.load_asset(G + "/Drawings/draw_1")'''),
])

edit(R + "Scripts/art/make_tv_atlas.py", [
    ('ORDER = ["bedtime7", "t_living", "t_yard", "t_rocker"]      # the four Cheyenne signed off (2026-11-19); the first batch is retired',
     'ORDER = ["bedtime7", "t_living"]      # only what Cheyenne approved (2026-11-19 05:14 UTC); everything else is retired'),
    ('print(n, "tapes")', '''for k in range(n + 1, 9):
    for stale in (f"{ROOT}/TV/T_Tape_{k}.png", f"{ROOT}/Audio/tv_tape_{k}.wav"):
        if os.path.exists(stale):
            os.remove(stale)
            print("retired", stale)
print(n, "tapes")'''),
])
print("pass 85 applied")
