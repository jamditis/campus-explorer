# ws70: grass berms graded from the back top of the gap-strip curbs down to ground (lawn material, not the ortho drape)
import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
MATN=os.environ.get('MAT','Lawn_Varied_Oct_local_fade')
M=bpy.data.materials[MATN]
print('B70 mat nodes',[(n.type,n.name) for n in M.node_tree.nodes][:30])
def bvh(o):
    oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
GB=[bvh(o) for o in O if o.name.startswith(('Terrain_LiDAR_DTM_1m','WS68_RHD_ground'))]
RB=[bvh(o) for o in O if o.name.startswith(('WS27_CollegeAve_carriageway','KY_college_ave_carriageway','WS67_CollegeAve_gap_asphalt'))]
def gz(x,y):
    hs=[t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0] for t in GB]; hs=[h.z for h in hs if h]; return max(hs) if hs else None
def rz(x,y):
    hs=[t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0] for t in RB]; hs=[h.z for h in hs if h]; return max(hs) if hs else None
C=O['WS69_CollegeAve_gap_strip_curbs_UNVERIFIED']; cm=C.data
old=O.get('WS70_gap_strip_grass_berms')
if old: bpy.data.objects.remove(old)
bm=bmesh.new(); n=0; vs=[C.matrix_world@v.co for v in cm.vertices]; mx=0
for i in range(0,len(vs),8):
    a,b=vs[i+4],vs[i+5]; nrm=(vs[i+4]-vs[i+3]); nrm.z=0; nrm.normalize()
    # extend along the edge slightly so neighbouring segments overlap
    t=(b-a); t.z=0; t.normalize(); a=a-t*0.05; b=b+t*0.05
    mid=(a+b)/2; drop=max(0.0,mid.z-(gz(*(mid+nrm*2.0).xy) or mid.z-0.3)); Dm=min(6.0,max(2.0,3.0*drop)); mx=max(mx,drop)
    L=6; rows=[]
    for k in range(L+1):
        p=a.lerp(b,k/L); row=[]
        for j,f in enumerate((0,0.12,0.3,0.55,0.8,1.0)):
            d=f*Dm; q=p+nrm*d; g=gz(q.x,q.y)
            if g is None: g=p.z-0.3
            w=f*f*(3-2*f)
            z=(p.z-0.01)*(1-w)+(g+0.03)*w if f<1 else g-0.04
            if 0<f<1: z=max(z,g+0.02)
            r=rz(q.x,q.y)
            if r is not None and f>0: z=min(z,r-0.04)
            row.append(bm.verts.new((q.x,q.y,z)))
        rows.append(row)
    for k in range(L):
        for j in range(5):
            bm.faces.new((rows[k][j],rows[k+1][j],rows[k+1][j+1],rows[k][j+1])); n+=1
bm.normal_update()
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
m=bpy.data.meshes.new('WS70_berms'); bm.to_mesh(m); bm.free()
uv=m.uv_layers.new(name='UVMap')
for l in m.loops:
    c=m.vertices[l.vertex_index].co; uv.data[l.index].uv=(c.x/4.0,c.y/4.0)
ob=bpy.data.objects.new('WS70_gap_strip_grass_berms',m); ob.data.materials.append(M)
for p in m.polygons: p.use_smooth=True
C.users_collection[0].objects.link(ob); print('B70 faces',n,'max drop',round(mx,2))
bpy.ops.wm.save_mainfile(); print('B70 saved')
