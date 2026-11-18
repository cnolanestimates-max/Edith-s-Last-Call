"""After the first drive: the dash was lit flat green by its own glow; white rocks and glowing mushrooms on the verge."""
import json, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "forest.py", [
    ('''cpart(light_point("DashGlow", CRX + 62, CRY - 36, 96, 0.5, (0.35, 1.0, 0.6), 110, "Cruiser", tags=["CarRunning"], shadows=False, vol=0.0, source=2))''',
     '''cpart(light_point("DashGlow", CRX + 44, CRY - 37, -40 + 92, 0.035, (0.55, 1.0, 0.7), 60, "Cruiser", tags=["CarRunning"], shadows=False, vol=0.0, source=1))
cpart(light_point("CabinFill", CRX - 10, CRY - 10, -40 + 138, 0.10, (0.55, 0.66, 1.0), 170, "Cruiser", tags=["CarRunning"], shadows=False, vol=0.0, source=6))'''),
])
o = json.load(open(L + "overrides.json"))
o.update({"M_GlowSickly": "MI_PaperOld", "M_StoneFog": "MI_CellarStone", "M_StoneMossy": "MI_CellarStone", "M_GraveDirt": "MI_YardGround", "M_GraveDirtDark": "MI_CellarFloor",
          "M_GrassDead": "MI_ForestFloor", "M_Moss": "MI_ForestFloor", "M_Lichen": "MI_ForestFloor", "M_BarkBirch": "MI_Bark", "M_Swamp": "MI_CellarFloor", "M_SwampMud": "MI_CellarFloor",
          "M_LeafDark": "MI_ForestFloor", "M_LeafAutumn": "MI_ForestFloor", "M_Ash": "MI_Soot", "M_Sand": "MI_Gravel", "M_Stem": "MI_Bark", "M_MushroomPale": "MI_PaperOld",
          "M_MushroomRed": "MI_LeatherRed", "M_Cobweb": "MI_Sheet", "M_Ghost": "MI_Sheet", "M_Bone": "MI_PaperOld", "M_Feather": "MI_FabricDark", "M_Beak": "MI_Leather",
          "M_Fur": "MI_FabricDark", "M_RatFur": "MI_FabricDark", "M_Corn": "MI_PaperOld", "M_Marble" : "MI_Porcelain", "M_MarbleOld": "MI_Porcelain", "M_MarbleDark": "MI_CellarStone",
          "M_TileDark": "MI_MegaTilesStained", "M_TileBlack": "MI_MegaTilesStained", "M_TileSick": "MI_MegaTilesStained", "M_SilverOld": "MI_Iron", "M_Chrome": "MI_Iron", "M_Gold": "MI_Brass",
          "M_Wax": "MI_PaperOld", "M_Ink": "MI_Soot", "M_Rubber": "MI_Leather", "M_Portrait": "MI_FabricDark", "M_PortraitDark": "MI_FabricDark"})
json.dump(o, open(L + "overrides.json", "w"), indent=1)
print("ok", len(o))
