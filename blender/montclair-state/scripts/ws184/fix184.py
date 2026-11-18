# ws184 — UNIFY #89 (c) + (a): runs AFTER ws183/fix183.py.
# (c) WS163_Lot3_aisle_S_drive (Lot 3 aisle -> Normal Ave ramp along the Lot 36 bank, x -315..-303, y -251..-234): ws184 probe
#     (scripts/ws184/probe184a.out) shows the verts DO follow the 2023 DTM (median +3 cm, p10..p90 -16..+6 cm) but the irregular
#     triangulation carries +-5 cm per-vertex noise under FLAT shading -> 216/352 faces tilted, read as faceted grey triangles from
#     Lot 36 (eye level ~ drive height, surface seen nearly edge-on). A real ramp drive is a smooth graded surface (2023 DTM 0.5 m shows
#     a continuous fall 117.8 -> 115.6, no steps). Fix: Laplacian z-smoothing of INTERIOR verts (boundary pinned so seams with the bank
#     lawn / Lot 3 apron / Normal Ave don't open), |dz| capped 6 cm, then smooth shading.
# (a) WS181 Lot 36 asphalt: flat-shaded 4312-tri drape shows faint parallelogram facets at (-319.9,-230.1) (ws183 flatten test made it
#     worse) -> smooth shading only (no geometry change).
import bpy, bmesh, math
from mathutils import Vector
def ob(pre): return next((o for o in bpy.data.objects if o.name.startswith(pre)),None)
def dihed(me):
    bm=bmesh.new(); bm.from_mesh(me); s=0; n=0; big=0
    for e in bm.edges:
        if len(e.link_faces)==2:
            a=math.degrees(e.link_faces[0].normal.angle(e.link_faces[1].normal,0)); s+=a; n+=1; big+=(a>3)
    bm.free(); return (s/max(n,1), big, n)
DR=ob('WS163_Lot3_aisle_S_drive'); LOT=ob('WS181_Lot36_asphalt')
if DR:
    me=DR.data; b0=dihed(me)
    # (c2) W-edge flap: 2023 class-2 intensity (prep/ws171_lot36/int171_lot36_0p25m.npy) puts the asphalt/lawn break at
    #      x_e = -310.7 + 0.17*(y+235) for y -235..-238 (1-3k asphalt -> 5.5-12k lawn), i.e. at the top of the bank break (DTM z 116.8-116.9);
    #      the model drapes the drive 0.6-0.9 m further W down the bank (z 116.3-116.5) = the hanging grey flap. Compress the W 1 m of the
    #      drive (y -234..-239.5, taper 0 at -239.5) so its W boundary lands on x_e; moved verts re-seated on the DTM +3 cm.
    import numpy as _np
    _D=_np.load('/workspace/nj-scenes/montclair-state/prep/ws181_lot36/dtm181_0p5m.npy')
    def dtm(x,y):
        c=int(round((x+355)/0.5)); r=int(round((-200-y)/0.5)); w=_D[max(r-1,0):r+2,max(c-1,0):c+2]
        return float(_np.nanmean(w)) if _np.isfinite(w).any() else None
    M0=DR.matrix_world; M0i=M0.inverted(); bmF=bmesh.new(); bmF.from_mesh(me)
    bW=[(M0@v.co) for v in bmF.verts if v.is_boundary and (M0@v.co).x<-310.5 and -239.5<(M0@v.co).y<-234.0]
    if len(bW)>=3:
        A=_np.array([[w.y,1.0] for w in bW]); kb=_np.linalg.lstsq(A,_np.array([w.x for w in bW]),rcond=None)[0]
        nmv=0; mxs=0
        for v in bmF.verts:
            w=M0@v.co
            if not (-239.5<w.y<-234.0): continue
            xe=-310.7+0.17*(w.y+235.0); xb=min(kb[0]*w.y+kb[1],xe-0.05); 
            if w.x>=xe+1.0: continue
            wt=min(1.0,(w.y+239.5)/1.0)
            s_=1.0/(xe+1.0-xb); xn=max(xe,xe+1.0-(xe+1.0-w.x)*s_); xn=w.x+wt*(xn-w.x)
            if abs(xn-w.x)<0.01: continue
            zd=dtm(xn,w.y); zn=(zd+0.03) if zd is not None else w.z
            mxs=max(mxs,abs(xn-w.x)); v.co=M0i@Vector((xn,w.y,zn)); nmv+=1
        bmF.to_mesh(me); me.update()
        print('FIX184 W-edge flap: boundary fit x=%.3f*y%+.2f, verts moved %d max shift %.2f'%(kb[0],kb[1],nmv,mxs),flush=True)
    bmF.free()
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    M=DR.matrix_world
    z0=[(M@v.co).z for v in bm.verts]; z=list(z0)
    inner=[v.index for v in bm.verts if not v.is_boundary and all(len(e.link_faces)==2 for e in v.link_edges)]
    nb={i:[e.other_vert(bm.verts[i]).index for e in bm.verts[i].link_edges] for i in inner}
    for it in range(12):
        zn=list(z)
        for i in inner:
            m=sum(z[j] for j in nb[i])/len(nb[i]); zn[i]=z[i]+0.6*(m-z[i])
            zn[i]=min(z0[i]+0.06,max(z0[i]-0.06,zn[i]))
        z=zn
    Mi=M.inverted(); mx=0
    for i in inner:
        w=M@bm.verts[i].co; w.z=z[i]; bm.verts[i].co=Mi@w; mx=max(mx,abs(z[i]-z0[i]))
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    me.update(); b1=dihed(me)

    # lawn sheets under the drive: after smoothing (interior drops <= 6 cm) the pushed-under lawn surfaced as blobs (ws184a render)
    # -> every lawn vert under the drive footprint goes >= 2.5 cm below the drive surface (ray from above). Nothing visible moves.
    from mathutils.bvhtree import BVHTree
    dg=bpy.context.evaluated_depsgraph_get(); bmD=bmesh.new(); bmD.from_object(DR,dg); bmD.transform(DR.matrix_world); TD=BVHTree.FromBMesh(bmD); bmD.free()
    pushed={}
    for o in bpy.data.objects:
        if o.type!='MESH' or o is DR or not o.name.startswith(('WS163_ground_patch','WS169c','WS162_Lot3_W_shoulder_lawn','WS167_ground_W','Context_ground')): continue
        me2=o.data; M2=o.matrix_world; M2i=M2.inverted(); c=0
        for v in me2.vertices:
            w=M2@v.co
            if not (-316<w.x<-302 and -252<w.y<-233.5): continue
            h=TD.ray_cast(Vector((w.x,w.y,w.z+1.0)),Vector((0,0,-1)),2.0)
            if h[0] is not None and w.z>h[0].z-0.025: v.co=M2i@Vector((w.x,w.y,h[0].z-0.025)); c+=1
        if c: me2.update(); pushed[o.name[:28]]=c
    print('FIX184 lawn verts pushed under drive',pushed,flush=True)
    print('FIX184 drive inner %d/%d max dz %.3f dihedral mean %.2f->%.2f deg, edges>3deg %d->%d of %d'%(len(inner),len(me.vertices),mx,b0[0],b1[0],b0[1],b1[1],b1[2]),flush=True)
