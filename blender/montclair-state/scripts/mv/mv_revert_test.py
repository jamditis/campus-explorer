# Session mv REVERT test (in-folder copy): restore the LiDAR roof mesh vertex coords from montclair_state_pre_20261029mv.blend;
# expect 10 verts changed by mv and identical coords afterwards; object count unchanged (6,095).
import bpy
nm='School of Communication and Media roof (LiDAR)'
o=bpy.data.objects[nm]; cur=o.data
with bpy.data.libraries.load('//montclair_state_pre_20261029mv.blend') as (src,dst):
    dst.objects=[nm]
bo=dst.objects[0]; old=bo.data
diff=[i for i,(a,b) in enumerate(zip(cur.vertices,old.vertices)) if (a.co-b.co).length>1e-6]
print('NVERT',len(cur.vertices),len(old.vertices),'CHANGED',len(diff),diff)
for i in diff: cur.vertices[i].co=old.vertices[i].co
cur.update()
d2=[i for i,(a,b) in enumerate(zip(cur.vertices,old.vertices)) if (a.co-b.co).length>1e-6]
bpy.data.objects.remove(bo)
print('REVERT remaining diffs',len(d2),'COUNT',len(bpy.data.objects))
