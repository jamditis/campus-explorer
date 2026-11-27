# ws255 (CHAIN via ws208/merge208.py on main ws254d): UNIFY W63f — Feliciano E wall foot north of the recess (y 172..191.5).
# (1) Paved strip between the W63d walk (W edge x -192) and Feliciano's E wall for y ~179..190.9, where the ground still showed the
#     2020 ortho's building shadow as a dark strip (probe255.out: terrain cells x -194.6..-192.1, y 179.5..190.5). Evidence: ortho shows
#     paving running to the wall in the lit stretch (y 169..171); the 2023 LiDAR has no ground returns under the eave (overhang) ->
#     paving to the wall (UNVERIFIED for y > 179; in shadow on the ortho). Top = max(walk level, ground + 4 cm).
# (2) PI_Feliciano_east_base_course_UNVERIFIED segments between the original breaks inside y 172..191.6 rebuilt on the same wall line:
#     front 7 cm proud, bottom = surface - 8 cm (sloped, buried), flat top = max surface along the segment + 0.85 m (the band's
#     existing height above ground north of y 183), closed ends -> the band no longer floats 0.4-0.9 m above the walk/stairs.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F255A'
def bvo(n):
    o=bpy.data.objects.get(n)
    if not o: print(TAG,'MISSING',n,flush=True); return None
    M=o.matrix_world; me=o.data; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(-200<vs[i].x<-186 and 165<vs[i].y<196 for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps) if ps else None
GR=[b for b in map(bvo,['Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m','WS251_W63b_passage_LiDAR2023_ground_patch_1m']) if b]
WK=[b for b in map(bvo,['WS253_W63d_Feliciano_E_walk_slabs','WS253_W63d_Feliciano_E_walk_and_stairs_UNVERIFIED','WS254_W63e_recess_stairs_landing_to_wall_UNVERIFIED','WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED']) if b]
def zmax(bl,x,y):
    z=-1e9
    for b in bl:
        h=b.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
        if h[0]: z=max(z,h[0].z)
    return z
