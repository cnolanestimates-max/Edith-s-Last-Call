"""Snag spots from the full bot playthrough of 2026-11-23 (Saved/fulltest3_1123_1637/REPORT.md), fixed on the saved map.
Every move is to a fixed place, so running it twice changes nothing.  apply_polish.py step "snag_fixes"; build_house.py runs it last.
Measured first with snag_survey.py.  Capsule: radius 30, so any gap under 60 cm between two blockers is a pocket he wedges into."""
import unreal as u

V = u.Vector


def dress():
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = sub.get_all_level_actors()

    def one(label, near=None, within=60.0):
        found = [a for a in actors if a.get_actor_label() == label and
                 (near is None or (a.get_actor_location() - V(*near)).length() < within)]
        if len(found) != 1:
            u.log_warning(f"WC_SNAGFIX {label}: {len(found)} found near {near}, skipped")
            return None
        found[0].modify()
        return found[0]

    def put(a, xyz, yaw=None):
        a.set_actor_location(V(*xyz), False, True)
        if yaw is not None:
            a.set_actor_rotation(u.Rotator(0, 0, yaw), False)
        o, e = a.get_actor_bounds(True)
        u.log_warning(f"WC_SNAGFIX {a.get_actor_label()} -> ({xyz[0]:.0f},{xyz[1]:.0f},{xyz[2]:.0f}) box x {o.x - e.x:.0f}..{o.x + e.x:.0f} y {o.y - e.y:.0f}..{o.y + e.y:.0f}")

    # 1. Edith's bathroom (downstairs): the wheelchair stood across the east half of the doorway, 1.1 m in, so walking straight
    #    in ran into it.  Half a metre east it is still the first thing you see from the door, still faces the mirror, and the
    #    door lane is clear.  Her note rides on the seat.  The mirror scene and the roll both start from wherever the chair is.
    chair = one("Wheelchair_Rusted_NoFootrest", (2622, -346, 0), 80)
    if chair:
        put(chair, (2669, -346, 0))
    letter = one("BathMirrorLetter", (2616, -346, 53.7), 80)
    if letter:
        put(letter, (2663, -346, 53.7))

    # 2. Front upstairs bathroom: the invisible blocker round the hole in the floor stood 22 cm out from the hole on every side,
    #    a wall in mid-air that boxed him away from the dresser and the tub.  Now it is the hole itself plus 2 cm: his capsule
    #    still cannot reach over the edge, and the room is walkable round it.
    block = one("HoleBlock_1365_350")
    if block:
        x0, x1, y0, y1 = 1290 - 2, 1440 + 2, -430 - 2, -310 + 2
        o, e = block.get_actor_bounds(True)
        s = block.get_actor_scale3d()
        k = ((x1 - x0) / (2 * e.x), (y1 - y0) / (2 * e.y))
        block.set_actor_scale3d(V(s.x * k[0], s.y * k[1], s.z))
        put(block, ((x0 + x1) / 2, (y0 + y1) / 2, block.get_actor_location().z))

    # 3. Living-room piano: the stool stood 39 cm off the piano's front at its north end, a pocket he walked into and stuck in on
    #    the way to the drawer key.  Tucked in under the keyboard, a little left of the drawer, there is no gap to catch in and
    #    he can stand at the keys.
    stool = one("Piano_Stool", (190, -363, 0), 80)
    if stool:
        put(stool, (152, -440, 0))

    # 4. Sewing room: the high-backed chair stood 60 cm inside the doorway, square in the way in.  It goes to the sewing table,
    #    facing it, clear of the box-room door.
    sew = one("Chair_Dining_HighBack", (3210, -306, 350), 80)
    if sew:
        put(sew, (3126, -432, 350), 90)

    # 5. Attic: Daniel's tags lay at the back of the footlocker lid, 91 cm from where he stands at its front.  At the front edge
    #    of the lid they are easy to take (the padlock key stays where it is).
    tags = one("Pickup_pick_keep_daniel", (752, -444, 772), 40)
    if tags:
        put(tags, (752, -403, 772))

    u.log_warning("WC_SNAGFIX done")
