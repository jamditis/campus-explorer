# W53c part 2 (after fix227a): probe227b shows the residual SE high ground is long sliver fans radiating from two base
# apex vertices on the mesh boundary, (246.3,-248.7) +3.6 m and (246.0,-33.5) +1.5-1.8 m over dtm_1m. Both apices are
# welded to WS60_terrain_edge_apron_LiDAR_to_skirt, so they stay put (snapping them alone, tried as ws227b, dropped the
# slivers up to 3 m under the DTM). Instead split every non-boundary edge > 4 m of the fan faces (repeat until none)
# and set each new vertex to dtm_1m, blended back to the linear sliver height within 12 m of the apex. Mesh boundary
# edges are never split (apron join unchanged). UVs interpolate with the split.
import bpy, bmesh
from mathutils import Vector
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def dtm(x,y):
    gx=x+250-0.5; gy=y+250-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(498,max(0,i)); j=min(498,max(0,j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
AP=[Vector((246.29,-248.74)),Vector((245.97,-33.5))]
apex=[v for v in bm.verts if min((v.co.to_2d()-a).length for a in AP)<0.05]
assert len(apex)==2, len(apex)
hot=set(apex); faces=set(f for v in apex for f in v.link_faces)
nv=0
for it in range(14):
    E=set(e for f in faces if f.is_valid for e in f.edges if not e.is_boundary and e.calc_length()>4.0)
    if not E: break
    r=bmesh.ops.subdivide_edges(bm,edges=list(E),cuts=1,use_grid_fill=False)
    new=[g for g in r['geom_inner'] if isinstance(g,bmesh.types.BMVert)]
    for v in new:
        x,y,z=v.co; da=min((v.co.to_2d()-a).length for a in AP)
        w=min(1.0,da/12.0); w=w*w*(3-2*w); v.co.z=z*(1-w)+dtm(x,y)*w
    nv+=len(new); hot.update(new)
    hot=set(v for v in hot if v.is_valid); fs=set(f for v in hot for f in v.link_faces)
    bmesh.ops.triangulate(bm,faces=[f for f in fs if len(f.verts)>3],quad_method='BEAUTY',ngon_method='BEAUTY')
    hot=set(v for v in hot if v.is_valid); faces=set(f for v in hot for f in v.link_faces)
faces=set(f for v in hot if v.is_valid for f in v.link_faces)
tri=bmesh.ops.triangulate(bm,faces=[f for f in faces if len(f.verts)>3])
faces=set(f for v in hot if v.is_valid for f in v.link_faces)
up=0
for f in faces:
    if f.is_valid and f.normal.z<0: f.normal_flip(); up+=1
big=sum(1 for f in bm.faces if f.calc_area()>20 and f.calc_center_median().x>90 and f.calc_center_median().y<-30)
maxe=max((e.calc_length() for f in faces if f.is_valid for e in f.edges if not e.is_boundary),default=0)
bm.to_mesh(me); bm.free(); me.update()
print('F227Y big SE faces >20m2',big,'max inner edge',round(maxe,2),flush=True)
print('F227Y iters',it,'new verts',nv,'faces touched',len(faces),'flipped',up,flush=True)
