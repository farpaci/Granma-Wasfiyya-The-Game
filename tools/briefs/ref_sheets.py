"""Reference sheets for the art brief: native-resolution frames only (no upscaling), on chroma green.
Men: hands-up photo cropped from the original 2000 px stills + one in-game walk frame at native size.
Granma: walk and slap frames at native size. Usage: python3 tools/briefs/ref_sheets.py <repo root>"""
import json, os, sys
import numpy as np
from PIL import Image
R = sys.argv[1]; OUT = os.path.join(R, 'art', 'briefs', 'refs'); os.makedirs(OUT, exist_ok=True)
GREEN = (0, 177, 64)
A = lambda p: Image.open(os.path.join(R, p))

def sheet(ims, name, pad=40):
    ims = [im.convert('RGBA') for im in ims]
    H = max(i.height for i in ims)
    c = Image.new('RGB', (sum(i.width for i in ims) + pad * (len(ims) + 1), H + 2 * pad), GREEN); x = pad
    for im in ims:
        c.paste(im, (x, pad + H - im.height), im); x += im.width + pad   # bottom-aligned, native size
    c.save(os.path.join(OUT, name), optimize=True); print(name, c.size, [i.size for i in ims])

def figures(path, n=3, pad=30):
    im = Image.open(os.path.join(R, path)).convert('RGB'); a = np.asarray(im).astype(int)
    fg = ~((a[..., 1] > a[..., 0] + 40) & (a[..., 1] > a[..., 2] + 40))      # not green
    W = im.width; out = []
    for k in range(n):
        x0, x1 = k * W // n, (k + 1) * W // n
        ys, xs = np.where(fg[:, x0:x1])
        out.append(im.crop((max(0, x0 + xs.min() - pad), max(0, ys.min() - pad), min(W, x0 + xs.max() + pad), min(im.height, ys.max() + pad))))
    return out

ms = json.load(open(os.path.join(R, 'assets_slap', 'meta_slap.json')))
sheet([A('assets_video/walk_00.webp'), A('assets_video/walk_12.webp'),
       A(f"assets_slap/slapA_{ms['A']['hit']:02d}.webp"), A(f"assets_slap/slapB_{ms['B']['hit']:02d}.webp")], 'granma_back_view.png')
photos = dict(zip(['hoodie', 'shirt', 'shemagh'], figures('art/source/enemies_frozen_1.jpg')))
photos.update(zip(['thobe', 'tank', 'tee'], figures('art/source/enemies_frozen_2.jpg')))
for i, ph in photos.items():
    sheet([A(f'assets_enemy/walk_{i}_00.webp'), ph], f'man_{i}.png')
