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
