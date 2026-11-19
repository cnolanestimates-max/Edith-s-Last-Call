# Pass 130 (Cheyenne, 21:24 / 21:25 UTC): "this is set around the 90s ... all the notes and stuff updated to reflect
# that"; "all the notes, diaries and pictures that have dates need to tell the story from around the 70s on".
# The deputy's night is Tuesday, November 9, 1993.  The whole line of dates is in Docs/TIMELINE.md; this puts them on
# the papers (notes.json) and on the things he can look at (looks.py).  Nothing is re-voiced here (the three dispatch
# lines that needed it were done in pass 129).
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

ROOT = r"C:\GameDev\Unreal\WellnessCheck"
NP = ROOT + r"\Scripts\level\notes.json"
d = json.load(open(NP, encoding="utf-8"))


def sub(key, old, new, field="body"):
    assert old in d[key][field], (key, old)
    d[key][field] = d[key][field].replace(old, new, 1)


def head(key, line):
    if not d[key]["body"].startswith(line):
        d[key]["body"] = line + "\n\n" + d[key]["body"]


sub("note_mail", "FINAL NOTICE\n", "FINAL NOTICE\nOctober 4, 1993\n")
sub("note_mail", "September 2 of last year", "September 2, 1992")
head("note_letter1", "December 27, 1990")
head("note_calendar", "SEPTEMBER 1992")
head("note_grocery", "Sept. 23, 1992")
head("note_diary1", "January 14, 1990")
head("note_diary2", "March 1990")
sub("note_walter", "ASHBY COURIER\n", "ASHBY COURIER\nThursday, October 19, 1989\n")
head("note_ruth", "November 15, 1989")
d["note_kids"]["title"] = "A child's letter, in crayon. Pencilled on the back: Christmas 1969"
sub("note_doctor", "ASHBY COUNTY CLINIC\n", "ASHBY COUNTY CLINIC\nApril 3, 1990\n")
sub("note_aide1", "Client: HARROW, E.\n", "Client: HARROW, E.\nWeek of July 20, 1992\n")
sub("note_aide2", "Not for the county.\n", "Not for the county.\nAugust 1992.\n")
head("note_aide3", "September 6, 1992")
sub("note_box", "November 14\n", "November 14, 1990\n")
json.dump(d, open(NP, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

edit(ROOT + r"\Scripts\level\looks.py", [
    ('"Newspapers still in their bands. The oldest is fourteen months back."', '"Newspapers still in their bands. The oldest is September of 1992, fourteen months back."'),
    ('"Scrapbooks. Ruth\'s school reports, Danny\'s ribbons. The last page of each one is torn out."', '"Scrapbooks. Danny\'s ribbons from the county fair, 1961. Ruth\'s school reports, 1967 to 1979. The last page of each one is torn out."'),
    ('"Preserves, labelled by year. The newest ones are not fruit."', '"Preserves, labelled by year. 1974. 1981. 1988. The newest ones are not fruit."'),
    ("'E.H. March.' Then April, a hand higher.", "'E.H. March 1992.' Then April, a hand higher."),
    ('"A boy in a uniform that doesn\'t fit yet, squinting at the sun. The glass is clean."', '"A boy in a uniform that doesn\'t fit yet, squinting at the sun. \'Fort Polk, 1968\' on the mat. The glass is clean."'),
    ("Every tag says 'To Danny' or 'To Ruth.' Forty years of them. None opened.", "Every tag says 'To Danny' or 'To Ruth.' One for every Christmas since 1969. None opened."),
])
print("pass 130 applied")
