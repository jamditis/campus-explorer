import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    names=list(a.objects); mats=list(a.materials)
for n in names:
    if any(k in n.lower() for k in ('sprague','turf','field','stadium','lot36','ws185','ws181')): print('OBJ',n)
for m in mats:
    if any(k in m.lower() for k in ('turf','sprague','field','lawn')): print('MAT',m)
