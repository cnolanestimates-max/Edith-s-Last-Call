# Pass 127: the bot can do the yard the way a person has to (-WCOutside): knock, no answer, the shed, the tape, the
# trash can going over behind him, back round to the front, in.  It is carried between the places (there are no bot
# waypoints round the outside of the house); what is being checked is that nothing in that sequence brings the game down.
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

edit(r"C:\GameDev\Unreal\WellnessCheck\Source\WellnessCheck\WCAuto.cpp", [
    ("""	Go(TEXT("A_Porch")); Shot(TEXT("02_porch"));
	Use(TEXT("front")); Flag(TEXT("door_opened"), 30.f); Wait(4.f); Shot(TEXT("03_door_ajar"));
""",
     """	Go(TEXT("A_Porch")); Shot(TEXT("02_porch"));
	if (FParse::Param(FCommandLine::Get(), TEXT("WCOutside")))
	{
		Use(TEXT("front")); Flag(TEXT("knocked_first"), 10.f); Wait(9.f); Shot(TEXT("02b_no_answer"));
		AutoSteps.Add({ A_Tele, TEXT("A_Shed"), 0.f }); Wait(2.5f); Shot(TEXT("02c_at_the_shed"));
		AutoSteps.Add({ A_Do, TEXT("at:3790,-745,59,-22,-28"), 0.f }); Wait(1.5f); Shot(TEXT("02d_shed_tape"));
		Use(TEXT("pick_tape1")); Flag(TEXT("tape1_taken"), 15.f); Wait(8.f);
		AutoSteps.Add({ A_Do, TEXT("at:3140,-470,59,140,-18"), 0.f }); Wait(1.5f); Shot(TEXT("02e_trash_can_over"));
		AutoSteps.Add({ A_Tele, TEXT("A_Porch"), 0.f }); Wait(1.5f);
	}
	Use(TEXT("front")); Flag(TEXT("door_opened"), 30.f); Wait(4.f); Shot(TEXT("03_door_ajar"));
"""),
])
print("pass 127 applied")
