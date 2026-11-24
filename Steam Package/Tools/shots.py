# Steam screenshots: chosen gameplay frames (no HUD), at 1920x1080. Smaller takes are upscaled with Lanczos and a light sharpen.
import os, sys, glob
from PIL import Image, ImageFilter
R = r'C:\GameDev\Unreal\WellnessCheck\Saved'
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
PICKS = [l.split('|') for l in sys.argv[2:]]   # name|folder|frame index
for name, folder, idx in PICKS:
    fs = sorted(glob.glob(os.path.join(R, folder, '**', 'f_*.*'), recursive=True))
    src = fs[int(idx)] if not os.path.isfile(folder) else folder
    im = Image.open(src).convert('RGB')
    if im.size != (1920, 1080):
        im = im.resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 60, 2))
    im.save(os.path.join(OUT, name + '.jpg'), quality=94)
    print(name, os.path.relpath(src, R), Image.open(src).size)
