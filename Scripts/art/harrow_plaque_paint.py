"""Paint two versions of the same Harrow children's door plaque."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DEST = Path(__file__).resolve().parents[2] / "SourceArt/Props/HarrowFurniture"
SIZE = (1024, 384)
FONT = Path("C:/Windows/Fonts/Inkfree.ttf")


def cloud(rng, size):
    source = Image.fromarray(rng.integers(0, 255, size[::-1], dtype=np.uint8))
    return np.asarray(source.resize(SIZE, Image.Resampling.BICUBIC), dtype=float) / 255


def paint(name, seed):
    rng = np.random.default_rng(seed)
    width, height = SIZE
    x, y = np.meshgrid(np.arange(width), np.arange(height))
    ruth = name == "Ruth"
    field = cloud(rng, (24, 11))
    pores = rng.normal(0, 1, (height, width))
    grain = cloud(rng, (30, 165))
    rough = (field - .5) * 24 + (grain - .5) * 28 + pores * 3
    edge = np.minimum(np.minimum(x, width - 1 - x), np.minimum(y, height - 1 - y))
    base = np.array((108, 48, 48) if ruth else (47, 42, 37), dtype=float)
    colour = base + rough[..., None] + np.clip((edge - 14) / 70, 0, 1)[..., None] * 10
    # Thin, lopsided strips of older paint show through the corners and chamfer.
    worn = edge < (.05 + field ** 2) * (45 if ruth else 26)
    primer = np.array((65, 91, 85) if ruth else (107, 81, 57)) + rough[..., None]
    wood = np.array((129, 97, 62)) + rough[..., None] * 1.6
    colour[worn] = np.where((edge[worn] < 7)[..., None], wood[worn], primer[worn])
    colour = np.clip(colour, 0, 255).astype(np.uint8)
    image = Image.fromarray(colour)
    ink = "RUTH" if ruth else "DANNY"
    font = ImageFont.truetype(str(FONT), 177 if ruth else 163)
    mask = Image.new("L", SIZE)
    if ruth:
        ImageDraw.Draw(mask).text((width / 2, 194), ink, font=font, fill=255, stroke_width=1, anchor="mm")
    else:
        # Individual strokes and letter spacing give the scratched name its uneven baseline.
        for char, left, baseline, angle in zip(ink, (270, 389, 512, 640, 766), (208, 194, 204, 191, 210), (5, -3, 2, -4, 4)):
            tile = Image.new("L", (232, 250))
            ImageDraw.Draw(tile).text((116, 125), char, font=font, fill=255, stroke_width=2, anchor="mm")
            tile = tile.rotate(angle, Image.Resampling.BICUBIC)
            mask.paste(tile, (left - 116, baseline - 125), tile)
    draw = ImageDraw.Draw(image)
    for inset, tint in ((21, (157, 119, 78) if ruth else (24, 23, 23)), (29, (115, 83, 53) if ruth else (85, 66, 48))):
        draw.rounded_rectangle((inset, inset, width-inset-1, height-inset-1), 46, outline=tint, width=3)
    fleck = cloud(rng, (186, 85))
    alpha = np.asarray(mask, dtype=float) / 255
    alpha *= np.clip((fleck + .24) * 1.4, .34, 1)
    alpha[pores > 1.5] *= .46
    letter_ink = np.array((215, 173, 123) if ruth else (176, 140, 97))
    out = np.asarray(image) * (1 - alpha[..., None]) + (letter_ink + rough[..., None] * 1.7) * alpha[..., None]
    image = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    draw = ImageDraw.Draw(image)
    for _ in range(94):
        xx = int(rng.integers(22, width-22))
        yy = int(rng.choice([rng.integers(9, 81), rng.integers(height-81, height-9)]))
        length = int(rng.integers(2, 45))
        draw.line((xx, yy, xx + length, yy + int(rng.integers(-3, 4))),
                  fill=tuple(int(v) for v in (primer if ruth else wood)[yy, xx]), width=int(rng.integers(1, 3)))
    for cx in (86, width - 86):
        cy = height // 2
        draw.ellipse((cx-17, cy-17, cx+17, cy+17), fill=(46, 29, 22))
        draw.ellipse((cx-13, cy-13, cx+13, cy+13), fill=(105, 88, 65))
        draw.arc((cx-12, cy-12, cx+12, cy+12), 190, 285, fill=(148, 124, 87), width=2)
        draw.line((cx-8, cy+5, cx+8, cy-6), fill=(38, 31, 28), width=4)
    image.resize((1024, 512), Image.Resampling.LANCZOS).save(DEST / f"T_HarrowPlaque{name}.png")


if __name__ == "__main__":
    paint("Danny", 414)
    paint("Ruth", 519)
