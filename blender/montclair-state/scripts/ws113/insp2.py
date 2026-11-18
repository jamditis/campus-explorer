import bpy, numpy as np
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
print('P113 mats',[m.name if m else None for m in me.materials])
a=me.attributes['ortho']; print('P113 ortho',a.data_type,a.domain)
n=len(a.data); 
if a.domain=='CORNER':
    vi=np.array([l.vertex_index for l in me.loops])
else: vi=np.arange(n)
dim=2 if a.data_type in('FLOAT2',) else 3
val=np.array([d.vector[:] for d in a.data]) if hasattr(a.data[0],'vector') else np.array([d.value for d in a.data])
co=np.array([v.co[:] for v in me.vertices])[vi]
A=np.c_[co[:,0],co[:,1],np.ones(len(co))]
for k in range(val.shape[1] if val.ndim>1 else 1):
    y=val[:,k] if val.ndim>1 else val
    c,res,_,_=np.linalg.lstsq(A,y,rcond=None); print('P113 fit',k,c.tolist(),'rms',float(np.sqrt(np.mean((A@c-y)**2))))
mi=np.array([p.material_index for p in me.polygons]); print('P113 matidx counts',np.bincount(mi).tolist())
for nm in ('bs_orig_mat',):
    b=me.attributes[nm]; print('P113',nm,b.data_type,b.domain)
