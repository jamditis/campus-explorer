# ws69c: grass shoulders graded from the back top of the gap-strip curbs down to the ground over 2.5 m (ortho-UV affine copied from WS68 ground)
import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
G=[o for o in O if o.name.startswith('WS68_RHD_ground')][0]
# affine uv fit
me=G.data; uvl=me.uv_layers.active.data; X=[];U=[]
for pi in range(0,len(me.polygons),7):
    p=me.polygons[pi]
    for li in p.loop_indices:
        c=G.matrix_world@me.vertices[me.loops[li].vertex_index].co; X.append((c.x,c.y,1)); U.append(tuple(uvl[li].uv))
X=np.array(X);U=np.array(U); A,res,_,_=np.linalg.lstsq(X,U,rcond=None); err=np.abs(X@A-U).max(); print('H69 uv fit err',err)
GB=[bvh(o) for o in O if o.name.startswith(('Terrain_LiDAR_DTM_1m','WS68_RHD_ground'))]
def gz(x,y):
    hs=[t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0] for t in GB]; hs=[h.z for h in hs if h]; return max(hs) if hs else None
C=O['WS69_CollegeAve_gap_strip_curbs_UNVERIFIED']; cm=C.data
old=O.get('WS69_gap_strip_grass_shoulders'); 
if old: bpy.data.objects.remove(old)
bm=bmesh.new(); uvL=bm.loops.layers.uv.new('UVMap'); n=0
# each curb seg = 3 faces; back top edge = verts 4,5 of each 8-vert block
vs=[C.matrix_world@v.co for v in cm.vertices]
for i in range(0,len(vs),8):
    a,b=vs[i+4],vs[i+5]; t=(b-a); t.z=0; nrm=(vs[i+4]-vs[i+3]); nrm.z=0; nrm.normalize()
    L=8; rows=[]
    for k in range(L+1):
        p=a.lerp(b,k/L); row=[]
        for j,d in enumerate((0,0.6,1.3,2.0,2.8)):
            q=p+nrm*d; g=gz(q.x,q.y)
            if g is None: g=p.z-0.3
            w=min(1,d/2.8); w=w*w*(3-2*w)
            z=(p.z-0.01)*(1-w)+(g+0.02)*w if d<2.8 else g-0.03
            z=max(z,g+0.0) if d>0 else z
            row.append(bm.verts.new((q.x,q.y,z)))
        rows.append(row)
    for k in range(L):
        for j in range(4):
            f=bm.faces.new((rows[k][j],rows[k+1][j],rows[k+1][j+1],rows[k][j+1])); n+=1
            for l in f.loops:
                c=l.vert.co; l[uvL].uv=tuple(np.array((c.x,c.y,1))@A)
bm.normal_update()
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
m=bpy.data.meshes.new('WS69_shoulders'); bm.to_mesh(m); bm.free()
ob=bpy.data.objects.new('WS69_gap_strip_grass_shoulders',m); ob.data.materials.append(G.data.materials[0])
for p in m.polygons: p.use_smooth=True
C.users_collection[0].objects.link(ob); print('H69 faces',n)
bpy.ops.wm.save_mainfile(); print('H69 saved')
