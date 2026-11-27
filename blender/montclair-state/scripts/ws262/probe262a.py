# ws262 probe (subset CHAIN, terrain GN on, crop259, exits before render): W66 hairline E of the WS115 walk. Per 0.1 m cell in
# x -230..-212, y -224..-198: z of the FIRST WS113 hit and FIRST Terrain_LiDAR_DTM_1m hit (rays continue through both), plus the top
# non-tree object -> eval262a.json. Tells where the WS113 fan fill is redundant (terrain right under it).
import bpy, json, os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
X0,Y0,R,NX,NY=-230.0,-224.0,0.1,180,260; out={}
for j in range(NY):
    for i in range(NX):
        o0=Vector((X0+(i+0.5)*R,Y0+(j+0.5)*R,200)); top=None; w=None; t=None
        for k in range(80):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            nm=r[4].name
            if top is None and not nm.startswith(('T_','TREE','MID_canopy')): top=(nm[:50],round(r[1].z,3))
            if w is None and nm.startswith('WS113_terrain_fan_fill'): w=round(r[1].z,3)
            if t is None and nm.startswith('Terrain_LiDAR_DTM_1m'): t=round(r[1].z,3)
            if (w is not None and t is not None) or r[1].z<110: break
            o0=r[1]+Vector((0,0,-0.0005))
        out['%d,%d'%(i,j)]=(top,w,t)
json.dump({'X0':X0,'Y0':Y0,'R':R,'NX':NX,'NY':NY,'c':out},open(os.environ.get('PJ','/workspace/nj-scenes/montclair-state/scripts/ws262/eval262a.json'),'w'))
print('P262A done',flush=True)
raise SystemExit
