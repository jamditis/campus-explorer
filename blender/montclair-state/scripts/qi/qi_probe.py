import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
sk=[o for o in bpy.data.objects if 'skirt' in o.name.lower()]
print('SKIRTS',[(o.name,o.hide_render,[round(v,1) for v in o.dimensions]) for o in sk])
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; bt=BVHTree.FromObject(T,dg)
bs={o.name:BVHTree.FromObject(o,dg) for o in sk if not o.hide_render and o.type=='MESH'}
for y in (-30,0,50,100,150,200,245):
    row=[]
    for x in (200,219,235,244,246,248,250,253,258,265):
        t=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]; s={k:(round(b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0].z,1) if b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] else None) for k,b in bs.items()}
        row.append((x,None if t is None else round(t.z,1),s))
    print('ROW',y,row)
for n in [o.name for o in bpy.data.objects if o.name.startswith(('Roads','Footpaths','OZ'))][:30]:
    o=bpy.data.objects[n]
    if o.type!='MESH': print('OBJ',n,o.type); continue
    M=o.matrix_world; W=[M@v.co for v in o.data.vertices]; W=[w for w in W if 150<=w.x<=250 and -35<=w.y<=250]
    if not W: continue
    d=[]
    for w in W[::max(1,len(W)//300)]:
        t=bt.ray_cast(Vector((w.x,w.y,400)),Vector((0,0,-1)))[0]
        if t: d.append(w.z-t.z)
    d=np.array(d); print('OBJ',n,len(W),'mods',[m.type for m in o.modifiers],'dz pct',np.round(np.percentile(d,[5,25,50,75,95]),2) if len(d) else None)
