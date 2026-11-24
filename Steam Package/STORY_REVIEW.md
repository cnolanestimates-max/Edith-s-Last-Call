# Story and dialogue review, 2026-11-24

Everything the player can read or hear was checked against `Docs/TIMELINE.md`: the 26 notes (`Scripts/level/notes.json`),
the examine lines (`looks.py`, overridden in part by `harrow_progression.py` and `WCFamilyPhotos.cpp`), the 100 voice
lines (`WCStory.cpp` line table), inventory items (`WCGame.cpp`), objectives and feedback lines. Every date's weekday was
computed (Walter died on a Tuesday, the Courier ran on a Thursday, November 9, 1993 is a Tuesday: all correct).

The restored deputy lines are all present and unchanged: table set for four, phone cord, drawings "taller each time",
Ruth's music box, knots in her hair, dog tags, "a draft behind this". Nothing in the stairwell/hall ending or Edith's attack
audio was touched.

## Fixed and pushed (commit 16f68e9, text only, no voiced words changed)

Shows in game after the next C++ build and level/items step (the editor was open, so nothing was rebuilt).

| Where | Was | Now | Why |
|---|---|---|---|
| Drawings (look) | "She was eighty-six." | "She was seventy." | She is 72 on the night; drawn 1990 to 1992 |
| Diary, Jan 1990 | alone "for nineteen years" | "for twenty years" | Danny died March 1969 |
| Care chart | "I marked her height on the door frame in March" | "She has marked her own height on the door frame every month since March. Today I measured it myself." | Pruitt only started in July 1992; the frame says "E.H. March 1992" |
| Care chart | "Week of July 20" with two Mondays | "Weeks of July 20 and 27" | Two weeks of entries |
| Care chart | "tablets" | "pills" | American |
| Pruitt's letter, Sept 6 | power off "in September" | "on the second" | Written in September |
| Telegram | to MRS EDITH HARROW | MR AND MRS WALTER J HARROW | How the Army addressed parents in 1969 |
| Linen log | "Edith asked", "Pruitt's linen log" | "Mrs. Harrow asked", "Mrs. Pruitt's linen log" | Pruitt calls her Mrs. Harrow everywhere else |
| Aide's suitcase (look) | tape "tucked among her things" | "packed and buckled." | The tape is on her bed (`pick_tape2`, linen log) |
| Tape loan slip | "check the suitcase" | "check her bed" | Same |
| Den shelf card, typewriter | Walter writes "Desk key inside" himself; "Walter typed one line" | the key hint is in her pencil; the line is hers again ("i will not be put in a home") | Her note says "He thinks I do not know"; Walter died before the dementia |
| Gun cabinet | "box of cartridges" by a shotgun rack | "box of pistol cartridges" | He takes them for his pistol |
| Everywhere | Mrs Pruitt, mould, labelled, pyjamas, grey, round the, any more, Synthesised, alright | Mrs., mold, labeled, pajamas, gray, around, anymore, Synthesized, all right | 1993 rural America |

## Needs Cheyenne: voice or story beats (not changed)

1. **The knock contradicts the call (re-record `d_knock`).** He says "Your daughter asked us to check on you," but dispatch
   said the caller left no name, and later the call came from Edith's own phone. Proposed: "Sheriff's office! Mrs. Harrow?
   We got a call asking us to check on you."
2. **"Every face scratched out. Every one but hers." (`d_photos`)** no longer matches the photos: the hall portrait says the
   women's eyes are cut (Edith is one), and Walter's photo is untouched. Either re-record as "Every face scratched out. All
   but Walter's." or I change the photo text to match the line (text only, my pick if you have no preference).
3. **Your rule "never tell the player what to fear" is broken by item text at the start.** The flashlight ("It goes dim when
   she is close") and pistol ("It does not hurt her... three or four shots and she goes") descriptions, and the hint "She
   cannot be killed, but enough shots drive her off", tell the player about her before they meet her. Proposed: flashlight
   "County issue, three cells."; pistol "Service pistol. Eight to the magazine."; hint "Right Mouse: raise your pistol." The
   deputy then learns it in the moment ("But she flinched. Every shot, she flinched." already does this). Text only.
4. **Walter labels his own secret key (`WCHouse.cpp`, desk tag).** "A tag under the handle reads: W. Harrow. Desk key in
   First Settlers" contradicts her note. Proposed: "Locked. Under the handle, in her pencil: W. keeps the key in First
   Settlers. Living room, shelf by the stairs." (Left alone because another worker has open changes in that file.) The key
   is now hinted five times (her note, the bath note, the shelf card, the typewriter, the tag); two would do.
5. **The home tapes.** "Ruthie - bedtime, Oct. 1991": Ruth is 30 in 1991. It works if Edith, confused, calls a grandchild
   Ruthie, but nothing says so. And the Thanksgiving tape's burned-in stamp is Nov 24, 1991; Thanksgiving that year was
   Nov 28. Either re-stamp the picture or label it "the Sunday before Thanksgiving".
6. **Dawn timing (`r_end1`).** Arrival 3:07 a.m. plus "almost five hours" is about 8 a.m., full daylight in November; the
   ending wants first light. "Almost four hours" fits (re-record).
7. **Edith's voice direction** in `gen_vo.py` still says "late eighties" (the old character); she is 72. Only matters for
   any line generated again.
8. **Daniel's stone** says they never got him back to bury, but his tags are in his footlocker and the telegram reads as an
   ordinary death notice. Optional: "1949 - 1969. The grass on this one is kept short."

## Pacing

On paper it follows your shape: 8 to 10 minutes of the house alone, first sight gated by the doll chain, the big set pieces
(long hall, phone, head by the ceiling) in the middle, quiet sightings between, the cellar last. Two risks to check in play:
- The book scare (her eye behind First Settlers) is not gated. A player who tries Walter's desk early gets told where the
  book is and could see her eye before the first sighting.
- From the long hall to the cellar there are eight authored scares plus repeating hunts. `Rest()` spaces them, but no person
  has timed it; the real-pace run would show whether the middle feels relentless.
