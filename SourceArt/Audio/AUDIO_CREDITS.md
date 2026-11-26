# Wellness Check: audio sources

## Generated
Sound effects and ambiences named below were generated for this game with Higgsfield (Mirelo text-to-audio) on Cheyenne's paid plan; job ids are in raw/_jobs.json.

amb_cellar, amb_house, amb_night, body_fall, bulb_die, bullet_impact_01, car_door, chair_scrape, crawl_knocks, creak_01, creak_02, creak_03, creak_04, cut_rope, door_close_01, door_creak_long, door_locked_01, door_open_01, door_slam, door_unlock, drag_floor, flies_buzz, gun_empty, gun_reload, gun_shot, her_breath, her_scream_01, her_scream_02, her_scream_03, her_scream_short_01, her_scream_short_02, house_groan_01, house_groan_02, knock, knock_far_01, knock_far_02, musicbox, paper, phone_pickup, phone_ring, pickup, radio_click, radio_static, shelf_scrape, sting_hit, sting_low, sting_rise, sting_soft, thump_far_01, thump_far_02, thump_heavy, trunk_open, whisper_far_01, whisper_far_02

## Kenney (CC0 1.0), from the Open Game SFX library

- step_wood_01: Impacts and Footsteps/footstep wood 000.wav
- step_wood_02: Impacts and Footsteps/footstep wood 001.wav
- step_wood_03: Impacts and Footsteps/footstep wood 002.wav
- step_wood_04: Impacts and Footsteps/footstep wood 003.wav
- step_wood_05: Impacts and Footsteps/footstep wood 004.wav
- step_gravel_01: Impacts and Footsteps/footstep grass 000.wav
- step_gravel_02: Impacts and Footsteps/footstep grass 001.wav
- step_gravel_03: Impacts and Footsteps/footstep grass 002.wav
- step_gravel_04: Impacts and Footsteps/footstep grass 003.wav
- step_stone_01: Impacts and Footsteps/footstep concrete 000.wav
- step_stone_02: Impacts and Footsteps/footstep concrete 001.wav
- step_stone_03: Impacts and Footsteps/footstep concrete 002.wav
- step_stone_04: Impacts and Footsteps/footstep concrete 003.wav
- step_stairs_01: Impacts and Footsteps/footstep wood 001.wav
- step_stairs_02: Impacts and Footsteps/footstep wood 003.wav
- ui_tick: Interface/click 002.wav
- flashlight_click: Interface/switch 002.wav

## Yard crows

