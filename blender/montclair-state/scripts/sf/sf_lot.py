# sf (Nov 4 2026 ~3:35 PM ET, MAIN, day 8 Student Center north side). ALL UNVERIFIED, reversible (REVERT=1).
# The ortho shows Lot 38 (OSM 313028558, service/accessible lot with dumpsters) and Quad Road (313028549/548) north of the
# Student Center; MAIN had only lawn-shaded 3DEP skirt + grass there. Adds: Lot 38 asphalt slab (conformal 1 m grid, ground+4 cm,
# 0.3 m edge curtain), Quad Road asphalt ribbon (7 m, from the 2020 ortho), 2 m footway ribbons for the OSM walks round the lot
# (only where no walk exists), culls grass points on them, moves RZ_CAM_eye_SC_from_E to a clear spot, adds SF cameras.
# OSM local coords: data/sf/north_lot_osm.json (affine fit on 112 shared nodes, max err 1 mm).
import bpy, bmesh, os, json, math
from mathutils import Vector, kdtree
REV=os.environ.get('REVERT')=='1'; COL='SF_Lot38_QuadRoad_UNVERIFIED'; BK='montclair_state_pre_20261104sf.blend'
GRASS=['QV_Richardson_NW_lawn_grass_points_UNVERIFIED','QX_Richardson_W_ramp_grass_points_UNVERIFIED','QXP_band_refill_grass_points_UNVERIFIED']
def revert():
    c=bpy.data.collections.get(COL)
    if c:
        for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
        bpy.data.collections.remove(c)
    for me in [m for m in bpy.data.meshes if m.name.startswith('SF_') and m.users==0]: bpy.data.meshes.remove(me)
    for o in [o for o in bpy.data.objects if o.name.startswith('SF_CAM')]: bpy.data.objects.remove(o,do_unlink=True)
    for c in [c for c in bpy.data.cameras if c.name.startswith('SF_CAM') and c.users==0]: bpy.data.cameras.remove(c)
    for gn in GRASS:
        o=bpy.data.objects.get(gn)
        if o and 'sf_culled' in o:
            old=o.data; orig=bpy.data.meshes[o['sf_orig_mesh']]; o.data=orig; orig.use_fake_user=False
            if old.users==0: bpy.data.meshes.remove(old)
            base=orig.name.split('.')[0] if orig.name.split('.')[-1].isdigit() else orig.name
            for m in [m for m in bpy.data.meshes if m is not orig and m.use_fake_user and m.users==1 and (m.name==base or m.name.startswith(base+'.'))]: bpy.data.meshes.remove(m)
            if orig.name!=base and base not in bpy.data.meshes: orig.name=base
            del o['sf_culled']; del o['sf_orig_mesh']
            print('SF grass restored',gn,orig.name,len(orig.vertices))
    rc=bpy.data.objects.get('RZ_CAM_eye_SC_from_E')
    if rc and 'sf_old' in rc: v=rc['sf_old']; rc.location=v[:3]; rc.rotation_euler=v[3:6]; rc.data.lens=v[6]; del rc['sf_old']
    m=bpy.data.materials.get('SF_asphalt_worn_UNVERIFIED')
    if m: bpy.data.materials.remove(m)
    print('SF reverted')
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
def pip(x,y,poly):
    ins=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
def asph():
    m=bpy.data.materials.new('SF_asphalt_worn_UNVERIFIED'); m.use_nodes=True; N=m.node_tree.nodes; L=m.node_tree.links; b=N['Principled BSDF']
    g=N.new('ShaderNodeNewGeometry'); n1=N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value=0.35; n1.inputs['Detail'].default_value=8
    n2=N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=18; n2.inputs['Detail'].default_value=4
    L.new(g.outputs['Position'],n1.inputs['Vector']); L.new(g.outputs['Position'],n2.inputs['Vector'])
    mx=N.new('ShaderNodeMath'); mx.operation='MULTIPLY_ADD'; mx.inputs[1].default_value=0.6; L.new(n1.outputs['Fac'],mx.inputs[0]); L.new(n2.outputs['Fac'],mx.inputs[2])
    cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position=0.45; cr.color_ramp.elements[0].color=(0.05,0.05,0.052,1)
    cr.color_ramp.elements[1].position=0.85; cr.color_ramp.elements[1].color=(0.11,0.108,0.102,1); L.new(mx.outputs[0],cr.inputs[0])
    L.new(cr.outputs[0],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.95; b.inputs['Specular IOR Level'].default_value=0.25
    bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.15; L.new(n2.outputs['Fac'],bp.inputs['Height']); L.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
col=bpy.data.collections.new(COL); sc.collection.children.link(col)
mrd=asph(); mfp=bpy.data.objects['Footpaths_OSM'].material_slots[0].material
print('SF mats',mrd.name,mfp.name)
SC=[o for o in bpy.data.objects if o.name.startswith('StudentCenter L0_low')][0]
def link(name,bm,mat,note):
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); ob['UNVERIFIED_sf']=note; return ob
# ---- Lot 38 slab
LOT=W['313028558']['pts'][:-1]
# entry apron from the 2020 ortho (paved between the lot's OSM north edge and Quad Road, x -3..18; ±0.5 m)
i=[k for k,p in enumerate(LOT) if abs(p[0]-16.2)<0.2][0]
LOT=LOT[:i+1]+[(18.5,357.6),(18.0,358.7),(0.0,359.6),(-3.0,359.0)]+LOT[i+1:]
bm=bmesh.new(); vs=[bm.verts.new((x,y,0)) for x,y in LOT]; f=bm.faces.new(vs)
xs=[p[0] for p in LOT]; ys=[p[1] for p in LOT]
for x in range(math.floor(min(xs))+1,math.ceil(max(xs))):
    bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],plane_co=(x,0,0),plane_no=(1,0,0))
