import bpy,numpy as np
I=bpy.data.objects['WS196_lot_accessible_ISA_symbol_paint_UNVERIFIED']; mw=I.matrix_world
W=np.array([tuple(mw@v.co) for v in I.data.vertices]); n=len(W)//18
cen=W[:,:2].reshape(18,n,2).mean(1); t=cen[8]-cen[0]; t/=np.linalg.norm(t); up=np.array((-t[1],t[0]))
for s in (0,8,9,17):
    SB=W[s*n:(s+1)*n]; head=SB[:21,:2].mean(0); print('V197 sym',s,'head offset along north-up %.2f'%((head-SB[:,:2].mean(0))@up),'centre %.2f %.2f'%tuple(SB[:,:2].mean(0)),flush=True)
print('V197 skirt mods on',sum(m.show_viewport for m in bpy.data.objects['Context_skirt_3DEP_ortho_4km'].modifiers),flush=True)
