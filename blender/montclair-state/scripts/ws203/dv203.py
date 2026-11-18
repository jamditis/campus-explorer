import bpy, numpy as np
out={}
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith(('WS163_Lot3_aisle_S_drive','WS163_ground_patch_W_of_WS110','WS110_ground_patch_S','WS191c','WS170b','WS190b','WS192_Lot3','WS191b')):
        mw=o.matrix_world; P=np.array([tuple(mw@v.co) for v in o.data.vertices]); out[o.name[:12]]=P
        print('D203',o.name[:40],len(P),[s.material.name if s.material else None for s in o.material_slots][:3],flush=True)
np.savez('/workspace/nj-scenes/montclair-state/scripts/ws203/dv203.npz',**out)
