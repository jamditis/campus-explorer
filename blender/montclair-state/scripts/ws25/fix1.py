import bpy, bmesh
from mathutils import Vector
col=bpy.data.collections['WS25_Partridge_tile_hip_roof_stucco_JoePhoto_20261110ws25']
F=bpy.data.materials['WS25_Partridge_fascia_burgundy_JoePhoto']
F.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.11,0.012,0.012,1)
so=bpy.data.objects['WS25_Partridge_eave_soffit_UNVERIFIED']
z=min(v.co.z for v in so.data.vertices)+so.matrix_world.translation.z
outer=[]
for v in so.data.vertices:
    w=so.matrix_world@v.co
    outer.append(w)
# outer rect corners = the 4 points farthest from centre
cen=sum(outer,Vector())/len(outer)
uniq=[]
for p in outer:
    if all((p-q).length>0.01 for q in uniq): uniq.append(p)
uniq.sort(key=lambda p:-(p-cen).length); rect=uniq[:4]
import math
rect.sort(key=lambda p: math.atan2(p.y-cen.y,p.x-cen.x))
core=[o for o in bpy.data.objects if o.name.startswith('TX Partridge core')][0]
top=[p for p in core.data.polygons if p.normal.z>0.9][0]
poly=[core.matrix_world@core.data.vertices[i].co for i in top.vertices]
cc=sum(poly,Vector())/len(poly)
poly=[Vector((p.x,p.y,0)) for p in poly]
# offset outward 2 cm (radial approx)
poly=[p+((p-Vector((cc.x,cc.y,0))).normalized()*0.02) for p in poly]
bm=bmesh.new()
ro=[bm.verts.new((p.x,p.y,z)) for p in rect]
ri=[bm.verts.new((p.x,p.y,z)) for p in poly]
es=[bm.edges.new((ro[i],ro[(i+1)%4])) for i in range(4)]+[bm.edges.new((ri[i],ri[(i+1)%len(ri)])) for i in range(len(ri))]
bmesh.ops.triangle_fill(bm,use_beauty=True,use_dissolve=False,edges=es)
for f in bm.faces:
    if f.normal.z>0: f.normal_flip()
me=so.data; so.matrix_world=__import__('mathutils').Matrix(); bm.to_mesh(me); bm.free()
print('SOFFIT faces',len(me.polygons))
# frieze skirt: stucco band on the core outline from 155.3 to soffit
ST=bpy.data.materials['WS25_Partridge_stucco_cream_JoePhoto']
bm=bmesh.new(); n=len(poly)
lo=[bm.verts.new((p.x,p.y,155.3)) for p in poly]; hi=[bm.verts.new((p.x,p.y,z+0.01)) for p in poly]
for i in range(n):
    j=(i+1)%n; bm.faces.new((lo[i],lo[j],hi[j],hi[i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
# ensure outward
f0=bm.faces[0]; c0=f0.calc_center_median()
if (c0-Vector((cc.x,cc.y,c0.z))).dot(f0.normal)<0:
    for f in bm.faces: f.normal_flip()
me2=bpy.data.meshes.new('WS25_Partridge_frieze_skirt_stucco_UNVERIFIED'); bm.to_mesh(me2); bm.free()
o=bpy.data.objects.new(me2.name,me2); col.objects.link(o); me2.materials.append(ST)
# brackets bigger (scale about each bracket centre)
bo=bpy.data.objects['WS25_Partridge_corner_brackets_burgundy_UNVERIFIED']
bm=bmesh.new(); bm.from_mesh(bo.data)
islands=[]; seen=set()
for v in bm.verts:
    if v.index in seen: continue
    st=[v]; isl=[]
    while st:
        x=st.pop()
        if x.index in seen: continue
        seen.add(x.index); isl.append(x); st+= [e.other_vert(x) for e in x.link_edges]
    islands.append(isl)
for isl in islands:
    top=max(v.co.z for v in isl); c=sum((v.co for v in isl),Vector())/len(isl)
    for v in isl:
        d=v.co-c; v.co=Vector((c.x+d.x*1.3,c.y+d.y*1.3,top-(top-v.co.z)*1.4))
bm.to_mesh(bo.data); bm.free()
print('brackets',len(islands))
bpy.ops.wm.save_mainfile(); print('SAVED')
