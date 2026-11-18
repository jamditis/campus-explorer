# UNIFY #31: triangular gap between the stair's S edge (y -201.3) and the skewed S-wing face beside the upper risers -> continue the S cheek wall up the stair to the landing
import bpy, bmesh
ch=next(o for o in bpy.data.objects if o.name.startswith('WS120_Chapin_W_entrance_stair_S_cheek'))
bm=bmesh.new()
P=[(-215.40,-201.28,123.75),(-213.40,-201.28,124.77),(-213.40,-201.86,124.77),(-215.40,-201.42,123.75)]
top=[bm.verts.new(p) for p in P]; bot=[bm.verts.new((p[0],p[1],122.5)) for p in P]
bm.faces.new(top); bm.faces.new(list(reversed(bot)))
for i in range(4): j=(i+1)%4; bm.faces.new((bot[i],bot[j],top[j],top[i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
me=bpy.data.meshes.new('WS124_Chapin_W_stair_S_cheek_upper_to_landing_UNIFY31'); bm.to_mesh(me); bm.free()
for m in ch.data.materials: me.materials.append(m)
o=bpy.data.objects.new(me.name,me); ch.users_collection[0].objects.link(o)
bpy.ops.wm.save_mainfile(); print('M124g SAVED')
