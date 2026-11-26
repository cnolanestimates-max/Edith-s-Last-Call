# Audio pass 2 (2026-11-25): sources of the rebuilt sounds

Append this section to `SourceArt/Audio/AUDIO_CREDITS.md` when the pass is applied. Every recipe is in
`Scripts/audio/pass2_build.py`; library recordings are listed in `Scripts/audio/pass2_sources.py`. Nothing in this pass
needs a credit line: all added material is from the Sonniss GDC 2026 Game Audio Bundle (royalty-free, no attribution
required) or is CC0. The music credits already listed for `music_house` still apply (its approved core is unchanged).

## Stings (stereo)

- `sting_hit`: Epic Stock Media *Halloween Game* (Gore Designed Transient Heavy Impact Smash 01), InMotionAudio *Sinister
  Textures 4* (NoiseBoxHit 36), Effective Trailer *Booms Vol. 2* (011), 344 Audio *Bass Drops and Downers Vol. 3* (Jump
  Start Drop 3) and *Medieval Weapons Vol. 2* (Spear And Stick Impact), Epic Stock Media *HD Game Materials* (Dry Ice High
  Metal Squeal Groan 13).
- `sting_low`: 344 Audio *Bass Drops & Downers* (Slow 10), *Cinematic Horn Braam* 32 (bundle 3), The Noisery *Moaning
  Metal* (Metal Scrape Low Tonal LFE 4), Effective Trailer *Booms Vol. 2* (075).
- `sting_rise`: Effective Trailer *Booms Vol. 2* (214, reversed), InMotionAudio *Sinister Textures 4* (NoiseBoxHit 10
  reversed, 36), The Noisery *Moaning Metal* (Designed Metal Bowed Screech Tonal Reverb 7), *Psycho Glitched Screechy
  Tones Noise* (bundle 2), the same smash as `sting_hit`, 344 Audio *Bass Drops & Downers* (Medium 04).
- `sting_soft`: The Noisery *Moaning Metal* (Bowed Screech 7), *magic, drone, tension, spellbound, evanescence-002*
  (bundle 2), the dry-ice squeal above.
- `sting_braam`: the existing braam plus *Cinematic Horn Braam* 67 (bundle 3). `sting_swell`: the existing file, remastered.

## The wheelchair in the bath

- `wheel_on_boards`: the earlier procedural rumble plus Epic Stock Media *HD Game Materials* (Wood Shaker Microphone Head
  Roll Table), 344 Audio *Christmas* (Sleigh Movement, Pulling) and Kenney impact sounds (impactWood light, CC0).
- `wheel_axle_rub`: 344 Audio *Cinema Experience* (Sitting Down, Creaky Seat, Squeaks 3) and the dry-ice squeal.
- `wheel_baseboard`, `wheel_sidefall`: the earlier impacts plus 344 Audio *Medieval Weapons Vol. 2* (stick impact; Metal
  Shield Spin On Floor), *Haunting Ambiences Vol. 3* (Wooden Hit, Dark, Heavy Hit), InMotionAudio *Sinister Textures 5*
  (Concrete MetalPipe 02), Kenney impactWood heavy and impactMetal heavy (CC0).

## Pistol, doors, falls

- `gun_shot`: the loudest click of the earlier generated shot, *Fireworks, powerful explosions, multiples in a row, near*
  (bundle 3), 344 Audio *Cinematic Fight Vol. 1* (4 x Punch, Body 02) and the stick impact. `gun_empty`: plus Epic Stock
  Media *HD Lo-Fi Mechanics* (Click Deep Mechanism Latch Thunk 02).
- `door_close_01`, `door_locked_01`, `door_unlock`, `door_slam`, `switch_click`: the earlier generated sounds plus Kenney
  impactWood (CC0), InMotionAudio *Instrument Case* (Case Closed 06), 344 Audio *Antiques - Luggage* (Suitcase Being
  Locked; Opening and Closing), *Antique Small Metals* (Tinkering Antique Lock), *Haunting Ambiences Vol. 3* (Wooden Hit)
  and the latch thunk. `door_far_01..03` are the new close, creak and slam heard through a wall.
- `car_door`, `body_fall`: plus the body punch above. `knock`: plus Kenney impactWood medium (CC0).
- `phone_pickup`: plus 344 Audio *Antiques - Telephone* (Pick Up & Drop Ear Piece).
- `bulb_die`, `bulb_pop`: the earlier sounds plus InMotionAudio *Arc* (ArcDesign 15, Buzz 27) and Kenney impactGlass
  light and impactSoft medium (CC0).

## Footsteps

- `step_wood_01..05`, `step_stairs_01..02`: the Kenney wood steps already credited plus *Boots Stomping Footsteps on
  Wooden Floor 37* (sfxmint, CC0 1.0, https://sfxmint.com/sounds/footsteps-wood-37).
- `step_gravel_01..04`: the Kenney grass steps already credited plus Kenney footstep snow (CC0) and Joseph Sardin, *Steps
  on the Twigs* (BigSoundBank 1301, CC0).
- `step_stone_01..04`: the Kenney concrete steps with a short room.

## Remastered only (no new material)

`gun_reload`, `bullet_impact_01`, `door_open_01`, `door_creak_long`, `trunk_open`, `knock_far_*`, `thump_far_*`,
`thump_heavy`, `bang_far_01`, `wood_hit_far_01`, `steps_above_*`, `ceiling_thump_*`, `ceiling_boot_step_*`,
`shelf_stair_step_*`, `her_step_*`, `frame_fall`, `creak_*`, `house_groan_*`, `drag_floor`, `shelf_scrape`,
`chair_scrape`, `chair_creak_01`, `scratch_wall_*`, `bath_drain`, `wind_gust_*`, `bulb_buzz`, `flashlight_click`,
`pickup`, `paper`, `phone_ring`, `music_drone`, `amb_cellar`. Low content gained harmonics a laptop speaker can play;
levels were made consistent.

## Loops

- `music_house`: the approved 162 s piece (Apprehension, Kevin MacLeod, CC BY 4.0; She's Watching Me, Darren Curtis) is
  the unchanged core. Added around it: six slow waves of The Noisery *Moaning Metal* (Bowed Screech 7) at different
  pitches, the *spellbound* tension drone on a slow breathing cycle, and *Dark Industrial Ambience* (bundle 2) as a floor.
- `music_stalk`: the same death-whistle drone, doubled one, two and three octaves up.

## Not touched

Edith's screams, whispers, moans and breathing, the deputy's breathing, every voice line, crickets and crows, the music
box, record, television, clock, bell, flashlight shake and smack, `scare_bump` / `scare_left_bump`, `trash_can_fall`.
