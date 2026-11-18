import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
for o in bpy.data.objects:
    n=o.name.lower()
    if o.type=='MESH' and any(k in n for k in ('back hallway','blockout','blocked','fill box','n classroom','1f','floor','ground','grass','lawn')) and not o.hide_render:
        lo,hi=bb(o)
        if hi[0]>-30 and lo[0]<30 and hi[1]>-25 and lo[1]<40 and hi[2]>130:
            print('P|',o.name,'|',lo,hi,'|',[s.material.name if s.material else None for s in o.material_slots][:3], len(o.data.polygons))
for o in bpy.data.objects:
    if o.type=='CAMERA' and o.name.startswith(('NU_','NT_')): print('C|',o.name,tuple(round(x,2) for x in o.location))
