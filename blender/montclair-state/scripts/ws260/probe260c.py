# ws260 probe (subset CHAIN, terrain GN on, crop259, exits before render): EVALUATED top surface per 0.5 m cell, x -266..-242, y -239..-204
# (ws260a: patch joined). Cells with no hit (or only Context_ground_beyond_data / skirt) = remaining holes -> eval260c.json
import bpy, json
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
X0,Y0,R,NX,NY=-266.0,-239.0,0.5,48,86; out={}
for j in range(NY):
    for i in range(NX):
        o0=Vector((X0+(i+0.5)*R,Y0+(j+0.5)*R,200)); top=None
        for k in range(60):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            n=r[4].name
            if n.startswith('Context_'): break
            if not n.startswith(('T_','TREE','MID_canopy')): top=(n,round(r[1].z,3)); break
            o0=r[1]+Vector((0,0,-0.001))
        out['%d,%d'%(i,j)]=top
json.dump({'X0':X0,'Y0':Y0,'R':R,'NX':NX,'NY':NY,'top':out},open('/workspace/nj-scenes/montclair-state/scripts/ws260/eval260c.json','w'))
print('P260C holes',sum(1 for v in out.values() if v is None),flush=True)
raise SystemExit
