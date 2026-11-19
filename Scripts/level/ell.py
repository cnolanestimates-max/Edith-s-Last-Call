# The rear wing: eight more rooms, each with its own story, plus what the longer game needs (desk, fuse box, shears,
# cartridges).  exec'd by build_house.py after decay.py (shares its helpers).
#
# Layout rule (Cheyenne): fill the rooms, but leave room to walk.  Furniture goes against the walls; the middle of
# every room and a straight line from each door stay clear.
E = "Dressing/"
_world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
_drop = {"hit": 0, "miss": 0}


def surface_z(x, y, z_from, reach=140.0, ignore=()):
    """Height of whatever is under (x, y) looking down from z_from (None if nothing within reach)."""
    try:
        hit = unreal.SystemLibrary.line_trace_single(_world, V(x, y, z_from), V(x, y, z_from - reach), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True,
                                                     list(ignore), unreal.DrawDebugTrace.NONE, True)
        if hit:
            t = hit.to_tuple()
            if t[0]:
                _drop["hit"] += 1
                return t[5].z
    except Exception as exc:
        if _drop["miss"] == 0:
            log(f"surface trace unavailable: {exc}")
    _drop["miss"] += 1
    return None


def put(mesh, x, y, zhint, yaw=0.0, folder="Props", lift=0.3, **kw):
    """Place a small thing ON whatever is there: zhint is where we think the surface is; a trace corrects it."""
    z = surface_z(x, y, zhint + 45.0, 110.0)
    kw.setdefault("collide", False)
    return place(mesh, x, y, (z if z is not None else zhint) + lift, yaw, folder, **kw)


def put_note(wid, mesh, x, y, zhint, yaw=0.0, **kw):
    z = surface_z(x, y, zhint + 45.0, 110.0)
    return note(wid, mesh, x, y, (z if z is not None else zhint) + 0.4, yaw, **kw)


def put_pickup(wid, item, display, mesh, x, y, zhint, yaw=0.0, scale=1.0, **kw):
    z = surface_z(x, y, zhint + 45.0, 110.0)
    return pickup(wid, item, display, mesh, x, y, (z if z is not None else zhint) + 0.6, yaw, scale, **kw)


def ammo(wid, x, y, zhint, yaw=0.0, **kw):
    """A box of cartridges: small cardboard box with a brass-coloured end."""
    real = ITEM("AmmoBox")
    a = put_pickup("pick_" + wid, wid, "Box of cartridges", ("AmmoBox", CUBE, (0.11, 0.07, 0.055), {0: surf("Cardboard", "MI_Cardboard")}), x, y,
                   zhint + (0.0 if real else 3.0), yaw, grab=(12, 12, 9), **kw)
    return a


TOILET = asset(G + "/Props/SM_Toilet", must=False)
RADIO = asset("/Game/Fab/Vintage_Radio/SM_VintageRadio_LOD0", must=False)

# ================================================================== GROUND: rear hall
RH_ = E + "RearHall"
place("Rug_Persian_Worn", 2200, 0, GZ, 90, RH_, collide=False)
place("Coat_Rack", 2730, -150, GZ, 0, RH_)
place(TABLE, 2420, 150, GZ, 0, RH_)
put("Oil_Lamp_Broken_Unlit", 2420, 150, GZ + 98, 0, RH_)
place("Wheelchair_Tipped", 2520, -110, GZ, 40, RH_, tags=["HallWheelchair"])
place("Portrait_Large", 2000, -181, GZ + 130, 0, RH_, collide=False)
place("Portrait_Oval", 2360, 181, GZ + 150, 180, RH_, collide=False)
place("Portrait_Small", 2250, -181, GZ + 160, 0, RH_, collide=False)
place("Picture_Frame_Fallen", 1900, 150, GZ, 70, RH_, collide=False)
place("Radiator_Cast_Iron", 2000, 172, GZ, 180, RH_)
place("Umbrella_Stand_Umbrellas", 2740, 150, GZ, 0, RH_)
place("Cobweb_Doorway", 1620, 0, GZ + 240, 90, RH_, collide=False)

