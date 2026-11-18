# Edith's Last Call: scare manifest

Nine authored scares, a repeating stalk encounter, and a long build-up in which nothing is seen at all. Code:
`Source/WellnessCheck/WCStory.cpp` (S1 to S8) and `Source/WellnessCheck/WCHouse.cpp` (build-up, lights, stalks, S9).
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
| **S4 Head by the ceiling** (signature) | Her true height. | Holding the iron key, box `t_up_landing`, `Gate()`. | At the far end of the upstairs hall at full height, head against the ceiling. She draws back, the light goes out, three seconds of nothing, then the scream and the sprint. Knock-down. | Full. | "She doesn't want me dead. She wants me here." Ruth's door, locked a minute ago, creaks open; a music box plays. Checkpoint. | Resolves after 9 s whatever happens. |
| **S7 Under the bed** | Quiet and close. | Taking Ruth's music box. | The music stops. She is under the bed, face to him, and lunges an arm's length with a short shriek. | Full. | Keepsake 1 of 3. Checkpoint. | One-shot. |
| **S9 The sewing room** | She is not attacking. She is keeping him company. | Taking the sewing shears (needed to cut the knots). | All lights die, then the flashlight. When it comes back she is sitting in the rocking chair by the cradle, rocking, eye on him. "Don't you leave me too." She rises; dark; gone; the door slams. | Movement free, no damage. | Shears in hand. Checkpoint. | One-shot. |
| **S5 The attic** | Daniel's truth, and punishment for finding it. | Opening the footlocker (attic key is in Daniel's room; taking it makes his radio tune itself and something whisper "is that you, Danny?"). | She comes the length of the attic on all fours, stops in arm's reach, rises over him screaming; dark; gone. | Full. | Dog tags and the cellar padlock key. Checkpoint. | One-shot. |
| **S6 The cellar door** | She does not want that door opened. | Unlocking the cellar padlock. | She runs the hall at him; on contact he is thrown down the cellar stairs and the door locks above him. | Full until contact. | Wakes at the foot of the stairs. Checkpoint. | Resolves after 9 s. |
| **S8 The root cellar** | Climax: break the pact while she begs him not to. | Laying the three keepsakes at her body, then cutting each knot with the shears. | "Don't." / "Don't you leave me too." / "Everybody leaves!" Each cut brings her closer; at the third she is in his face: "STAY!" Black. "...thank you." | Free between cuts. | Dawn. Doors open. | More than 95 s and she keeps him ("You stayed."); checkpoint reloads. |

## The stalk (repeats; the gun matters)

From S3 until the cellar, when things have been quiet for a few minutes, she comes looking: the house lights die, a low brass note,
and she is standing somewhere on his floor where he was not looking. She walks at him along the halls and through the doors, slowly
at first. Every shot that is aimed at her makes her flinch and lose ground; four or five drive her off with a shriek, for a few
minutes (she cannot be killed, and each box of cartridges is eight rounds). If she reaches him he is thrown down and she lets go;
the third time she does not let go ("You stayed.", checkpoint). If he gets right away from her for a quarter of a minute she gives up.
Code: `TickStalk`, `StalkShot`, `EndStalk`. Cartridges: den gun cabinet, Walter's desk, Daniel's room, kitchen, attic, cellar.

## Minor disturbances (not counted)

The front door opening itself; doors that were locked standing open; candles lit in a house with no one in it; flies; the wheelchair
in the rear hall; the tricycle; Walter's portrait turned back to face the room; the examine lines on about 55 objects.
