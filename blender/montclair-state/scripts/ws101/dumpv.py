import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (s,d): d.objects=['WS73_curb_back_lawn_verge_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_curb_right_UNVERIFIED']
out={}
for o in d.objects:
    me=o.data; n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); out[o.name[:30]]=co@M[:3,:3].T+M[:3,3]; print('DV',o.name,n,[m.type for m in o.modifiers],len(me.polygons))
np.savez('/workspace/nj-scenes/montclair-state/scripts/ws101/dumpv.npz',**out)
