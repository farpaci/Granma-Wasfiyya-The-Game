# Builds the 3-hit combo sprites: assets_enemy/{hit1,hit2,fall,down}_<id>.webp, new walk loops, assets_slap/kick_*.webp,
# and updates assets_enemy/meta_enemy.json + assets_slap/meta_slap.json. Sources: art/source/combo/*.  Intermediates: work/combo/.
# Usage: python3 tools/build_combo.py   (needs opencv-python-headless, scipy, numpy, pillow, ffmpeg)
import os, sys, json, glob, subprocess, heapq
import numpy as np, cv2
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_enemies as BE
ROOT = BE.ROOT; SRC = ROOT + '/art/source/combo'; W = ROOT + '/work/combo'; OUT = ROOT + '/assets_enemy'; OUTS = ROOT + '/assets_slap'
os.makedirs(W + '/tv', exist_ok=True)
HP_NEW = 350.   # head-to-feet px of the new men's walk sprites

# ---- per-man configuration ----
OLD = ['tank', 'tee', 'shirt', 'shemagh']                      # keep their video walk loops
NEW = ['thobe', 'hoodie', 'tourist', 'suit', 'courier', 'influencer', 'uncle']
IDS = ['thobe', 'tank', 'tee', 'hoodie', 'shirt', 'shemagh', 'tourist', 'suit', 'courier', 'influencer', 'uncle']
EXT = {'tank': 'jpg', 'tee': 'jpg', 'shirt': 'jpg', 'shemagh': 'jpg', 'tourist': 'jpg', 'suit': 'jpg'}
HIT1_MIRROR = {'tank', 'shirt', 'shemagh', 'suit', 'thobe', 'influencer'}   # hand on the screen-right cheek in the source
ROT = {'tee': 25., 'shirt': 15., 'shemagh': 25.}   # extra in-game lean (deg, + = top towards screen-right) for the barely-leaning dodges
# walk-sheet frames to drop (0-based, reading order)
DROP = {}
# seed points (preview coords of the 1400 px wide preview, x,y) per figure idx for touching blobs (watershed split)
PS = 2000 / 1400.
SEEDS = {
 'tank':  {2: [(720, 320), (710, 560), (620, 680), (790, 680), (600, 190)], 3: [(1040, 300), (960, 520), (840, 462), (960, 690), (950, 160)]},
 'tee':   {3: [(1010, 280), (960, 550), (810, 525), (975, 690), (900, 170)], 4: [(1190, 610), (1270, 665), (1020, 570), (1215, 525), (1010, 645), (1340, 600)]},
 'shirt': {2: [(720, 300), (700, 550), (640, 700), (780, 700), (630, 160)], 3: [(1000, 280), (1070, 170), (900, 420), (810, 540), (900, 670), (920, 100)]},
 'tourist': {2: [(680, 350), (650, 600), (640, 660), (760, 660), (610, 230)], 3: [(1010, 310), (1070, 225), (900, 420), (810, 505), (950, 600), (940, 640)],
             4: [(1200, 625), (1340, 600), (1020, 670), (910, 685), (1180, 735), (972, 583), (990, 603)]},
}

def disk(r): return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))

def load(path, minsz=1500):
    """-> BGRA uint8 (alpha from the file when it has real transparency, else green-keyed)"""
    im = Image.open(path)
    if im.mode == 'RGBA' and (np.array(im)[..., 3] < 250).mean() > .05:
        a = np.array(im); return a[..., [2, 1, 0, 3]].copy()
    return BE.key(cv2.cvtColor(np.array(im.convert('RGB')), cv2.COLOR_RGB2BGR), minsz)

def watershed(mask, seeds):
    """priority flood on the distance transform; seeds: list of (label, [(x, y)])  -> int32 labels"""
    dt = cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 5); lab = np.zeros(mask.shape, np.int32); h = []
    for l, pts in seeds:
        for x, y in pts:
            tmp = np.zeros(mask.shape, np.uint8); cv2.circle(tmp, (int(x), int(y)), 7, 1, -1); tmp = (tmp > 0) & mask & (lab == 0)
            ys, xs = np.where(tmp); lab[ys, xs] = l
            for yy, xx in zip(ys, xs): heapq.heappush(h, (-dt[yy, xx], yy, xx))
    H, Wd = mask.shape
    while h:
        _, y, x = heapq.heappop(h); l = lab[y, x]
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = y + dy, x + dx
            if 0 <= yy < H and 0 <= xx < Wd and mask[yy, xx] and lab[yy, xx] == 0:
                lab[yy, xx] = l; heapq.heappush(h, (-dt[yy, xx], yy, xx))
    return lab

