import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
pre=('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill','WS79_lot_E_patch','WS81_lot_seam_underlay','WS94_lot_slit')
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in s.objects if n.startswith(pre)]
for o in d.objects: bpy.context.scene.collection.objects.link(o)
import os
if os.environ.get('BEFORE'): exec(open('/workspace/nj-scenes/montclair-state/scripts/ws94/probe_after94.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws94/seam94.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws94/seam94.py').read())
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws94/probe_after94.py').read())
