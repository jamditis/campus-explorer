import bpy, os
PRE=('WS138b_ground_fill','WS134_ground_patch','WS133b_ground_patch','WS163','WS110','WS172','WS173','WS174','WS175','WS166','WS170','WS113_paving_tops_proxy','UTIL170')
saved={}
for o in bpy.data.objects:
    saved[o.name]=o.hide_viewport
    if not o.name.startswith(PRE): o.hide_viewport=True
for c in bpy.data.collections: pass
print('LOWMEM hidden',sum(1 for o in bpy.data.objects if o.hide_viewport),'of',len(bpy.data.objects),flush=True)
for f in ('/workspace/nj-scenes/montclair-state/scripts/ws177/fix177.py','/workspace/nj-scenes/montclair-state/scripts/ws177/fix177b.py','/workspace/nj-scenes/montclair-state/scripts/ws177/fix177c.py','/workspace/nj-scenes/montclair-state/scripts/ws178/fix178.py'):
    exec(open(f).read())
for o in bpy.data.objects:
    if o.name in saved: o.hide_viewport=saved[o.name]
print('LOWMEM restored',sum(1 for o in bpy.data.objects if o.hide_viewport),flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUT'],copy=True,compress=True)
print('SAVED',flush=True)
