import io
R = "C:/GameDev/Unreal/WellnessCheck/"


def sub(f, old, new, count=1):
    s = io.open(R + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(R + f, "w", encoding="utf-8", newline="\n").write(s)


C = "Source/WellnessCheck/"
# a cold glint on her face so the eye can be found in the dark when the script wants it
sub(C + "WCEntity.cpp", "	EyeGlint->SetupAttachment(Eye);", "	EyeGlint->SetupAttachment(Body, TEXT(\"Head\"));\n	EyeGlint->SetRelativeLocation(FVector(6.f, -34.f, 14.f));\n	EyeGlint->SetLightColor(FLinearColor(0.75f, 0.85f, 1.f));")
sub(C + "WCEntity.h", "	void SetStutter(float Fps) { StutterFps = Fps; }", "	void SetStutter(float Fps) { StutterFps = Fps; }\n	/** Faint cold light on her face (lumens; 0 = off). */\n	void SetGlow(float Lumens);")
sub(C + "WCEntity.cpp", "void AWCEntity::StopMoving()", "void AWCEntity::SetGlow(float Lumens)\n{\n	EyeGlint->SetIntensity(Lumens);\n	EyeGlint->SetAttenuationRadius(90.f);\n}\n\nvoid AWCEntity::StopMoving()")
sub(C + "WCEntity.cpp", "	bFacePlayer = false;\n	StutterFps = 0.f;", "	bFacePlayer = false;\n	StutterFps = 0.f;\n	EyeGlint->SetIntensity(0.f);")
# S4: enough light to make out a head near the ceiling at the far end, no more
sub(C + "WCStory.cpp", '''	H->Appear(Pos(TEXT("Her_UpFar")), YawOf(TEXT("Her_UpFar")), TEXT("Tall"));
	P->SetLightScale(0.16f);''', '''	H->Appear(Pos(TEXT("Her_UpFar")), YawOf(TEXT("Her_UpFar")), TEXT("Tall"));
	H->SetGlow(1.6f);
	P->SetLightScale(0.3f);''')
sub(C + "WCStory.cpp", '''	if (AWCDoor* D = Door(TEXT("up_master"))) D->SetOpen(true, 0.01f, true);
	H->Appear(Pos(TEXT("Her_Peek")), YawOf(TEXT("Her_Peek")), TEXT("Peek"));''', '''	if (AWCDoor* D = Door(TEXT("up_master"))) D->SetOpen(true, 0.01f, true);
	H->Appear(Pos(TEXT("Her_Peek")), YawOf(TEXT("Her_Peek")), TEXT("Peek"));
	H->SetGlow(0.8f);''')
# level: phone away from the kitchen door's swing
L = "Scripts/level/"
sub(L + "build_house.py", 'place("Table_Side_Round", 860, 250, GZ, 0, K)\ninteract("WCUsable", "phone", "Telephone_Rotary", 860, 250, GZ + 98, 200, "Pick up the phone", (16, 16, 12))\npoint("PhonePoint", 860, 250, GZ + 110)',
    'place("Table_Side_Round", 868, 536, GZ, 0, K)\ninteract("WCUsable", "phone", "Telephone_Rotary", 868, 536, GZ + 98, 20, "Pick up the phone", (18, 18, 14))\npoint("PhonePoint", 868, 536, GZ + 110)')
sub(L + "import_assets.py", '    tint = vparam(m, "Tint", (0.82, 0.84, 0.86, 1), -700, -420)', '    tint = vparam(m, "Tint", (0.46, 0.47, 0.5, 1), -700, -420)')
sub(L + "import_assets.py", '    sp = const1(m, 0.35, -400, 180)', '    sp = const1(m, 0.22, -400, 180)')
sub(L + "import_more.py", 'mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(0.42, 0.36, 0.27, 1))', 'mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(0.2, 0.17, 0.13, 1))')
print("ok")
