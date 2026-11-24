# Title lettering for Edith's Last Call: transparent PNG, distressed bone-white serif with a soft dark halo.
import sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

FONT = 'C:/Windows/Fonts/BASKVILL.TTF'

def tracked(draw, xy, text, font, track, fill):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track
    return x

def width(draw, text, font, track):
    return sum(draw.textlength(c, font=font) for c in text) + track * (len(text) - 1)

def make_logo(W=2400, seed=3):
    H = int(W * 0.42)
    big = ImageFont.truetype(FONT, int(W * 0.175))
    small = ImageFont.truetype(FONT, int(W * 0.062))
    t1, t2 = "EDITH\u2019S", 'LAST CALL'
    tr1, tr2 = W * 0.032, W * 0.012
    d0 = ImageDraw.Draw(Image.new('L', (8, 8)))
    w2 = width(d0, t2, big, tr2)
    W = int(w2 * 1.1)                       # canvas wide enough for the big line, with a margin for the halo
    mask = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(mask)
    w1, w2 = width(d, t1, small, tr1), width(d, t2, big, tr2)
    y1 = int(H * 0.06); y2 = int(H * 0.30)
    tracked(d, ((W - w1) / 2, y1), t1, small, tr1, 255)
    tracked(d, ((W - w2) / 2, y2), t2, big, tr2, 255)
    # thin rule either side of EDITH'S
    ry = y1 + int(small.size * 0.62)
    gap = W * 0.03
    d.rectangle([(W - w2) / 2, ry, (W - w1) / 2 - gap, ry + max(2, W // 900)], fill=200)
    d.rectangle([(W + w1) / 2 + gap, ry, (W + w2) / 2, ry + max(2, W // 900)], fill=200)
    # distress: speckle holes and blotchy wear (PIL only)
    speck = Image.effect_noise((W, H), 40).point(lambda v: 150 if v < 20 else 255)
    blot = Image.effect_noise((W // 6, H // 6), 90).resize((W, H), Image.BICUBIC).point(lambda v: max(0, min(255, int(140 + (v - 128) * 1.4))))
    alpha = ImageChops.multiply(ImageChops.multiply(mask, speck), blot.point(lambda v: min(255, v + 150)))
    alpha = alpha.filter(ImageFilter.GaussianBlur(W / 2400 * 0.8))
    # colour: bone white with a faint warm cast
    col = Image.new('RGB', (W, H), (226, 218, 198))
    text = Image.merge('RGBA', (*col.split(), alpha))
    # halo for legibility on busy art
    halo = mask.filter(ImageFilter.GaussianBlur(W / 60))
    halo = halo.point(lambda v: int(min(255, v * 1.6)))
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shadow.putalpha(halo.point(lambda v: int(v * 0.75)))
    out = Image.alpha_composite(shadow, text)
    return out.crop(out.getbbox())

if __name__ == '__main__':
    lg = make_logo(int(sys.argv[2]) if len(sys.argv) > 2 else 2400)
    lg.save(sys.argv[1])
    print(lg.size)





