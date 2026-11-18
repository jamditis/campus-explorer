# sg (Nov 4 2026 ~4:35 PM ET, MAIN, day 8 Student Center north side). ALL UNVERIFIED, reversible (REVERT=1).
# Follow-ups from sf: (1) Quad Road rebuilt along its FULL OSM extent (313028548+549, x -83..148) + Webster Road 313028543 (6.5 m),
# open ends sink into the ground over 6 m instead of a hard cut; sf ribbon hidden (kept). (2) Lot/road joint: lot slab copy lowered under
# the road band (lot faces fully under the road removed). (3) 15 cm concrete curbs on lot edges that border lawn (auto: not where the
# building is within 1.2 m; stop at the road edge) - typical detail, no source. (4) oil-drip stains in the 7 stalls + worn stall paint
# (material copy). (5) SF footway fragments < 4 m removed (mesh copy). (6) grass culled on the new road extents. (7) SG cameras.
import bpy, bmesh, os, json, math, random
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; COL='SG_QuadRoad_full_curbs_stains_UNVERIFIED'
def restore(o,key):
    if o and key in o:
        old=o.data; orig=bpy.data.meshes.get(o[key])
        if orig: o.data=orig; orig.use_fake_user=False
        if old.users==0 and old is not orig: bpy.data.meshes.remove(old)
        del o[key]
def revert():
    c=bpy.data.collections.get(COL)
    if c:
        for o in list(c.objects): me=o.data; bpy.data.objects.remove(o,do_unlink=True); (me and me.users==0 and isinstance(me,bpy.types.Mesh) and bpy.data.meshes.remove(me))
        bpy.data.collections.remove(c)
    for o in [o for o in bpy.data.objects if o.name.startswith('SG_CAM')]: cd=o.data; bpy.data.objects.remove(o,do_unlink=True); cd.users==0 and bpy.data.cameras.remove(cd)
    for o in bpy.data.objects: restore(o,'sg_orig_mesh')
    r=bpy.data.objects.get('SF_QuadRoad_313028549_UNVERIFIED')
    if r and 'sg_hidden' in r: r.hide_render=False; r.hide_viewport=False; del r['sg_hidden']
    s=bpy.data.objects.get('SF_Lot38_stall_stripes_UNVERIFIED')
    if s and 'sg_oldmat' in s: m0=bpy.data.materials[s['sg_oldmat']]; s.material_slots[0].material=m0; m0.use_fake_user=False; del s['sg_oldmat']
    for n in ('SG_stripe_paint_worn_UNVERIFIED','SG_oil_stain_UNVERIFIED','SG_curb_concrete_UNVERIFIED'):
        m=bpy.data.materials.get(n)
        if m: bpy.data.materials.remove(m)
    print('SG reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
W=json.load(open('data/sf/north_lot_osm.json'))['ways']
GN=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','RZ2_SC_LiDAR_ground_patch','QW_DTM_north_edge_ramp_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED']
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
def gz(x,y):
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
def segd(x,y,P):
    best=1e9
    for (ax,ay),(bx,by) in zip(P[:-1],P[1:]):
        dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1; t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2))
        best=min(best,math.hypot(x-ax-t*dx,y-ay-t*dy))
    return best
def editcopy(o):
    if 'sg_orig_mesh' not in o: o['sg_orig_mesh']=o.data.name; o.data.use_fake_user=True; nm=o.data.copy(); nm.name=o.data.name+'.sg'; o.data=nm
    return o.data
