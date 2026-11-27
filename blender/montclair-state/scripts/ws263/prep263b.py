# ws263 W66 residual (dotted marks): = ws262/prep262a.py with the skin region widened to the whole lawn component(s) that touch the terrain band (probe262g: 77 single 5 cm cells of WS113 poke through along the ws262 skin W edge, a diagonal 0.1 m staircase mid-lawn in front of the eye camera). Edge now 0.1 m off walks / Chapin / beds and on the axis-aligned eval-box edge.
# ws262 W66: build a smooth 0.1 m lawn skin over the diagonal Terrain_LiDAR_DTM_1m band that runs through the WS113 fan fill
# E of the WS115 walk (eval262a.json). Region = lawn cells (top WS113/Terrain) within 0.6 m of a Terrain-top or WS113-over-terrain
# cell, minus any cell within 0.25 m of a non-lawn top (walks, plaza, Chapin, beds). z = Gaussian-smoothed visible lawn z
# (sigma 0.35 m, lawn cells only), blended back to the raw visible z over the outer 0.3 m so the skin's edge sits on WS113;
# +4 mm. Smoothed field = 40 passes of max(raw, Gaussian 0.15 m) so neither old surface pokes through. Output skin263b.json {v:[...], f:[...]}.
import json, numpy as np
from scipy import ndimage
d=json.load(open('../ws262/eval262a.json')); C=d['c']; NX,NY,X0,Y0,R=d['NX'],d['NY'],d['X0'],d['Y0'],d['R']
Z=np.full((NY,NX),np.nan); lawn=np.zeros((NY,NX),bool); band=np.zeros((NY,NX),bool); other=np.zeros((NY,NX),bool)
for k,(top,w,t) in C.items():
    i,j=map(int,k.split(','))
    if top is None: other[j,i]=True; continue
    n=top[0]
    if n.startswith(('WS113_terrain_fan','Terrain_LiDAR_DTM_1m','WS261_UNIFY32')):
        lawn[j,i]=True; Z[j,i]=top[1]
        if n.startswith('Terrain') or (t is not None and w is not None and w-t<0.06): band[j,i]=True
    else: other[j,i]=True
# drop isolated terrain specks far from the main band: keep the largest band component(s) > 200 cells
lab,nl=ndimage.label(ndimage.binary_dilation(band,iterations=2)); sz=ndimage.sum(np.ones_like(lab),lab,range(1,nl+1))
keep=np.isin(lab,[i+1 for i,s in enumerate(sz) if s>200]); band&=keep
dist_band=ndimage.distance_transform_edt(~band)*R; dist_other=ndimage.distance_transform_edt(~other)*R
reg0=lawn&(dist_other>0.1); labr,nr=ndimage.label(reg0); ids=np.unique(labr[band&reg0]); ids=ids[ids>0]; reg=np.isin(labr,ids)  # ws263: whole lawn component(s) touching the band, so the skin edge lies at the walk/wall feet and the eval-box edge instead of mid-lawn (ws262 W edge staircase = the dotted marks)
# iterated clamp-smoothing: Zs <- max(raw, Gaussian(Zs, 0.15 m)), 40 passes (normalised over lawn cells). Linear slopes stay put,
# steps become ramps from below, nothing ends up under the old surfaces.
raw=np.where(lawn,Z,np.nan); wg=lawn.astype(float); den=np.maximum(ndimage.gaussian_filter(wg,0.15/R),1e-6); Zs=np.where(lawn,Z,0.0)
floor=ndimage.maximum_filter(np.where(lawn,Z,-1e9),size=3); floor=np.where(lawn,floor,np.nan)  # ws262d: >= raw of all 8 neighbours, so the old step edges can't poke up between 0.1 m samples
for it in range(40):
    Zs=ndimage.gaussian_filter(np.where(lawn,Zs,0.0),0.15/R)/den; Zs=np.where(lawn,np.fmax(Zs,floor),0.0)
# blend to raw near region edge
dedge=ndimage.distance_transform_edt(reg)*R
a=np.clip((dedge-0.05)/0.3,0,1); a=a*a*(3-2*a)
Zf=np.maximum(np.minimum(Z*(1-a)+Zs*a,Z+0.07),np.where(a>0.5,floor,Z))+0.004  # lift capped at 7 cm (a few edge cells of the 0.1 m grid)
print('min skin-raw %.4f'%np.nanmin((Zf-Z)[reg]),'max %.3f'%np.nanmax((Zf-Z)[reg]))
print('band cells',band.sum(),'region cells',reg.sum(),'max |smooth-raw| %.3f'%np.nanmax(np.abs((Zf-0.004-Z)[reg])))
idx=-np.ones((NY,NX),int); V=[]
for j in range(NY):
    for i in range(NX):
        if reg[j,i]: idx[j,i]=len(V); V.append((round(X0+(i+.5)*R,3),round(Y0+(j+.5)*R,3),round(float(Zf[j,i]),4)))
F=[]
for j in range(NY-1):
    for i in range(NX-1):
        q=(idx[j,i],idx[j,i+1],idx[j+1,i+1],idx[j+1,i])
        if min(q)>=0: F.append(q)
F=[tuple(int(x) for x in q) for q in F]
used=sorted({x for q in F for x in q}); remap={o:n for n,o in enumerate(used)}
json.dump({'v':[V[u] for u in used],'f':[[remap[x] for x in q] for q in F]},open('skin263b.json','w'))
print('verts',len(used),'faces',len(F))
dd=(Zf-0.004-Z); dd[~reg]=np.nan
print('lift pct',np.nanpercentile(dd,[50,90,99,99.9]).round(3))
jj,ii=np.where(dd>0.05); print('cells >5cm',len(jj), 'x %.1f..%.1f y %.1f..%.1f'%(X0+ii.min()*R,X0+ii.max()*R,Y0+jj.min()*R,Y0+jj.max()*R) if len(jj) else '')
import collections
print(collections.Counter(C['%d,%d'%(i,j)][0][0][:20] for j,i in zip(jj,ii)))
