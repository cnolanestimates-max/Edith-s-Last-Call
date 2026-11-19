# Edith's Last Call: QA report

Updated 2026-11-19 00:45 UTC. Everything here was run on WorkLaptop2 in the editor's `-game` mode at 1280x720 (not a packaged
build). "Bot" is the automatic play-through in `WCAuto.cpp`: it walks the real nav graph, aims the real camera at things and
presses the real interact, fire and reload functions. Where it could not do something it was allowed to force past it
(`-WCAutoForce`), and every one of those is listed as a failure below.

**No person has played this build from start to finish.** No packaged build exists yet (Cheyenne asked for no interim package).
Sound has not been judged by ear. Scores are in `PRODUCTION_STATUS.md` and are my own estimate.

## Run 7 (2026-11-19 00:01 to 00:22 UTC), full play-through, accelerated pacing

Command: `wc.ps1 game auto7 "-WCAuto -WCFast -WCAutoForce -WCNoDrive -WCShots=Saved/Auto7"`. Log `Saved/Logs/auto7.log`, 54
screenshots in `Saved/Auto7/`. `-WCFast` shortens the quiet waits between events to 8% (scares themselves play at real speed), so
this run says nothing about real play length.

| Check | Result |
|---|---|
| Reaches the ending and credits without a crash | Yes: `WCENDING t=1157.4`, then credits, then the menu, then the bot quit |
| Scares fire once each, in order | S1 227 s, S3 339 s, S2 490 s, S10 586 s, S4 641 s, S7 676 s, S9 901 s, S5 957 s, S6 1015 s, S8 finale |
| Memories on the first three grabs | 1 at 354 s, 2 at 390 s, 3 at 518 s; screenshots `memory_1..3.png` show all three tableaux |
| Grabs | 7 in the run (`grab_01..07.png`): she is in his face with her mouth open. Her face was under-lit (the flashlight hit her chest); fixed after this run, not yet re-photographed in a full run |
| Hand under the bed (S7) | Fired, and measured her wrist at 101 cm forward, 35 cm left, as designed. The bot was still in the doorway, where the rocking horse hid the box, so it photographed nothing. After this run: the moment now waits until the box is in plain sight within 4 m, the toys were moved, and test runs photograph it themselves. Seen working in look test 6 (below) |
| Frame time | Mean 13.9 ms (72 fps) over 22 one-minute windows; worst 99th-percentile window 94 ms. Occasional hitches remain |

Failures the bot was forced past (each is a thing to fix or explain):

| What | Why (from the bot's own trace) | Does it affect a person? |
|---|---|---|
| Could not focus `note_diary2` and `pick_key_prayer` (sitting room) | `Desk_Writing` is between the eye and the item at 1.4 m | Probably not: a person steps round to the open side of the desk. Needs an `-WCItems` photo to be sure they are not sunk in the desk |
| `pick_keep_ruth` unreachable, then hidden by `RuthBed` | The box was drawn a full metre under the bed | Yes, this could have stuck a player. Fixed after the run: it now stops just under the edge of the bed |
| `A_Bath2`, `A_Sewing` unreachable | Bot route (nav nodes), it teleported | Unknown until checked: a doorway may be blocked by furniture |
| Could not focus `pick_shears` | `Chair_Dining_HighBack` in the way from where the bot was teleported | Probably not |
| Could not focus `up_attic`, `cellar` doors | The bot stood on the wrong side of a wall (`Wall_Plain_Simple` at 62 cm) | No: bot route only |
| `A_Foyer` unreachable at dawn | Bot route | Unknown |

## Look tests (still images of specific things)

`wc.ps1 game Her5|Her6 "-WCHerLook -WCShots=..."`, screenshots in `Saved/Her5/`, `Saved/Her6/`.

| Thing | Result |
|---|---|
| Pistol | Reads as a pistol in a gloved hand, pointing forward (`gun_up.png`) |
| Flashlight up close | The beam used to land 30 cm below what he looked at. It now converges on what he looks at: the eye behind the book is lit (`Her6/book_eye.png`); it was black in `Her5` |
| Eye behind the settlers' book (S10) | Visible, lit, in the hole behind the book |
| The Company | Tall black outline against the window at the end of the upstairs rear hall (`company_uprear.png`) |
| Her drawings | On the sitting-room wall, six sheets (`drawings_wall.png`). Small at room distance |
| Hand under the bed | `hand_1_coming`, `hand_2_on_box`: a long arm from under the foot of the bed with the hand on the music box |
| Her face | Scream mouth opens; jaw, brow and lip keys are driven every frame (not visible in stills) |
| Hair hanks, eyes in walls | Hair hanks visible; the wall eyes are small and dark by design and hard to see in stills |

The second look test stopped at the crouch step (the bot's crouch step did nothing). Fixed.

## Not tested yet

- A run at real pacing (so there is no measured play length).
- The forest drive after the polish pass (no capture yet).
- Whether small props still float (`-WCItems` run not done on this level build).
- The inventory screen (built after run 7; its own photo test is `-WCInvTest=<dir>`).
- Main menu, settings and controls screens on this build (`-WCMenuTest=<dir>`).
- Sound mix, her footsteps and her many-voiced lines by ear.
- A packaged Shipping build and a fresh-folder launch.
- Any human playtest.
