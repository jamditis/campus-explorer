# ws166b: UNIFY #66 W shoulder N of y -199 — Lot 3's W curb (WEDGE y -199..-171.5) has no ground W of it: lot reads as a platform over the skirt.
# Evidence: 2023 LiDAR class-2 DTM (scripts/ws162/dtm162.npy) — from the curb (~118.0) a grass bank (intensity 6-8k) drops ~2.3 m over 5-6 m
# (about 1:2.3) to a flat toe at ~115.65 (Sprague level); a dark (asphalt, int ~2k) strip runs at the toe ~8.5-10 m W of the curb (not built here).
# Build: lawn bank draped on DTM+0.02 from the curb back (start 2 cm under curb top) to t=8.0 m, last row at t=8.6 m dropping onto
# min(evaluated skirt, DTM)-0.03. No walk band N of y -199 (LiDAR shows grass right to the curb). Idempotent (removes WS166_ bank first).
import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
ZS=np.load('/workspace/nj-scenes/montclair-state/scripts/ws162/dtm162.npy')[1]; X0,Y1,R=-330.0,-165.0,0.5
def dz(x,y):
    fi=(x-X0)/R; fj=(Y1-y)/R
    i=int(min(max(math.floor(fi),0),ZS.shape[1]-2)); j=int(min(max(math.floor(fj),0),ZS.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(ZS[j,i]*(1-tx)*(1-ty)+ZS[j,i+1]*tx*(1-ty)+ZS[j+1,i]*(1-tx)*ty+ZS[j+1,i+1]*tx*ty)
for o in [o for o in OB if o.name.startswith('WS166_Lot3_W_shoulder')]: OB.remove(o)
LS=[(-300.2,-198.7),(-298.6,-190.0),(-297.4,-182.0),(-296.6,-176.0),(-296.4,-171.5)]
dg=bpy.context.evaluated_depsgraph_get(); skirt=OB.get('Context_skirt_3DEP_ortho_4km'); sk=None
if skirt:
    se=skirt.evaluated_get(dg); sme=se.to_mesh(); smw=skirt.matrix_world
    sk=BVHTree.FromPolygons([smw@v.co for v in sme.vertices],[p.vertices for p in sme.polygons]); se.to_mesh_clear()
def skz(x,y):
    if sk is None: return None
    h=sk.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
pts=[]
for k in range(len(LS)-1):
    a=np.array(LS[k],float); b=np.array(LS[k+1],float); n=max(1,int(math.ceil(np.linalg.norm(b-a)/0.75)))
    for s_ in range(n): pts.append(a+(b-a)*s_/n)
pts.append(np.array(LS[-1],float))
TS=[0.18,0.5,1.0,1.5,2.0,2.75,3.5,4.25,5.0,5.75,6.5,7.25,8.0]; bm=bmesh.new(); rows=[]; sk_lo=[]; sc=bpy.context.scene; hits={}
for k,p in enumerate(pts):
    q=pts[min(k+1,len(pts)-1)]-pts[max(k-1,0)]; d=q/np.linalg.norm(q); n=np.array([-d[1],d[0]]); r=[]
    zc=dz(*p)+0.04+0.12   # curb top (ws162: lz+0.12)
    for t in TS:
        x,y=p+n*t; zd=dz(x,y)+0.02; w=min(t/1.0,1.0); w=w*w*(3-2*w)
        z=min(zc-0.02, (zc-0.02)*(1-w)+zd*w) if t<1.0 else zd
        r.append(bm.verts.new((x,y,z)))
        if t==2.75:
            h=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
            if h[0]: hits[h[4].name[:40]]=hits.get(h[4].name[:40],0)+1
    x,y=p+n*8.6; zs=skz(x,y); zd=dz(x,y)
    z=(min(zs,zd)-0.03) if zs is not None else zd-0.3; sk_lo.append(None if zs is None else round(zd-zs,2))
    r.append(bm.verts.new((x,y,z))); rows.append(r)
for i in range(len(rows)-1):
    for j in range(len(rows[i])-1): bm.faces.new((rows[i][j],rows[i][j+1],rows[i+1][j+1],rows[i+1][j]))
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS166_Lot3_W_shoulder_bank_N_LiDAR2023_DTM'); bm.to_mesh(me); bm.free()
lm=bpy.data.materials.get('COLE_lawn_post2020_bs') or (OB.get('WS162_Lot3_W_shoulder_lawn_bank_to_skirt_UNVERIFIED').active_material)
me.materials.append(lm); uv=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    pp=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(pp.x*0.25,pp.y*0.25)
col=bpy.data.collections.get('WS162_Lot3_W_side') or bpy.context.scene.collection
ob=OB.new('WS166_Lot3_W_shoulder_bank_N_of_y-199_LiDAR2023_DTM_UNVERIFIEDtoe',me); col.objects.link(ob)
print('BANK166 rows',len(rows),'faces',len(me.polygons),'pre-existing top hits at t=2.75',hits,'DTM-skirt at toe (m)',[v for v in sk_lo[::4]],flush=True)