# ================================================================== GROUND: Walter's den
DN = E + "Den"
place("Rug_Persian_Worn", 2000, -400, GZ, 0, DN, collide=False)
place("Fireplace_Marble", 2200, -562, GZ, 0, DN)
place("Fireplace_Tools", 2300, -560, GZ, 0, DN, collide=False)
place("Portrait_Large", 2200, -581, GZ + 185, 0, DN, collide=False, name="Portrait_Walter")
interact("WCUsable", "desk", ow("Desk_01a", "Desk_Writing"), 2340, -330, GZ, 270 + OW_YAW, "Open the desk", (44, 86, 66), (0, 0, 66))
place("Chair_Dining_HighBack", 2205, -425, GZ, 55, DN)          # pushed back from the desk and aside: he has to be able to stand at it
# what is in the desk, seen once it is open: Walter's key ring and a box of his cartridges (they used to go straight into the inventory)
put_pickup("pick_key_ell", "key_ell", "Walter's keys", ("Keyring", CUBE, (0.06, 0.05, 0.006), {0: "Iron"}), 2312, -352, GZ + 78, 25, grab=(11, 11, 7), tags=["Show_desk"])
ammo("ammo_desk", 2314, -306, GZ + 78, 70, tags=["Show_deskammo"])


def sight_report(what, tx, ty, tz):
    """From where can a standing man see this?  (eye 156 cm; a line trace against everything that blocks sight)"""
    out = []
    for (ex, ey) in ((2190, -352), (2225, -352), (2250, -352), (2225, -300), (2250, -300), (2225, -400), (2250, -290), (2270, -330)):
        try:
            hit = unreal.SystemLibrary.line_trace_single(_world, V(ex, ey, GZ + 156), V(tx, ty, tz + 1.0), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [],
                                                         unreal.DrawDebugTrace.NONE, True)
            t = hit.to_tuple() if hit else None
            if t and t[0]:
                gap = ((t[4].x - tx) ** 2 + (t[4].y - ty) ** 2 + (t[4].z - tz) ** 2) ** 0.5
                who = t[9].get_actor_label() if t[9] else "?"
                out.append(f"({ex},{ey}): {'SEEN' if (gap < 22 or who.startswith('Pickup_')) else 'blocked by ' + who + ' ' + str(int(gap)) + ' cm short'}")
            else:
                out.append(f"({ex},{ey}): nothing hit")
        except Exception as exc:
            out.append(f"trace failed: {str(exc)[:80]}")
            break
    log(f"sight {what} at ({tx:.0f},{ty:.0f},{tz:.0f}): " + "; ".join(out))


for _a in actors.get_all_level_actors():
    if _a.get_actor_label() in ("Pickup_pick_key_ell", "Pickup_pick_ammo_desk"):
        _l = _a.get_actor_location()
        sight_report(_a.get_actor_label(), _l.x, _l.y, _l.z)
put("Typewriter_Old", 2318, -310, GZ + 78, 250, DN)
put("Desk_Lamp_Green", 2318, -385, GZ + 78, 200, DN)
put("Book_Stack_Old", 2318, -262, GZ + 78, 30, DN)
place("Bookshelf_Tall", 1642, -330, GZ, 90, DN)
place("Bookshelf_Tall", 1642, -470, GZ, 90, DN)
place("Sofa_Chesterfield", 2030, -252, GZ, 180, DN)
place("Armchair_Wingback", 2010, -500, GZ, 20, DN)
place("Ottoman_Footstool", 2090, -440, GZ, 0, DN)
place(TABLE, 1900, -545, GZ, 0, DN)
if RADIO:
    put(RADIO, 1900, -545, GZ + 98, 100, DN, name="DenRadio", scale=1.35)
else:
    put("Radio_Old_Cathedral", 1900, -545, GZ + 98, 100, DN, name="DenRadio")
point("RadioPoint", 1900, -545, GZ + 120)
place(ow("Cabinet_02a", "Cabinet_Instruments_Glass"), 2356, -520, GZ, 270 + OW_YAW, DN, name="GunCabinet")
place("Filing_Cabinet_4", 2352, -240, GZ, 270, DN)
place("Portrait_Small", 1990, -581, GZ + 170, 0, DN, collide=False)
place("Portrait_Small", 1634, -260, GZ + 170, 90, DN, collide=False)
place("Curtains_Torn_Window", 1800, -578, GZ + 20, 0, DN, collide=False)
place("Book_Pile_Fallen", 1720, -400, GZ, 40, DN, collide=False)
place("Clock_Grandfather_Broken", 1650, -245, GZ, 90, DN)
put_note("note_doctor", "Letters_Scattered", 1885, -520, GZ + 98, 30, scale=0.7)
# (the spare fuse is in her sitting room now: build_house.py)

