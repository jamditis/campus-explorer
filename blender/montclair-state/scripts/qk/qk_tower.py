import bpy, numpy as np
dg=bpy.context.evaluated_depsgraph_get()
t=np.array([0.4,0.92]); n=np.array([0.92,-0.4])
cam=bpy.data.objects['QE_CAM_eye_ccis_east']; print('CAM',tuple(round(c,1) for c in cam.matrix_world.translation))
for nm in ('QF_CCIS_stucco_skin_recessed_openings_photo','Center for Computing and Information Science roof (LiDAR)','Center for Computing and Information Science walls'):
    o=bpy.data.objects[nm]; e=o.evaluated_get(dg); me=e.to_mesh(); W=np.array(o.matrix_world)
    V=np.array([v.co[:] for v in me.vertices]); V=V@W[:3,:3].T+W[:3,3]
    s=(V[:,0]>30)&(V[:,0]<44)&(V[:,1]>212)&(V[:,1]<232); V=V[s]
    print(nm,len(V))
    for z0 in range(138,158,2):
        b=V[(V[:,2]>=z0)&(V[:,2]<z0+2)]
        if len(b)==0: continue
        T=b[:,:2]@t; Nn=b[:,:2]@n
        print('  z',z0,'t %.2f..%.2f'%(T.min(),T.max()),'n %.2f..%.2f'%(Nn.min(),Nn.max()),len(b))
    e.to_mesh_clear()
