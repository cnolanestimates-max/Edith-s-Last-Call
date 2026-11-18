"""Edith's drawings: an old woman with dementia, drawing like a child, the only friend who never left.
Made with PIL only (no paid generation).  Writes SourceArt/Drawings/draw_<n>.png (512 x 640, yellowed paper)."""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Drawings"
os.makedirs(OUT, exist_ok=True)
W, H = 512, 640
FONT = next((f for f in ("C:/Windows/Fonts/Inkfree.ttf", "C:/Windows/Fonts/comic.ttf", "C:/Windows/Fonts/segoepr.ttf") if os.path.exists(f)), None)
BLACK, RED, BLUE, BROWN, YELLOW, GREY = (22, 20, 22), (150, 32, 28), (40, 60, 120), (96, 62, 34), (190, 150, 40), (120, 116, 110)


def paper(rng):
    im = Image.new("RGB", (W, H), (214, 198, 160))
    px = im.load()
    for _ in range(9000):
        x, y = rng.randrange(W), rng.randrange(H)
        d = rng.randint(-14, 8)
        r, g, b = px[x, y]
        px[x, y] = (max(0, r + d), max(0, g + d), max(0, b + d - 3))
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(5):                                   # damp stains
        x, y, r = rng.randrange(W), rng.randrange(H), rng.randint(40, 120)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(120, 96, 60, rng.randint(14, 30)))
    for y in (H // 3, 2 * H // 3):                       # fold lines
        d.line((0, y + rng.randint(-3, 3), W, y + rng.randint(-3, 3)), fill=(150, 132, 100, 90), width=2)
    return im.filter(ImageFilter.GaussianBlur(0.6))


def crayon(d, pts, col, width=5, rng=None, passes=3):
    """A wobbly, waxy line through pts."""
    for _ in range(passes):
        q = [(x + rng.uniform(-2.2, 2.2), y + rng.uniform(-2.2, 2.2)) for (x, y) in pts]
        d.line(q, fill=col + (rng.randint(120, 200),), width=max(1, width + rng.randint(-1, 1)), joint="curve")


def scribble(d, box, col, rng, n=260, width=5):
    """Fill a shape the way a child does: back and forth, going over the edge."""
    x0, y0, x1, y1 = box
    for _ in range(n):
        y = rng.uniform(y0, y1)
        a, b = rng.uniform(x0 - 6, x0 + (x1 - x0) * 0.4), rng.uniform(x0 + (x1 - x0) * 0.6, x1 + 6)
        t = (y - y0) / max(1.0, (y1 - y0))
        sh = (x1 - x0) * 0.18 * math.sin(t * 3.1)
        d.line((a + sh, y, b + sh, y + rng.uniform(-9, 9)), fill=col + (rng.randint(120, 220),), width=width + rng.randint(-2, 2))


def words(im, text, y, col, rng, size=40):
    d = ImageDraw.Draw(im, "RGBA")
    f = ImageFont.truetype(FONT, size) if FONT else ImageFont.load_default()
    x = 34 + rng.randint(0, 20)
    for ch in text:
        if ch == "\n":
            y += size + 8; x = 34 + rng.randint(0, 24); continue
        t = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((size // 2, size // 3), ch, font=f, fill=col + (230,))
        t = t.rotate(rng.uniform(-11, 11), resample=Image.BICUBIC)
        im.paste(t, (int(x - size // 2), int(y - size // 3 + rng.uniform(-4, 4))), t)
        x += f.getlength(ch) + rng.uniform(1, 5)


def woman(d, x, y, h, rng, col=BLUE):
    """Stick woman: round head, triangle dress, stick arms and legs.  (x, y) = feet."""
    r = h * 0.13
    crayon(d, [(x + r * math.cos(a / 8 * math.pi), y - h + r + r * math.sin(a / 8 * math.pi)) for a in range(17)], col, 4, rng)
    crayon(d, [(x, y - h + 2 * r), (x - h * 0.2, y - h * 0.28), (x + h * 0.2, y - h * 0.28), (x, y - h + 2 * r)], col, 4, rng)
    crayon(d, [(x - h * 0.08, y - h * 0.28), (x - h * 0.09, y)], col, 4, rng)
    crayon(d, [(x + h * 0.08, y - h * 0.28), (x + h * 0.09, y)], col, 4, rng)
    for k in range(7):                                    # hair
        crayon(d, [(x - r + k * r / 3, y - h + r * 0.4), (x - r * 1.3 + k * r / 2.3, y - h + r * 2.6)], YELLOW, 2, rng, 2)
    crayon(d, [(x - r * 0.35, y - h + r * 0.9), (x - r * 0.3, y - h + r)], col, 3, rng, 1)
    crayon(d, [(x + r * 0.35, y - h + r * 0.9), (x + r * 0.4, y - h + r)], col, 3, rng, 1)
    crayon(d, [(x - r * 0.4, y - h + r * 1.4), (x, y - h + r * 1.65), (x + r * 0.4, y - h + r * 1.4)], RED, 3, rng, 2)   # she is smiling
    return (x + h * 0.2, y - h * 0.62)


def friend(d, x, y, h, rng, eye=True):
    """The friend: very tall, all black, long arms, no face but one eye.  (x, y) = feet."""
    w = h * 0.11
    scribble(d, (x - w, y - h * 0.86, x + w, y), BLACK, rng, n=int(h * 1.1))
    scribble(d, (x - w * 0.8, y - h, x + w * 0.8, y - h * 0.84), BLACK, rng, n=int(h * 0.3))
    crayon(d, [(x - w, y - h * 0.78), (x - w * 2.6, y - h * 0.45), (x - w * 2.2, y - h * 0.12)], BLACK, 6, rng, 5)
    crayon(d, [(x + w, y - h * 0.78), (x + w * 2.6, y - h * 0.45), (x + w * 2.2, y - h * 0.12)], BLACK, 6, rng, 5)
    if eye:
        ex, ey, er = x + w * 0.15, y - h * 0.93, max(5, h * 0.022)
        d.ellipse((ex - er, ey - er, ex + er, ey + er), fill=(226, 214, 180, 255))
        d.ellipse((ex - er * 0.4, ey - er * 0.4, ex + er * 0.4, ey + er * 0.4), fill=(10, 10, 10, 255))
    return (x - w * 2.2, y - h * 0.12)


def sheet(n, fn):
    rng = random.Random(1000 + n)
    im = paper(rng)
    d = ImageDraw.Draw(im, "RGBA")
    fn(im, d, rng)
    im = im.filter(ImageFilter.GaussianBlur(0.5))
    im.save(f"{OUT}/draw_{n}.png")


def d1(im, d, rng):          # holding hands
    crayon(d, [(20, 500), (490, 508)], BROWN, 5, rng)
    hand = woman(d, 170, 500, 170, rng)
    fh = friend(d, 350, 500, 400, rng)
    crayon(d, [hand, ((hand[0] + fh[0]) / 2, hand[1] + 18), fh], BLACK, 4, rng)
    words(im, "MY FREND", 540, RED, rng, 46)


def d2(im, d, rng):          # bigger than the house
    crayon(d, [(20, 520), (490, 524)], BROWN, 5, rng)
    crayon(d, [(70, 520), (70, 330), (250, 330), (250, 520)], BROWN, 5, rng)
    crayon(d, [(55, 330), (160, 240), (265, 330)], RED, 5, rng)
    for (wx, wy) in ((100, 360), (190, 360), (100, 440)):
        crayon(d, [(wx, wy), (wx + 34, wy), (wx + 34, wy + 34), (wx, wy + 34), (wx, wy)], BLUE, 3, rng)
    crayon(d, [(180, 520), (180, 450), (220, 450), (220, 520)], BROWN, 4, rng)
    friend(d, 380, 520, 470, rng)
    words(im, "HE IS BIGER\nTHAN THE HOUS", 548, BLACK, rng, 34)


def d3(im, d, rng):          # supper for two
    crayon(d, [(90, 330), (420, 330), (420, 350), (90, 350), (90, 330)], BROWN, 5, rng)
    crayon(d, [(110, 350), (110, 470)], BROWN, 5, rng); crayon(d, [(400, 350), (400, 470)], BROWN, 5, rng)
    for i, (cx, lab) in enumerate(((150, "W"), (250, "R"), (350, "D"))):
        crayon(d, [(cx - 20, 250), (cx - 20, 320), (cx + 20, 320)], GREY, 4, rng)
        words(im, lab, 196, GREY, rng, 36) if False else None
        f = ImageFont.truetype(FONT, 34) if FONT else ImageFont.load_default()
        d.text((cx - 10, 206), lab, font=f, fill=GREY + (230,))
        crayon(d, [(cx - 22, 204), (cx + 24, 246)], RED, 4, rng); crayon(d, [(cx + 22, 204), (cx - 24, 246)], RED, 4, rng)
    woman(d, 60, 470, 150, rng)
    friend(d, 462, 470, 330, rng)
    words(im, "SUPPER FOR 2", 520, RED, rng, 42)


def d4(im, d, rng):          # he makes room in me
    crayon(d, [(20, 540), (490, 544)], BROWN, 5, rng)
    friend(d, 256, 540, 430, rng)
    # her outline drawn round him, stretched to his height
    crayon(d, [(256 + 46 * math.cos(a / 8 * math.pi), 96 + 46 * math.sin(a / 8 * math.pi)) for a in range(17)], BLUE, 4, rng)
    crayon(d, [(256, 142), (150, 440), (362, 440), (256, 142)], BLUE, 4, rng)
    crayon(d, [(220, 440), (216, 540)], BLUE, 4, rng); crayon(d, [(292, 440), (296, 540)], BLUE, 4, rng)
    for k in range(9):
        crayon(d, [(214 + k * 10, 62), (196 + k * 13, 190)], YELLOW, 2, rng, 2)
    words(im, "HE MAKES\nROOM IN ME", 556, BLACK, rng, 34)


def d5(im, d, rng):          # he never leaves
    crayon(d, [(150, 560), (150, 120), (370, 120), (370, 560)], BROWN, 6, rng)
    d.ellipse((338, 330, 352, 344), fill=YELLOW + (255,))
    friend(d, 262, 556, 430, rng)
    woman(d, 70, 560, 120, rng)
    words(im, "HE NEVER LEVES", 40, RED, rng, 40)


def d6(im, d, rng):          # i see every room now
    crayon(d, [(60, 560), (60, 220), (452, 220), (452, 560), (60, 560)], BROWN, 5, rng)
    crayon(d, [(40, 220), (256, 90), (472, 220)], RED, 5, rng)
    crayon(d, [(256, 220), (256, 560)], BROWN, 4, rng); crayon(d, [(60, 390), (452, 390)], BROWN, 4, rng)
    for (ex, ey) in ((150, 300), (350, 300), (150, 470), (350, 470), (256, 160)):
        d.ellipse((ex - 30, ey - 20, ex + 30, ey + 20), fill=(10, 10, 10, 255))
        d.ellipse((ex - 9, ey - 9, ex + 9, ey + 9), outline=(226, 214, 180, 255), width=3)
    words(im, "I SEE EVRY\nROOM NOW", 572, BLACK, rng, 30)


for n, fn in enumerate((d1, d2, d3, d4, d5, d6), 1):
    sheet(n, fn)
print("drawings: 6 ->", OUT)
