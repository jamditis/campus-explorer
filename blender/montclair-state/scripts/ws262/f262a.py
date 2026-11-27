# ws262 W66 (merge208 CHAIN): the faint hairline on the lawn E of the WS115 walk is where a 2-3 m diagonal band of
# Terrain_LiDAR_DTM_1m shows through a hole in the WS113 fan fill (eval262a: 986 WS113|Terrain neighbour pairs, 214 > 1.5 cm,
# max 5 cm). Lay one smooth 0.1 m lawn skin over the band + 0.6 m (skin262a.json from prep262a.py: clamp-smoothed visible lawn
# z, never under either old surface, edge back on WS113, +4 mm), same lawn material as the WS113 face under its centre, smooth
# shading. The old surfaces stay underneath (no deletions).
import bpy, json
from mathutils import Vector
TAG='F262A'; SN='WS262_W66_lawn_skin_over_WS113_terrain_band'
if SN in bpy.data.objects: raise SystemExit('F262A already')
d=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws262/skin262a.json'))
me=bpy.data.meshes.new(SN); me.from_pydata([tuple(v) for v in d['v']],[],[tuple(f) for f in d['f']])
me.shade_smooth()
src=[x for x in bpy.data.objects if x.name.startswith('WS113_terrain_fan_fill_DTM1m')][0]
W=src.matrix_world; import numpy as np; V=np.array(d['v']); c=Vector((V[:,0].mean(),V[:,1].mean(),0))
best=min(src.data.polygons,key=lambda p:((W@p.center).xy-c.xy).length); mat=src.data.materials[best.material_index]
if mat.name=='Ground_ortho_grass': mat=bpy.data.materials.get('COLE_lawn_post2020_bs') or mat
me.materials.append(mat)
ob=bpy.data.objects.new(SN,me); src.users_collection[0].objects.link(ob)
print(TAG,'made',SN,'v',len(me.vertices),'f',len(me.polygons),'mat',mat.name,'coll',src.users_collection[0].name,flush=True)
