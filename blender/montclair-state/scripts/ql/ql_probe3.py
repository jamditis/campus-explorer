import bpy, numpy as np
dg=bpy.context.evaluated_depsgraph_get()
for n,zmin in [('Center for Computing and Information Science roof (LiDAR)',150),('Center for Computing and Information Science walls',150),('QF_CCIS_stucco_skin_recessed_openings_photo',150)]:
    o=bpy.data.objects[n]; me=o.evaluated_get(dg).data; M=np.array(o.matrix_world)
    v=np.array([tuple(x.co) for x in me.vertices]); v=(np.c_[v,np.ones(len(v))]@M.T)[:,:3]
    v=v[v[:,2]>zmin]; t=0.4*v[:,0]+0.92*v[:,1]; nn=0.92*v[:,0]-0.4*v[:,1]
    print('OBJ',n)
    for b in range(190,248,2):
        s=(t>=b)&(t<b+2)
        if s.any(): print('  t',b,'max n',nn[s].max().round(2),'z@max',v[s][np.argmax(nn[s]),2].round(1),'cnt',s.sum())
