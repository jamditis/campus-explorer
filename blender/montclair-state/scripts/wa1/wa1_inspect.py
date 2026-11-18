import bpy
O=bpy.data.objects
for o in O:
    if o.name.startswith(('QT','QS','QQ','QV','WV','WA0')) and o.type=='MESH':
        d=o.dimensions; bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
        print(o.name,len(o.data.vertices),[round(min(b[i] for b in bb),1) for i in range(2)],[round(max(b[i] for b in bb),1) for i in range(2)],[m.name for m in o.data.materials][:2])
