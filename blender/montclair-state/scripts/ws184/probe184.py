# ws184 probe: WS163_Lot3_aisle_S_drive geometry vs 2023 DTM 0.5 m (prep/ws181_lot36/dtm181_0p5m.npy)
import bpy, numpy as np
D=np.load('/workspace/nj-scenes/montclair-state/prep/ws181_lot36/dtm181_0p5m.npy')
def dtm(x,y):
    c=(x+355)/0.5; r=(y+200)/-0.5
    c0=int(np.floor(c)); r0=int(np.floor(r)); fx=c-c0; fy=r-r0
    if not (0<=c0<119 and 0<=r0<119): return float('nan')
    q=D[r0:r0+2,c0:c0+2]
    return float(q[0,0]*(1-fx)*(1-fy)+q[0,1]*fx*(1-fy)+q[1,0]*(1-fx)*fy+q[1,1]*fx*fy)
for o in bpy.data.objects:
    if not o.name.startswith(('WS163_Lot3_aisle_S_drive','WS181_Lot36','WS169c','WS162_Lot3_S_end_apron')): continue
    me=o.data; M=o.matrix_world
    W=np.array([tuple(M@v.co) for v in me.vertices])
    print('P184 OBJ',o.name,'mods',[m.type for m in o.modifiers],'v',len(W),'f',len(me.polygons),'bbox',W.min(0).round(2),W.max(0).round(2),'smooth',sum(p.use_smooth for p in me.polygons),flush=True)
    if 'aisle_S_drive' in o.name:
        dz=np.array([w[2]-dtm(w[0],w[1]) for w in W])
        ok=~np.isnan(dz); print('P184 drive dz vs DTM n',ok.sum(),'med %.3f min %.3f max %.3f p10 %.3f p90 %.3f'%(np.median(dz[ok]),dz[ok].min(),dz[ok].max(),np.percentile(dz[ok],10),np.percentile(dz[ok],90)),flush=True)
        for v,w,d in zip(me.vertices,W,dz):
            if -320<w[0]<-300 and -242<w[1]<-228: print('P184V %.2f %.2f %.3f dz %.3f'%(w[0],w[1],w[2],d))
        for p in me.polygons:
            c=M@p.center; n=(M.to_3x3()@p.normal).normalized()
            if -320<c.x<-300 and -242<c.y<-228: print('P184F %.2f %.2f %.3f nz %.3f area %.2f nv %d'%(c.x,c.y,c.z,n.z,p.area,len(p.vertices)))
