# ws230 W53j probe: QI / QH patch + WS60 apron verts vs dtm_1m and USGS 3DEP 1 m (fetched ws230), in the padded zones
import bpy,sys,json,numpy as np,collections
M='/workspace/nj-scenes/montclair-state/'
A=np.load(M+'data/dtm_1m.npy'); P=np.load(M+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy'); PAD=np.load(M+'scripts/ws230/pad_mask230.npy')
def bil(G,x,y,o):
    gx=x+o-0.5; gy=y+o-0.5; n=G.shape[0]; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(n-2,max(0,i)); j=min(n-2,max(0,j)); fx=min(1,max(0,fx)); fy=min(1,max(0,fy))
    return float(G[i,j]*(1-fx)*(1-fy)+G[i,j+1]*fx*(1-fy)+G[i+1,j]*(1-fx)*fy+G[i+1,j+1]*fx*fy)
NAMES=['QI_east_edge_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch','WS60_terrain_edge_apron_LiDAR_to_skirt']
with bpy.data.libraries.load(M+'montclair_state.blend',link=False) as (src,dst): dst.objects=[n for n in src.objects if n in NAMES]
out={}
for o in dst.objects:
    mw=o.matrix_world; vs=[mw@v.co for v in o.data.vertices]
    rows=[]
    for w in vs:
        if not(-280<w.x<280 and -280<w.y<280): continue
        dd=bil(A,w.x,w.y,250) if (-250<w.x<250 and -250<w.y<250) else None
        pp=bil(P,w.x,w.y,280); pad=bool(PAD[min(499,max(0,int(w.y+250))),min(499,max(0,int(w.x+250)))]) if dd is not None else None
        rows.append((w.x,w.y,w.z,dd,pp,pad))
    r=np.array([(a,b,c,d if d is not None else np.nan,e,1 if f else 0) for a,b,c,d,e,f in rows])
    dz3=r[:,2]-r[:,4]
    print('P230',o.name,'v',len(vs),'in',len(r),'z-3dep pct',np.percentile(dz3,[1,10,50,90,99]).round(2),'n>0.5',int((dz3>0.5).sum()),'n<-0.5',int((dz3<-0.5).sum()),flush=True)
    c=collections.Counter(); cm=collections.defaultdict(float)
    for x,y,z,d,e,f in r:
        if abs(z-e)>0.5:
            k=(int(x//20*20),int(y//20*20)); c[k]+=1; cm[k]=max(cm[k],round(z-e,1)) if z>e else min(cm[k],round(z-e,1))
    print('P230 cells',o.name,sorted([(k,c[k],cm[k]) for k in c])[:80],flush=True)
    np.save(M+'scripts/ws230/probe230a_%s.npy'%o.name[:4],r)
sys.stdout.flush(); import os; os._exit(0)
