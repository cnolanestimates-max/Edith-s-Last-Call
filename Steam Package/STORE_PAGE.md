# Edith's Last Call: store page text

Draft for the Steam store page. Nothing here has been entered into Steamworks. Every line avoids the ending.

## Name

**Edith's Last Call**

## Short description (Steam limit: 300 characters)

> November 1993. A call comes in from a farmhouse at the end of County Road 9, from a telephone whose cord was cut long ago. You are the deputy on the night shift, and you are going up there alone. A short first-person horror game about a woman who could not bear to be left.

(282 characters.)

Shorter alternative (for ads and the small capsule's hover text, 150 characters):

> 1993. A call from a dead line. One deputy, one farmhouse, one night. A first-person horror story about loneliness and the thing that answered it.

## About this game (long description)

Paste the block below into the "About This Game" field. It uses Steam's own markup (`[h2]`, `[b]`, `[list]`). The image lines are placeholders: upload the matching GIF or screenshot in Steamworks and swap in its link.

```
[h2]Nobody has seen Edith Harrow in over a year. Tonight, she called.[/h2]

Tuesday, November 9, 1993. Ashby County. The overnight shift is quiet until dispatch gets a call: a voice gives an address at the end of County Road 9 and says only that she needs company. The call was placed from the Harrow farmhouse, on a line the phone company cut off long ago.

You are Deputy Cole Brandt. It is a welfare check. Knock, make sure she is alive, call it in. Ten minutes.

The front door is unlocked. The table is set for four. The phone cord has been cut. And someone in this house has been waiting a very long time for somebody to come.

[h2]A slow, close kind of horror[/h2]
Edith's Last Call is a short first-person horror game set in one rotting farmhouse at the end of a forest road. There is no map, no glowing markers and no one coming to help. There is a flashlight, a service pistol with too few cartridges, and a house full of the things a family left behind.

[list]
[*][b]One house, searched by hand.[/b] Twelve rooms, an attic and a cellar, nailed shut from the inside. Find the keys, the fuses and the way through.
[*][b]A story told in what was left.[/b] Notes she pinned up to remember, letters from a daughter who stopped visiting, a son's last letter home, an aide's night log, and home videos that still play on the old TV/VCR.
[*][b]She will not let you go.[/b] You cannot kill what lives in this house. Gunfire only buys you time.
[*][b]A build that takes its time.[/b] Minutes of nothing but the house: a thump overhead, a light that goes out, a door you know you shut. Then it starts.
[*][b]1993, down to the grain.[/b] A rural Victorian farmhouse, a cruiser with a radio and no cell phones, and an optional VHS camcorder filter that is on by default.
[*][b]Short and finished.[/b] One sitting, about 60 to 90 minutes, with an ending.
[/list]

[h2]Content warning[/h2]
Edith's Last Call deals with dementia, grief, the death of a child in war, neglect of the elderly, and the supernatural. It contains frightening images, sudden loud sounds and moments of violence against the player character.
```

## Content descriptors (Steam's mature content survey, suggested answers)

- Frequent violence or gore: **No.** Some violence or gore: **Yes** (the creature knocks the player down; disturbing body imagery; firearm use against a supernatural creature).
- Adult only sexual content, nudity: **No.**
- General mature content: **Yes.** Suggested text: "Frightening imagery, sudden loud sounds, themes of grief, dementia and elder neglect."

## AI content disclosure (Steam requires this)

Steam asks whether the game or its store page uses AI-generated content. Answer truthfully when filling it in. What we know is used:
- **Store art:** the key art and capsule backgrounds in this folder were made with an AI image model (Higgsfield, Nano Banana Pro) using in-game captures of Edith and the house as references. Title lettering was set by hand.
- **In the game:** Higgsfield was used for the VHS tape footage (per `PRODUCTION_STATUS.md`), and the deputy, dispatch and Edith voice lines were made with text-to-speech. Cheyenne should confirm the full list before answering.

## Languages

English (interface, full audio, subtitles).

## Draft system requirements

Measured on the development laptop only (RTX 5070 Laptop GPU, 8 GB; editor game mode, 1280x720): mean frame 11 ms (about 90 fps). No packaged build has been measured yet, so treat these as placeholders until it has.

| | Minimum | Recommended |
|---|---|---|
| OS | Windows 10 64-bit | Windows 11 64-bit |
| Processor | 4-core, 3.0 GHz (Intel Core i5-8400 / Ryzen 5 2600) | 6-core (Intel Core i5-12400 / Ryzen 5 5600) |
| Memory | 8 GB RAM | 16 GB RAM |
| Graphics | GTX 1060 6 GB / RX 580, DirectX 12 | RTX 3060 / RX 6600 XT |
| Storage | 10 GB (to confirm against the package) | SSD |
