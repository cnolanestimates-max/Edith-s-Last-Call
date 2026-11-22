"""Apply Scripts/level/polish_pass.py (and the other polish steps that live next to it) to the saved House map, without
rebuilding the level.  UnrealEditor-Cmd WellnessCheck.uproject -run=pythonscript -script=<this> -unattended -nosplash"""
import os, runpy
import unreal as u

HERE = os.path.dirname(os.path.abspath(__file__))
le = u.get_editor_subsystem(u.LevelEditorSubsystem)
if not le.load_level("/Game/WC/Maps/House"):
    raise RuntimeError("could not open the House map")
for step in [s for s in os.environ.get("WC_POLISH_STEPS", "polish_pass").split(",") if s]:
    runpy.run_path(os.path.join(HERE, step + ".py"))["dress"]()
if not le.save_current_level():
    raise RuntimeError("could not save the House map")
u.log_warning("WC_POLISH saved")