ammo("ammo_den", 2300, -545, GZ + 0, 20)

# ================================================================== GROUND: the downstairs bath
BG = E + "BathG"
fab("Urban_Ruin_Bathtub_Tiled_Derelict", 2690, -400, GZ, 90, "BathG") or fab("Urban_Australian_Desolation_Bathtub_Metal_Rusty", 2700, -400, GZ, 90, "BathG", scale=1.15)
fab("Urban_Australian_Desolation_Sink_Mixed_Weathered", 2450, -330, GZ, 90, "BathG")
if TOILET:
    place(TOILET, 2470, -545, GZ, float(os.environ.get("WC_TOILET_YAW", "90")), BG, name="ToiletG")
place("Mirror_Wall_Ornate_Cracked", 2423, -330, GZ + 150, 90, BG, collide=False)
place("Medicine_Cabinet_Wall_Broken", 2423, -450, GZ + 140, 90, BG, collide=False)
place("Wheelchair_Rusted_NoFootrest", 2560, -500, GZ, 300, BG)
place("Bucket_Rusty", 2740, -250, GZ, 0, BG)
fab("Urban_Shanty_Town_Rag_Fabric_Worn", 2600, -420, GZ + 1, 60, "BathG", collide=False, roll=90)
point("Flies_bathg", 2470, -530, GZ + 70, tags=["Flies"])
for (n, x, y, face, sz) in (("filth_03", 2700, -584, "y+", 260), ("mold_03", 2500, -584, "y+", 280), ("rust_01", 2784, -400, "x-", 220), ("filth_02", 2416, -520, "x+", 220)):
    wall_decal(n, x, y, GZ + 150, face, sz)
for (x, y, n) in ((2600, -330, "puddle_01"), (2500, -480, "filth_01"), (2700, -520, "puddle_02")):
    floor_decal(n, x, y, GZ + 1, 200)

# ================================================================== GROUND: pantry (and the fuse box)
PN = E + "Pantry"
place("Specimen_Jar_Shelf", 1930, 565, GZ, 180, PN)
place("Cabinet_Steel_Tall", 1958, 290, GZ, 270, PN)
place("Barrel_Old", 1660, 545, GZ, 0, PN)
place("Crate_Wood_Open", 1910, 250, GZ, 20, PN)
place("Crate_Wood_Small", 1840, 250, GZ, 70, PN)
place("Broom_Leaning", 1630, 240, GZ, 30, PN, collide=False)
place("Box_Cardboard_Stack", 1680, 250, GZ, 10, PN)
place("Tin_Cans_Rusty", 1760, 560, GZ, 0, PN, collide=False)
place("Bottles_Empty_Group", 1700, 480, GZ, 0, PN, collide=False)
place("Rat_Group", 1850, 520, GZ, 100, PN, collide=False)
place("Jar_Herbs_Shelf", 1625, 520, GZ + 130, 90, PN, collide=False)
place("Hook_Rack_Wall", 1700, 222, GZ + 160, 0, PN, collide=False)
point("Flies_pantry", 1880, 520, GZ + 90, tags=["Flies"])
floor_decal("filth_01", 1800, 440, GZ + 1.5, 240)
# the fuse box: grey steel on the wall, door hanging open, one porcelain fuse black
box("FuseBoxBack", 1975, 1984, 400, 446, GZ + 118, GZ + 176, surf("Rust", "MI_Iron"), PN, collide=False)
box("FuseBoxDoor", 1950, 1976, 446, 449, GZ + 118, GZ + 176, surf("Rust", "MI_Rust"), PN, collide=False, yaw=-25)
for i in range(4):
    place(CYL, 1972, 408 + i * 10, GZ + 160, 0, PN, name=f"Fuse_{i}", scale=(0.028, 0.028, 0.05), mats={0: "Porcelain" if i != 2 else "WC:M_Black"}, collide=False, pitch=90)
