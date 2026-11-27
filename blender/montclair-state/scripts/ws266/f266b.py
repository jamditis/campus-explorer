# ws266 W68 (merge208 CHAIN): the "thin dark slit" at the Chapin W stair foot is an exposed pit of WS113 terrain fan fill
# (x -218.7...-216.9, y -200.35...-201.40, z 122.61-122.72) between the plaza E-corridor concrete (N, z 122.83-122.90) and the
# S-wing door apron (S, z 122.673): 6 cm below the apron, 15-25 cm below the corridor (probe266c, 5 cm BVH grid on the evaluated
# box meshes). Fill it with a concrete infill slab whose top is the Laplace (harmonic) interpolation of the surrounding paving tops,
# so the corridor ramps down to the apron with no pit. 1-cell overlap under the neighbours at their top - 5 mm (no visible seam).
# Real joint detail (ramp vs step) not documented in photos/ortho at this scale = UNVERIFIED; material = the apron's concrete.
import bpy, json, numpy as np
TAG='F266B'; NAME='WS266_Chapin_W_corridor_apron_infill_concrete_W68_UNVERIFIED'
if NAME in bpy.data.objects: raise SystemExit('F266B already applied')
R=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws266/eval266c.json')); N=240; S=0.05; X0=-224.0; Y0=-208.0
Z=np.full((N,N),np.nan); NM=np.empty((N,N),object)
for k,(x,y,h) in enumerate(R):
    j,i=divmod(k,N)
    if h: Z[j,i]=h[0][0]; NM[j,i]=h[0][1]
ij=lambda x,y:(int(round((y-Y0)/S)),int(round((x-X0)/S)))
ja,ia=ij(-218.95,-201.50); jb,ib=ij(-216.80,-200.25)
G=np.zeros((N,N),bool)
for j in range(ja,jb+1):
    for i in range(ia,ib+1):
        if NM[j,i] and NM[j,i].startswith('WS113_terrain_fan_fill'): G[j,i]=True
PAVE=('WS116_Chapin_W_plaza','WS120_Chapin_W_S_wing_door_apron','WS117_Chapin_W_entrance_stair_11R')
D=np.zeros_like(G)
for j in range(ja-1,jb+2):
    for i in range(ia-1,ib+2):
        if not G[j,i] and G[j-1:j+2,i-1:i+2].any() and NM[j,i] and NM[j,i].startswith(PAVE): D[j,i]=True
print(TAG,'pit cells',int(G.sum()),'boundary cells',int(D.sum()),'pit z %.3f..%.3f'%(np.nanmin(Z[G]),np.nanmax(Z[G])),flush=True)
# boundary value: stair cells use the plaza/apron z next to them (the stair top is a riser, not a floor)
B=Z.copy()
for j,i in zip(*np.where(D)):
    if NM[j,i].startswith('WS117'):
        nb=[Z[a,b] for a in range(j-2,j+3) for b in range(i-3,i+1) if NM[a,b] and NM[a,b].startswith(PAVE[:2])]
        B[j,i]=np.median(nb) if nb else np.nan
F=np.where(G,np.nanmean(B[D]),B)
for it in range(3000):
    Fn=F.copy()
    for j,i in zip(*np.where(G)):
        nb=[F[a,b] for a,b in ((j-1,i),(j+1,i),(j,i-1),(j,i+1)) if (G[a,b] or (D[a,b] and not np.isnan(B[a,b])))]
        if nb: Fn[j,i]=np.mean(nb)
    if np.nanmax(np.abs(Fn-F))<1e-5: break
    F=Fn
print(TAG,'laplace iters',it,'infill z %.3f..%.3f'%(F[G].min(),F[G].max()),'rise over pit %.3f'%(F[G].max()-np.nanmax(Z[G])),flush=True)
M=G|D; V={}; verts=[]; faces=[]
for j,i in zip(*np.where(M)):
    z=F[j,i] if G[j,i] else (B[j,i]-0.005 if not np.isnan(B[j,i]) else np.nan)
    if np.isnan(z): continue
    V[(j,i)]=len(verts); verts.append((X0+i*S,Y0+j*S,float(z)))
for (j,i) in list(V):
    q=[(j,i),(j,i+1),(j+1,i+1),(j+1,i)]
    if all(c in V for c in q) and any(G[c] for c in q): faces.append([V[c] for c in q])
me=bpy.data.meshes.new(NAME); me.from_pydata(verts,[],faces); me.update()
ref=bpy.data.objects['WS120_Chapin_W_S_wing_door_apron_concrete_plaza_level_UNIFY25_UNVERIFIED'] if 'WS120_Chapin_W_S_wing_door_apron_concrete_plaza_level_UNIFY25_UNVERIFIED' in bpy.data.objects else next(o for o in bpy.data.objects if o.name.startswith('WS120_Chapin_W_S_wing_door_apron'))
for m in ref.data.materials: me.materials.append(m)
ob=bpy.data.objects.new(NAME,me)
for c in ref.users_collection: c.objects.link(ob)
# planar UVs (1 m) so the concrete texture tiles like the apron
uv=me.uv_layers.new(name='UVMap')
for l in me.loops: v=me.vertices[l.vertex_index].co; uv.data[l.index].uv=(v.x,v.y)
for p in me.polygons: p.use_smooth=False
print(TAG,'built',NAME,'verts',len(verts),'faces',len(faces),'mat',[m.name for m in me.materials],'coll',[c.name for c in ref.users_collection],flush=True)
