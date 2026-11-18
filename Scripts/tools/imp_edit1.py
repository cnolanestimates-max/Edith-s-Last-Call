import io
p = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/import_assets.py"
s = io.open(p, encoding="utf-8").read()
old = 'for name, fn in (("kit", step_kit), ("her", step_her), ("mats", step_mats), ("audio", step_audio), ("tex", step_tex)):'
new = ('exec(open(ROOT + "/Scripts/level/import_more.py", encoding="utf-8").read())\n\n'
       'for name, fn in (("kit", step_kit), ("her", step_her), ("mats", step_mats), ("audio", step_audio), ("tex", step_tex), ("props", step_props), ("decals", step_decals), ("extra", step_extra_mats)):')
assert old in s
s = s.replace(old, new)
s = s.replace('"kit,her,mats,audio,tex"', '"kit,her,mats,audio,tex,props,decals,extra"')
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
