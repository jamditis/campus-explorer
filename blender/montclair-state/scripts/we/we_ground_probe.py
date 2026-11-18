import bpy, json
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def top(x,y):
    o=Vector((x,y,300)); hits=[]
    for i in range(12):
        r=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not r[0]: break
        hits.append((round(r[1].z,2),r[4].name))
        o=r[1]-Vector((0,0,0.01))
        if not r[4].name.startswith('TL_tree') and len(hits)>0 and not r[4].name.startswith(('TL_','Grass')): pass
    return hits
res={}
for n in ['TL_tree_095_UNVERIFIED','TL_tree_096_UNVERIFIED','TL_tree_099_UNVERIFIED','TL_tree_100_UNVERIFIED','TL_tree_101_UNVERIFIED','TL_tree_104_UNVERIFIED','TL_tree_107_UNVERIFIED']:
    p=bpy.data.objects[n].matrix_world.translation
    res[n]=[h for h in top(p.x,p.y) if not h[1].startswith('TL_tree')][:5]
for k,v in res.items(): print(k,v)
json.dump(res,open('data/we/ground_probe.json','w'),indent=1)
