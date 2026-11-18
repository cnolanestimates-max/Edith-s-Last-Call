import unreal
ok = unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
result = "saved=" + str(ok)
