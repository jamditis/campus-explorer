import bpy, os, numpy as np
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws252f.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; me=T.data; M=T.matrix_world; uvl=me.uv_layers['ortho'].data
img=next(n.image for m in me.materials if m and m.node_tree for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'ortho' in n.image.name.lower())
BX=tuple(float(a) for a in os.environ.get('BX','-200,-174,158,184').split(','))
P=[];U=[]
for p in me.polygons:
    c=M@p.center
    if BX[0]<c.x<BX[1] and BX[2]<c.y<BX[3]:
        for li in p.loop_indices:
            w=M@me.vertices[me.loops[li].vertex_index].co; P.append((w.x,w.y)); U.append(tuple(uvl[li].uv))
P=np.array(P);U=np.array(U);X=np.c_[P,np.ones(len(P))];A=np.linalg.lstsq(X,U,rcond=None)[0]
w,h=img.size; px=np.empty(w*h*4,np.float32); img.pixels.foreach_get(px); px=px.reshape(h,w,4)
S=0.25; xs=np.arange(BX[0],BX[1],S); ys=np.arange(BX[3],BX[2],-S)
out=np.zeros((len(ys),len(xs),3),np.float32)
for j,y in enumerate(ys):
    uv=np.c_[xs,np.full_like(xs,y),np.ones_like(xs)]@A
    ii=np.clip((uv[:,1]*h).astype(int),0,h-1); jj=np.clip((uv[:,0]*w).astype(int),0,w-1); out[j]=px[ii,jj,:3]
np.save('/tmp/crop253.npy',out); print('C253',out.shape,'texel size m',round(1/(np.linalg.norm(A[0])*w),3),flush=True)
os._exit(0)
