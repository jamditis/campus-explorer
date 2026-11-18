import bpy,numpy as np
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); out={}
for n in ('QX_Richardson_W_ramp_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED','Footpaths_OSM','Roads_OSM','QW_DTM_north_edge_ramp_UNVERIFIED'):
    o=bpy.data.objects.get(n)
    if not o: print('missing',n); continue
    e=o.evaluated_get(dg) if not n.endswith('points_UNVERIFIED') else o
    me=e.to_mesh(); mw=o.matrix_world
    a=np.array([tuple(mw@v.co) for v in me.vertices]); e.to_mesh_clear()
    if len(a): a=a[(a[:,0]>-80)&(a[:,0]<60)&(a[:,1]>220)&(a[:,1]<360)]
    out[n]=a; print(n,len(a))
cam=bpy.data.objects['QX_CAM_closeup_ramp_west_grass']; out['cam']=np.array(cam.location)
np.savez('data/qx/probe.npz',**out)
