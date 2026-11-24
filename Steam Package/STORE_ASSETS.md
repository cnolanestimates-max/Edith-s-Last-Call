# Store assets: what each file is and where it goes in Steamworks

Made 2026-11-24. Nothing has been uploaded to Steam.

## Capsules (`capsules/`)

| File | Size | Steamworks slot |
|---|---|---|
| `header_capsule_920x430.jpg` | 920x430 | Store Assets > Header Capsule |
| `small_capsule_462x174.jpg` | 462x174 | Store Assets > Small Capsule |
| `main_capsule_1232x706.jpg` | 1232x706 | Store Assets > Main Capsule |
| `vertical_capsule_748x896.jpg` | 748x896 | Store Assets > Vertical Capsule |
| `page_background_1438x810.jpg` | 1438x810 | Store Assets > Page Background (optional) |
| `library_capsule_600x900.jpg` | 600x900 | Library Assets > Library Capsule |
| `library_hero_3840x1240.jpg` | 3840x1240 | Library Assets > Library Hero (no text, as Steam asks) |
| `library_logo_1280.png` | 1280x351, transparent | Library Assets > Library Logo |
| `event_cover_800x450.jpg` | 800x450 | Events > cover image |
| `event_header_1920x622.jpg` | 1920x622 | Events > header image |
| `key_art_wide_clean_3840x2160.jpg`, `key_art_wide_titled_3840x2160.jpg`, `key_art_vertical_clean_3712x4608.jpg` | | Press kit, social posts, itch.io, trailer thumbnail |

**How the art was made.** The two key art paintings were generated on Higgsfield (Nano Banana Pro, 4K, 4 credits each, 8 in all) with in-game captures of Edith and the house as reference. On 2026-11-24 Edith was edited out of both (Nano Banana Pro edit, 4 credits each, 16 in all) because Cheyenne wants the monster kept out of the promo: the house now has an empty open doorway and the hallway is empty. The title lettering is set in Baskerville Old Face (a Windows/Office font) with hand-made wear; `Tools/` has the scripts that rebuild every capsule from the two paintings. Steam's AI disclosure form must mention the AI-made store art (see `STORE_PAGE.md`).

**Things to check before upload:** Steam rejects capsules whose text is unreadable at small size; the small capsule is the one to look at on a phone. Either painting can be regenerated for 4 credits if a detail is wrong for the game.

## Screenshots (`screenshots/`)

1920x1080 JPG, no HUD, every one a real frame from the game (no paint-over). Steam needs at least 5; upload them in the order of their numbers. Where each frame came from is in `screenshots/SOURCES.md`.

## Trailer (`trailer/`)

See `trailer/TRAILER_NOTES.md` for the cut, the sources, the music credits and where the full-quality file lives.

## Text

- `STORE_PAGE.md`: short and long descriptions (in Steam markup), content descriptors, AI disclosure, draft system requirements.
- `ANNOUNCEMENT.md`: the first announcement event, plus a short social post.
- `TAGS.md`: twenty tags in order, genres, and comparable games.
