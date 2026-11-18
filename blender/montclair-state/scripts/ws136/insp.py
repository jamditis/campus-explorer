import bpy
from mathutils import Vector
def hit(o,b):
    mw=o.matrix_world
    xs=[(mw@Vector(c)) for c in o.bound_box]
    return not(max(v.x for v in xs)<b[0] or min(v.x for v in xs)>b[1] or max(v.y for v in xs)<b[2] or min(v.y for v in xs)>b[3])
for b in [(-90,-58,-250,-205)]:
    for o in bpy.data.objects:
        if o.type=='MESH' and hit(o,b) and len(o.data.polygons)<200000:
            mw=o.matrix_world; vs=[mw@v.co for v in o.data.vertices if b[0]<=(mw@v.co).x<=b[1] and b[2]<=(mw@v.co).y<=b[3]]
            print(o.name,len(o.data.polygons),len(vs), round(min([v.z for v in vs]),2) if vs else None, round(max([v.z for v in vs]),2) if vs else None,[m.name for m in o.data.materials][:2],o.hide_render, [m.type for m in o.modifiers])
