"""Pass 94: the deputy's commentary (Cheyenne 2026-11-19 14:45 and 14:47 UTC).
Voice and subtitles stay for him and dispatch, and him and Edith.  Every other spoken remark goes, and so does the on-screen
thought text after pick-ups and events ("when you have to tell somebody they should be scared, it's not scary anymore").
What stays as text: bare feedback when something he tries cannot be done ("Locked.", "Nailed shut."), and the description he
gets when the PLAYER chooses to look at a thing."""
import re, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('void Think(const FString& Text, float Seconds = -1.f);', '''void Think(const FString& Text, float Seconds = -1.f);      // his thoughts: no longer shown (kept in the code as a record of what each moment is)
	void Feedback(const FString& Text, float Seconds = -1.f);   // bare feedback on something he tried, and what he sees when the player chooses to look'''),
])
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''static const TSet<FName> Muted = { TEXT("d_locked"), TEXT("d_cellar_locked"), TEXT("d_window"), TEXT("d_backdoor"), TEXT("d_table"), TEXT("d_photos"),
		TEXT("d_foyer"), TEXT("d_wayout"), TEXT("d_drawer"), TEXT("d_sitting"), TEXT("d_kidsdoor"), TEXT("d_musicbox"), TEXT("d_prayer"), TEXT("d_ring"),
		TEXT("d_attic"), TEXT("d_after_attic"), TEXT("d_cellar"), TEXT("d_shelf"), TEXT("d_dawn"), TEXT("d_need"), TEXT("d_leave_early"), TEXT("d_phone_ring") };''',
     '''// 2026-11-19: only what he says to dispatch and to Edith is left.  Remarks to himself, about what he finds or what it
	// means, are all gone (voice and subtitle).
	static const TSet<FName> Muted = { TEXT("d_locked"), TEXT("d_cellar_locked"), TEXT("d_window"), TEXT("d_backdoor"), TEXT("d_table"), TEXT("d_photos"),
		TEXT("d_foyer"), TEXT("d_wayout"), TEXT("d_drawer"), TEXT("d_sitting"), TEXT("d_kidsdoor"), TEXT("d_musicbox"), TEXT("d_prayer"), TEXT("d_ring"),
		TEXT("d_attic"), TEXT("d_after_attic"), TEXT("d_cellar"), TEXT("d_shelf"), TEXT("d_dawn"), TEXT("d_need"), TEXT("d_leave_early"), TEXT("d_phone_ring"),
		TEXT("d_phonecord"), TEXT("d_masterempty"), TEXT("d_doorstuck"), TEXT("d_getup1b"), TEXT("d_getup2"), TEXT("d_tags") };'''),
    ('''void AWCDirector::Think(const FString& Text, float Seconds)
{
	FWCSubtitle Sub;''', '''void AWCDirector::Think(const FString& Text, float Seconds)
{
	// not shown any more: the player works it out without him pointing at it
}

void AWCDirector::Feedback(const FString& Text, float Seconds)
{
	FWCSubtitle Sub;'''),
    ('Think(TEXT("Not until I\'ve laid eyes on her."));', 'Feedback(TEXT("Not yet."));'),
    ('Think(TEXT("It will not open."));', 'Feedback(TEXT("It will not open."));'),
    ('Think(TEXT("Padlocked from this side. The cellar."));', 'Feedback(TEXT("Padlocked."));'),
    ('Think(TEXT("Locked. A newer lock than the others. The man of the house would have kept the key."));', 'Feedback(TEXT("Locked."));'),
    ('Think(TEXT("The attic. Locked. Danny\'s things are up there."));', 'Feedback(TEXT("Locked."));'),
    ('Think(TEXT("Locked. Scratches round the keyhole, from the inside."));', 'Feedback(TEXT("Locked."));'),
    ('Think(TEXT("Locked."));', 'Feedback(TEXT("Locked."));'),
    ('Think(TEXT("Nailed shut. From the inside."));', 'Feedback(TEXT("Nailed shut."));'),
    ('Think(TEXT("Nailed shut from the inside. Every board."));', 'Feedback(TEXT("Nailed shut."));'),
    ('Think(TEXT("Not yet. She needs what was theirs. All three."));', 'Feedback(TEXT("Not yet."));'),
    ('Think(TEXT("Nothing to cut it with. She said scissors. The sewing room."));', 'Feedback(TEXT("Nothing to cut it with."));'),
])
edit(R + "Source/WellnessCheck/WCHouse.cpp", [
    ('Think(TEXT("It won\'t come on."));', 'Feedback(TEXT("Dead."));'),
    ('Think(TEXT("One fuse is blown black. I need a spare."));', 'Feedback(TEXT("A fuse is blown."));'),
    ('Think(TEXT("The roll-top is locked. A small brass lock."));', 'Feedback(TEXT("Locked."));'),
])
edit(R + "Source/WellnessCheck/WCWorld.cpp", [
    ('D->Think(Text);\n\t\tD->Event(FName(*FString::Printf(TEXT("look:%s")', 'D->Feedback(Text);\n\t\tD->Event(FName(*FString::Printf(TEXT("look:%s")'),
])
edit(R + "Source/WellnessCheck/WCEvents.cpp", [
    ('''Think(TEXT("The switch is low on the front. I have to get right down to it."));
				ShowHint(''', '''ShowHint('''),
])
print("pass 94 applied")
