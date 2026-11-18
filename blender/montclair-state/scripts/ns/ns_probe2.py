import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    lo,hi=bb(o)
    if hi[0]>-23 and lo[0]<-12 and hi[1]>7 and lo[1]<17 and hi[2]>136.5 and lo[2]<141 and (hi[0]-lo[0])<12:
        print('Q|',o.name,'|',lo,hi,len(o.data.vertices),o.users_collection[0].name if o.users_collection else '')
for o in bpy.data.objects:
    if o.type=='CAMERA' and o.name.startswith(('NR_','NQ_','NK_','NJ_','NI_')): print('C|',o.name,tuple(round(v,2) for v in o.location),tuple(round(v,3) for v in o.rotation_euler),round(o.data.lens,1))
