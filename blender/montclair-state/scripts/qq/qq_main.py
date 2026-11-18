# qq: Richardson Hall entrances (from OSM footway endpoints 313027431 SW / 313027437 NE), paved apron under the recessed
# ground storey, top-storey gap patch (black 'window' at edge starts), transom raised to clear door heads.
# ALL UNVERIFIED (door positions inferred from OSM footway ends; door design generic 1970s bronze storefront).
# REVERT=1 removes everything in data/qq/added.json and restores the backed-up ground-storey mesh.
import bpy, bmesh, json, os, math
from mathutils import Vector
from mathutils.geometry import intersect_point_line
REV=os.environ.get('REVERT')=='1'; J='data/qq/added.json'; COL='QQ_Richardson_entries_UNVERIFIED'
GS='QP_Richardson_ground_storey_glass_piers_UNVERIFIED'; BAK='QQ_bak_ground_storey_mesh'
def revert():
    if not os.path.exists(J): return
    d=json.load(open(J))
    for n in d['objects']:
        o=bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o,do_unlink=True)
    c=bpy.data.collections.get(COL)
    if c: bpy.data.collections.remove(c)
    g=bpy.data.objects.get(GS); b=bpy.data.meshes.get(BAK)
    if g and b:
        cur=g.data; g.data=b; b.use_fake_user=False; nm=d.get('gs_mesh_name',cur.name); bpy.data.meshes.remove(cur); b.name=nm
    for k in ('meshes','materials','cameras'):
        for n in d[k]:
            x=getattr(bpy.data,k).get(n)
            if x and x.users==0: getattr(bpy.data,k).remove(x)
    print('QQ reverted')