col=bpy.data.collections.new(COL); sc.collection.children.link(col)
def link(name,bm,mat,note,shadow=True):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); ob['UNVERIFIED_sg']=note; ob.visible_shadow=shadow; return ob
mrd=bpy.data.materials['SF_asphalt_worn_UNVERIFIED']
ROAD=W['313028548']['pts'][::-1]+W['313028549']['pts'][1:]
WEB=W['313028543']['pts']
# ---- (1) roads
def ribbon(pts,w,off,name,taper_start,taper_end,T=6.0):
    S=[]
    for (ax,ay),(bx,by) in zip(pts[:-1],pts[1:]):
        L=math.hypot(bx-ax,by-ay); n=max(1,int(L/0.75))
        for i in range(n): t=i/n; S.append((ax+(bx-ax)*t,ay+(by-ay)*t))
    S.append(tuple(pts[-1]))
    cum=[0.0]
    for a,b in zip(S[:-1],S[1:]): cum.append(cum[-1]+math.hypot(b[0]-a[0],b[1]-a[1]))
    tot=cum[-1]; bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap'); rows=[]
    for i,(x,y) in enumerate(S):
        a=S[max(i-1,0)]; b=S[min(i+1,len(S)-1)]; tx,ty=b[0]-a[0],b[1]-a[1]; l=math.hypot(tx,ty) or 1; nx,ny=-ty/l,tx/l
        o=off
        if taper_start and cum[i]<T: o=off-(0.16)*(1-cum[i]/T)
        if taper_end and tot-cum[i]<T: o=off-(0.16)*(1-(tot-cum[i])/T)
        L=(x+nx*w/2,y+ny*w/2); R=(x-nx*w/2,y-ny*w/2); zc=gz(x,y)
        if zc is None: rows.append(None); continue
        zl=gz(*L) or zc; zr=gz(*R) or zc
        rows.append([bm.verts.new((L[0],L[1],zl+o)),bm.verts.new((R[0],R[1],zr+o)),bm.verts.new((L[0],L[1],zl+o-0.3)),bm.verts.new((R[0],R[1],zr+o-0.3))])
    nq=0
    for p,q in zip(rows[:-1],rows[1:]):
        if p is None or q is None: continue
        for quad in ((p[0],q[0],q[1],p[1]),(p[2],q[2],q[0],p[0]),(p[1],q[1],q[3],p[3])):
            fc=bm.faces.new(quad); nq+=1
            for lp in fc.loops: lp[uv].uv=(lp.vert.co.x/2.0,lp.vert.co.y/2.0)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    return link(name,bm,mrd,'OSM centreline drape (full way), width from the 2020 ortho / default; open ends sink 16 cm over 6 m'),nq
# Quad Road west end joins Webster Road (no taper there); east end (148.3, 315.6) = edge of the OSM cut -> taper
r1=ribbon(ROAD,7.0,0.03,'SG_QuadRoad_full_313028548_549_UNVERIFIED',False,True); print('SG road',r1[1])
r2=ribbon(WEB,6.5,0.024,'SG_WebsterRoad_313028543_UNVERIFIED',False,True); print('SG webster',r2[1])
old=bpy.data.objects.get('SF_QuadRoad_313028549_UNVERIFIED')
if old: old.hide_render=True; old.hide_viewport=True; old['sg_hidden']=1
# ---- (2) lot under the road band
lot=bpy.data.objects['SF_Lot38_asphalt_313028558_UNVERIFIED']; me=editcopy(lot)
bm=bmesh.new(); bm.from_mesh(me); mw=lot.matrix_world
dele=[f for f in bm.faces if all(segd(*(mw@v.co).xy,ROAD)<3.2 for v in f.verts)]
bmesh.ops.delete(bm,geom=dele,context='FACES'); nlow=0
for v in bm.verts:
    p=mw@v.co; d=segd(p.x,p.y,ROAD)
    if d<4.6:
        g=gz(p.x,p.y)
        if g is not None:
            top=v.co.z>g-0.1
            v.co.z=(g+0.022) if top else (g-0.28); nlow+=1
