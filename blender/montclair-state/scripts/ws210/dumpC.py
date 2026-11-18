import bpy, numpy as np
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (a,b): b.objects=['WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED']
for o in b.objects:
    mw=o.matrix_world; V=np.array([tuple(mw@v.co) for v in o.data.vertices]); np.save('/workspace/nj-scenes/montclair-state/scripts/ws210/C_%s.npy'%o.name[23:28],V)
    print('DC',o.name,len(V),flush=True)
