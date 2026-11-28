# ws273 probe F (NO SAVE): Terrain 'ortho' UV — base-mesh linear fit vs position, and evaluated UVs on the regrid faces in the lot pocket.
import bpy, os, numpy as np
TAG='P273F'
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; mw=T.matrix_world; uv=me.uv_layers['ortho'].data
X=[];U=[]
for p in me.polygons:
    c=mw@p.center
    if -300<c.x<-180 and -160<c.y<-60:
        for li in p.loop_indices:
            v=mw@me.vertices[me.loops[li].vertex_index].co; X.append((v.x,v.y,1)); U.append(tuple(uv[li].uv))
X=np.array(X);U=np.array(U); co,res,_,_=np.linalg.lstsq(X,U,rcond=None); err=np.abs(X@co-U).max(axis=0)
print(TAG,'fit u=a x+b y+c',co[:,0].tolist(),'v',co[:,1].tolist(),'maxerr',err.tolist(),'n',len(X),flush=True)
for m in T.modifiers: m.show_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); oe=T.evaluated_get(dg); em=oe.to_mesh()
print(TAG,'eval uv layers',[u.name for u in em.uv_layers],flush=True)
if 'ortho' in em.uv_layers:
    ed=em.uv_layers['ortho'].data; S=[]
    for p in em.polygons:
        c=mw@p.center
        if -249<c.x<-236 and -113<c.y<-101:
            li=p.loop_indices[0]; v=mw@em.vertices[em.loops[li].vertex_index].co
            S.append((round(v.x,2),round(v.y,2),tuple(round(a,5) for a in ed[li].uv),tuple(round(a,5) for a in (np.array([v.x,v.y,1])@co))))
    print(TAG,'n',len(S),'samples',S[:3],S[len(S)//2:len(S)//2+2],S[-2:],flush=True)
oe.to_mesh_clear(); os._exit(0)
