# pm (session pm, Nov 1 2026). ALL UNVERIFIED, removable; REVERT=1 undoes (mesh swap back).
# Feliciano LiDAR roof: the sloped tile band read as lumpy 'curtains'. Each interior tile vertex is re-set onto a ruled
# slope between its nearest lower anchor (eave / lower flat deck) and nearest higher anchor (upper flat deck), k-NN averaged,
# so the tile reads as straight-sloped planes. Anchors (flat/boundary verts) unmoved -> no cracks. Mesh swap: old mesh kept (fake user).
import bpy, os, sys, numpy as np
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv; OUT=os.environ.get('SAVEAS')
R='Feliciano School of Business roof (LiDAR)'; PR='pm_prev_mesh'
r=bpy.data.objects[R]
if PR in r.keys():
    old=bpy.data.meshes[r[PR]]; new=r.data; r.data=old; old.use_fake_user=False; del r[PR]
    if new.users==0: bpy.data.meshes.remove(new)
    print('REVERTED_PM_ROOF')
if not REV:
    K=int(os.environ.get('K','4')); DZ=float(os.environ.get('DZ','0.6')); MAXW=float(os.environ.get('MAXW','14'))
    old=r.data; m=old.copy(); m.name=old.name+'_pm_planar_UNVERIFIED'; old.use_fake_user=True
    n=len(m.vertices); co=np.zeros(n*3); m.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    mi=np.zeros(len(m.polygons),dtype=int); m.polygons.foreach_get('material_index',mi)
    tile_any=np.zeros(n,bool); other=np.zeros(n,bool)
    for p in m.polygons:
        vs=list(p.vertices)
        if mi[p.index]==4: tile_any[vs]=True
        else: other[vs]=True
    # boundary verts
    from collections import Counter
    ec=Counter()
    for p in m.polygons:
        for e in p.edge_keys: ec[e]+=1
    bnd=np.zeros(n,bool)
    for e,c in ec.items():
        if c==1: bnd[list(e)]=True
    T=np.where(tile_any & ~other & ~bnd)[0]; A=np.where(other | bnd)[0]
    xy=co[:,:2]; z=co[:,2]
    newz=z.copy(); moved=0; skipped=0
    for v in T:
        d=np.hypot(*(xy[A]-xy[v]).T)
        lo=A[z[A]<z[v]-DZ]; hi=A[z[A]>z[v]+DZ]
        if len(lo)==0 or len(hi)==0: skipped+=1; continue
        dl=d[np.searchsorted(A,lo)]; dh=d[np.searchsorted(A,hi)]
        il=np.argsort(dl)[:K]; ih=np.argsort(dh)[:K]
        a=dl[il].mean(); b=dh[ih].mean()
        if a+b>MAXW: skipped+=1; continue
        zl=z[lo[il]].mean(); zh=z[hi[ih]].mean()
        newz[v]=zl+(zh-zl)*a/(a+b); moved+=1
    dzv=np.abs(newz-z)
    co[:,2]=newz; m.vertices.foreach_set('co',co.ravel()); m.update()
    r[PR]=old.name; r.data=m
    r['UNVERIFIED_pm_planar']='tile band verts re-set on ruled slopes between nearest lower/upper flat anchors (K=%d, DZ=%.2f); style fix, no survey'%(K,DZ)
    print('PM_ROOF tileverts',len(T),'anchors',len(A),'moved',moved,'skipped',skipped,'mean|dz|',dzv[T].mean(),'max',dzv.max())
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED_AS',OUT)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
