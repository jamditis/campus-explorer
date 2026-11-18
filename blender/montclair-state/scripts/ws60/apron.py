# ws60: WS60_terrain_edge_apron — a 30 m smooth ramp strip from the LiDAR terrain boundary (tucked 5 cm under) down/up to the 4 km skirt (tucked 10 cm under), hiding the 0.5–7 m plate-edge steps. Uses terrain material.
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
W=30.0; ROWS=4
dg=bpy.context.evaluated_depsgraph_get()
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tb=bmesh.new(); tb.from_mesh(t.evaluated_get(dg).to_mesh()); tb.transform(t.matrix_world)
s=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; sb=bmesh.new(); sb.from_mesh(s.evaluated_get(dg).to_mesh()); sb.transform(s.matrix_world); S=BVHTree.FromBMesh(sb)
xs=[v.co.x for v in tb.verts]; ys=[v.co.y for v in tb.verts]; X0,X1,Y0,Y1=min(xs),max(xs),min(ys),max(ys)
def outdir(p):
    d={(-1,0):p.x-X0,(1,0):X1-p.x,(0,-1):p.y-Y0,(0,1):Y1-p.y}
    k=min(d,key=d.get); return Vector((k[0],k[1],0)),d[k]
def sz(x,y,fallback):
    r=S.ray_cast(Vector((x,y,fallback+80)),Vector((0,0,-1)),400); return r[0].z if r[0] else fallback
bm=bmesh.new(); cache={}
def ring(v):
    key=v.index
    if key in cache: return cache[key]
    o,dist=outdir(v.co)
    if dist>3: cache[key]=None; return None   # interior hole boundary, not the outer edge
    z0=v.co.z-0.05; out=v.co+o*W; z1=sz(out.x,out.y,z0)-0.10
    vs=[]
    for r in range(ROWS+1):
        f=r/ROWS; k=f*f*(3-2*f); p=v.co+o*(W*f)
        vs.append(bm.verts.new((p.x,p.y,z0+(z1-z0)*k if r<ROWS else z1)))
    cache[key]=vs; return vs
n=0
for e in tb.edges:
    if not e.is_boundary: continue
    a=ring(e.verts[0]); b=ring(e.verts[1])
    if not a or not b: continue
    for r in range(ROWS):
        try: bm.faces.new((a[r],b[r],b[r+1],a[r+1])); n+=1
        except ValueError: pass
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS60_terrain_edge_apron'); bm.to_mesh(me)
for p in me.polygons: p.use_smooth=True
ob=bpy.data.objects.new('WS60_terrain_edge_apron_LiDAR_to_skirt',me)
for m in t.data.materials: me.materials.append(m)
(t.users_collection[0] if t.users_collection else bpy.context.scene.collection).objects.link(ob)
print('AP60 faces',n,'verts',len(me.vertices))
