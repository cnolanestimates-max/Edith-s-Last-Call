"""Bot script for the new game flow; the bot defends itself when she stalks it; desk key pickup; pacing of stalks in fast tests."""
import io, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
import patchlib
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"

p = R + "WCAuto.cpp"
s = io.open(p, encoding="utf-8").read()
a = s.index("	// ---- arrival\n	Wait(5.f);")
b = s.index("	AutoIndex = 0;\n	AutoStepStart = Clock;\n	AutoStuckAt = Clock;")
script = r'''	auto Close = [this]() { AutoSteps.Add({ A_Use, TEXT("__close"), 0.f }); };
	const float Slow = 1.f / FMath::Max(TestPace, 0.05f) > 2.f ? 1.f : 12.f;       // real pacing needs real patience
	// ---- arrival (the drive, when it is on, ends by setting "briefed")
	Flag(TEXT("briefed"), 150.f);
	Wait(2.f); AutoSteps.Add({ A_Light, NAME_None, 0.f });
	Look(TEXT("FrontDoorPoint")); Wait(1.f); Shot(TEXT("01_arrival"));
	Go(TEXT("A_Porch")); Shot(TEXT("02_porch"));
	Use(TEXT("front")); Flag(TEXT("door_opened"), 30.f); Wait(4.f); Shot(TEXT("03_door_ajar"));
	Use(TEXT("front")); Wait(2.f);
	Go(TEXT("A_Foyer")); Flag(TEXT("inside"), 10.f); Wait(3.f); Shot(TEXT("04_foyer"));
	Use(TEXT("sw_hall")); Wait(1.6f); Shot(TEXT("04b_hall_light"));
	Flag(TEXT("locked_in"), 60.f); Wait(2.f); Use(TEXT("front")); Flag(TEXT("door_stuck"), 10.f); Wait(9.f);
	// ---- ground floor, front
	Go(TEXT("A_Living")); Use(TEXT("sw_living")); Wait(2.f); Shot(TEXT("05_living")); Use(TEXT("note_letter1")); Wait(1.f); Shot(TEXT("06_note")); Close();
	Use(TEXT("look_piano")); Wait(1.6f); Shot(TEXT("06b_look"));
	Go(TEXT("A_Dining")); Wait(2.f); Shot(TEXT("07_dining")); Use(TEXT("look_dining_table")); Wait(1.5f);
	Go(TEXT("A_Kitchen")); Use(TEXT("sw_kitchen")); Wait(2.f); Shot(TEXT("08_kitchen")); Use(TEXT("phone")); Wait(3.f);
	// ---- ground floor, rear wing
	Go(TEXT("A_Pantry")); Wait(1.5f); Shot(TEXT("08b_pantry")); Use(TEXT("fusebox")); Wait(1.5f);
	Go(TEXT("A_Den")); Use(TEXT("sw_den")); Wait(2.f); Shot(TEXT("08c_den")); Use(TEXT("pick_fuse")); Use(TEXT("desk")); Wait(1.5f); Use(TEXT("note_doctor")); Wait(1.f); Close();
	Go(TEXT("A_BathG")); Wait(1.5f); Shot(TEXT("08d_bath"));
	Go(TEXT("A_Sickroom")); Use(TEXT("sw_sickroom")); Wait(2.f); Shot(TEXT("08e_sickroom")); Use(TEXT("note_aide1")); Wait(1.f); Close(); Use(TEXT("look_sick_bed")); Wait(1.5f);
	// ---- the long quiet, then the thump
	Flag(TEXT("heard_upstairs"), 55.f * Slow); Wait(14.f);
	// ---- upstairs: S1
	Go(TEXT("A_StairsTop")); Go(TEXT("N_up_hallB")); Flag(TEXT("peek_started"), 30.f); LookHer(1.0f); Shot(TEXT("09_S1_peek")); LookHer(2.5f);
	Flag(TEXT("peek_done"), 40.f); Wait(5.f);
	Go(TEXT("A_Master")); Flag(TEXT("master_seen"), 10.f); Shot(TEXT("10_master")); Flag(TEXT("want_leave"), 60.f);
	// ---- S3: the long hall
	Go(TEXT("A_BackDoor")); Flag(TEXT("lockin_started"), 20.f);
	WaitHer(15.f); LookHer(3.5f); Shot(TEXT("11_S3_hall")); Fire(3); LookHer(4.f); Shot(TEXT("12_S3_mid")); LookHer(40.f);
	Flag(TEXT("lockin_done"), 80.f); Wait(10.f); Shot(TEXT("13_after_S3"));
	// ---- the fuse
	Go(TEXT("A_Pantry")); Use(TEXT("fusebox")); Wait(2.f); Shot(TEXT("13b_fuse"));
	// ---- S2: the phone
	Use(TEXT("back")); Flag(TEXT("phone_ringing"), 30.f * Slow); Wait(3.f);
	Use(TEXT("phone")); Flag(TEXT("phone_seat"), 40.f); LookHer(1.2f); Shot(TEXT("14_S2_table")); LookHer(6.f);
	Wait(10.f); Shot(TEXT("15_after_S2"));
	Use(TEXT("pick_key_sitting")); Use(TEXT("sitting")); Wait(3.f);
	Go(TEXT("A_Sitting")); Wait(3.f); Shot(TEXT("16_sitting")); Use(TEXT("note_diary2")); Wait(1.f); Close();
	Use(TEXT("pick_key_prayer")); Use(TEXT("pick_key_desk"));
	Use(TEXT("desk")); Flag(TEXT("desk_open"), 6.f); Wait(2.f);
	// ---- S4: the head by the ceiling
	Go(TEXT("A_StairsTop")); Flag(TEXT("ceiling_started"), 20.f * Slow); LookHer(2.5f); Shot(TEXT("17_S4_ceiling")); LookHer(7.5f); Shot(TEXT("18_S4_sprint")); LookHer(3.f);
	Flag(TEXT("ceiling_done"), 40.f); Wait(8.f);
	// ---- S7: under the bed
	Go(TEXT("A_Kids")); Wait(3.f); Shot(TEXT("19_kids")); Use(TEXT("pick_keep_ruth")); Wait(1.5f); LookHer(0.4f); Shot(TEXT("20_S7_underbed")); Wait(8.f);
	// ---- prayer room
	Use(TEXT("up_prayer")); Go(TEXT("A_Prayer")); Wait(3.f); Shot(TEXT("21_prayer")); Use(TEXT("pick_keep_walter")); Wait(3.f); Use(TEXT("note_prayer")); Wait(1.f); Close();
	// ---- upstairs rear wing: Daniel's room, the aide's room, the sewing room (S9)
	Use(TEXT("up_ell")); Go(TEXT("A_UpEll")); Wait(2.f); Shot(TEXT("21b_up_rear"));
	Go(TEXT("A_Daniel")); Use(TEXT("sw_daniel")); Wait(2.f); Shot(TEXT("21c_daniel")); Use(TEXT("pick_key_attic")); Wait(9.f);
	Go(TEXT("A_Aide")); Wait(2.f); Shot(TEXT("21d_aide"));
	Go(TEXT("A_Bath2")); Wait(2.f); Shot(TEXT("21e_bath2"));
	Go(TEXT("A_Sewing")); Wait(2.f); Shot(TEXT("21f_sewing")); Use(TEXT("pick_shears")); Flag(TEXT("sewing_done"), 6.f); Wait(3.4f); LookHer(1.4f); Shot(TEXT("21g_S9_rocker")); LookHer(4.5f); Wait(5.f);
	// ---- attic: S5
	Use(TEXT("up_attic")); Go(TEXT("A_Attic")); Wait(2.f); Shot(TEXT("22_attic")); Use(TEXT("trunk")); Flag(TEXT("attic_started"), 5.f);
	WaitHer(25.f); LookHer(1.2f); Shot(TEXT("23_S5_crawl")); LookHer(2.2f); Shot(TEXT("24_S5_rise")); Flag(TEXT("attic_done"), 30.f); Wait(8.f);
	// ---- S6: the cellar door
	Use(TEXT("cellar")); Flag(TEXT("sprint_started"), 10.f); WaitHer(12.f); LookHer(0.7f); Shot(TEXT("25_S6_sprint")); LookHer(4.f);
	Flag(TEXT("sprint_done"), 40.f); Wait(5.f); Shot(TEXT("26_cellar"));
	// ---- finale
	Go(TEXT("A_CellarShelf")); Use(TEXT("shelf")); Wait(5.f); Go(TEXT("A_Root")); Flag(TEXT("seen_body"), 10.f); Wait(6.f); Shot(TEXT("27_body"));
	Use(TEXT("place")); Flag(TEXT("placed"), 5.f); Wait(9.f); LookHer(1.f); Shot(TEXT("28_S8_far"));
	Use(TEXT("knot1")); Flag(TEXT("knot1"), 8.f); Wait(3.f); LookHer(1.f); Shot(TEXT("29_S8_mid"));
	Use(TEXT("knot2")); Flag(TEXT("knot2"), 8.f); Wait(4.5f); LookHer(1.f); Shot(TEXT("30_S8_near"));
	Use(TEXT("knot3")); Flag(TEXT("finale_done"), 8.f); Wait(2.2f); Shot(TEXT("31_S8_face"));
	Flag(TEXT("dawn"), 40.f); Wait(9.f); Shot(TEXT("32_dawn_cellar"));
	// ---- ending
	Go(TEXT("A_Foyer")); Shot(TEXT("33_dawn_foyer")); Go(TEXT("A_Porch")); Shot(TEXT("34_dawn_porch"));
	Go(TEXT("A_Cruiser")); Flag(TEXT("ended"), 20.f); Wait(30.f); Shot(TEXT("35_ending")); Wait(20.f); Shot(TEXT("36_credits"));

'''
s = s[:a] + script + s[b:]
# the bot fights back when she stalks it (and that tests the deterrent)
old = "	const FAuto& S = AutoSteps[AutoIndex];\n	const double In = Clock - AutoStepStart;"
assert old in s
s = s.replace(old, '''	if (StalkState > 0 && Her() && Her()->IsShown() && !P->IsDown() && !P->IsInputLocked())
	{
		AutoStepStart += Dt; AutoStuckAt = Clock;
		P->SetAiming(true);
		AimAt(P, Her()->HeadLocation() - FVector(0, 0, 60), Dt, 14.f);
		static double NextShot = 0.0;
		if (P->Ammo <= 0) P->DoReload();
		else if (P->IsGunUp() && Clock > NextShot && StalkState == 2) { NextShot = Clock + 0.65; P->DoFire(); }
		bAutoDefending = true;
		return;
	}
	if (bAutoDefending) { bAutoDefending = false; P->SetAiming(false); AutoPath.Reset(); }
''' + old, 1)
s = s.replace("	if (PlaySeconds > 60.f * 40.f)", "	if (PlaySeconds > 60.f * 75.f)")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

