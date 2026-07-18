import json, math
import numpy as np

d = json.load(open('mesh.json'))
V = np.array(d['v'])
tris = []
for f in d['f']:
    for k in range(1, len(f) - 1):
        tris.append((f[0], f[k], f[k+1]))
T = np.array(tris)

c = (V.max(0) + V.min(0)) / 2
V = V - c
V /= np.abs(V).max()

W, H = 78, 56
SS = 2                     # supersample factor
RAMP = " .,:;irsXA253hMHGS#9B&@"
TILT = math.radians(-14)

def render(angle):
    ca, sa = math.cos(angle), math.sin(angle)
    x = V[:,0]*ca - V[:,1]*sa
    y = V[:,0]*sa + V[:,1]*ca
    z = V[:,2]
    ct, st = math.cos(TILT), math.sin(TILT)
    yv = y*ct - z*st
    zv = y*st + z*ct
    ppu_y = (H-1) / 2.42
    ppu_x = ppu_y * 2.0
    sx = (W/2 + x * ppu_x) * SS
    sy = ((H-1)/2 - zv * ppu_y) * SS
    depth = yv

    HW, HH = W*SS, H*SS
    zbuf = np.full((HH, HW), 1e9)
    img = np.zeros((HH, HW))
    light = np.array([0.5, 0.7, -0.6]); light /= np.linalg.norm(light)
    P3 = np.stack([x, zv, yv], 1)

    for a, b, cc in T:
        n = np.cross(P3[b]-P3[a], P3[cc]-P3[a])
        nn = np.linalg.norm(n)
        if nn < 1e-12: continue
        lum = abs((n/nn) @ light)
        ax, ay, ad = sx[a], sy[a], depth[a]
        bx, by, bd = sx[b], sy[b], depth[b]
        cx, cy, cd = sx[cc], sy[cc], depth[cc]
        # vertex splats catch sub-pixel geometry
        for vx_, vy_, vd_ in ((ax,ay,ad),(bx,by,bd),(cx,cy,cd)):
            ix, iy = int(vx_), int(vy_)
            if 0 <= ix < HW and 0 <= iy < HH and vd_ < zbuf[iy, ix]:
                zbuf[iy, ix] = vd_; img[iy, ix] = lum
        x0 = max(int(min(ax,bx,cx)), 0); x1 = min(int(max(ax,bx,cx))+1, HW)
        y0 = max(int(min(ay,by,cy)), 0); y1 = min(int(max(ay,by,cy))+1, HH)
        if x0 >= x1 or y0 >= y1: continue
        d0 = (by-cy)*(ax-cx) + (cx-bx)*(ay-cy)
        if abs(d0) < 1e-12: continue
        for py in range(y0, y1):
            pyc = py + 0.5
            for px in range(x0, x1):
                pxc = px + 0.5
                w0 = ((by-cy)*(pxc-cx) + (cx-bx)*(pyc-cy)) / d0
                w1 = ((cy-ay)*(pxc-cx) + (ax-cx)*(pyc-cy)) / d0
                w2 = 1 - w0 - w1
                if w0 < -0.05 or w1 < -0.05 or w2 < -0.05: continue
                dep = w0*ad + w1*bd + w2*cd
                if dep < zbuf[py, px]:
                    zbuf[py, px] = dep
                    img[py, px] = lum

    # downsample: nearest-depth sample wins luminance, weighted by coverage
    lines = []
    for cy_ in range(H):
        chars = []
        for cx_ in range(W):
            block_z = zbuf[cy_*SS:(cy_+1)*SS, cx_*SS:(cx_+1)*SS]
            block_l = img[cy_*SS:(cy_+1)*SS, cx_*SS:(cx_+1)*SS]
            mask = block_z < 1e9
            cov = mask.sum() / (SS*SS)
            if cov == 0:
                chars.append(' '); continue
            i = np.unravel_index(np.argmin(block_z), block_z.shape)
            v = block_l[i] * (0.45 + 0.55*cov)
            chars.append(RAMP[min(int(v*(len(RAMP)-1))+1, len(RAMP)-1)])
        lines.append(''.join(chars).rstrip())
    return '\n'.join(lines)

if __name__ == '__main__':
    import sys, time
    if len(sys.argv) > 1 and sys.argv[1] == 'frames':
        N = 48
        frames = []
        t0 = time.time()
        for i in range(N):
            frames.append(render(2*math.pi*i/N))
            if i == 0: print('per-frame ~%.1fs' % (time.time()-t0))
        json.dump(frames, open('frames.json', 'w'))
        print('wrote', N, 'frames in %.0fs' % (time.time()-t0))
    else:
        print(render(math.radians(35)))
