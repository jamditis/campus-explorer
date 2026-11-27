# ws263 probe (subset CHAIN, police views, exits before render): which object/material is the visible ground under the police-lawn grass close-up
import bpy, collections
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene; c=collections.Counter()
for j in range(31):
    for i in range(31):
        o0=Vector((-345+i*0.5,0+j*0.5,200))
        for k in range(40):
            r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
            if not r[0]: break
            nm=r[4].name
            if not nm.startswith(('T_','TREE','MID_canopy','gd_grass')):
                ob=r[4]; mi=r[3]
                try: mat=ob.data.polygons[mi].material_index; mn=ob.material_slots[mat].material.name if ob.material_slots else None
                except Exception as e: mn='?'
                c[(nm[:45],mn)]+=1; break
            o0=r[1]+Vector((0,0,-0.001))
print('P263P',c.most_common(12),flush=True)
m=bpy.data.materials.get('WS68_Ground_ortho_grass_north2020'); print('P263P mat has W263',m and 'W263_soil_mix' in m.node_tree.nodes,flush=True)
for n in (m.node_tree.nodes if m else []):
    if n.name.startswith('WR_litter'): print('P263P litter node',n.name,n.type,[ (i.name,i.is_linked, getattr(i,'default_value',None) if not hasattr(i.default_value,'__len__') else tuple(i.default_value)) for i in n.inputs][:4],flush=True)
raise SystemExit
