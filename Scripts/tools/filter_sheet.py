"""Before / after sheets for the picture filters: one sheet per spot, the six looks side by side with their names.
   python filter_sheet.py <shots dir> <out dir>"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
LOOKS = [("0_off", "NO FILTER (the game as it is now)"), ("1_vhs", "1  VHS CAMCORDER"), ("2_oldfilm", "2  OLD FILM"),
         ("3_cold", "3  COLD, DRAINED"), ("4_bodycam", "4  FISHEYE BODYCAM"), ("5_nightvision", "5  BLACK-AND-WHITE NIGHT VISION")]
SPOTS = [("a_hall", "front hall"), ("b_television", "television"), ("c_edith", "Edith in the hall"), ("d_house", "the house from the yard")]
try:
    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 26)
except Exception:
    font = ImageFont.load_default()
W, H, PAD = 960, 540, 6
for spot, title in SPOTS:
    sheet = Image.new("RGB", (3 * W + 4 * PAD, 2 * H + 3 * PAD), (18, 18, 18))
    n = 0
    for i, (key, label) in enumerate(LOOKS):
        f = os.path.join(src, f"{spot}_{key}.png")
        if not os.path.exists(f):
            continue
        im = Image.open(f).convert("RGB").resize((W, H), Image.LANCZOS)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, d.textlength(label, font=font) + 28, 44), fill=(0, 0, 0))
        d.text((14, 8), label, fill=(255, 230, 90), font=font)
        sheet.paste(im, (PAD + (i % 3) * (W + PAD), PAD + (i // 3) * (H + PAD)))
        n += 1
    if n:
        p = os.path.join(out, f"filters_{spot}.jpg")
        sheet.save(p, quality=90)
        print(p, n)
