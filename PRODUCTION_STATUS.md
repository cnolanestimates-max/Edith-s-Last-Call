# Edith's Last Call: production status

(Working title "Wellness Check"; the project folder keeps that name.) Updated 2026-11-19 22:00 UTC. Handoff to Codex below.
Engine: UE 5.9.0. Project: `C:\GameDev\Unreal\WellnessCheck`. Git: local repo on `main`, remote
`github.com/cnolanestimates-max/Edith-s-Last-Call` (private). Pushed; checkpoints are pushed as work lands.

## HANDOFF 2026-11-19 22:00 UTC (Claude stopped at Cheyenne's request; Codex continues)

**Everything below is committed and pushed.** Read `Docs/TIMELINE.md` before adding anything with a date on it.

Done this evening (all in the build; details further down and in `Scripts/tools/fix_pass126.py` to `fix_pass130.py`):
- Crash a second after the cruiser stops: fixed (dust and flies no longer rebuild their ISM proxy every frame).
- Opening as Cheyenne laid it out: knock, "It's locked ... check around the side", shed tape (it can be taken now), the
  big wheeled bin goes over with 44 pieces of rubbish, loud crash, steps running off, deputy terrified, back to the front,
  "can you please open up?" and the door opens on those words. Check run: `wc.ps1 game yardN "-WCAuto -WCAutoForce -WCDrive
  -WCOutside -WCSndLog -WCAutoStop=inside -WCShots=..."` (it quits on purpose six seconds after he is inside).
- 1993 timeline on notes.json and looks.py; dispatch lines re-voiced ("welfare check", "her own telephone", seventy-two).
- Twenty face keys on Edith, nine faces; drone opening shot; book scare on the stair wall.

**Unverified by ear (nobody has listened): tell Cheyenne, do not claim.**
- **ENGINE: FIRST THING TO FIX (Cheyenne, 22:03 UTC: the synthesized tone was "awful ... that's not it").** What is in
  the build now is the real car-interior recording that was there before today (InMotionAudio "Car Interior Driving
  Ambience", `SourceArt/Audio_unused/amb_car_old.wav`), lifted from -25 to about -18 LUFS with a mid-range push. It is a
  stopgap: a modern car's hum, not a 1990s V8. `Scripts/audio/make_engine.py` is the rejected synthesis; do not run it.
  **Wanted:** a real recorded sedan or V8 idle and cruise, smooth, with body between 150 Hz and 1.5 kHz (her laptop
  speakers play nothing below about 200 Hz), no exhaust pops. Searched so far, all in her library
  (`OneDrive/Documents/ChatGPT/forklight-tts`): Sonniss bundle 3 has the InMotionAudio car interiors
  (`VEHCar_TownDrivingAmbience06` and `13`); bundle 5 has SoundBits "Cars - Mad Mustang Mercury"
  (`VEHCar_Various Driving at Slow Speed 15 06`: rejected, all exhaust crackle on small speakers) and motorcycles; bundle 1
  has only car foley; the other zips have nothing but a siren. The Fab inventory lists no vehicle audio: look on Fab for a
  free car or truck engine pack (she asked), or ask her to pick one. In game the engine is full over the drone shot and
  0.30 in the cab (`TickDrive`), off on arrival.
- **Night bed (22:12 UTC, quick fix at her request, unheard):** `amb_night.wav` is now the synthesized cricket bed at the
  front with the old bed (the one with birds, kept as `Audio_unused/amb_night_birds.wav`) sixteen decibels under it, at the
  same loudness as before (-27 LUFS). If birds are still too present, drop the `volume=0.16` on the old bed; if the
  crickets sound thin, a real cricket and cicada recording is still wanted.
- Fly buzz: now loops, with its own attenuation (silent beyond about nine metres). Before that, sixteen swarms at the
  shared attenuation's floor were audible as crackle over the opening.
- Deputy lines re-levelled to -16 LUFS with a presence lift (`gen_vo.py`, the plain branch) and played at 1.0: his first
  lines were "low as hell" on her speakers.
- Trash crash is -9 LUFS (2D at 1.0 plus positional at 0.45).

**Not done / open:**
- Photographs in frames (Codex): give them dates from `Docs/TIMELINE.md`. The falling frame still uses kit pieces.
- The Inspect photo check (`chain.ps1 -NoBuild -Inv Inv6`) has never been run. Desk pick-ups in the den unconfirmed by a person.
- The second knock replays nothing now, but `d_knock` and `d_openup` both begin with a knock sound; fine unless she objects.
- `m_whyleave` TTS (one attempt only), real-pace run, re-score, QA report, menu test, cruiser Ford badge, packaging (only when asked).
- The upright bin is `SM_Item_BigBin`; if she wants more or nastier rubbish, add to `Scripts/art/trash_models.py` and the
  `_spill` list in `exterior.py`, then `chain.ps1 -NoBuild -Steps items -Level`.

**Rules that bit today:** her screen shows every test run (say so first; the bot's shortcut looked like cut content);
never build or launch while `UnrealEditor*` is running; judge sound for laptop speakers; Blender needs absolute paths.

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

- **Edith's face (passes 119 to 120):** twenty shape keys built in `Scripts/her/build_her.py` (Scream, Sneer, Brow, BrowUp,
  BrowKnit, BrowDown, EyeWide, Squint, Snarl, SneerR, Grin, Frown, JawSide, Pucker, CheekSuck, Stretch, Unhinge, CheekL,
  CheekR, CheekRaise). The eye-side keys are measured from the game's eye (`WCEntity.h` EyeRef 6.0, 21.9, 246.6, radius 4.3);
  `her_info.json`'s "eye_centre" is on her nose and must not be used. Nine faces in `WCEntity.cpp` (`FaceMoods`: rest, watch,
  grin, snarl, rage, scream, wince, grief, hush), one per clip, `SetMood(name, seconds)`, random twitches, lip shapes when
  she talks; the scream (Scream + Unhinge + Stretch) mixes in by `SetScream`. Previews: `blender ... build_her.py -- <glb>
  <abs out dir> --faceshot` (sheets `Saved/_s/face_keys.jpg`, `face_moods.jpg`); in game `-WCHerLook -WCFaceOnly`.
  Use absolute paths with Blender here: a relative out dir lands in `C:\SourceArt`.
