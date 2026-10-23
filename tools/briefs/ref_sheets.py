import json, os, sys
from PIL import Image
R = sys.argv[1]; OUT = os.path.join(R, 'art', 'briefs', 'refs'); os.makedirs(OUT, exist_ok=True)
GREEN = (0, 177, 64)
def sheet(imgs, name, H=900, pad=40):
    ims = [im.convert('RGBA') for im in imgs]
    ims = [im.resize((round(im.width * H / im.height), H), Image.LANCZOS) for im in ims]
    W = sum(i.width for i in ims) + pad * (len(ims) + 1)
    c = Image.new('RGB', (W, H + 2 * pad), GREEN); x = pad
    for im in ims: c.paste(im, (x, pad), im); x += im.width + pad
    c.save(os.path.join(OUT, name), optimize=True); print(name, c.size)
A = lambda p: Image.open(os.path.join(R, p))
ms = json.load(open(os.path.join(R, 'assets_slap', 'meta_slap.json')))
sheet([A('assets_video/walk_00.webp'), A('assets_video/walk_12.webp'),
       A(f"assets_slap/slapA_{ms['A']['hit']:02d}.webp"), A(f"assets_slap/slapB_{ms['B']['hit']:02d}.webp")], 'granma_back_view.png')
for i in ['thobe', 'tank', 'tee', 'hoodie', 'shirt', 'shemagh']:
    sheet([A(f'assets_enemy/walk_{i}_00.webp'), A(f'assets_enemy/walk_{i}_08.webp'), A(f'assets_enemy/frozen_{i}.webp')], f'man_{i}.png')
