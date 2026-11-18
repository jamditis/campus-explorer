import bpy,numpy as np
from mathutils import Vector
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for m in T.modifiers:
    info=[m.name,m.type,m.show_render]
    if m.type=='NODES':
        info.append(m.node_group.name if m.node_group else None)
        for k in m.keys():
            v=m[k]; 
            if isinstance(v,bpy.types.ID): info.append((k,v.name))
    for a in ('object','target','texture'):
        if hasattr(m,a) and getattr(m,a): info.append((a,getattr(m,a).name))
    print('Q102',info)
me=T.data; co=np.array([v.co for v in me.vertices]); M=np.array(T.matrix_world); W=co@M[:3,:3].T+M[:3,3]
m=(W[:,0]>-250)&(W[:,0]<-235)&(W[:,1]>-240)&(W[:,1]<-225); print('Q102 base verts in s70-85 box',m.sum(), W[m][:6].round(2).tolist())
dg=bpy.context.evaluated_depsgraph_get(); e=T.evaluated_get(dg); em=e.to_mesh(); ec=np.array([v.co for v in em.vertices]); EW_=ec@M[:3,:3].T+M[:3,3]
m2=(EW_[:,0]>-250)&(EW_[:,0]<-235)&(EW_[:,1]>-240)&(EW_[:,1]<-225); print('Q102 eval verts',m2.sum(),EW_[m2][:6].round(2).tolist(),'total base',len(W),'eval',len(EW_))
