import bpy, mathutils
for c in bpy.data.collections:
    if c.name[:2] in ('NG','NH','NI','NJ','NK','NL','NM','NN','NO','NP','NQ','NR','NS','NT','NU','NV','NW','NX','NY','NZ'):
        print('COL',c.name,len(c.objects))
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
for o in bpy.data.objects:
    n=o.name
    if o.type=='MESH' and not o.hide_render and ('2F' in n or 'balcony' in n.lower() or 'back hallway' in n.lower() or 'student' in n.lower()) :
        print('OBJ',n,bb(o),len(o.data.polygons))
for o in bpy.data.objects:
    if o.type=='CAMERA' and o.name.startswith(('NZ_','NG_CAM','NV_CAM','NW_')): print('CAM',o.name,tuple(round(x,2) for x in o.location))