def figures(bgra, n, seeds=None, big=20000):
    """split a sheet into n figures (sorted by x). Returns list of (bgra cropped to its bbox + pad, (x0,y0))"""
    m = bgra[..., 3] > 128; lab, k = ndimage.label(m); sz = ndimage.sum(m, lab, range(1, k + 1))
    owner = np.zeros(m.shape, np.int32); nid = 1; centres = {}
    seeded = {}
    if seeds:
        for f, pts in seeds.items():
            for x, y in pts:
                l = lab[int(y * PS), int(x * PS)]
                if l: seeded.setdefault(l, []).append(f); break
    for i in range(1, k + 1):
        if sz[i - 1] < big: continue
        if i in seeded:
            sl = [(f + 1, [(x * PS, y * PS) for x, y in seeds[f]]) for f in seeded[i]]
            w = watershed(lab == i, sl)
            for f in seeded[i]:
                owner[w == f + 1] = 100 + f; centres[100 + f] = None
            # detached bits of a figure that touch another figure belong to that one (shoe tips on the contact line)
            for f in seeded[i]:
                m1 = owner == 100 + f; l1, k1 = ndimage.label(m1)
                if k1 < 2: continue
                s1 = ndimage.sum(m1, l1, range(1, k1 + 1)); main = 1 + int(np.argmax(s1))
                for j in range(1, k1 + 1):
                    if j == main: continue
                    ring = ndimage.binary_dilation(l1 == j, iterations=3) & (owner >= 100) & (owner != 100 + f)
                    owner[l1 == j] = int(np.bincount(owner[ring]).argmax()) if ring.any() else 0
        else:
            owner[lab == i] = nid; centres[nid] = None; nid += 1
    ids = sorted(centres, key=lambda i: np.where(owner == i)[1].mean())
    assert len(ids) == n, (len(ids), n)
    # every other pixel with alpha (soft edges, small fragments) goes to the nearest figure
    idx = ndimage.distance_transform_edt(owner == 0, return_distances=False, return_indices=True)
    full = owner[idx[0], idx[1]]; res = []
    for i in ids:
        a = bgra[..., 3] * ((full == i) & (bgra[..., 3] > 0)); f = bgra.copy(); f[..., 3] = a
        ys, xs = np.where(a > 0); x0, x1, y0, y1 = max(xs.min() - 4, 0), xs.max() + 5, max(ys.min() - 4, 0), ys.max() + 5
        res.append(f[y0:y1, x0:x1])
    return res

def scale(bgra, k):
    f = bgra.astype(np.float32); f[..., :3] *= f[..., 3:4] / 255
    w = max(1, int(round(f.shape[1] * k))); h = max(1, int(round(f.shape[0] * k)))
    o = cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA); al = o[..., 3:4]
    o[..., :3] = np.where(al > .5, o[..., :3] / np.maximum(al, 1) * 255, 0); return o.clip(0, 255).astype(np.uint8)

def trim(bgra, pad=3):
    ys, xs = np.where(bgra[..., 3] > 20)
    return bgra[max(ys.min() - pad, 0):ys.max() + pad + 1, max(xs.min() - pad, 0):xs.max() + pad + 1]

def neutral_height(a):
    ys, xs = np.where(a > 128); cx = body_cx_(a); wf = xs.max() - xs.min()
    return ys.max() - BE.head_top(a, cx, wf), cx
def body_cx_(a): return BE.body_cx(a)

def head_info(a, hp):
    """head top row + head x via opening that removes arms/hands"""
    m = (a > 128).astype(np.uint8); r = max(2, int(.0375 * hp))
    o = cv2.morphologyEx(m, cv2.MORPH_OPEN, disk(r))
    if not o.any(): o = m
    ys, xs = np.where(o > 0); top = ys.min(); band = (ys < top + .08 * hp)
    return int(top), float(xs[band].mean())

def feet_x(a, hp):
    ys, xs = np.where(a > 128); b = ys > ys.max() - .05 * hp; return float(xs[b].mean())

