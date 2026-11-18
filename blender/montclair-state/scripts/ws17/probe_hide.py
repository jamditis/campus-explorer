import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws17/crop_render.py').read().split("sc.render.filepath")[0])
for tag,name in [('nogutter','Gutters half-round (3f, Life/CCOM UNVERIFIED)'),('nobarrel','Morehead Hall barrel tile eave course')]:
    for n in ('Gutters half-round (3f, Life/CCOM UNVERIFIED)','Morehead Hall barrel tile eave course'): bpy.data.objects[n].hide_render=(n==name)
    sc.render.filepath=f'/workspace/nj-scenes/montclair-state/renders/wip/20261110-0148_ws17_probe_{tag}.jpg'
    bpy.ops.render.render(write_still=True); print('WROTE',tag,flush=True)
o=bpy.data.objects['Gutters half-round (3f, Life/CCOM UNVERIFIED)']; print('GUT',o.type,[s.material.name for s in o.material_slots if s.material])