The four `yard_caw` one-shots are separate calls from Mish7913’s 2018 field recording. Each was trimmed, filtered and level-matched for the exterior perches. [Hooded Crow: Panic Cawing](https://freesound.org/people/Mish7913/sounds/741365/) · [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)

## Deputy breathing

Joseph Sardin recorded both breathing takes. The resting take uses 14.8–25.8 seconds of *Man Breathing*. The faster take uses 4.1–12.5 seconds of *Breathless Man*. Both recordings are CC0. The audition excerpts are in `FieldRecordings`. `Scripts/audio/make_deputy_breaths.py` cuts the six gameplay cues at natural pauses. [Man Breathing](https://bigsoundbank.com/man-breathing-s2195.html) · [Breathless Man](https://bigsoundbank.com/breathless-man-s1103.html)

## Music (credit required)

- `music_house` crossfades edited excerpts of “Apprehension” by Kevin MacLeod and “She's Watching Me” by Darren Curtis. [Apprehension](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100327) · [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) · [Darren Curtis](https://www.darrencurtismusic.com/) · [Composer's permission](https://www.darrencurtismusic.com/faqs)
- `scare_bump` and the shorter upstairs accent `scare_left_bump` use trimmed, level-adjusted excerpts of “Bump in the Night” by Kevin MacLeod. [Track](https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100789) · [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
- The legacy `music_drone` is synthesized. An archived earlier version used “Long Note Four” by Kevin MacLeod (CC BY 4.0).
- music_menu: "Ossuary 6 - Air" Kevin MacLeod (incompetech.com), CC BY 4.0
- music_finale: "Gathering Darkness" Kevin MacLeod (incompetech.com), CC BY 4.0
- music_dawn: "Sanctuary" Scott Buckley (scottbuckley.com.au), CC BY 4.0

## Voices
Synthesized dialogue uses Google Gemini TTS (see VO/_manifest.json). Radio and phone treatment: Cheyenne's Forklight Voice Effects v1 (voice_effects.py).

- Cheyenne performed Edith's “You left me!” scream. The approved master in `VO/m_whyleave.wav` carries a lower vocal double and rasp through the line. Its Sound Wave adds 9.5 dB in the upstairs scene.
- The hall pendant's two-direction creak uses a short, lowered excerpt of Epic Stock Media's *HD Game Materials*, “Dry Ice High Metal Squeal Groan Bright Squeak Dissonant Short 13,” from volume 2 of the licensed Sonniss GDC 2026 bundle.
- The bookshelf violin layers four solo bowed violin recordings (A6 forte and piano, G6 forte, and E6 piano) from Versilian Studios’ VS Chamber Orchestra Community Edition, recorded by Sam Gossner and Simon Dalzell under CC0. [Original samples](https://github.com/sgossner/VSCO-2-CE/tree/master/Strings/Solo%20Violin/Arco%20Vib) · [License](https://github.com/sgossner/VSCO-2-CE/blob/master/LICENSE). The mix is reproducible with `Scripts/audio/make_shelf_violin.py`.

## From Cheyenne's Sonniss GDC 2026 Game Audio Bundle and Night Shift package (royalty-free, no attribution required)

- The wheelchair's rolling tread and axle rub are original procedural Foley. Its baseboard tap uses the game's wood footstep and chair scrape. Its landing blends the wood recording with a shortened, damped layer from `trash_crash`, which includes 344 Audio's *Haunting Ambiences Vol. 3* metal impacts from the licensed Sonniss GDC 2026 bundle. The four sounds can be rebuilt with `Scripts/audio/make_bath_wheel.py`.

- `deputy_pant` uses SoundBits, *Vox Hominis – Human Effort Voices*, “Panting Male 02 04” from volume 5 of the Sonniss GDC 2026 bundle. Edited to a 5.4-second close-mic breathing cue under the included Game Audio GDC Bundle license.

- amb_car: InMotionAudio - Car Interior Driving Ambience/VEHCar_TownDrivingAmbience06_InMotionAudio_CarInteriorDrivingAmbience.wav
- car_stop: SoundBits - Cars - Mad Mustang Mercury/VEHSkid_Tire Skids on Gravel 15 06_SNDBTS_CRS-MMM.wav
- car_door: SoundBits - Cars - Mad Mustang Mercury/VEHDoor_Car Foley Car Door Open and Close Exterior 04 Perspective A_SNDBTS_CRS-MMM.wav
- wind_gust_01: InMotionAudio - Chimney Wind/WINDInt_ChimneyWind05_InMotionAudio_ChimneyWind.wav
- wind_gust_02: InMotionAudio - Chimney Wind/WINDInt_ChimneyWind05_InMotionAudio_ChimneyWind.wav
- wind_gust_03: InMotionAudio - Chimney Wind/WINDInt_ChimneyWind05_InMotionAudio_ChimneyWind.wav
- amb_wind: InMotionAudio - Chimney Wind/WINDInt_ChimneyWind05_InMotionAudio_ChimneyWind.wav
- scratch_wall_01: InMotionAudio - Sinister Textures 5/GOREMisc_Cladding_NailScratch19_InMotionAudio_SinisterTextures5.wav
- scratch_wall_02: InMotionAudio - Sinister Textures 5/GOREMisc_Cladding_Scratch06_InMotionAudio_SinisterTextures5.wav
- scratch_wall_03: InMotionAudio - Sinister Textures 5/GOREMisc_Cladding_NailScratch19_InMotionAudio_SinisterTextures5.wav
- scratch_wall_04: InMotionAudio - Scratch Card/OBJMisc_ScratchCard_CoinTapScratch_01_InMotionAudio_ScratchCard.wav
- skitter_01: Selected_Originals/skitter__Spider Chattering.wav
- skitter_02: Selected_Originals/skitter__Spider Chattering.wav
- skitter_03: Epic Stock Media - HD Game Materials/WOODFric_Wood Shaker Microphone Head Roll Table Alternate Grainy 05_ESM_HDGM.wav
- skitter_04: Epic Stock Media - HD Game Materials/ICEFric_Dry Ice Squeak Metal Animal Mouse Imitation Short 07_ESM_HDGM.wav
- bang_far_01: 344 Audio - Haunting Ambiences Vol. 3/METLImpt_Metal Bangs, Metal Hits, Banging On Doors_344 Audio_Haunting Ambiences Vol 3.wav
- wood_hit_far_01: 344 Audio - Haunting Ambiences Vol. 3/WOODImpt_Wooden Hit, Dark, Heavy Hit, Vampire's Prison_344 Audio_Haunting Ambiences Vol 3.wav
- chair_creak_01: 344 Audio - Cinema Experience Vol. 1/FOLYProp_Sitting Down, Creaky Seat, Squeaks 3_344 Audio_CInema Experience.wav
- switch_click: InMotionAudio - USA Hotel/MECHClik_USALightSwitch_On05_InMotionAudio_USAHotel.wav
- bulb_buzz: InMotionAudio - Arc/ELECBuzz_Buzz27_InMotionAudio_Arc.wav
- bulb_pop: InMotionAudio - Arc/ELECArc_ArcDesign15_InMotionAudio_Arc.wav
- amb_fridge: Jake Fielding - Fridge Hums Vol.2/MACHAppl_Deep Fridge Hum, Buzz, Electric Tone, Deep_Jake Fielding_Fridge Hums Pt2.wav
- toilet_far: InMotionAudio - USA Hotel/WATRPlmb_ToiletFlush01_InMotionAudio_USAHotel.wav
- radio_tune: Sonic Bat - Vintage Radio/SBvr_AM EQ Sweeping 002.wav
- breath_near_01: SoundBits - Vox Bestiae - Source Elements/CREAHmn_Violent Humanoid Creature Exhale Short 4_SNDBTS_VB-SE.wav
- breath_near_02: her_breath (re-processed)
- her_hurt_01: Epic Stock Media - Humanoid Creatures Vol 4 - Monstrous and Undead Creature Vocalization Sound Sets/HMNBrth_Construction Kit Male Screeching Breath Inhale Weak Squeal 05_ESM_HC4.wav
- her_hurt_02: her_scream_short_02 (re-processed)
- her_flinch_01: her_scream_short_01 (re-processed)
- her_flinch_02: SoundBits - Vox Bestiae - Source Elements/CREAHmn_Violent Humanoid Creature Exhale Short 4_SNDBTS_VB-SE.wav
- music_low: Epic Stock Media - Strange Game Ambient Loops 3/DSGNSynth_Dark Loop Mystic Forest Tonal Steady Synth_ESM_SGA3.wav
- music_stalk: InMotionAudio - The Death Whistle/CREAEthr_Aztec Death Whistle Drone_05_IMA_Death Whistle Samples.wav
- music_evil: 344 Audio - Ghostly Presences Vol. 1/AMBDsgn_Evil Spell Ambience_344 Audio_Ghostly Presences.wav
- sting_braam: Cinematic Sound Design - Ultra Transitions & Impacts/Transition Braam Slow Dark Creepy.wav
- sting_whisper: Epic Stock Media - Halloween Game - Haunted House and Horror Audio Scare Kit/DSGNEthr_Jumpscare Vocal Aggressive Whisper Harsh Distortion 02_ESM_HALG.wav
- sting_swell: Epic Stock Media - Halloween Game - Haunted House and Horror Audio Scare Kit/UIAlert_Alert Designed Transition Swell Creature Strange Alien Layered 01_ESM_HALG.wav
- sting_noisebox: InMotionAudio - Sinister Textures 4/DSGNErie_NoiseBoxHit_10_InMotionAudio_SinisterTextures4.wav
- door_far_01: door_close_01 (re-processed)
- door_far_02: door_creak_long (re-processed)
- door_far_03: door_slam (re-processed)
- her_step_01: Epic Stock Media - Tower Defense Game/WOODImpt_Hit Blood Spill Splat Wood Impact Light Hit Squelch Small Thump 03_ESM_TDG.wav + our own step_wood_01
- The bookshelf stair run uses the existing licensed her_step and Kenney wood contacts with a synthesized low board resonance. It is rendered by `Scripts/audio/make_shelf_steps.py`.
- her_step_02: Epic Stock Media - Tower Defense Game/WOODImpt_Hit Blood Spill Splat Wood Impact Light Hit Squelch Small Thump 03_ESM_TDG.wav + our own step_wood_03
- her_step_03: Epic Stock Media - Tower Defense Game/WOODImpt_Hit Blood Spill Splat Wood Impact Light Hit Squelch Small Thump 03_ESM_TDG.wav + our own step_wood_02
- her_step_04: Epic Stock Media - Tower Defense Game/WOODImpt_Hit Blood Spill Splat Wood Impact Light Hit Squelch Small Thump 03_ESM_TDG.wav + our own step_wood_05

## Things that act by themselves

- record_tune: Darren Curtis, "Sweet Little Lullaby" (darrencurtismusic.com; free for commercial use with credit), processed to sound like a horn gramophone
- record_stop: made from record_tune and our own shelf_scrape
- clock_tick: 344 Audio - Antique Clocks/CLOCKTick_Crooked Antique Clock_344 Audio_Antique Clocks.wav
- clock_single_01 and clock_single_02 are individual mechanical strikes edited from the same 344 Audio antique clock recording.
- bell_toll: Ivo Vicic - Church Bells/04 Church Bells, Near Distance, In Church Tower-3 Different Bell 02.wav (first stroke, pitched down)
- tv_static: synthesised (noise, 60 Hz hum, line whine)

## Edith's indoor one-shots

- The two whimpers, two groans and two whispered snickers are edits of Edith's original Gemini vocal takes in `VO_dry`. The snickers use the timing and changing mouth sounds of her unlayered laughter. The mastering recipe is in `Scripts/audio/make_edith_haunts.py`.
- The listening snicker uses a longer passage from the same unlayered `m_laugh2` performance and the same whispered treatment.
- Edith's upstairs steps use the existing four `her_step` wet footfalls credited above.
- Edith's ceiling crawl uses edited hits from *Walking on Wooden Floor*, credited to Ruvhjnvdkvndjine (Freesound) on Pixabay under the Pixabay Content License. The cuts lower the pitch, reinforce the low end and shorten the strikes. The game places the hits on the animated foot contacts. Rebuild the hits with `Scripts/audio/make_ceiling_boot_steps.py` and a local copy of the download. [Recording and license](https://pixabay.com/sound-effects/film-special-effects-walking-on-wooden-floor-94493/).

## Yard and rear shed

- `amb_yard` and `amb_dawn` are original synthesized wind and insect beds. `Scripts/audio/make_exterior_beds.py` masters both loops.
- The falling trash can uses *Light Metal Crash* by DieselsiselMedia. The 2.5-second positional cue starts 0.145 s into the recording, mixes to mono and fades over the last 0.35 s. Its original creator released the recording under CC0. [Original recording and license](https://freesound.org/people/DieselsiselMedia/sounds/387139/) · [Pixabay download](https://pixabay.com/sound-effects/film-special-effects-light-metal-crash-6765/).
- The earlier `trash_crash` master remains a source for the wheelchair Foley. It uses two edited hits from 344 Audio, *Haunting Ambiences Vol. 3*, "Metal Bangs, Metal Hits, Banging On Doors," from the Sonniss GDC 2026 Game Audio Bundle 1 of 5 under the included GDC Game Audio license. Its mastering recipe is in `Scripts/audio/make_trash.py`.

## Ruth's door

The sobs in this encounter use Epic Stock Media's *AAA Game Character British Female Detective* (Crying Vocal Female Low Energy Weep) and SoundBits' *Vox Hominis* (Crying Female 04 05). The recordings came from volumes 2 and 5 of Cheyenne's Sonniss GDC 2026 collection under the included Game Audio GDC Bundle license. The late vocal distortion is ordinary pitch and saturation processing. The wordless whisper and background scream use the game's own breath and scream recordings. The scene mix can be rebuilt with Scripts/audio/make_door_voices.py.

## The stairwell

The five `bone_crack` hits are synthesized from noise and tone with ffmpeg; nothing recorded is used. `stair_moan` is Edith's own `m_moan2` voice line (see Voices), raised in pitch, slowed, given a waver and a stairwell echo. Both can be rebuilt with `Scripts/audio/make_stair_sounds.py`. The deputy's "Mrs. ... Harrow?" on the stairs (`d_stairs_call`) is Gemini TTS like his other lines, with the pause between the words lengthened by the same script. His "Shit... shit..." (`d_stairs_shit`) and Edith's whisper "You should never have come here." (`m_never`) are Gemini TTS too; the whisper is the spoken take (`VO_dry/m_never_spoken.wav`) turned into a true whisper with `Scripts/audio/whisperize.py`. `flashlight_shake`, `flashlight_smack` and `allfours_rush` were generated for the scene with Higgsfield (Mirelo text-to-audio), job ids in raw/_jobs.json, then trimmed and levelled. The flashlight smack is low-passed to take out a ringing tone in the generated take. The rest of the scene reuses sounds already listed above.

## Audio pass 2 (applied 2026-11-26): sources of the rebuilt sounds

Every recipe is in
`Scripts/audio/pass2_build.py`; library recordings are listed in `Scripts/audio/pass2_sources.py`. Nothing in this pass
needs a credit line: all added material is from the Sonniss GDC 2026 Game Audio Bundle (royalty-free, no attribution
required) or is CC0. The music credits already listed for `music_house` still apply (its approved core is unchanged).

### Stings (stereo)

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

### The wheelchair in the bath

- `wheel_on_boards`: the earlier procedural rumble plus Epic Stock Media *HD Game Materials* (Wood Shaker Microphone Head
  Roll Table), 344 Audio *Christmas* (Sleigh Movement, Pulling) and Kenney impact sounds (impactWood light, CC0).
- `wheel_axle_rub`: 344 Audio *Cinema Experience* (Sitting Down, Creaky Seat, Squeaks 3) and the dry-ice squeal.
- `wheel_baseboard`, `wheel_sidefall`: the earlier impacts plus 344 Audio *Medieval Weapons Vol. 2* (stick impact; Metal
  Shield Spin On Floor), *Haunting Ambiences Vol. 3* (Wooden Hit, Dark, Heavy Hit), InMotionAudio *Sinister Textures 5*
  (Concrete MetalPipe 02), Kenney impactWood heavy and impactMetal heavy (CC0).

### Pistol, doors, falls

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

### Footsteps

- `step_wood_01..05`, `step_stairs_01..02`: the Kenney wood steps already credited plus *Boots Stomping Footsteps on
  Wooden Floor 37* (sfxmint, CC0 1.0, https://sfxmint.com/sounds/footsteps-wood-37).
- `step_gravel_01..04`: the Kenney grass steps already credited plus Kenney footstep snow (CC0) and Joseph Sardin, *Steps
  on the Twigs* (BigSoundBank 1301, CC0).
- `step_stone_01..04`: the Kenney concrete steps with a short room.

### Remastered only (no new material)

`gun_reload`, `bullet_impact_01`, `door_open_01`, `door_creak_long`, `trunk_open`, `knock_far_*`, `thump_far_*`,
`thump_heavy`, `bang_far_01`, `wood_hit_far_01`, `steps_above_*`, `ceiling_thump_*`, `ceiling_boot_step_*`,
`shelf_stair_step_*`, `her_step_*`, `frame_fall`, `creak_*`, `house_groan_*`, `drag_floor`, `shelf_scrape`,
`chair_scrape`, `chair_creak_01`, `scratch_wall_*`, `bath_drain`, `wind_gust_*`, `bulb_buzz`, `flashlight_click`,
`pickup`, `paper`, `phone_ring`, `music_drone`, `amb_cellar`. Low content gained harmonics a laptop speaker can play;
levels were made consistent.

### Loops

- `music_house`: the approved 162 s piece (Apprehension, Kevin MacLeod, CC BY 4.0; She's Watching Me, Darren Curtis) is
  the unchanged core. Added around it: six slow waves of The Noisery *Moaning Metal* (Bowed Screech 7) at different
  pitches, the *spellbound* tension drone on a slow breathing cycle, and *Dark Industrial Ambience* (bundle 2) as a floor.
- `music_stalk`: the same death-whistle drone, doubled one, two and three octaves up.

### Not touched

Edith's screams, whispers, moans and breathing, the deputy's breathing, every voice line, crickets and crows, the music
box, record, television, clock, bell, flashlight shake and smack, `scare_bump` / `scare_left_bump`, `trash_can_fall`.

### The cruiser

- `amb_car`: the cab recording already credited (InMotionAudio, Car Interior Driving Ambience) under SoundBits, *Cars - Mad
  Mustang Mercury* (Various Driving at Slow Speed 15 06) from volume 5 of the Sonniss bundle: crackle filtered off, pops softened,
  engine note given harmonics, level held steady.
