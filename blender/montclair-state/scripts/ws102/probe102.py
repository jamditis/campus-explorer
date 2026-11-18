import bpy,numpy as np
from mathutils import Vector
src=open('/workspace/nj-scenes/montclair-state/scripts/ws102/apply102.py').read(); exec(src[:src.index('mats={')])
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
road=[o for o in bpy.data.objects if o.name.startswith('WS102_CollegeAve_S_carriageway')][0]
print('P102 road coll',[c.name for c in road.users_collection],'hide_render',road.hide_render,'visible',road.visible_get())
for c in road.users_collection: print('P102 coll hide_render',c.hide_render)
for s in (2,10,20,30,45,60,75,85):
    for off in (-2,0,2):
        p,n=frame(s); q=p+n*off
        hits=[];o=Vector((q[0],q[1],200))
        for _ in range(4):
            r=sc.ray_cast(dg,o,Vector((0,0,-1)))
            if not r[0]: break
            hits.append((r[4].name[:40],round(r[1].z,2))); o=Vector((q[0],q[1],r[1].z-0.005))
        print('P102 s%d o%d zc %.2f'%(s,off,zc(s)),hits)
