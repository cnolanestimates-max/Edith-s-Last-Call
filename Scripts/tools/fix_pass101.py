"""Pass 101: her glass eye (Cheyenne 2026-11-19 15:37 UTC).
"Maybe it's a glass eye ... we know that one of her eyes is covered up ... maybe at the very end, when he finds her dead body,
he puts her eye back ... that's the thing that releases her and lets her go in peace."

  - the jewelry box holds her glass eye (a real object) as well as Ruth's letter
  - it is the last thing he does in the root cellar: after the third knot and her "STAY!", the dark lifts, and putting the
    eye back in her face is what lets her go ("...thank you."), then dawn
  - it is wanted with the three keepsakes before the knots can be cut, so nobody reaches the end without it; and if he comes
    down without everything, the cellar door above unbolts itself so he can go back up (it used to stay locked)"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

edit(R + "Scripts/art/build_items.py", [
    ('''build("JewelBox", jewelbox)''', '''def glasseye():
    # a hand-made glass eye of the 1940s: a white shell, a pale blue painted iris, a black pupil, lying iris-up
    P = [sphere16(0.0125, (0, 0, 0.0125), "Ceramic")]
    P.append(cyl(0.0062, 0.0016, (0, 0, 0.0246), m="Glass", v=24))
    P.append(cyl(0.0026, 0.0018, (0, 0, 0.0248), m="Polymer", v=16))
    return P


def sphere16(r, loc, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=28, ring_count=14, location=loc)
    bpy.ops.object.shade_smooth()
    return done(m)


build("GlassEye", glasseye)
build("JewelBox", jewelbox)'''),
])

edit(R + "Scripts/level/build_house.py", [
    ('''note("note_box", "Letters_Scattered", 690, 268, UZ + 98.6, 60, scale=0.32, grab=(9, 9, 5), tags=["Show_jewel"])''',
     '''note("note_box", "Letters_Scattered", 690, 268, UZ + 98.6, 60, scale=0.32, grab=(9, 9, 5), tags=["Show_jewel"])
# and in the box, on the faded lining: her glass eye.  It goes back to her at the very end.
pickup("pick_keep_eye", "keep_eye", "Glass eye", ("GlassEye", CUBE, (0.025, 0.025, 0.025), {0: "Porcelain"}), 716, 284, UZ + 104.5, 0, grab=(9, 9, 7), tags=["Show_jeweleye"])'''),
    ('''interact("WCUsable", "place", None, 1400, 430, CZ + 4, 0, "Lay the keepsakes at her feet", (34, 26, 10), (0, 0, 8))''',
     '''interact("WCUsable", "place", None, 1400, 430, CZ + 4, 0, "Lay the keepsakes at her feet", (34, 26, 10), (0, 0, 8))
if ITEM("GlassEye"):
    place(ITEM("GlassEye"), 1392, 462, CZ + 1, 0, RC, tags=["Show_eyegiven"], collide=False, name="EyeGiven")'''),
])
p = R + "Scripts/level/settle.py"
s = open(p, encoding="utf-8").read()
assert "JewelBoxOpen" not in s
s += '''
# her glass eye lies on the lining of the open jewelry box, wherever the box came to rest
_jb = next((a for a in actors.get_all_level_actors() if a.get_actor_label() == "JewelBoxOpen"), None)
_je = next((a for a in actors.get_all_level_actors() if a.get_actor_label() == "Pickup_pick_keep_eye"), None)
if _jb and _je:
    _l = _jb.get_actor_location()
    _je.set_actor_location(V(_l.x, _l.y, _l.z + 6.1), False, False)
    log(f"glass eye set in the jewelry box at z {_l.z + 6.1:.1f}")
'''
open(p, "w", encoding="utf-8", newline="\n").write(s)

edit(R + "Source/WellnessCheck/WCGame.cpp", [
    ('''{ TEXT("key_box"), TEXT("Small key"),''', '''{ TEXT("keep_eye"), TEXT("Glass eye"), TEXT("Pale blue, painted by hand, older than I am. It was wrapped in a handkerchief. Hers."), TEXT("/Game/WC/Props/SM_Item_GlassEye.SM_Item_GlassEye") },
		{ TEXT("key_box"), TEXT("Small key"),'''),
])
edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('void UpstairsThump();', 'void UpstairsThump();\n\tvoid FinaleDawn();'),
])
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''ShowTagged(TEXT("Show_jewel"), Has(TEXT("box_open")));''', '''ShowTagged(TEXT("Show_jewel"), Has(TEXT("box_open")));
	ShowTagged(TEXT("Show_jeweleye"), Has(TEXT("box_open")) && !HasItem(TEXT("keep_eye")) && !Has(TEXT("eye_given")));
	ShowTagged(TEXT("Show_eyegiven"), Has(TEXT("eye_given")));'''),
    ('''if (Is(Id, TEXT("use:place")) && !Has(TEXT("placed")))
	{
		if (!(HasItem(TEXT("keep_ruth")) && HasItem(TEXT("keep_walter")) && HasItem(TEXT("keep_daniel"))))
		{
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Feedback(TEXT("Not yet.")); }
			return;
		}''', '''// the last thing: her eye goes back, and that is what lets her go
	if (Is(Id, TEXT("use:place")) && Has(TEXT("eye_wanted")) && !Has(TEXT("eye_given")))
	{
		Set(TEXT("eye_given"));
		Items.Remove(TEXT("keep_eye"));
		bBusy = true;
		P->SetInputLocked(true);
		if (AWCInteractable* Pl = Thing(TEXT("place"))) Pl->bEnabled = false;
		Play2D(TEXT("pickup"), 0.5f, EWCSnd::SFX, 0.8f);
		ApplyWorldState();
		UE_LOG(LogWCStory, Display, TEXT("WCENDING t=%.1f her eye is given back"), PlaySeconds);
		After(2.0f, [this]() { FadeTo(1.f, 2.5f); });
		const float T2 = Say(TEXT("m_end"), 3.2f);
		After(T2 + 1.5f, [this]() { FinaleDawn(); });
		return;
	}
	if (Is(Id, TEXT("use:place")) && !Has(TEXT("placed")))
	{
		if (!(HasItem(TEXT("keep_ruth")) && HasItem(TEXT("keep_walter")) && HasItem(TEXT("keep_daniel")) && HasItem(TEXT("keep_eye"))))
		{
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Feedback(TEXT("Not yet.")); }
			// he has come down without everything: the door at the top of the stairs lets go, so he can fetch it
			if (AWCDoor* Cd = Door(TEXT("cellar"))) if (Cd->bLocked) { Cd->SetLocked(false); PlayAt(TEXT("door_unlock"), Cd->GetActorLocation() + FVector(0, 0, 100), 1.f, 0.8f, 3000.f); }
			return;
		}'''),
    ('''				Tension = 0.f;
				float T2 = Say(TEXT("m_end"), 4.5f);
				After(T2 + 1.5f, [this]()
				{
					Set(TEXT("dawn"));''', '''				Tension = 0.f;
				// she is still here.  The dark lifts on the root cellar, quiet, and there is one thing left to do.
				After(3.5f, [this]()
				{
					FadeTo(0.f, 3.f);
					bBusy = false;
					if (AWCCharacter* Q = Player()) { Q->SetInputLocked(false); Q->SetLightScale(1.f); }
					Set(TEXT("eye_wanted"));
					if (AWCInteractable* Pl = Thing(TEXT("place"))) { Pl->Prompt = TEXT("Put her eye back"); Pl->bEnabled = true; }
					SetObjective(TEXT("Give her back her eye"));
					Checkpoint(TEXT("eye"));
				});
			});
		});
	}
}

/** Morning: the doors are open and the house is only a house. */
void AWCDirector::FinaleDawn()
{
	{
		{
			{
				{
					Set(TEXT("dawn"));'''),
])
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''Go(TEXT("A_Master")); Flag(TEXT("master_seen"), 10.f); Shot(TEXT("10_master")); Flag(TEXT("want_leave"), 60.f);''',
     '''Go(TEXT("A_Master")); Flag(TEXT("master_seen"), 10.f); Shot(TEXT("10_master")); Use(TEXT("jewelbox")); Flag(TEXT("box_open"), 4.f); Wait(0.8f); Shot(TEXT("10b_jewelry_box_open")); Use(TEXT("pick_keep_eye")); Flag(TEXT("want_leave"), 60.f);'''),
    ('''Use(TEXT("knot3")); Flag(TEXT("finale_done"), 8.f); Wait(2.2f); Shot(TEXT("31_S8_face"));''',
     '''Use(TEXT("knot3")); Flag(TEXT("finale_done"), 8.f); Wait(2.2f); Shot(TEXT("31_S8_face")); Flag(TEXT("eye_wanted"), 12.f); Wait(3.5f); Shot(TEXT("31b_give_her_eye_back")); Use(TEXT("place")); Flag(TEXT("eye_given"), 6.f);'''),
])
print("pass 101 applied")
