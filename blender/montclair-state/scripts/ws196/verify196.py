import bpy
print('V196',[n for n in bpy.data.objects.keys() if 'accessible_symbol' in n or 'ISA' in n], len(bpy.data.objects['WS76_lot_stall_paint_blue_accessible_ortho2020_UNVERIFIED'].data.vertices), sum(m.show_viewport for m in bpy.data.objects['Context_skirt_3DEP_ortho_4km'].modifiers),flush=True)
