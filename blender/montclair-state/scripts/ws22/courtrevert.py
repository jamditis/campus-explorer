import bpy,os
o=bpy.data.objects['QG_north_strip_LiDAR_terrain_patch']; me=o.data
a=me.attributes['ws22_orig_mat']
for p in me.polygons: p.material_index=a.data[p.index].value
me.attributes.remove(a); me.update(); print('REVERTED')
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
O=Vector((34,124,139.4))
for tx,ty in [(30,117),(28,116.5),(26,116),(32,117.5),(24,115),(36,118),(30,119)]:
    d=(Vector((tx,ty,137.2))-O).normalized()
    hit,loc,n,i,ob,m=sc.ray_cast(dg,O,d)
    if hit:
        oe=ob.evaluated_get(dg); pm=oe.data.polygons[i].material_index if hasattr(oe.data,'polygons') and i<len(oe.data.polygons) else -1
        print('HIT',(tx,ty),ob.name,[round(x,2) for x in loc],round(n.z,3),ob.material_slots[pm].material.name if pm>=0 and ob.material_slots else None)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
