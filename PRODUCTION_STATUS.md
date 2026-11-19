# Edith's Last Call: production status

(Working title "Wellness Check"; the project folder keeps that name.) Updated 2026-11-19 20:40 UTC, in progress.
Engine: UE 5.9.0. Project: `C:\GameDev\Unreal\WellnessCheck`. Git: local repo on `main`, remote
`github.com/cnolanestimates-max/Edith-s-Last-Call` (private). Pushed; checkpoints are pushed as work lands.

## State 2026-11-19 16:45 UTC (Cheyenne play-tested today and is directing live)

**Built today from her play-test and design notes** (passes 96 to 105; details in each `Scripts/tools/fix_passNN.py`)
- Picture: VHS camcorder filter is the default (options row "Picture"; the other four stay switchable).
- Sound: clean synthesized room tone and night bed (`Scripts/audio/make_ambience.py`), one quiet cue every 35 to 80 s, no
  looping doors or switches, no birds on the drive. A real door opens by itself twice in the game at most (`WCDOOR`).
- Deputy: voice and subtitles only to dispatch and to Edith; thought text removed; short feedback kept ("Locked.").
- Outside first: knock, no answer, round the back (tree line, tool shed, locked back door), then the front door opens.
- Removed: hair drawn into the ceiling, the smoke figure on the road.
- Flashlight 20% wider and 30% longer. Flashlight hand mirrored (it was a right hand on the left).
- First scare is set off by the player, no clock. **Fetch chain:** kitchen wall vent screwed shut, screwdriver upstairs beside
  the locked jewelry box, rag doll behind the vent, small key sewn in her back (found in Inspect: `GWCHidden` in `WCGame.cpp`),
  thump, first sight of her on the way back up, jewelry box: Ruth's letter and **Edith's glass eye**.
- **Ending:** after the third knot and "STAY!", the dark lifts and the last act is putting her eye back (`eye_wanted`,
  `eye_given`, `FinaleDawn`). Bot run auto14 reached it (`WCENDING ... her eye is given back`, then the ending).
- **Keys away from their locks:** sitting-room key in a drawer in the upstairs bath (after the phone), hollow book in the
  living room (desk is in the den), fuse inside the locked sitting room, objectives say "Find what the key opens".
- **Items:** everything that can be picked up is remodelled with baked wear (`Scripts/art/build_items_fine.py`, 21 models,
  previews `SourceArt/Props/items_fine/preview`, sheet `Saved/_s/items_fine_sheet.jpg`); imported over the plain models by the
  `items` step. Each key has its own model.
- Bug found by the bot and fixed: after a memory (grab) the picture stayed black until some later event faded it in.
- Trigger sequence document for her: https://claude.ai/artifact/98k2iiutMNma5NAK3a5iUm (kept current). Dev keys with
  `Play Edith's Last Call (dev).cmd`: F9 thump now (gives the small key), F10 end the quiet gap.

**State at 20:40 UTC, 2026-11-19: RESUME HERE** (passes 113 to 118; she play-tested at 19:30 and gave a list)

Cheyenne also works with **Codex in this same folder**. Codex owns the flashlight (`WCCharacter` beam width, lumens) and the
photographs in the picture frames (`living_room.py`, album shots). Pull first, never revert its changes, and never build,
import, rebuild the level or launch the game while any `UnrealEditor*` process is running.

Built from her 19:33 to 20:12 list (in the level and compiled unless marked):
- **Outside:** front door stays locked until the first VHS tape is taken from the shed bench. Taking it tips a real trash
  can at the back of the house (`TrashCanUp/Down`, spilled rubbish, `trash_crash`), the deputy calls "Mrs. Harrow, is that
  you?" (`d_shedcall`), and only then does the front door open (`tape1_taken`).
- **Tapes:** the television is a TV/VCR combo and is off on arrival. Three tapes: shed, the aide's bed, the attic. Use the
  television while holding a tape to play it; it plays until switched off.
- **Sound:** only the music drone and the ambience beds loop. The repeating thump was the indoor wind loop and then the
  library drone; both are gone (the drone is synthesized, `Scripts/audio/make_play3.py`). Crickets are back outside. Every
  other sound is a one-shot from the trigger table `GWCCues` in `WCEvents.cpp`; whispers stay on a long timer.
- **Frame:** a portrait falls off the hall wall behind him with a hit (`frame_fall`, cue Act 6); picking it up shows the
  scratched-out eyes and plays `d_photos`. The smell line `d_foyer` is back.
- **Book scare (living room, no gating):** tall bookcase on the stair wall, settlers book at his eye height. He must be
  within 30 cm either side and 35 to 115 cm back ("Stand right in front of it."); the game then slides him square to the gap
  and settles his view on it. Her eye is in the hole (she is on the stairs behind that wall), holds 2 s, then she runs up the
  stairs: `step_stairs` from `StairRunA` to `StairRunB`, `her_step` along the landing to `StairRunC`.
- **Props:** loose props dropped onto surfaces by `float_sweep.py` (bottles and plates at the kitchen sink were in mid-air).
- **Edith's skin:** look D, crusted scabs (`SourceArt/Her/look_d`, baked by `Scripts/her/her_tex.py --bake d`); Codex's
  look C face is kept above the jaw line by `portrait_mask.png`.

