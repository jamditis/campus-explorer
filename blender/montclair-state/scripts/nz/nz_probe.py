import bpy, mathutils
def bb(o):
    ws=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    return tuple(round(min(w[i] for w in ws),2) for i in range(3))+tuple(round(max(w[i] for w in ws),2) for i in range(3))
for o in bpy.data.objects:
    if o.type!='MESH': continue
    b=bb(o)
    if b[0]<7 and b[3]>-1 and b[1]<18.5 and b[4]>12 and b[2]<141.5 and b[5]>137 and (b[3]-b[0])<30:
        print('NCL',o.name,b,o.hide_render,[s.material.name for s in o.material_slots if s.material][:2])
for o in bpy.data.objects:
    if 'strobe' in o.name.lower() or 'inward room shell' in o.name.lower() or 'room shell' in o.name.lower():
        print('X',o.name,bb(o) if o.type=='MESH' else '',o.hide_render)
