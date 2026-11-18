import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (src,dst):
    print("NOBJ",len(src.objects))
    print("FOOT",[o for o in src.objects if 'oot' in o])
    print("LOT",[o for o in src.objects if o.startswith(('WS74','WS75','WS76','WS79','WS80','WS81'))][:40])
