import bpy
out=open('data/nq/probe2.txt','w')
for o in bpy.data.objects:
    if o.type!='MESH' or o.instance_type!='NONE':
        l=o.matrix_world.translation
        if -40<l.x<40 and -30<l.y<45: out.write(f"{o.name}|{o.type}|{o.instance_type}|{o.instance_collection.name if o.instance_collection else ''}|{tuple(round(v,2) for v in l)}|{o.hide_render}|{o.users_collection[0].name if o.users_collection else ''}\n")
    elif o.data and o.data.library:
        pass
for o in bpy.data.objects:
    if o.type=='MESH' and ('dome' in o.name.lower() or 'vent' in o.name.lower() or 'rtu' in o.name.lower() or 'mushroom' in o.name.lower() or 'turbine' in o.name.lower()):
        out.write('M|'+o.name+'|'+str(tuple(round(v,2) for v in o.matrix_world.translation))+'|'+str(o.hide_render)+'\n')
out.close()
