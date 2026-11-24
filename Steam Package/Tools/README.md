# Tools that made the store assets

Run with the system Python (Pillow) and ffmpeg on the dev laptop.

- `logo.py <out.png> [width]`: the title lettering (transparent PNG).
- `capsules.py <out dir>`: every capsule size. It reads the two key art paintings from `ka/keyart_wide_1.png` and
  `ka/keyart_vert_1.png` next to it; the clean full-size copies are `../capsules/key_art_wide_clean_3840x2160.jpg` and
  `../capsules/key_art_vertical_clean_3712x4608.jpg` (the original PNGs were 5504x3072 and 3712x4608).
- `cards.py <out dir>`: the trailer's text cards and end title.
- `trailer.py <out.mp4>`: the trailer cut (shot list and sound cues inside). Needs `cards/` and `glimpse.jpg` next to it and the
  recorded frames in `C:\GameDev\Unreal\WellnessCheck\Saved`. See `../trailer/TRAILER_NOTES.md`.
- `float_shots.py <dir>`: the floating-camera moves for `-WCFloat` (and start/end stills for `-WCShotFile`).
- `shots.py <out dir> "name|folder|frame" ...`: exports chosen frames as 1920x1080 screenshots.

The opening capture was recorded with the game's own flags, off-screen:
`UnrealEditor.exe WellnessCheck.uproject /Game/WC/Maps/House -game -resx=1920 -resy=1080 -RenderOffscreen -WCAuto
-WCAutoForce -WCDrive -WCOutside -WCAutoStop=inside -WCVideo=<dir>\video -WCShots=<dir>\shots -UseFixedTimeStep -FPS=30
-ini:GameUserSettings:[WellnessCheck]:Subtitles=False`. At 1080p it runs at about 4 frames a second, so 150 seconds of
game takes about 18 minutes, and the PNGs need converting to JPG as they land (about 3 MB each).
