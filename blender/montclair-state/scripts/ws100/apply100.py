import bpy, numpy as np, os, json
from mathutils import Vector
B='/workspace/nj-scenes/montclair-state/scripts/ws100/'
f=np.load(B+'field100b.npz'); F=f['F']; FX,FY,FR=float(f['X0']),float(f['Y0']),float(f['R'])
l=np.load(B+'lidar100.npz'); L=l['G']; LX,LY,LR=float(l['X0']),float(l['Y0']),float(l['R'])
def field(xy):
    fx=(xy[:,0]-FX)/FR; fy=(xy[:,1]-FY)/FR
    i0=np.clip(np.floor(fx).astype(int),0,F.shape[1]-2); j0=np.clip(np.floor(fy).astype(int),0,F.shape[0]-2)
    tx=np.clip(fx-i0,0,1); ty=np.clip(fy-j0,0,1)
    return (F[j0,i0]*(1-tx)*(1-ty)+F[j0,i0+1]*tx*(1-ty)+F[j0+1,i0]*(1-tx)*ty+F[j0+1,i0+1]*tx*ty)
def lid(xy):
    i=((xy[:,0]-LX)/LR).astype(int); j=((xy[:,1]-LY)/LR).astype(int)
    ok=(i>=0)&(i<L.shape[1])&(j>=0)&(j<L.shape[0]); out=np.full(len(xy),np.nan)
    out[ok]=L[j[ok],i[ok]]; return out
EXCL=('Alexander Kasser','Susan A. Cole','Cole Hall','TW_','TZ_','UE_','UF_','Terrain_LiDAR_DTM_1m_hidden')
SAVE=os.environ.get('SAVE')=='1'
OK_MODS={'SOLIDIFY','BEVEL','WEIGHTED_NORMAL','EDGE_SPLIT','TRIANGULATE','SUBSURF'}
rep=[]
CLAMP=('COLE_plaza','WS67_','WS78_')
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith(EXCL): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<-217.5 or min(xs)>-185.5 or max(ys)<-119.5 or min(ys)>-61: continue
    me=o.data; n=len(me.vertices)
    if n==0: continue
    co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); W=co@M[:3,:3].T+M[:3,3]
    dz=field(W[:,:2]); act=dz>0.01
    if not act.any(): continue
    dl=W[act,2]-lid(W[act,:2])
    mods=[m.type for m in o.modifiers]
    small=max(max(xs)-min(xs),max(ys)-min(ys))<4
    r=dict(n=o.name[:70],nv=int(act.sum()),dz_med=round(float(np.median(dz[act])),2),dz_max=round(float(dz.max()),2),
           model_minus_lidar=round(float(np.nanmedian(dl)),2) if np.isfinite(dl).any() else None,mods=mods,users=me.users,parent=bool(o.parent),small=small)
    action='skip'
    if o.parent: action='skip_parent'
    elif small and not me.users>1: action='move_loc' 
    elif small and me.users>1: action='move_loc'
    elif me.users>1: action='move_loc'
    elif o.name.startswith('Terrain_LiDAR_DTM_1m'): action='verts_clamp'; print('A100 TERRMODS',[m.name for m in o.modifiers])
    elif any(m not in OK_MODS for m in mods): action='skip_mods'
    elif o.name.startswith(CLAMP): action='verts_clamp'
    else: action='verts'
    r['action']=action; rep.append(r)
    if not SAVE: continue
    if action=='move_loc':
        c=np.array(o.matrix_world.translation)[None,:2]; o.matrix_world.translation.z+=float(field(c)[0])
    elif action in ('verts','verts_clamp'):
        if action=='verts_clamp':
            lz=lid(W[:,:2]); cap=np.where(np.isfinite(lz),np.clip(lz+0.05-W[:,2],0,None),0.0); dz=np.minimum(dz,cap)
        W[:,2]+=dz; Mi=np.linalg.inv(M); L2=W@Mi[:3,:3].T+Mi[:3,3]
        me.vertices.foreach_set('co',L2.ravel()); me.update()
for r in rep: print('A100',json.dumps(r))
json.dump(rep,open(B+('applied100.json' if SAVE else 'dry100.json'),'w'),indent=0)
if SAVE: bpy.ops.wm.save_mainfile(); print('A100 SAVED')
