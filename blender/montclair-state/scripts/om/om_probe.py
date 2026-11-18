import bpy
from mathutils import Vector
cap=bpy.data.objects['OL_Schmitt_walk_island_lawn_caps']; me=cap.data
print('cap polys',len(me.polygons),'mats',[m.name for m in me.materials])
for o in bpy.data.objects:
    if o.type in('MESH','EMPTY') and abs(o.location.x-21.6)<12 and abs(o.location.y-136.5)<12 or abs(o.location.x-47.8)<15 and abs(o.location.y-150.2)<15:
        if o.type=='EMPTY' or len(o.data.vertices)<5000 if o.type=='MESH' else True:
            print('NEAR',o.name,o.type,[round(x,2) for x in o.location],o.users_collection[0].name if o.users_collection else None, o.instance_collection.name if o.instance_type=='COLLECTION' and o.instance_collection else '')
c=bpy.data.collections['OK_Schmitt_window_grids_sills_return_plinth_20261031ok']
for o in c.objects: print('OK',o.name,o.type,len(o.data.vertices) if o.type=='MESH' else '',[m.name for m in o.data.materials] if o.type=='MESH' else '')
for n in bpy.data.objects:
    if 'blind' in n.name.lower() and 'Schmitt' in n.name or ('blind' in n.name.lower() and n.name.startswith('O')): print('BLIND',n.name,n.type)
for m in bpy.data.materials:
    if 'blind' in m.name.lower(): print('BMAT',m.name,m.users)
