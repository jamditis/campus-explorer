import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws188/skirtoff188.py').read())
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
print('LOADED');hwm()
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
print('EVAL');hwm()
o=bpy.data.objects[SK].evaluated_get(dg); print('SKIRT faces eval',len(o.data.polygons))
restore(); print('restored (no eval)');hwm()
