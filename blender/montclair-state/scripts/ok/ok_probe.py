import bpy, collections
from mathutils import Vector
cnt=collections.Counter(); vis=collections.Counter(); ex={}
for o in bpy.data.objects:
    if o.name.startswith('SCH_win_'):
        k=(o.get('run'),o.get('row')); cnt[k]+=1
        if not o.hide_render: vis[k]+=1; ex.setdefault(k,o)
for k in sorted(cnt,key=str): print('RUN',k,cnt[k],'visible',vis[k])
o=next(iter(ex.values())); print('example',o.name,o.type,o.instance_type,o.instance_collection and o.instance_collection.name, [round(x,3) for x in o.scale], o.matrix_world.to_3x3()); print(dict(o.items()))
ic=o.instance_collection
if ic:
    for ob in ic.all_objects: print(' inst',ob.name,[round(x,3) for x in ob.dimensions], ob.location)
for n in bpy.data.objects.keys():
    if n.startswith(('OI_Schmitt_pav','OI_Schmitt_pier','OJ_','OH_Schmitt','OH_land','OH_cheek')) or 'cheek' in n.lower() or 'plinth' in n.lower():
        ob=bpy.data.objects[n]
        if ob.type=='MESH':
            bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
            print('OBJ',n,[m.name for m in ob.data.materials],'z',round(min(v.z for v in bb),2),round(max(v.z for v in bb),2),'x',round(min(v.x for v in bb),1),round(max(v.x for v in bb),1),'y',round(min(v.y for v in bb),1),round(max(v.y for v in bb),1), ob.users_collection[0].name)