patchlib.edit(R + "WCDirector.h", [("	bool bAuto = false;", "	bool bAuto = false;\n	bool bAutoDefending = false;")])
# stalks never closer together than a minute, even in fast tests
p = R + "WCHouse.cpp"
s = io.open(p, encoding="utf-8").read()
n = s.count("* TestPace;")
s = s.replace("Rng.FRandRange(210.f, 320.f) * TestPace;", "Rng.FRandRange(210.f, 320.f) * FMath::Max(TestPace, 0.3f);").replace("Rng.FRandRange(200.f, 330.f) * TestPace;", "Rng.FRandRange(200.f, 330.f) * FMath::Max(TestPace, 0.3f);")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# the desk key lies with the prayer-room key in her sitting room
patchlib.edit(L + "build_house.py", [
    ('''pickup("pick_key_prayer", "key_prayer", "Iron key on a ribbon", CUBE, 1510, -450, GZ + 102, 70, (0.08, 0.024, 0.006), mats={0: "Iron"})''',
     '''pickup("pick_key_prayer", "key_prayer", "Iron key on a ribbon", CUBE, 1510, -450, GZ + 102, 70, (0.08, 0.024, 0.006), mats={0: "Iron"})
pickup("pick_key_desk", "key_desk", "Small desk key", CUBE, 1488, -372, GZ + 102, 20, (0.045, 0.016, 0.005), mats={0: "BrassOld"})'''),
])
print("ok")
