"""Writes the pause point into PRODUCTION_STATUS.md (2026-11-18 22:58 UTC)."""
import io
p = "C:/GameDev/Unreal/WellnessCheck/PRODUCTION_STATUS.md"
s = io.open(p, encoding="utf-8").read()
mark = "## Build ID"
block = r'''## PAUSED 2026-11-18 22:58 UTC (Cheyenne left work; laptop offline for about an hour)

Nothing was running when work stopped (no Unreal, Blender or ffmpeg process), and nothing was deleted. Everything is in files on
disk; there is no unsaved editor state. **The C++ source has unbuilt, untested edits (passes 43 to 46), so the game DLL and the
map on disk are still the run-6 build.** Backups of earlier source are in `Saved/old_src/`.

### Resume here, in this order
1. **Finish pass 46 before building** (`Scripts/tools/fix_pass46.py` is applied; these parts are still wrong or missing):
   - `ScareUnderBed` in `WCStory.cpp` assumes a 150 cm reach from her origin. Measured from the rig, in the `Under` clip her
     left wrist is 92 cm forward and 30 cm to her LEFT of the actor origin (fingertips about 110), head front about 30 forward.
     Fix: scale her to 1.25 for this moment only (longer arm, bigger hand; reset before `Vanish`), place her so the wrist stops
     about 16 cm short of the box (use `Body->GetBoneLocation("LeftHand")` with the analytic numbers as fallback), make the box
     follow her as she withdraws, and stop it about 100 cm back (48 cm under the bed edge) so a crouched player can reach it.
   - `build_house.py`: read `RuthBed` bounds after placing it (line ~676) and put `pick_keep_ruth`, `MusicBoxPoint` and
     `Her_Under` relative to the bed's open edge (box about 52 cm out from the edge; `Her_Under` under the bed on the same line).
   - Sound `her_step` does not exist yet. Add `her_step_01..04` to `Scripts/audio/lib_sfx.py`: the only wet hit in the library
     is Sonniss bundle 2 `WOODImpt_Hit Blood Spill Splat Wood Impact Light Hit Squelch Small Thump 03` (several hits in one
     file; cut different ones), pitched down about 0.75, mixed over our own `step_wood_0N` pitched to about 0.6 for weight.
   - `Scripts/her/build_her.py`: add shape keys `Sneer` (upper lip on her left side lifts: z 234.75 to 239, x from mouth
     centre 0.3 out to about +9, front of face y < -14, dz about +2.4) and `Brow` (z 241.6 to 249, |x| < 11, dz about -1.9,
     dy -1.1), right after the Scream block; add them to the `--screamshot` preview. Her eye is at (2.9, -25.1, 240.0).
     The code in `WCEntity.cpp` already drives `Scream`, `Sneer` and `Brow` every tick.
2. Blender: `build_her.py -- <raw.glb> <out_dir> all` (must be `all`), check the preview renders.
3. `python Scripts/audio/lib_sfx.py` (new footsteps). The demonic voice files are already in `SourceArt/Audio/VO`
   (made by `Scripts/audio/demon_vo.py` from clean takes kept in `VO_dry`); they only need importing.
4. Build C++ (`C:\GameDev\Unreal\Setup\unreal.ps1 -Action Build -Project ...\WellnessCheck.uproject`), with no Unreal process running.
5. `Scripts/tools/wc.ps1 import "her,mats,props,extra,audio"`, then `wc.ps1 level` (check `Saved/Logs/level.log` for a Traceback).
6. Look test (`wc.ps1 game look "-WCHerLook ..."`): pistol orientation (yaw 173, unverified), book eye lit, watchers,
   silhouette, drawings on walls, her face moving, the hand under the bed.
7. Full bot run (`-WCAuto -WCFast -WCAutoForce -WCNoDrive`), then the drive capture (`-WCAuto -WCDrive`) to judge the forest,
   then `-WCItems` for floating props (phone, papers on the new tables).
8. Then: real-pace run for play length, menu test, Shipping package and fresh-folder launch, docs, honest scores.

### Queue of Cheyenne's requests and where each stands
| Request | State |
|---|---|
| Her heavy wet footsteps as the warning cue; player creaks | Code written (pass 46), sound files not made, unbuilt |
| Slow hand under the bed replaces the old lunge | Code written (pass 46), reach numbers need the fix above, unbuilt |
| Moving face (jaw, brow, sneer, twitches) | Game code written; `Sneer` and `Brow` shape keys not yet in the model |
| Demonic many-voiced present-day Edith | 18 lines processed; not yet imported or heard in game |
| Three flashbacks on grabs | In the run-6 build; 1 and 2 seen in screenshots, 3 not yet seen; grade toned down (pass 44, unbuilt) |
| The demon silhouette (the Company) | In the run-6 build; not yet seen in a screenshot |
| Her drawings | In the level; not yet checked in a screenshot in game |
| Grabs twice as fast, scream held on her face | In the run-6 build; hunt-catch caption fix is pass 44, unbuilt |
| Floating props, phone stand, papers | Tables and settle pass in the level; `-WCItems` check not yet run |
| Pistol looks like a pistol | Yaw fix is pass 43, unbuilt and unverified; if still wrong, rebuild from her reference #2 with SF3D/Blender |
| Forest polish | Denser trees, saplings, ferns, headlight beams are pass 45; level not rebuilt, not yet seen |
| Ambient laugh, crying, whispers | In the run-6 build; mix not judged by ear |
| Bot route failures (bath 2, sewing room, shears, attic and cellar doors, foyer at dawn) | Open |

Spend today: Higgsfield none since the last-resort rule (about 955 credits left). Google TTS: 13 short lines this evening.

'''
if "## PAUSED 2026-11-18 22:58" not in s:
    assert mark in s
    s = s.replace(mark, block + mark, 1).replace("Updated 2026-11-18 22:35 UTC, session 1, still in progress.", "Updated 2026-11-18 22:58 UTC, session 1, paused (see next section).")
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("status written")
