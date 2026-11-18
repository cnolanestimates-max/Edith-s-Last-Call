import io
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"


def sub(f, old, new, count=1):
    s = io.open(R + f, encoding="utf-8").read()
    assert old in s, (f, old[:70])
    s = s.replace(old, new, count)
    io.open(R + f, "w", encoding="utf-8", newline="\n").write(s)


# ---- menu screenshot test: -WCMenuTest=<dir> captures the main menu, settings and controls screens, then quits
sub("WCGame.h", "	bool bSettingsDirty = false;", "	bool bSettingsDirty = false;\n	FString MenuTestDir;\n	int32 MenuTestStage = 0;\n	double MenuTestAt = 0.0;")
sub("WCGame.cpp", '''	if (TitleFont) TitleBaseH = FMath::Max(TitleFont->GetMaxCharHeight(), 1.f);''', '''	if (TitleFont) TitleBaseH = FMath::Max(TitleFont->GetMaxCharHeight(), 1.f);
	if (FParse::Value(FCommandLine::Get(), TEXT("WCMenuTest="), MenuTestDir))
	{
		MenuTestDir = FPaths::ConvertRelativePathToFull(MenuTestDir);
		IFileManager::Get().MakeDirectory(*MenuTestDir, true);
		MenuTestAt = FPlatformTime::Seconds() + 9.0;
	}''')
sub("WCGame.cpp", '''	if (Screen != EWCScreen::None) DrawMenu(D);
}''', '''	if (Screen != EWCScreen::None) DrawMenu(D);
	if (!MenuTestDir.IsEmpty() && RealNow > MenuTestAt)
	{
		static const TCHAR* Names[] = { TEXT("menu_main"), TEXT("menu_settings"), TEXT("menu_controls") };
		if (MenuTestStage < 3)
		{
			FScreenshotRequest::RequestScreenshot(MenuTestDir / (FString(Names[MenuTestStage]) + TEXT(".png")), true, false);
			++MenuTestStage;
			MenuTestAt = RealNow + 1.5;
			// the next screen is opened a moment after this capture is taken
		}
		else if (MenuTestStage == 3)
		{
			UKismetSystemLibrary::QuitGame(this, PC, EQuitPreference::Quit, false);
			++MenuTestStage;
		}
	}
	else if (!MenuTestDir.IsEmpty() && MenuTestStage > 0 && MenuTestStage < 3 && RealNow > MenuTestAt - 1.0)
	{
		const EWCScreen Want = MenuTestStage == 1 ? EWCScreen::Settings : EWCScreen::Controls;
		if (Screen != Want) { Back = EWCScreen::Main; Open(Want); }
	}
}''')
sub("WCGame.cpp", '#include "Kismet/KismetSystemLibrary.h"', '#include "Kismet/KismetSystemLibrary.h"\n#include "HAL/FileManager.h"\n#include "Misc/CommandLine.h"\n#include "Misc/Paths.h"\n#include "UnrealClient.h"')

# ---- Tab shows what she needs once you have read how to free her
sub("WCGame.cpp", '''		for (const FName& It : D->Items) { Text(ItemName(It), Px(60.f), Y, Px(22.f), Ink); Y += Px(30.f); }''',
    '''		for (const FName& It : D->Items) { Text(ItemName(It), Px(60.f), Y, Px(22.f), Ink); Y += Px(30.f); }
		if (D->NotesRead.Contains(TEXT("note_prayer")) || D->NotesRead.Contains(TEXT("note_cellar")))
		{
			Y += Px(22.f);
			Text(TEXT("WHAT WAS THEIRS"), Px(60.f), Y, Px(17.f), Dim); Y += Px(26.f);
			static const TCHAR* Keep[][2] = { { TEXT("keep_ruth"), TEXT("Ruth's music box (under her bed)") }, { TEXT("keep_walter"), TEXT("Walter's ring (with her knots)") }, { TEXT("keep_daniel"), TEXT("Daniel's tags (his footlocker, attic)") } };
			for (const auto& K : Keep)
			{
				const bool bHave = D->Items.Contains(K[0]);
				Text(FString::Printf(TEXT("%s  %s"), bHave ? TEXT("[x]") : TEXT("[  ]"), K[1]), Px(60.f), Y, Px(22.f), bHave ? Ink : Dim); Y += Px(30.f);
			}
			Text(TEXT("Bring them to where she lies. Cut the three knots."), Px(60.f), Y + Px(6.f), Px(20.f), Dim);
		}''')
print("ok")
