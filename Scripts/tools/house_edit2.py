import io
p = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/build_house.py"
s = io.open(p, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new, count)


# the knots are cords of her own hair, not dolls
sub('''for i, (x, y) in enumerate(((1100, 380), (1200, 300), (1300, 380))):
    place("Doll_Voodoo_Hanging", x, y, UZ + 225, i * 70, PR, collide=False, name=f"HairKnot_{i}")''',
    '''def hair_cord(x, y, z_top, length, folder, tags=(), name="HairCord"):
    """A hanging cord of grey hair with a fat knot in it."""
    place(CYL, x, y, z_top - length / 2, 0, folder, name=name, tags=tags, collide=False, scale=(0.014, 0.014, length / 100.0), mats={0: surf("Rope", "MI_Sheet")})
    place(SPHERE, x, y, z_top - length * 0.62, 0, folder, name=name + "_knot", tags=tags, collide=False, scale=(0.06, 0.06, 0.085), mats={0: surf("Rope", "MI_Sheet")})
    place(SPHERE, x, y, z_top - length, 0, folder, name=name + "_end", tags=tags, collide=False, scale=(0.035, 0.035, 0.12), mats={0: surf("Rope", "MI_Sheet")})


for i, (x, y) in enumerate(((1100, 380), (1200, 300), (1300, 380))):
    hair_cord(x, y, UZ + 328, 150 + i * 14, PR, name=f"PrayerCord_{i}")''')
sub('''for i, (x, y) in enumerate(((1330, 470), (1400, 455), (1470, 470))):
    interact("WCUsable", f"knot{i + 1}", "Doll_Voodoo_Hanging", x, y, CZ + 205, i * 80, "Cut the knot", (14, 14, 50), (0, 0, -45), tags=[f"Show_knot{i + 1}"])''',
    '''for i, (x, y) in enumerate(((1330, 470), (1400, 455), (1470, 470))):
    interact("WCUsable", f"knot{i + 1}", None, x, y, CZ + 205, i * 80, "Cut the knot", (14, 14, 50), (0, 0, -45), tags=[f"Show_knot{i + 1}"])
    hair_cord(x, y, CZ + 328, 190 + i * 10, RC, tags=[f"Show_knot{i + 1}"], name=f"Knot_{i + 1}")''')
sub('place("Potion_Shelf_Wall", 520, 190, CZ + 120, 180, CE, collide=False)\n', '')
sub('place("Jar_Herbs_Shelf", 1560, 400, CZ + 120, 270, RC, collide=False)\n', '')
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
