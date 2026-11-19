"""The forest road becomes a tree tunnel (Cheyenne 03:38 UTC): tall pines close on both sides in three ranks, the first
rank leaning in over the road, with young pines between them bent right across it; ferns thick at the verge.  The grey kit
rocks, stumps, logs, bramble bushes and flat-coloured kit trees are gone from the road.  A dim wash from the car tilts up into
the branches so the roof of the tunnel is seen."""
import io, sys
p = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/forest.py"
s = io.open(p, encoding="utf-8").read()

# ---- trees can lean
old = '''def tree(mesh, x, y, scale, sub="Trees"):
    a = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(x, y, -44), R(_fr.uniform(0, 360)))'''
new = '''def tree(mesh, x, y, scale, sub="Trees", lean=0.0, toward=None):
    rot = R(_fr.uniform(0, 360))
    if lean and toward:
        # spun about its own trunk first, then tipped toward a point (the road)
        rot = unreal.MathLibrary.compose_rotators(rot, R(math.degrees(math.atan2(toward[1] - y, toward[0] - x)), -lean))
    a = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(x, y, -44 - (18 if lean > 12 else 0)), rot)'''
assert old in s
s = s.replace(old, new)

a = s.index("# along the road: two close rows that wall it in, then a thinning forest behind")
b = s.index('place("Sign_Turn_Back"')
s = s[:a] + '''# along the road: a tunnel.  Three ranks of tall pines each side, the first leaning in; young pines bent over the road
# between them; nothing but trees and ferns (the kit rocks, stumps and logs read as grey slabs in the headlights).
def road_tree(x, y, kind, lean, toward, scale):
    if in_yard(x, y) or near_road(x, y, 205):
        return
    for (tx, ty) in TREE_SPOTS[-60:]:
        if abs(tx - x) < 70 and abs(ty - y) < 70:
            return
    TREE_SPOTS.append((x, y))
    if kind == "small" and SAPS:
        tree(_fr.choice(SAPS), x, y, scale, "Saplings", lean, toward)
    elif kind == "dead" and DEAD:
        tree(_fr.choice(DEAD), x, y, scale, "Trees", lean, toward)
    elif PINES:
        tree(_fr.choice(PINES), x, y, scale, "Trees", lean, toward)


for i in range(0, len(SAMPLES) - 1):
    (x0, y0), (x1, y1) = SAMPLES[i], SAMPLES[i + 1]
    if x0 > -2500:
        break
    d = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    for side in (-1, 1):
        def at(off, along):
            return x0 + ux * along - uy * off * side, y0 + uy * along + ux * off * side
        mid = (x0 + ux * 60, y0 + uy * 60)
        # first rank: at the very edge of the dirt, leaning in so the crowns meet overhead
        px, py = at(_fr.uniform(238, 292), _fr.uniform(-90, 90))
        road_tree(px, py, "big" if _fr.random() > 0.1 else "dead", _fr.uniform(6, 12), mid, _fr.uniform(1.05, 1.4))
        # second and third ranks, upright, so there is no seeing through
        if _fr.random() < 0.85:
            px, py = at(_fr.uniform(360, 520), _fr.uniform(-120, 120))
            road_tree(px, py, "big", _fr.uniform(2, 6), mid, _fr.uniform(0.95, 1.3))
        if _fr.random() < 0.6:
            px, py = at(_fr.uniform(600, 900), _fr.uniform(-120, 120))
            road_tree(px, py, "big" if _fr.random() > 0.2 else "dead", 0.0, None, _fr.uniform(0.9, 1.25))
        if i % 2 == 0 and _fr.random() < 0.5:
            px, py = at(_fr.uniform(1000, 1700), _fr.uniform(-200, 200))
            road_tree(px, py, "big", 0.0, None, _fr.uniform(0.9, 1.2))
        # young pines bent right over the road: the roof of the tunnel, low enough for the headlights
        for _rep in range(2):
            if _fr.random() < 0.8:
                px, py = at(_fr.uniform(214, 268), _fr.uniform(-125, 125))
                road_tree(px, py, "small", _fr.uniform(24, 42), mid, _fr.uniform(2.0, 3.2))
# round the yard: the forest stands right behind the fence on every side
for i in range(150):
    x, y = _fr.uniform(-3400, XB + 2300), _fr.uniform(-2600, 2600)
    if in_yard(x, y):
        continue
    near_fence = min(abs(x + 2640), abs(abs(y) - 1260)) < 500 and x < 600
    if near_fence or _fr.random() < 0.6:
        try_tree(x, y, "big" if _fr.random() < 0.8 else "dead")
log(f"forest: {count['tree']} trees ({len(PINES)} pine types, {len(DEAD)} dead, {len(SAPS)} saplings)")

# ferns thick along both verges
n_under = 0
for i in range(0, len(SAMPLES) - 1, 1):
    (x0, y0), (x1, y1) = SAMPLES[i], SAMPLES[i + 1]
    if x0 > -2700:
        break
    d = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    for side in (-1, 1):
        if not FERNS or _fr.random() > 0.9:
            continue
        off = _fr.uniform(222, 330) * side
        px, py = x0 - uy * off + ux * _fr.uniform(-120, 120), y0 + ux * off + uy * _fr.uniform(-120, 120)
        for k in range(3):
            a = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(px + _fr.uniform(-90, 90), py + _fr.uniform(-90, 90), -42), R(_fr.uniform(0, 360)))
            a.set_actor_label("Fern")
            c = a.skeletal_mesh_component
            c.set_skeletal_mesh_asset(_fr.choice(FERNS))
            s_ = _fr.uniform(1.4, 2.5)
            a.set_actor_scale3d(V(s_, s_, s_))
            c.set_collision_profile_name("NoCollision")
            c.set_editor_property("cast_shadow", False)
            lean_skel(c)
            a.set_folder_path(f"House/{FO}/Ferns")
        n_under += 1
''' + s[b:]
old = '''place("Tree_Fallen_Log", -13800, -60, -42, 70, FO + "/Under", scale=1.7, collide=False)
'''
assert old in s
s = s.replace(old, "")
old = '''cpart(light_point("TailGlow",'''
new = '''# and a dimmer, cooler one tilted up into the branches, so the roof of the tunnel shows
cpart(light_spot("CanopyWash", CRX + 200, CRY, 150, 0, 24, 4200, (0.86, 0.92, 1.0), 3400, 30, 58, "Cruiser", tags=["Hide_dawn", "Headlight"], shadows=False, vol=0.25))
cpart(light_point("TailGlow",'''
assert old in s
s = s.replace(old, new, 1)
compile(s, p, "exec")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