def lean_deg(a, hp):
    top, hx = head_info(a, hp); ys, _ = np.where(a > 128)
    return float(np.degrees(np.arctan2(hx - feet_x(a, hp), ys.max() - top)))

def save_img(bgra, name): BE.save_webp(BE.to_img(BE.defringe(bgra)), f'{OUT}/{name}.webp')

# ---------- poses ----------
def export_poses(id_, figs, hp, report):
    nh, _ = neutral_height(figs[0][..., 3]); k = hp / nh; meta = {}
    for pi, name in ((1, 'hit1'), (2, 'hit2'), (3, 'fall'), (4, 'down')):
        f = figs[pi]; mir = False; a0 = f[..., 3]
        if name == 'hit1': mir = id_ in HIT1_MIRROR
        elif name in ('hit2', 'fall'): mir = lean_deg(a0, nh) < 0
        if mir: f = f[:, ::-1].copy()
        f = trim(scale(f, k)); a = f[..., 3]; h, w = a.shape
        ys, xs = np.where(a > 128); bot = ys.max()
        m = dict(w=int(w), h=int(h))
        if name == 'down': m['pivot'] = float((xs.min() + xs.max()) / 2 / w)
        elif name == 'hit1': m['pivot'] = float(BE.body_cx(a) / w)
        else: m['pivot'] = float(feet_x(a, hp) / w)
        if name in ('hit1', 'hit2'):
            top, _ = head_info(a, hp); m['face'] = float((top + .09 * hp) / h); m['headTop'] = float(top / h)
        if name == 'hit2':
            if id_ in ROT: m['rot'] = ROT[id_]
        if name == 'fall':
            m['hip'] = float(ndimage.center_of_mass(a > 128)[0] / h)
        m['mirrored'] = bool(mir)
        report.append(f'{id_} {name} mirror={mir} {m}')
        save_img(f, f'{name}_{id_}'); meta[name] = m
    return meta

# ---------- walk loops from sheets ----------
def sheet_frames(bgra):
    figs = figures(bgra, 8, None, big=15000)   # sorted by x
    # figures() sorts by x; rebuild reading order by row (needs positions): recompute from alpha centroids
    return figs

def walk_from_cells(id_, cells, hp, loop):
    """normalise cells (BGRA) to head-to-feet = hp, feet at BOT, torso centred; export walk_<id>_nn"""
    CW, CH, CX, BOT = BE.CW, BE.CH, BE.CX, BE.BOT; out = []
    for c in cells:
        a = c[..., 3]; ys, xs = np.where(a > 128); cx = BE.body_cx(a); top = BE.head_top(a, cx, xs.max() - xs.min()); k = hp / (ys.max() - top)
        M = np.float32([[k, 0, CX - k * cx], [0, k, BOT - k * ys.max()]]); out.append(BE.premul_resize(BE.defringe(c), M, (CW, CH)))
    return export_loop(id_, out, hp, loop, None)

def export_loop(id_, sel, hp, loop, extra):
    CW, BOT = BE.CW, BE.BOT
    boxes = [BE.bbox(f[..., 3], 20) for f in sel]
    x0 = max(0, min(b[0] for b in boxes) - 6); x1 = min(CW, max(b[2] for b in boxes) + 7); y0 = max(0, min(b[1] for b in boxes) - 4); y1 = BOT + 3
    pv = []; tops = []
    for k, f in enumerate(sel):
        crop = f[y0:y1, x0:x1]; save_img(crop, f'walk_{id_}_{k:02d}'); a = crop[..., 3]; pv.append(BE.body_cx(a))
        xs = np.where((a > 128).any(0))[0]; tops.append(BE.head_top(a, BE.body_cx(a), xs.max() - xs.min()))
    h = y1 - y0; ht = float(np.mean(tops))
    meta = dict(n=len(sel), w=int(x1 - x0), h=int(h), pivot=float(np.mean(pv)) / (x1 - x0), loop=loop, face=(ht + .09 * hp) / h, headTop=ht / h)
    return meta, float((BOT - y0) - ht), sel, (x0, x1, y0, y1)

