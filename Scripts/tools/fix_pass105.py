"""Pass 105: the inventory photo test (-WCInvTest=<dir>) shows every thing in Inspect, the doll from both sides, and the key
coming out of her."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
R = "C:/GameDev/Unreal/WellnessCheck/"
p = R + "Source/WellnessCheck/WCGame.cpp"
s = open(p, encoding="utf-8").read()
a = s.index("		// -WCInvTest=<dir>: fill the bag, open it, photograph each page, quit")
b = s.index("	if (!MenuTestDir.IsEmpty() && RealNow > MenuTestAt)")
new = r'''		// -WCInvTest=<dir>: fill the bag, open it, photograph every thing in Inspect (the doll from both sides, and emptied), quit
		struct FInvShot { const TCHAR* Item; float Yaw, Pitch; const TCHAR* Name; const TCHAR* Before; };
		static const FInvShot Shots[] = {
			{ TEXT(""), 0.f, 0.f, TEXT("inv_00_list"), nullptr },
			{ TEXT("doll"), 0.f, 0.f, TEXT("inv_01_doll_front"), nullptr }, { TEXT("doll"), 180.f, -10.f, TEXT("inv_02_doll_back_prompt"), nullptr },
			{ TEXT("doll_empty"), 180.f, -10.f, TEXT("inv_03_doll_emptied"), TEXT("inspect:doll") }, { TEXT("key_box"), 20.f, 0.f, TEXT("inv_04_small_key"), nullptr },
			{ TEXT("screwdriver"), 25.f, 0.f, TEXT("inv_05_screwdriver"), nullptr }, { TEXT("keep_eye"), 0.f, 0.f, TEXT("inv_06_glass_eye"), nullptr },
			{ TEXT("keep_eye"), 0.f, -55.f, TEXT("inv_07_glass_eye_iris"), nullptr }, { TEXT("key_sitting"), 20.f, 0.f, TEXT("inv_08_brass_key"), nullptr },
			{ TEXT("key_prayer"), 20.f, 0.f, TEXT("inv_09_iron_key"), nullptr }, { TEXT("key_desk"), 20.f, 0.f, TEXT("inv_10_desk_key"), nullptr },
			{ TEXT("key_ell"), 15.f, 0.f, TEXT("inv_11_keyring"), nullptr }, { TEXT("key_attic"), 20.f, 0.f, TEXT("inv_12_long_key"), nullptr },
			{ TEXT("key_cellar"), 20.f, 0.f, TEXT("inv_13_padlock_key"), nullptr }, { TEXT("fuse"), 30.f, 10.f, TEXT("inv_14_fuse"), nullptr },
			{ TEXT("shears"), 35.f, 18.f, TEXT("inv_15_shears"), nullptr }, { TEXT("keep_walter"), 30.f, 20.f, TEXT("inv_16_ring"), nullptr },
			{ TEXT("keep_daniel"), 10.f, 0.f, TEXT("inv_17_tags"), nullptr }, { TEXT("keep_ruth"), 30.f, 10.f, TEXT("inv_18_music_box"), nullptr },
			{ TEXT("pistol"), 0.f, 0.f, TEXT("inv_19_pistol"), nullptr }, { TEXT("!papers"), 0.f, 0.f, TEXT("inv_20_papers"), nullptr },
		};
		static const TCHAR* Give[] = { TEXT("doll"), TEXT("screwdriver"), TEXT("keep_eye"), TEXT("key_sitting"), TEXT("key_prayer"), TEXT("key_desk"), TEXT("key_ell"), TEXT("key_attic"),
			TEXT("key_cellar"), TEXT("fuse"), TEXT("shears"), TEXT("keep_ruth"), TEXT("keep_walter"), TEXT("keep_daniel") };
		const int32 NShots = UE_ARRAY_COUNT(Shots);
		static int32 SetFor = -1;
		if (InvTestStage == 0 && D->PlaySeconds > 7.f && Screen == EWCScreen::None)
		{
			for (const TCHAR* G : Give) D->Items.Add(G);
			int32 n = 0;
			for (TActorIterator<AWCNote> It(GetWorld()); It && n < 9; ++It, ++n) D->NotesRead.AddUnique(It->WCId);
			D->bBusy = false;
			OpenInventory(D);
			InvTestStage = 1;
			InvTestAt = RealNow + 2.5;
		}
		else if (InvTestStage >= 1 && InvTestStage <= NShots && Screen == EWCScreen::Inventory)
		{
			const FInvShot& S = Shots[InvTestStage - 1];
			if (SetFor != InvTestStage && RealNow > InvTestAt - 1.9)
			{
				SetFor = InvTestStage;
				if (S.Before) D->Event(S.Before);
				TArray<FInvItem> Now;
				BuildInventory(D, Now);
				const bool bPapers = FCString::Strcmp(S.Item, TEXT("!papers")) == 0;
				InvTab = bPapers ? 1 : 0;
				bInvInspect = !bPapers && S.Item[0] != 0;
				for (int32 i = 0; i < Now.Num(); ++i) if (Now[i].Id == FName(S.Item)) InvSel = i;
			}
			if (SetFor == InvTestStage) { InvYaw = S.Yaw; InvPitch = S.Pitch; InvTouchedAt = RealNow; }
			if (RealNow > InvTestAt)
			{
				FScreenshotRequest::RequestScreenshot(InvTestDir / (FString(S.Name) + TEXT(".png")), true, false);
				++InvTestStage;
				InvTestAt = RealNow + 2.2;
			}
		}
		else if (InvTestStage == NShots + 1 && RealNow > InvTestAt)
		{
			++InvTestStage;
			UKismetSystemLibrary::QuitGame(this, PC, EQuitPreference::Quit, false);
		}
	}
'''
s = s[:a] + new + s[b:]
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("pass 105 applied")
