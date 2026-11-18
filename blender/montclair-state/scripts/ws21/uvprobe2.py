import bpy,bmesh
from mathutils import Vector
o=bpy.data.objects['Life Hall walls']; M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data)
uvl=bm.loops.layers.uv['facade']
for f in bm.faces:
    c=M@f.calc_center_median()
    if 10<c.x<45 and 95<c.y<112 and c.z>139:
        print('F',f.index,[(round((M@l.vert.co).x,2),round((M@l.vert.co).y,2),round((M@l.vert.co).z,2),round(l[uvl].uv.x,2),round(l[uvl].uv.y,2)) for l in f.loops])
