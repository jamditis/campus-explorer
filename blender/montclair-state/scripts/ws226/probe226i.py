import bpy, sys, os, collections
import numpy as np
for me in bpy.data.meshes:
    if not me.name.startswith('Tree_') or me.users==0: continue
    co=np.array([v.co[:] for v in me.vertices]);
    if len(co)==0: continue
    z=co[:,2]; zs=np.unique(np.round(z,2))[:6]
    rings=[]
    for zz in zs:
        m=np.abs(z-zz)<0.02; r=np.hypot(co[m,0]-co[m,0].mean(),co[m,1]-co[m,1].mean()).max(); rings.append((float(zz),int(m.sum()),round(float(r),2)))
    print('P226I %-38s users %3d zmin %.2f zmax %.1f'%(me.name[:38],me.users,z.min(),z.max()),rings[:4],flush=True)
sys.stdout.flush(); os._exit(0)
