# ws188 memory-safe merge: skirt_under_* GN off during load/fixes (load_post), restored before save. Peak ~2.9 GB vs 7.9 GB.
import bpy, os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws188/skirtoff188.py').read())
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
for f in os.environ['CHAIN'].split():
    exec(open('/workspace/nj-scenes/montclair-state/scripts/'+f).read())
w=bpy.data.worlds.get('WP2_World_GOLDEN')
if w and w.use_nodes:
    for nd in w.node_tree.nodes:
        if nd.type=='TEX_SKY': print('SKY188',nd.sky_type,getattr(nd,'sun_elevation',None),getattr(nd,'sun_rotation',None),flush=True)
restore()
o=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; print('SKIRT188 viewport on',sum(m.show_viewport for m in o.modifiers),'of',len(o.modifiers),flush=True)
hwm()
bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True); print('SAVED',flush=True)
