# ws222e W41 leftover "green fleck": between the W39 curb return's road face (x ~ -248.77 at y -53.7) and the WS27 carriageway
# W edge (straight (-249.208,-56.194)->(-248.495,-53.435)) a 0.1-0.2 m strip of Terrain_LiDAR_DTM_1m showed 6-8 cm below the
# asphalt (evaluated grid probe222g). New gutter fill strip WS222_CollegeAve_return_gutter_asphalt_fill: one quad per return
# section (WS27 edge piecewise via its v5 corner (-248.495,-53.435) to v6 at the curb_left start), inner edge 1.5 cm inside the curb road face, outer edge 2 cm under the WS27 edge, z = WS27 surface - 3 mm.
import bpy, bmesh
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
r=bpy.data.objects['WS220_CollegeAve_curb_jog_return_UNVERIFIED']; RM=r.matrix_world; n=len(r.data.vertices)
car=[o for o in bpy.data.objects if o.name.startswith('WS27_CollegeAve_carriageway')][0]; CM=car.matrix_world; CI=CM.inverted()
E0=Vector((-249.208,-56.194)); E1=Vector((-248.495,-53.435))
E2=Vector((-248.395,-53.048))
def edge_x(y):
    if y<=E1.y: return E0.x+(E1.x-E0.x)*(y-E0.y)/(E1.y-E0.y)
    return E1.x+(E2.x-E1.x)*(y-E1.y)/(E2.y-E1.y)
def asph_z(x,y):
    ok,loc,nn,fi=car.ray_cast(CI@Vector((x,y,128.0)),(CI.to_3x3()@Vector((0,0,-1))).normalized(),distance=10)
    return (CM@loc).z if ok else None
pairs=[]
for k in range(n//5):
    rf=RM@r.data.vertices[5*k+1].co; bk=RM@r.data.vertices[5*k+3].co
    if not (-56.19<=rf.y<=-53.05): continue
    ex=edge_x(rf.y)
    if rf.x>=ex-0.005: continue
    inn=rf.xy+(bk.xy-rf.xy).normalized()*0.015; out=Vector((ex+0.02,rf.y))
    z=asph_z(out.x,out.y)
    if z is None: print('F222E no asphalt at',tuple(out),flush=True); continue
    pairs.append((inn,out,z-0.003)); print('F222E k%d rf (%.3f,%.3f) edge %.3f gap %.3f z %.3f'%(k,rf.x,rf.y,ex,ex-rf.x,z),flush=True)
me=bpy.data.meshes.new('WS222_return_gutter_fill'); bm=bmesh.new(); prev=None
for inn,out,z in pairs:
    a=bm.verts.new((inn.x,inn.y,z)); b=bm.verts.new((out.x,out.y,z))
    if prev: bm.faces.new((prev[0],prev[1],b,a))
    prev=(a,b)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
bm.to_mesh(me); bm.free()
ob=bpy.data.objects.new('WS222_CollegeAve_return_gutter_asphalt_fill_UNVERIFIED',me)
for c in car.users_collection: c.objects.link(ob)
me.materials.append(car.material_slots[0].material)
print('F222E fill faces',len(me.polygons),'collections',[c.name for c in ob.users_collection],flush=True)
