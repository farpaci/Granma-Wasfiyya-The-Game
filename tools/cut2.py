import cv2, numpy as np
from scipy import ndimage
BOX = {0:(575,268,940,932), 1:(490,303,820,962), 2:(605,316,920,914), 3:(655,306,945,874), 4:(482,231,812,1008), 5:(510,306,882,947)}

def run(im, mask, iters):
    bg = np.zeros((1,65)); fg = np.zeros((1,65))
    cv2.grabCut(im, mask, None, bg, fg, iters, cv2.GC_INIT_WITH_MASK)
    return (mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD)

def largest(m):
    lab,n = ndimage.label(m)
    if not n: return m
    sizes = ndimage.sum(m, lab, range(1,n+1)); return lab==(1+int(np.argmax(sizes)))

def disk(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))

out = {}
for i,(x0,y0,x1,y1) in BOX.items():
    im = cv2.imread(f'shots/s{i}.png')
    H,W = im.shape[:2]; bh = y1-y0; bw = x1-x0
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    dark = (hsv[...,2] < 55)
    red = ((hsv[...,0] < 8) | (hsv[...,0] > 170)) & (hsv[...,1] > 120) & (hsv[...,2] > 60) & (hsv[...,2] < 200)
    box = np.zeros((H,W), bool); box[y0:y1, x0:x1] = True

    mask = np.full((H,W), cv2.GC_BGD, np.uint8)
    mask[y0:y1, x0:x1] = cv2.GC_PR_BGD
    cx0,cy0,cx1,cy1 = x0+int(bw*.12), y0+int(bh*.08), x1-int(bw*.12), y0+int(bh*.78)
    mask[cy0:cy1, cx0:cx1] = cv2.GC_PR_FGD
    core = np.zeros((H,W), bool); core[cy0:cy1, cx0:cx1] = True
    mask[ndimage.binary_opening((dark|red)&box, iterations=2) & core] = cv2.GC_FGD
    m1 = largest(run(im, mask, 6))

    # pass 2: seed the leg zone from where the body sits at ~72% height
    r = y0 + int(bh*.72)
    xs = np.where(m1[r])[0]
    lx0, lx1 = xs.min(), xs.max()
    shrink = int((lx1-lx0)*.14)
    mask2 = np.full((H,W), cv2.GC_BGD, np.uint8)
    mask2[y0:y1, x0:x1] = cv2.GC_PR_BGD
    mask2[ndimage.binary_erosion(m1, iterations=8)] = cv2.GC_FGD
    leg = np.zeros((H,W), bool); leg[r:y1-4, lx0+shrink:lx1-shrink] = True
    mask2[leg & (mask2 != cv2.GC_FGD)] = cv2.GC_PR_FGD
    mask2[ndimage.binary_opening(red & box & (np.arange(H)[:,None] > r), iterations=1)] = cv2.GC_FGD
    m = largest(run(im, mask2, 8))

    # remove thin protrusions (posts, poles), keep body
    op = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, disk(11))
    keep = cv2.dilate(op, disk(5)) > 0
    # stronger opening in the upper body (hijab/shoulders) to drop poles
    up = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, disk(34))
    upk = cv2.dilate(up, disk(8)) > 0
    cut_row = y0 + int(bh*.30)
    keep[:cut_row] = upk[:cut_row]
    # but do not open away the feet: restore bottom part from m
    keep[r:] = m[r:]
    m = largest(m & keep)
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_opening(m, structure=disk(2))
    a = cv2.GaussianBlur(m.astype(np.float32),(0,0),1.0)
    # slight erode of alpha to cut background fringe
    a = np.clip((a-0.35)/0.65,0,1)
    rgba = np.dstack([im, (a*255).astype(np.uint8)])
    ys,xs = np.where(m)
    crop = rgba[ys.min():ys.max()+1, xs.min():xs.max()+1]
    np.save(f'shots/base{i}.npy', m); print(i, crop.shape[:2])
