import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2, json
from key import process  # also chdirs into work/video
from concurrent.futures import ProcessPoolExecutor
def job(i):
    im,m,d = process(f'raw/f_{i:03d}.png')
    ys,xs = np.where(m)
    a = cv2.GaussianBlur(m.astype(np.float32),(0,0),0.9); a = np.clip((a-0.3)/0.7,0,1)
    rgba = np.dstack([im,(a*255).astype(np.uint8)])
    cv2.imwrite(f'keyed/k_{i:03d}.png', rgba)
    return i, int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()), int(m.sum())
if __name__=='__main__':
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(job, range(1,122)))
    json.dump(res, open('bbox.json','w'))
    for r in res[::6]: print(r)
    print('touch bottom:', [r[0] for r in res if r[4]>=686])
