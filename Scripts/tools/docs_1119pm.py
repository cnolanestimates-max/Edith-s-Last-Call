"""Bring the status file and the scare manifest up to the afternoon of 2026-11-19 (fetch chain, doll, items, outside)."""
R = "C:/GameDev/Unreal/WellnessCheck/"
p = R + "PRODUCTION_STATUS.md"
s = open(p, encoding="utf-8").read()
a = s.index("## Resumed 2026-11-19 14:18 UTC")
b = s.index("## Build ID")
new = '''## State 2026-11-19 16:45 UTC (Cheyenne play-tested today and is directing live)

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

**Open, in this order**
1. Read bot run auto15 (new chain: `WCVENT`, `WCDOLL`, `WCTHUMP`, then everything to the ending) and fix what it shows.
2. Inventory photo test of every item in Inspect (`chain.ps1 -Inv Inv6`), second pass on the item models, her feedback on the sheet.
3. Back yard too dark at night (`Saved/Out2`): pass 104 (tree line casts no shadow, moon 26) is written, not tested.
4. Edith's skin: she was sent previews A to D (`Saved/_s/edith_skin_previews.jpg`); bake and import the one she picks.
5. Desk pickups: the bot could not focus the key ring and cartridges in the roll-top desk (auto14); check a person can.
6. TTS still missing: `r_end3` new dispatcher take, `m_whyleave` (quota; one attempt each).
7. Real-pace run for scare spacing; honest re-score; QA report; menu test; cruiser Ford badge; packaging only when asked.

**Spend:** Higgsfield 698.75 credits left (250 spent on the television tapes; no more tape spending unless she asks). Nothing
paid was used for the items or the doll. **Helpers:** `Scripts/tools/chain.ps1`, `wc.ps1 game <tag> "<flags>"`,
`commit_push.ps1`. Run the game alone at start-up (starting it while a build, ffmpeg or a bake runs has crashed it).

'''
s = s[:a] + new + s[b:]
s = s.replace("Updated 2026-11-19 14:50 UTC, in progress.", "Updated 2026-11-19 16:45 UTC, in progress.")
open(p, "w", encoding="utf-8", newline="\n").write(s)

p = R + "Docs/SCARE_MANIFEST.md"
s = open(p, encoding="utf-8").read()
if "## Changes 2026-11-19 afternoon" not in s:
    s += '''

## Changes 2026-11-19 afternoon (Cheyenne's play-test and design notes)
- **S1 is gated by the player, not a clock.** Chain: kitchen vent (screwed shut) -> screwdriver in the master bedroom ->
  rag doll behind the vent -> Inspect, turn her over, E: the small key -> heavy thump upstairs 6 s later (`UpstairsThump`,
  log `WCTHUMP`) -> the walk up, S1 at the master doorway -> jewelry box: Ruth's letter, the glass eye.
- **S8 (ending) has a last beat:** after "STAY!" and black the dark lifts; putting her glass eye back releases her
  ("...thank you."), then dawn. The eye is required with the three keepsakes; the cellar door unbolts if anything is missing.
- **Before the house:** knock, no answer, look round the back (shed, locked back door), then the front door opens. No scare.
- **Removed:** the smoke figure on the road; the hair drawn up into the ceiling (watchers are the eight eyes only).
- **New house event:** a door opens by itself with its creak, twice at most, never over another event (`DoorOpensByItself`).
- **Call-outs:** he calls to her three times while he looks round, before the thump.
- **After S2 (phone):** a drawer scrapes open upstairs (bathroom) instead of the kitchen drawer; the brass key is there.
- **Lights after S3:** the spare fuse is in her locked sitting room, so the house stays dark through S2 until then.
- **S10 (book):** the shelf of county histories is in the living room now; the desk it opens is in the den.
- **After any grab memory** the picture fades back in by itself (it used to stay black until the next event).
'''
    open(p, "w", encoding="utf-8", newline="\n").write(s)
print("docs updated")
