# Announcement trailer (70 seconds)

`EdithsLastCall_Trailer_1080p.mp4`: 1920x1080, 30 fps, H.264 about 6 Mbps, AAC 256k, -16 LUFS. This is the copy in git
(Git LFS, 51 MB). The higher-quality master (CRF 17, 284 MB) is kept out of git on the dev laptop at
`C:\GameDev\Unreal\WellnessCheck\Saved\SteamPackage\EdithsLastCall_Trailer_master.mp4`; upload that one to Steam.

Nothing has been uploaded anywhere. Nobody has watched it with sound yet: please listen once on headphones and once on the
laptop speakers before it goes up.

## The cut

| Time | Picture | Sound |
|---|---|---|
| 0:00 | Black | A telephone rings twice |
| 0:03 | Card: ASHBY COUNTY / NOVEMBER 9, 1993 | Radio static; the house music fades in |
| 0:07 | Over the forest, following the cruiser (the game's own title appears) | Dispatch: the welfare check on Edith Harrow |
| 0:12 | The road in the headlights | |
| 0:19 | The house comes out of the trees | Dispatch: "...said she needs company, and hung up." |
| 0:25 | The house | Deputy: "...Needs company. Copy." |
| 0:28 | Card: A WELFARE CHECK. / TEN MINUTES. | A knock |
| 0:31 | The long hall, a figure under the lamp | Deputy: "Cord's cut clean through..." |
| 0:36 | The eye behind the settlers' book | Dispatch: "It came from Mrs. Harrow's own telephone. From inside that house." |
| 0:40 | The bathroom door, and her in it | A swell |
| 0:43 | Black | |
| 0:46 | Card: SHE HAS BEEN WAITING / A LONG TIME FOR COMPANY | The stalk drone comes in |
| 0:50 | Her on the ceiling | Heavy thumps |
| 0:53 | Round the door frame in the moonlight | |
| 0:55 | She lunges | Braam and her scream, then everything cuts |
| 0:58 | Black | Edith whispers "Stay." The phone rings once. "Sit down. Supper's getting cold." |
| 1:02 | Title, WISHLIST NOW ON STEAM | A hit, then silence |

No ending, no cellar, no knots.

## Sources

- **Picture:** every shot is a frame the game rendered, recorded frame by frame at 30 fps with the HUD off. The forest,
  road and house were captured for this trailer on 2026-11-24 (`Saved/steam_open`, `-WCVideo` at 1920x1080, subtitles off).
  The interior shots come from earlier recorded takes in `Saved` (HallLightScareRec, SettlersTake2, BathChairFinal,
  Corner24Work, Moon64, MoonFront); the three at 1152x648 are upscaled. Text cards and the end title were added in the edit.
- **Sound:** the game's own files from `SourceArt/Audio` (voice lines, phone ring, radio static, knock, thumps, stings, scream),
  mixed in the edit, since frame-by-frame captures have no usable sound.
- **Music:** `music_house` (edited excerpts of "Apprehension" by Kevin MacLeod, incompetech.com, CC BY 4.0, and "She's
  Watching Me" by Darren Curtis, darrencurtismusic.com, used with the composer's permission) and `music_stalk`
  (InMotionAudio "The Death Whistle", Sonniss GDC bundle, royalty-free).

**Credit line for the trailer's description on Steam/YouTube (required by CC BY):**

> Music: "Apprehension" by Kevin MacLeod (incompetech.com), licensed under Creative Commons: By Attribution 4.0
> (creativecommons.org/licenses/by/4.0). "She's Watching Me" by Darren Curtis (darrencurtismusic.com).

## Rebuilding it

`Tools/trailer.py <out.mp4>` re-cuts it from the frames in `Saved` (edit the shot list and the cue list at the top), using
the cards made by `Tools/cards.py`. To free disk space, the opening capture was trimmed to its first 1,800
frames (the drive and the house, which is all the cut uses); the yard, shed and front door part was deleted and would
need a new capture.

## Worth doing before launch

- Re-record the interior shots from the current build at 1080p (the takes are from 2026-11-20 and 21), and add a shot of the
  kitchen table set for four and the cut phone cord, which the narration mentions but the picture doesn't show.
- A 30 second cut for social posts, and a version with burned-in subtitles (most people watch store trailers muted).
