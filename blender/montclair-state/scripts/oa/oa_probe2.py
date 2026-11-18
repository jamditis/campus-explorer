import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
for o in bpy.data.objects:
    if o.type not in ('MESH','LIGHT') or o.hide_render: continue
    lo,hi=bb(o)
    if hi[0]>-2.3 and lo[0]<8.6 and hi[1]>6.9 and lo[1]<14.1 and hi[2]>141.8 and lo[2]<145.1 and (hi[0]-lo[0])<40:
        print('IN',o.name[:90],lo,hi,o.type)
