import bpy
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (src,dst):
    n=src.objects
for x in n:
    if any(k in x.lower() for k in ('ws35','step','cole','arch','statue','median','ws87','ws88','ws77','terrain')): print('N89',x)
print('N89 total',len(n))
