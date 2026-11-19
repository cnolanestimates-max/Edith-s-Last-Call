# Edith's Last Call: production status

(Working title "Wellness Check"; the project folder keeps that name.) Updated 2026-11-19 14:50 UTC, in progress.
Engine: UE 5.9.0. Project: `C:\GameDev\Unreal\WellnessCheck`. Git: local repo on `main`, remote
`github.com/cnolanestimates-max/Edith-s-Last-Call` (private). Pushed; checkpoints are pushed as work lands.

## Resumed 2026-11-19 14:18 UTC (Cheyenne is back; she will play-test today)

**Since the pause**
- First peek (S1) fixed and tested (`Saved/peek3`): invisible from the stairs, a glint at 4 m, and once the flashlight is on
  her she pulls back behind the door frame in half a second. Last night's failure was the test (the look test marks the peek
  as already done).
- Whole-game picture filters, one switchable layer (`M_Filter`, `AWCDirector::SetFilter`, `-WCFilter=N`; 1 VHS camcorder,
  2 old film, 3 cold and drained, 4 fisheye bodycam, 5 black-and-white night vision). Before/after sheets sent
  (`Saved/_s/filters_*.jpg`, test `-WCHerLook -WCFilterShots`). **Waiting for her pick**; then make it a menu option.
- The Fab editor plugin updated itself overnight to a build that does not match the installed engine (BuildId 60738873 against
  60351404) and stopped the editor commandlets from starting. It is disabled in `WellnessCheck.uproject` (`"Fab": false`). The
  game does not use it; re-enable it after the engine is updated in the Epic launcher if she wants the in-editor Fab browser.

**Open, in this order**
1. Bot regression run with the short reach and short flashlight (`chain.ps1 -NoBuild -Run auto13`), then a real-pace run
   (`-Real`) to see S11, S12, S13 and S14 in order and check that the far scares read.
2. Put her chosen filter in the game (menu option, saved setting).
3. `m_whyleave` voice line still missing (TTS quota, one attempt only); a scream stands in.
4. Bring the sections below up to date (they still describe 02:45 UTC) and the QA report; honest re-score with run evidence.
5. Menu test review; cruiser Ford badge; packaging only when asked.

**Spend:** Higgsfield 698.75 credits left (250 spent on the television tapes on 2026-11-19; no more tape spending unless she
asks). **Helpers:** `Scripts/tools/chain.ps1`, `wc.ps1 game <tag> "<flags>"`, `commit_push.ps1`. Run the game alone (starting
it while a build, ffmpeg or a generation is running has crashed it at start-up).

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
