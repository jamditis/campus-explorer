import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
print('P70 mats',[m.name for m in bpy.data.materials if any(k in m.name.lower() for k in ('grass','lawn','turf'))])
# which objects use grass mats near region
for o in O:
    if o.type=='MESH' and o.data.materials and any(m and 'grass' in m.name.lower() for m in o.data.materials):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        if min(v.x for v in bb)<-200 and max(v.x for v in bb)>-300: print('P70 grassobj',o.name,[m.name for m in o.data.materials if m][:3],len(o.data.polygons))
G=[o for o in O if o.name.startswith('WS67_CollegeAve_gap_asphalt')][0]
bb=[G.matrix_world@Vector(c) for c in G.bound_box]; print('P70 gap bbox',G.name,[round(f(v[i] for v in bb),2) for i in range(3) for f in (min,max)])
GB={o.name:bvh(o) for o in O if o.name.startswith(('Terrain_LiDAR_DTM_1m','WS68_RHD_ground','Context_skirt'))}
RB={o.name:bvh(o) for o in O if o.name.startswith(('WS27_CollegeAve_carriageway','KY_college_ave_carriageway','WS67_CollegeAve_gap_asphalt'))}
def h(t,x,y):
    r=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]; return round(r.z,2) if r else None
bm=bmesh.new(); bm.from_mesh(G.data); bm.transform(G.matrix_world)
for e in bm.edges:
    if not e.is_boundary: continue
    m=(e.verts[0].co+e.verts[1].co)/2
    print('P70 edge',round(m.x,1),round(m.y,1),round(m.z,2),'len',round(e.calc_length(),1),{k[:14]:h(t,m.x,m.y) for k,t in GB.items()},{k[:14]:h(t,m.x,m.y) for k,t in RB.items()})
