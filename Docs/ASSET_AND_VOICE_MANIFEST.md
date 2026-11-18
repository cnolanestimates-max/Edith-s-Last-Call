# Edith's Last Call: asset and voice manifest

Updated 2026-11-18. Everything in the game and where it came from. "Generated" means made for this game with a paid service on
Cheyenne's own accounts; "Fab" means claimed free on her Fab account (Fab Standard License: commercial use allowed, no credit
required); "Library" means her own Forklight audio library on OneDrive (files are copied, never moved).

## Characters

| Asset | Source | Notes |
|---|---|---|
| Edith (`/Game/WC/Her/SK_Her`, 24 bones, 148k vertices) | Generated: concept image (Higgsfield nano_banana_pro), rigged model (Higgsfield Meshy 7 image-to-3D). Raw: `SourceArt/Her/her_meshy_raw.glb`. | All motion is hand-built in Blender by `Scripts/her/build_her.py`: 10 clips (Idle, Walk, Run, Peek, Rise, Tall, Crawl, Sit, Under, Lunge). |
| Her eye | Built in engine (`WCEntity.cpp`): black ball, thin pale iris, pupil; turns to follow the player. | Cheyenne's direction: no white at all. |
| Her scream | Blender shape key `Scream` (`build_her.py`): the jaw drops 11.5 cm from the lip line, the gap is hollowed and painted black. | No paid generation. Driven automatically by the Run, Lunge, Rise and Crawl clips. |
| Watchers (`AWCWatcher`) | Built in engine: the same eye in wall holes; hanks of hair made of 46 thin strands. | 8 eyes, 5 hanks, 1 scripted eye behind the settlers book. |
| Deputy's hands (`SM_HandPistol`, `SM_HandFlashlight`) | Generated: image (Higgsfield) to 3D (Hunyuan 3D v3). | Glove, pistol, flashlight. |

## Environment

| Asset | Source | Notes |
|---|---|---|
| Horror House Kit, Full Modular (557 meshes) | Fab | Walls, doors, furniture, props. Its flat-colour materials are replaced by our textured ones (`Scripts/level/overrides.json`, 124 slots). |
| 35 decay surface texture sets, 16 grime decals | Generated (Higgsfield seedream), `Scripts/art/gen_textures.py` | World-aligned master material `M_Surface` with a grime mask and per-storey dirt bands. |
| Megascans surfaces and derelict props (plaster, rotten wood, tiles, stove, oven, bathtubs, sinks, mattress, couch, rags, bookshelf, fireplace, cans, debris) | Fab (Quixel Megascans) | List with listing ids: `Saved/fab/_installed.json`. |
| Old West VOL.1, Interior Furniture (beds, desks, dressers, cabinets, washstand, work table) | Fab (Dekogon) | `/Game/OldWest`. |
| Megaplants: Baltic Pine, Baltic Pine Saplings, Dead Pine, Bracken Fern | Fab (Quixel) | The forest road. Placed as static, unskinned-cost trees (`forest.py`, `lean_skel`). |
| Vintage Radio | Fab | Walter's radio and Daniel's radio. |
| Sheriff's cruiser (`SM_Cruiser`), fridge, toilet | Generated: image to 3D (Higgsfield). | **Before release: the cruiser image has a Ford badge; paint it out or replace the car.** |
| The house itself, the exterior, porch, stairs, road, cabin of the cruiser, light fixtures, switches, fuse box, bookshelf | Built by script from boxes, cylinders and kit pieces: `Scripts/level/build_house.py`, `exterior.py`, `ell.py`, `forest.py`, `switches.py`, `watchers.py`, `decay.py`, `lighting.py`, `looks.py`, `settle.py`, `nav.py`. | Re-running `build_house.py` rebuilds the whole map from nothing. |

## Audio

| Group | Source | Notes |
|---|---|---|
| 74 dialogue lines | Generated: Google Gemini TTS (`Scripts/audio/gen_vo.py`); voices algenib (deputy), kore (dispatch), gacrux (Edith). | Radio and phone treatment: Cheyenne's Forklight Voice Effects v1. Line table and ids: `WCStory.cpp`; manifest: `SourceArt/Audio/VO/_manifest.json`. |
| 55 effects and ambiences (screams, breath, creaks, doors, phone, music box, stings, room tones) | Generated: Higgsfield Mirelo text-to-audio (`Scripts/audio/gen_sfx.py`). | Job ids in `SourceArt/Audio/raw/_jobs.json`. |
| 43 effects and beds (nail scratches, skittering, chimney wind, car interior, light switch, bulb buzz and pop, fridge hum, radio tuning, creaky seat, her flinch and hurt, stalk drone, low bed, stings, far doors, steps overhead) | Library: Sonniss GDC 2026 Game Audio Bundle and the Night Shift package (`Scripts/audio/lib_sfx.py`). | Royalty-free, commercial use, no attribution required. Each file's origin is listed in `SourceArt/Audio/AUDIO_CREDITS.md`. No credits spent. |
| Footsteps, clicks | Library: Kenney (CC0). | |
| Music: "Long Note Four", "Ossuary 6 - Air", "Gathering Darkness" (Kevin MacLeod), "Sanctuary" (Scott Buckley) | Library. CC BY 4.0. | **Credit is required and is in the in-game credits.** |

## Writing

24 readable notes (`Scripts/level/notes.json`), about 55 examine lines (`Scripts/level/looks.py`), all dialogue and on-screen
thoughts (`WCStory.cpp`, `WCHouse.cpp`): written for this game.

## Spend

Higgsfield: started the day at 1,206.5 credits; about 955 left when Cheyenne asked for it to become a last resort (20:13 UTC).
Nothing has been spent on Higgsfield since. Google TTS since then: 2 short lines (the deputy's two re-written radio lines).

## To check before a Steam release

1. The Ford badge on the generated cruiser.
2. Kevin MacLeod / Scott Buckley credits must stay in the credits roll (they are).
3. Fab Standard License covers shipping these assets inside a game; do not redistribute the source assets.
4. The Sonniss GDC bundle licence text is inside each bundle zip in the Forklight library; keep a copy with the project records.
