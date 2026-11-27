# ws259 probe (FULL main, all modifiers as saved, no save): evaluated ground beside the WS103 walk W edge (UNIFY W64)
import bpy, resource
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
print('P259G loaded, VmHWM MB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024, flush=True)
for (y,xe) in ((-238,-251.62),(-234,-250.29),(-230,-248.96),(-226,-247.47),(-222,-246.15),(-218,-244.65)):
    for dx in (0.35,1.5,3.0,6.0):
        o0=Vector((xe-dx,y,200)); hits=[]
        for k in range(5):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            if not r[4].name.startswith(('T_','TREE')) or k>3: hits.append('%s@%.2f'%(r[4].name[:40],r[1].z))
            o0=r[1]+Vector((0,0,-0.001))
            if len(hits)>=2: break
        print('P259G y',y,'dx',dx,hits,flush=True)
print('P259G VmHWM MB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024, flush=True)
