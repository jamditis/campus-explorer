# ws221c (found in the W40 close-up): (1) wedge gap in the College Ave asphalt just S of the W39 curb junction: WS67 gap
# asphalt E edge is straight at x -249.42 while the WS27 carriageway W edge runs diagonally (-249.208,-56.194)->(-249.608,
# -57.744), leaving a 0.21 m x 0.8 m triangle showing the lower DTM target/ground. WS67 v24/v21 moved E onto the WS27 edge
# (v24 ends under the curb-return nose). (2) dark void between the WS70 verge grass edge (straight diagonal v84-v86) and the
# curb return back arc: those grass edge verts re-placed on the return's back line, placed 1 cm behind the curb back (edge v84-v85 subdivided x4 so it follows the arc), z = curb
# top - 3 cm (raise-only; v86 was 15 cm low).
import bpy
from mathutils import Vector
a=[o for o in bpy.data.objects if o.name.startswith('WS67_CollegeAve_gap_asphalt')][0]; M=a.matrix_world; MI=M.inverted()
E0=Vector((-249.208,-56.194)); E1=Vector((-249.608,-57.744))
for i in (24,21):
    v=a.data.vertices[i]; w=M@v.co; assert abs(w.x+249.42)<0.01, ('F221C WS67',i,tuple(w))
    t=(w.y-E0.y)/(E1.y-E0.y); x=E0.x+(E1.x-E0.x)*t+0.005
    print('F221C WS67 v%d y %.3f x %.3f -> %.3f'%(i,w.y,w.x,x),flush=True); w.x=x; v.co=MI@w
a.data.update()
c=bpy.data.objects['WS220_CollegeAve_curb_jog_return_UNVERIFIED']; CM=c.matrix_world
nv=len(c.data.vertices); assert nv%5==0
BK=[(CM@c.data.vertices[5*k+3].co) for k in range(nv//5)]; RF=[(CM@c.data.vertices[5*k+1].co) for k in range(nv//5)]
def proj(p):
    best=None
    for k in range(len(BK)-1):
        A=BK[k].xy; B=BK[k+1].xy; ab=B-A; t=max(0,min(1,(p-A).dot(ab)/ab.length_squared)); q=A+ab*t
        d=(p-q).length
        if best is None or d<best[0]:
            inward=((RF[k].xy+(RF[k+1].xy-RF[k].xy)*t)-q).normalized()   # toward the road face
            best=(d,q,inward,BK[k].z+(BK[k+1].z-BK[k].z)*t)
    return best
import bmesh
g=bpy.data.objects['WS70_gap_strip_grass_berms']; GM=g.matrix_world; GI=GM.inverted()
bm=bmesh.new(); bm.from_mesh(g.data); bm.verts.ensure_lookup_table()
e=[e for e in bm.edges if {e.verts[0].index,e.verts[1].index}=={84,85}]
assert e, 'F221C no edge 84-85'
n0=len(bm.verts)
r=bmesh.ops.subdivide_edges(bm,edges=e,cuts=4,use_grid_fill=False)
bm.verts.ensure_lookup_table(); bm.verts.index_update(); bm.verts.ensure_lookup_table()
print('F221C subdiv new verts',len(bm.verts)-n0,flush=True)
for v in [bm.verts[i] for i in [84,85,86]+list(range(n0,len(bm.verts)))]:
    w=GM@v.co; d,q,inw,zt=proj(w.xy)
    nw=Vector((q.x-inw.x*0.01,q.y-inw.y*0.01,max(w.z,zt-0.03)))   # 1 cm behind the curb back (blades stop at the back face)
    print('F221C grass v%d (%.3f,%.3f,%.3f) -> (%.3f,%.3f,%.3f) d %.3f'%(v.index,*w,*nw,d),flush=True); v.co=GI@nw
bm.to_mesh(g.data); bm.free(); g.data.update()
# (3) leftover WS70 grass on the ROAD side of the curb-return straight run (y -54.6...-53.8 showed grass 5-9 cm above the
# WS27 asphalt, E of the curb): v93 (under the curb front) moved to 1 cm behind the curb back; v87/v88/v94/v100 (E of the
# curb, under the carriageway) dropped to 125.30 so no grass face reaches above the asphalt at the curb front face.
g=bpy.data.objects['WS70_gap_strip_grass_berms']; GM=g.matrix_world; GI=GM.inverted()
v=g.data.vertices[93]; w=GM@v.co; d,q,inw,zt=proj(w.xy); nw=Vector((q.x-inw.x*0.01,q.y-inw.y*0.01,max(w.z,zt-0.03)))
print('F221C grass v93 (%.3f,%.3f,%.3f) -> (%.3f,%.3f,%.3f)'%(*w,*nw),flush=True); v.co=GI@nw
for i in (87,88,94,100):
    v=g.data.vertices[i]; w=GM@v.co; assert w.x>-248.9, ('F221C',i,tuple(w))
    print('F221C grass v%d z %.3f -> 125.300'%(i,w.z),flush=True); w.z=125.30; v.co=GI@w
g.data.update()
