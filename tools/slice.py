import os, sys
import numpy as np
from PIL import Image
try:
    from scipy import ndimage
except Exception:
    ndimage = None

SRC = '/home/claude/game/work/sheet.png'
OUT = '/home/claude/game/assets'
os.makedirs(OUT, exist_ok=True)
sheet = Image.open(SRC).convert('RGB')
A = np.asarray(sheet).astype(np.float32)

KEY = np.array([20, 240, 20], dtype=np.float32)


def key_region(box, inset=4, side=True):
    x0, y0, x1, y1 = box
    reg = A[y0:y1, x0:x1].copy()
    d = np.sqrt(((reg - KEY) ** 2).sum(axis=2))
    alpha = np.clip((d - 70) / 80.0, 0, 1)
    # despill: where partially transparent, pull green down toward the other channels
    rb = np.maximum(reg[..., 0], reg[..., 2])
    spill = np.clip(reg[..., 1] - rb, 0, None)
    edge = (alpha < 1.0) & (alpha > 0)
    reg[..., 1] = np.where(edge, reg[..., 1] - spill * 0.9, reg[..., 1])
    # mild despill on all pixels for bright green halos
    reg[..., 1] = np.minimum(reg[..., 1], rb + 90 + (1 - alpha) * 0)
    alpha[:inset, :] = 0
    alpha[-inset:, :] = 0
    if side:
        alpha[:, :inset] = 0
        alpha[:, -inset:] = 0
    rgba = np.dstack([reg, alpha * 255]).clip(0, 255).astype(np.uint8)
    return rgba


def edge_despill(rgba, hard=False):
    rgba = rgba.copy()
    a = rgba[..., 3]
    opaque = a > 200
    if ndimage is not None:
        near_edge = ndimage.binary_dilation(~opaque, iterations=3) & (a > 0)
    else:
        near_edge = a < 255
    r = rgba[..., 0].astype(np.int32); g = rgba[..., 1].astype(np.int32); b = rgba[..., 2].astype(np.int32)
    cap = np.maximum(r, b) + (6 if hard else 20)
    sel = np.ones_like(near_edge) if hard else near_edge
    rgba[..., 1] = np.where(sel, np.minimum(g, cap), g).astype(np.uint8)
    return rgba


def clean_and_trim(rgba, min_area=40, keep_largest_only=False, hard=False):
    rgba = edge_despill(rgba, hard)
    a = rgba[..., 3]
    mask = a > 24
    if ndimage is not None:
        lab, n = ndimage.label(mask)
        if n > 0:
            sizes = ndimage.sum(mask, lab, range(1, n + 1))
            keep = np.zeros(n + 1, bool)
            objs = ndimage.find_objects(lab)
            # drop thin border lines left over from the sheet's panel frames
            for i, sl in enumerate(objs):
                h = sl[0].stop - sl[0].start
                w = sl[1].stop - sl[1].start
                if h < 7 or w < 7:
                    sizes[i] = 0
            if keep_largest_only:
                keep[1 + int(np.argmax(sizes))] = True
            else:
                for i, s in enumerate(sizes):
                    if s >= min_area:
                        keep[i + 1] = True
            m = keep[lab]
            rgba = rgba.copy()
            rgba[..., 3] = np.where(m, rgba[..., 3], 0)
            mask = m
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return Image.fromarray(rgba)
    return Image.fromarray(rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1])


def save_sprite(name, box, side=True, **kw):
    img = clean_and_trim(key_region(box, side=side), **kw)
    img.save(f'{OUT}/{name}.png')
    print(name, img.size)
    return img


# 1. ground
sheet.crop((16, 41, 172, 204)).save(f'{OUT}/paving.png')
# shadow overlay: black with alpha from how dark the green is
reg = A[212:302, 22:286]
alpha = np.clip((225 - reg[..., 1]) / 130.0, 0, 1) ** 0.9
alpha = np.clip((alpha - 0.16) / 0.84, 0, 1)
# fade the edges so no frame lines or noise survive
fy = np.minimum(np.arange(reg.shape[0]), np.arange(reg.shape[0])[::-1])
fx = np.minimum(np.arange(reg.shape[1]), np.arange(reg.shape[1])[::-1])
alpha *= np.clip(np.minimum.outer(fy, fx) / 10.0, 0, 1)
sh = np.zeros(reg.shape[:2] + (4,), np.uint8)
sh[..., 3] = (alpha * 255).astype(np.uint8)
Image.fromarray(sh).save(f'{OUT}/shadow.png')

# 2. palms
palm_boxes = [(298, 40, 472, 341), (470, 40, 575, 341), (570, 38, 728, 341), (718, 40, 836, 341)]
for i, b in enumerate(palm_boxes, 1):
    save_sprite(f'palm{i}', b, keep_largest_only=True)

# 3. arches
arch_boxes = [(842, 40, 1098, 342), (1098, 40, 1330, 342), (1328, 40, 1530, 342)]
for i, b in enumerate(arch_boxes, 1):
    save_sprite(f'arch{i}', b, side=(i in (1,)) and False)

# 4. cafe sets
for i, b in enumerate([(8, 380, 272, 592), (272, 380, 498, 592), (498, 380, 712, 592)], 1):
    save_sprite(f'cafe{i}', b)

# 5. chalkboards
for i, b in enumerate([(728, 395, 868, 592), (866, 405, 986, 592), (986, 420, 1112, 592)], 1):
    save_sprite(f'board{i}', b)

# 6. rug stall
save_sprite('stall', (1124, 388, 1526, 592))

# 7. planters
for i, b in enumerate([(14, 625, 170, 760), (166, 625, 286, 760), (287, 625, 438, 760), (439, 625, 538, 760)], 1):
    save_sprite(f'planter{i}', b)

# 8. benches
for i, b in enumerate([(558, 634, 776, 764), (778, 634, 1012, 764)], 1):
    save_sprite(f'bench{i}', b)

# 9. lamps
for i, b in enumerate([(1046, 622, 1104, 764), (1130, 622, 1224, 764), (1236, 622, 1296, 764)], 1):
    save_sprite(f'lamp{i}', b)

# 10. bins
for i, b in enumerate([(1336, 640, 1418, 764), (1436, 640, 1514, 764)], 1):
    save_sprite(f'bin{i}', b)

# 11. backdrop
sheet.crop((6, 799, 797, 1019)).save(f'{OUT}/backdrop.jpg', quality=92)

# 12. mama frames: bottom-aligned, same canvas
centers = [855, 930, 1005, 1080, 1155, 1230]
lean = [1395, 1482]
frames = []
for c in centers + lean:
    box = (c - 42, 808, c + 42, 982)
    img = clean_and_trim(key_region(box), keep_largest_only=True, hard=True)
    frames.append(img)
W = max(f.width for f in frames) + 4
H = max(f.height for f in frames)
for i, f in enumerate(frames):
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.paste(f, ((W - f.width) // 2, H - f.height), f)
    name = f'mama{i + 1}' if i < 6 else ('mama_left' if i == 6 else 'mama_right')
    canvas.save(f'{OUT}/{name}.png')
    print(name, f.size, '->', canvas.size)
