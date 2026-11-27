# ws260c = f260b + (c) the WS60 apron (its base mesh sits above its evaluated surface) is no longer a blend/clamp neighbour: overlap
# cells under it follow LiDAR - 4 cm (ws260b raised a 0.5 m hump over Panzer's E wall foot); (d) tint ramp: ws247_lawn = clip((1.7 - lum)/0.6)
# (ws260b's lum < 1.02 cut missed the bluish Panzer shadow, lum ~1.0-1.6; pale paving texels >= 1.7 keep the ortho).
# ws260b = f260a + (a) box y -239..-203 aligned with the evaluated probe grid (probe260c/eval260c.json) and its remaining evaluated
# holes (0.5 m sliver S of the WS60 apron at y -204.5, 2-3 cells at x -248, y -214) added to the hole set; (b) W63g-style shadow
# tint: patch verts whose 2020-ortho texel is shadow-dark (RGB sum < 1.02, Panzer's shadow) get ws247_lawn = 1 (1-ring 0.5).
# ws260 (CHAIN via ws208/merge208.py on main ws259b): UNIFY W64 — 2023 LiDAR ground patch for the hole W of the WS103 College Ave
# S-leg W walk (between it and Panzer's S gym / E block, y -238.5 .. -204.5). Before: only the 4 km skirt, 2.2-2.4 m under the walk.
# The 2020 ortho shows a planted bank (grass + shrubs) here; 2023 class-2 LiDAR (prep/ws259_w64/dtm259.npy, 1 m, box only): verge
# level with the walk, bank down to a flat ~118.6-118.9 m along Panzer. Patch = 0.5 m grid on the LiDAR (bilinear), only over cells no
# other ground/walk/building covers (base-mesh BVH rays, as probe260a), plus a 0.5 m overlap tucked 4 cm under the neighbours, with a
# 1.5 m blend to the neighbour edge height (no lip, no gap) and 0.4 m down-skirts on the outer edges. Joined into Terrain_LiDAR_DTM_1m
# by GN WS260_W64_LiDAR_patch_join_terrain right after WS250_W63_LiDAR_patch_join_terrain (same as ws250), so terrain material/'ortho'
# UV (affine fit to Terrain's own UVs nearby). Ground cover = ortho texture; shrubs not modelled (UNVERIFIED species/extent).
import bpy, json, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F260C'; PN='WS260_W64_CollegeAveS_W_bank_LiDAR2023_ground_patch'; MN='WS260_W64_LiDAR_patch_join_terrain'
MS='/workspace/nj-scenes/montclair-state/'
if PN in bpy.data.objects: raise SystemExit('already in main')
D=np.load(MS+'prep/ws259_w64/dtm259.npy')[0]; DX0,DY0=-292.0,-246.0
def lid(x,y):
    fi=x-DX0-0.5; fj=y-DY0-0.5; i=int(min(max(math.floor(fi),0),D.shape[1]-2)); j=int(min(max(math.floor(fj),0),D.shape[0]-2))
    tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty)
