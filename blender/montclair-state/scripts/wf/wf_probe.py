# wf probe: what surface ray-hits under TL trees / Bohn N stair / W walk; Terrain vs skirt coverage in box
import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1=50.,300.,320.,520.
SK=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
T=bpy.data.objects.get('Terrain_LiDAR_DTM_1m')
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); vs=[o.matrix_world@v.co for v in m.vertices]; fs=[tuple(p.vertices) for p in m.polygons]; e.to_mesh_clear()
    return BVHTree.FromPolygons(vs,fs), vs
bsk,_=bvh(SK)
bt=None; tmax=None
if T:
    bt,tvs=bvh(T)
    arr=np.array([(v.x,v.y,v.z) for v in tvs])
    # coverage in box
    m=(arr[:,0]>=X0)&(arr[:,0]<X1)&(arr[:,1]>=Y0)&(arr[:,1]<Y1)
    tmax=dict(n_in_box=int(m.sum()), xmax=float(arr[:,0].max()), ymax=float(arr[:,1].max()),
              xmin=float(arr[:,0].min()), ymin=float(arr[:,1].min()),
              box_xmax=float(arr[m,0].max()) if m.any() else None,
              box_ymax=float(arr[m,1].max()) if m.any() else None,
              box_xmin=float(arr[m,0].min()) if m.any() else None,
              box_ymin=float(arr[m,1].min()) if m.any() else None)
print('TERRAIN',tmax)

# sample grid of ground hits
samples=[]
for x in range(60,300,20):
    for y in range(330,520,20):
        hs=[]; names=[]
        for nm,b in [('skirt',bsk),('terrain',bt)]:
            if b is None: continue
            h=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if h[0] is not None:
                hs.append(round(h[0].z,3)); names.append(nm)
        samples.append(dict(x=x,y=y,hits=list(zip(names,hs)), top=names[0] if names else None, topz=hs[0] if hs else None))
# count who wins
from collections import Counter
c=Counter(s['top'] for s in samples)
print('TOP_SURFACE',dict(c),'n',len(samples))

# TL trees in box
trees=[]
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree') or o.type!='MESH': continue
    p=o.matrix_world.translation
    if not(X0<=p.x<X1 and Y0<=p.y<Y1): continue
    mw=o.matrix_world
    P=[(mw@v.co).z for v in o.data.vertices if ((mw@v.co).xy-p.xy).length<0.3]
    tb=min(P) if P else p.z
    hs=[]
    for nm,b in [('skirt',bsk),('terrain',bt)]:
        if b is None: continue
        h=b.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))
        if h[0] is not None: hs.append((nm,round(h[0].z,3),round(tb-h[0].z,3)))
    trees.append(dict(n=o.name,x=round(p.x,2),y=round(p.y,2),tb=round(tb,3),hits=hs,we_dz=o.get('we_dz')))
print('TREES_IN_BOX',len(trees),'with we_dz',sum(1 for t in trees if t.get('we_dz') is not None))
off=[t for t in trees if t['hits'] and abs(t['hits'][0][2]+0.25)>0.15]
print('trees off sink>0.15',len(off))

# Bohn N stair / landing / W walk
wd=[]
for nm in sorted(bpy.data.objects.keys()):
    if not (nm.startswith('WD_') or nm.startswith('TK_Bohn_landing') or 'Bohn_N' in nm or '1132693523' in nm): continue
    o=bpy.data.objects[nm]
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    cx=sum(p.x for p in bb)/8; cy=sum(p.y for p in bb)/8; zmin=min(p.z for p in bb); zmax=max(p.z for p in bb)
    if not(X0-5<=cx<=X1+5 and Y0-5<=cy<=Y1+5): continue
    hs=[]
    for bnm,b in [('skirt',bsk),('terrain',bt)]:
        if b is None: continue
        h=b.ray_cast(Vector((cx,cy,400)),Vector((0,0,-1)))
        if h[0] is not None: hs.append((bnm,round(h[0].z,3),round(zmin-h[0].z,3)))
    wd.append(dict(n=nm,cx=round(cx,2),cy=round(cy,2),zmin=round(zmin,3),zmax=round(zmax,3),hits=hs,nverts=len(o.data.vertices)))
print('WD_OBJS',len(wd))
for w in wd[:30]: print(' ',w)

# DTM vs skirt at key points
D=np.load('data/wf/east_dorm_dtm_1m.npz')
filled=D['dtm_filled']; X0d,X1d,Y0d,Y1d,_=D['extent']
def dtm(x,y):
    i=int(np.floor(x-X0d)); j=int(np.floor(y-Y0d))
    if 0<=i<filled.shape[1]-1 and 0<=j<filled.shape[0]-1:
        # bilinear
        fx=x-X0d-i; fy=y-Y0d-j
        z00=filled[j,i]; z10=filled[j,i+1]; z01=filled[j+1,i]; z11=filled[j+1,i+1]
        return float((1-fx)*(1-fy)*z00+fx*(1-fy)*z10+(1-fx)*fy*z01+fx*fy*z11)
    return None
keypts=[(225,430,'Bohn_N_stair'),(212,405,'Bohn_W_door'),(250,400,'east_slope'),(180,380,'west_box'),
        (240,420,'N_landing_area'),(228.8,412.7,'stair_mid'),(222.8,413.8,'stair_top')]
cmp=[]
for x,y,lab in keypts:
    z=dtm(x,y)
    hs=[]
    for nm,b in [('skirt',bsk),('terrain',bt)]:
        if b is None: continue
        h=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        if h[0] is not None: hs.append((nm,round(h[0].z,3), round(z-h[0].z,3) if z else None))
    cmp.append(dict(lab=lab,x=x,y=y,dtm=round(z,3) if z else None, hits=hs))
    print('KEY',lab,cmp[-1])

# skirt modifiers (WD cut?)
mods=[(m.name,m.type) for m in SK.modifiers]
print('SKIRT_MODS',mods)

# grass points collections near box
grass=[]
for o in bpy.data.objects:
    if 'grass' not in o.name.lower() and 'Grass' not in o.name: continue
    if o.type not in ('MESH','POINTS'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(p.x for p in bb)<X0 or min(p.x for p in bb)>X1 or max(p.y for p in bb)<Y0 or min(p.y for p in bb)>Y1: continue
    grass.append(dict(n=o.name,t=o.type,nv=len(o.data.vertices) if o.type=='MESH' else -1))
print('GRASS',grass[:20],'n',len(grass))

# WD boolean cutter status
cut=bpy.data.objects.get('WD_skirt_cutter_Bohn_N_steps')
print('WD_cutter',cut.name if cut else None, 'hide',cut.hide_render if cut else None)

out=dict(terrain=tmax,top=dict(c),trees_n=len(trees),trees_off=len(off),wd=wd,keys=cmp,skirt_mods=mods,grass=grass)
json.dump(out,open('data/wf/probe.json','w'),indent=1)
json.dump(trees,open('data/wf/trees_in_box.json','w'),indent=1)
json.dump(samples,open('data/wf/ground_samples.json','w'),indent=1)
print('DONE')
