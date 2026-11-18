# ws125b: GN leaf-card source objects must be in the scene view layer for Object Info to evaluate; link them (hidden) into WS125 collection.
import bpy
col=bpy.data.collections['WS125_Chapin_W_bank_planting']
for n in ('Boxwood','Azalea','Yew'):
    l=bpy.data.objects['ShrubLeaf_'+n]
    if l.name not in col.objects: col.objects.link(l)
    l.hide_render=True; l.hide_viewport=True; l.location=(0,0,-500) if False else l.location
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
print('M125b inst',sum(1 for i in dg.object_instances if i.is_instance and i.parent and i.parent.name.startswith('WS125_bed_')))
bpy.ops.wm.save_mainfile(); print('M125b SAVED')
