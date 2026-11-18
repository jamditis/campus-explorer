import bpy, numpy as np, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B='/workspace/nj-scenes/montclair-state/scripts/ws101/'
f=np.load(B+'field101.npz'); F=f['F']; FX,FY,FR=float(f['X0']),float(f['Y0']),float(f['R'])
l=np.load(B+'lidgrid101.npz'); LG=l['G']; LX,LY,LR=float(l['X0']),float(l['Y0']),float(l['R'])
def field(xy):
    fx=(xy[:,0]-FX)/FR; fy=(xy[:,1]-FY)/FR
    i0=np.clip(np.floor(fx).astype(int),0,F.shape[1]-2); j0=np.clip(np.floor(fy).astype(int),0,F.shape[0]-2)
    tx=np.clip(fx-i0,0,1); ty=np.clip(fy-j0,0,1)
    out=(F[j0,i0]*(1-tx)*(1-ty)+F[j0,i0+1]*tx*(1-ty)+F[j0+1,i0]*(1-tx)*ty+F[j0+1,i0+1]*tx*ty)
    inside=(fx>=0)&(fx<F.shape[1]-1)&(fy>=0)&(fy<F.shape[0]-1); return np.where(inside,out,0.0)
def lid(xy):
    i=np.round((xy[:,0]-LX)/LR).astype(int); j=np.round((xy[:,1]-LY)/LR).astype(int)
    ok=(i>=0)&(i<LG.shape[1])&(j>=0)&(j<LG.shape[0]); out=np.full(len(xy),np.nan); out[ok]=LG[j[ok],i[ok]]; return out
EXCL=('Terrain_LiDAR_DTM_1m_hidden','Context_','BD_','Roads_OSM','Footpaths_OSM','WS60_terrain_edge','WS48_band','WS68_RHD_ground','Roof_vent')
SAVE=os.environ.get('SAVE')=='1'
OK_MODS={'SOLIDIFY','BEVEL','WEIGHTED_NORMAL','EDGE_SPLIT','TRIANGULATE','SUBSURF'}
FULL=('WS27_CollegeAve','UA_CollegeAve','WS35_CollegeAve_bed')
rep=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith(EXCL): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<-262 or min(xs)>-185 or max(ys)<-205 or min(ys)>-105: continue
    me=o.data; n=len(me.vertices)
    if n==0: continue
    co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); W=co@M[:3,:3].T+M[:3,3]
    dz=field(W[:,:2]); act=dz>0.01
    if not act.any(): continue
    mods=[m.type for m in o.modifiers]; small=max(max(xs)-min(xs),max(ys)-min(ys))<4
    r=dict(n=o.name[:70],nv=int(act.sum()),dz_med=round(float(np.median(dz[act])),2),dz_max=round(float(dz.max()),2),mods=mods,users=me.users)
    if o.parent: action='skip_parent'
    elif small or me.users>1: action='move_loc'
    elif o.name=='Terrain_LiDAR_DTM_1m': action='verts_clamp'
    elif any(m not in OK_MODS for m in mods): action='skip_mods'
    elif o.name.startswith(FULL): action='verts'
    else: action='verts_clamp'
    r['action']=action; rep.append(r); print('A101',json.dumps(r))
    if action=='move_loc':
        c=np.array(o.matrix_world.translation)[None,:2]; lz=lid(c)[0]; d0=float(field(c)[0])
        if np.isfinite(lz): d0=min(d0,max(0.0,lz+0.05-o.matrix_world.translation.z))
        o.matrix_world.translation.z+=d0; r['moved']=round(d0,2)
    elif action in ('verts','verts_clamp'):
        if action=='verts_clamp':
            s=np.where(act)[0]; lz=np.full(n,np.nan); lz[s]=lid(W[s,:2])
            cap=np.where(np.isfinite(lz),np.clip(lz+0.05-W[:,2],0,None),0.0); dz=np.minimum(dz,cap)
        W[:,2]+=dz; Mi=np.linalg.inv(M); L2=W@Mi[:3,:3].T+Mi[:3,3]
        me.vertices.foreach_set('co',L2.ravel()); me.update()
# terrain cap 5 cm under paving (BVH, not scene.ray_cast)
PAVE=['WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED','UA_CollegeAve_spur_1557427669_UNVERIFIED']
PAVE+=[o.name for o in bpy.data.objects if o.name.startswith('WS98_') and o.type=='MESH']
tris=[];vs=[]
for nm in PAVE:
    o=bpy.data.objects.get(nm)
    if not o: continue
    mw=o.matrix_world; base=len(vs); vs+= [mw@v.co for v in o.data.vertices]
    for p in o.data.polygons: tris.append([base+i for i in p.vertices])
bvh=BVHTree.FromPolygons(vs,tris)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data; n=len(me.vertices)
co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3); M=np.array(t.matrix_world); W=co@M[:3,:3].T+M[:3,3]
sel=np.where(((W[:,0]>-262)&(W[:,0]<-185)&(W[:,1]>-205)&(W[:,1]<-105))|((W[:,0]>-221)&(W[:,0]<-200)&(W[:,1]>-90)&(W[:,1]<-68.6)))[0]; capped=0; mx=0
pushes=[]
for k in sel:
    best=None; center=False
    for off in ((0,0),(0.35,0),(-0.35,0),(0,0.35),(0,-0.35)):
        hit=bvh.ray_cast(Vector((W[k,0]+off[0],W[k,1]+off[1],W[k,2]+5)),Vector((0,0,-1)),12)
        if hit[0] is not None:
            if off==(0,0): center=True
            best=hit[0].z if best is None else min(best,hit[0].z)
    if best is not None and W[k,2]>best-0.05:
        pu=W[k,2]-(best-0.05)
        if not center and pu>0.2: continue
        pushes.append((round(float(W[k,0]),1),round(float(W[k,1]),1),round(float(pu),2),center))
        mx=max(mx,pu); W[k,2]=best-0.05; capped+=1
big=[p for p in pushes if p[2]>0.3]; print('A101 bigpush',len(big),big[:12]); aisle=[p for p in pushes if p[1]>-90]; print('A101 aislecap',len(aisle),max([p[2] for p in aisle] or [0]))
Mi=np.linalg.inv(M); me.vertices.foreach_set('co',(W@Mi[:3,:3].T+Mi[:3,3]).ravel()); me.update()
print('A101 terrain capped',capped,'max push %.2f'%mx)
json.dump(rep,open(B+('applied101.json' if SAVE else 'dry101.json'),'w'),indent=0)
if SAVE: bpy.ops.wm.save_mainfile(); print('A101 SAVED')
