import bpy
from mathutils import Vector
for n in ['Context_skirt_3DEP_ortho_4km','QW_DTM_north_edge_ramp_UNVERIFIED','RZ2_SC_LiDAR_ground_patch_UNVERIFIED']:
    o=bpy.data.objects[n]; print('OB',n,len(o.data.vertices),len(o.data.polygons),[(m.name,m.type) for m in o.modifiers],o.data.users)
for o in bpy.data.objects:
    if o.type!='MESH' and o.type!='EMPTY': continue
    if o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8
    dx=max(v.x for v in bb)-min(v.x for v in bb)
    if -115<cx<70 and 250<cy<372 and dx<150: print('IN',o.name[:60],o.type,len(o.data.vertices) if o.type=='MESH' else 0,[c.name[:30] for c in o.users_collection][:2],'%.1f %.1f'%(cx,cy))
