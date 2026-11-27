# ws262 probe (subset CHAIN, terrain GN on, crop259, exits before render): M2c gd_grass_police_lawn_points (north file). Load the
# point mesh (not linked to the scene, so its GN never evaluates), ray-cast every point straight down on main's EVALUATED scene
# (skip trees) and record the top object + z -> eval262b.json [(x,y,z_north,top_name,z_top)].
import bpy, json, os, collections
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws259/crop259.py').read())
from mathutils import Vector
NF='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
with bpy.data.libraries.load(NF,link=False) as (src,dst):
    dst.meshes=[n for n in src.meshes if n in ('gd_grass_police_lawn_points',)] or []
    dst.objects=['gd_grass_police_lawn_points']
o=dst.objects[0]; W=o.matrix_world; P=[W@v.co for v in o.data.vertices]
print('P262B pts',len(P),'mesh',o.data.name,flush=True)
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene; res=[]
for p in P:
    o0=Vector((p.x,p.y,p.z+25)); hit=None
    for k in range(40):
        r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
        if not r[0]: break
        nm=r[4].name
        if not nm.startswith(('T_','TREE','MID_canopy')): hit=(nm[:60],round(r[1].z,3)); break
        o0=r[1]+Vector((0,0,-0.0005))
    res.append((round(p.x,3),round(p.y,3),round(p.z,3))+(hit if hit else (None,None)))
json.dump(res,open('/workspace/nj-scenes/montclair-state/scripts/ws262/eval262b.json','w'))
c=collections.Counter(r[3] for r in res); print('P262B tops',c.most_common(20),flush=True)
raise SystemExit
