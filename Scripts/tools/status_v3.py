"""Rewrites PRODUCTION_STATUS.md (2026-11-19 early morning UTC)."""
import io
TEXT = r'''# Edith's Last Call: production status

(Working title "Wellness Check"; the project folder keeps that name.) Updated 2026-11-19 01:30 UTC, session 1, in progress.
Engine: UE 5.9.0. Project: `C:\GameDev\Unreal\WellnessCheck`. Git: local repo on `main`, remote
`github.com/cnolanestimates-max/Edith-s-Last-Call` (private). **The first push has to be run by Cheyenne**
(`git -C C:/GameDev/Unreal/WellnessCheck push -u origin main`): pushes from this session are blocked by the safety check.

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
- **Run 8** (`Saved/Logs/auto8.log`, `Saved/Auto8/`, accelerated pacing): all ten scares in order, three memories, ending and
  credits reached; mean frame 12.4 ms (81 fps), worst 99th-percentile window 46 ms, in the editor's `-game` mode at 1280x720.
  The hand under the bed was photographed by the run itself from across the room. Six bot failures forced past, listed in
  the QA report with causes; fixes for five are written and go into the next run.
- **Look tests** (`Saved/Her5..7/`): pistol, eye behind the book, the silhouette, the drawings, the hand under the bed.
- **Inventory photo test** (`Saved/Inv2/`): list, inspect, papers.
- **Forest drive capture** (`Saved/Drive2/`): trunks in the headlights, but the road itself was black and the gauge glow was
  a green slab. Fix written (a road wash light, small gauge marks); recapture pending.

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
'''
io.open("C:/GameDev/Unreal/WellnessCheck/PRODUCTION_STATUS.md", "w", encoding="utf-8", newline="\n").write(TEXT.lstrip("\n"))
print("status rewritten")
