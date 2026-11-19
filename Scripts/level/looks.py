# Things to examine.  Press E and a line of what the deputy notices comes up on screen (no voice).
# exec'd by build_house.py.  Each: (id, x, y, z, text, grab half-extent).  The box you aim at sits at (x, y, z).
LOOKS = [
    # ---- outside
    ("porch_boxes", -125, -165, 30, "Hartley's Market. Three delivery boxes. The milk in the bottom one has gone to something solid.", (40, 40, 30)),
    ("porch_papers", -110, 130, 14, "Newspapers still in their bands. The oldest is fourteen months back.", (34, 34, 16)),
    ("porch_rocker", -200, 470, 55, "The seat is worn pale. This was her chair. It is the only thing on the porch without dust on it.", (34, 34, 50)),
    ("grave_walter", -560, 960, 30, "WALTER J. HARROW. 1921 - 1989. The flowers in the jar are dead, but they are not fourteen months dead.", (40, 40, 55)),
    ("grave_daniel", -700, 990, 25, "PVT. DANIEL W. HARROW. 1949 - 1969. No grave in front of it. They never got him back to bury.", (40, 40, 50)),
    ("clothesline", -1060, 505, 120, "A sheet and a nightgown, grey with rain. Hung out to dry a year ago and never brought in.", (130, 20, 50)),
    ("well", -1500, -620, 40, "Boarded over. The boards are newer than the well.", (60, 60, 60)),
    ("bulkhead", 1000, 715, 10, "Cellar doors, chained from outside. So nobody went in that way. Or came out.", (110, 50, 40)),
    # ---- front hall
    ("coat_rack", 60, 150, 140, "A man's coat, a child's coat, an army jacket. All hung up as if they were only out for the afternoon.", (26, 26, 60)),
    ("hall_clock", 1100, -168, 150, "Stopped at ten past three. The weights are on the floor of the case, cut loose.", (28, 28, 100)),
    ("hall_portrait", 1250, -181, 150, "Somebody took a knife to the canvas. Careful about it. Only the faces.", (40, 12, 50)),
    ("stairs_marks", 420, 60, 60, "Gouges in the newel post, up high. Higher than I can reach.", (22, 22, 60)),
    # ---- living room
    ("piano", 90, -420, 90, "The lid's down and there's dust on it, except on the keys. Somebody still plays.", (36, 70, 50)),
    ("mantel_photos", 600, -548, 150, "Every face scratched out of every frame. Every one but hers.", (60, 16, 26)),
    ("living_rocker", 690, -500, 60, "A shawl over the arm, still folded. It is rocking. No. It just stopped.", (32, 32, 55)),
    ("living_shelf", 60, -540, 110, "Scrapbooks. Ruth's school reports, Danny's ribbons. The last page of each one is torn out.", (26, 60, 90)),
    # ---- dining room
    ("dining_table", 420, 400, 95, "Four places laid. The food went to mould months ago, but the napkins have been refolded.", (110, 60, 22)),
    ("dining_chandelier", 600, 300, 30, "It came down on the table end. Nobody moved it. She just kept setting places around it.", (60, 60, 34)),
    ("dining_clock", 60, 560, 140, "This one stopped at ten past three as well.", (26, 26, 90)),
    # ---- kitchen and pantry
    ("stove", 1180, 545, 95, "Every knob taped down in the off position. Then the tape's been picked at.", (50, 32, 30)),
    ("fridge", 1545, 520, 100, "Don't. ...I did. Don't.", (40, 44, 80)),
    ("kitchen_sink", 1050, 560, 95, "Dishes for four, stacked dirty. One plate has been licked clean.", (44, 30, 24)),
    ("pantry_shelves", 1930, 550, 110, "Preserves, labelled by year. The newest ones are not fruit.", (60, 22, 90)),
    # ---- her sitting room
    ("drawings", 824, -410, 160, "Crayon, like a child's. A small woman and a tall black shape, holding hands. MY FREND. She was eighty-six.", (10, 160, 80)),
    
    ("sitting_wardrobe", 1300, -560, 120, "The mirror is cracked from the inside of the glass, if that is a thing that can happen.", (50, 26, 100)),
    # ---- den, bath, sickroom
    ("gun_cabinet", 2352, -530, 110, "Rack for a shotgun. No shotgun. One box of cartridges left on the shelf.", (26, 46, 90)),
    ("den_portrait", 2200, -575, 200, "Walter Harrow. He is the only one in this house she did not scratch out. She turned him to face the wall instead, and somebody has turned him back.", (50, 12, 50)),
    ("den_typewriter", 2330, -310, 115, "One line, typed over and over until the ribbon gave out: i will not be put in a home i will not be put in a home", (22, 22, 18)),
    ("den_books", 1642, -400, 120, "County histories. One spine is cleaner than the rest. 'Customs of the First Settlers.' The chapter on winter is cut out with a razor.", (22, 110, 100)),
    ("bathg_mirror", 2423, -330, 150, "Soap on the glass. A line drawn across at the height of my chin, and a date. Then another, higher. Then another.", (10, 30, 40)),
    ("bathg_tub", 2690, -400, 50, "A ring of grey hair around the drain, long as my arm.", (44, 80, 34)),
    ("sick_bed", 2480, 505, 70, "Leather cuffs on the rails. The buckles are open. The leather is not torn. It is stretched.", (50, 100, 40)),
    ("sick_wheelchair", 2240, 420, 60, "County property tag on the frame. They never came back for it.", (34, 34, 50)),
    ("sick_door_marks", 2200, 216, 150, "Pencil marks up the door frame. 'E.H. March.' Then April, a hand higher. The last mark is above the lintel.", (56, 10, 90)),
    ("hall_wheelchair", 2520, -110, 50, "On its side. One wheel is still turning.", (40, 40, 44)),
    # ---- upstairs front
    ("master_bed", 560, 440, UZ + 80, "One side slept in. The other side has his pyjamas laid out on the pillow.", (100, 80, 40)),
    ("vanity", 420, 560, UZ + 110, "She smashed the mirror. Then she swept up the glass and put the pieces in the drawer, in order.", (60, 22, 60)),
    ("master_wardrobe", 60, 500, UZ + 120, "Her dresses, let out at the seams. Then let out again. Then cut open down the back.", (24, 50, 100)),
    ("kids_dollhouse", 730, -290, UZ + 70, "It's this house. Somebody has put a doll in the cellar and shut the little door on it.", (34, 34, 50)),
    ("kids_cradle", 80, -300, UZ + 50, "Still made up. The blanket has been tucked in very recently.", (30, 40, 36)),
    ("upbath_tub", 1000, -520, UZ + 50, "Black water to the brim. Something long and grey just under the surface. Hair. Only hair. I'm not putting my hand in to check.", (80, 44, 36)),
    # ---- upstairs rear
    ("tricycle", 2300, -110, UZ + 40, "Ruth's, I'd guess. No dust on the seat.", (30, 30, 34)),
    ("daniel_bed", 2230, -450, UZ + 80, "Made up tight, army corners. Dusted. In a house like this. She kept one room for him and let the rest go.", (100, 80, 40)),
    ("daniel_photo", 1640, -350, UZ + 118, "A boy in a uniform that doesn't fit yet, squinting at the sun. The glass is clean.", (16, 16, 16)),
    ("family_dolls", 2445, -412, UZ + 122, "Four rag dolls. WALTER. RUTH. DANNY, stitched across their chests. The fourth one has no name. It is taller than the others and it has one eye.", (16, 50, 24)),
    ("sewing_cradle", 2700, -540, UZ + 45, "Empty. It always was.", (30, 40, 36)),
    ("aide_chair", 1905, 268, UZ + 40, "A chair, split along the top rail where it was jammed under the doorknob. From the inside. She slept like that.", (30, 30, 40)),
    ("aide_suitcase", 2060, 400, UZ + 30, "Half packed and left behind. She didn't stop to close it.", (34, 34, 26)),
    ("bath2_tub", 2700, 300, UZ + 55, "Full. The water isn't moving. My light won't go down into it.", (44, 80, 34)),
    ("bath2_hole", 2540, 390, UZ + 30, "Floor's gone through to the sickroom. Rotted from the top. Something stood in this spot for a long time.", (70, 70, 40)),
    # ---- attic and cellar
    ("attic_easel", 1000, 420, AZ + 120, "A family portrait under a sheet. Four people. Five, now. Someone has painted a tall grey shape in behind them, in house paint.", (40, 40, 80)),
    ("attic_wardrobe", 780, 560, AZ + 110, "Christmas boxes. Every tag says 'To Danny' or 'To Ruth.' Forty years of them. None opened.", (60, 30, 100)),
    ("furnace", 600, -500, CZ + 70, "Cold. There's bedding in front of it. She was sleeping down here, as close to the ground as she could get.", (44, 44, 60)),
    ("cellar_jars", 700, 185, CZ + 120, "More preserves. And hair. Jars of grey hair, each one labelled with a name.", (60, 22, 90)),
]
_z = {"hit": 0}
for (lid, x, y, z, text, grab) in LOOKS:
    a = actors.spawn_actor_from_class(WC["WCLook"], V(x, y, z), R())
    a.set_actor_label("Look_" + lid)
    a.set_editor_property("wc_id", unreal.Name("look_" + lid))
    a.set_editor_property("prompt", "Look")
    a.set_editor_property("text", text)
    a.set_editor_property("grab_extent", V(*grab))
    a.set_editor_property("grab_offset", V(0, 0, 0))
    a.set_folder_path("House/Looks")
    count["game"] += 1
# the gouges on the newel post need something to look at
wall_decal("scratches", 408, 60, GZ + 230, "x+", 90)
log(f"looks: {len(LOOKS)}")
