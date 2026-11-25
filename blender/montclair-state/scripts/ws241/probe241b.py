# W57/W58 edge probe: base-mesh boundary verts of a ground object inside a region, and the raw outside ground at that xy
# (Context skirt evaluated with its *_under_* modifiers OFF, plus M3b / other listed grounds). Writes probe241b.json.
import bpy, bmesh, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
JOBS=[('M3a_north_LiDAR_DTM_1m_ext_y515',(-150,-110,900,1090)),('WS68_RHD_ground_northDTM',(-356,-340,-80,0))]
OTH=['M3b_north_LiDAR_DTM_1m_west_rail_corridor']
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
print('P241B skirt mods',[(m.name,m.show_render) for m in sk.modifiers],flush=True)
for m in sk.modifiers:
    m.show_viewport = m.show_render and ('under' not in m.name.lower())
def bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear(); return t
T=[('skirt',bvh(sk))]+[(o.name[:20],bvh(o)) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(tuple(OTH))]
out={}
for pre,(x0,x1,y0,y1) in JOBS:
    o=next(x for x in bpy.data.objects if x.name.startswith(pre)); M=o.matrix_world
    print('P241B',o.name,'mods',[(m.name,m.type,m.show_render) for m in o.modifiers],flush=True)
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); L=[]
    for v in bm.verts:
        if not v.is_boundary: continue
        p=M@v.co
        if not (x0<=p.x<=x1 and y0<=p.y<=y1): continue
        zs=[]
        for n,t in T:
            h=t.ray_cast(Vector((p.x,p.y,p.z+30)),Vector((0,0,-1)),60)
            if h[0] is not None: zs.append((round(h[0].z,3),n))
        L.append([v.index,round(p.x,2),round(p.y,2),round(p.z,3),zs])
    out[o.name]=L; bm.free()
    d=[l[3]-max(z for z,n in l[4]) for l in L if l[4]]
    print('P241B',o.name[:30],'boundary verts',len(L),'step over outside: n>0.05',sum(1 for x in d if x>0.05),'max',round(max(d),2) if d else None,flush=True)
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws241/probe241b.json','w'))
os._exit(0)
