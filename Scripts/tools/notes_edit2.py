import json
P = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/notes.json"
n = json.load(open(P, encoding="utf-8"))
n.update({
    "note_doctor": {"title": "A letter from the county clinic", "style": 0, "body":
        "ASHBY COUNTY CLINIC\n\nMrs. Harrow,\n\nAs I explained on the telephone, the tests confirm what we discussed. It is dementia, and it is progressing. You should not be living alone in that house.\n\n"
        "I have written to your daughter twice. I have had no reply.\n\nThe county can send a home aide three days a week. Her name is Mrs. Pruitt. Please let her in when she knocks.\n\nDr. H. Vance\n\n\n"
        "Across the bottom, in pencil, pressed hard:\n\nI AM NOT ALONE"},
    "note_aide1": {"title": "A care chart on a clipboard", "style": 0, "body":
        "ASHBY COUNTY HOME CARE\nClient: HARROW, E.\n\nMon. Refused her tablets. Asked me when Walter would be home.\n\nWed. Has not slept. Says it stands at the foot of the bed.\n\n"
        "Fri. Bruising on both wrists. She says she did not do it. Night restraints from today, on Dr. Vance's order, for her own safety.\n\n"
        "Mon. Restraints were undone this morning. Unbuckled, not torn. I did not undo them.\n\nWed. She is taller. I marked her height on the door frame in March. I am not imagining this.\n\nM. Pruitt"},
    "note_rem6": {"title": "A note pinned beside the bed", "style": 1, "body":
        "The lady who comes is PRUITT.\nShe is PAID to come. She is not family.\n\nDo not tell her about the company.\n\nShe will make it leave.\n\nDo not let her make it leave."},
    "note_daniel": {"title": "A letter from Vietnam, kept flat under glass", "style": 1, "body":
        "March 9, 1969\n\nMama,\n\nDon't fuss. It is mostly rain and waiting.\n\nTell Ruthie I got her drawing. It's in my helmet. Tell Dad the truck can wait till I'm home to fix it right.\n\n"
        "Keep my room how it is. I mean it. Don't let Ruthie have my radio.\n\nAnd leave a light on, so I can find the house.\n\nDanny"},
    "note_baby": {"title": "A list, tucked in the cradle", "style": 1, "body":
        "For the little one, when he comes.\n\nBlanket. Done.\nCap. Done.\nBooties. Done.\n\n\nUnderneath, years later, in the shaking hand:\n\nHe did not come.\nThey do not come.\n\nSo I made my own."},
    "note_aide2": {"title": "Mrs. Pruitt's own notebook", "style": 1, "body":
        "Not for the county.\n\nI have moved into the upstairs back room. She should not be alone at night, and nobody else will come.\n\n"
        "Night 3. Something walks the hall after I have strapped her in. It is heavy. It stops outside my door.\n\nNight 5. I put the chair under the knob.\n\n"
        "Night 6. It tried the knob. Then it spoke through the door, in Mrs. Harrow's voice, and asked me to stay. Mrs. Harrow was downstairs. I buckled her in myself.\n\n"
        "Night 7. I am going at first light. God forgive me. I am leaving her with it."},
    "note_aide3": {"title": "A letter, started and not sent", "style": 0, "body":
        "To the Home Care office,\n\nI am giving up the Harrow case as of today. Do not send another girl out there by herself. Send the sheriff.\n\n"
        "And tell whoever goes: the lights still work in that house. The co-op shut the power off in September. I do not know what is burning in those bulbs.\n\nM. Pruitt"},
})
json.dump(n, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(n), "notes")
