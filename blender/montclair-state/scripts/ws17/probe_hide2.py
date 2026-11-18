import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws17/crop_render.py').read().split("sc.render.filepath")[0])
for tag,name in [('nosoffit','Morehead Hall eave soffit + fascia + rafter tails')]:
    bpy.data.objects[name].hide_render=True
    sc.render.filepath=f'/workspace/nj-scenes/montclair-state/renders/wip/20261110-0148_ws17_probe_{tag}.jpg'
    bpy.ops.render.render(write_still=True); print('WROTE',tag,flush=True)
