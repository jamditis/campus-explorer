import bpy,numpy as np
O=bpy.data.objects; D={}
for o in O:
    if o.type!='MESH' or o.hide_render: continue
    if not any(k in o.name for k in ('WS76','WS195','median','WS79_lot_E','WS196')): continue
    mw=o.matrix_world; P=np.array([tuple(mw@v.co) for v in o.data.vertices])
    if len(P)==0 or P[:,0].max()<-262 or P[:,0].min()>-212 or P[:,1].max()<-95 or P[:,1].min()>-60: continue
    D[o.name]=P; E=np.array([tuple(e.vertices) for e in o.data.edges]); D[o.name+'|E']=E
    print('P197b',o.name,len(P),[m.name for m in o.data.materials if m],flush=True)
np.savez('/tmp/p197b.npz',**D)
