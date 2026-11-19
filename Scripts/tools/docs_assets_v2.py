"""Brings Docs/ASSET_AND_VOICE_MANIFEST.md up to date."""
import io
p = "C:/GameDev/Unreal/WellnessCheck/Docs/ASSET_AND_VOICE_MANIFEST.md"
s = io.open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new, 1)


rep('''| Watchers (`AWCWatcher`)''', '''| Her face | Blender shape keys `Sneer` (upper lip lifts on one side) and `Brow` (brow comes down), with `Scream` used at low weights as the jaw; driven every frame in `WCEntity.cpp` (talking, breathing, twitches). | No paid generation. |
| The Company | Her own model drawn in a pure black unlit material (`M_Void`), taller and thinner. | No new asset. |
| Memory figures (Edith, Ruth, a man) | Her own model at human scale, posed; the others as black outlines against the light. | No new asset. |
| Her drawings (6) | Drawn by script with PIL (`Scripts/art/gen_drawings.py`), `SourceArt/Drawings`. | No paid generation. |
| Watchers (`AWCWatcher`)''')
rep('''| 74 dialogue lines |''', '''| Present-day Edith's voice | The same Gemini takes (kept clean in `SourceArt/Audio/VO_dry`), rebuilt by `Scripts/audio/demon_vo.py` as six layers pitched 0.5x to 1.26x and delayed up to 115 ms, with echo. 18 lines. The memory lines (`m_mem1-3`) and her last "thank you" stay as one human voice. | ffmpeg only, no paid generation. |
| Her footsteps (`her_step_01-04`) | Library: one Sonniss wet wood hit, pitched down, over our own wood step slowed to 0.55x (`lib_sfx.py`). | No paid generation. |
| 85 dialogue lines in all (the 74 below plus 11 added on 2026-11-18: three memory lines, two laughs, two cries, three whispers, a hum) | Generated: Google Gemini TTS, voice gacrux. | |
| 74 dialogue lines |''')
rep('''Nothing has been spent on Higgsfield since. Google TTS since then: 2 short lines (the deputy's two re-written radio lines).''',
    '''Nothing has been spent on Higgsfield since. Google TTS since then: 13 short lines (the deputy's two re-written radio lines and
Edith's eleven new ones). The pistol, the face, the drawings, the footsteps and the many-voiced treatment cost nothing.''')
rep('''24 readable notes''', '''26 readable notes''')
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("asset manifest updated")
