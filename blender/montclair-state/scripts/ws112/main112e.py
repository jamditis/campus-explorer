import bpy
BK='/workspace/nj-scenes/montclair-state/montclair_state_pre_20261113ws112_c.blend'
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
with bpy.data.libraries.load(BK) as (src,dst): dst.objects=[n for n in src.objects if n.startswith('WS110_ground_patch')]
b=dst.objects[0]; cur=O('WS110_ground_patch'); nr=0
for vc,vb in zip(cur.data.vertices,b.data.vertices):
    if (vc.co-vb.co).length>1e-6: vc.co=vb.co.copy(); nr+=1
cur.data.update(); bpy.data.objects.remove(b,do_unlink=True); print('E112e restored patch',nr)
bpy.ops.wm.save_mainfile(); print('E112 SAVED')
