# Announcement trailer (93 seconds, second cut)

`EdithsLastCall_Trailer_1080p.mp4`: 1920x1080, 30 fps, H.264 about 6.5 Mbps, AAC 256k, -16 LUFS (Git LFS, 64 MB). The
higher-quality master is kept out of git on the dev laptop at
`C:\GameDev\Unreal\WellnessCheck\Saved\SteamPackage\EdithsLastCall_Trailer_master.mp4`; upload that one to Steam.
`thumbnail.jpg` is the dining-room frame (no Edith). Nothing has been uploaded anywhere.

## Why it is cut this way (2026-11-24)

Cheyenne rejected the first cut: it showed Edith five times, gave away the scares, and used an out-of-date take of the
bookshelf scare. This cut follows how comparable Steam trailers are built. Looked at frame by frame: *Visage* (Early Access
teaser: one slow low dolly across a floor of toys to a door, then the title, the monster only in the key art), *MADiSON*
(long slow moves through rooms and props, the threat only as a blur, black, title, Wishlist, a short stinger after the
title), *The Mortuary Assistant* (environment and props, short black cuts, one body shot near the end), *Fears to Fathom:
Home Alone* (the setup told through dialogue over ordinary rooms). The shared pattern: setup, atmosphere, a quickening, at
most a glimpse, black, title, stinger.

## The cut

| Time | Picture | Sound |
|---|---|---|
| 0:00 | Black | The telephone rings twice |
| 0:03 | ASHBY COUNTY / NOVEMBER 9, 1993 | Radio static. Deputy: "Dispatch, Fourteen. I'm out on County Road Nine..." |
| 0:06 | Over the forest, following the cruiser | Dispatch: the welfare check on Edith Harrow, 72, lives alone, family out of state |
| 0:11 | The road in the headlights, the house through the trees | The house score comes in |
| 0:23 | The house | Dispatch: "...said she needs company, and hung up." Deputy: "...Needs company. Copy." |
| 0:33 | Black | A knock |
| 0:35 | Floating: the hall and the stairs | A door creaks. "God, that smell. ...Mrs. Harrow?" |
| 0:40 | The dining table | "Table's set for four. This food's been sitting here for months." |
| 0:46 | Her kitchen, her drawings, the children's room, the prayer room, the attic, the cellar | "Her drawings. The same figure in every one..." / Dispatch: the call came from inside the house / "That phone's cut off at the wall." |
| 1:12 | Quickening: sickroom, den, bedroom, cellar, piano (1 to 0.6 s each) | The stalk drone, thumps, a bulb buzzing, a door slam, a bulb pops |
| 1:17 | One glimpse: her body in a doorway, face out of frame (0.6 s) | A hit, then the music cuts dead |
| 1:18 | Black | Edith: "Nobody comes. Nobody comes to see me anymore." |
| 1:23 | Title, WISHLIST NOW ON STEAM | A hit |
| 1:30 | Black | The phone rings once. Edith: "You came." |

No scares, no ending, no bookshelf, no cellar body.

## Sources

- **Picture:** all from the game. The forest, road and house are the in-game drive, recorded 2026-11-24 (`Saved/steam_open`).
  The interiors are slow floating-camera moves recorded from the current build on 2026-11-24 with `-WCFloat` (WCAuto.cpp;
  the moves are in `Tools/float_shots.py`) and `-WCFloatFill=2500` (a soft warm light carried with the camera so the rooms
  read; the flashlight is on as in play), lifted a little in the edit (gamma 1.28). The one glimpse is the cropped frame
  also used as screenshot 05 (a take from 2026-11-20).
- **Sound:** the game's own files in `SourceArt/Audio` (voice lines, phone, radio, knock, creaks, thumps, bulbs, stings).
- **Music:** `music_house` (edited excerpts of "Apprehension" by Kevin MacLeod, incompetech.com, CC BY 4.0, and "She's
  Watching Me" by Darren Curtis, darrencurtismusic.com, used with the composer's permission) and `music_stalk`
  (InMotionAudio "The Death Whistle", Sonniss GDC bundle, royalty-free).

**Credit line for the trailer's description on Steam/YouTube (required by CC BY):**

> Music: "Apprehension" by Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0
> (creativecommons.org/licenses/by/4.0). "She's Watching Me" by Darren Curtis (darrencurtismusic.com).

## Rebuilding it

1. `python Tools/float_shots.py Saved/trailer2` writes the move list.
2. With nothing else in Unreal: `UnrealEditor.exe WellnessCheck.uproject /Game/WC/Maps/House -game -RenderOffscreen
   -resx=1920 -resy=1080 -UseFixedTimeStep -FPS=30 -WCAuto -WCFloat=Saved/trailer2/float.txt -WCFloatFill=2500
   -WCShots=Saved/trailer2/video -ini:GameUserSettings:[WellnessCheck]:Subtitles=False` (about 15 minutes; ~3 MB a frame).
3. `python Tools/trailer.py <out.mp4>` (needs `cards/` and `glimpse.jpg` next to it).

## Worth doing before launch

- A version with burned-in subtitles (most store trailers play muted), and a 30-second cut for social posts.
- Re-record the house exterior without the lit window if the window is meant to be dark on arrival.