interact("WCUsable", "fusebox", None, 1966, 423, GZ + 147, 0, "Fuse box", (16, 26, 32), (0, 0, 0))
point("FusePoint", 1966, 423, GZ + 147)

# ================================================================== GROUND: the sickroom (where she slept at the end)
SK_ = E + "Sickroom"
place("Rug_Persian_Worn", 2400, 380, GZ, 0, SK_, collide=False, scale=0.8)
place("Bed_Hospital_Restraints", 2480, 505, GZ, 180, SK_, name="SickBed")
place("IV_Stand", 2600, 520, GZ, 0, SK_)
place(TABLE, 2350, 540, GZ, 0, SK_)
put("Pill_Bottle_Set", 2350, 540, GZ + 98, 0, SK_)
place("Wheelchair_Old", 2240, 420, GZ, 215, SK_)
place("Armchair_Wingback_Torn", 2080, 520, GZ, 300, SK_)
place(ow("Sink_01a", "Dresser_Drawers"), 2748, 300, GZ, 270 + OW_YAW, SK_, name="Washstand")
put("Porcelain_Doll_Cracked", 2752, 250, GZ + 92, 250, SK_)
place("Cabinet_Medicine_Glass_Open", 2752, 420, GZ, 270, SK_)
place("Scale_Doctor", 2745, 540, GZ, 250, SK_)
place("Privacy_Screen_Torn", 2060, 300, GZ, 60, SK_)
place("Bucket_Rusty", 2420, 430, GZ, 0, SK_)
place("Curtains_Torn_Window", 2600, 578, GZ + 20, 180, SK_, collide=False)
place("Mirror_Covered_Sheet", 2700, 240, GZ, 200, SK_)
fab("Urban_Shanty_Town_Blanket_Fabric_Worn", 2560, 400, GZ + 2, 20, "Sickroom", collide=False, pitch=-90)
point("Flies_sick", 2480, 500, GZ + 90, tags=["Flies"])
wall_decal("scratches", 2480, 584, GZ + 120, "y-", 130)
wall_decal("scratches", 2143, 216, GZ + 110, "y+", 110)
put_note("note_aide1", "Clipboard_Chart", 2335, 520, GZ + 98, 30)
put_note("note_rem6", "Newspaper_Single", 2024, 420, GZ + 150, 0, scale=0.5, roll=90, grab=(6, 20, 22))

# ================================================================== UPSTAIRS: rear hall
UR = E + "UpperRear"
place("Rug_Persian_Worn", 2200, 0, UZ, 90, UR, collide=False)
place(TABLE, 2730, 140, UZ, 0, UR)
put("Candle_Melted_Puddle", 2730, 140, UZ + 98, 0, UR)
place("Tricycle_Rusty", 2300, -110, UZ, 30, UR, tags=["Tricycle"])
place("Chair_Dining_Broken", 2650, -130, UZ, 200, UR)
place("Portrait_Large", 2200, 181, UZ + 130, 180, UR, collide=False)
place("Portrait_Glowing_Eyes", 2000, -181, UZ + 140, 0, UR, collide=False)
place("Portrait_Slashed", 2400, -181, UZ + 140, 0, UR, collide=False)
place("Cobweb_Doorway", 1622, 0, UZ + 240, 90, UR, collide=False)
place("Plant_Stand_Dead_Fern", 2740, -140, UZ, 0, UR)

# ================================================================== UPSTAIRS: Daniel's room, kept exactly as it was
DR = E + "Daniel"
place("Rug_Persian_Worn", 2000, -400, UZ, 0, DR, collide=False, scale=0.9)
place(ow("Bed_02g", "Bed_FourPoster"), 2240, -470, UZ, 180 + OW_YAW, DR, name="DanielBed")
place("Chest_Trunk", 2080, -450, UZ, 0, DR)
place(ow("Desk_01a", "Desk_Writing"), 1660, -400, UZ, 90 + OW_YAW, DR, name="DanielDesk")
place("Chair_Dining_HighBack", 1725, -400, UZ, 270, DR)
put("Portrait_Small", 1682, -350, UZ + 78, 90, DR, name="DanielPhoto", pitch=-70)
put("Toy_Train_Wind_Up", 1682, -455, UZ + 78, 60, DR)
put("Book_Closed_Leather", 1684, -395, UZ + 78, 20, DR)
place("Bookshelf_Tall", 1980, -565, UZ, 0, DR)
place("Wardrobe_Tall", 2350, -262, UZ, 270, DR)
place("Suitcase_Old", 2300, -540, UZ, 20, DR)
place("Rocking_Horse", 1700, -540, UZ, 40, DR)
place(TABLE, 2340, -400, UZ, 0, DR)
if RADIO:
    put(RADIO, 2340, -400, UZ + 98, 200, DR, name="DanielRadio", scale=1.35)
