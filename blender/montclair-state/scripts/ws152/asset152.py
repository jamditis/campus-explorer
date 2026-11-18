import bpy
for o in list(bpy.data.objects):
    if not o.name.startswith('WS152_Freeman'): bpy.data.objects.remove(o)
for c in bpy.data.collections: c.asset_mark() if False else None
for o in bpy.data.objects:
    o.asset_mark(); o.asset_data.description='Freeman Hall (MSU) long-facade kit: cream modular brick piers framing red porcelain-enamel spandrel bays + grey aluminium ribbon-window grid, N stair glazing strip, white fascia. Layout N->S [3,6,6,6,3,5] columns from Wikimedia Commons File:MSU_Freeman_Hall.jpg (public domain) + Montclarion 2019 photo (reference only). Built in scene coords on OSM 312845860. UNVERIFIED dims. ws152.'
    o.asset_data.tags.new('Freeman'); o.asset_data.tags.new('facade'); o.asset_data.tags.new('ws152')
bpy.ops.outliner.orphans_purge(do_recursive=True)
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/assets/freeman_facade_ws152.blend')
print('ASSET SAVED',[o.name for o in bpy.data.objects])
