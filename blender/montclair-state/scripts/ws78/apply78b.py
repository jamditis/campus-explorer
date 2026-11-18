# ws78b: fix spike verts left by ws78a (verts whose terrain ray missed -> delta 0): any vert in BOX that stands >0.12 m above ALL its edge neighbours gets the offline delta (delta_grid.npz, same formula as the GN) subtracted; iterate.
import bpy,numpy as np
from mathutils import Vector
G=np.load('/workspace/nj-scenes/montclair-state/scripts/ws78/delta_grid.npz'); xs,ys,DL=G['xs'],G['ys'],G['delta']
def dl(x,y):
    i=(x-xs[0])/0.25; j=(y-ys[0])/0.25; i0=int(np.clip(np.floor(i),0,len(xs)-2)); j0=int(np.clip(np.floor(j),0,len(ys)-2)); a=min(max(i-i0,0),1); b=min(max(j-j0,0),1)
    return float((DL[j0,i0]*(1-a)+DL[j0,i0+1]*a)*(1-b)+(DL[j0+1,i0]*(1-a)+DL[j0+1,i0+1]*a)*b)
BOX=(-258,-210,-132,-78)
OBJ=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS76_lot_','WS77_lot_median_island'))]
for o in OBJ:
    me=o.data; mw=o.matrix_world; mi=mw.inverted()
    nb=[[] for _ in me.vertices]
    for e in me.edges: a,b=e.vertices; nb[a].append(b); nb[b].append(a)
    fixed=set()
    for it in range(4):
        W=[mw@v.co for v in me.vertices]; n=0
        for i,p in enumerate(W):
            if i in fixed or not nb[i] or not (BOX[0]<p.x<BOX[1] and BOX[2]<p.y<BOX[3]): continue
            if p.z-max(W[k].z for k in nb[i])>0.12:
                d=dl(p.x,p.y)
                if d>0.1:
                    me.vertices[i].co=mi@Vector((p.x,p.y,p.z-d)); fixed.add(i); n+=1
        if n==0: break
    me.update(); print('WS78B spikes fixed',o.name[:45],len(fixed),flush=True)