else:
    put("Radio_Old_Cathedral", 2340, -400, UZ + 98, 200, DR, name="DanielRadio")
point("DanielRadioPoint", 2340, -400, UZ + 120)
place("Curtains_Torn_Window", 1800, -578, UZ + 20, 0, DR, collide=False)
place("Bunting_Banner", 2000, -578, UZ + 250, 0, DR, collide=False)
put_note("note_daniel", "Letters_Scattered", 1686, -425, UZ + 78, 100, scale=0.7)
put_pickup("pick_key_attic", "key_attic", "Long key", ("KeyLong", CUBE, (0.075, 0.022, 0.006), {0: "BrassOld"}), 1686, -372, UZ + 78, 110)
ammo("ammo_daniel", 2085, -450, UZ + 62, 70)

# ================================================================== UPSTAIRS: the sewing room that was going to be a nursery
SW = E + "Sewing"
place("Cradle_Rocking", 2700, -540, UZ, 0, SW)
place("Rocking_Chair", 2720, -300, UZ, 215, SW, tags=["SewRocker"])
point("Her_Sewing", 2720, -300, UZ, 215)
place(ow("Work_Table_01a", "Desk_Writing"), 2446, -470, UZ, 90 + OW_YAW, SW, name="SewingTable")
place("Chair_Dining_HighBack", 2530, -335, UZ, 205, SW)
place("Wardrobe_Open_Clothes", 2560, -560, UZ, 0, SW)
place("Hatbox_Round", 2440, -250, UZ, 0, SW, collide=False)
place("Box_Cardboard_Open", 2470, -300, UZ, 30, SW)
put("Hatbox_Round", 2445, -525, UZ + 74, 0, SW)
# the family, in rags: three with names stitched on, and one that is too tall
for i, (m, s) in enumerate((("Rag_Doll_Sitting", 1.0), ("Rag_Doll_Sitting", 0.8), ("Rag_Doll_Sitting", 0.92), ("Effigy_Twig_Standing", 0.5))):
    put(m, 2440, -450 + i * 22, UZ + 74, 90, SW, name=f"FamilyDoll_{i}", scale=s)
put_pickup("pick_shears", "shears", "Sewing shears", ("Shears", CUBE, (0.21, 0.035, 0.008), {0: "Iron"}), 2456, -492, UZ + 74, 35, grab=(14, 14, 9))
if not ITEM("Shears"):
    put(CUBE, 2456, -492, UZ + 74.6, 62, SW, name="ShearsBlade2", scale=(0.21, 0.03, 0.007), mats={0: "Iron"}, tags=["Hide_shears"])
place("Curtains_Torn_Window", 2600, -578, UZ + 20, 0, SW, collide=False)
place("Teddy_Bear_Old", 2700, -520, UZ + 40, 30, SW, collide=False)
place("Rug_Persian_Worn", 2600, -400, UZ, 90, SW, collide=False, scale=0.7)
put_note("note_baby", "Letters_Scattered", 2690, -470, UZ + 2, 60, scale=0.6)

