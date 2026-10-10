import cv2, numpy as np, json, os
from scipy import ndimage
from PIL import Image
START, N = 27, 24
os.makedirs('walk_png', exist_ok=True); os.makedirs('/home/claude/game/assets_video', exist_ok=True)
frames = [cv2.imread(f'keyed/k_{i:03d}.png', cv2.IMREAD_UNCHANGED) for i in range(START, START+N)]
H, W = frames[0].shape[:2]
boxes = []
for f in frames:
    ys, xs = np.where(f[...,3] > 20); boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
x0 = max(0, min(b[0] for b in boxes) - 6); x1 = min(W, max(b[2] for b in boxes) + 7)
y0 = max(0, min(b[1] for b in boxes) - 6); y1 = H
cx = float(np.mean([ (f[...,3]>128).any(axis=0).nonzero()[0].mean() for f in frames ]))
# body centre = mean x of mask over the torso band (steadier than arms/legs)
cxs = []
for f in frames:
    a = f[...,3] > 128; ys = np.where(a.any(axis=1))[0]; h = ys.max()-ys.min()
    xs = [np.where(a[r])[0].mean() for r in range(ys.min()+int(.1*h), ys.min()+int(.45*h)) if a[r].any()]
    cxs.append(np.mean(xs))
pivot = (float(np.mean(cxs)) - x0) / (x1 - x0)

def defringe(bgra):
    a = bgra[...,3]
    solid = ndimage.binary_erosion(a > 215, iterations=2)
    idx = ndimage.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    out = bgra.copy(); edge = ~solid & (a > 0)
    out[...,:3][edge] = bgra[...,:3][idx[0], idx[1]][edge]
    out[...,3] = np.where(a < 40, 0, a)
    return out

gap = []
for n, f in enumerate(frames):
    f = defringe(f)[y0:y1, x0:x1]
    img = Image.fromarray(f[..., [2,1,0,3]])
    img.save(f'walk_png/walk_{n:02d}.png', optimize=True)
    img.save(f'/home/claude/game/assets_video/walk_{n:02d}.webp', quality=90, method=6)
    a = f[...,3] > 128; ys = np.where(a.any(axis=1))[0]; h = ys.max()-ys.min()
    lo = a[ys.max()-int(.14*h):ys.max()+1]            # feet band
    cols = np.where(lo.any(axis=0))[0]
    gap.append(cols.max()-cols.min())
idle = int(np.argmin(gap))
meta = dict(n=N, w=int(x1-x0), h=int(y1-y0), pivot=pivot, idle=idle, src=f'frames {START}-{START+N-1} @24fps')
json.dump(meta, open('/home/claude/game/assets_video/meta.json','w')); print(meta)
sz = sum(os.path.getsize(f'/home/claude/game/assets_video/walk_{n:02d}.webp') for n in range(N)); print('webp total KB', sz//1024)
# contact strip
strip = Image.new('RGB', ((x1-x0)//3*8+10, (y1-y0)//3*3+10), (190,0,190))
for n in range(N):
    im = Image.open(f'walk_png/walk_{n:02d}.png'); im = im.resize((im.width//3, im.height//3), Image.LANCZOS)
    strip.paste(im, (5+(n%8)*(im.width), 5+(n//8)*(im.height)), im)
strip.save('walk_strip.png')
