# Edith's Last Call: scare manifest

Ten authored scares, repeating hunts, three memories, a set of quiet "she was there the whole time" sightings, and a long build-up in which nothing is seen at all. Code:
`Source/WellnessCheck/WCStory.cpp` (S1 to S8) and `Source/WellnessCheck/WCHouse.cpp` (build-up, lights, hunts, grabs, memories, S9, S10), `WCWorld.cpp` (`AWCWatcher`).
Every scare is driven by story flags, so it fires once, survives a checkpoint reload in a valid state, and cannot overlap another
(`Gate()` is false while another sequence or a stalk is running, and each scare buys a rest period with `Rest()`).
"Evidence" means automatic play-through logs and screenshots (`Saved/Auto*/`, `Saved/Logs/*.log`); see the QA report for what was and
was not verified. No human fear response has been measured.

## Pacing rule (Cheyenne)

She is not seen, not even at the edge of a doorway, for the first 8 to 10 minutes inside. Until then the house does the work.

| Minute inside (about) | What happens | Code |
|---|---|---|
| 0:25 | The front door shuts and locks behind him. When he tries it: "It was just open!" The radio gives static. | `TickBuildUp` step 0, `locked:front` |
| any | Light switches work: dim yellow bulbs that sag and flicker. The power was cut off a year ago (the mail says so). | `SwitchRoom`, `TickHouseLights` |
| 1:25 | A heavy thump overhead. | step 1 |
| 2:30 | Footsteps cross the ceiling. "Somebody's up there." | step 2 |
| 3:35 | The rocking chair in the living room rocks by itself, and stops when looked at. | step 3 |
| 4:40 | A light he switched on goes off by itself, with the click of the switch. "I didn't touch that." (If none is on, a door slams upstairs.) | step 4 |
| 5:45 | Fingernails in the wall right beside him, then something skittering away inside it. | step 5 |
| 6:40 | Walter's radio in the den tunes itself; a breath at his ear; the flashlight flickers. | step 6 |
| 7:30 to 9:30 | The body-drop thump and the dragging upstairs. "Mrs. Harrow? I'm coming upstairs." | `heard_upstairs` |
| 8 to 10 | S1, the first sight of her. | `ScarePeek` |

Under all of it: room tone, a low drone that rises with tension, chimney wind, and a random cue every 5 to 13 seconds (creaks,
skittering, scratching in the walls, knocks, far doors, steps overhead, whispers, a breath).

## The scares

| ID | Purpose | Trigger and preconditions | The event | Player control | Aftermath | If missed or repeated |
|---|---|---|---|---|---|---|
| **S1 Corner peek** (signature) | First sight. She is in the house, she is tall, she is watching. | `heard_upstairs`, then box `t_up_corridor` in the upstairs hall at least 12 s after reaching the landing. | Half her face and the one black eye lean out of the master bedroom doorway, high up, fingers on the frame. After about 1.25 s of being looked at, or within 3.8 m, she slides back and the door swings shut. | Full. | Bedroom empty. Radio: the call came from this house's own dead landline; then the radio dies. Objective: get out, try the back door. | Whispers "who's there?" after 9 s unseen; withdraws after 26 s anyway. |
| **S3 The long hall** | The turn. No way out, and the first use of the gun. | `want_leave`, entering the rear hall (`t_backhall`) or trying the nailed back door. | Every light in the house dies (a fuse blows). She stands at the far front end of the 28 m hall and walks at him, slowly. Each shot makes her flinch and stop for a moment. About halfway she screams and runs. Contact: thrown on his back, black. | Full: move, aim, fire, reload. | "Went right through her." / "But she flinched. Every shot." House lights stay dead until the fuse is replaced (fuse box in the pantry, spare fuse in the den). Checkpoint. | She follows if he runs; she runs after 30 s regardless. |
| **S2 The phone** | Her voice; she invites him to supper. | `lockin_done`, back door tried, and a quiet spell; pressing E on the ringing phone. | "You came. Sit down. Supper's getting cold." Flashlight dies; her breath; when the light returns she is seated at the kitchen table. Looked at (or after 5 s): scream, rush, light out. | Full except the light. | Drawer that was shut is open with the brass key. Checkpoint. | Timer fallback. One-shot. |
| **S4 Head by the ceiling** (signature) | Her true height. | Holding the iron key, box `t_up_landing`, `Gate()`. | At the far end of the upstairs hall at full height, head against the ceiling. She draws back, the light goes out, three seconds of nothing, then the scream and the sprint. Knock-down. | Full. | "She doesn't want me dead. She wants me here." Checkpoint. (Ruth's door opens two quiet minutes later, see S7.) | Resolves after 9 s whatever happens. |
| **S7 The hand under the bed** (slow) | Not a jump. She shows him she could have had him at any time. | At least two quiet minutes after S4, Ruth's door creaks open and a music box plays (`kids_open`). Entering the room (`t_kids`) with `Gate()` true. | The music stops. The game takes his view and holds it on the music box on the floor by the bed. A long arm comes slowly out from under the bed, the fingers close on the box, and it is drawn back under. She is never seen. About ten seconds. | None during the moment; returned afterwards. | "It took it. It's under the bed." He has to crouch and take it back; nothing is there. Keepsake 1 of 3. 140 s rest before anything else. Checkpoint. | One-shot. |
| **S10 The settlers' book** | She was in the wall the whole time. | Reading the note that says the desk key is in the hollow book, then pulling the book from the den shelf. | Behind the book is a ragged hole, and her eye is in it, looking at him. He drops the book. The eye is gone; something scurries away inside the wall. | Full. | The desk key is in the book on the floor. | One-shot. |
| **S9 The sewing room** | She is not attacking. She is keeping him company. | Taking the sewing shears (needed to cut the knots). | All lights die, then the flashlight. When it comes back she is sitting in the rocking chair by the cradle, rocking, eye on him. "Don't you leave me too." She rises; dark; gone; the door slams. | Movement free, no damage. | Shears in hand. Checkpoint. | One-shot. |
| **S5 The attic** | Daniel's truth, and punishment for finding it. | Opening the footlocker (attic key is in Daniel's room; taking it makes his radio tune itself and something whisper "is that you, Danny?"). | She comes the length of the attic on all fours, stops in arm's reach, rises over him screaming; dark; gone. | Full. | Dog tags and the cellar padlock key. Checkpoint. | One-shot. |
| **S6 The cellar door** | She does not want that door opened. | Unlocking the cellar padlock. | She runs the hall at him; on contact he is thrown down the cellar stairs and the door locks above him. | Full until contact. | Wakes at the foot of the stairs. Checkpoint. | Resolves after 9 s. |
| **S8 The root cellar** | Climax: break the pact while she begs him not to. | Laying the three keepsakes at her body, then cutting each knot with the shears. | "Don't." / "Don't you leave me too." / "Everybody leaves!" Each cut brings her closer; at the third she is in his face: "STAY!" Black. "...thank you." | Free between cuts. | Dawn. Doors open. | More than 95 s and she keeps him ("You stayed."); checkpoint reloads. |

## The hunts (repeat; the gun matters)

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

## Minor disturbances (not counted)

The front door opening itself; doors that were locked standing open; candles lit in a house with no one in it; flies; the wheelchair
in the rear hall; the tricycle; Walter's portrait turned back to face the room; the examine lines on about 55 objects.
