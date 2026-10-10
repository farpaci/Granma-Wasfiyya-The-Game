# Builds assets_enemy/ (walk loops + frozen stills + meta_enemy.json) from art/source/enemies_*.
# Usage: python3 tools/build_enemies.py   (needs opencv-python-headless, scipy, numpy, pillow, ffmpeg)
import cv2, numpy as np, os, json, subprocess, glob, pickle
from scipy import ndimage
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.path.join(ROOT, 'work', 'enemy'); OUT = os.path.join(ROOT, 'assets_enemy'); SRC = os.path.join(ROOT, 'art', 'source')
os.makedirs(W + '/raw', exist_ok=True); os.makedirs(OUT, exist_ok=True)
IDS = ['thobe', 'tank', 'tee', 'hoodie', 'shirt', 'shemagh']   # video grid order (row-major)
FROZEN = {'hoodie': (1, 0), 'shirt': (1, 1), 'shemagh': (1, 2), 'thobe': (2, 0), 'tank': (2, 1), 'tee': (2, 2)}  # (jpg, column)
TARGET_H = 360; NOUT = 16; Q = 80
def disk(r): return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))

def key(im, minsz=1500):
    """BGR uint8 -> BGRA uint8: soft alpha from green spill, despilled, largest CC (+ big parts) kept."""
    f = im.astype(np.float32); b, g, r = f[..., 0], f[..., 1], f[..., 2]
    spill = g - np.maximum(r, b)
    bg = np.median(spill[spill > 60]) if (spill > 60).any() else 150.
    t1 = bg * .78; t0 = bg * .38
    a = np.clip((t1 - spill) / (t1 - t0), 0, 1)
    # shadows on the green keep the chroma ratio but have low spill: also key on spill/g
    ratio = spill / (g + 1); rb = np.median(ratio[spill > 60]) if (spill > 60).any() else .8
    ar = np.where(g > 40, np.clip((.85 * rb - ratio) / (.30 * rb), 0, 1), 1)
    a = np.minimum(a, ar)
    a = cv2.GaussianBlur(a, (0, 0), 0.7)
    m = a > .5
    lab, n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1, n + 1)); keep = np.zeros(n + 1, bool)
        keep[1:] = sizes > minsz; keep[1 + int(np.argmax(sizes))] = True
        a = a * ndimage.binary_dilation(keep[lab], structure=disk(3))
    m = a > .5
    # fill only tiny holes (inside fists); big enclosed background (arm/leg gaps) stays transparent
    hl, hn = ndimage.label(ndimage.binary_fill_holes(m) & ~m)
    if hn:
        hs = ndimage.sum(np.ones_like(hl), hl, range(1, hn + 1)); small = np.zeros(hn + 1, bool); small[1:] = hs < 60
        m = m | small[hl]
    a = np.maximum(a, m * 1. * ndimage.binary_erosion(m, iterations=2))
    # replace green-contaminated colour inside the figure by the nearest clean pixel
    clean = (a > .9) & (spill < .12 * bg); clean = ndimage.binary_erosion(clean, iterations=1) | (clean & (spill < 0))
    idx = ndimage.distance_transform_edt(~clean, return_distances=False, return_indices=True)
    bad = (spill >= .12 * bg) & (a > 0)
    for ch in (b, g, r): ch[bad] = ch[idx[0], idx[1]][bad]
    # edge band: skin/green mixes read olive (g~r, g>>b) but have no 'spill'; repaint from the interior
    dist = ndimage.distance_transform_edt(a > .5); band = (a > 0) & (dist <= 4)
    olive = band & (g - r > -30) & (g - b > 15); good = (a > .9) & (dist > 4) & ~((g - r > -30) & (g - b > 15))
    idx = ndimage.distance_transform_edt(~good, return_distances=False, return_indices=True)
    for ch in (b, g, r): ch[olive] = ch[idx[0], idx[1]][olive]
    g2 = np.minimum(g, np.maximum(r, b) + 2)
    return np.dstack([b, g2, r, a * 255]).clip(0, 255).astype(np.uint8)

def defringe(bgra):
    a = bgra[..., 3]
    solid = ndimage.binary_erosion(a > 215, iterations=2)
    idx = ndimage.distance_transform_edt(~solid, return_distances=False, return_indices=True)
    out = bgra.copy(); edge = ~solid & (a > 0)
    out[..., :3][edge] = bgra[..., :3][idx[0], idx[1]][edge]
    out[..., 3] = np.where(a < 40, 0, a)
    return out

def bbox(a, th=128):
    ys, xs = np.where(a > th); return xs.min(), ys.min(), xs.max(), ys.max()

