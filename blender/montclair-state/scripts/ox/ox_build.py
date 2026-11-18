# ox (UNVERIFIED, removable; REVERT=1 undoes): CELS walk/road edge in the ow2 box (x121-141, y201-218), local only:
#  (A) scoring/control joints: thin dark decal strips cut across the EVALUATED walk at 1.52 m (5 ft) spacing along the walk's main axis (shared walk material untouched)
#  (B) smoothed continuous lip ribbon replacing the per-edge OW3 lip (OW3 object hidden, not deleted; mitred, Laplacian-smoothed path -> no kink/step)
#  (C) feathered grime band just outside the walk edge (alpha fade over 22 cm on road/lawn), softens the wavy tip
import bpy, os, sys, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='OX_walk_joints_lip_feather_20261101ox_UNVERIFIED'; MATS=['OX_walk_joint_dark_UNVERIFIED','OX_lip_worn_concrete_UNVERIFIED','OX_walk_edge_grime_feather_UNVERIFIED']
OW3='OW3_CELS_walk_road_curb_lip_UNVERIFIED'
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects):
        d=o.data; bpy.data.objects.remove(o)
        if d and d.users==0:
            (bpy.data.meshes if isinstance(d,bpy.types.Mesh) else bpy.data.cameras).remove(d)
    bpy.data.collections.remove(c)
for mn in MATS:
    m=bpy.data.materials.get(mn)
    if m and m.users==0: bpy.data.materials.remove(m)
lo=bpy.data.objects[OW3]
if 'ox_prev_hide' in lo.keys():
    lo.hide_render,lo.hide_viewport=bool(lo['ox_prev_hide'][0]),bool(lo['ox_prev_hide'][1]); del lo['ox_prev_hide']
if REV:
    print('REVERTED_OX')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
