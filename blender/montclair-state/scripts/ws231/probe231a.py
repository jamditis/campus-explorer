# ws231 probe a: Roads_OSM / Footpaths_OSM structure + W53l footpath and W53k street heights vs evaluated ground and 3DEP 1 m
import bpy,sys,os,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
P=np.load(M+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y):
    gx=x+280-0.5; gy=y+280-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    return float(P[i,j]*(1-fx)*(1-fy)+P[i,j+1]*fx*(1-fy)+P[i+1,j]*(1-fx)*fy+P[i+1,j+1]*fx*fy)
G=['Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt','WS230_NE_east_gap_fill_3DEP_UNVERIFIED']
with bpy.data.libraries.load(M+'montclair_state.blend',link=False) as (src,dst):
    dst.objects=G+['Roads_OSM','Footpaths_OSM']
O=[o for o in dst.objects if o]
for o in O: bpy.context.scene.collection.objects.link(o)
for o in O: print('P231A',o.name,len(o.data.vertices),[(m.name,m.type) for m in o.modifiers],[c.name for c in o.users_collection],o.data.materials[:] and o.data.materials[0].name,flush=True)
dg=bpy.context.evaluated_depsgraph_get(); B=[]
for o in O:
    if o.name in G:
        e=o.evaluated_get(dg); mm=e.to_mesh(); W=o.matrix_world
        B.append((o.name,BVHTree.FromPolygons([W@v.co for v in mm.vertices],[p.vertices[:] for p in mm.polygons]))); e.to_mesh_clear()
def gz(x,y):
    zs=[(b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0],n) for n,b in B]
    zs=[(h.z,n) for h,n in zs if h is not None]
    return max(zs) if zs else (None,None)
fp=bpy.data.objects['Footpaths_OSM']; W=fp.matrix_world
for v in fp.data.vertices:
    w=W@v.co
    if 150<w.x<175 and 230<w.y<262: print('P231A W53l v',v.index,round(w.x,1),round(w.y,1),round(w.z,2),'3dep',round(p3(w.x,w.y),2),'ground',gz(w.x,w.y),flush=True)
# Footpaths edges topology near region
me=fp.data; print('P231A fp polys',len(me.polygons),'edges',len(me.edges),flush=True)
rd=bpy.data.objects['Roads_OSM']; W=rd.matrix_world; d=[]
for v in rd.data.vertices:
    w=W@v.co
    if 205<w.x<236 and 160<w.y<225: d.append((round(w.x,1),round(w.y,1),round(w.z,2),round(w.z-p3(w.x,w.y),2)))
print('P231A W53k road verts',len(d),'dz range',min(x[3] for x in d),max(x[3] for x in d),flush=True)
print('P231A sample',d[:40],flush=True)
sys.stdout.flush(); os._exit(0)
