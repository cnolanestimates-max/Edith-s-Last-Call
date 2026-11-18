import io, json
R = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
n = json.load(io.open(R + "notes.json", encoding="utf-8"))
n["note_rem1"] = {"style": 1, "title": "A note pinned by the front door",
                  "body": "EDITH.\n\nYour name is Edith Harrow.\nThis is your house. You live here.\n\nDo not go out. You get lost.\n\nIf somebody knocks, it is Ruth.\nIt is not Ruth. Ruth does not come."}
n["note_rem2"] = {"style": 1, "title": "A note stuck to the wall by the stove",
                  "body": "The stove is OFF. You checked.\n\nDo not check again.\n\nYou checked.\n\nYou checked.\n\nCheck."}
n["note_rem3"] = {"style": 1, "title": "A note on the sideboard",
                  "body": "Set FOUR places.\nWalter. Ruth. Danny. Me.\n\nWalter is dead. Do NOT set his place.\n\nSet his place. He gets cross.\n\nSupper is at six. If they are late, keep it warm.\nThey are only late."}
n["note_rem4"] = {"style": 1, "title": "A list on the hall table, written over and over",
                  "body": "Ruth called Tuesday.\nRuth called.\nRuth called?\nDid Ruth call.\nRuth did not call.\n\nRUTH DID NOT CALL\n\nWho is Ruth"}
n["note_rem5"] = {"style": 1, "title": "A note on the bathroom mirror",
                  "body": "That is YOU in the mirror.\nDo not be frightened of her.\n\n\nUnderneath, in a different, harder hand:\n\nThat is not me in the mirror.\nShe is too tall."}
json.dump(n, io.open(R + "notes.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
p = R + "build_house.py"
s = io.open(p, encoding="utf-8").read()
a = 'log("dressing done")'
assert a in s
s = s.replace(a, '''# her reminders to herself, from when she could still write them
note("note_rem1", "Newspaper_Single", 19, 110, GZ + 150, 0, scale=0.5, roll=90, grab=(6, 20, 22))
note("note_rem2", "Newspaper_Single", 1240, 583, GZ + 150, 0, scale=0.5, pitch=0, roll=90, grab=(20, 6, 22))
note("note_rem3", "Letters_Scattered", 420, 555, GZ + 96, 30, scale=0.6)
note("note_rem4", "Letters_Scattered", 1520, 150, UZ + 99, 80, scale=0.6)
note("note_rem5", "Newspaper_Single", 1250, -581, UZ + 120, 0, scale=0.45, roll=90, grab=(20, 6, 22))
log("dressing done")''', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok", len(n))