X0,X1,Y0,Y1=-266.0,-242.0,-239.0,-203.0; R=0.5; NX=int((X1-X0)/R); NY=int((Y1-Y0)/R)
SKIP=('T_','TREE','Context_skirt','Context_ground_beyond','Roof_vent','el roof','WS259_UNIFY6')
objs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name.startswith(SKIP) or o.hide_render: continue
    mw=o.matrix_world; bb=[mw@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0-1 or min(v.x for v in bb)>X1+1 or max(v.y for v in bb)<Y0-1 or min(v.y for v in bb)>Y1+1: continue
    V=[mw@v.co for v in o.data.vertices]; P=[]
    for p in o.data.polygons:
        vs=[V[i] for i in p.vertices]
        if max(v.x for v in vs)<X0-1 or min(v.x for v in vs)>X1+1 or max(v.y for v in vs)<Y0-1 or min(v.y for v in vs)>Y1+1: continue
        P.append(tuple(p.vertices))
    if P: objs.append((o.name,BVHTree.FromPolygons(V,P),o.name.startswith(('WS160','WS161'))))
def hit(x,y):
    best=None
    for n,t,bld in objs:
        h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if h[0] is None: continue
        if bld: return ('B',None)
        if best is None or h[0].z>best[1]: best=(n,h[0].z)
    return best
# cell classes: hole (None), building ('B'), ground/walk neighbour (name,z top)
CL={}
for j in range(NY):
    for i in range(NX):
        CL[(i,j)]=hit(X0+(i+0.5)*R,Y0+(j+0.5)*R)
hole={k for k,v in CL.items() if v is None}
EV=json.load(open(MS+'scripts/ws260/eval260c.json'))['top']
evh={tuple(map(int,k.split(','))) for k,v in EV.items() if v is None}
evh={k for k in evh if k in CL and (CL[k] is None or CL[k][0]!='B')}
print(TAG,'eval holes',len(evh),'new',len(evh-hole),flush=True); hole|=evh
# keep only the main connected hole region(s) >= 20 m2 (ignore pinholes between meshes)
seen=set(); keep=set()
for k in hole:
    if k in seen: continue
    st=[k]; comp=[]; seen.add(k)
    while st:
        c=st.pop(); comp.append(c)
        for d in ((1,0),(-1,0),(0,1),(0,-1)):
            n=(c[0]+d[0],c[1]+d[1])
            if n in hole and n not in seen: seen.add(n); st.append(n)
    if len(comp)*R*R>=20 or any(c in evh for c in comp): keep|=set(comp)
    print(TAG,'hole comp',len(comp)*R*R,'m2',flush=True)
cells=set(keep)
for (i,j) in keep:
    for di in (-1,0,1):
        for dj in (-1,0,1):
            n=(i+di,j+dj)
            if n in CL and n not in keep: cells.add(n)
# neighbour edge samples for the blend: (x,y,z_top) of covered ground cells bordering the hole
nb=[(X0+(i+0.5)*R,Y0+(j+0.5)*R,CL[(i,j)][1]) for (i,j) in cells if (i,j) not in keep and CL[(i,j)] and CL[(i,j)][0]!='B' and not CL[(i,j)][0].startswith('WS60')]
NB=np.array(nb) if nb else np.zeros((0,3))
print(TAG,'objs',len(objs),'hole m2',len(keep)*R*R,'patch cells',len(cells),'nb samples',len(nb),flush=True)
def zat(x,y):
    zl=lid(x,y)
    if len(NB)==0: return zl,9
    d2=(NB[:,0]-x)**2+(NB[:,1]-y)**2; k=int(np.argmin(d2)); d=math.sqrt(d2[k])
    w=d<0.9
    # inverse-distance mean of neighbour tops within 1.2 m
    m=d2<1.44
    zn=float((NB[m,2]/(d2[m]+0.05)).sum()/(1/(d2[m]+0.05)).sum()) if m.any() else float(NB[k,2])
    u=min(1.0,max(0.0,(d-0.25)/1.5)); s=u*u*(3-2*u)
    return (1-s)*(zn-0.04)+s*zl, d
VI={}; verts=[]; faces=[]; nclamp=0; dmax=0
def vid(i,j):
    global nclamp
    if (i,j) not in VI:
        x=X0+i*R; y=Y0+j*R; z,d=zat(x,y)
        VI[(i,j)]=len(verts); verts.append((x,y,z))
    return VI[(i,j)]
for (i,j) in sorted(cells):
    faces.append((vid(i,j),vid(i+1,j),vid(i+1,j+1),vid(i,j+1)))
# covered-neighbour overlap cells must stay under the neighbour: clamp their verts to top-0.04
for (i,j) in cells:
    if (i,j) in keep or not CL[(i,j)] or CL[(i,j)][0]=='B': continue
    zt=CL[(i,j)][1]-0.04
    if CL[(i,j)][0].startswith('WS60'):
        for k in ((i,j),(i+1,j),(i+1,j+1),(i,j+1)):
            v=verts[VI[k]]; verts[VI[k]]=(v[0],v[1],min(v[2],lid(v[0],v[1])-0.04)); nclamp+=1
        continue
    for k in ((i,j),(i+1,j),(i+1,j+1),(i,j+1)):
        v=verts[VI[k]]
        if v[2]>zt: verts[VI[k]]=(v[0],v[1],zt); nclamp+=1
# outer boundary down-skirts 0.4 m
from collections import Counter
ec=Counter()
for f in faces:
    for a in range(4): ec[tuple(sorted((f[a],f[(a+1)%4])))]+=1
ns=0
for f in list(faces):
    for a in range(4):
        e=(f[a],f[(a+1)%4])
        if ec[tuple(sorted(e))]==1:
            p,q=verts[e[0]],verts[e[1]]
            i0=len(verts); verts.append((p[0],p[1],p[2]-0.4)); verts.append((q[0],q[1],q[2]-0.4))
            faces.append((e[1],e[0],i0,i0+1)); ns+=1
me=bpy.data.meshes.new(PN); me.from_pydata(verts,[],faces); me.validate(); me.update()
for p in me.polygons: p.use_smooth=True
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.data; tw=T.matrix_world
# material slot + 'ortho' UV affine fit from Terrain's own loops nearby
uvn='ortho' if 'ortho' in tm.uv_layers else tm.uv_layers.active.name
tuv=tm.uv_layers[uvn].data; A=[];U=[]; mc=Counter()
for p in tm.polygons:
    c=tw@p.center
    if -250<c.x<-225 and -245<c.y<-195:
        mc[p.material_index]+=1
        for li in p.loop_indices:
            co=tw@tm.vertices[tm.loops[li].vertex_index].co; A.append((co.x,co.y,1.0)); U.append(tuple(tuv[li].uv))
A=np.array(A); U=np.array(U); coef,res,_,_=np.linalg.lstsq(A,U,rcond=None); resid=float(np.abs(A@coef-U).max())
ms=mc.most_common(1)[0][0]
me.materials.append(tm.materials[ms])
uv=me.uv_layers.new(name=uvn)
for lp in me.loops:
    co=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=tuple(np.array([co.x,co.y,1.0])@coef)
ref=bpy.data.objects['WS250_W63_lawn_LiDAR2023_ground_patch_1m']
o=bpy.data.objects.new(PN,me); o.hide_render=True; o.display_type='WIRE'
for c in ref.users_collection: c.objects.link(o)
zs=[v.co.z for v in me.vertices]
print(TAG,'patch',PN,'verts',len(me.vertices),'faces',len(me.polygons),'skirts',ns,'clamped',nclamp,'z %.2f..%.2f'%(min(zs),max(zs)),'mat',tm.materials[ms].name,'uv',uvn,'fit resid %.4f'%resid,flush=True)
ng=bpy.data.node_groups.new(MN,'GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=o; oi.transform_space='RELATIVE'
jn=N.new('GeometryNodeJoinGeometry'); L.new(oi.outputs['Geometry'],jn.inputs[0]); L.new(gi.outputs[0],jn.inputs[0]); L.new(jn.outputs[0],go.inputs[0])
m=T.modifiers.new(MN,'NODES'); m.node_group=ng; m.show_viewport=False  # merge208 restores Realtime via _OFF? -> handled below
names=[x.name for x in T.modifiers]; idx=names.index('WS250_W63_LiDAR_patch_join_terrain')+1
with bpy.context.temp_override(object=T): bpy.ops.object.modifier_move_to_index(modifier=MN,index=idx)
_OFF.append((T.name,MN))
print(TAG,'stack',[x.name for x in T.modifiers],flush=True)
json.dump({'hole':sorted(keep),'cells':len(cells),'X0':X0,'Y0':Y0,'R':R},open(MS+'scripts/ws260/cells260c.json','w'))

# (b) shadow tint (as ws255 f255d): ortho texel luminance per patch vertex
img=next(n.image for n in bpy.data.materials['Ground_ortho_grass'].node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'ortho' in n.image.name.lower())
w,h=img.size; px=np.empty(w*h*4,np.float32); img.pixels.foreach_get(px); px=px.reshape(h,w,4)
def col(u,v): return px[min(h-1,max(0,int(v*h))),min(w-1,max(0,int(u*w))),:3]
lum={}
for lp in me.loops: lum.setdefault(lp.vertex_index,[]).append(float(col(*uv.data[lp.index].uv).sum()))
L={v:float(np.mean(s)) for v,s in lum.items()}; vals=np.array(list(L.values()))
at=me.attributes.new('ws247_lawn','FLOAT','POINT'); f=np.zeros(len(me.vertices),np.float32)
for v,l in L.items(): f[v]=min(1.0,max(0.0,(1.7-l)/0.6))
dark={v for v in L if f[v]>=0.99}; ring=[v for v in L if 0<f[v]<0.99]
at.data.foreach_set('value',f); me.update(); del px
print(TAG,'lum p10 %.3f p50 %.3f p90 %.3f'%tuple(np.percentile(vals,[10,50,90])),'dark',len(dark),'ring',len(ring),'of',len(me.vertices),flush=True)