def body_cx(a):
    """x centre of the torso band (steadier than arms/legs)"""
    ys = np.where((a > 128).any(axis=1))[0]; h = ys.max() - ys.min()
    xs = [np.where(a[r] > 128)[0].mean() for r in range(ys.min() + int(.1 * h), ys.min() + int(.45 * h)) if (a[r] > 128).any()]
    return float(np.mean(xs))

def head_top(a, cx, wfig):
    """topmost mask row in a narrow band around the body centre (ignores raised hands)"""
    x0 = int(cx - .12 * wfig); x1 = int(cx + .12 * wfig)
    rows = np.where((a[:, max(x0, 0):x1] > 128).any(axis=1))[0]; return int(rows.min())

def face_y(a, top, bot):
    # face centre ~ 0.07 of the standing height below the head top (head ~ 0.13 H, face centre near the middle of the head)
    return top + .075 * (bot - top)

def to_img(f): return Image.fromarray(f[..., [2, 1, 0, 3]])

def save_webp(img, path): img.save(path, quality=Q, method=6, exact=True)

# ---------- walk video ----------
def extract():
    if len(glob.glob(W + '/raw/f_*.png')) < 124:
        subprocess.check_call(['ffmpeg', '-loglevel', 'error', '-y', '-i', SRC + '/enemies_walk.mp4', W + '/raw/f_%03d.png'])

def watermark_boxes(frames):
    """locate the jumping viggle.ai watermark per frame by template matching a clean sighting (frame 1)"""
    wm = lambda im: (im.min(2) > 225).astype(np.float32)
    t = wm(frames[0])[350:420, 38:245]; boxes = []
    for im in frames:
        r = cv2.matchTemplate(wm(im), t, cv2.TM_CCOEFF_NORMED); _, mx, _, loc = cv2.minMaxLoc(r)
        boxes.append((loc[0] - 4, loc[1] - 4, loc[0] + t.shape[1] + 4, loc[1] + t.shape[0] + 4) if mx > .6 else None)
    return boxes

def process_video():
    cache = W + '/keyed.pkl'
    if os.path.exists(cache): return pickle.load(open(cache, 'rb'))
    extract(); N = 124
    raws = [cv2.imread(W + '/raw/f_%03d.png' % (i + 1)) for i in range(N)]
    wb = watermark_boxes(raws); H, Wd = raws[0].shape[:2]
    keyed = {i: [] for i in IDS}; dirty = {i: [] for i in IDS}
    for fi, im in enumerate(raws):
        k_full = key(im, 400)
        clean = im.copy()
        if wb[fi]:
            x0, y0, x1, y1 = wb[fi]; clean[max(y0, 0):y1, max(x0, 0):x1] = np.median(im[:5, :5].reshape(-1, 3), 0)
        k = key(clean, 400)
        for ci, id_ in enumerate(IDS):
            r, c = divmod(ci, 3); y0, y1, x0, x1 = r * H // 2, (r + 1) * H // 2, c * Wd // 3, (c + 1) * Wd // 3
            cell = k[y0:y1, x0:x1].copy(); cellf = k_full[y0:y1, x0:x1]
            # keep the biggest component of the cell only
            m = cell[..., 3] > 128; lab, n = ndimage.label(m)
            if n > 1:
                s = ndimage.sum(m, lab, range(1, n + 1)); big = lab == 1 + int(np.argmax(s))
                cell[..., 3] = (cell[..., 3] * ndimage.binary_dilation(big, structure=disk(3))).astype(np.uint8)
            # contaminated if blanking the watermark box removed a chunk of the man
            full_m = cellf[..., 3] > 128; lab, n = ndimage.label(full_m)
            sz_full = ndimage.sum(full_m, lab, range(1, n + 1)).max() if n else 0
            sz_clean = (cell[..., 3] > 128).sum()
            hit = False
            if wb[fi]:
                bx0, by0, bx1, by1 = wb[fi]; mm = cell[..., 3] > 128
                bb = (mm.any() and True)
                # watermark box (cell coords) touches the man's mask => unsafe
                sub = np.zeros_like(mm); sub[max(by0 - y0, 0):max(by1 - y0, 0), max(bx0 - x0, 0):max(bx1 - x0, 0)] = True
                hit = bool((ndimage.binary_dilation(mm, iterations=6) & sub).any()) and sub.any()
                if not hit and abs(sz_full - sz_clean) > 0.02 * sz_clean: hit = True
            keyed[id_].append(cell); dirty[id_].append(hit)
    pickle.dump((keyed, dirty), open(cache, 'wb'), protocol=4)
    return keyed, dirty

# ---------- normalise + loop ----------
CW, CH, CX, BOT = 720, 440, 360, 420
def premul_resize(bgra, M, size):
    f = bgra.astype(np.float32); f[..., :3] *= f[..., 3:4] / 255
    o = cv2.warpAffine(f, M, size, flags=cv2.INTER_LINEAR, borderValue=0)
    a = o[..., 3:4]; o[..., :3] = np.where(a > 0.5, o[..., :3] / np.maximum(a, 1) * 255, 0)
    return o.clip(0, 255).astype(np.uint8)

