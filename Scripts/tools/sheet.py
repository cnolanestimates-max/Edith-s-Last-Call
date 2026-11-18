"""contact sheet: python sheet.py <dir> <out.jpg> [cols] [tile_w] [start] [count]"""
import sys, glob, os
from PIL import Image, ImageDraw
d, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
tw = int(sys.argv[4]) if len(sys.argv) > 4 else 480
start = int(sys.argv[5]) if len(sys.argv) > 5 else 0
count = int(sys.argv[6]) if len(sys.argv) > 6 else 999
fs = sorted(glob.glob(os.path.join(d, "*.png")))[start:start + count]
ims = []
for f in fs:
    im = Image.open(f).convert("RGB")
    th = int(tw * im.height / im.width)
    im = im.resize((tw, th))
    ImageDraw.Draw(im).text((6, 4), os.path.basename(f)[:-4], fill=(255, 255, 0))
    ims.append(im)
if not ims: sys.exit("no images")
th = ims[0].height
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * th))
for i, im in enumerate(ims):
    sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
sheet.save(out, quality=88)
print(len(ims), sheet.size)
