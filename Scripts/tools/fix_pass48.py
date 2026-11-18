"""Face preview: every render sets all three keys explicitly and refreshes the scene first."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
edit("C:/GameDev/Unreal/WellnessCheck/Scripts/her/build_her.py", [
    ('''    for _nm, _keys in (("sneer_1", (sk_sneer,)), ("brow_1", (sk_brow,)), ("all_1", (sk_sneer, sk_brow))):
        for _k in _keys:
            _k.value = 1.0
        sk_scream.value = 0.3 if _nm == "all_1" else 0.0
        _cam.location = _tgt + Vector((0.15, -1, 0.0)).normalized() * 150
        _cam.rotation_euler = (_tgt - _cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "preview", _nm + ".png")
        bpy.ops.render.render(write_still=True)
        for _k in _keys:
            _k.value = 0.0''', '''    for _nm, _sn, _br, _scr in (("sneer_1", 1.0, 0.0, 0.0), ("brow_1", 0.0, 1.0, 0.0), ("talk_1", 0.2, 0.4, 0.3), ("rest_1", 0.0, 0.0, 0.0)):
        sk_sneer.value, sk_brow.value, sk_scream.value = _sn, _br, _scr
        mesh.data.update()
        bpy.context.view_layer.update()
        _cam.location = _tgt + Vector((0.15, -1, 0.0)).normalized() * 150
        _cam.rotation_euler = (_tgt - _cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "preview", _nm + ".png")
        bpy.ops.render.render(write_still=True)
    sk_sneer.value = sk_brow.value = 0.0'''),
])
print("ok")
