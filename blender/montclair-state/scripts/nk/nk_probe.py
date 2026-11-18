import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
print('=== doors/glass in CCOM interior')
for o in bpy.data.objects:
    n=o.name.lower()
    if o.type=='MESH' and ('door' in n or 'frosted' in n) and not o.hide_render:
        lo,hi=bb(o)
        if lo[0]>-22 and hi[0]<25 and lo[1]>-20 and hi[1]<30 and lo[2]>135 and hi[2]<150:
            print('D',o.name,lo,hi,[s.material.name if s.material else None for s in o.material_slots], o.users_collection[0].name)
print('=== lights')
for o in bpy.data.objects:
    if o.type=='LIGHT' and not o.hide_render:
        l=o.location
        if -22<l.x<25 and -20<l.y<30 and 135<l.z<150:
            print('L',o.name,o.data.type,round(o.data.energy,1),getattr(o.data,'size',None),tuple(round(x,2) for x in l), o.users_collection[0].name)
print('=== cutaway aerial objects above atrium x-19.5..-2 y6..17 z>141')
for o in bpy.data.objects:
    if o.type=='MESH' and not o.hide_render:
        lo,hi=bb(o)
        if hi[2]>141 and lo[0]<-3 and hi[0]>-19 and lo[1]<16 and hi[1]>7 and (hi[0]-lo[0])<200:
            print('R',o.name,lo,hi,o.users_collection[0].name)
