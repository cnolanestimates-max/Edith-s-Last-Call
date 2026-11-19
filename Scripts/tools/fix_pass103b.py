"""Pass 103b: Items is a set, not an array (build fix), and Inspect stays on the doll after the key comes out."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''		const int32 At = Items.IndexOfByKey(FName(TEXT("doll")));
		if (At == INDEX_NONE) return;
		Items[At] = FName(TEXT("doll_empty"));
		Set(TEXT("doll_opened"));
		if (!HasItem(TEXT("key_box")) && !Has(TEXT("box_open"))) Items.Insert(FName(TEXT("key_box")), At + 1);''',
     '''		if (!HasItem(TEXT("doll"))) return;
		Items.Remove(TEXT("doll"));
		Items.Add(TEXT("doll_empty"));
		Set(TEXT("doll_opened"));
		if (!HasItem(TEXT("key_box")) && !Has(TEXT("box_open"))) Items.Add(TEXT("key_box"));'''),
])
edit(R + "Source/WellnessCheck/WCGame.cpp", [
    ('''				if (Now.IsValidIndex(InvSel)) { ShowInvItem(D, Now[InvSel].Id); InvYaw = Y0; InvPitch = P0; InvZoom = Z0; }''',
     '''				for (int32 i = 0; i < Now.Num(); ++i) if (Now[i].Id == TEXT("doll_empty")) InvSel = i;
				if (Now.IsValidIndex(InvSel)) { ShowInvItem(D, Now[InvSel].Id); InvYaw = Y0; InvPitch = P0; InvZoom = Z0; }'''),
])
print("pass 103b applied")
