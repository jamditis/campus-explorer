"""wp: raise WM_litter_mask in the ravine-head woodland hollow (OSM wood 315835594
AND (2017 CHM canopy>3 OR the low ravine floor)), including gaps between crowns.
Does NOT paint the Stone Hall lawn plateau (outside OSM wood, CHM~0).
Existing mask elsewhere is unchanged (max-merge)."""
import numpy as np, json, os, shutil
from scipy import ndimage as nd
from PIL import Image

R = '/workspace/nj-scenes/montclair-state'
os.makedirs(f'{R}/data/wp', exist_ok=True)

src_npz = f'{R}/data/wm/litter_mask_wm.npz'
src_png = f'{R}/data/wm/wm_litter_mask.png'
shutil.copy2(src_npz, f'{R}/data/wp/litter_mask_wm_pre_wp.npz')
shutil.copy2(src_png, f'{R}/data/wp/wm_litter_mask_pre_wp.png')

z = np.load(src_npz)
M = z['m'].copy()
Mpre = z['m_pre_trees'].copy() if 'm_pre_trees' in z.files else M.copy()
extent = z['extent']
X0, Y0, NX, NY = 120.0, 215.0, 200, 205
assert M.shape == (NY, NX)

wood = json.load(open(f'{R}/data/wk/wood.json'))
ring = np.array(wood['ring'])

def pip(px, py, poly):
    ins = np.zeros(px.shape, bool)
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        ins ^= ((y1 > py) != (y2 > py)) & (px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-12) + x1)
    return ins

g = np.load(f'{R}/data/wo/chm_grid_sw_1m.npz')
dtm = g[[k for k in g.files if k.endswith('dtm')][0]]
dsm = g[[k for k in g.files if k.endswith('dsm')][0]]
chm = dsm - dtm
GX0, GY0 = 40, 140

# ravine-head region: WO box plus a small WJ/WF overlap so the seam matches
RX0, RX1, RY0, RY1 = 155, 195, 292, 328
gx, gy = np.meshgrid(X0 + np.arange(NX) + 0.5, Y0 + np.arange(NY) + 0.5)
region = (gx >= RX0) & (gx <= RX1) & (gy >= RY0) & (gy <= RY1)
inw = pip(gx, gy, ring)

# sample DTM/CHM onto the mask grid (1 m, same world integers)
ix = np.clip(np.round(gx).astype(int) - GX0, 0, dtm.shape[1] - 1)
iy = np.clip(np.round(gy).astype(int) - GY0, 0, dtm.shape[0] - 1)
in_wo_grid = ((gx >= GX0) & (gx <= GX0 + dtm.shape[1] - 1)
              & (gy >= GY0) & (gy <= GY0 + dtm.shape[0] - 1))
D = np.full(M.shape, np.nan); C = np.full(M.shape, np.nan)
D[in_wo_grid] = dtm[iy[in_wo_grid], ix[in_wo_grid]]
C[in_wo_grid] = chm[iy[in_wo_grid], ix[in_wo_grid]]

canopy = np.isfinite(C) & (C > 3)
hollow = np.isfinite(D) & (D < 134.5)
# woodland floor inside the region: OSM wood AND (canopy OR ravine-head hollow)
# hollow is already 100% inside wood in this box; keep the AND as a safety clip
floor = region & inw & (canopy | hollow)

# soft fill of gaps between crowns, then clip back to OSM wood so the Stone Hall
# lawn plateau (outside the wood polygon) cannot pick up bleed
base = floor.astype(float)
base = nd.gaussian_filter(base, 1.2)
base = np.clip(base, 0, 1) * inw * region

M2 = np.maximum(M, base)

def stats(arr, pred, name):
    sub = arr[pred]
    print(f'  {name:22s} n={pred.sum():4d} min={sub.min():.3f} max={sub.max():.3f} '
          f'mean={sub.mean():.3f} >0.2={(sub>0.2).mean():.3f} >0.5={(sub>0.5).mean():.3f}')

wo = (gx >= 155) & (gx <= 182) & (gy >= 292) & (gy <= 320)
wo_h = wo & (np.isfinite(D) & (D < 134.5))
wo_p = wo & (gx <= 170) & (gy <= 310)
wj = (gx >= 190) & (gx <= 220) & (gy >= 300) & (gy <= 318)
print('BEFORE')
stats(M, wo_h, 'WO hollow')
stats(M, wo_p, 'WO plateau')
stats(M, wo, 'WO all')
stats(M, wj, 'WJ core')
print('AFTER')
stats(M2, wo_h, 'WO hollow')
stats(M2, wo_p, 'WO plateau')
stats(M2, wo, 'WO all')
stats(M2, wj, 'WJ core')
print('raised cells', int((M2 - M > 0.02).sum()), 'max raise', float((M2 - M).max()),
      'raised in plateau', int(((M2 - M > 0.02) & wo_p).sum()),
      'raised outside wood', int(((M2 - M > 0.02) & ~inw).sum()))

np.savez(f'{R}/data/wm/litter_mask_wm.npz', m=M2, m_pre_trees=Mpre, m_pre_wp=M,
         extent=extent)
np.savez(f'{R}/data/wp/litter_mask_wm.npz', m=M2, m_pre_trees=Mpre, m_pre_wp=M,
         extent=extent)
png = (np.flipud(M2) * 65535).astype(np.uint16)
Image.fromarray(png).save(f'{R}/data/wm/wm_litter_mask.png')
Image.fromarray(png).save(f'{R}/data/wp/wm_litter_mask.png')
print('wrote mask png/npz')
# ascii after for WO
print('AFTER WO mask (y from 320):')
xs = np.arange(155, 183); ys = np.arange(292, 321)
i0, j0 = int(155 - X0), int(292 - Y0)
sub = M2[j0:j0 + 29, i0:i0 + 28]
for j in range(sub.shape[0] - 1, -1, -2):
    row = ''.join('#' if sub[j, i] > 0.6 else ('+' if sub[j, i] > 0.2 else ('.' if sub[j, i] > 0.05 else ' '))
                  for i in range(0, sub.shape[1], 2))
    print(f'  {int(ys[j]):3d} |{row}|')
