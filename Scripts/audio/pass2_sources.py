"""Audio pass 2 (2026-11-25): pull the library recordings the pass uses into SourceArt/Audio/raw_lib (git-ignored).

Files are copied out of Cheyenne's library, never moved or changed.  Sonniss GDC 2026 bundle: royalty-free, commercial
use allowed, no attribution required.  Kenney (Open Game SFX "Impacts and Footsteps"): CC0.

  python pass2_sources.py            extract what is missing
  <numpy python> pass2_sources.py --survey   list length, level and the hits found in each file
"""
import glob, os, re, shutil, sys, zipfile

ROOT = "C:/GameDev/Unreal/WellnessCheck"
RAW = ROOT + "/SourceArt/Audio/raw_lib"
LIB = "C:/Users/cheye/OneDrive/Documents/ChatGPT/forklight-tts"
SON = LIB + "/Sonniss.com-GDC2026-GameAudioBundle%dof5.zip"
KEN = LIB + "/Open Game SFX - WAV Library/WAV Files/Impacts and Footsteps"

# key: (bundle number or zip name, substring of the member name)
SONNISS = {
    # ---- hits, drops, braams, screeches (stings)
    "smash": (2, "GORESplt_Gore Designed Transient Heavy Impact Smash 01"),
    "boom_011": (2, "EffectiveTrailer_Booms_Vol2_011"),
    "boom_075": (2, "EffectiveTrailer_Booms_Vol2_075"),
    "boom_214": (2, "EffectiveTrailer_Booms_Vol2_214"),
    "drop_fast": (1, "DSGNBass_Bass Drop & Downer Fast 16"),
    "drop_fast2": (1, "DSGNBass_Bass Drop & Downer Fast 12"),
    "drop_med": (1, "DSGNBass_Bass Drop & Downer Medium 04"),
    "drop_slow": (1, "DSGNBass_Bass Drop & Downer Slow 10"),
    "drop_jump": (1, "DSGNBass_Jump Start Drop 3"),
    "drop_rattle": (1, "DSGNBass_Rattling Downer 3"),
    "drop_tone": (1, "DSGNBass_Tone Downer (Reverb)"),
    "braam_32": (3, "Cinematic Horn Braam, Epic, Cinematic, Dark, Instrument, Huge-32"),
    "braam_67": (3, "Cinematic Horn Braam, Epic, Cinematic, Dark, Instrument, Huge-67"),
    "braam_creepy": (2, "Transition Braam Slow Dark Creepy"),
    "noisebox_10": (3, "DSGNErie_NoiseBoxHit_10"),
    "noisebox_36": (3, "DSGNErie_NoiseBoxHit_36"),
    "metal_thud": (5, "DSGNImpt_Metal Hit Thud Thump Low Ring Geofon 1"),
    "bowed_screech": (5, "DSGNTonl_Designed Metal Bowed Screech Tonal Reverb 7"),
    "metal_scrape_low": (5, "DSGNTonl_Metal Scrape Low Tonal LFE 4"),
    "ice_squeal": (2, "ICEFric_Dry Ice High Metal Squeal Groan Bright Squeak Dissonant Short 13"),
    "psycho": (2, "Psycho Glitched Screechy Tones Noise"),
    "chord_hit": (2, "Impact Hit Rapid Chord Reverb"),
    "evil_presence": (2, "magic, action gesture, evil presence, onslaught-004"),
    "drone_tension": (2, "magic, drone, tension, spellbound, evanescence-002"),
    "grim_pain": (5, "CREAEthr_Ethereal Entity Grim Pain Long 4"),
    "fire_growl": (2, "FIREWhsh_Whoosh Fire Deep Growl Monster Saturated Crisp 03"),
    "elec_impact": (2, "ELECMisc_Impact Electric Tonal Deep Movement Motion Hiss Glitch 01"),
    "wind_rush": (1, "WINDDsgn_Wind, Rush, Whoosh, Long x5 01"),
    "metal_whoosh": (1, "METLMisc_Metal, Slow Whoosh, Rattle, Pass By x4 01"),
    "whisper_jump": (2, "DSGNEthr_Jumpscare Vocal Aggressive Whisper Harsh Distortion 02"),
    "dark_industrial": (2, "Dark Industrial Ambience"),
    "mystic_loop": (2, "DSGNSynth_Dark Loop Mystic Forest Tonal Steady Synth"),
    # ---- foley
    "barber_pump": (1, "OBJFurn_Barber Chair, Foot Pump 4"),
    "sleigh": (1, "MAGMisc_Sleigh Movement, Pulling"),
    "shaker_roll": (2, "WOODFric_Wood Shaker Microphone Head Roll Table Alternate Grainy 05"),
    "spring_wire": (2, "METLTonl_Item Spring Wire Impact Flick Top Clatter Light Tap Roll Handling Short 01"),
    "latch_thunk": (2, "MECHLtch_Click Deep Mechanism Latch Button Nearfield Thunk 02"),
    "antique_lock": (1, "METLMvmt_  Tinkering Antique Lock"),
    "suitcase_lock": (1, "OBJLug_Suitcase Being Locked, Antique Suitcase 1"),
    "suitcase_open": (1, "OBJLug_Suitcase Opening and Closing, Antique Suitcase"),
    "stairwell_door": (3, "DOORMetl_StairWellDoor01"),
    "punch_body": (1, "FGHTImpt_4 x Punch, Body 02"),
    "stick_impact": (1, "WEAPBlnt_Spear And Stick Impact, Wooden MKH 2"),
    "fireworks_near": (3, "13 Fireworks_powerful explosions_multiples in a row_near"),
    "books_fall": (1, "PAPRMisc_Pile Of Antique Books Falling Over 8"),
    "phone_handset": (1, "COMTelph_Antique Telephone Pick Up & Drop Ear Piece"),
    "phone_fall": (1, "COMTelph_Antique Telephone Ear Piece Falling Down"),
    "arc_powerup": (3, "ELECArc_ArcPowerUpDesign04"),
    "arc": (3, "ELECArc_ArcDesign15"),
    "buzz": (3, "ELECBuzz_Buzz27"),
    "creaky_seat": (1, "FOLYProp_Sitting Down, Creaky Seat, Squeaks 3"),
    "metal_bangs": (1, "METLImpt_Metal Bangs, Metal Hits, Banging On Doors"),
    "wood_hit_dark": (1, "WOODImpt_Wooden Hit, Dark, Heavy Hit"),
    "pipe_concrete": (3, "GOREMisc_Concrete_MetalPipe02"),
    "case_down": (3, "OBJLug_CaseDown_Concrete12"),
    "case_closed": (3, "OBJLug_Case_Closed06"),
    "tape_measure": (2, "MECHMisc_Tool Tape Measure Pull Retract Spring Slide Spin Long 07"),
    "shield_spin": (1, "WEAPArmr_Metal Shield Spin On Floor, Buckler MKH"),
    "box_drag": (1, "METLFric_Large Metal Box, Drag, Geofon"),
    "light_switch": (3, "MECHClik_USALightSwitch_On05"),
    "book_pages": (1, "PAPRMisc_Antique Books Slow Page Turns 6"),
    "gravel_skid": (5, "VEHSkid_Tire Skids on Gravel 15 06"),
    "mustang_slow": (5, "VEHCar_Various Driving at Slow Speed 15 06"),
    "car_town_13": (3, "VEHCar_TownDrivingAmbience13"),
}
OTHER = {
    "boots_wood": (LIB + "/Forklight_Footstep_Gap_Additions_2026-10-12.zip", "boots_stomping_wood_sfxmint_37.wav"),
    "twigs": (LIB + "/Forklight_Footstep_Gap_Additions_2026-10-12.zip", "BigSoundBank_1301_Steps_on_the_Twigs.wav"),
}


