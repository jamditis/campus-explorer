# ws213b: delete the replaced draped white stall paint (only after the ws213a mask render was verified)
import bpy
o=bpy.data.objects.get('WS76_lot_stall_paint_white_ortho2020_UNVERIFIED')
if o: bpy.data.objects.remove(o); print('F213 deleted WS76_lot_stall_paint_white_ortho2020_UNVERIFIED',flush=True)
