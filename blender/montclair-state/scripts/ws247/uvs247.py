# ws247: UV stretch on Terrain_LiDAR_DTM_1m over the east bank: per face, ortho-UV span (m) vs xy span (m), and texel paleness
import bpy, os, numpy as np
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; bpy.context.scene.collection.objects.link(T); me=T.data; M=T.matrix_world; uvl=me.uv_layers['ortho'].data
BX=[float(v) for v in os.environ.get('BOX','-250,-195,90,180').split(',')]
vin=np.array([BX[0]<(M@v.co).x<BX[1] and BX[2]<(M@v.co).y<BX[3] for v in me.vertices])
# affine xy->uv from loops in box using the unmodified majority: robust fit via median of per-loop residual
P=[];U=[];L=[]
for p in me.polygons:
    if not vin[p.vertices[0]]: continue
    for li in p.loop_indices:
        v=me.vertices[me.loops[li].vertex_index]; w=M@v.co; P.append((w.x,w.y)); U.append(tuple(uvl[li].uv)); L.append(li)
P=np.array(P);U=np.array(U);X=np.c_[P,np.ones(len(P))]
A=np.linalg.lstsq(X,U,rcond=None)[0]
for it in range(3):
    r=np.abs(X@A-U).sum(1); k=r<np.percentile(r,80); A=np.linalg.lstsq(X[k],U[k],rcond=None)[0]
Ainv=np.linalg.pinv(A[:2])  # uv delta -> xy delta
res=np.linalg.norm(((U-(X@A)))@Ainv,axis=1)   # metres the loop's UV is displaced from its own xy
print('U247 loops',len(L),'displaced>0.5m',int((res>0.5).sum()),'max',round(float(res.max()),1),flush=True)
# faces: max displacement difference between corners (stretch)
bad=[]
for p in me.polygons:
    if not vin[p.vertices[0]]: continue
    d=[]; 
    for li in p.loop_indices:
        w=M@me.vertices[me.loops[li].vertex_index].co; u=np.array(uvl[li].uv); d.append((u-np.array([w.x,w.y,1])@A)@Ainv)
    d=np.array(d); s=float(np.linalg.norm(d.max(0)-d.min(0)))
    if s>1.0: c=M@p.center; bad.append((round(s,1),round(c.x,1),round(c.y,1),round(c.z,2)))
bad.sort(reverse=True)
print('U247 faces with corner-displacement spread >1 m',len(bad),flush=True)
import collections
print('U247 spread hist',collections.Counter(int(min(s,20)//2*2) for s,*_ in bad),flush=True)
for x in bad[:25]: print('U247 f',x,flush=True)
os._exit(0)
