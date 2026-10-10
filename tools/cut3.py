import os
import cv2, numpy as np
from scipy import ndimage
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
os.chdir(os.path.join(ROOT, 'work'))  # shots/ (s0-5.png in, base/cut out) lives here

POLY = {
 0: [[(758,806),(803,806),(803,832),(800,840),(798,860),(812,868),(822,890),(820,912),(805,922),(765,920),(742,905),(742,885),(752,866),(758,850),(757,832)]],
 1: [[(552,805),(640,803),(642,830),(625,836),(622,862),(626,880),(628,905),(630,925),(628,945),(612,953),(580,950),(565,940),(562,915),(570,895),(573,865),(572,840),(558,840),(550,825)]],
 3: [[(708,742),(765,742),(764,758),(760,775),(757,800),(762,818),(758,845),(750,862),(725,866),(700,858),(692,845),(700,825),(716,815),(716,790),(714,760),(706,752)]],
 4: [[(545,815),(634,812),(636,850),(632,880),(620,892),(622,925),(628,945),(637,962),(636,988),(622,999),(583,1001),(564,992),(562,968),(568,950),(566,918),(570,893),(556,885),(546,860)],
     [(656,812),(722,810),(724,838),(712,852),(702,858),(701,885),(712,880),(724,888),(726,905),(716,920),(690,928),(658,922),(652,905),(656,885),(660,858),(655,840)]],
 5: [[(690,850),(752,850),(756,880),(746,900),(730,890),(728,925),(735,935),(762,935),(780,952),(778,968),(745,978),(700,975),(668,962),(668,945),(680,935),(684,910),(678,890),(690,872)]],
}

EXCL = {
 1: [[(717,340),(760,340),(760,402),(717,402)]],
 3: [[(695,365),(742,365),(742,377),(737,382),(730,392),(720,402),(707,415),(702,422),(695,422),(680,340),(742,340)]],
}

def largest(m):
    lab,n = ndimage.label(m)
    if not n: return m
    sizes = ndimage.sum(m, lab, range(1,n+1)); return lab==(1+int(np.argmax(sizes)))

def disk(r):
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))

for i in range(6):
    im = cv2.imread(f'shots/s{i}.png'); H,W = im.shape[:2]
    base = np.load(f'shots/base{i}.npy')
    if i in EXCL:
        ex = np.zeros((H,W), np.uint8)
        for p in EXCL[i]: cv2.fillPoly(ex, [np.array(p, np.int32)], 1)
        base = base & ~(ex.astype(bool))
        base = largest(ndimage.binary_opening(base, structure=disk(3)))
    # head zone only contains the black hijab: drop any bright/brown pixel there (poles, lamps)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    ys0 = np.where(base.any(axis=1))[0]; yt, yb = ys0.min(), ys0.max()
    head = np.zeros((H,W), bool); head[yt:yt+int((yb-yt)*.16)] = True
    bad = head & (hsv[...,1] > 85) & (hsv[...,2] > 55)
    bad = cv2.dilate(bad.astype(np.uint8), disk(2)) > 0
    base = largest(ndimage.binary_opening(base & ~bad, structure=disk(2)))
    m = base.copy()
    if i in POLY:
        poly = np.zeros((H,W), np.uint8)
        for p in POLY[i]:
            cv2.fillPoly(poly, [np.array(p, np.int32)], 1)
        poly = poly.astype(bool)
        ys,xs = np.where(poly)
        pad = 25
        bx0,bx1,by0,by1 = max(0,xs.min()-pad), min(W,xs.max()+pad), max(0,ys.min()-pad), min(H,ys.max()+pad)
        mask = np.full((H,W), cv2.GC_BGD, np.uint8)
        mask[by0:by1, bx0:bx1] = cv2.GC_PR_BGD
        dil = cv2.dilate(poly.astype(np.uint8), disk(5)) > 0
        ero = cv2.erode(poly.astype(np.uint8), disk(7)) > 0
        mask[dil] = cv2.GC_PR_FGD
        mask[ero] = cv2.GC_FGD
        mask[ndimage.binary_erosion(base, iterations=6)] = cv2.GC_FGD
        bg = np.zeros((1,65)); fg = np.zeros((1,65))
        cv2.grabCut(im, mask, None, bg, fg, 6, cv2.GC_INIT_WITH_MASK)
        leg = ((mask==cv2.GC_FGD)|(mask==cv2.GC_PR_FGD)) & dil
        m = base | leg
    m = largest(m)
    m = ndimage.binary_fill_holes(m)
    m = ndimage.binary_opening(m, structure=disk(1))
    a = cv2.GaussianBlur(m.astype(np.float32),(0,0),0.9)
    a = np.clip((a-0.3)/0.7,0,1)
    rgba = np.dstack([im, (a*255).astype(np.uint8)])
    ys,xs = np.where(m)
    crop = rgba[ys.min():ys.max()+1, xs.min():xs.max()+1]
    cv2.imwrite(f'shots/cut{i}.png', crop); print(i, crop.shape[:2])
