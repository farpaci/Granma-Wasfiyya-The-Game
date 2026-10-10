import cv2, numpy as np, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
os.makedirs(os.path.join(ROOT, 'work', 'slap'), exist_ok=True)
os.chdir(os.path.join(ROOT, 'work', 'slap'))  # raw/ in, keyed/ slap_png/ out
from scipy import ndimage
from concurrent.futures import ProcessPoolExecutor
os.makedirs('keyed', exist_ok=True)
def disk(r): return cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
def key(path):
    im = cv2.imread(path).astype(np.float32)
    b,g,r = im[...,0],im[...,1],im[...,2]
    spill = g - np.maximum(r,b)
    # background green has large spill; character has ~0 or negative
    bgspill = np.median(spill[:60, :200])
    t1 = bgspill*0.78; t0 = bgspill*0.38
    a = np.clip((t1 - spill)/(t1 - t0), 0, 1)
    a = cv2.GaussianBlur(a,(0,0),0.7)
    # remove tiny islands, fill pinholes
    m = a > 0.5
    lab,n = ndimage.label(m)
    if n:
        sizes = ndimage.sum(m, lab, range(1,n+1))
        keep = np.zeros(n+1,bool); keep[1:] = sizes > 1500
        keep[1+int(np.argmax(sizes))] = True
        m2 = keep[lab]
        a = a*ndimage.binary_dilation(m2, structure=disk(3))
    m = a>0.5
    m = ndimage.binary_fill_holes(m); a = np.maximum(a, m*1.0*(ndimage.binary_erosion(m, iterations=2)))
    # despill
    g2 = np.minimum(g, np.maximum(r,b)+2)
    out = np.dstack([b, g2, r, a*255]).clip(0,255).astype(np.uint8)
    return out
def job(i):
    out = key(f'raw/f_{i:03d}.png'); cv2.imwrite(f'keyed/k_{i:03d}.png', out)
    ys,xs = np.where(out[...,3]>128)
    return i, int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()), int((out[...,3]>128).sum())
if __name__=='__main__':
    with ProcessPoolExecutor(2) as ex: res = list(ex.map(job, range(1,241)))
    json.dump(res, open('bbox.json','w'))
    for r in res[::8]: print(r)
