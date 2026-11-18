import bpy, numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
W=('WS162_Lot3_S_end_apron_feather_UNVERIFIED','WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED','WS162_Lot3_W_curb_LiDAR2023_concrete_band_UNVERIFIEDsection','WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED')
with bpy.data.libraries.load(p) as (a,b): b.objects=[n for n in a.objects if n in W]
D=np.load('/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/dtm163.npy')[0]
def dz(x,y):
    i=int((x+350)/0.5); j=int((y+290)/0.5); s=D[max(j-1,0):j+2,max(i-1,0):i+2]; return float(np.nanmedian(s)) if np.isfinite(s).any() else float('nan')
for o in b.objects:
    print('##',o.name,len(o.data.vertices),len(o.data.polygons), [m.name for m in o.data.materials][:3], 'mods',[m.type for m in o.modifiers])
    for v in o.data.vertices:
        w=o.matrix_world@v.co
        if -320<w.x<-294 and -242<w.y<-226:
            d=w.z-dz(w.x,w.y)
            if abs(d)>0.12 or o.name.startswith('WS162_Lot3_S'): print('V %.2f %.2f %.2f dz %+.2f'%(w.x,w.y,w.z,d))
