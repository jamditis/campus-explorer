# ws69: concrete curbs (0.15 m reveal, 0.15 m wide) along the open long edges of WS67_CollegeAve_gap_asphalt
import bpy,bmesh
from mathutils import Vector
O=bpy.data.objects
G=[o for o in O if o.name.startswith('WS67_CollegeAve_gap_asphalt')][0]
roads=[o for o in O if o.name.startswith(('WS27_CollegeAve_carriageway','KY_college_ave_carriageway'))]
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
from mathutils.bvhtree import BVHTree
def bvh(o):
    oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
RB=[bvh(o) for o in roads]
old=O.get('WS69_CollegeAve_gap_strip_curbs_UNVERIFIED')
if old: bpy.data.objects.remove(old)
GB=[bvh(o) for o in O if o.name.startswith(('Terrain_LiDAR_DTM_1m','WS68_RHD_ground'))]
def gz(p):
    hs=[t.ray_cast(Vector((p.x,p.y,p.z+30)),Vector((0,0,-1)))[0] for t in GB]; hs=[h.z for h in hs if h]
    return min(max(hs),p.z-0.12)-0.15 if hs else p.z-0.12
bm=bmesh.new(); bm.from_mesh(G.data); bm.transform(G.matrix_world); bm.faces.ensure_lookup_table()
cen=sum((f.calc_center_median() for f in bm.faces),Vector())/len(bm.faces)
out=bmesh.new(); W=0.15; H=0.12; D=0.12; n=0
for e in bm.edges:
    if not e.is_boundary: continue
    a,b=e.verts[0].co.copy(),e.verts[1].co.copy(); mid=(a+b)/2; t=(b-a); t.z=0
    if t.length<0.05: continue
    nrm=Vector((-t.y,t.x,0)).normalized()
    fc=e.link_faces[0].calc_center_median()
    if (mid-fc).dot(nrm)<0: nrm=-nrm
    p=mid+nrm*0.4
    if any(r.ray_cast(Vector((p.x,p.y,p.z+20)),Vector((0,0,-1)))[0] for r in RB): continue  # joins another road
    aw,bw=a+nrm*W,b+nrm*W
    vs=[out.verts.new(v) for v in (a+Vector((0,0,-D)),b+Vector((0,0,-D)),b+Vector((0,0,H)),a+Vector((0,0,H)),
         aw+Vector((0,0,H)),bw+Vector((0,0,H)),Vector((bw.x,bw.y,gz(bw))),Vector((aw.x,aw.y,gz(aw))))]
    for q in ((0,1,2,3),(3,2,5,4),(4,5,6,7)): out.faces.new([vs[i] for i in q])
    n+=1
me=bpy.data.meshes.new('WS69_gap_strip_curbs'); out.to_mesh(me); out.free(); bm.free()
ob=bpy.data.objects.new('WS69_CollegeAve_gap_strip_curbs_UNVERIFIED',me)
ob.data.materials.append(bpy.data.materials['WS27_curb_concrete_UNVERIFIED'])
G.users_collection[0].objects.link(ob)
for p in ob.data.polygons: p.use_smooth=False
print('K69 curb segs',n)
bpy.ops.wm.save_mainfile(); print('K69 saved')