else: print('FIX184 SKIPPED drive missing',flush=True)
if LOT:
    for p in LOT.data.polygons: p.use_smooth=True
    LOT.data.update(); print('FIX184 lot smooth-shaded faces',len(LOT.data.polygons),flush=True)

# (d) hole: probe184b found NOTHING but the far-field base (z 0.5) at x -312.5..-311.5, y -236.0..-234.5 (W of the drive edge, between the
#     WS163 patch and WS169c bridge) = the black void under the flap. Fill with a lawn patch on the 2023 DTM -3 cm (below every existing
#     surface there, so it only shows where nothing else is). COLE lawn material like the neighbouring sheets.
if DR:
    import numpy as _np
    xs=_np.arange(-313.25,-310.49,0.25); ys=_np.arange(-237.0,-233.99,0.25)
    vs=[]; fs=[]
    for j,y in enumerate(ys):
        for i,x in enumerate(xs):
            zd=dtm(x,y); vs.append((x,y,(zd if zd is not None else 116.5)-0.03))
    nx=len(xs)
    for j in range(len(ys)-1):
        for i in range(nx-1): a=j*nx+i; fs.append((a,a+1,a+nx+1,a+nx))
    mF=bpy.data.meshes.new('WS184_Lot3_S_drive_W_edge_lawn_fill_DTM2023'); mF.from_pydata(vs,[],fs); mF.update()
    for p in mF.polygons: p.use_smooth=True
    lm=bpy.data.materials.get('COLE_lawn_post2020_bs')
    if lm: mF.materials.append(lm)
    oF=bpy.data.objects.new('WS184_Lot3_S_drive_W_edge_lawn_fill_DTM2023_UNIFY89',mF)
    (DR.users_collection[0] if DR.users_collection else bpy.context.scene.collection).objects.link(oF)
    print('FIX184 lawn fill faces',len(fs),'mat',lm.name if lm else None,flush=True)
    # review fix (ws184c renders): small dark notches where WS163 patch / WS169c lawn triangles poke 0-1 cm through the fill ->
    # their verts inside the fill (1 cell in from its edge) go 2 cm under the fill; the fill is the smoother DTM surface.
    from mathutils.bvhtree import BVHTree as _B
    tf=_B.FromPolygons([Vector(v) for v in vs],fs); cnt={}
    for o in bpy.data.objects:
        if o.type!='MESH' or not o.name.startswith(('WS163_ground_patch','WS169c')): continue
        me3=o.data; M3=o.matrix_world; M3i=M3.inverted(); c=0
        for v in me3.vertices:
            w=M3@v.co
            if not (-313.0<w.x<-310.75 and -236.75<w.y<-234.25): continue
            h=tf.ray_cast(Vector((w.x,w.y,w.z+1.0)),Vector((0,0,-1)),2.0)
            if h[0] is not None and w.z>h[0].z-0.02: v.co=M3i@Vector((w.x,w.y,h[0].z-0.02)); c+=1
        if c: me3.update(); cnt[o.name[:24]]=c
    print('FIX184 lawn verts under fill',cnt,flush=True)
