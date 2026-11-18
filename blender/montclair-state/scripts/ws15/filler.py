import bpy,bmesh
from mathutils import Vector
A=Vector((-98.07,-83.63)); B=Vector((-97.69,-82.99))
d=(B-A).normalized(); n=Vector((-d.y,d.x))  # west/inside
A2=A-d*0.15; B2=B+d*0.35
t=0.35; z0,z1=131.6,143.0
pts=[A2,B2,B2+n*t,A2+n*t]
me=bpy.data.meshes.new('WS15_Cole_addition_junction_filler_wall')
bm=bmesh.new()
lo=[bm.verts.new((p.x,p.y,z0)) for p in pts]; hi=[bm.verts.new((p.x,p.y,z1)) for p in pts]
bm.faces.new(lo[::-1]); bm.faces.new(hi)
for i in range(4):
    j=(i+1)%4; bm.faces.new((lo[i],lo[j],hi[j],hi[i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
bm.to_mesh(me); bm.free()
o=bpy.data.objects.new('WS15_Cole_addition_junction_filler_wall_UNVERIFIED',me)
w=bpy.data.objects['Susan A. Cole Hall walls']
for c in w.users_collection: c.objects.link(o)
me.materials.append(bpy.data.materials['TW_Cole_stucco_cream_UNVERIFIED'])
# box-project UVs via smart project not needed if material uses object/generated coords
bpy.ops.wm.save_mainfile(); print('SAVED')
