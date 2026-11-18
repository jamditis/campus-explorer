# ws211b: delete the replaced draped paint (only after the ws211a mask render was verified)
import bpy
def _f211():
    for n in ('WS196_lot_accessible_ISA_symbol_paint_UNVERIFIED','WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED'):
        o=bpy.data.objects.get(n)
        if o: me=o.data; bpy.data.objects.remove(o); print('F211 deleted',n,flush=True)
_f211()
del _f211
