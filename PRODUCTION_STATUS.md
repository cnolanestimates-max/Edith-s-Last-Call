# Edith's Last Call: production status

(Working title "Wellness Check"; the project folder keeps that name.) Updated 2026-11-19 06:25 UTC, session 1, PAUSED (see the first section).
Engine: UE 5.9.0. Project: `C:\GameDev\Unreal\WellnessCheck`. Git: local repo on `main`, remote
`github.com/cnolanestimates-max/Edith-s-Last-Call` (private). Pushed; checkpoints are pushed as work lands.

## PAUSED 2026-11-19 06:25 UTC (Cheyenne went to bed; resume when she says so)

Everything is committed and pushed. No game or editor process is running. Code builds (last build OK at 06:19 UTC, passes 81
to 90) and the map was rebuilt after the last lighting change. Nothing below has been played by a person yet; Cheyenne will
play-test in the morning.

**Done tonight (03:14 to 06:25 UTC), all at Cheyenne's direction**
- Television in the living room (S13) with three approved tapes (`bedtime8`, `living8`, `porch8`, Seedance 2.5): already on
  when he first comes in; he has to crouch right up to the set to switch it off (nothing happens the first time); it comes on
  again after the head-by-the-ceiling scare, and switching it off then shows her in the dead glass (doorway, then running).
  No camera takeover (she decided against it). Tested with `-WCHerLook -WCTVOnly` (`Saved/TV9`).
- The eye in the dark (S14): total blackout, her eye up by the ceiling down the hall, gone under the flashlight, back when the
  light moves off. Now waits until after the long hall (S3). Tested with `-WCHerLook -WCEyeOnly` (`Saved/Eye5`).
- Record player (S11) and "you left me" (S12): built, never yet seen in a run.
- The Company is black smoke (road, house, memory 3); tree-tunnel forest road with the road shadow.
- Flashlight: 150 lm with a 3.9 m cut-off (was 980 lm, 26 m): about five feet of clear sight. Moonlight through the windows
  cut from 9000 to 2600 lm. She carries a faint cold light (`FarLight`, 320 lm) beyond 2.3 m so the far scares still read;
  Cheyenne said keep it until she has play-tested.
- Reach: a thing must be within about a metre on the floor plan to use it (`InteractReach` 105, trace 190).

**Open, in this order**
1. **The first peek (S1) does not yet leave when the light hits her.** Test `-WCHerLook -WCPeekOnly` (`Saved/peek2`, log
   `Saved/Logs/peek2.log`): at 3.2 m with the light on her she was still there 1.7 s later (`her=1 dist=321`). Look at the peek
   block in `StoryTick` (`WCStory.cpp`, "S1: the peek is watching you back"): `Seen` only counts when the flashlight is on and
   `PlayerSees(head, 0.86, 360)` is true; check whether the look-test bot has its flashlight on, whether the line of sight to
   her head is blocked by the door frame, and whether 360 cm is too short for where the hall lets him stand. Wanted: barely
   visible, only found when already close to the doorway, gone the instant the light is on her. Also look at `Saved/_s/peek2_sheet.jpg`
   to confirm she no longer shows against the hall window from the stairs (the window light is dimmed to 4% during the peek).
   Cheyenne, 06:24 UTC: the peek must vanish FAST, instantly when lit. The cold glow is confirmed: keep it at long distances and
   wherever she has to be seen for a scare to work.
2. **Bot regression run** with the short reach and short flashlight: `chain.ps1 -NoBuild -Run auto13` (fast), then a real-pace
   run (`-Real`) to see S11, S12, S13 and S14 in order and to check that the far scares (long hall, ceiling, hunts) read.
   The 05:52 real-pace run (`auto12`) was stopped at about 15 minutes: it showed the TV as the first scare (now fixed) and
   reached S3.
3. `m_whyleave` voice line still missing (TTS quota, one attempt only); a scream stands in.
4. Docs to bring up to date for the 06:05 changes: scare manifest rows for S1 and S13, QA report, the status sections below
   (they still describe 02:45 UTC).
5. Then: honest re-score against the rubric with run evidence; menu test review; cruiser Ford badge; packaging only when asked.

**Spend tonight:** Higgsfield 948.75 to 698.75 credits (250: Grok Lite attempts 110, stills 20, Seedance 2.5 clips 120).
Cheyenne asked for no more tape spending unless she asks. Google TTS: one line.

**How to resume:** read this section, then `Docs/SCARE_MANIFEST.md`; helpers are `Scripts/tools/chain.ps1` (build, import,
level, tests), `wc.ps1 game <tag> "<flags>"`, `commit_push.ps1`. Run the game alone (starting it while a build, ffmpeg or a
generation is running has crashed it at start-up twice).

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