def smooth(v, r):
    v = np.asarray(v, float); p = np.pad(v, r, mode='edge'); return np.convolve(p, np.ones(2 * r + 1) / (2 * r + 1), 'valid')

def normalise(cells, height):
    """scale every frame to a constant trend height (cancels the slow camera zoom), feet at BOT, body centred at CX"""
    bb = [bbox(c[..., 3]) for c in cells]; hs = np.array([b[3] - b[1] for b in bb], float)
    t = np.polyval(np.polyfit(np.arange(len(hs)), hs, 2), np.arange(len(hs)))
    cxs = smooth([body_cx(c[..., 3]) for c in cells], 12); out = []
    for i, c in enumerate(cells):
        k = height / t[i]; M = np.float32([[k, 0, CX - k * cxs[i]], [0, k, BOT - k * bb[i][3]]])
        out.append(premul_resize(defringe(c), M, (CW, CH)))
    return out, float(np.mean(t))

def small(a): return cv2.resize(a, None, fx=.25, fy=.25, interpolation=cv2.INTER_AREA).astype(np.float32)
def fdiff(sa, sb):
    w = np.maximum(sa[..., 3], sb[..., 3]) / 255
    return float(((np.abs(sa[..., :3] - sb[..., :3]).mean(2) * w).sum() + np.abs(sa[..., 3] - sb[..., 3]).sum() * .5) / max((sa[..., 3] > 128).sum(), 1))

def find_loop(fr, dirty):
    best = None; N = len(fr); fr = [small(f) for f in fr]
    for s in range(1, N - 1):
        for P in range(12, 41):
            if s + P + 1 >= N: break
            if any(dirty[s - 1:s + P + 2]): continue
            c = (fdiff(fr[s], fr[s + P]) + fdiff(fr[s + 1], fr[s + P + 1]) + fdiff(fr[s - 1], fr[s + P - 1])) / 3 * (1 + .004 * P)
            if best is None or c < best[0]: best = (c, s, P)
    return best

def export_walk(id_, cells, dirty):
    fr, hmean = normalise(cells, 340.)
    lp = W + '/loops.json'; cache = json.load(open(lp)) if os.path.exists(lp) else {}
    if id_ not in cache: cache[id_] = find_loop(fr, dirty); json.dump(cache, open(lp, 'w'))
    c, s, P = cache[id_]; n = P if P < NOUT else NOUT
    idx = [s + int(round(k * P / n)) % P for k in range(n)]; sel = [fr[i] for i in idx]
    boxes = [bbox(f[..., 3], 20) for f in sel]
    x0 = max(0, min(b[0] for b in boxes) - 6); x1 = min(CW, max(b[2] for b in boxes) + 7); y0 = max(0, min(b[1] for b in boxes) - 4); y1 = BOT + 3
    tops = []; pv = []
    for k, f in enumerate(sel):
        crop = f[y0:y1, x0:x1]; save_webp(to_img(crop), f'{OUT}/walk_{id_}_{k:02d}.webp')
        a = crop[..., 3]; pv.append(body_cx(a)); tops.append(bbox(a)[1])
    h = y1 - y0; top = float(np.mean(tops)); hp = (BOT - y0) - top
    meta = dict(n=n, w=int(x1 - x0), h=int(h), pivot=float(np.mean(pv)) / (x1 - x0), loop=P / 24., face=0., period=P, start=s, cost=round(c, 2))
    return meta, hp, y0, sel, (x0, x1, y0, y1)

# ---------- frozen stills ----------
FACE = {'shemagh': .105}
def export_frozen(id_, bgra, walk_meta, hp):
    a = bgra[..., 3]; x0, y0, x1, y1 = bbox(a, 20); fig_w = x1 - x0
    cx = body_cx(a); top = head_top(a, cx, fig_w); bot = y1
    stand = bot - top; k = hp / stand
    pad = 6; cx0 = max(0, x0 - pad); cx1 = min(a.shape[1], x1 + pad + 1); cy0 = max(0, y0 - pad); cy1 = min(a.shape[0], bot + 4)
    crop = defringe(bgra)[cy0:cy1, cx0:cx1]
    w = int(round(crop.shape[1] * k)); h = int(round(crop.shape[0] * k))
    f = crop.astype(np.float32); f[..., :3] *= f[..., 3:4] / 255
    o = cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA); al = o[..., 3:4]
    o[..., :3] = np.where(al > .5, o[..., :3] / np.maximum(al, 1) * 255, 0); o = o.clip(0, 255).astype(np.uint8)
    save_webp(to_img(o), f'{OUT}/frozen_{id_}.webp')
    ttop = (top - cy0) * k
    fh = (ttop + FACE.get(id_, .09) * hp) / h
    return dict(w=w, h=h, pivot=(cx - cx0) * k / w, face=float(fh), headTop=float(ttop / h))

