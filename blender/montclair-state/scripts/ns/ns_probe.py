import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
print('NOBJ',len(bpy.data.objects))
for o in bpy.data.objects:
    n=o.name.lower()
    if o.type in('MESH','CAMERA') and (any(k in n for k in ('entrance','front door','vestib','push bar','mat ','arch','threshold')) or o.type=='CAMERA' and o.name.startswith(('NR_','NQ_'))):
        lo,hi=bb(o); print('P|',o.name,'|',o.type,lo,hi,o.hide_render, o.users_collection[0].name if o.users_collection else '')
