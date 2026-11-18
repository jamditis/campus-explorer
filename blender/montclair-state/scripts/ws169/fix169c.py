# ws169c: UNIFY #75 — the Context_skirt stood +0.55..+0.68 m above the 2023 LiDAR DTM in a sliver gap between the WS167 ground patch's slanted
# S edge (chord s=-34: y -232.4 at x -305 rising to ~-230 at x -320) and the WS163 ground patch (probe169: y -231.5, x -320..-312), plus a skirt
# pit (-0.29) at (-310,-234.5) -> the dark ridge/crease at the bank's S end. Fix: lawn bridge strip on the same DTM (prep/ws163_lot3S/dtm163.npy,
# as WS167) at DTM-0.025, chord s -37..-33.5, t 4.5..45 (lane/drive asphalt at DTM+0.03..0.05 stays on top), and the same faces appended to
# WS167_skirt_target_hidden so the WS167 skirt GN drop now reaches the gap. Idempotent (removes WS169c_ first; target faces tagged by attribute).
import bpy, bmesh, math, numpy as np
from mathutils import Vector
OB=bpy.data.objects
P='/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/'
D=np.load(P+'dtm163.npy')[0].copy(); X0,Y0,R=-350.0,-290.0,0.5
for j,i in zip(*np.nonzero(np.isnan(D))):
    if not (Y0+j*R>-245 and Y0+j*R<-220 and X0+i*R<-296): continue
    for rr in range(1,14):
        sub=D[max(j-rr,0):j+rr+1,max(i-rr,0):i+rr+1]
        if np.isfinite(sub).any(): D[j,i]=float(np.nanmedian(sub)); break
def dz(x,y):
    fi=(x-X0)/R-0.5; fj=(y-Y0)/R-0.5
    i=int(min(max(math.floor(fi),0),D.shape[1]-2)); j=int(min(max(math.floor(fj),0),D.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty)
C0=np.array([-300.2,-198.7]); C1=np.array([-296.4,-171.5]); cd=(C1-C0)/np.linalg.norm(C1-C0); cn=np.array([-cd[1],cd[0]])
if cn[0]>0: cn=-cn
def P2(s,t): q=C0+cd*s+cn*t; return float(q[0]),float(q[1])
for o in [o for o in OB if o.name.startswith('WS169c_')]: OB.remove(o)
SS=[-37.0,-36.0,-35.0,-34.0,-33.5]; TS=list(np.arange(4.5,45.01,1.0))
def build(bm,off):
    G={}
    for s in SS:
        for t in TS:
            x,y=P2(s,t); G[(s,t)]=bm.verts.new((x,y,dz(x,y)+off))
    for i in range(len(SS)-1):
        for j in range(len(TS)-1):
            bm.faces.new((G[(SS[i],TS[j])],G[(SS[i],TS[j+1])],G[(SS[i+1],TS[j+1])],G[(SS[i+1],TS[j])]))
bm=bmesh.new(); build(bm,-0.025)
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS169c_Lot3_S_end_lawn_bridge_LiDAR2023_1m'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials.get('COLE_lawn_post2020_bs')); uv=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    p=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(p.x*0.25,p.y*0.25)
col=bpy.data.collections.get('WS167_Sprague_E_bank_lane_bleachers') or bpy.context.scene.collection
ob=OB.new('WS169c_Lot3_S_end_lawn_bridge_LiDAR2023_1m',me); col.objects.link(ob)
tgt=OB['WS167_skirt_target_hidden']; tm=tgt.data
if 'ws169c' not in tm.attributes:
    tb=bmesh.new(); tb.from_mesh(tm); n0=len(tb.verts); build(tb,-0.02); tb.to_mesh(tm); tb.free()
    a=tm.attributes['wv_in']; vals=[0.0]*len(tm.vertices); a.data.foreach_get('value',vals)
    for k in range(n0,len(vals)): vals[k]=0.10
    a.data.foreach_set('value',vals); tm.attributes.new('ws169c','INT','POINT'); tm.update()
print('BRIDGE faces',len(me.polygons),'target verts',len(tm.vertices),flush=True)
ZS=np.load('/workspace/nj-scenes/montclair-state/scripts/ws162/dtm162.npy')[1]
def dz2(x,y):
    fi=(x+330.0)/0.5; fj=(-165.0-y)/0.5
    i=int(min(max(math.floor(fi),0),ZS.shape[1]-2)); j=int(min(max(math.floor(fj),0),ZS.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(ZS[j,i]*(1-tx)*(1-ty)+ZS[j,i+1]*tx*(1-ty)+ZS[j+1,i]*(1-tx)*ty+ZS[j+1,i+1]*tx*ty)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in (-230.0,-231.5,-233.0,-234.5,-236.0):
    row=[]
    for x in np.arange(-320,-299.9,2.0):
        r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
        row.append('%s%+.2f'%(r[4].name[:9] if r[0] else '-', (r[1].z-dz2(x,y)) if r[0] else 0))
    print('PROBE y%.1f '%y+' '.join(row),flush=True)
