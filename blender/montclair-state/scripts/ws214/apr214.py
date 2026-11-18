import bpy, numpy as np
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('KX_drive_apron','eu_rhd_ground_slab','LH_college_ave_gutter','KY_rhd_drive_side_walk_fill','KY_college_ave_carriageway','KX_','WS27_curb'))]
for o in b.objects:
    if o.type!='MESH': continue
    me=o.data; m=o.matrix_world; V=np.array([(m@v.co)[:] for v in me.vertices])
    sel=(V[:,0]>-282)&(V[:,0]<-256)&(V[:,1]>-56)&(V[:,1]<-30)
    if not sel.sum(): continue
    W=V[sel]; print('OBJ',o.name[:70],len(V),'sel',sel.sum(),'x',W[:,0].min().round(1),W[:,0].max().round(1),'y',W[:,1].min().round(1),W[:,1].max().round(1),'z',W[:,2].min().round(2),W[:,2].max().round(2),[x.name for x in me.materials if x][:3])
    if o.name.startswith(('KX_drive_apron','eu_rhd','LH_')):
        for yb in range(-56,-30,2):
            s=(W[:,1]>=yb)&(W[:,1]<yb+2)
            if s.sum(): print('   y',yb,'x',W[s,0].min().round(1),W[s,0].max().round(1),'z',W[s,2].min().round(2),W[s,2].max().round(2))
