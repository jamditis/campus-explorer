import bpy
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend', load_ui=False)
import numpy as np
for o in bpy.data.objects:
    if o.name.startswith(('WS72','WS214_WS69_N','WS214_N','bx2_rhd_se','LH_rhd_se_door','WS215')):
        me=o.data
        V=np.array([o.matrix_world@v.co for v in me.vertices]) if o.type=='MESH' else None
        print('Q216',o.name[:60],'hr',o.hide_render,'hv',o.hide_viewport,'cols',[c.name[:20] for c in o.users_collection],[ (c.hide_render) for c in o.users_collection],'mats',[m.name[:24] for m in me.materials if m] if o.type=='MESH' else '', 'bb', V.min(0).round(2).tolist() if V is not None and len(V) else '', V.max(0).round(2).tolist() if V is not None and len(V) else '','mods',[m.type for m in o.modifiers])
