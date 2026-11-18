import bpy, numpy as np, math
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS162','WS163','WS164','WS165','WS166','WS167','WS169','WS110')) and 'skirt' not in n]
D=np.load('/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/dtm163.npy')[0]
def dz(x,y):
    i=int((x+350)/0.5); j=int((y+290)/0.5); s=D[max(j-1,0):j+2,max(i-1,0):i+2]; return float(np.nanmedian(s)) if np.isfinite(s).any() else float('nan')
for o in b.objects:
    if o is None or o.type!='MESH': continue
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    n=[v for v in vs if -320<v.x<-294 and -242<v.y<-226]
    if not n: continue
    d=np.array([v.z-dz(v.x,v.y) for v in n]); d=d[np.isfinite(d)]
    print('O %-62s n%4d  dz p5 %+.2f p50 %+.2f p95 %+.2f  x %.1f..%.1f y %.1f..%.1f'%(o.name[:62],len(n),*np.percentile(d,[5,50,95]),min(v.x for v in n),max(v.x for v in n),min(v.y for v in n),max(v.y for v in n)),flush=True)