for y in range(math.floor(min(ys))+1,math.ceil(max(ys))):
    bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],plane_co=(0,y,0),plane_no=(0,1,0))
miss=0
for v in bm.verts:
    z=gz(v.co.x,v.co.y)
    if z is None: z=139.3; miss+=1
    v.co.z=z+0.04
bnd=[e for e in bm.edges if e.is_boundary]
ext=bmesh.ops.extrude_edge_only(bm,edges=bnd)
for v in [g for g in ext['geom'] if isinstance(g,bmesh.types.BMVert)]: v.co.z-=0.3
uv=bm.loops.layers.uv.new('UVMap')
for fc in bm.faces:
    for lp in fc.loops: lp[uv].uv=(lp.vert.co.x/2.0,lp.vert.co.y/2.0)
lot=link('SF_Lot38_asphalt_313028558_UNVERIFIED',bm,mrd,'OSM Lot 38 outline (matches 2020 ortho ±0.5 m), draped ground+4 cm; no stall paint yet')
print('SF lot faces',len(lot.data.polygons),'miss',miss)
# ---- ribbons
def ribbon(pts,w,off,name,mat,skipkd=None,clip=None):
    S=[]
    for (ax,ay),(bx,by) in zip(pts[:-1],pts[1:]):
        L=math.hypot(bx-ax,by-ay); n=max(1,int(L/0.75))
        for i in range(n): t=i/n; S.append((ax+(bx-ax)*t,ay+(by-ay)*t))
    S.append(tuple(pts[-1]))
    keep=[(skipkd is None or skipkd.find((x,y,0))[2]>1.5) and not pip(x,y,LOT) and (clip is None or clip(x,y)) for x,y in S]
    runs=[];cur=[]
    for s,k in zip(S,keep):
        if k: cur.append(s)
        elif cur: runs.append(cur); cur=[]
    if cur: runs.append(cur)
    bm=bmesh.new(); uv=bm.loops.layers.uv.new('UVMap'); nq=0
    for r in runs:
        if len(r)<3: continue
        rows=[]
        for i,(x,y) in enumerate(r):
            a=r[max(i-1,0)]; b=r[min(i+1,len(r)-1)]; tx,ty=b[0]-a[0],b[1]-a[1]; l=math.hypot(tx,ty) or 1; nx,ny=-ty/l,tx/l
            L=(x+nx*w/2,y+ny*w/2); R=(x-nx*w/2,y-ny*w/2)
            zc=gz(x,y)
            if zc is None: rows.append(None); continue
            zl=gz(*L) or zc; zr=gz(*R) or zc
            rows.append([bm.verts.new((L[0],L[1],zl+off)),bm.verts.new((R[0],R[1],zr+off)),bm.verts.new((L[0],L[1],zl+off-0.3)),bm.verts.new((R[0],R[1],zr+off-0.3))])
        for p,q in zip(rows[:-1],rows[1:]):
            if p is None or q is None: continue
            for quad in ((p[0],q[0],q[1],p[1]),(p[2],q[2],q[0],p[0]),(p[1],q[1],q[3],p[3])):
                fc=bm.faces.new(quad); nq+=1
                for lp in fc.loops: lp[uv].uv=(lp.vert.co.x/2.0,lp.vert.co.y/2.0)
    if nq==0: bm.free(); return None
    return link(name,bm,mat,'OSM centreline drape, width from the 2020 ortho / default'),nq
