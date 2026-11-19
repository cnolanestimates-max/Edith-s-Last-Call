"""Pass 104: the yard at night was still black from the back (Saved/Out2): the new tree line stood between the moon and the
yard.  The tree line no longer casts shadows (it is a silhouette against the sky anyway) and the moon is stronger."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Scripts/level/exterior.py", [
    ('''            place(_tr.choice(_KT), _x + _tr.uniform(-90, 90), _side * (_off + _tr.uniform(-70, 110)), -46, _tr.uniform(0, 360), EX + "/TreeLine",
                  scale=_tr.uniform(1.7, 2.6), collide=False)
            _n += 1''', '''            _ta = place(_tr.choice(_KT), _x + _tr.uniform(-90, 90), _side * (_off + _tr.uniform(-70, 110)), -46, _tr.uniform(0, 360), EX + "/TreeLine",
                        scale=_tr.uniform(1.7, 2.6), collide=False)
            _ta.static_mesh_component.set_editor_property("cast_shadow", False)       # the moon has to reach the yard
            _n += 1'''),
    ('''        place(_tr.choice(_KT), YARD_BACK + _off + _tr.uniform(-80, 110), _y + _tr.uniform(-90, 90), -46, _tr.uniform(0, 360), EX + "/TreeLine",
              scale=_tr.uniform(1.8, 2.8), collide=False)
        _n += 1''', '''        _ta = place(_tr.choice(_KT), YARD_BACK + _off + _tr.uniform(-80, 110), _y + _tr.uniform(-90, 90), -46, _tr.uniform(0, 360), EX + "/TreeLine",
                    scale=_tr.uniform(1.8, 2.8), collide=False)
        _ta.static_mesh_component.set_editor_property("cast_shadow", False)
        _n += 1'''),
])
edit(R + "Scripts/level/lighting.py", [
    ('''mc.set_intensity(float(os.environ.get("WC_MOON", "9.0")))''', '''mc.set_intensity(float(os.environ.get("WC_MOON", "26.0")))'''),
])
print("pass 104 applied")
