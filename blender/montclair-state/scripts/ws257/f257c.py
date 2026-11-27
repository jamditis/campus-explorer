# ws257c (UNIFY #10): WS110_ground_patch_S_of_y-238 ends on a hard edge at y -300 with the coarse 4 km 3DEP skirt up to 3.2 m BELOW it
# (probe257f/g: x -283..-176; worst x -215..-182, 2.9-3.2 m; skirt base mesh itself is that low, not a GN drop) = a cliff seen from the air.
# Fix: a lawn strip S of the edge (beyond the modelling edge: residential yards S of Normal Ave, houses not modelled, as WS172):
#   first 6 m follow the LiDAR class-2 DTM (prep/ws257_u10/dtm257.npy: 2023 J5D5 W of x -268, 2017 B17 J5D5/J5D6 E of it, shifted by the
#   overlap median -0.08 m), offset so the strip meets the patch edge exactly (offset fades out over 5 m); then a smoothstep grade down
#   to the skirt (+5 cm) out to L = 10 + 5*step m (10..28 m). The real ground stays ~121-122 m to y -325 (las257b ROW x -190) - the
#   skirt is ~3 m too low over the whole block, so the grade-down is a designed transition, not real terrain (UNVERIFIED by design);
#   alpha fade (WS172_lawn_fade_nostripe_WS175, 'fade172') on the last 2 m and over 3 m at the E/W ends, so it melts into the skirt.
#   Always >= skirt + 5 cm (skirt sampled every 1 m, evaluated, edge257.json from probe257h). The N row tucks 0.5 m under WS110 at -4 cm.
# Columns only where the step is > 0.15 m and nothing else (sidewalk / lip / WS172) borders the edge. Grade beyond y -306 UNVERIFIED (design).
import bpy, bmesh, json, math, numpy as np
TAG='F257C'; MS='/workspace/nj-scenes/montclair-state/'; SN='WS257_UNIFY10_S_edge_feather_DTM2023_to_skirt_UNVERIFIED'
if SN in bpy.data.objects: raise SystemExit('already in main')
E=json.load(open(MS+'scripts/ws257/edge257.json'))
D=np.load(MS+'prep/ws257_u10/dtm257.npy')[0]; DX0,DY0,R=-290.0,-330.0,0.5
def dz(x,y):
    fi=(x-DX0)/R-0.5; fj=(y-DY0)/R-0.5
    i=int(min(max(math.floor(fi),0),D.shape[1]-2)); j=int(min(max(math.floor(fj),0),D.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty)
def ss(u): u=min(1.0,max(0.0,u)); return u*u*(3-2*u)
cols=sorted(float(k) for k,v in E.items() if v['ze'] is not None and v['sk'][0] is not None and v['ze']-v['sk'][0]>0.15 and not v['oth'])
# keep contiguous runs of columns >= 6 m wide
runs=[];cur=[]
for x in cols:
    if cur and x-cur[-1]>1.01: runs.append(cur); cur=[]
    cur.append(x)
if cur: runs.append(cur)
runs=[r for r in runs if len(r)>=6]
print(TAG,'runs',[(r[0],r[-1],len(r)) for r in runs],flush=True)
# ws257c2 (first test render: per-column integer L + raw 0.5 m DTM gave N-S ridges and a jagged outer outline): L is a float,
# smoothed over +-7 columns; the DTM part uses a 3 x 3 m mean; every column has the same rows (0..ceil(Lmax)); beyond its own L a
# column sits on the skirt + 5 cm with alpha 0; alpha ramps over the last 5 m before L and over 4 m at the E/W ends.
def dzs(x,y): return sum(dz(x+a,y+b) for a in (-1,0,1) for b in (-1,0,1))/9.0
bm=bmesh.new(); fl=bm.verts.layers.float.new('fade172'); G={}; nclamp=0; st=[]
for r in runs:
    stp=np.array([E[str(x)]['ze']-E[str(x)]['sk'][0] for x in r]); st+=list(stp)
    Lr=np.clip(10+5*stp,10,28); k=7; Lsm=np.array([Lr[max(0,i-k):i+k+1].mean() for i in range(len(r))])
    DM=int(math.ceil(Lsm.max()))
    for ci,x in enumerate(r):
        v=E[str(x)]; ye,ze,sk=v['ye'],v['ze'],v['sk']; L=float(Lsm[ci]); off0=(ze-0.02)-dzs(x,ye)
        endf=min(1.0,min(ci,len(r)-1-ci)/4.0)
        rows=[(-1,ye+0.5,ze-0.04,1.0)]
        for d in range(0,DM+1):
            y=ye-d; skd=(sk[d] if d<len(sk) and sk[d] is not None else sk[-1])
            zd=dzs(x,y)+off0*(1-ss(d/5.0)); w=ss((d-6.0)/(L-6.0)); z=(1-w)*zd+w*(skd+0.05)
            if z<skd+0.05: z=skd+0.05; nclamp+=1
            rows.append((d,y,z,min(1.0,max(0.0,(L-d)/5.0))))
        for d,y,z,f in rows:
            vv=bm.verts.new((x,y,z)); vv[fl]=f*endf; G[(x,d)]=vv
for r in runs:
    for x in r[:-1]:
        for d in range(-1,40):
            q=[(x,d),(x+1.0,d),(x+1.0,d+1),(x,d+1)]
            if all(kk in G for kk in q): bm.faces.new([G[kk] for kk in q])
for vv in [vv for vv in bm.verts if not vv.link_faces]: bm.verts.remove(vv)
bm.normal_update()
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new(SN); bm.to_mesh(me); bm.free()
mat=bpy.data.materials.get('WS172_lawn_fade_nostripe_WS175')  # = the WS172 front-yard lawn (same 'fade172' alpha)
me.materials.append(mat)
uv=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*0.25,p.y*0.25)
p110=bpy.data.objects['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED']
o=bpy.data.objects.new(SN,me); p110.users_collection[0].objects.link(o)
print(TAG,'made',SN,'verts',len(me.vertices),'faces',len(me.polygons),'step max %.2f'%max(st),'clamped to skirt',nclamp,'mats',[m.name for m in me.materials if m],flush=True)