road=W['313028548']['pts'][::-1]+W['313028549']['pts'][1:]
r=ribbon(road,7.0,0.03,'SF_QuadRoad_313028549_UNVERIFIED',mrd,clip=lambda x,y:-80<x<80); print('SF road',r and r[1])
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
# existing walks kd
pts=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    n=o.name
    if not (n=='Footpaths_OSM' or 'footway' in n.lower() or n.startswith('QXP_') or n.startswith('SB_')): continue
    if 'grass' in n.lower() or 'soil' in n.lower(): continue
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    for v in me.vertices:
        p=mw@v.co
        if -70<p.x<90 and 315<p.y<380: pts.append(p)
    e.to_mesh_clear()
kd=kdtree.KDTree(max(1,len(pts)))
for i,p in enumerate(pts): kd.insert((p.x,p.y,0),i)
kd.balance(); print('SF existing walk verts',len(pts))
RD=road
def offroad(x,y):
    for (ax,ay),(bx,by) in zip(RD[:-1],RD[1:]):
        dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1; t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2))
        if (x-ax-t*dx)**2+(y-ay-t*dy)**2<3.4**2: return False
    return True
FW=['313028550','313028552','313028553','313028554','313028556','313028562','1132693538','1132693539','313028555','313028551','313028563','313028564']
for i,wid in enumerate(FW):
    if wid not in W: continue
    r=ribbon(W[wid]['pts'],2.0,0.05+0.002*i,'SF_footway_%s_UNVERIFIED'%wid,mfp,skipkd=kd,clip=lambda x,y:offroad(x,y) and -70<x<90 and y<380 and not pip(x,y,[(p[0],p[1]) for p in []]))
    print('SF footway',wid,r and r[1])
bpy.context.view_layer.update()
# ---- grass cull: inside lot (+0.6), road band (4.2), new footways (1.3)
segs=[(a,b,4.2) for a,b in zip(RD[:-1],RD[1:])]
for o in col.objects:
    if o.name.startswith('SF_footway'):
        wid=o.name.split('_')[2]; P=W[wid]['pts']; segs+=[(a,b,1.3) for a,b in zip(P[:-1],P[1:])]
def hit(x,y):
    if pip(x,y,LOT): return True
    for (ax,ay),(bx,by),hw in segs:
        dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1; t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2))
        if (x-ax-t*dx)**2+(y-ay-t*dy)**2<hw*hw: return True
    # lot edge margin
    for (ax,ay),(bx,by) in zip(LOT,LOT[1:]+LOT[:1]):
        dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1; t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2))
        if (x-ax-t*dx)**2+(y-ay-t*dy)**2<0.36: return True
    return False
for gn in GRASS:
    o=bpy.data.objects.get(gn)
    if not o: continue
    mw=o.matrix_world; me=o.data
    idx=[v.index for v in me.vertices if (lambda p:-75<p.x<95 and 320<p.y<385 and hit(p.x,p.y))(mw@v.co)]
    if not idx: print('SF grass none',gn); continue
    o['sf_orig_mesh']=me.name; nm=me.copy(); nm.name=me.name+'.sf'; o.data=nm; o['sf_culled']=len(idx)
    me.use_fake_user=True
    bm=bmesh.new(); bm.from_mesh(nm); bm.verts.ensure_lookup_table(); bmesh.ops.delete(bm,geom=[bm.verts[i] for i in idx],context='VERTS'); bm.to_mesh(nm); bm.free()
    print('SF grass culled',gn,len(idx),'left',len(nm.vertices))
# ---- cameras
def cam(name,loc,tgt,lens):
    c=bpy.data.cameras.new(name); c.lens=lens; c.clip_end=5000; o=bpy.data.objects.new(name,c); sc.collection.objects.link(o)
    d=Vector(tgt)-Vector(loc); o.location=loc
    o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2); return o
g=gz(30,366) or 139.3; cam('SF_CAM_closeup_lot38_entry',(30,366,g+4.5),(14,344,g+0.2),30)
cam('SF_CAM_oblique_SC_from_NE',(95,425,190),(12,318,143),32)
rc=bpy.data.objects.get('RZ_CAM_eye_SC_from_E')
if rc:
    rc['sf_old']=list(rc.location)+list(rc.rotation_euler)+[rc.data.lens]
    g=gz(56,326) or 139.0; rc.location=(56,326,g+1.65); d=Vector((22,298,g+4))-rc.location
    rc.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2); rc.data.lens=24
    print('SF E cam',tuple(round(a,2) for a in rc.location))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
