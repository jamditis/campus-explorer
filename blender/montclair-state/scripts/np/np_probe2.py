import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    lo,hi=bb(o)
    if -30<lo[0] and hi[0]<25 and -25<lo[1] and hi[1]<30 and lo[2]>144 and (hi[0]-lo[0])<3 and (hi[1]-lo[1])<3:
        print('SMALLHIGH',o.name,lo,hi)
for n in ('NG east balcony slab edge','NG east balcony glass rail','NG bridge W glass rail','NG bridge fascia wood','NG stair S glass rail'):
    o=bpy.data.objects[n]; print('MAT',n,[ (s.link,s.material.name if s.material else None) for s in o.material_slots])
