# Waypoint graph for the automatic play-through (the bot walks node to node with real movement input).
# exec'd by build_house.py.  Nodes are TargetPoints tagged NavNode, N_<name>, E_<neighbour>...
NODES = {
    # yard / ground floor
    "yard": (-1440, 120, -40), "path": (-700, 0, -40), "porch": (-200, 0, GZ), "door_front": (-40, 0, GZ), "foyer": (120, 0, GZ),
    "hallA": (300, 100, GZ), "hallB": (600, 104, GZ), "hallC": (900, 70, GZ), "hallD": (1300, 0, GZ), "arch": (1600, 0, GZ), "hallE": (1750, 0, GZ),
    "hallF": (2150, 0, GZ), "hallG": (2550, 0, GZ), "back": (2700, 0, GZ), "den_d": (1800, -200, GZ), "den": (2000, -380, GZ), "den_desk": (2230, -340, GZ), "den_shelf": (2240, -290, GZ), "bathg_d": (2600, -200, GZ), "bathg": (2600, -380, GZ),
    "sick_d": (2200, 200, GZ), "sick": (2400, 380, GZ), "pantry_d": (1600, 400, GZ), "pantry": (1800, 400, GZ), "kitchen3": (1500, 400, GZ),
    "living_d": (200, -200, GZ), "living": (380, -330, GZ), "living2": (640, -300, GZ),
    "dining_d": (200, 200, GZ), "dining": (300, 330, GZ), "dining2": (650, 300, GZ), "dk": (800, 400, GZ),
    "kitchen_d": (1000, 200, GZ), "kitchen": (1000, 380, GZ), "kitchen_b": (1060, 290, GZ), "kitchen2": (1440, 290, GZ),
    "sitting_d": (1400, -200, GZ), "sitting": (1250, -350, GZ),
    "stairs_g": (370, -88, GZ), "cellar_top": (860, -88, GZ), "cruiser": (-1450, 130, -40),
    # upstairs
    "stairs_u": (830, -88, UZ), "up_land": (890, 0, UZ), "up_c": (860, 110, UZ), "up_hallB": (600, 108, UZ), "up_hallA": (250, 60, UZ),
    "up_hallD": (1300, 0, UZ), "up_ell_d": (1600, 0, UZ), "up_hallE": (1750, 0, UZ), "up_hallF": (2150, 0, UZ), "up_hallG": (2550, 0, UZ),
    "daniel_d": (1800, -200, UZ), "daniel": (2000, -380, UZ), "sewing_d": (2600, -200, UZ), "sewing": (2600, -380, UZ), "aide_d": (1800, 200, UZ), "aide": (2000, 380, UZ),
    "bath2_d": (2600, 200, UZ), "bath2": (2600, 380, UZ), "master_d": (200, 200, UZ), "master": (380, 330, UZ), "kids_d": (200, -200, UZ), "kids": (420, -330, UZ),
    "bath_d": (1000, -200, UZ), "bath": (1150, -330, UZ), "prayer_d": (1000, 200, UZ), "prayer": (1150, 330, UZ),
    "attic_foot": (360, -88, UZ),
    # attic
    "attic_top": (840, -88, AZ), "attic": (760, -250, AZ), "attic2": (800, 150, AZ),
    # cellar
    "c_bot": (340, -88, CZ), "c_hallA": (250, 60, CZ), "c_hallC": (1000, 60, CZ), "c_shelf": (1380, 60, CZ), "root_d": (1400, 216, CZ),
    "root": (1400, 330, CZ), "c_wing_d": (210, -208, CZ), "c_wing": (300, -380, CZ),
}
EDGES = [("cruiser", "yard"), ("yard", "path"), ("path", "porch"), ("porch", "door_front"), ("door_front", "foyer"), ("foyer", "hallA"),
         ("foyer", "living_d"), ("living_d", "living"), ("living", "living2"), ("foyer", "dining_d"), ("dining_d", "dining"),
         ("dining", "dining2"), ("dining2", "dk"), ("dk", "kitchen"), ("hallA", "hallB"), ("hallB", "hallC"), ("hallA", "stairs_g"),
         ("foyer", "stairs_g"), ("stairs_g", "stairs_u"), ("stairs_u", "up_land"), ("hallC", "kitchen_d"), ("kitchen_d", "kitchen"),
         ("kitchen", "kitchen_b"), ("kitchen_d", "kitchen_b"), ("kitchen_b", "kitchen2"), ("hallC", "hallD"), ("hallD", "arch"), ("arch", "hallE"), ("hallE", "hallF"), ("hallF", "hallG"), ("hallG", "back"), ("hallD", "sitting_d"),
         ("hallE", "den_d"), ("den_d", "den"), ("den", "den_desk"), ("den_desk", "den_shelf"), ("hallG", "bathg_d"), ("bathg_d", "bathg"), ("hallF", "sick_d"), ("sick_d", "sick"),
         ("kitchen2", "kitchen3"), ("kitchen3", "pantry_d"), ("pantry_d", "pantry"),
         ("up_hallD", "up_ell_d"), ("up_ell_d", "up_hallE"), ("up_hallE", "up_hallF"), ("up_hallF", "up_hallG"), ("up_hallE", "daniel_d"), ("daniel_d", "daniel"),
         ("up_hallG", "sewing_d"), ("sewing_d", "sewing"), ("up_hallE", "aide_d"), ("aide_d", "aide"), ("up_hallG", "bath2_d"), ("bath2_d", "bath2"), ("sitting_d", "sitting"),
         ("hallC", "cellar_top"), ("cellar_top", "c_bot"), ("c_bot", "c_hallA"), ("c_hallA", "c_hallC"), ("c_hallC", "c_shelf"),
         ("c_shelf", "root_d"), ("root_d", "root"), ("c_hallA", "c_wing_d"), ("c_wing_d", "c_wing"),
         ("up_land", "up_c"), ("up_c", "up_hallB"), ("up_hallB", "up_hallA"), ("up_hallA", "master_d"), ("master_d", "master"),
         ("up_hallA", "kids_d"), ("kids_d", "kids"), ("up_hallA", "attic_foot"), ("attic_foot", "attic_top"), ("attic_top", "attic"),
         ("attic_top", "attic2"), ("up_land", "up_hallD"), ("up_land", "prayer_d"), ("up_c", "prayer_d"), ("prayer_d", "prayer"),
         ("up_land", "bath_d"), ("bath_d", "bath")]
_adj = {n: set() for n in NODES}
for a, b in EDGES:
    _adj[a].add(b)
    _adj[b].add(a)
for n, (x, y, z) in NODES.items():
    point("Nav_" + n, x, y, z, 0, tags=["NavNode", "N_" + n] + ["E_" + o for o in sorted(_adj[n])], folder="Nav")
log(f"nav: {len(NODES)} nodes, {len(EDGES)} edges")