if REV or bpy.data.collections.get(COL): revert()
if not REV:
    before={k:set(x.name for x in getattr(bpy.data,k)) for k in ('objects','meshes','materials','cameras')}
    P=json.load(open('data/qp/rich_poly.json')); OUT=[Vector((x,y,0)) for x,y in P['outer']]; INS=[Vector((x,y,0)) for x,y in P['inset']]
    A=json.load(open('data/qq/apron_mesh.json')); RB=[Vector((x,y,0)) for x,y in A['outer_buf']]
    col=bpy.data.collections.new(COL); bpy.context.scene.collection.children.link(col)
    dg=bpy.context.evaluated_depsgraph_get()
    TER=[bpy.data.objects[n] for n in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km') if n in bpy.data.objects]
    def gz(x,y):
        for T in TER:
            Te=T.evaluated_get(dg); Mi=T.matrix_world.inverted()
            ok,loc,nr,ix=Te.ray_cast(Mi@Vector((x,y,400)),Mi.to_3x3()@Vector((0,0,-1)),depsgraph=dg)
            if ok: return (T.matrix_world@loc).z
        return None
    def nearest_on(ring,p):
        best=None
        for i in range(len(ring)):
            a,b=ring[i],ring[(i+1)%len(ring)]; q,f=intersect_point_line(p,a,b); f=min(max(f,0),1); q=a+(b-a)*f
            dd=(p-q).length
            if best is None or dd<best[0]: best=(dd,q,i)
        return best
    def mat(name,fn):
        m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']; fn(nt,b); return m
    def pavers(nt,b):
        N=nt.nodes; L=nt.links.new; tc=N.new('ShaderNodeTexCoord'); bt=N.new('ShaderNodeTexBrick')
        bt.inputs['Color1'].default_value=(0.46,0.445,0.42,1); bt.inputs['Color2'].default_value=(0.52,0.505,0.48,1); bt.inputs['Mortar'].default_value=(0.30,0.29,0.27,1)
        bt.inputs['Scale'].default_value=1.0; bt.inputs['Mortar Size'].default_value=0.006; bt.inputs['Brick Width'].default_value=0.6; bt.inputs['Row Height'].default_value=0.6; bt.offset=0.0
        L(tc.outputs['Object'],bt.inputs['Vector'])
        nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=1.3; nz.inputs['Detail'].default_value=8; L(tc.outputs['Object'],nz.inputs['Vector'])
        mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=0.3
        L(bt.outputs['Color'],mx.inputs['A']); L(nz.outputs['Color'],mx.inputs['B']); L(mx.outputs['Result'],b.inputs['Base Color'])
        bm=N.new('ShaderNodeBump'); bm.inputs['Strength'].default_value=0.3; bm.inputs['Distance'].default_value=0.003; L(bt.outputs['Fac'],bm.inputs['Height']); L(bm.outputs['Normal'],b.inputs['Normal'])
        b.inputs['Roughness'].default_value=0.9
    def flat(c,r,met=0.0):
        def f(nt,b): b.inputs['Base Color'].default_value=(*c,1); b.inputs['Roughness'].default_value=r; b.inputs['Metallic'].default_value=met
        return f
    M={'pav':mat('QQ_Richardson_apron_pavers_UNVERIFIED',pavers),'curb':mat('QQ_Richardson_apron_curb_concrete',flat((0.42,0.41,0.39),0.9)),
       'dglass':mat('QQ_Richardson_door_glass_UNVERIFIED',flat((0.05,0.048,0.045),0.04)),'frame':bpy.data.materials['QP_Richardson_mullion_bronze'],
       'steel':mat('QQ_Richardson_door_pull_steel',flat((0.6,0.6,0.6),0.25,1.0)),'brick':bpy.data.materials['QP_Richardson_brick_brown_UNVERIFIED'],
       'mat':mat('QQ_Richardson_walkoff_mat',flat((0.05,0.05,0.05),0.95))}
    def newobj(name,keys):
        me=bpy.data.meshes.new(name); o=bpy.data.objects.new(name,me); col.objects.link(o)
        for k in keys: me.materials.append(M[k])
        o['UNVERIFIED_qq']='qq: Richardson entrances/apron (doors at OSM footway ends; design generic)'; return o,bmesh.new(),keys
    def face(bm,keys,pts,k,want=None):
        vs=[bm.verts.new(p) for p in pts]; f=bm.faces.new(vs); f.material_index=keys.index(k); f.normal_update()
        if want is not None and f.normal.dot(want)<0: f.normal_flip()
        return f
    def boxf(bm,keys,c,ax,ay,hx,hy,z0,z1,k):
        cs=[c+ax*sx*hx+ay*sy*hy for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
        for i in range(4):
            a,b=cs[i],cs[(i+1)%4]; o=((a+b)/2-c); o.z=0
            face(bm,keys,[Vector((a.x,a.y,z0)),Vector((b.x,b.y,z0)),Vector((b.x,b.y,z1)),Vector((a.x,a.y,z1))],k,o)
        face(bm,keys,[Vector((p.x,p.y,z1)) for p in cs],k,Vector((0,0,1))); face(bm,keys,[Vector((p.x,p.y,z0)) for p in cs],k,Vector((0,0,-1)))
    def finish(o,bm):
        uvl=bm.loops.layers.uv.new('UVMap')
        for f in bm.faces:
            n=f.normal
            if abs(n.z)<0.5:
                t=Vector((-n.y,n.x,0)).normalized()
                for l in f.loops: l[uvl].uv=(l.vert.co.dot(t),l.vert.co.z)
            else:
                for l in f.loops: l[uvl].uv=(l.vert.co.x,l.vert.co.y)
        bm.to_mesh(o.data); bm.free()
    # ---- 1. apron: ground sampled 0.6 m outside the footprint (terrain has a hole under the building), top = ground + 0.08
    zc={}
    def apz(x,y):
        k=(round(x,1),round(y,1))
        if k not in zc:
            d_,q,i=nearest_on(RB,Vector((x,y,0))); g=gz(q.x,q.y); zc[k]=(g if g is not None else 137.8)+0.08
        return zc[k]
    o,bm,K=newobj('QQ_Richardson_paved_apron_UNVERIFIED',['pav','curb'])
    vs=[bm.verts.new((x,y,apz(x,y))) for x,y in A['V']]
    for f in A['F']:
        try: ff=bm.faces.new([vs[i] for i in f]); ff.material_index=0; ff.normal_update(); 
        except ValueError: continue
        if ff.normal.z<0: ff.normal_flip()
    ext=A['ext']
    for i in range(len(ext)):
        a,b=ext[i],ext[(i+1)%len(ext)]; za,zb=apz(*a),apz(*b)
        face(bm,K,[Vector((a[0],a[1],za)),Vector((b[0],b[1],zb)),Vector((b[0],b[1],zb-0.25)),Vector((a[0],a[1],za-0.25))],'curb',None)
    bm.normal_update()
    # curb faces outward: flip any facing the centroid
    cen=Vector((83.5,263.9,0))
    for f in bm.faces:
        if f.material_index==1:
            c=f.calc_center_median(); v=c-cen; v.z=0
            if f.normal.dot(v)<0: f.normal_flip()
    finish(o,bm); APRON=o
    # ---- 2. top-storey gap patch: qp's punched-window rows start their walls at u=0.8, leaving a 0.8 x 1.9 m hole at every edge start
    o,bm,K=newobj('QQ_Richardson_topstorey_gap_patch_UNVERIFIED',['brick'])
    dsm={ (round(e['from'][0],2),round(e['from'][1],2)): e['dsm_2m_in_med_max'][0] for e in P['edges']}
    np_=0
    for i in range(len(OUT)):
        p0,p1=OUT[i],OUT[(i+1)%len(OUT)]; e=p1-p0; Ln=e.length; t=e/Ln; n=Vector((t.y,-t.x,0))
        dv=dsm.get((round(p0.x,2),round(p0.y,2))) or 0
        tower=dv>155 or (Ln<7 and dv>153)
        if tower or Ln<4.0: continue
        P3=lambda u,z: Vector((p0.x+t.x*u,p0.y+t.y*u,z))
        face(bm,K,[P3(0,147.9),P3(0.8,147.9),P3(0.8,149.8),P3(0,149.8)],'brick',n); np_+=1
    finish(o,bm); print('QQ_GAP_PATCHES',np_)
    # ---- 3. ground storey: back up mesh, raise transom 139.6/139.7 -> 140.25/140.35, drop mullions inside door spans
    g=bpy.data.objects[GS]; gs_name=g.data.name; bk=g.data.copy(); bk.name=BAK; bk.use_fake_user=True
    ENT=[('SW',Vector((74.2,241.1,0))),('NE',Vector((80.4,291.4,0)))]
    doors=[]
    for nm,p in ENT:
        d_,q,i=nearest_on(INS,p); a,b=INS[i],INS[(i+1)%len(INS)]; t=(b-a).normalized(); n=Vector((t.y,-t.x,0))
        # keep the door bay >=1.3 m from the inset corners
        u=(q-a).dot(t); Ln=(b-a).length; u=min(max(u,1.3),Ln-1.3); c=a+t*u
        zf=apz(*(c+n*0.3).xy); doors.append((nm,c,t,n,zf)); print('QQ_DOOR',nm,[round(v,2) for v in c.xy],round(zf,2),'edge',i,round(Ln,2))
    bm=bmesh.new(); bm.from_mesh(g.data); bm.verts.ensure_lookup_table()
    for v in bm.verts:
        if abs(v.co.z-139.6)<1e-3: v.co.z=140.25
        elif abs(v.co.z-139.7)<1e-3: v.co.z=140.35
    kill=set()
    for f in bm.faces:
        mi=f.material_index; 
        if g.data.materials[mi].name!='QP_Richardson_mullion_bronze': continue
        c=f.calc_center_median()
        if abs(c.z-138.45)>0.5 and not (c.z<140.2 and c.z>137): continue
        for nm,dc,t,n,zf in doors:
            rel=c-dc; rel.z=0
            if abs(rel.dot(t))<1.15 and abs(rel.dot(n))<0.2: kill.add(f)
    # only delete whole vertical mullion boxes (all faces of a box share verts; delete verts of killed faces that are tall)
    kv=set(v for f in kill for v in f.verts if (max(x.co.z for x in f.verts)-min(x.co.z for x in f.verts))>1.0 or True)
    tall=set()
    for f in kill:
        zs=[v.co.z for v in f.verts]
        if max(zs)-min(zs)>3.0: tall.update(f.verts)
    # remove boxes: verts connected to tall-face verts
    rm=set()
    for v in tall:
        rm.add(v)
        for e in v.link_edges: rm.add(e.other_vert(v))
    bmesh.ops.delete(bm,geom=list(rm),context='VERTS'); bm.to_mesh(g.data); bm.free(); print('QQ_MULLION_VERTS_DELETED',len(rm))
    # ---- 4. door assemblies: pair of 0.95 x 2.3 m bronze-framed glass leaves, push bars, threshold, walk-off mat, head frame to the transom
    o,bm,K=newobj('QQ_Richardson_entrance_doors_UNVERIFIED',['dglass','frame','steel','mat','curb'])
    for nm,c,t,n,zf in doors:
        H=2.3; W=0.95; zt=zf+H
        P=lambda u,dn,z: Vector((c.x+t.x*u+n.x*dn,c.y+t.y*u+n.y*dn,z))
        for s in (-1,1):
            u0,u1=(0,W) if s>0 else (-W,0)
            face(bm,K,[P(u0,0.035,zf),P(u1,0.035,zf),P(u1,0.035,zt),P(u0,0.035,zt)],'dglass',n)
            uc=(u0+u1)/2
            for (ua,ub,za,zb) in ((u0,u0+0.11,zf,zt),(u1-0.11,u1,zf,zt),(u0,u1,zt-0.11,zt),(u0,u1,zf,zf+0.26)):
                boxf(bm,K,P((ua+ub)/2,0.07,0),t,n,(ub-ua)/2,0.035,za,zb,'frame')
            # horizontal push bar on standoffs, near the meeting stiles
            ub=-0.12*s if False else 0
            bu=(u1-0.55) if s>0 else (u0+0.55)
            boxf(bm,K,P(bu,0.20,0),t,n,0.36,0.018,zf+1.0,zf+1.04,'steel')
            for du in (-0.3,0.3): boxf(bm,K,P(bu+du,0.14,0),t,n,0.015,0.05,zf+1.0,zf+1.04,'steel')
        # head frame up to the transom + side jambs
        boxf(bm,K,P(0,0.07,0),t,n,W+0.06,0.05,zt,140.25,'frame')
        for uu in (-W-0.03,W+0.03): boxf(bm,K,P(uu,0.07,0),t,n,0.05,0.06,zf,140.25,'frame')
        # threshold + walk-off mat on the apron in front
        boxf(bm,K,P(0,0.15,0),t,n,W,0.12,zf,zf+0.015,'steel')
        boxf(bm,K,P(0,0.95,0),t,n,1.1,0.65,zf,zf+0.012,'mat')
    finish(o,bm)
    # ---- 5. close-up camera on the SW entrance (also shows the patched top-storey corner)
    nm,c,t,n,zf=doors[0]
    loc=c+n*13.0+t*4.0; g0=gz(loc.x,loc.y); loc.z=(g0 if g0 else zf)+1.65
    cd=bpy.data.cameras.new('QQ_CAM_closeup_richardson_SW_entrance'); cd.lens=24; cd.clip_end=3000
    co=bpy.data.objects.new('QQ_CAM_closeup_richardson_SW_entrance',cd); col.objects.link(co); co.location=loc
    tg=Vector((c.x+t.x*0.5,c.y+t.y*0.5,zf+3.0)); co.rotation_euler=(tg-loc).to_track_quat('-Z','Y').to_euler()
    print('QQ_CAM',[round(v,2) for v in loc])
    after={k:set(x.name for x in getattr(bpy.data,k)) for k in before}
    d={k:sorted(after[k]-before[k]) for k in before}; d['meshes']=[m for m in d['meshes'] if m!=BAK]; d['gs_mesh_name']=gs_name
    json.dump(d,open(J,'w'),indent=0); print('QQ built',{k:len(v) for k,v in d.items() if isinstance(v,list)})
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QQSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
elif os.environ.get('QQSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QQSAVEAS'],copy=True); print('SAVED_AS')
