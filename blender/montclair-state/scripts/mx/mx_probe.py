import bpy, math
from mathutils import Vector
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36
for o in bpy.data.objects:
    if o.name.startswith(('CCOM_win_078','CCOM_win_079','CCOM_win_080','CCOM_win_081','CCOM_win_082')) or o.name.startswith('CCOM_win_07'):
        c=o.matrix_world.translation
        print("WIN",o.name,o.type,o.instance_collection.name if o.instance_collection else o.data.name if o.data else None,"hide",o.hide_render,"u %.2f t %.2f z %.2f"%(d.dot(c),n.dot(c)-C0,c.z),"rot %.2f"%math.degrees(o.matrix_world.to_euler().z), [round(x,2) for x in o.scale])
col=bpy.data.collections['MS_CCOM_newsroom_studio_20261029mw']
for o in col.objects: print("MW",o.name,len(o.data.polygons))
print("HIDDEN_N",len(bpy.context.scene.get('mw_hidden',[])))
# what's inside near SW corner: room objects starting dd_SOUTH
for o in bpy.data.objects:
    if o.name.startswith('dd_SOUTH') and not o.hide_render:
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]; c=sum(bb,Vector())/8
        u=d.dot(c); t=n.dot(c)-C0
        if u<-14 and t>-20: print("DDS",o.name,"u %.2f t %.2f z %.2f"%(u,t,c.z))
print("NOBJ",len(bpy.data.objects))
for o in bpy.data.objects:
    if 'monument' in o.name.lower() or ('sign' in o.name.lower() and 'CCOM' in o.name): print("SIGN",o.name,o.type,o.hide_render)
