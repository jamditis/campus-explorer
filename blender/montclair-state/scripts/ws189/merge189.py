# ws189 memory-safe merge v2: like ws188/merge188.py, but (a) evaluates the depsgraph while skirt_under is still OFF
# (clears tags from the fixes cheaply) and (b) restores skirt_under show_viewport by a DNA poke (poke189.py) instead of RNA,
# so save_as_mainfile does NOT re-evaluate the full skirt stack (that was a hidden ~6.5 GB spike at save in merge188).
import bpy, os
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws188/skirtoff188.py').read()); exec(open(S+'ws189/poke189.py').read())
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
for f in os.environ['CHAIN'].split():
    exec(open(S+f).read())
bpy.context.view_layer.update(); hwm()
poke_restore(); hwm()
bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True); hwm(); print('SAVED',flush=True)
