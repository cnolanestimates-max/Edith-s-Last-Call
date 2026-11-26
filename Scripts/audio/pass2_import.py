"""Unreal (headless): import only the sounds listed in SourceArt/AudioPass2/applied.json into /Game/WC/Audio.

Unlike the `audio` step of import_assets.py this touches no other sound, and every asset keeps the loop flag, volume and
pitch it had (Codex set some of those by hand, e.g. the looping wheelchair roll).  Env WC_PASS2_ONLY=a,b limits the list.
"""
import json, os
import unreal

ROOT = "C:/GameDev/Unreal/WellnessCheck"
names = json.load(open(ROOT + "/SourceArt/AudioPass2/applied.json"))
only = [s for s in os.environ.get("WC_PASS2_ONLY", "").split(",") if s]
if only:
    names = [n for n in names if n in only]
eal = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
ok = 0
for n in names:
    path = f"/Game/WC/Audio/{n}"
    keep = {}
    if eal.does_asset_exist(path):
        w = eal.load_asset(path)
        for prop in ("looping", "volume", "pitch"):
            try:
                keep[prop] = w.get_editor_property(prop)
            except Exception:
                pass
    else:
        keep["looping"] = n.startswith(("amb_", "music_"))
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", f"{ROOT}/SourceArt/Audio/{n}.wav")
    t.set_editor_property("destination_path", "/Game/WC/Audio")
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("automated", True)
    t.set_editor_property("save", True)
    tools.import_asset_tasks([t])
    w = eal.load_asset(path)
    if not isinstance(w, unreal.SoundWave):
        unreal.log_warning(f"WC_PASS2: FAILED {n}")
        continue
    for prop, val in keep.items():
        w.set_editor_property(prop, val)
    eal.save_loaded_asset(w, False)
    ok += 1
    unreal.log_warning(f"WC_PASS2: {n} {w.get_editor_property('duration'):.2f}s loop={w.get_editor_property('looping')} vol={keep.get('volume', 1.0)}")
unreal.log_warning(f"WC_PASS2: DONE {ok} of {len(names)}")
