"""Textures for the walls-and-floors mock-up (Cheyenne, 2026-11-22: "give me some before and after pics and I'll tell you to
keep or trash"): the kitchen in 1950s farmhouse paper and linoleum instead of the same peeling plaster and boards as
everywhere else.  Plain Python (PIL), seamless tiles at 1024:
  SourceArt/Mock/T_MockKitchenPaper_C/ORM/N.png   faded cream paper, pinstripes and a small half-drop sprig, yellowed,
                                                  water-stained and scuffed (repeat 64 cm)
  SourceArt/Mock/T_MockLinoleum_C/ORM/N.png       oxblood and cream checker linoleum, 30 cm squares, worn pale where
                                                  people walked, scuffed, dirt in the seams and a crack or two (repeat 60 cm)
python mock_surfaces.py"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "SourceArt", "Mock")
os.makedirs(OUT, exist_ok=True)
S = 1024
random.seed(1954)


def noise(scale, seed, octaves=4):
    """Seamless value noise in 0..255 (L), from small random tiles upscaled with wrap."""
    acc = Image.new("L", (S, S), 0)
    amp, tot = 1.0, 0.0
    rnd = random.Random(seed)
    for o in range(octaves):
        n = max(2, int(scale * (2 ** o)))
        small = Image.new("L", (n, n))
        small.putdata([rnd.randint(0, 255) for _ in range(n * n)])
        big = Image.new("L", (n * 3, n * 3))
        for i in range(3):
            for j in range(3):
                big.paste(small, (i * n, j * n))
        big = big.resize((S * 3, S * 3), Image.BICUBIC).crop((S, S, 2 * S, 2 * S))
        acc = Image.blend(acc, big, amp / (tot + amp)) if tot else big
        tot += amp
        amp *= 0.5
    return acc.convert("L")


def save(img, name):
    img.save(os.path.join(OUT, name + ".png"))


def orm(rough_l, ao_l=None):
    r = rough_l
    a = ao_l or Image.new("L", (S, S), 255)
    m = Image.new("L", (S, S), 0)
    return Image.merge("RGB", (a, r, m))


def normal_from(height_l, strength=2.0):
    h = height_l.convert("F")
    px = h.load()
    out = Image.new("RGB", (S, S))
    po = out.load()
    for y in range(S):
        for x in range(S):
            dx = (px[(x + 1) % S, y] - px[(x - 1) % S, y]) / 255.0 * strength
            dy = (px[x, (y + 1) % S] - px[x, (y - 1) % S]) / 255.0 * strength
            l = math.sqrt(dx * dx + dy * dy + 1.0)
            po[x, y] = (int((-dx / l * 0.5 + 0.5) * 255), int((dy / l * 0.5 + 0.5) * 255), int((1.0 / l * 0.5 + 0.5) * 255))
    return out


# ------------------------------------------------------------------------------------------------ the kitchen paper
def paper():
    base = Image.new("RGBA", (S, S), (214, 202, 168, 255))
    d = ImageDraw.Draw(base)
    # pinstripes: a pair of thin faded green lines every 128 px (8 cm)
    for x0 in range(0, S, 128):
        for off in (0, 7):
            d.line([(x0 + off, 0), (x0 + off, S)], fill=(128, 142, 104, 255), width=2)
    # a small sprig in a half-drop: three red-orange berries and two leaves, between the stripes
    sprig = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sprig)
    sd.line([(30, 52), (30, 26)], fill=(98, 112, 72, 255), width=2)
    sd.ellipse([14, 30, 30, 40], fill=(112, 130, 84, 255))
    sd.ellipse([30, 36, 46, 46], fill=(112, 130, 84, 255))
    for (cx, cy) in ((24, 18), (36, 16), (30, 26)):
        sd.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(176, 84, 52, 255))
        sd.ellipse([cx - 2, cy - 4, cx + 1, cy - 1], fill=(206, 132, 96, 255))
    big = Image.new("RGBA", (S * 3, S * 3), (0, 0, 0, 0))                  # stamped on a 3x3 canvas so it wraps
    for k, x in enumerate(range(64 - 30, S, 128)):
        for y in range(0, S, 160):
            yy = y + (80 if k % 2 else 0) - 30
            for dx in (0, S, 2 * S):
                for dy in (0, S, 2 * S):
                    big.alpha_composite(sprig, (x + dx, (yy % S) + dy))
    base.alpha_composite(big.crop((S, S, 2 * S, 2 * S)))
    img = base.convert("RGB")
    # age: yellowing mottle, water-stain tide marks running down, scuffs low down where chairs went
    mott = noise(3, 11).point(lambda v: int(v * 0.6))
    yel = Image.new("RGB", (S, S), (150, 120, 70))
    img = Image.composite(yel, img, mott.point(lambda v: int(max(0, v - 70) * 0.9)))
    stain = noise(2, 23, 5).point(lambda v: 255 if 150 < v < 158 else 0).filter(ImageFilter.GaussianBlur(2))
    img = Image.composite(Image.new("RGB", (S, S), (112, 82, 46)), img, stain.point(lambda v: int(v * 0.55)))
    fade = noise(5, 31).point(lambda v: int(max(0, v - 120) * 0.7))
    img = Image.composite(Image.new("RGB", (S, S), (190, 176, 140)), img, fade)
    save(img, "T_MockKitchenPaper_C")
    h = noise(40, 41, 3)
    save(orm(h.point(lambda v: int(190 + v * 0.2))), "T_MockKitchenPaper_ORM")
    save(normal_from(h.filter(ImageFilter.GaussianBlur(1)), 1.2), "T_MockKitchenPaper_N")


# ------------------------------------------------------------------------------------------------ the linoleum
def linoleum():
    img = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(img)
    q = S // 2                                                        # two squares a side: 30 cm each at a 60 cm repeat
    cols = [(196, 182, 150), (92, 34, 28)]
    for i in range(2):
        for j in range(2):
            c = cols[(i + j) % 2]
            d.rectangle([i * q, j * q, i * q + q - 1, j * q + q - 1], fill=c)
    # the marbled fleck linoleum has
    fl = noise(60, 51, 3).point(lambda v: 255 if v > 200 else 0).filter(ImageFilter.GaussianBlur(0.8))
    img = Image.composite(Image.new("RGB", (S, S), (150, 132, 108)), img, fl.point(lambda v: int(v * 0.35)))
    # worn pale and dull in broad patches, scuffs, dirt packed into the seams
    wear = noise(2, 61, 4).point(lambda v: int(max(0, v - 110) * 1.1))
    img = Image.composite(Image.new("RGB", (S, S), (150, 128, 100)), img, wear)
    sc = Image.new("L", (S, S), 0)
    sd = ImageDraw.Draw(sc)
    rnd = random.Random(71)
    for _ in range(260):
        x, y = rnd.randint(0, S), rnd.randint(0, S)
        a = rnd.uniform(0, math.pi)
        L = rnd.uniform(10, 70)
        sd.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=rnd.randint(60, 160), width=rnd.choice((1, 1, 2)))
    img = Image.composite(Image.new("RGB", (S, S), (40, 30, 22)), img, sc)
    seams = Image.new("L", (S, S), 0)
    sd = ImageDraw.Draw(seams)
    for k in (0, q):
        sd.line([(k, 0), (k, S)], fill=255, width=4)
        sd.line([(0, k), (S, k)], fill=255, width=4)
    seams = seams.filter(ImageFilter.GaussianBlur(2))
    img = Image.composite(Image.new("RGB", (S, S), (30, 22, 16)), img, seams.point(lambda v: int(v * 0.8)))
    crack = Image.new("L", (S, S), 0)
    cd = ImageDraw.Draw(crack)
    x, y = 140, 380
    for _ in range(40):
        nx_, ny_ = x + rnd.uniform(4, 14), y + rnd.uniform(-8, 8)
        cd.line([(x, y), (nx_, ny_)], fill=255, width=2)
        x, y = nx_, ny_
    img = Image.composite(Image.new("RGB", (S, S), (24, 18, 12)), img, crack)
    save(img, "T_MockLinoleum_C")
    rough = ImageChops.add(Image.new("L", (S, S), 120), wear.point(lambda v: int(v * 0.4)))
    rough = ImageChops.lighter(rough, seams.point(lambda v: int(v * 0.9)))
    save(orm(rough, ImageChops.invert(seams.point(lambda v: int(v * 0.5)))), "T_MockLinoleum_ORM")
    h = ImageChops.invert(ImageChops.lighter(seams, crack))
    save(normal_from(h.filter(ImageFilter.GaussianBlur(1.5)), 3.0), "T_MockLinoleum_N")


paper()
linoleum()
print("MOCK surfaces written to", os.path.abspath(OUT))
