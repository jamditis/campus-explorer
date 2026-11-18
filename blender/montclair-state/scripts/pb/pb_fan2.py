import bpy, numpy as np
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data
co=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
for p in me.polygons:
    vs=co[list(p.vertices)]; e=np.linalg.norm(vs-np.roll(vs,1,0),axis=1)
    if e.mean()>2 and vs[:,0].max()>60 and vs[:,0].min()<220 and vs[:,1].max()>110 and vs[:,1].min()<280:
        print('PBF',p.index,np.round(vs,1).tolist(),round(p.area,1))
