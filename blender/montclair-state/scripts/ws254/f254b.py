# ws254b: the Feliciano E base course (PI, stepped band that followed the old hump) crossed the new doors and stood up to ~1 m above
# the widened treads in the recess -> drop its faces on the recessed wall plane (x < -196.9, y 166..172.2); the wall above the
# stairs/landing is plain stucco there now (base course north of y 172 unchanged).
import bpy, bmesh
pi=bpy.data.objects['PI_Feliciano_east_base_course_UNVERIFIED']; Mp=pi.matrix_world
bm=bmesh.new(); bm.from_mesh(pi.data)
df=[f for f in bm.faces if all((Mp@v.co).x<-196.9 and 166.0<=(Mp@v.co).y<=172.2 for v in f.verts)]
n0=len(bm.faces); bmesh.ops.delete(bm,geom=df,context='FACES_ONLY')
lv=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lv,context='VERTS')
bm.to_mesh(pi.data); bm.free(); pi.data.update(); print('F254B base course faces',n0,'-> deleted',len(df),flush=True)
