"""Pass 108: the settlers book at eye level (Cheyenne 2026-11-19 16:38 UTC: "the shelf is low so after pulling the book you get
the scripted scare sound but you don't see anything ... make the bookshelf as tall as you, at least eye level, so when you pull
the book Edith's eye and yours are equal").
The single low shelf (book at 104 to 128 cm) becomes a tall open bookcase of four shelves with uprights; the settlers book is on
the shelf at 141 cm, so the hole behind it is at 154 cm: the height of his eyes."""
R = "C:/GameDev/Unreal/WellnessCheck/"
p = R + "Scripts/level/watchers.py"
s = open(p, encoding="utf-8").read()
a = s.index("BKX0, BKX1, BKY, BKZ = ")
b = s.index('interact("WCUsable", "book_settlers"')
new = '''BKX0, BKX1, BKY, BKZ = 470.0, 624.0, -216.0, GZ + 141.0             # the settlers book's shelf: its hole is at the height of his eyes (it was a low shelf, and in the den)
M_SHELF = surf("WoodDark", "MI_WoodDark")
_leathers = [surf("LeatherOld", m) for m in ("MI_LeatherRed", "MI_LeatherGreen", "MI_LeatherBlue", "MI_LeatherTan", "MI_Leather")]
# a tall open bookcase against the wall: two uprights, a top, four shelves of county histories
for bx in (BKX0 - 3.0, BKX1):
    box(f"BookCaseSide_{int(bx)}", bx, bx + 3.0, BKY - 22, BKY, GZ, GZ + 182, M_SHELF, "Dressing/Living", collide=False)
box("BookCaseTop", BKX0 - 3.0, BKX1 + 3.0, BKY - 23, BKY, GZ + 179, GZ + 182, M_SHELF, "Dressing/Living", collide=False)
box("BookCaseKick", BKX0, BKX1, BKY - 20, BKY, GZ, GZ + 9, M_SHELF, "Dressing/Living", collide=False)
box("BookCaseBlock", BKX0 - 3.0, BKX1 + 3.0, BKY - 22, BKY, GZ, GZ + 60, "WC:M_Invisible" if False else M_SHELF, "Dressing/Living", collide=True).set_actor_hidden_in_game(True)
SETTLERS_X = None
for _row, _z in enumerate((GZ + 33.0, GZ + 69.0, GZ + 105.0, BKZ)):
    box(f"BookShelfBoard_{_row}", BKX0, BKX1, BKY - 21, BKY, _z - 3, _z, M_SHELF, "Dressing/Living", collide=False)
    _bk = random.Random(42 + _row * 7)
    bx = BKX0 + 5.0
    k = 0
    while bx < BKX1 - 8:
        w = _bk.uniform(3.4, 6.2)
        h = _bk.uniform(19.0, 25.0)
        d = _bk.uniform(13.0, 16.5)
        if _z == BKZ and SETTLERS_X is None and bx > (BKX0 + BKX1) / 2 - 6:
            SETTLERS_X = bx + 2.6
            b_ = box("SettlersBook", bx, bx + 5.2, BKY - 17.5, BKY - 2.0, BKZ, BKZ + 24.0, surf("LeatherOld", "MI_Leather"), "Dressing/Living", collide=False, tags=["SettlersBook"])
            b_.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            bx += 5.6
            continue
        if _row < 3 and _bk.random() < 0.12:
            bx += _bk.uniform(6.0, 14.0)                 # a gap where one has gone
            continue
        box(f"ShelfBook_{_row}_{k}", bx, bx + w, BKY - d - 1.5, BKY - 1.5, _z, _z + h, _bk.choice(_leathers), "Dressing/Living", collide=False, roll=_bk.choice((0, 0, 0, 4, -3)))
        bx += w + 0.5
        k += 1
'''
s = s[:a] + new + s[b:]
open(p, "w", encoding="utf-8", newline="\n").write(s)
import py_compile
py_compile.compile(p, doraise=True)
print("pass 108 applied")
