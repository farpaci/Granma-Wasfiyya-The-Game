import cv2, numpy as np, json, os
from PIL import Image
OUT = '/home/claude/game/assets_slap'; os.makedirs(OUT, exist_ok=True); os.makedirs('slap_png', exist_ok=True)
Y_TOP, Y_BOT, Y_CROP_BOT = 38.0, 702.0, 704
SCALE = 0.935                         # match px-per-metre of the walk-cycle sprites
STRENGTH = 1.0                        # proportion reshaping strength (1 = match original Mama)
CLIPS = {
 'A': dict(frames=list(range(43,100,6)) + list(range(100,112,3)) + list(range(112,126)) + list(range(126,134,2)), hit_src=118),
 'B': dict(frames=list(range(128,140,2)) + list(range(140,156)) + list(range(156,181,4)) + list(range(182,193,2)), hit_src=150),
}
# ---- width-ratio profile: original Mama / new Mama (measured in the same standing pose) ----
po, pn = np.load('prof_orig.npy'), np.load('prof_new.npy')
ratio = np.clip(po/np.maximum(pn,1e-3), 0.9, 1.3)
ratio = np.convolve(np.pad(ratio,(2,2),mode='edge'), np.ones(5)/5, mode='valid')
fs = (np.arange(len(ratio))+0.5)/len(ratio)
def sx(f): return 1 + (np.interp(f, fs, ratio) - 1)*STRENGTH

def load(i): return cv2.imread(f'keyed/k_{i:03d}.png', cv2.IMREAD_UNCHANGED)
def body_center(rgba):
    a = rgba[...,3] > 128; rows = range(int(Y_TOP + .25*(Y_BOT-Y_TOP)), int(Y_TOP + .55*(Y_BOT-Y_TOP)))
    return float(np.mean([np.where(a[r])[0].mean() for r in rows if a[r].any()]))

def warp(rgba, cx):
    h, w = rgba.shape[:2]
    f = (np.arange(h) - Y_TOP)/(Y_BOT - Y_TOP)
    s = sx(np.clip(f, 0, 1))[:,None].astype(np.float32)
    xs = np.arange(w, dtype=np.float32)[None,:]
    mapx = cx + (xs - cx)/s; mapy = np.repeat(np.arange(h, dtype=np.float32)[:,None], w, 1)
    a = rgba[...,3:4].astype(np.float32)/255
    pm = np.dstack([rgba[...,:3].astype(np.float32)*a, a*255])
    r = cv2.remap(pm, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT)
    al = np.clip(r[...,3:4], 0, 255); col = r[...,:3]/np.maximum(al/255, 1e-3)
    return np.dstack([np.clip(col,0,255), al]).astype(np.float32)

# ---- colour statistics (Lab, masked) ----
def lab_stats(imgs):
    px = []
    for im in imgs:
        m = im[...,3] > 230
        lab = cv2.cvtColor(im[...,:3].astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
        px.append(lab[m][::7])
    px = np.concatenate(px); return px.mean(0), px.std(0)
orig_imgs = [cv2.imread(f'/home/claude/game/video/walk_png/walk_{n:02d}.png', cv2.IMREAD_UNCHANGED) for n in range(0,24,3)]
mo, so = lab_stats(orig_imgs)

meta = {}
for name, c in CLIPS.items():
    src = [load(i) for i in c['frames']]
    cx = body_center(src[0])
    warped = [warp(s, cx) for s in src]
    mn, sn = lab_stats([w.astype(np.uint8) for w in warped])
    gain = np.clip(so/sn, 0.8, 1.25); gain[1:] = 1 + (gain[1:]-1)*0.5      # tone matched fully, hue/chroma halfway
    print(name, 'Lab mean orig', mo.round(1), 'new', mn.round(1), 'gain', gain.round(2))
    graded = []
    for w in warped:
        lab = cv2.cvtColor(np.clip(w[...,:3],0,255).astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
        tgt = np.array([mo[0], mn[1] + (mo[1]-mn[1])*0.6, mn[2] + (mo[2]-mn[2])*0.6], np.float32)
        lab = (lab - mn)*gain + tgt
        bgr = cv2.cvtColor(np.clip(lab,0,255).astype(np.uint8), cv2.COLOR_LAB2BGR)
        graded.append(np.dstack([bgr, w[...,3].astype(np.uint8)]))
    boxes = []
    for g in graded:
        ys, xs = np.where(g[...,3] > 20); boxes.append((xs.min(), ys.min(), xs.max(), ys.max()))
    x0 = max(0, min(b[0] for b in boxes) - 6); x1 = min(1280, max(b[2] for b in boxes) + 7); y0 = max(0, min(b[1] for b in boxes) - 6)
    fr = []
    for n, g in enumerate(graded):
        crop = g[y0:Y_CROP_BOT, x0:x1]
        crop = cv2.resize(crop, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_AREA)
        crop[...,3] = np.where(crop[...,3] < 30, 0, crop[...,3])
        img = Image.fromarray(crop[..., [2,1,0,3]])
        img.save(f'slap_png/slap{name}_{n:02d}.png', optimize=True)
        img.save(f'{OUT}/slap{name}_{n:02d}.webp', quality=82, method=6)
        fr.append(img.size)
    W, H = fr[0]
    hit = c['frames'].index(c['hit_src'])
    meta[name] = dict(n=len(graded), w=W, h=H, pivot=float((cx - x0)*SCALE / W), hit=hit, fps=30)
    print(name, meta[name], 'webp KB', sum(os.path.getsize(f'{OUT}/slap{name}_{n:02d}.webp') for n in range(len(graded)))//1024)
json.dump(meta, open(f'{OUT}/meta_slap.json','w'))
