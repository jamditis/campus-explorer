# ws266 probe (merge208 CHAIN, NO SAVE): W68 thin dark slit, Chapin W stair landing slab <-> plaza paving (seen in the ws264
# close-up, cam -209.5,-208.5,124.6 -> -216,-202,122.9). 5 cm ray grid on the EVALUATED scene (modifiers on only for meshes
# meeting the box); records the top object + z, and the next object under it. Output eval266b.json.
import bpy, json, collections, os, numpy as np
from mathutils import Vector
TAG='P266B'; BX=(-224.0,-212.0,-208.0,-196.0)
def meets(o,m=1):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    return not (max(v.x for v in bb)<BX[0]-m or min(v.x for v in bb)>BX[1]+m or max(v.y for v in bb)<BX[2]-m or min(v.y for v in bb)>BX[3]+m)
on=[]
for o in bpy.data.objects:
    if o.type=='MESH' and meets(o) and not o.name.startswith(('BD_farfield','Context_skirt')) and max(o.dimensions.x,o.dimensions.y)<900:
        for m in o.modifiers:
            if not m.show_viewport: m.show_viewport=True; on.append((o,m))
print(TAG,'mods on',len(on),[o.name[:40] for o,_ in on][:30],flush=True)
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
S=0.05; res=[]
for y in np.arange(BX[2],BX[3],S):
    for x in np.arange(BX[0],BX[1],S):
        o0=Vector((x,y,200)); hits=[]
        for k in range(30):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            ob=r[4]
            if not (ob.name.startswith(('T_','TREE','MID_canopy','gd_grass')) or ob.hide_render):
                hits.append((ob.name[:60],round(r[1].z,3),round(r[2].z,3)))
                if len(hits)==2: break
            o0=r[1]+Vector((0,0,-0.0005))
        res.append((round(float(x),3),round(float(y),3),hits))
json.dump(res,open('/workspace/nj-scenes/montclair-state/scripts/ws266/eval266b.json','w'))
print(TAG,'n',len(res),'tops',collections.Counter(r[2][0][0] if r[2] else None for r in res).most_common(25),flush=True)
for o,m in on: m.show_viewport=False
os._exit(0)
