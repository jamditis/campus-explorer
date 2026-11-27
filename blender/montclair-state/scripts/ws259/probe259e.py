# ws259 probe (merge208 CHAIN, base meshes, exits without saving): every object hit (base mesh) beside the WS103 walk W edge
import bpy, json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
B=set(json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws205/bbox205.json')).keys())
for (x,y) in ((-251.9,-238),(-250.6,-234),(-249.3,-230),(-247.8,-226),(-246.5,-222),(-245.0,-218),(-243.7,-214)):
    o0=Vector((x,y,200)); hits=[]
    for k in range(8):
        r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
        if not r[0]: break
        hits.append('%s%s(hr%d)@%.2f'%(r[4].name[:50],'' if r[4].name in B else '[NEW]',r[4].hide_render,r[1].z)); o0=r[1]+Vector((0,0,-0.001))
    print('P259E',x,y,hits,flush=True)
raise SystemExit
