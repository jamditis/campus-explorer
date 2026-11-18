import numpy as np, json
c=np.load('data/wo/coverage.npz'); p=np.load('data/wq/probe_rasters.npz')
g=np.load('data/wo/chm_grid_sw_1m.npz'); k=[q for q in g.files if q.endswith('dtm')][0]; dtm=g[k]
xs=p['xs']; ys=p['ys']; X,Y=np.meshgrid(xs,ys)
dz=dtm-c['skz']
out={'names':[str(n) for n in c['names']]}
tiles={'A_west_x40-80':(40,80),'B_mid_x80-120':(80,120),'C_east_x120-155':(120,155)}
for tn,(x0,x1) in tiles.items():
    m=(X>=x0)&(X<x1)&(Y>=245)&(Y<320)
    unc=m&(c['cov']==0); f=unc&np.isfinite(dz)
    d=dz[f]
    out[tn]={'cells':int(m.sum()),'uncovered':int(unc.sum()),
      'dz_median':round(float(np.median(d)),2) if d.size else None,
      'dz_p5':round(float(np.percentile(d,5)),2) if d.size else None,'dz_p95':round(float(np.percentile(d,95)),2) if d.size else None,
      'abs_gt1m_frac':round(float((np.abs(d)>1).mean()),3) if d.size else None,
      'bldg_frac':round(float(p['any_bldg'][unc].mean()),3),'road_frac':round(float(p['roads'][unc].mean()),3),
      'walk_frac':round(float(p['walks'][unc].mean()),3),'wood_frac':round(float(p['wood'][unc].mean()),3)}
print(json.dumps(out,indent=1)); json.dump(out,open('data/wr/day12_band_tiles.json','w'),indent=1)