**Seen in photo checks** (`Saved/spot2` to `spot6`): vent and doll, jewelry box and screwdriver, fuse, shed tape, tipped
trash can, bookcase and prompt, TV cabinet, frame on the wall, Edith with skin D, the eye behind the book.
**Not verified in game by anyone:** the trigger sounds by ear, the new drone, crickets, the frame-fall event firing, tape
playback through `use:tv`, the trash crash sequence and `d_shedcall` timing, every item in Inspect (`chain.ps1 -NoBuild -Inv
Inv6` has never been run), whether a person finds the desk pickups. **No bot playthroughs unless she asks.**

Still open: use Codex's frame photos on the falling frame (kit pieces now); TTS `r_end3` and `m_whyleave` (one attempt
each); yard brightness with moon 26; real-pace run when she allows runs; honest re-score; QA report; menu test; cruiser
Ford badge; packaging only when asked.

**Spend:** Higgsfield 698.75 credits left (250 spent on the television tapes; no more tape spending unless she asks). Nothing
paid was used for the items or the doll. **Helpers:** `Scripts/tools/chain.ps1`, `wc.ps1 game <tag> "<flags>"`,
`commit_push.ps1`. Run the game alone at start-up (starting it while a build, ffmpeg or a bake runs has crashed it).

## Build ID
`elc-0.5-dev`. **No packaged build exists** (Cheyenne asked for no interim package). Nothing below has been played start to
finish by a person. Scores are my own estimate against the rubric; none is 8 except performance.

## What exists
- **Game:** first-person horror in one house. Drive up a forest road, get locked in, search twelve rooms, an attic and a
  cellar, read 26 notes, examine about 55 objects, find three keepsakes and the shears, cut three knots in the root cellar.
  Ten authored scares (S7 is now the slow hand under the bed), hunts announced by her footsteps where the pistol drives her
  off, a long build-up with no sight of her, watchers (eyes in walls, hanging hair, the black silhouette), her drawings, three
  memories shown when she grabs you, an inventory (use, inspect in 3D, drop, papers to re-read), ending and credits.
- **Code (C++ module `WellnessCheck`, no Blueprints):** `WCCharacter` (movement, converging flashlight, pistol, interaction,
  knock-down, the inventory's held-up item), `WCWorld` (doors, notes, pick-ups, examine and use spots, triggers, watchers),
  `WCEntity` (Edith: clips, eye, scream / sneer / brow face keys, footsteps), `WCDirector` + `WCStory.cpp` + `WCHouse.cpp`
  (story, scares, lights, build-up, drive, hunts, grabs, memories), `WCGame` (HUD, menus, inventory, credits), `WCAuto.cpp`
  (test bot, tours, look test).
- **Level:** generated from nothing by `Scripts/level/build_house.py` and its modules. About 2,530 meshes, 426 trees, 415
  decals, 77 lights.
- **Docs:** `Docs/STORY_AND_ENTITY_BIBLE.md`, `Docs/SCARE_MANIFEST.md`, `Docs/ASSET_AND_VOICE_MANIFEST.md`, `Docs/QA_REPORT.md`.

## Evidence (details in `Docs/QA_REPORT.md`)
- **Run 9, real pacing** (`Saved/Logs/auto9.log`): ending reached in 37 min 17 s by a bot that reads and explores nothing
  (a person: about 60 to 80 minutes, estimated); first sight of her at 9 min 4 s; all ten scares; hunts 2 and 3 driven off with
  the pistol in about 10 s each; mean frame 11.0 ms (91 fps), worst 99th-percentile window 28 ms.
- **A game-ending defect found and fixed:** nobody could climb out of the cellar (three ground slabs crossed the stairwell).
  A stair-walking test now passes on every flight, up and down.
- **Look tests** (`Saved/Her5..9/`, `Saved/Grab_*/`): pistol, eye behind the book, the silhouette, the drawings, the hand
  under the bed, the grab (her face level with his, lit, mouth open).
- **Inventory photo test** (`Saved/Inv2/`), **every interactable photographed** (`Saved/Items2/`), **forest drive**
  (`Saved/Drive4/`: road, verges and trunks in the headlights).

## Rubric (my estimate, 2026-11-19 01:30 UTC)
| Category | Weight | Score | Why not higher |
|---|---|---|---|
| Atmosphere | 20% | 7.0 | Forest drive still weak; sound not judged by ear |
| Scares | 15% | 7.0 | Her face in the grab was under-lit (fix written, not yet seen); no person has been scared by it |
| Story and entity | 15% | 7.5 | The memories are tableaux, not acted scenes |
| Visuals, lighting, animation | 15% | 6.5 | Forest; her face motion is subtle; some props are still kit pieces |
| Sound and voice | 15% | 6.5 | Unheard by a person: footsteps, many-voiced lines and the mix are untested by ear |
| Interaction and navigation | 10% | 7.0 | No human play; a few awkward reaches (desk in the sitting room) |
| Performance | 5% | 8.5 | Editor game mode only, no packaged measurement |
| Completeness and delivery | 5% | 3.5 | No package, no real-pace run, no fresh-folder test |
| **Overall** | | **6.8** | |

## Next, in order
1. Recapture the drive and the grab with the fixes; run 9.
2. One run at real pacing for a measured play length (about an hour of machine time).
3. Menu test on this build.
4. When Cheyenne says so: Shipping package and fresh-folder launch.

## Standing rules (from Cheyenne)
Higgsfield is a last resort (about 955 credits left, none spent since 20:13 UTC on the 18th). Use SF3D, Blender, Fab and her
audio library. No interim packaged builds. Keep working without check-ins until every category is 8 or better. Commit locally
as checkpoints.
