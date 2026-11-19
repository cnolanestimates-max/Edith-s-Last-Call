"""Brings Docs/STORY_AND_ENTITY_BIBLE.md up to date: the Company, her drawings, the memories, her voice and face, her feet."""
import io
p = "C:/GameDev/Unreal/WellnessCheck/Docs/STORY_AND_ENTITY_BIBLE.md"
s = io.open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new, 1)


rep('''- **Sound:** a wet, rattling breath; the scream; a short hurt shriek when she is driven off; her own voice, close and gentle, when she
  speaks. The house answers her: a floorboard under weight, a switch clicking off, a door that was shut.''',
    '''- **Face:** never still. The jaw hangs a little and works when she speaks; the brow creeps down over the eye; one side of the
  upper lip twitches up off black teeth. When she screams the mouth opens far too long, down to her collar bone.
- **Sound:** her feet first: bare, heavy, wet, on boards that creak under her weight. A wet, rattling breath; the scream; a short
  hurt shriek when she is driven off. Her voice now is many voices at once, some far too low, a little out of step with each other.
  Only in the memories does she sound like one old woman. Around the house, quietly: a laugh in another room, crying behind a wall,
  humming, a whisper at the ear. The house answers her: a floorboard under weight, a switch clicking off, a door that was shut.''')
rep('''  height in the dark -> under the bed -> in the rocking chair -> crawling in the attic -> sprinting the hall -> face to face in the cellar.''',
    '''  height in the dark -> only her arm, from under a bed -> in the rocking chair -> crawling in the attic -> sprinting the hall -> face
  to face in the cellar.  Alongside, for anyone who looks: an eye in a hole in the wall, hair hanging from the rafters.

## Entity bible: the Company

- **What it is:** what answered her on the ninth night. It has no name; in her notes and drawings it is "my friend", "the Company",
  "him". It gave her exactly what she asked for, never to be alone, by moving in.
- **Look:** a standing black outline about nine feet tall with no face, no features and no light on it at all, like a hole cut in
  the room. It never moves while it is looked at and it never comes closer.
- **Behaviour:** it is seen at most four times, only after the first sight of Edith, at the far end of a room or hall. When the
  light finds it the light stutters, and the corner is empty. It does not attack; Edith does that. It watches what it owns.
- **Her drawings:** Edith has gone back to being a child. Crayon drawings on her sitting-room wall and around the house show a
  small figure in a nightgown holding hands with a tall black one, the two of them at supper ("SUPPER FOR 2"), and in a
  child's letters "HE NEVER LEVES". It is the only one who did not leave her.
- **The memories:** each of the first three times she has hold of him he sees one, in order: the last Thanksgiving, her
  family going out of the front door while she asks them to stay; the attic, where she finds her grandmother's book under
  Danny's things; the ninth night, the candles, and the tall black shape in the corner. He later finds the same book in the attic.''')
rep('''| 10 | Ruth's room | Take the music box | Letter to Santa | **S7 under the bed** |''',
    '''| 10 | Ruth's room | Walk in; watch; then get the music box back from under the bed | Letter to Santa | **S7 the hand under the bed** (slow) |''')
rep('''| 8 | Sitting room | Unlock | Diary 2, Ruth's letter, drawings; iron key, desk key | |''',
    '''| 8 | Sitting room, den | Unlock; read where the desk key is; pull the settlers' book | Diary 2, Ruth's letter, her drawings of her friend; iron key; desk key in the hollow book | **S10 her eye behind the book** |''')
rep('''| 6 | Pantry, den | Replace the fuse | Lights again | (stalks begin) |''',
    '''| 6 | Pantry, den | Replace the fuse | Lights again | (hunts begin: the first an ambush, later ones announced by her feet; each of the first three grabs shows a memory) |''')
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("bible updated")
