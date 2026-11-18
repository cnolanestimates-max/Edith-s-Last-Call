import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCStory.cpp", [
    ('''TEXT("Dispatch, Fourteen. On scene at eleven-forty County Road Nine.")''', '''TEXT("Dispatch, Fourteen. I'm out on County Road Nine, coming up on the Harrow place.")'''),
    ('''TEXT("Dispatch? ...Dead. I'll call it in from the car.")''', '''TEXT("Dispatch? ...Dispatch. ...Dead.")'''),
])
print("ok")
