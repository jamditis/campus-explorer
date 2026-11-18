import bpy, bmesh, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
GN=['QW_DTM_north_edge_ramp_UNVERIFIED','WV_stone_west_LiDAR_patch_UNVERIFIED','Context_skirt_3DEP_ortho_4km','WN_south_wood_LiDAR_patch_ext_UNVERIFIED','WO_gully_head_LiDAR_patch_UNVERIFIED']
import glob
# add other ground-like objects near Stone
for o in bpy.data.objects:
    if o.type=='MESH' and ('LiDAR_patch' in o.name or 'DTM' in o.name) and o.name not in GN:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if min(p.x for p in bb)<180 and max(p.x for p in bb)>128 and min(p.y for p in bb)<305 and max(p.y for p in bb)>210: GN.append(o.name)
print('GROUND',GN)
trees={}
for n in GN:
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh()
    bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    trees[n]=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear()
def gz(x,y):
    best=None
    for n,t in trees.items():
        h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
        if h[0] is not None and (best is None or h[0].z>best[0]): best=(h[0].z,n)
    return best
o=bpy.data.objects['TI_Stone_Hall_313028565_lower_UNVERIFIED']
me=o.data; mw=o.matrix_world
zmin=min((mw@v.co).z for v in me.vertices)
# outer wall faces: vertical polys
edges=[]
for p in me.polygons:
    n=(mw.to_3x3()@p.normal).normalized()
    if abs(n.z)>0.1: continue
    vs=[mw@me.vertices[i].co for i in p.vertices]
    low=[v for v in vs if v.z<zmin+0.5]
    if len(low)<2: continue
    a,b=low[0],low[1]
    edges.append((a,b,n,p.index))
out=[]
for a,b,n,pi in edges:
    L=(Vector((b.x,b.y))-Vector((a.x,a.y))).length
    k=max(2,int(L/0.25))
    prof=[]
    for i in range(k+1):
        t=i/k; p=a.lerp(b,t)+n*0.15
        g=gz(p.x,p.y); prof.append(None if g is None else round(g[0],3))
    vals=[v for v in prof if v is not None]
    if not vals: continue
    out.append(dict(poly=pi,a=[round(a.x,2),round(a.y,2)],b=[round(b.x,2),round(b.y,2)],n=[round(n.x,2),round(n.y,2)],L=round(L,1),zmin=min(vals),zmax=max(vals),rough=round(sum(abs(vals[i+1]-vals[i]) for i in range(len(vals)-1)),2),prof=prof))
    print('EDGE',pi,out[-1]['a'],out[-1]['b'],'n',out[-1]['n'],'L',out[-1]['L'],'z',min(vals),max(vals),'rough',out[-1]['rough'])
json.dump(dict(zmin=zmin,edges=out),open('/workspace/nj-scenes/montclair-state/scripts/wm/stone_base.json','w'))
print('ZMIN',zmin)
