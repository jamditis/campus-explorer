import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['KX_drive_apron (UNVERIFIED depth/finish)','KY_rhd_drive_side_walk_fill (photo: paved; UNVERIFIED widths)','LH_college_ave_gutter_asphalt_fill (green drape strip by the cu','WS68_RHD_ground_northDTM (north grid_1m dtm_filled; NJ 2020 ort','eu_rhd_ground_slab','KY_college_ave_carriageway_asphalt (OSM centreline + kx curb; s','ce_rhd_retaining_wall (grade from LiDAR; wall finish UNVERIFIED']
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if any(n.startswith(k[:40]) for k in names)]
for o in b.objects:
    me=o.data; m=o.matrix_world; V=np.array([(m@v.co)[:] for v in me.vertices])
    sel=(V[:,0]>-280)&(V[:,0]<-258)&(V[:,1]>-54)&(V[:,1]<-36)
    print('OBJ',o.name[:60],len(V),[(mm.type,mm.name) for mm in o.modifiers],[x.name for x in me.materials])
    if sel.sum():
        W=V[sel]
        for yb in range(-54,-36,2):
            s=(W[:,1]>=yb)&(W[:,1]<yb+2)
            if s.sum(): print('   y',yb,'n',s.sum(),'x',round(W[s,0].min(),1),round(W[s,0].max(),1),'z',round(W[s,2].min(),2),round(W[s,2].max(),2))
