# ws74a: soften the lawn crease at the College Ave north-curb bend (x -207..-193): Laplacian-smooth Terrain_LiDAR_DTM_1m base
# verts in a feathered box (edges fixed; LOWER-ONLY, max 25 cm, so nothing rises through walks/curbs), then re-seat WS73 verge outer edge on the smoothed terrain (+1 cm, eased profile).
import bpy,bmesh,json,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1,F=-209.0,-191.0,-73.0,-59.5,2.5
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
if t.get('ws74_smooth'): print('W74a skip terrain (flag)')
else:
    mw=t.matrix_world; bm=bmesh.new(); bm.from_mesh(t.data); bm.verts.ensure_lookup_table()
    def w(p):
        d=min(p.x-X0,X1-p.x,p.y-Y0,Y1-p.y)
        return 0 if d<=0 else min(1,d/F)
    sel=[(v,w(mw@v.co)) for v in bm.verts]; sel=[(v,k) for v,k in sel if k>0]
    old={v.index:v.co.z for v,_ in sel}
    for it in range(60):
        nz={}
        for v,k in sel:
            nb=[e.other_vert(v) for e in v.link_edges]
            if nb: nz[v]=v.co.z+0.5*k*(sum(n.co.z for n in nb)/len(nb)-v.co.z)
        for v,z in nz.items(): v.co.z=max(old[v.index]-0.25,min(z,old[v.index]))  # lower-only (no poke-through under walks), max 25 cm
    dz=[v.co.z-old[v.index] for v,_ in sel]
    print('W74a terrain verts',len(sel),'dz min/max',round(min(dz),3),round(max(dz),3),flush=True)
    json.dump({str(i):z for i,z in old.items()},open('/workspace/nj-scenes/montclair-state/scripts/ws74/terrain_oldz_%s.json'%os.environ.get('RUNTAG','main'),'w'))
    bm.to_mesh(t.data); bm.free(); t.data.update(); t['ws74_smooth']=1
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
oe=t.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(t.matrix_world); T=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear()
v=bpy.data.objects['WS73_curb_back_lawn_verge_UNVERIFIED']; V=v.data.vertices; vm=v.matrix_world; vi=vm.inverted()
n=0
for r in range(len(V)//5):
    row=[V[5*r+k] for k in range(5)]
    p4=vm@row[4].co; h=T.ray_cast(Vector((p4.x,p4.y,p4.z+5)),Vector((0,0,-1)))[0]
    if not h: continue
    z0=(vm@row[0].co).z; z4=h.z+0.01
    for k in range(1,5):
        s=k/4; e=s*s*(3-2*s); p=vm@row[k].co; p.z=z0*(1-e)+z4*e; row[k].co=vi@p
    n+=1
v.data.update(); print('W74a verge rows reseated',n,flush=True)
# check: terrain above verge / curb top
hi=0
for p in V:
    q=vm@p.co; h=T.ray_cast(Vector((q.x,q.y,q.z+5)),Vector((0,0,-1)))[0]
    if h and h.z>q.z+0.005: hi+=1
print('W74a verge verts with terrain above',hi,'/',len(V),flush=True)