def safe(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.basename(name))


def path(key):
    """Raw file for a key (extracting it if needed)."""
    if key.startswith("ken:"):                     # "ken:impactWood_heavy_002" is the file "impactWood_heavy_002.wav"
        a = key[4:].rsplit("_", 1)
        for cand in (key[4:], a[0].replace("_", " ") + " " + a[1], a[0] + " " + a[1]):
            if os.path.exists(KEN + "/" + cand + ".wav"):
                return KEN + "/" + cand + ".wav"
        raise FileNotFoundError(key)
    src, sub = SONNISS[key] if key in SONNISS else OTHER[key]
    z = SON % src if isinstance(src, int) else src
    hits = glob.glob(RAW + "/*" + safe(sub).replace(".wav", "") + "*")
    if hits:
        return hits[0].replace("\\", "/")
    os.makedirs(RAW, exist_ok=True)
    with zipfile.ZipFile(z) as zf:
        m = [i for i in zf.infolist() if sub in i.filename and i.filename.lower().endswith((".wav", ".mp3"))]
        if not m:
            raise FileNotFoundError(f"{sub} not in {z}")
        out = RAW + "/" + safe(m[0].filename)
        with zf.open(m[0]) as fi, open(out, "wb") as fo:
            shutil.copyfileobj(fi, fo, 1 << 20)
    return out


if __name__ == "__main__":
    for k in list(SONNISS) + list(OTHER):
        try:
            p = path(k)
            print(f"{k:18s} {os.path.getsize(p) / 1048576:7.1f} MB  {os.path.basename(p)}")
        except Exception as exc:
            print(f"{k:18s} FAILED {exc}")