def inner(y): return -194.69+0.0615*(y-172.0)   # wall line fitted to the PI band (y173 -194.62, y199 -193.03)
COL=bpy.data.objects['WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED'].users_collection[0]
M_WALK=bpy.data.materials.get('WS159_concrete_walk_broomed')
SN='WS255_W63f_Feliciano_E_wall_foot_paving_to_wall_UNVERIFIED'
if SN not in bpy.data.objects:
    # strip start: N end of the widened stair/walk at the wall
    y0=None
    for y in np.arange(177.5,181.0,0.02):
        if zmax(WK,-193.6,y)<-1e8: y0=round(float(y),2); break
    print(TAG,'widened walk ends at y',y0,flush=True)
    y1=190.9; ys=list(np.arange(y0,y1,0.5))+[y1]
    XE=-191.95
    def xs(y): xw=inner(y)-0.10; return list(np.linspace(xw,XE,6))
    def wtop(y): return zmax(WK,-191.5,max(y,y0+0.02))
    bm=bmesh.new(); G=[]
    for y in ys:
        row=[]; wt=wtop(y)
        for k,x in enumerate(xs(y)):
            g=zmax(GR,x,y)
            z=max(wt-(0.004 if k==5 else 0.0), g+0.04 if k<5 else -1e9)
            row.append(bm.verts.new((x,y,z)))
        G.append(row)
    lo=lambda v: bm.verts.new((v.co.x,v.co.y,v.co.z-0.35))
    for i in range(len(ys)-1):
        for k in range(5): bm.faces.new([G[i][k],G[i][k+1],G[i+1][k+1],G[i+1][k]])
    for row,rev in ((G[0],False),(G[-1],True)):
        L=[lo(v) for v in row]
        for k in range(5):
            q=[row[k],L[k],L[k+1],row[k+1]]; bm.faces.new(q[::-1] if rev else q)
    print(TAG,'strip ys',len(ys),'z S %.2f..%.2f N %.2f..%.2f'%(min(v.co.z for v in G[0]),max(v.co.z for v in G[0]),min(v.co.z for v in G[-1]),max(v.co.z for v in G[-1])),flush=True)
    for i in range(0,len(ys),4): print(TAG,'strip y%.1f'%ys[i],' '.join('%.2f'%v.co.z for v in G[i]),'| walk %.2f'%wtop(ys[i]),flush=True)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    for f in bm.faces:
        if f.calc_center_median().z>0 and f.normal.z<-0.5 and len(f.verts)==4 and all(v in sum(G,[]) for v in f.verts): f.normal_flip()
    me=bpy.data.meshes.new(SN); bm.to_mesh(me); bm.free(); me.materials.append(M_WALK)
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        n=p.normal
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=(co.x,co.y) if abs(n.z)>0.5 else (co.x,co.z)
    so=bpy.data.objects.new(SN,me); COL.objects.link(so)
    up=sum(1 for p in me.polygons if p.normal.z>0.5); print(TAG,'obj',SN,len(me.vertices),len(me.polygons),'up',up,flush=True)
    SB=BVHTree.FromObject(so,bpy.context.evaluated_depsgraph_get())
    # (2) base course
    pi=bpy.data.objects['PI_Feliciano_east_base_course_UNVERIFIED']; Mp=pi.matrix_world; Mi=Mp.inverted()
    bm=bmesh.new(); bm.from_mesh(pi.data)
    fv=[(Mp@v.co) for v in bm.verts]
    brk=sorted(set(round(p.y,2) for p in fv if p.x>-196 and 171.0<p.y<193.0))
    # merge near-duplicate breaks
    B=[]
    for y in brk:
        if not B or y-B[-1]>0.3: B.append(y)
    ya=min(y for y in B if y>=172.0); yb=max(y for y in B if y<=191.6)
    df=[f for f in bm.faces if all((Mp@v.co).x>-196 and ya-0.02<=(Mp@v.co).y<=yb+0.02 for v in f.verts)]
    n0=len(bm.faces); bmesh.ops.delete(bm,geom=df,context='FACES_ONLY')
    lv=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lv,context='VERTS')
    seg=[y for y in B if ya<=y<=yb]
    print(TAG,'PI faces',n0,'deleted',len(df),'segments',len(seg)-1,'ya %.2f yb %.2f'%(ya,yb),flush=True)
    def surf(x,y):
        z=max(zmax(GR,x,y),zmax(WK,x,y))
        h=SB.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
        return max(z,h[0].z) if h[0] else z
    for a,b in zip(seg[:-1],seg[1:]):
        smp=[surf(inner(y)+0.12,y) for y in np.linspace(a,b,7)]
        top=max(smp)+0.85; za=surf(inner(a)+0.12,a)-0.08; zb=surf(inner(b)+0.12,b)-0.08
        def V(x,y,z): return bm.verts.new(Mi@Vector((x,y,z)))
        fa0,fb0=V(inner(a)+0.07,a,za),V(inner(b)+0.07,b,zb); fa1,fb1=V(inner(a)+0.07,a,top),V(inner(b)+0.07,b,top)
        ia1,ib1=V(inner(a)-0.01,a,top),V(inner(b)-0.01,b,top); ia0,ib0=V(inner(a)-0.01,a,za),V(inner(b)-0.01,b,zb)
        bm.faces.new([fa0,fb0,fb1,fa1]); bm.faces.new([fa1,fb1,ib1,ia1]); bm.faces.new([ia0,fa0,fa1,ia1]); bm.faces.new([fb0,ib0,ib1,fb1])
        print(TAG,'seg y%.2f-%.2f bot %.2f/%.2f top %.2f (surf %.2f..%.2f)'%(a,b,za,zb,top,min(smp),max(smp)),flush=True)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    bm.to_mesh(pi.data); bm.free(); pi.data.update()
    print(TAG,'PI now',len(pi.data.polygons),flush=True)
