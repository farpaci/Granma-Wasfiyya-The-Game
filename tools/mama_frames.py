import cv2, numpy as np, glob, os
from scipy import ndimage
from PIL import Image

TARGET_H = 640
TARGET_TORSO = 300          # px: torso width after normalisation
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
os.chdir(os.path.join(ROOT, 'work'))  # shots/ (s0-5.png in, base/cut out) lives here
OUT = os.path.join(ROOT, 'assets')

def load(i):
    return cv2.imread(f'shots/cut{i}.png', cv2.IMREAD_UNCHANGED)   # BGRA

def decontaminate(bgra):
    a = bgra[..., 3]
    solid = ndimage.binary_erosion(a > 200, iterations=2)
    idx = ndimage.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    rgb = bgra[..., :3][idx[0], idx[1]]
    out = bgra.copy()
    edge = ~solid & (a > 0)
    out[..., :3][edge] = rgb[edge]
    return out

def torso_width(bgra):
    a = bgra[..., 3] > 128
    ys = np.where(a.any(axis=1))[0]; h = ys.max() - ys.min()
    best = 0
    for r in range(ys.min() + int(h * .26), ys.min() + int(h * .52)):
        xs = np.where(a[r])[0]
        if len(xs): best = max(best, xs.max() - xs.min())
    return best

def pivot_x(bgra):
    a = bgra[..., 3] > 128
    ys = np.where(a.any(axis=1))[0]; h = ys.max() - ys.min()
    xs = []
    for r in range(ys.min() + int(h * .30), ys.min() + int(h * .50)):
        x = np.where(a[r])[0]
        if len(x): xs.append((x.min() + x.max()) / 2)
    return float(np.mean(xs))

frames = {}
for i in range(6):
    b = decontaminate(load(i))
    ys = np.where((b[..., 3] > 10).any(axis=1))[0]
    s_w = TARGET_TORSO / torso_width(b)
    s_h = TARGET_H / (ys.max() - ys.min() + 1)
    s = (s_h ** 0.75) * (s_w ** 0.25)
    b = cv2.resize(b, None, fx=s, fy=s, interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)
    frames[i] = b
    print(i, b.shape[:2], 'scale %.2f' % s)

def mirrored(b):
    return b[:, ::-1].copy()

# 8-frame cycle: left-trailing half, then right-trailing half (mirrored/real poses)
seq = [('f', 4), ('f', 3), ('f', 1), ('f', 2),
       ('m', 4), ('f', 5), ('f', 0), ('m', 2)]
imgs = []
for kind, i in seq:
    b = frames[i]
    imgs.append(mirrored(b) if kind == 'm' else b)

pivs = [pivot_x(b) for b in imgs]
left = max(pivs); right = max(b.shape[1] - p for b, p in zip(imgs, pivs))
W = int(np.ceil(left + right)) + 6
H = max(b.shape[0] for b in imgs) + 2
for f in glob.glob(f'{OUT}/mama*.png'): os.remove(f)
for n, (b, p) in enumerate(zip(imgs, pivs), 1):
    canvas = np.zeros((H, W, 4), np.uint8)
    # align lowest visible pixel to canvas bottom
    a = b[..., 3] > 10
    bottom = np.where(a.any(axis=1))[0].max()
    ox = int(round(left - p + 3)); oy = H - 1 - bottom
    h, w = b.shape[:2]
    y0 = max(0, oy); y1 = min(H, oy + h); sy = y0 - oy
    canvas[y0:y1, ox:ox + w] = b[sy:sy + (y1 - y0)]
    Image.fromarray(canvas[..., [2, 1, 0, 3]]).save(f'{OUT}/mama{n}.png', optimize=True)
print('canvas', W, 'x', H, '| frames:', len(imgs))

# preview strip on checker-free magenta
strip = Image.new('RGB', (W * len(imgs) // 2 + 20, H // 2 + 20), (190, 0, 190))
for n in range(1, len(imgs) + 1):
    im = Image.open(f'{OUT}/mama{n}.png'); im = im.resize((W // 2, H // 2), Image.LANCZOS)
    strip.paste(im, (10 + (n - 1) * (W // 2) // 2 * 1 if False else 10 + (n - 1) * (W // 2), 10), im)
strip.save('shots/strip.png')