- **Opening shot from the air (passes 121 to 123):** for the first 18 s of the drive the camera is high over the forest
  following the cruiser, then comes down a curve and into the seat (`TickDrive`, `bAir`, `AirIntoCar`). Moon, sky and
  headlights are raised while it is high. Flags: `-WCNoAir`, `-WCAirOnly`, `-WCAirHi= -WCAirLo= -WCAirFov= -WCAirHead=
  -WCAirMoon= -WCAirSky= -WCAirWood=<n>` (extra instanced trees either side; off, it cost the frame rate). The forest is
  only planted along the road and is culled at 100 m (`forest_meshes.py`); the cull is lifted while the camera is in the air.
  Photo check: `wc.ps1 game air1 "-WCAuto -WCAutoForce -WCDrive -WCDriveOnly -WCAirOnly -WCShots=..."`.

- **Crash after the drive (pass 126):** the dust motes (`WCCharacter::TickDust`) and the flies (`TickFlies`) called
  `UpdateInstanceTransform(..., bMarkRenderStateDirty = true)`, which rebuilds the whole ISM proxy every frame; the engine
  asserted (`InstanceDataSceneProxy.h:400`) when an instance update was still in flight. **Never pass that flag for
  per-frame instance moves.** Stack recovered with `scratchpad/crash/sym.py`-style export lookup (no engine PDBs here).
- **Pick-ups win over descriptions (pass 128):** a `AWCLook` box no longer blocks a pick-up or usable behind it (the shed
  tape could not be taken). Check runs: `-WCOutside` (knock, shed, tape, bin, door), `-WCAutoStop=<flag>`.
  **Her screen shows my check runs**: she took the bot's shortcut for cut content. Say so before running one.
- **Opening as she laid it out (pass 129):** knock (`d_knock`), "It's locked ... check around the side" (`d_side`), shed
  tape, the bin goes over (`trash_crash` at -9 LUFS, 2D and at `TrashPoint`, shake, `her_step` running to `TrashRunTo`,
  `d_shedcall` terrified), back at the front `d_openup` and the door opens on its last words, then `d_dooropen`.
- **The bin and the trash:** `Scripts/art/trash_models.py` (exec'd by `build_items_fine.py`): BigBin (full, lid thrown
  back), BigBinDown, and twelve kinds of rubbish; 44 pieces fanned out in `exterior.py` plus kit props. Flies at the bin
  and at every toilet and sink; `flies_buzz` now loops (it was silent after six seconds).
- **Engine:** `Scripts/audio/make_engine.py`: a real V8 at low speed (SoundBits "Mad Mustang Mercury", Sonniss bundle 5,
  royalty-free), -15 LUFS, 100 s loop; old file in `Audio_unused/amb_car_old.wav`.
- **1990s:** the night is Tuesday, November 9, 1993. All dates are in `Docs/TIMELINE.md` (the single source: notes.json,
  looks.py, and any dated photograph must fit it). Dispatch says "welfare check" and "her own telephone"; Edith is 72.

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
