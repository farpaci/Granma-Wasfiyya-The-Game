import cv2, numpy as np, glob, os, sys
from scipy import ndimage
os.makedirs('keyed', exist_ok=True)

def disk(r): return cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
def largest(m):
    lab,n = ndimage.label(m)
    if not n: return m
    sizes = ndimage.sum(m, lab, range(1,n+1)); return lab==(1+int(np.argmax(sizes)))

H,W = 688,1024
yy,xx = np.mgrid[0:H,0:W].astype(np.float32)
xn,yn = (xx-W/2)/W, (yy-H/2)/H
A = np.stack([np.ones_like(xn), xn, yn, xn*xn, xn*yn, yn*yn, xn**3, yn**3, xn*xn*yn, xn*yn*yn], -1).reshape(-1,10)

def bg_model(lab, fit):
    out = np.zeros((H*W,3), np.float32)
    idx = np.where(fit.reshape(-1))[0]
    sub = idx[::7]
    for c in range(3):
        coef,_,_,_ = np.linalg.lstsq(A[sub], lab[...,c].reshape(-1)[sub], rcond=None)
        out[:,c] = A@coef
    return out.reshape(H,W,3)

def process(path, dbg=False):
    im = cv2.imread(path)
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
    # exclude a generous central region + watermark corner when fitting background
    fit = np.ones((H,W), bool)
    fit[30:H, 250:700] = False
    fit[0:110, 900:1024] = False
    bg = bg_model(lab, fit)
    d = np.linalg.norm((lab-bg)*np.array([0.6,1.2,1.2],np.float32), axis=2)
    d[0:110, 880:1024] = 0           # watermark
    m0 = d > 16
    m0 = ndimage.binary_opening(m0, structure=disk(2))
    m0 = largest(ndimage.binary_closing(m0, structure=disk(4)))
    m0 = ndimage.binary_fill_holes(m0)
    # GrabCut refinement around the rough mask (soft shadow lives in the uncertain band)
    mask = np.full((H,W), cv2.GC_BGD, np.uint8)
    band = cv2.dilate(m0.astype(np.uint8), disk(9)) > 0
    mask[band] = cv2.GC_PR_BGD
    mask[m0] = cv2.GC_PR_FGD
    mask[ndimage.binary_erosion(m0, iterations=7)] = cv2.GC_FGD
    bgd = np.zeros((1,65)); fgd = np.zeros((1,65))
    cv2.grabCut(im, mask, None, bgd, fgd, 4, cv2.GC_INIT_WITH_MASK)
    m = ((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD))
    m = largest(ndimage.binary_opening(m, structure=disk(1)))
    # floor shadow: same chroma as the background (just darker) -> not the character
    chroma = np.linalg.norm((lab-bg)[...,1:], axis=2)
    ys0 = np.where(m.any(axis=1))[0]
    y_cut = ys0.min() + int((ys0.max()-ys0.min())*0.62)
    shadow = (chroma < 11) & (lab[...,0] < bg[...,0] + 4)
    shadow[:y_cut] = False
    m = m & ~ndimage.binary_dilation(shadow, structure=disk(1))
    # stricter near the ground, where olive specks blend with the shoes
    y_low = ys0.min() + int((ys0.max()-ys0.min())*0.66)
    specks = (chroma < 15) & (lab[...,0] < bg[...,0] + 6)
    specks[:y_low] = False
    m = m & ~ndimage.binary_dilation(specks, structure=disk(1))
    m = ndimage.binary_opening(m, structure=disk(2))
    lab_, n_ = ndimage.label(m)
    if n_:
        sizes = ndimage.sum(m, lab_, range(1, n_+1))
        keep = np.zeros(n_+1, bool)
        for k, sz in enumerate(sizes, 1):
            if sz > 350: keep[k] = True
        keep[1+int(np.argmax(sizes))] = True
        m = keep[lab_]
    m = ndimage.binary_fill_holes(m)
    return im, m, d

if __name__ == '__main__':
    ids = [int(a) for a in sys.argv[1:]]
    tiles=[]
    for i in ids:
        im,m,d = process(f'raw/f_{i:03d}.png')
        vis = np.full_like(im,(190,0,190)); vis[m] = im[m]
        ys,xs = np.where(m); print(i, 'bbox', xs.min(), ys.min(), xs.max(), ys.max(), 'area', m.sum())
        tiles.append(vis[40:688, 250:720])
    cv2.imwrite('probe.png', np.hstack(tiles))
