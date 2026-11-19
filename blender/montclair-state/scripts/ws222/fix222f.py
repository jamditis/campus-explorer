# ws222f: the WS72 Kasser landing's south edge v150 (-248.930,-53.620) -> v160 (-247.500,-53.105) was a straight chord across
# the W39 curb-return arc and the WS27 curb_left start, so the landing overhung College Ave by up to ~0.38 m in front of the
# curb and its 20 cm slab face stood on the asphalt as a fake curb. The top and bottom chord edges are subdivided and the new
# verts placed along the curb BACK line (return back points k19..k25, then curb_left back v3/v9), 1 cm into the curb, so the
# landing ends behind the curb like the rest of the walk. Side face rebuilt as quads; z interpolated along the old edge.
import bpy, bmesh
from mathutils import Vector
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; LM=L.matrix_world; LI=LM.inverted()
r=bpy.data.objects['WS220_CollegeAve_curb_jog_return_UNVERIFIED']; RM=r.matrix_world
cl=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; CM=cl.matrix_world
P=[]
for k in range(19,26):
    bk=RM@r.data.vertices[5*k+3].co; rf=RM@r.data.vertices[5*k+1].co; P.append(bk.xy+(rf.xy-bk.xy).normalized()*0.01)
for bi,fi in ((3,0),(9,6)):
    bk=CM@cl.data.vertices[bi].co; rf=CM@cl.data.vertices[fi].co; P.append(bk.xy+(rf.xy-bk.xy).normalized()*0.01)
for p in P: print('F222F path (%.3f,%.3f)'%tuple(p),flush=True)
bm=bmesh.new(); bm.from_mesh(L.data); bm.verts.ensure_lookup_table()
C={i:bm.verts[i].co.copy() for i in (150,160,151,161)}
def at(co):
    v=min(bm.verts,key=lambda v:(v.co-co).length); assert (v.co-co).length<1e-5; return v
N=len(P)
def split(ia,ib):
    A=at(C[ia]); B=at(C[ib]); e=[e for e in A.link_edges if B in e.verts]; assert e
    n0=len(bm.verts)
    bmesh.ops.subdivide_edges(bm,edges=e,cuts=N,use_grid_fill=False)
    bm.verts.ensure_lookup_table()
    nv=[bm.verts[i] for i in range(n0,len(bm.verts))]
    nv.sort(key=lambda v:(v.co-C[ia]).length); assert len(nv)==N,len(nv); return [v.co.copy() for v in nv]
topc=split(150,160); botc=split(151,161)
top=[at(c) for c in topc]; bot=[at(c) for c in botc]
v150,v160,v151,v161=[at(C[i]) for i in (150,160,151,161)]
side=[f for f in bm.faces if v150 in f.verts and v151 in f.verts and v160 in f.verts]; assert len(side)==1,len(side)
bm.faces.remove(side[0])
for row in (top,bot):
    for v,p in zip(row,P):
        w=LM@v.co; w.x,w.y=p.x,p.y; v.co=LI@w
ring_t=[v150]+top+[v160]; ring_b=[v151]+bot+[v161]
for i in range(len(ring_t)-1):
    f=bm.faces.new((ring_t[i],ring_b[i],ring_b[i+1],ring_t[i+1]))
bm.normal_update()
# outward check: side faces should face the road (-y-ish / +x-ish away from landing centroid)
cen=sum((v.co for v in bm.verts),Vector())/len(bm.verts); flipped=0
for f in bm.faces:
    if len(f.verts)==4 and set(f.verts)<=set(ring_t+ring_b) and f.normal.dot(f.calc_center_median()-cen)<0: f.normal_flip(); flipped+=1
bm.to_mesh(L.data); bm.free(); L.data.update()
print('F222F landing verts',len(L.data.vertices),'polys',len(L.data.polygons),'flipped',flipped,flush=True)