bm.to_mesh(me); bm.free(); print('SG lot faces del',len(dele),'lowered',nlow)
# ---- (3) curbs
LOT=W['313028558']['pts'][:-1]; i=[k for k,p in enumerate(LOT) if abs(p[0]-16.2)<0.2][0]
LOT=LOT[:i+1]+[(18.5,357.6),(18.0,358.7),(0.0,359.6),(-3.0,359.0)]+LOT[i+1:]
area=sum(LOT[k][0]*LOT[(k+1)%len(LOT)][1]-LOT[(k+1)%len(LOT)][0]*LOT[k][1] for k in range(len(LOT)))/2
cm=bpy.data.materials.new('SG_curb_concrete_UNVERIFIED'); cm.use_nodes=True; N=cm.node_tree.nodes; Lk=cm.node_tree.links; b=N['Principled BSDF']
nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=6; cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.30,0.295,0.28,1); cr.color_ramp.elements[1].color=(0.46,0.45,0.43,1)
Lk.new(nz.outputs['Fac'],cr.inputs[0]); Lk.new(cr.outputs[0],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.9
def blocked(x,y):
    hit,loc,nrm,idx,ob,m=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
    g=gz(x,y)
    return hit and g is not None and loc.z>g+1.0
bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap'); nseg=0; kept=[]
for k in range(len(LOT)):
    (ax,ay),(bx,by)=LOT[k],LOT[(k+1)%len(LOT)]; L=math.hypot(bx-ax,by-ay)
    if L<0.5: continue
    ux,uy=(bx-ax)/L,(by-ay)/L; ox,oy=(uy,-ux) if area>0 else (-uy,ux)   # outward normal
    n=max(1,int(L/0.5)); run=[]
    for s in range(n+1):
        t=s/n; x=ax+(bx-ax)*t; y=ay+(by-ay)*t
        ok=segd(x,y,ROAD)>3.6 and not blocked(x+ox*1.2,y+oy*1.2) and not blocked(x+ox*0.4,y+oy*0.4)
        run.append((x,y) if ok else None)
    rows=[]
    for p in run:
        if p is None: rows.append(None); continue
        x,y=p; xi,yi=x-ox*0.02,y-oy*0.02; xo,yo=x+ox*0.15,y+oy*0.15
        gi=gz(xi,yi); go=gz(xo,yo)
        if gi is None or go is None: rows.append(None); continue
        top=max(gi,go)+0.04+0.11
        rows.append([bm.verts.new((xi,yi,top)),bm.verts.new((xo,yo,top-0.01)),bm.verts.new((xo,yo,go-0.15)),bm.verts.new((xi,yi,gi-0.15))])
    i0=0
    while i0<len(rows):
        if rows[i0] is None: i0+=1; continue
        j0=i0
        while j0<len(rows) and rows[j0] is not None: j0+=1
        if j0-i0<5:
            for r in rows[i0:j0]:
                for v in r: bm.verts.remove(v)
            for t in range(i0,j0): rows[t]=None
        i0=j0
    for p,q in zip(rows[:-1],rows[1:]):
        if p is None or q is None: continue
        for quad in ((p[0],p[1],q[1],q[0]),(p[1],p[2],q[2],q[1]),(p[3],p[0],q[0],q[3])):
            fc=bm.faces.new(quad); nseg+=1
            for lp in fc.loops: lp[uv].uv=(lp.vert.co.x+lp.vert.co.y,lp.vert.co.z)
    # end caps
    segs=[];cur=[]
    for r in rows:
        if r: cur.append(r)
        elif cur: segs.append(cur); cur=[]
    if cur: segs.append(cur)
    for s in segs:
        if len(s)<2: continue
        kept.append(len(s))
        for r in (s[0],s[-1]):
            try: bm.faces.new((r[0],r[1],r[2],r[3]))
            except ValueError: pass
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
link('SG_Lot38_curbs_UNVERIFIED',bm,cm,'15 cm concrete curb on lot edges bordering lawn; typical, no photo source'); print('SG curb quads',nseg,'runs',kept)
# ---- (4) worn stall paint + oil stains
st=bpy.data.objects.get('SF_Lot38_stall_stripes_UNVERIFIED')
if st:
    om=st.material_slots[0].material; st['sg_oldmat']=om.name; om.use_fake_user=True
    pm=bpy.data.materials.new('SG_stripe_paint_worn_UNVERIFIED'); pm.use_nodes=True; N=pm.node_tree.nodes; Lk=pm.node_tree.links; b=N['Principled BSDF']
    g=N.new('ShaderNodeNewGeometry'); nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=3.5; nz.inputs['Detail'].default_value=10
    Lk.new(g.outputs['Position'],nz.inputs['Vector']); cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position=0.26; cr.color_ramp.elements[0].color=(0.10,0.098,0.094,1)
    cr.color_ramp.elements[1].position=0.40; cr.color_ramp.elements[1].color=(0.47,0.47,0.44,1); Lk.new(nz.outputs['Fac'],cr.inputs[0]); Lk.new(cr.outputs[0],b.inputs['Base Color'])
    b.inputs['Roughness'].default_value=0.85; st.material_slots[0].material=pm
sm=bpy.data.materials.new('SG_oil_stain_UNVERIFIED'); sm.use_nodes=True; N=sm.node_tree.nodes; Lk=sm.node_tree.links; b=N['Principled BSDF']
b.inputs['Base Color'].default_value=(0.010,0.009,0.008,1); b.inputs['Roughness'].default_value=0.55
tc=N.new('ShaderNodeTexCoord'); gr=N.new('ShaderNodeTexGradient'); gr.gradient_type='SPHERICAL'; nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=9
Lk.new(tc.outputs['UV'],gr.inputs['Vector']); Lk.new(tc.outputs['Object'],nz.inputs['Vector'])
mu=N.new('ShaderNodeMath'); mu.operation='MULTIPLY'; Lk.new(gr.outputs['Fac'],mu.inputs[0]); Lk.new(nz.outputs['Fac'],mu.inputs[1])
mr=N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=0.05; mr.inputs['From Max'].default_value=0.28; mr.inputs['To Max'].default_value=0.8
Lk.new(mu.outputs[0],mr.inputs['Value']); Lk.new(mr.outputs['Result'],b.inputs['Alpha'])
le=lot.evaluated_get(bpy.context.evaluated_depsgraph_get()); iw=lot.matrix_world.inverted()
def lz(x,y):
    r=le.ray_cast(iw@Vector((x,y,300)),Vector((0,0,-1))); return (lot.matrix_world@r[1]).z if r[0] else None
def edge_y(x): return 355.0+(x-16.2)*(352.4-355.0)/(37.2-16.2)
random.seed(4); bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap'); ns=0
for k in range(7):
    xb=16.9+2.2*k+1.1; yb=348.2; yt=edge_y(xb+1.0)-0.45; cx=xb+0.55+random.uniform(-0.2,0.2); cy=yb+(yt-yb)*random.uniform(0.35,0.55)
    rx=random.uniform(0.45,0.7); ry=random.uniform(0.7,1.1); z=lz(cx,cy)
    if z is None: continue
    c=bm.verts.new((cx,cy,z+0.004)); ring=[]
    for j in range(16):
        a=2*math.pi*j/16; ring.append(bm.verts.new((cx+rx*math.cos(a),cy+ry*math.sin(a),(lz(cx+rx*math.cos(a),cy+ry*math.sin(a)) or z)+0.004)))
    for j in range(16):
        f=bm.faces.new((c,ring[j],ring[(j+1)%16])); ns+=1
        for lp in f.loops:
            v=lp.vert; lp[uv].uv=(0.5+(v.co.x-cx)/(2*rx), 0.5+(v.co.y-cy)/(2*ry))
link('SG_Lot38_oil_stains_UNVERIFIED',bm,sm,'oil-drip stains in the stall centres; typical, no source',shadow=False); sm.blend_method='BLEND' if hasattr(sm,'blend_method') else None
print('SG stains tris',ns)
# ---- (5) footway fragments
rm=0
for o in [o for o in bpy.data.objects if o.name.startswith('SF_footway_')]:
    me=o.data; bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
    seen=set(); isl=[]
    for f in bm.faces:
        if f.index in seen: continue
        st_=[f]; grp=[]; seen.add(f.index)
        while st_:
            g=st_.pop(); grp.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen: seen.add(h.index); st_.append(h)
        isl.append(grp)
    bad=[]
    for grp in isl:
        xs=[v.co.x for f in grp for v in f.verts]; ys=[v.co.y for f in grp for v in f.verts]
        if math.hypot(max(xs)-min(xs),max(ys)-min(ys))<4.5: bad+=grp
    if bad:
        idx={f.index for f in bad}; bm.free(); me=editcopy(o); bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index in idx],context='FACES'); bm.to_mesh(me); rm+=len(idx)
    bm.free()
