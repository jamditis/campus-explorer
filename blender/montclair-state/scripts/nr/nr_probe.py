import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
for o in bpy.data.objects:
    if o.type not in ('MESH','EMPTY','CURVE'): continue
    lo,hi=bb(o)
    if -23<lo[0] and hi[0]<16 and -2<lo[1] and hi[1]<22 and 137.3<lo[2]<139 and (hi[0]-lo[0])<4 and (hi[1]-lo[1])<4:
        n=o.name.lower()
        print('P',o.name,'|',o.users_collection[0].name if o.users_collection else '','|',o.type,lo,hi,len(o.data.vertices) if o.type=='MESH' else '', o.data.name if o.data else '', [m.name for m in o.modifiers][:3])