def frozen_all(hps):
    res = {}
    for jp in (1, 2):
        im = cv2.imread(f'{SRC}/enemies_frozen_{jp}.jpg'); k = key(im, 4000); m = k[..., 3] > 128
        lab, n = ndimage.label(m); s = ndimage.sum(m, lab, range(1, n + 1)); top3 = np.argsort(s)[::-1][:3] + 1
        comps = sorted(top3, key=lambda l: np.where(lab == l)[1].mean())
        ids = [i for i, (j, c) in FROZEN.items() if j == jp]; ids.sort(key=lambda i: FROZEN[i][1])
        for id_, l in zip(ids, comps):
            kk = k.copy(); kk[..., 3] = (kk[..., 3] * ndimage.binary_dilation(lab == l, structure=disk(3))).astype(np.uint8)
            res[id_] = kk
    return res

# ---------- granma slap contact point ----------
def slap_hand():
    sm = json.load(open(f'{ROOT}/assets_slap/meta_slap.json')); vm = json.load(open(f'{ROOT}/assets_video/meta.json'))
    PLAYER_H = 1.85; mpp = PLAYER_H / vm['h']; res = {}
    for c in 'AB':
        m = sm[c]; im = np.array(Image.open(f'{ROOT}/assets_slap/slap{c}_{m["hit"]:02d}.webp').convert('RGBA'))
        a = im[..., 3] > 128; ys, xs = np.where(a); xr = xs.max(); yy = ys[xs >= xr - 3].mean()
        feet = ys.max()
        res[c] = dict(x_m=float((xr - m['pivot'] * m['w']) * mpp), y_m=float((feet - yy) * mpp), x_frac=float((xr - m['pivot'] * m['w']) / m['h']),
                      y_frac=float((feet - yy) / m['h']), hit_px=[int(xr), int(round(yy))], feet_px=int(feet))
    return res

def sheet(rows, path):
    """rows: list of lists of RGBA PIL images (scaled to fit), on magenta"""
    th = 200; ims = [[im.resize((max(1, int(im.width * th / im.height)), th), Image.LANCZOS) for im in r] for r in rows]
    Wd = max(sum(i.width for i in r) for r in ims) + 10 * 20; sh = Image.new('RGB', (min(Wd, 4200), (th + 6) * len(ims)), (190, 0, 190))
    for ri, r in enumerate(ims):
        x = 3
        for im in r: sh.paste(im, (x, 3 + ri * (th + 6)), im); x += im.width
    sh.save(path)

def main():
    keyed, dirty = process_video(); meta = {}; sheets = []
    for id_ in IDS:
        wm, hp, _, sel, box = export_walk(id_, keyed[id_], dirty[id_]); meta[id_] = dict(walk=wm, heightPx=float(hp)); print(id_, wm, round(hp, 1))
        sheets.append((id_, sel, box))
    fz = frozen_all(None); rows = []
    for id_ in IDS:
        wm = meta[id_]['walk']; fm = export_frozen(id_, fz[id_], wm, meta[id_]['heightPx']); meta[id_]['frozen'] = fm
        wm['headTop'] = None
    # walk face/headTop: measured from the first exported frame's head top
    for id_, sel, (x0, x1, y0, y1) in sheets:
        wm = meta[id_]['walk']; tops = []
        for f in sel:
            c = f[y0:y1, x0:x1][..., 3]; cx = body_cx(c); xs = np.where((c > 128).any(0))[0]; tops.append(head_top(c, cx, xs.max() - xs.min()))
        ht = float(np.mean(tops)); wm['headTop'] = ht / wm['h']; wm['face'] = (ht + FACE.get(id_, .09) * meta[id_]['heightPx']) / wm['h']
        wm.pop('cost', None)
        rows.append([Image.open(f'{OUT}/walk_{id_}_{k:02d}.webp').convert('RGBA') for k in range(wm['n'])] + [Image.open(f'{OUT}/frozen_{id_}.webp').convert('RGBA')])
    meta['_slapHand'] = slap_hand()
    json.dump(meta, open(f'{OUT}/meta_enemy.json', 'w'), indent=1)
    for i in range(0, 6, 2): sheet(rows[i:i + 2], f'{W}/sheet_{i // 2}.png')
    tot = sum(os.path.getsize(p) for p in glob.glob(OUT + '/*.webp')); print('total KB', tot // 1024); print(meta['_slapHand'])

if __name__ == '__main__': main()
