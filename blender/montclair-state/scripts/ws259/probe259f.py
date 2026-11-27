# ws259 probe (subset CHAIN incl. the 4 km skirt, terrain GN on, exits before render): evaluated ground W of the WS103 walk S half
import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for (x,y,xe) in ((-251.9,-238,-251.62),(-250.6,-234,-250.29),(-249.3,-230,-248.96),(-247.8,-226,-247.47),(-246.5,-222,-246.15)):
    for dx in (0.35,1.5,3.0,6.0):
        o0=Vector((xe-dx,y,200)); hits=[]
        for k in range(4):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            hits.append('%s@%.2f'%(r[4].name[:34],r[1].z)); o0=r[1]+Vector((0,0,-0.001))
        print('P259F y',y,'dx',dx,hits,flush=True)
raise SystemExit
