# ws261 probe (subset CHAIN, terrain GN on, crop259, exits before render): UNIFY #32 (wider box x -228..-214, y -222..-196) — thin dark crease line on the lawn E of the WS115
# walk (x -230..-216, y -219..-209). Evaluated top object/z per 0.1 m cell -> eval261f.json (holes = Context_* top or no hit).
import bpy, json
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
X0,Y0,R,NX,NY=-228.0,-222.0,0.1,140,260; top={}; nrm={}
for j in range(NY):
    for i in range(NX):
        o0=Vector((X0+(i+0.5)*R,Y0+(j+0.5)*R,200)); t=None
        for k in range(60):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            nm=r[4].name
            if not nm.startswith(('T_','TREE','MID_canopy')): t=(nm[:50],round(r[1].z,3),round(r[2].z,3)); break
            o0=r[1]+Vector((0,0,-0.001))
        top['%d,%d'%(i,j)]=t
json.dump({'X0':X0,'Y0':Y0,'R':R,'NX':NX,'NY':NY,'top':top},open('/workspace/nj-scenes/montclair-state/scripts/ws261/eval261f.json','w'))
for n in ('WS113_terrain_fan_fill','Terrain_LiDAR_DTM_1m','WS115_E_walk_N'):
    for o in bpy.data.objects:
        if o.name.startswith(n): print('CROP259 MODS',o.name[:50],[(m.name,m.type,m.show_render) for m in o.modifiers][:12],len(o.data.vertices),flush=True)
raise SystemExit
