# ws249: build two 1 m LiDAR snap targets (JSON V/F/W, box only) from class-2 ground grids:
#  W  = soccer field W slope (PK_Feliciano_west_DTM_fill_UNVERIFIED was up to 3 m off; the slope line sat ~5 m east/west of the real one)
#       x -340..-282, y 92..216 from g1m_w23 (2023 J5D5+J5D6), 2017 fallback g1m_w17 if present
#  SE = SE berm corner of the east stand (ws248 residual) x -206..-172, y 40..74 from ws248 g1m_23 (2017 fallback)
# 3x3 nanmean, nan cells filled by iterative neighbour mean; weight = 1 in the core, linear 4 m feather to 0 at the box edge.
import numpy as np, json, os, sys
D='scripts/ws249/'
def nanmean3(G):
    P=np.pad(G,1,constant_values=np.nan); S=np.zeros_like(G); C=np.zeros_like(G)
    for dy in (0,1,2):
        for dx in (0,1,2):
            w=P[dy:dy+G.shape[0],dx:dx+G.shape[1]]; f=np.isfinite(w); S+=np.where(f,w,0); C+=f
    return np.where(C>0,S/np.maximum(C,1),np.nan)
def fill(G):
    G=G.copy()
    for _ in range(50):
        m=~np.isfinite(G)
        if not m.any(): break
        N=nanmean3(G); G[m]=N[m]
    return G
def build(G,X0,Y0,box,fe,name):
    x0,x1,y0,y1=box; xs=np.arange(x0,x1+0.01,1.0); ys=np.arange(y0,y1+0.01,1.0)
    H=fill(nanmean3(G))
    V=[];W=[]
    for y in ys:
        for x in xs:
            z=H[int(y-Y0) if y<Y0+H.shape[0] else -1, min(int(x-X0),H.shape[1]-1)]
            V.append((float(x),float(y),float(z)))
            e=min(x-x0,x1-x,y-y0,y1-y); W.append(float(np.clip(e/fe,0,1)))
    nx=len(xs); F=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(len(ys)-1) for i in range(nx-1)]
    json.dump({'V':V,'F':F,'W':W},open(D+name,'w')); print(name,len(V),len(F),'z %.2f..%.2f'%(min(v[2] for v in V),max(v[2] for v in V)))
Gw=np.load(D+'g1m_w23.npy')
if os.path.exists(D+'g1m_w17.npy'): Gw=np.where(np.isfinite(Gw),Gw,np.load(D+'g1m_w17.npy'))
build(Gw,-340.,-20.,(-340,-282,92,216),4.0,'t249w.json')
G23=np.load('scripts/ws248/g1m_23.npy'); G17=np.load('scripts/ws248/g1m_17.npy')
build(np.where(np.isfinite(G23),G23,G17),-320.,-20.,(-206,-172,40,74),4.0,'t249se.json')
