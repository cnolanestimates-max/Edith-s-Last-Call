# Text cards for the trailer: 1920x1080 PNG, bone-white Baskerville on black (or transparent for overlays).
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from logo import make_logo
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
F = 'C:/Windows/Fonts/BASKVILL.TTF'
COL = (226, 218, 198)

def card(name, lines, size=64, track=6, transparent=False, y=None):
    im = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0 if transparent else 255))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(F, size)
    hs = [font.getbbox('Hg')[3] for _ in lines]
    total = sum(hs) + (len(lines) - 1) * size * 0.55
    yy = (1080 - total) / 2 if y is None else y
    for ln, h in zip(lines, hs):
        w = sum(d.textlength(c, font=font) for c in ln) + track * (len(ln) - 1)
        x = (1920 - w) / 2
        if transparent:   # soft shadow so it reads over footage
            sh = Image.new('L', (1920, 1080), 0); sd = ImageDraw.Draw(sh); xx = x
            for c in ln: sd.text((xx, yy), c, font=font, fill=255); xx += d.textlength(c, font=font) + track
            sh = sh.filter(ImageFilter.GaussianBlur(10))
            im.alpha_composite(Image.merge('RGBA', (Image.new('L', (1920, 1080), 0),) * 3 + (sh.point(lambda v: int(v * 0.8)),)))
            d = ImageDraw.Draw(im)
        for c in ln:
            d.text((x, yy), c, font=font, fill=COL + (255,)); x += d.textlength(c, font=font) + track
        yy += h + size * 0.55
    im.save(os.path.join(OUT, name + '.png'))

card('c01_date', ['ASHBY COUNTY', 'NOVEMBER 9, 1993'], 58, 10)
card('c02_welfare', ['A WELFARE CHECK.', 'TEN MINUTES.'], 64, 8)
card('c03_waiting', ['SHE HAS BEEN WAITING', 'A LONG TIME FOR COMPANY'], 64, 8)
card('c04_nobody', ['NOBODY LEAVES', 'EDITH HARROW AGAIN'], 64, 8)
# end card: the logo and the call to action
end = Image.new('RGBA', (1920, 1080), (0, 0, 0, 255))
lg = make_logo(3000); w = 1250; lg = lg.resize((w, int(w * lg.height / lg.width)), Image.LANCZOS)
end.alpha_composite(lg, ((1920 - lg.width) // 2, 330))
d = ImageDraw.Draw(end); font = ImageFont.truetype(F, 46)
t = 'WISHLIST NOW ON STEAM'; tr = 9
w = sum(d.textlength(c, font=font) for c in t) + tr * (len(t) - 1); x = (1920 - w) / 2
for c in t: d.text((x, 760), c, font=font, fill=COL + (255,)); x += d.textlength(c, font=font) + tr
end.save(os.path.join(OUT, 'c09_end.png'))
print('ok')
