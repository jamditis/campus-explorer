# ws246 W59c: the f242c lattice fill in M3b's DTM no-data gap (x -396..-380, y -52..-21) reads as a paler, flat lawn patch
# next to the north-ortho-toned M3b ground. Cause: the fill's new loops never got a proper 'ortho' UV (they sit on one or a
# few texels). Fix: fit M3b's own planar xy->uv mapping (affine, from loops in a 60 m box OUTSIDE the gap) and give every
# loop in the gap box whose UV is off that mapping by > 3 texels its true ortho position, so the patch shows the real 2020
# north imagery there like its neighbours. Geometry and materials unchanged. DRY=1 reports only.
import bpy, numpy as np, os
o=next(x for x in bpy.data.objects if x.name.startswith('M3b_north_LiDAR_DTM_1m')); me=o.data; M=o.matrix_world
uvl=me.uv_layers['ortho'].data
X0,X1,Y0,Y1=-397,-379,-53,-20
co=np.array([tuple(M@v.co)[:2] for v in me.vertices])
lv=np.empty(len(me.loops),np.int64); me.loops.foreach_get('vertex_index',lv)
uv=np.empty(len(me.loops)*2,np.float32); uvl.foreach_get('uv',uv); uv=uv.reshape(-1,2)
P=co[lv]; ing=(P[:,0]>X0)&(P[:,0]<X1)&(P[:,1]>Y0)&(P[:,1]<Y1)
near=(P[:,0]>X0-30)&(P[:,0]<X1+30)&(P[:,1]>Y0-30)&(P[:,1]<Y1+30)&~ing
X=np.c_[P[near],np.ones(near.sum())]; A=np.linalg.lstsq(X,uv[near],rcond=None)[0]
img=None
for m in me.materials:
    if m and m.node_tree:
        for n in m.node_tree.nodes:
            if n.type=='TEX_IMAGE' and n.image: img=img or n.image
W=img.size[0] if img else 4096
res=np.abs(X@A-uv[near]).max(1)*W
print('F246C fit loops',int(near.sum()),'residual texels p50/p95/max',np.percentile(res,50).round(2),np.percentile(res,95).round(2),res.max().round(2),'image',img and img.name,img and img.size[:],flush=True)
pred=np.c_[P[ing],np.ones(ing.sum())]@A
off=np.abs(pred-uv[ing]).max(1)*W
bad=off>3
print('F246C gap loops',int(ing.sum()),'off-mapping >3 texels',int(bad.sum()),'p50 off',np.percentile(off,50).round(1) if len(off) else None,flush=True)
if os.environ.get('DRY')!='1' and bad.any():
    idx=np.where(ing)[0][bad]; uv[idx]=pred[bad]; uvl.foreach_set('uv',uv.ravel()); me.update(); print('F246C loops set',len(idx),flush=True)
