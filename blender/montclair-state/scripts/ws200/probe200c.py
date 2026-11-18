import bpy, numpy as np, os
for n in ('WS75_sprague_lot_asphalt','WS76_accessible_lot','WS77_lot_median'):
    o=[o for o in bpy.data.objects if o.name.startswith(n)][0]; mw=o.matrix_world
    P=np.array([tuple(mw@v.co) for v in o.data.vertices]); F=[list(p.vertices) for p in o.data.polygons]
    np.save(os.environ['OUT']+'_'+n[:4]+'.npy',P)
    print('P200c',o.name,len(P),len(F),P.min(0).round(2),P.max(0).round(2),[m.name for m in o.modifiers],flush=True)
