# ws239 W53s PK/M3b seam weld: M3b's free (boundary) edge sat a median 2.3 cm ABOVE the tucked PK/WS60/WS68 strips
# (ws236e left the strips' outer verts 5 mm under M3b's interior, but M3b's own edge verts still stood over the strip
# surface -> a thin dark lip line in the close-up). Weld: each M3b boundary vert within 3 m (2D) of a strip whose vertical
# ray hits the strip with the strip 0-0.50 m BELOW it goes to strip z - 3 mm (lower-only, terrain not paving); ring-1
# neighbours (non-boundary) get min(z, z + 0.5*delta), ring 2 0.25*delta. Larger steps (>0.15 m) are logged, not touched.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
M=O['M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam']
S=['PK_Feliciano_west_DTM_fill_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt']+[o.name for o in O if o.name.startswith('WS68_RHD_ground_northDTM')]
def bvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
T=[bvh(O[n]) for n in S]
mw=M.matrix_world; iw=mw.inverted(); me=M.data
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
DN=Vector((0,0,-1)); delta={}; big=[]
for v in bm.verts:
    if not any(e.is_boundary for e in v.link_edges): continue
    w=mw@v.co
    if min(t.find_nearest(w)[3] for t in T)>3: continue
    hz=None
    for t in T:
        h=t.ray_cast(w+Vector((0,0,0.001)),DN,1.0)
        if h[0] is not None and (hz is None or h[0].z>hz): hz=h[0].z
    if hz is None: continue
    d=(hz-0.003)-w.z
    if d>=0: continue
    if d<-0.50: big.append((round(w.x,1),round(w.y,1),round(d,3))); continue
    delta[v.index]=d
# rings: carry the boundary delta (root) outward; ring k vert gets F[k]*min(root of its ring k-1 neighbours)
root=dict(delta); done=set(delta); front=list(delta); rings=[]
for f in (0.6,0.3,0.1):
    R={}; RR={}
    for i in front:
        for e in bm.verts[i].link_edges:
            o=e.other_vert(bm.verts[i]).index
            if o in done or any(x.is_boundary for x in bm.verts[o].link_edges): continue
            RR[o]=min(RR.get(o,0),root[i]); R[o]=f*RR[o]
    root.update(RR); done|=set(R); front=list(R); rings.append(R)
r1,r2,r3=rings
mx=0
for D in (delta,r1,r2,r3):
    for i,d in D.items():
        v=bm.verts[i]; w=mw@v.co; w.z+=d; v.co=iw@w; mx=min(mx,d)
bm.to_mesh(me); bm.free(); me.update()
print('F239A welded',len(delta),'ring1',len(r1),'ring2',len(r2),'ring3',len(r3),'max drop %.3f'%mx,'big(>0.50) skipped',len(big),big[:12],flush=True)
