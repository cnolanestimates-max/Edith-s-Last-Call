"""Brings Docs/SCARE_MANIFEST.md up to date with the 2026-11-18 evening direction."""
import io
p = "C:/GameDev/Unreal/WellnessCheck/Docs/SCARE_MANIFEST.md"
s = io.open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert old in s, old[:60]
    s = s.replace(old, new, 1)


rep("Nine authored scares, a repeating stalk encounter, and a long build-up in which nothing is seen at all.",
    "Ten authored scares, repeating hunts, three memories, a set of quiet \"she was there the whole time\" sightings, and a long "
    "build-up in which nothing is seen at all.")
rep("`Source/WellnessCheck/WCHouse.cpp` (build-up, lights, stalks, S9).",
    "`Source/WellnessCheck/WCHouse.cpp` (build-up, lights, hunts, grabs, memories, S9, S10), `WCWorld.cpp` (`AWCWatcher`).")
a = s.index("| **S7 Under the bed**")
b = s.index("| **S9 The sewing room**")
s = s[:a] + ("| **S7 The hand under the bed** (slow) | Not a jump. She shows him she could have had him at any time. | At least two quiet minutes "
             "after S4, Ruth's door creaks open and a music box plays (`kids_open`). Entering the room (`t_kids`) with `Gate()` true. | The "
             "music stops. The game takes his view and holds it on the music box on the floor by the bed. A long arm comes slowly out "
             "from under the bed, the fingers close on the box, and it is drawn back under. She is never seen. About ten seconds. | None "
             "during the moment; returned afterwards. | \"It took it. It's under the bed.\" He has to crouch and take it back; nothing is "
             "there. Keepsake 1 of 3. 140 s rest before anything else. Checkpoint. | One-shot. |\n"
             "| **S10 The settlers' book** | She was in the wall the whole time. | Reading the note that says the desk key is in the hollow "
             "book, then pulling the book from the den shelf. | Behind the book is a ragged hole, and her eye is in it, looking at him. He "
             "drops the book. The eye is gone; something scurries away inside the wall. | Full. | The desk key is in the book on the floor. "
             "| One-shot. |\n") + s[b:]
rep("| Holding the iron key, box `t_up_landing`, `Gate()`. |", "| Holding the iron key, box `t_up_landing`, `Gate()`. |")
rep("Ruth's door, locked a minute ago, creaks open; a music box plays. Checkpoint.", "Checkpoint. (Ruth's door opens two quiet minutes later, see S7.)")
a = s.index("## The stalk (repeats; the gun matters)")
b = s.index("## Minor disturbances (not counted)")
s = s[:a] + '''## The hunts (repeat; the gun matters)

From S3 until the cellar, when things have been quiet for a few minutes, she comes for him.

- **The first is an ambush.** No warning but the lights dying: she comes round the nearest corner at a dead run and has him.
- **After that he hears her first.** Bare feet, heavy and wet, on boards that creak under her, from the far end of the floor
  (she starts at least 11 m away, at a walk). That sound is the cue to turn, put the light on her and shoot. Three or four
  aimed shots drive her off with a shriek for a few minutes; she cannot be killed, and each box of cartridges is eight rounds.
  Inside about 4.5 m she stops walking and runs, twice as fast as before.
- **The grab.** She is in his face, mouth open far too wide, screaming; the picture stays on her for a second and a third
  before it goes black. The first three grabs each show a memory (below). The third time in a row that he is caught she
  does not let go ("You stayed.", checkpoint).
- Her footsteps are also heard at other times: a few steps somewhere on this floor or the one above, then nothing.

Code: `TickStalk`, `StalkShot`, `EndStalk`, `Grab`; footsteps in `AWCEntity::Tick` (`her_step`). Cartridges: den gun cabinet,
Walter's desk, Daniel's room, kitchen, attic, cellar.

## The memories (one per grab, in order)

When she has hold of him he sees what she remembers, warm and washed out, with her own human voice (not the many-voiced one).

1. **The last Thanksgiving.** The front door open on daylight, her family already on the porch, Edith in the hall asking them to stay.
2. **The attic.** Edith on a crate with a lantern, her grandmother's book open in her lap. (Later he gets into the attic and finds the book.)
3. **The ninth night.** Edith in the rocking chair by candles, asking; something tall and black standing in the corner where the light does not reach.

Code: `PlayMemory` (`Cam_MemN`, actors tagged `MemN`, `PP_Memory`), level `Scripts/level/memory.py`.

## She was there the whole time (never a jump, never a grab)

- **Eyes in the walls.** Eight ragged holes (hall by the stairs, behind the fridge, the fireplace, and others) with her eye in them.
  If he notices and looks straight at one, it sinks back into the dark. If he does not notice, nothing happens.
- **Hair.** Five places where her long grey-blonde hair hangs down from a gap in the ceiling or the rafters. When he gets
  close or holds the light on it, it is drawn slowly up out of sight.
- **The Company.** The thing she asked in: a tall, featureless black outline, seen at most four times after the first sight
  of her (end of the upstairs rear hall, the attic, the cellar, the sickroom). The light stutters and the corner is empty.
  "That wasn't her. That was taller."
- **Her drawings.** Childlike crayon drawings of herself and the black shape (holding hands, at supper, "HE NEVER LEVES") on her
  sitting-room wall and in six other places. Edith has gone back to being a child, and it is the only friend that stayed.

Code: `AWCWatcher` (kinds 0 eye, 1 hair, 2 the Company), level `watchers.py` and `memory.py`.

## Her voice in the house (after the door locks)

Quiet, and rarer than the creaks: a laugh in another room, crying behind a wall, humming, a whisper close to one ear
("stay", "I see you") with nothing there when he turns. Present-day Edith speaks with many voices at once, pitched down and
out of step with each other; the memories keep her own voice. Code: ambience table in `StoryTick`; `Scripts/audio/demon_vo.py`.

'''.replace("\r", "") + s[b:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("scare manifest updated")
