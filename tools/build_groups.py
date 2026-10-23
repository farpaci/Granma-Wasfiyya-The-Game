# Builds assets_group/ (tea-table group sprites + meta_group.json) from art/source/combo/group_adana_*_sheet.webp.
# Usage: python3 tools/build_groups.py   (needs opencv-python-headless, scipy, numpy, pillow)
# Every panel is keyed (soft alpha + despill for green sheets), cut by a hand-set panel box (a panel may hold
# several blobs: runners, glasses, debris), and registered on the TABLE anchor (bottom-centre of table/stools).
# Canonical orientation: Granma kicks from the LEFT, group on her right (screen-right); the game mirrors it.
import cv2, numpy as np, os, json
from scipy import ndimage
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'art', 'source', 'combo'); OUT = os.path.join(ROOT, 'assets_group'); W = os.path.join(ROOT, 'work', 'groups')
os.makedirs(OUT, exist_ok=True); os.makedirs(W, exist_ok=True)
SC = 0.65; Q = 80
# per variant: sheet, kind, src px per metre (seated head ~1.25 m above ground), panels [key, box(x0,y0,x1,y1), anchor(x,y) or None (runners)]
V = {
 'a_run':  dict(file='group_adana_a_run_sheet.webp', kind='run', ppm=264, panels=[
    ('calm', (0, 100, 520, 500), (255, 462)), ('impact', (520, 60, 1042, 540), (800, 455)), ('jump', (1042, 60, 1536, 580), (1275, 445)),
    ('runners', (60, 520, 780, 960), None), ('after', (800, 680, 1536, 990), (1195, 885))]),
 'a_stay': dict(file='group_adana_a_stay_sheet.webp', kind='stay', ppm=300, panels=[
    ('calm', (0, 140, 660, 600), (335, 568)), ('impact', (660, 90, 1300, 640), (1030, 525)), ('after', (1300, 60, 2000, 690), (1650, 595))]),
 'b_run':  dict(file='group_adana_b_run_sheet.webp', kind='run', ppm=240, panels=[
    ('calm', (0, 100, 500, 460), (250, 440)), ('impact', (520, 80, 1020, 470), (750, 435)), ('jump', (1020, 50, 1536, 470), (1250, 430)),
    ('runners', (60, 500, 740, 950), None), ('after', (830, 670, 1536, 980), (1180, 890))]),
}

def key_green(im):
    f = im.astype(np.float32); r, g, b = f[..., 0], f[..., 1], f[..., 2]
    spill = g - np.maximum(r, b); bg = np.median(spill[spill > 60])
    a = np.clip((bg * .78 - spill) / (bg * .78 - bg * .38), 0, 1)
    ratio = spill / (g + 1); rb = np.median(ratio[spill > 60])
    a = np.minimum(a, np.where(g > 40, np.clip((.85 * rb - ratio) / (.30 * rb), 0, 1), 1))
    a = cv2.GaussianBlur(a, (0, 0), 0.7)
    m = a > .5; lab, n = ndimage.label(ndimage.binary_dilation(m, iterations=3))   # drop pure noise specks (dilate-then-label)
    if n:
        sz = ndimage.sum(m, lab, range(1, n + 1)); ok = np.zeros(n + 1, bool); ok[1:] = sz > 25; a = a * ok[lab]
    a = np.where(a < .06, 0, a)
    # despill: green may not exceed the other channels; edge pixels that read olive are repainted from the interior
    clean = (a > .9) & (spill < .12 * bg); clean = ndimage.binary_erosion(clean) | (clean & (spill < 0))
    idx = ndimage.distance_transform_edt(~clean, return_distances=False, return_indices=True)
    bad = (spill >= .12 * bg) & (a > 0)
    for ch in (r, g, b): ch[bad] = ch[idx[0], idx[1]][bad]
    d = ndimage.distance_transform_edt(a > .5); band = (a > 0) & (d <= 3)
    olive = band & (g - r > -30) & (g - b > 15); good = (a > .9) & (d > 4) & ~((g - r > -30) & (g - b > 15))
    idx = ndimage.distance_transform_edt(~good, return_distances=False, return_indices=True)
    for ch in (r, g, b): ch[olive] = ch[idx[0], idx[1]][olive]
    g = np.minimum(g, np.maximum(r, b) + 2)
    return np.dstack([r, g, b, a * 255]).clip(0, 255).astype(np.uint8)

meta = {}; sheets = []
for name, v in V.items():
    im = Image.open(os.path.join(SRC, v['file'])); rgba = np.array(im.convert('RGBA'))
    full = key_green(rgba[..., :3]) if v['kind'] == 'run' else rgba
    after = next(p for p in v['panels'] if p[0] == 'after'); axA, ayA = after[2] if after[2] else (0, 0)
    frames = []; runners = None; crops = []
    for k, (key, (x0, y0, x1, y1), anc) in enumerate(v['panels']):
        c = full[y0:y1, x0:x1].copy(); ys, xs = np.nonzero(c[..., 3] > 8)
        bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        c = c[by0:by1, bx0:bx1]
        if anc is None:       # runners: keep their offset to the panel's own bbox, start around the table (after-panel anchor)
            runners = k; ax, ay = (c.shape[1] / 2, c.shape[0] - 55)
        else: ax, ay = anc[0] - x0 - bx0, anc[1] - y0 - by0
        ci = Image.fromarray(c, 'RGBA'); w, h = max(1, round(ci.width * SC)), max(1, round(ci.height * SC))
        ci = ci.resize((w, h), Image.LANCZOS)
        ci.save(os.path.join(OUT, f'{name}_{k}.webp'), quality=Q, method=6)
        frames.append(dict(key=f'{name}_{k}', w=w, h=h, ax=round(ax * SC, 1), ay=round(ay * SC, 1))); crops.append(ci)
    meta[name] = dict(frames=frames, mpp=round(v['ppm'] * SC, 2), kind=v['kind'], runners=runners)
    sheets.append((name, crops, frames, v['ppm'] * SC))
json.dump(meta, open(os.path.join(OUT, 'meta_group.json'), 'w'))
# contact sheet: all frames of a variant at the same scale (px/m = 150), anchors aligned on a row, magenta background
for name, crops, frames, mpp in sheets:
    s = 150 / mpp; ims = [c.resize((max(1, round(c.width * s)), max(1, round(c.height * s)))) for c in crops]
    L = max(f['ax'] * s for f in frames) + 10; R = max(f['w'] * s - f['ax'] * s for f in frames) + 10
    U = max(f['ay'] * s for f in frames) + 10; D = max(f['h'] * s - f['ay'] * s for f in frames) + 10
    cw, ch = int(L + R), int(U + D); sheet = Image.new('RGBA', (cw * len(ims), ch), (255, 0, 255, 255))
    for i, (c, f) in enumerate(zip(ims, frames)):
        sheet.alpha_composite(c, (int(i * cw + L - f['ax'] * s), int(U - f['ay'] * s)))
        for dx in range(-3, 4): sheet.putpixel((int(i * cw + L) + dx, int(U)), (0, 255, 255, 255))
    # 1 m grid marks at the left edge + a 1.75 m bar
    for m in range(0, 3): sheet.paste((255, 255, 255, 255), (0, int(U - m * 150), 12, int(U - m * 150) + 2))
    sheet.convert('RGB').save(os.path.join(W, f'contact_{name}.jpg'), quality=88)
print({n: [f['key'] for f in m['frames']] for n, m in meta.items()}); print('total bytes', sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)))
