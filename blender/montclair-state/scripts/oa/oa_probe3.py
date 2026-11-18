import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    lo,hi=bb(o)
    if hi[0]>-2.3 and lo[0]<8.6 and hi[1]>13.3 and lo[1]<14.3 and hi[2]>137 and lo[2]<145.5 and ('door' in o.name.lower() or 'frame' in o.name.lower()):
        print('D',o.name[:80],lo,hi)
