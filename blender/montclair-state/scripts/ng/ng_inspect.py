import bpy, mathutils, json
out=[]
def bb(o):
    m=o.matrix_world; cs=[m@mathutils.Vector(c) for c in o.bound_box]
    return [round(min(c[i] for c in cs),2) for i in range(3)]+[round(max(c[i] for c in cs),2) for i in range(3)]
print("NOBJ",len(bpy.data.objects))
cols=[c.name for c in bpy.data.collections if 'CCOM' in c.name.upper() or 'ccom' in c.name]
for c in cols:
    col=bpy.data.collections[c]
    print("COL",c,len(col.objects),"hide_render",col.hide_render)
for o in bpy.data.objects:
    n=o.name
    if any(k in n.lower() for k in ['ccom_int','atrium','lounge','balcony','stair','1f','2f','corridor','ccom_floor','slab','entry','entrance']) and o.type=='MESH':
        try: b=bb(o)
        except: continue
        if -40<b[0]<80 and 0<b[1]<60 or True:
            print("OBJ",n,o.type,b,"hr",o.hide_render,"hv",o.hide_viewport,"col",[c.name for c in o.users_collection][:2])
