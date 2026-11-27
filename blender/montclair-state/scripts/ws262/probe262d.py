# ws262 M2c probe (merge208 CHAIN, NO SAVE): police lawn x -352..-326, y -5..33. Re-enable modifiers ONLY on meshes whose bbox meets
# the lawn box (+2 m), ray-cast the north grass points on main's evaluated scene (skip trees, hidden-render objects), report tops,
# then put the Realtime bits back off. Output eval262d.json [(x,y,z_north,top,z_top)].
import bpy, json, collections, os
from mathutils import Vector
TAG='P262D'; NF='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
BX=(-354,-324,-7,35)
def meets(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    return not (max(v.x for v in bb)<BX[0] or min(v.x for v in bb)>BX[1] or max(v.y for v in bb)<BX[2] or min(v.y for v in bb)>BX[3])
on=[]
for o in bpy.data.objects:
    if o.type=='MESH' and meets(o):
        for m in o.modifiers:
            if (o.name,m.name) in set(_OFF) or True:
                if not m.show_viewport: m.show_viewport=True; on.append((o,m))
loc=[o for o in bpy.data.objects if o.type=='MESH' and meets(o) and not o.hide_render and not o.name.startswith(('T_','TREE','Context_'))]
print(TAG,'meshes in box',len(loc),'mods on',len(on),sorted(set(o.name[:50] for o,m in on))[:30],flush=True)
for o in loc[:200]: print(TAG,'OBJ',o.name[:70],len(o.data.vertices),[m.name for m in o.modifiers][:4],flush=True)
with bpy.data.libraries.load(NF,link=False) as (src,dst): dst.objects=['gd_grass_police_lawn_points']
g=dst.objects[0]; W=g.matrix_world; P=[W@v.co for v in g.data.vertices]
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene; res=[]
for p in P:
    o0=Vector((p.x,p.y,p.z+25)); hit=None
    for k in range(40):
        r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
        if not r[0]: break
        nm=r[4].name
        if not (nm.startswith(('T_','TREE','MID_canopy')) or r[4].hide_render): hit=(nm[:60],round(r[1].z,3)); break
        o0=r[1]+Vector((0,0,-0.0005))
    res.append((round(p.x,3),round(p.y,3),round(p.z,3))+(hit if hit else (None,None)))
json.dump(res,open('/workspace/nj-scenes/montclair-state/scripts/ws262/eval262d.json','w'))
print(TAG,'tops',collections.Counter(r[3] for r in res).most_common(25),flush=True)
for o,m in on: m.show_viewport=False
os._exit(0)
