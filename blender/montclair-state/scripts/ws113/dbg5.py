import bpy, numpy as np
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
co=np.array([v.co[:] for v in me.vertices]); E=np.array([e.vertices[:] for e in me.edges])
L=np.linalg.norm(co[E[:,0],:2]-co[E[:,1],:2],axis=1)
print('P113 ORIG edges',len(E),'>8m',int((L>8).sum()),'max %.1f'%L.max())
d=np.linalg.norm(co[:,:2]-np.array([-245.09,-248.11]),axis=1); i=int(d.argmin()); print('P113 nearest orig vert',i,co[i],'d %.3f'%d[i])
long=E[L>8]
if len(long):
    u,c=np.unique(long,return_counts=True); top=u[np.argsort(-c)][:5]; print('P113 hub verts',[(int(k),int(c[list(u).index(k)]),co[k].round(2).tolist()) for k in top])
dg=bpy.context.evaluated_depsgraph_get(); em=t.evaluated_get(dg).data
co2=np.empty(len(em.vertices)*3); em.vertices.foreach_get('co',co2); co2=co2.reshape(-1,3)
E2=np.empty(len(em.edges)*2,dtype=np.int64); em.edges.foreach_get('vertices',E2); E2=E2.reshape(-1,2)
L2=np.linalg.norm(co2[E2[:,0],:2]-co2[E2[:,1],:2],axis=1)
print('P113 EVAL edges >8m',int((L2>8).sum()),'max %.1f'%L2.max())
long=E2[L2>8]; u,c=np.unique(long,return_counts=True); o=np.argsort(-c)[:6]; print('P113 eval hubs',[(int(u[k]),int(c[k]),co2[u[k]].round(2).tolist()) for k in o])