# ================================================================== UPSTAIRS: the aide's room (she left in a hurry)
AD = E + "Aide"
place(ow("Bed_02c", "Bed_Hospital_Bare_Springs"), 2200, 470, UZ, 0 + OW_YAW, AD, name="AideBed")
place("Suitcase_Old", 2060, 400, UZ, 250, AD)
place("Wardrobe_Open_Clothes", 2350, 300, UZ, 270, AD)
place(TABLE, 2040, 545, UZ, 0, AD)
put("Candle_In_Bottle", 2040, 545, UZ + 98, 0, AD)
place("Chair_Dining_Broken", 1905, 268, UZ, 110, AD, name="ChairUnderKnob")
place("Mirror_Standing_Cheval", 1650, 540, UZ, 130, AD)
place("Cross_Wood_Simple", 2200, 581, UZ + 190, 180, AD, collide=False, scale=0.22)
place(ow("Dresser_01a", "Dresser_Drawers_Open"), 1646, 380, UZ, 90 + OW_YAW, AD, name="AideDresser")
place("Curtains_Torn_Window", 1800, 578, UZ + 20, 180, AD, collide=False)
place("Rug_Persian_Worn", 2000, 400, UZ, 0, AD, collide=False, scale=0.8)
fab("Urban_Shanty_Town_Dress_Fabric_Worn", 2100, 330, UZ + 2, 70, "Aide", collide=False, roll=90)
put_note("note_aide2", "Book_Open_Pages", 2035, 525, UZ + 98, 20)
# the second tape: on the aide's stripped bed (behind Walter's keys, so about the middle of the night)
put_pickup("pick_tape2", "tape2", "VHS tape", ("Tape2", CUBE, (0.187, 0.103, 0.025), {0: "BrassOld"}), 2185, 430, UZ + 55, 70, grab=(13, 10, 6))
put_note("note_aide3", "Letters_Scattered", 1650, 380, UZ + 119, 60, scale=0.6)

# ================================================================== UPSTAIRS: second bath (the floor has gone through into the sickroom)
B2 = E + "Bath2"
_tub2 = fab("Urban_Australian_Desolation_Bathtub_Metal_Rusty", 2700, 300, UZ, 90, "Bath2", scale=1.15)
TUB2 = None
if _tub2:
    _to, _te = _tub2.get_actor_bounds(False)
    if _te.x > _te.y:                      # it must lie along the east wall, not across the doorway
        _tub2.set_actor_rotation(R(0.0), False)
        _to, _te = _tub2.get_actor_bounds(False)
        if abs(_to.x - 2700) > 2 or abs(_to.y - 300) > 2:
            _tub2.set_actor_location(V(2700 - (_to.x - 2700), 300 - (_to.y - 300), UZ), False, False)
            _to, _te = _tub2.get_actor_bounds(False)
    TUB2 = (_to.x, _to.y, _te.x, _te.y)
    log(f"Tub2 centre ({_to.x:.0f},{_to.y:.0f}) half ({_te.x:.0f},{_te.y:.0f},{_te.z:.0f})")
place("Sink_Hospital", 2738, 572, UZ, 180, B2)
if TOILET:
    place(TOILET, 2470, 550, UZ, float(os.environ.get("WC_TOILET_YAW", "90")) + 180, B2, name="Toilet2")
place("Mirror_Wall_Oval", 2738, 582, UZ + 150, 180, B2, collide=False)
place("Medicine_Cabinet_Wall_Open", 2462, 582, UZ + 150, 180, B2, collide=False)
place("Laundry_Cart", 2596, 540, UZ, 8, B2)
if TUB2:
    box("TubWater", TUB2[0] - TUB2[2] * 0.74, TUB2[0] + TUB2[2] * 0.74, TUB2[1] - TUB2[3] * 0.80, TUB2[1] + TUB2[3] * 0.80, UZ + 44, UZ + 45.5, "WC:M_Black", B2, collide=False, shadow=False)
point("Flies_bath2", 2700, 300, UZ + 80, tags=["Flies"])
for (n, x, y, face, sz) in (("filth_03", 2784, 300, "x-", 280), ("mold_03", 2600, 584, "y-", 300), ("rust_01", 2500, 584, "y-", 200), ("mold_01", 2416, 400, "x+", 260)):
    wall_decal(n, x, y, UZ + 150, face, sz)
for (x, y, n) in ((2620, 300, "puddle_01"), (2540, 520, "filth_01"), (2700, 480, "puddle_02")):
    floor_decal(n, x, y, UZ + 1, 200)

# ================================================================== more cartridges where a careful search finds them
ammo("ammo_attic", 1010, -470, AZ + 60, 30)
ammo("ammo_cellar", 950, 150, CZ + 81, 80)
ammo("ammo_kitchen", 905, 555, GZ + 95, 10)
log(f"rear wing done (surface traces: {_drop})")
