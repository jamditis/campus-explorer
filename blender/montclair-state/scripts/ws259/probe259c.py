# ws259 probe (subset-render CHAIN, exits before rendering): what surface is on top along the WS103 walk? scene.ray_cast down
import bpy, sys
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
from mathutils import Vector
print('P259C strips in scene', 'WS259_UNIFY6_CollegeAve_S_W_walk_sawcut_1p524m_UNVERIFIED' in sc.objects)
for (x,y) in ((-248.5,-230),(-246.3,-225),(-243.5,-218),(-241,-212),(-239.9,-210)):
    o0=Vector((x,y,200)); hits=[]
    for k in range(4):
        r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
        if not r[0]: break
        hits.append('%s@%.3f'%(r[4].name[:45],r[1].z)); o0=r[1]+Vector((0,0,-0.0005))
    print('P259C',x,y,hits,flush=True)
raise SystemExit
