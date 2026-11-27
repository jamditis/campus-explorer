# ws263 probe (subset CHAIN on ws263c, terrain GN on, crop259, exits before render): top non-tree object per 0.05 m cell near the W66 eye camera after the whole-strip skin (a solid dark diagonal line replaced the dots).
# near the ws262 eye-from-N camera (faint dotted marks). Top non-tree object per 0.05 m cell in x -224..-218, y -214..-204.
import bpy, json, collections
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
X0,Y0,R,NX,NY=-224.0,-214.0,0.05,120,200; top={}
for j in range(NY):
    for i in range(NX):
        o0=Vector((X0+(i+0.5)*R,Y0+(j+0.5)*R,200)); t=None
        for k in range(60):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            nm=r[4].name
            if not nm.startswith(('T_','TREE','MID_canopy')): t=(nm[:50],round(r[1].z,3)); break
            o0=r[1]+Vector((0,0,-0.001))
        top['%d,%d'%(i,j)]=t
json.dump({'X0':X0,'Y0':Y0,'R':R,'NX':NX,'NY':NY,'top':top},open('/workspace/nj-scenes/montclair-state/scripts/ws263/eval263g.json','w'))
print('P263G',collections.Counter((v[0][:40] if v else None) for v in top.values()).most_common(8),flush=True)
raise SystemExit
