# ws248: objects over the patch box: does their base sit on the new LiDAR ground? (old fan ground was -1..+2.2 m off)
import bpy, os, sys, json, numpy as np, warnings; warnings.filterwarnings('ignore')
S='/workspace/nj-scenes/montclair-state/scripts/'
BB=json.load(open(S+'ws205/bbox205.json')); box=(-226,-186,44,136)
want=[n for n,v in BB.items() if v[0] in('MESH','CURVE') and not (v[3]<box[0] or v[2]>box[1] or v[5]<box[2] or v[4]>box[3])]
want+=json.load(open(S+'ws248/extra248_small.json')); want=list(dict.fromkeys(want))
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state_ws248e.blend') as (a,b): have=set(a.objects); b.objects=[n for n in want if n in have]
G23=np.load(S+'ws248/g1m_23.npy'); G17=np.load(S+'ws248/g1m_17.npy'); G=np.where(np.isfinite(G23),G23,G17)
def gz(x,y):
    i=int(x+320); j=int(y+20); q=G[j-1:j+2,i-1:i+2]; return float(np.nanmedian(q)) if np.isfinite(q).any() else np.nan
for o in b.objects:
    if o is None or o.type!='MESH' or o.name.startswith(('Terrain_LiDAR','WS248_E','Context_skirt')): continue
    M=np.array(o.matrix_world); co=np.empty(len(o.data.vertices)*3); o.data.vertices.foreach_get('co',co); co=co.reshape(-1,3)@M[:3,:3].T+M[:3,3]
    m=(co[:,0]>box[0])&(co[:,0]<box[1])&(co[:,1]>box[2])&(co[:,1]<box[3])
    if m.sum()==0: continue
    c=co[m]; 
    # per 1 m cell: lowest vertex vs ground
    cells={}
    for v in c:
        k=(int(v[0]),int(v[1])); cells[k]=min(cells.get(k,1e9),v[2])
    d=np.array([z-gz(k[0]+0.5,k[1]+0.5) for k,z in cells.items()]); d=d[np.isfinite(d)]
    if len(d)==0: continue
    print('O248 %-60s verts %6d cells %5d base-ground min %.2f med %.2f max %.2f'%(o.name[:60],m.sum(),len(cells),d.min(),np.median(d),d.max()),flush=True)
sys.stdout.flush(); os._exit(0)
