# Steam capsules from the two key art images and the title lettering.
import sys, os
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from logo import make_logo

S = os.path.dirname(__file__)
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
wide = Image.open(os.path.join(S, 'ka', 'keyart_wide_1.png')).convert('RGB')    # 5504x3072
vert = Image.open(os.path.join(S, 'ka', 'keyart_vert_1.png')).convert('RGB')    # 3712x4608
LOGO = make_logo(3000)

def cover(img, w, h, cx=0.5, cy=0.5, zoom=1.0):
    """Crop img to aspect w:h around (cx, cy) (fractions), zoom >1 crops tighter, then resize."""
    iw, ih = img.size
    a = w / h
    cw, ch = (iw, iw / a) if iw / ih < a else (ih * a, ih)
    cw, ch = cw / zoom, ch / zoom
    x0 = min(max(cx * iw - cw / 2, 0), iw - cw)
    y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    return img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((w, h), Image.LANCZOS)

def shade(img, side='left', amount=0.55, reach=0.6):
    """Darken one side (or top) with a smooth gradient so the title reads."""
    w, h = img.size
    g = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(g)
    n = int((w if side == 'left' else h) * reach)
    for i in range(n):
        v = int(255 * amount * (1 - i / n) ** 1.6)
        if side == 'left': d.line([(i, 0), (i, h)], fill=v)
        else: d.line([(0, i), (w, i)], fill=v)
    black = Image.new('RGB', (w, h), (4, 5, 8))
    return Image.composite(black, img, g)

def put_logo(img, width_frac, cx_frac, cy_frac):
    img = img.convert('RGBA')
    w = int(img.width * width_frac)
    lg = LOGO.resize((w, int(w * LOGO.height / LOGO.width)), Image.LANCZOS)
    img.alpha_composite(lg, (int(img.width * cx_frac - lg.width / 2), int(img.height * cy_frac - lg.height / 2)))
    return img.convert('RGB')

def save(img, name):
    p = os.path.join(OUT, name)
    if name.endswith('.jpg'): img.save(p, quality=93)
    else: img.save(p)
    print(name, img.size)

# Store capsules (wide art; she and the deputy on the right, title in the sky on the left)
save(put_logo(shade(cover(wide, 920, 430, 0.5, 0.42), 'left', 0.55, 0.55), 0.42, 0.24, 0.30), 'header_capsule_920x430.jpg')
save(put_logo(shade(cover(wide, 1232, 706, 0.5, 0.5), 'left', 0.45, 0.55), 0.44, 0.255, 0.22), 'main_capsule_1232x706.jpg')
save(put_logo(shade(cover(wide, 462, 174, 0.62, 0.62, 1.55), 'left', 0.8, 0.8), 0.64, 0.35, 0.5), 'small_capsule_462x174.jpg')
# Vertical: the hall image, title in the dark ceiling at the top
save(put_logo(shade(cover(vert, 748, 896, 0.5, 0.5), 'top', 0.55, 0.35), 0.84, 0.5, 0.13), 'vertical_capsule_748x896.jpg')
save(put_logo(shade(cover(vert, 600, 900, 0.5, 0.5), 'top', 0.55, 0.32), 0.86, 0.5, 0.115), 'library_capsule_600x900.jpg')
# Library hero: art only, no text (Steam lays the logo over it)
save(cover(wide, 3840, 1240, 0.5, 0.45), 'library_hero_3840x1240.jpg')
# Library logo: transparent PNG, at most 1280 wide or 720 tall
lg = LOGO.copy(); lg.thumbnail((1280, 720), Image.LANCZOS); save(lg, 'library_logo_1280.png')
# Page background: dark, low contrast, so the store text stays readable
bg = cover(wide, 1438, 810, 0.5, 0.5)
bg = ImageEnhance.Brightness(ImageEnhance.Color(bg).enhance(0.35)).enhance(0.45).filter(ImageFilter.GaussianBlur(1.2))
save(bg, 'page_background_1438x810.jpg')
# Events and announcements
save(put_logo(shade(cover(wide, 800, 450, 0.5, 0.5), 'left', 0.45, 0.55), 0.44, 0.255, 0.22), 'event_cover_800x450.jpg')
save(put_logo(shade(cover(wide, 1920, 622, 0.5, 0.4), 'left', 0.5, 0.55), 0.38, 0.22, 0.32), 'event_header_1920x622.jpg')
# Full-size key art, clean and titled
save(cover(wide, 3840, 2160), 'key_art_wide_clean_3840x2160.jpg')
save(put_logo(shade(cover(wide, 3840, 2160), 'left', 0.45, 0.55), 0.44, 0.255, 0.2), 'key_art_wide_titled_3840x2160.jpg')
save(vert, 'key_art_vertical_clean_3712x4608.jpg')

