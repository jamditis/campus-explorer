import bpy,os
for f in ('montclair_state.blend','north/montclair_north.blend'):
    with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/'+f) as (a,b):
        print('LS256',f,[n for n in a.objects if 'olice' in n or n.startswith(('ge_','gf_police','fp_'))][:40],flush=True)
os._exit(0)
