import bpy, bmesh, collections, statistics
from mathutils import Vector
from mathutils.bvhtree import BVHTree
fp=bpy.data.objects['Footpaths_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
dg=bpy.context.evaluated_depsgraph_get(); te=ter.evaluated_get(dg); bt=bmesh.new(); bt.from_mesh(te.to_mesh()); bt.transform(ter.matrix_world); tree=BVHTree.FromBMesh(bt)
fe=fp.evaluated_get(dg); me=fe.to_mesh(); print('eval verts',len(me.vertices),'faces',len(me.polygons))
U=[]; C=Vector((10.6,141.1)); cells=collections.defaultdict(list); under=0; n=0
for p in me.polygons:
    c=fp.matrix_world@p.center
    h=tree.ray_cast(Vector((c.x,c.y,400)),Vector((0,0,-1)))
    if h[0] is None: continue
    f=c.z-h[0].z; n+=1
    if f<-0.005 and (c.xy-C).length>34: under+=1; U.append(f)
    cells[(int(c.x//16),int(c.y//16))].append(f)
bad=[(k,statistics.median(v)) for k,v in cells.items() if abs(statistics.median(v))>0.25]
print('faces',n,'face centres under DTM (outside zone)',under,'cells',len(cells),'bad cells',len(bad))
for k,v in sorted(bad,key=lambda r:-abs(r[1]))[:15]: print('BAD',k[0]*16,k[1]*16,round(v,2),'dist',round((Vector((k[0]*16+8,k[1]*16+8))-C).length,1))
import collections as cc
h=cc.Counter(min(int(-u/0.02),10) for u in U); print('under hist (2 cm bins)',sorted(h.items()))