print('SG footway fragment faces removed',rm)
# ---- (6) grass cull on the new road extents (band 4.2 m Quad, 4.0 m Webster)
gc=0
for o in [o for o in bpy.data.objects if o.type=='MESH' and 'grass_points' in o.name]:
    mw=o.matrix_world
    idx=[v.index for v in o.data.vertices if (lambda p:-95<p.x<160 and 300<p.y<425 and (segd(p.x,p.y,ROAD)<4.2 or segd(p.x,p.y,WEB)<4.0))(mw@v.co)]
    if not idx: continue
    me=editcopy(o); bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bmesh.ops.delete(bm,geom=[bm.verts[i] for i in idx],context='VERTS'); bm.to_mesh(me); bm.free(); gc+=len(idx)
    print('SG grass culled',o.name,len(idx))
print('SG grass total',gc)
# ---- (7) cameras
def cam(name,loc,tgt,lens):
    c=bpy.data.cameras.new(name); c.lens=lens; c.clip_end=5000; o=bpy.data.objects.new(name,c); sc.collection.objects.link(o)
    d=Vector(tgt)-Vector(loc); o.location=loc
    o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2); return o
g=gz(48,362) or 139.0; cam('SG_CAM_eye_QuadRoad_east_curve',(48,362.5,g+1.65),(118,331,g+0.5),28)
g=gz(33,357) or 139.0; cam('SG_CAM_closeup_lot38_NE_curb_stains',(36,359.5,g+2.2),(24,349,g),26)
cam('SG_CAM_oblique_QuadRoad_from_N',(30,470,200),(30,345,140),30)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
