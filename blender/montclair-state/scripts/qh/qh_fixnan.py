# qh: qg's patch had 211 NaN vertices on its east column (x=221, grid has only 820 cols -> empty mean). NaN breaks BVH
# ray casts (terrain probes missed ~96% of rays). Fix: z of each NaN vert = mean of finite neighbours in x (x-1). Indices kept
# in mesh['qh_nan_idx'] so REVERT=1 restores the exact pre-qh (NaN) state.
import bpy, os, numpy as np
P=bpy.data.objects['QG_north_strip_LiDAR_terrain_patch']; me=P.data
co=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
if os.environ.get('REVERT')=='1':
    if 'qh_nan_idx' in me:
        for i in me['qh_nan_idx']: me.vertices[i].co.z=float('nan')
        del me['qh_nan_idx']; me.update(); print('QH nan restored')
else:
    bad=np.where(~np.isfinite(co[:,2]))[0]
    if len(bad):
        good=np.isfinite(co[:,2]); key={(round(x),round(y)):z for (x,y,z) in co[good]}
        for i in bad:
            x,y=round(co[i,0]),round(co[i,1]); z=None
            for dx in (1,2,3):
                z=key.get((x-dx,y));
                if z is not None: break
            me.vertices[int(i)].co.z=float(z) if z is not None else float(np.nanmedian(co[:,2]))
        me['qh_nan_idx']=[int(i) for i in bad]; me.update()
    print('QH nanfix',len(bad))