JS=float(os.environ.get('JS','1.524')); JW=float(os.environ.get('JW','0.016')); LW=float(os.environ.get('LW','0.10')); FW=float(os.environ.get('FW','0.22'))
SM=int(os.environ.get('SM','80')); CL=float(os.environ.get('CL','0.02')); CO=float(os.environ.get('CO','0.06')); NW=int(os.environ.get('NW','6'))
X0,X1,Y0,Y1=121,141,201,218
F=bpy.data.objects['Footpaths_OSM']; T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; R=bpy.data.objects['Roads_OSM']
dg=bpy.context.evaluated_depsgraph_get()
def caster(o):
    e=o.evaluated_get(dg); mi=o.matrix_world.inverted(); mw=o.matrix_world
    def f(p):
        ok,loc,n,i=e.ray_cast(mi@Vector((p.x,p.y,p.z+30)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
        return (mw@loc).z if ok else None
    return f
dtm=caster(T); road=caster(R)
def ground(p):
    zs=[z for z in (dtm(p),road(p)) if z is not None and z<p.z+0.5]
    return max(zs) if zs else p.z-0.05
fe=F.evaluated_get(dg); me=fe.to_mesh(); bm=bmesh.new(); bm.from_mesh(me); bm.transform(F.matrix_world); fe.to_mesh_clear()
# local walk patch: faces with centre in the box
kill=[f for f in bm.faces if not(X0-1<=f.calc_center_median().x<=X1+1 and Y0-1<=f.calc_center_median().y<=Y1+1)]
bmesh.ops.delete(bm,geom=kill,context='FACES')
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
wbvh=BVHTree.FromBMesh(bm)
def walkz(p):
    loc,n,i,d=wbvh.ray_cast(Vector((p.x,p.y,p.z+2)),Vector((0,0,-1)))
    return loc.z if loc else None
# ---- boundary chains (true walk boundary: original boundary edges only inside the inner box) ----
inner=lambda v:(X0<=v.x<=X1 and Y0<=v.y<=Y1)
bed=[e for e in bm.edges if len(e.link_faces)==1 and inner((e.verts[0].co+e.verts[1].co)/2) and (e.verts[0].co-e.verts[1].co).length>1e-4]
# drop edges created by the box cut (they lie near the outer selection limit, never inside the inner box) -> already excluded by inner()
adj={}
for e in bed:
    for v in e.verts: adj.setdefault(v.index,[]).append(e)
used=set(); chains=[]
def walk_chain(e0,v0):
    ch=[v0]; e=e0; v=v0
    while True:
        used.add(e.index); w=e.other_vert(bm.verts[v]).index; ch.append(w)
        nxt=[x for x in adj.get(w,[]) if x.index not in used]
        if len(adj.get(w,[]))!=2 or not nxt: return ch,e
        e=nxt[0]; v=w
for v,es in adj.items():
    if len(es)!=2:
        for e in es:
            if e.index not in used: chains.append(walk_chain(e,v)[0])
for e in bed:
    if e.index not in used: chains.append(walk_chain(e,e.verts[0].index)[0])
def inward(a,b,fc):
    t=b-a; t.z=0; t.normalize(); n=Vector((-t.y,t.x,0))
    return n if n.dot(fc-(a+b)/2)>=0 else -n
# edge -> face centre lookup
efc={}
for e in bed: efc[frozenset((e.verts[0].index,e.verts[1].index))]=e.link_faces[0].calc_center_median()
lip=bmesh.new(); fea=bmesh.new(); fuv=[]; nlip=0; maxd=0
for ch in chains:
    closed=len(ch)>3 and ch[0]==ch[-1]
    P0=[bm.verts[i].co.copy() for i in ch]; P=[p.copy() for p in P0]; N=len(P)
    if N<2: continue
    N0=[]; REFS=[]
    for i in range(N):
        j=min(i,N-2); fc=efc.get(frozenset((ch[j],ch[j+1])))
        ia=max(i-NW,0); ib=min(i+NW,N-1); t=P0[ib]-P0[ia]; t.z=0
        t=t.normalized() if t.length>1e-6 else Vector((1,0,0)); n=Vector((-t.y,t.x,0))
        ref=inward(P0[j],P0[j+1],fc) if fc is not None else n
        N0.append(n if n.dot(ref)>=0 else -n); REFS.append(ref)
    for i in range(1,N):   # continuity: a jog edge's own inward normal is ambiguous, keep the chain's side consistent
        if N0[i].dot(N0[i-1])<0: N0[i]=-N0[i]
    if sum(1 for i in range(N) if N0[i].dot(REFS[i])>=0)<N/2: N0=[-n for n in N0]
    for it in range(SM):
        Q=[p.copy() for p in P]
        for i in range(N):
            if (i==0 or i==N-1) and not closed: continue
            a=P[i-1] if i>0 else P[N-2]; b=P[i+1] if i<N-1 else P[1]
            Q[i]=P[i]*0.5+(a+b)*0.25
        for i in range(N):
            d=Q[i]-P0[i]; d.z=0; n0=N0[i]; din=d.dot(n0); dt=d-n0*din
            if din>CL: din=CL           # never pull the lip more than CL into the walk (no walk teeth showing outside)
            if din<-CO: din=-CO         # outward (onto lawn/road) up to CO
            if dt.length>CO: dt=dt.normalized()*CO
            d=n0*din+dt; zq=max(Q[i].z,P0[i].z); Q[i]=Vector((P0[i].x+d.x,P0[i].y+d.y,zq))
        P=Q
    if os.environ.get('DBG'):
        print('CH',N,closed,tuple(round(x,2) for x in P0[0]),tuple(round(x,2) for x in P0[-1]))
        for i in range(1,N-1):
            a=P0[i]-P0[i-1]; b=P0[i+1]-P0[i]; a.z=0; b.z=0
            if a.length>1e-4 and b.length>1e-4 and math.degrees(a.angle(b))>25: print('  SHARP',i,tuple(round(x,2) for x in P0[i]),round(math.degrees(a.angle(b))),round(a.length,3),round(b.length,3),'dz',round(P0[i+1].z-P0[i-1].z,3))
    if os.environ.get('DBG2') and N==546:
        for i in range(462,484): print('PP',i,tuple(round(x,3) for x in P0[i]),tuple(round(x,3) for x in P[i]),tuple(round(x,2) for x in N0[i]))
    for i in range(N): maxd=max(maxd,(Vector((P[i].x,P[i].y,0))-Vector((P0[i].x,P0[i].y,0))).length)
    # per-point inward normal from neighbouring edges (sign from the original link face)
    NI=[]
    for i in range(N):
        ia=max(i-1,0); ib=min(i+1,N-1)
        t=P[ib]-P[ia]; t.z=0
        if t.length<1e-6: t=Vector((1,0,0))
        t.normalize(); n=Vector((-t.y,t.x,0))
        j=min(i,N-2); fc=efc.get(frozenset((ch[j],ch[j+1])))
        ref=inward(P0[j],P0[j+1],fc) if fc is not None else n
        NI.append(n if n.dot(N0[i])>=0 else -n)
    top_o=[];top_i=[];bot=[];fo=[];fi=[]
    for i in range(N):
        p=P[i]; n=NI[i]
        o=p-n*0.015; o.z=p.z+0.012
        ii=p+n*LW; wz=walkz(ii); ii.z=(wz if wz is not None else p.z)+0.012
        bz=min(dtm(p) or p.z,P0[i].z)-0.06
        top_o.append(lip.verts.new(o)); top_i.append(lip.verts.new(ii)); bot.append(lip.verts.new(Vector((o.x,o.y,bz))))
        f0=p-n*0.012; f0.z=ground(f0)+0.008; f1=p-n*FW; f1.z=ground(f1)+0.008
        fi.append(fea.verts.new(f0)); fo.append(fea.verts.new(f1))
    for i in range(N-1):
        lip.faces.new((top_o[i],top_o[i+1],top_i[i+1],top_i[i])); lip.faces.new((bot[i],bot[i+1],top_o[i+1],top_o[i]))
        fuv.append(fea.faces.new((fi[i],fi[i+1],fo[i+1],fo[i])))
    nlip+=N
# feather uv: u across (0 at walk edge -> 1 outside)
uvl=fea.loops.layers.uv.new('UVMap')
for f in fea.faces:
    for k,l in enumerate(f.loops): l[uvl].uv=(0.0 if k in (0,1) else 1.0, 0.0)
# ---- joints ----
xs=[v.co for v in bm.verts if inner(v.co)]
mx=sum(v.x for v in xs)/len(xs); my=sum(v.y for v in xs)/len(xs)
sxx=sum((v.x-mx)**2 for v in xs); syy=sum((v.y-my)**2 for v in xs); sxy=sum((v.x-mx)*(v.y-my) for v in xs)
ang=0.5*math.atan2(2*sxy,sxx-syy); ax=Vector((math.cos(ang),math.sin(ang),0))
if os.environ.get('JAX'): a=math.radians(float(os.environ['JAX'])); ax=Vector((math.cos(a),math.sin(a),0))
jb=bm.copy(); geom=jb.verts[:]+jb.edges[:]+jb.faces[:]
segs=[]
AXES=[ax,Vector((-ax.y,ax.x,0))] if os.environ.get('JGRID','1')=='1' else [ax]   # 5-ft square panels (both directions)
for axk in AXES:
    pr=[axk.dot(Vector((v.co.x,v.co.y,0))) for v in jb.verts]; k0=math.ceil(min(pr)/JS); k1=math.floor(max(pr)/JS)
    for k in range(k0,k1+1):
        r=bmesh.ops.bisect_plane(jb,geom=jb.verts[:]+jb.edges[:]+jb.faces[:],dist=1e-5,plane_co=axk*(k*JS),plane_no=axk)
        for g in r['geom_cut']:
            if isinstance(g,bmesh.types.BMEdge) and len(g.link_faces)>=1: segs.append((g.verts[0].co.copy(),g.verts[1].co.copy(),axk))
jb.free()
# keep segments inside the inner box and >= 6 cm inside the walk edge (lip covers the rest)
bed_xy=[((e.verts[0].co.x,e.verts[0].co.y),(e.verts[1].co.x,e.verts[1].co.y)) for e in bed]
ebvh=BVHTree.FromPolygons([e.verts[0].co.copy() for e in bed]+[e.verts[1].co.copy() for e in bed]+[(e.verts[0].co+Vector((0,0,0.001))) for e in bed],[(i,i+len(bed),i+2*len(bed)) for i in range(len(bed))]) if bed else None
jt=bmesh.new(); nj=0
for a,b,axk in segs:
    w=axk*(JW/2)
    m=(a+b)/2
    if not inner(m): continue
    if ebvh:
        hit=ebvh.find_nearest(m,0.06)
        if hit[0] is not None: continue
    l=Vector((0,0,0.005))
    vs=[jt.verts.new(x) for x in (a-w+l,b-w+l,b+w+l,a+w+l)]; jt.faces.new(vs); nj+=1
bm.free()
def mk(name,bmx,mat):
    mesh=bpy.data.meshes.new(name); bmesh.ops.remove_doubles(bmx,verts=bmx.verts,dist=0.002) if name.endswith('joints') else None; bmx.to_mesh(mesh); bmx.free(); mesh.materials.append(mat)
    o=bpy.data.objects.new(name+'_UNVERIFIED',mesh); col.objects.link(o); o['UNVERIFIED_ox']='no photo of this walk end'; return o
def mat_joint():
    m=bpy.data.materials.new(MATS[0]); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.08,0.077,0.072,1); b.inputs['Roughness'].default_value=0.95; return m
def mat_lip():
    m=bpy.data.materials.new(MATS[1]); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    noi=nt.nodes.new('ShaderNodeTexNoise'); noi.inputs['Scale'].default_value=9; noi.inputs['Detail'].default_value=8
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(0.20,0.195,0.185,1); ramp.color_ramp.elements[1].color=(0.34,0.33,0.31,1)
    nt.links.new(noi.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],b.inputs['Base Color']); b.inputs['Roughness'].default_value=0.9
    bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.25; nt.links.new(noi.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal']); return m
def mat_fea():
    m=bpy.data.materials.new(MATS[2]); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']; out=nt.nodes['Material Output']
    b.inputs['Base Color'].default_value=(0.10,0.09,0.075,1); b.inputs['Roughness'].default_value=1.0
    uv=nt.nodes.new('ShaderNodeUVMap'); uv.uv_map='UVMap'; sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(uv.outputs['UV'],sep.inputs['Vector'])
    mr=nt.nodes.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value=0.42; mr.inputs['To Max'].default_value=0.0; nt.links.new(sep.outputs['X'],mr.inputs['Value'])
    noi=nt.nodes.new('ShaderNodeTexNoise'); noi.inputs['Scale'].default_value=14; noi.inputs['Detail'].default_value=6
    mul=nt.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'; nt.links.new(mr.outputs['Result'],mul.inputs[0]); nt.links.new(noi.outputs['Fac'],mul.inputs[1])
    mul2=nt.nodes.new('ShaderNodeMath'); mul2.operation='MULTIPLY'; mul2.inputs[1].default_value=1.4; mul2.use_clamp=True; nt.links.new(mul.outputs[0],mul2.inputs[0])
    tr=nt.nodes.new('ShaderNodeBsdfTransparent'); mx=nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(mul2.outputs[0],mx.inputs['Fac']); nt.links.new(tr.outputs[0],mx.inputs[1]); nt.links.new(b.outputs[0],mx.inputs[2]); nt.links.new(mx.outputs[0],out.inputs['Surface'])
    return m
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
oj=mk('OX_CELS_walk_scoring_joints',jt,mat_joint()); ol=mk('OX_CELS_walk_road_lip_smoothed',lip,mat_lip()); of=mk('OX_CELS_walk_edge_grime_feather',fea,mat_fea())
for o in (oj,of): o.visible_shadow=False
for p in ol.data.polygons: p.use_smooth=False
lo['ox_prev_hide']=[int(lo.hide_render),int(lo.hide_viewport)]; lo.hide_render=True; lo.hide_viewport=True
print('OX chains',len(chains),'lip pts',nlip,'max xy shift %.3f'%maxd,'joint axis deg %.1f'%math.degrees(math.atan2(ax.y,ax.x)),'joint segs',nj,'feather faces',len(of.data.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