def reading_order(bgra, n=8):
    m = bgra[..., 3] > 128; lab, k = ndimage.label(ndimage.binary_dilation(m, iterations=6)); lab = lab * m
    sz = ndimage.sum(m, lab, range(1, k + 1)); ids = [i + 1 for i in np.argsort(sz)[::-1][:n]]
    cen = {i: ndimage.center_of_mass(lab == i) for i in ids}; ys = sorted(c[0] for c in cen.values()); split = (ys[n // 2 - 1] + ys[n // 2]) / 2
    ids.sort(key=lambda i: (cen[i][0] > split, cen[i][1])); res = []
    for i in ids:
        a = bgra[..., 3] * (lab == i); f = bgra.copy(); f[..., 3] = a; yy, xx = np.where(a > 0)
        res.append(f[yy.min():yy.max() + 1, xx.min():xx.max() + 1])
    return res

def tourist_walk():
    if len(glob.glob(W + '/tv/f_*.png')) < 96:
        subprocess.check_call(['ffmpeg', '-loglevel', 'error', '-y', '-i', SRC + '/man_tourist_walk.mp4', '-t', '4', W + '/tv/f_%03d.png'])
    cells = []
    for i in range(22, 67):
        k = BE.key(cv2.imread(W + '/tv/f_%03d.png' % i), 400); m = k[..., 3] > 128; lab, n = ndimage.label(m)
        s = ndimage.sum(m, lab, range(1, n + 1)); big = lab == 1 + int(np.argmax(s)); k[..., 3] = (k[..., 3] * ndimage.binary_dilation(big, structure=disk(3))).astype(np.uint8)
        ys, xs = np.where(k[..., 3] > 128); cells.append(k[:, max(xs.min() - 6, 0):xs.max() + 7])
    fr, _ = BE.normalise(cells, HP_NEW)
    lp = W + '/tourist_loop.json'
    if os.path.exists(lp): c, s, P = json.load(open(lp))
    else:
        sm = [BE.small(f) for f in fr]; best = None; N = len(fr)
        for s in range(1, N - 1):
            for P in range(14, 26):
                if s + P + 1 >= N: break
                c = (BE.fdiff(sm[s], sm[s + P]) + BE.fdiff(sm[s + 1], sm[s + P + 1]) + BE.fdiff(sm[s - 1], sm[s + P - 1])) / 3
                if best is None or c < best[0]: best = (c, s, P)
        c, s, P = best; json.dump(best, open(lp, 'w'))
    n = P if P <= 16 else 16; idx = [s + int(round(k * P / n)) % P for k in range(n)]
    print('tourist loop', c, s, P, n)
    return export_loop('tourist', [fr[i] for i in idx], HP_NEW, P / 24., None)

# ---------- contact sheets ----------
def contact(id_, meta, path, sc=.5):
    ims = []
    for k in range(meta['walk']['n']): ims.append(Image.open(f'{OUT}/walk_{id_}_{k:02d}.webp').convert('RGBA'))
    for p in ('hit1', 'hit2', 'fall', 'down'): ims.append(Image.open(f'{OUT}/{p}_{id_}.webp').convert('RGBA'))
    ims = [im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS) for im in ims]
    Wd = sum(i.width for i in ims) + 6 * (len(ims) + 1); Ht = max(i.height for i in ims) + 10
    sh = Image.new('RGB', (Wd, Ht), (190, 0, 190)); x = 6
    from PIL import ImageDraw
    d = ImageDraw.Draw(sh)
    for j, im in enumerate(ims):
        sh.paste(im, (x, Ht - 5 - im.height), im)
        if j >= meta['walk']['n']:
            p = ('hit1', 'hit2')[j - meta['walk']['n']] if j - meta['walk']['n'] < 2 else None
            if p:
                fy = Ht - 5 - im.height + meta[p]['face'] * im.height; d.ellipse((x + im.width * meta[p]['pivot'] - 3, fy - 3, x + im.width * meta[p]['pivot'] + 3, fy + 3), fill=(255, 255, 0))
            d.line((x + im.width * meta[('hit1', 'hit2', 'fall', 'down')[j - meta['walk']['n']]]['pivot'], Ht - 14, x + im.width * meta[('hit1', 'hit2', 'fall', 'down')[j - meta['walk']['n']]]['pivot'], Ht - 3), fill=(0, 255, 255))
        x += im.width + 6
    sh.save(path)

# ---------- granma kick ----------
def kick():
    vm = json.load(open(ROOT + '/assets_video/meta.json')); sm = json.load(open(OUTS + '/meta_slap.json'))
    w0 = np.array(Image.open(ROOT + '/assets_video/walk_00.webp').convert('RGBA'))[..., 3]; ys, xs = np.where(w0 > 128)
    cx0 = BE.body_cx(w0); h0 = ys.max() - BE.head_top(w0, cx0, xs.max() - xs.min())   # head-to-feet of the walk sprite
    sheet = load(SRC + '/granma_kick_sheet.jpg', 4000); figs = figures(sheet, 3, None, big=40000)
    a2 = figs[2][..., 3]; ys2, xs2 = np.where(a2 > 128); nh = ys2.max() - BE.head_top(a2, BE.body_cx(a2), xs2.max() - xs2.min()); k = h0 / nh
    mpp = 1.85 / vm['h']; frames = []; foot = None
    for i, f in enumerate(figs):
        f = trim(scale(f, k)); a = f[..., 3]; h, w = a.shape; ys, xs = np.where(a > 128)
        fr = dict(w=int(w), h=int(h), pivot=float(BE.body_cx(a) / w), stand=float(feet_x_lowest(a) / w)); frames.append(fr)
        BE.save_webp(BE.to_img(BE.defringe(f)), f'{OUTS}/kick_{i}.webp')
        if i == 1:
            xr = xs.max(); yy = ys[xs >= xr - 3].mean(); px = fr['pivot'] * w
            foot = dict(x_m=float((xr - px) * mpp), y_m=float((ys.max() - yy) * mpp), x_frac=float((xr - px) / h), px=[int(xr), int(round(yy))])
        print('kick', i, fr, 'height', ys.max() - BE.head_top(a, BE.body_cx(a), xs.max() - xs.min()), 'target', h0)
    sm['K'] = dict(n=3, w=max(f['w'] for f in frames), h=max(f['h'] for f in frames), pivot=frames[0]['pivot'], frames=frames, foot=foot)
    json.dump(sm, open(OUTS + '/meta_slap.json', 'w'), indent=1) if False else open(OUTS + '/meta_slap.json', 'w').write(json.dumps(sm))
    ims = [Image.open(ROOT + '/assets_video/walk_00.webp').convert('RGBA')] + [Image.open(f'{OUTS}/kick_{i}.webp').convert('RGBA') for i in range(3)]
    Wd = sum(i.width for i in ims) + 40; Ht = max(i.height for i in ims) + 10; sh = Image.new('RGB', (Wd, Ht), (190, 0, 190)); x = 8
    for im in ims: sh.paste(im, (x, Ht - 5 - im.height), im); x += im.width + 8
    sh.save(W + '/sheet_granma.png'); return foot

def feet_x_lowest(a):
    ys, xs = np.where(a > 128); b = ys > ys.max() - 6; return float(xs[b].mean())

def main():
    old = json.load(open(OUT + '/meta_enemy.json')); meta = {}; report = []; rows = {}
    for p in glob.glob(OUT + '/frozen_*.webp') + glob.glob(OUT + '/walk_thobe_*.webp'): os.remove(p)
    for id_ in IDS:
        sh = load(f'{SRC}/man_{id_}_sheet.' + ('jpg' if id_ in EXT else 'webp'))
        figs = figures(sh, 5, SEEDS.get(id_))
        if id_ in OLD:
            meta[id_] = dict(walk=old[id_]['walk'], heightPx=old[id_]['heightPx']); hp = old[id_]['heightPx']
        else:
            if id_ == 'tourist': wm, hp, _, _ = tourist_walk()
            else:
                cells = reading_order(load(f'{SRC}/man_{id_}_walk_sheet.webp'))
                keep = [c for i, c in enumerate(cells) if i not in DROP.get(id_, ())]
                wm, hp, _, _ = walk_from_cells(id_, keep, HP_NEW, 1.04)
            meta[id_] = dict(walk=wm, heightPx=float(hp))
        meta[id_].update(export_poses(id_, figs, meta[id_]['heightPx'], report))
        contact(id_, meta[id_], f'{W}/sheet_{id_}.png')
    print('\n'.join(report))
    meta['_slapHand'] = old['_slapHand']
    json.dump(meta, open(OUT + '/meta_enemy.json', 'w'), indent=1)
    print('kick foot', kick())
    tot = sum(os.path.getsize(p) for p in glob.glob(OUT + '/*.webp')) // 1024; print('assets_enemy KB', tot)

if __name__ == '__main__': main()
