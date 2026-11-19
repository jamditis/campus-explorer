# Q6 check: paving/walk vertices in the W53 area vs the corrected evaluated terrain (+ seam backing)
import bpy, sys, os, collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for m in t.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh()
B=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
import re
R=re.compile('road|walk|footpath|path|asphalt|paver|sidewalk|plaza|lot|drive|curb',re.I)
res=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or not R.search(o.name): continue
    M=o.matrix_world; c=collections.Counter(); n=0; worst=0; ds=[]
    for v in o.data.vertices:
        w=M@v.co
        if not (100<w.x<249 and -60<w.y<249): continue
        h=B.ray_cast(Vector((w.x,w.y,w.z+30)),Vector((0,0,-1)))
        if h[0] is None: continue
        d=w.z-h[0].z; n+=1; ds.append(d)
        if d>0.3: c['float>0.3']+=1; worst=max(worst,d)
        elif d<-0.05: c['under']+=1
    if n: ds.sort(); res.append((o.name[:50],len(o.modifiers),n,dict(c),round(worst,2),'median',round(ds[len(ds)//2],2),'min',round(ds[0],2)))
for r in sorted(res,key=lambda r:-r[3].get('float>0.3',0))[:20]: print('P226O',r,flush=True)
sys.stdout.flush(); os._exit(0)
