# tr (Nov 5 2026 ~2:25 AM ET, MAIN, day 8 Student Center east edge). ALL UNVERIFIED, reversible (REVERT=1).
# (1) Blanton infill: Blanton-only copy of TM_dorm_wall_streaked darkened/warmed to cream-grey concrete between TN piers.
# (2) Stone window sills + darker reveals: Stone-only TQ copy + small projecting sill boxes.
# (3) Stone grey block base: shorten plinth (0.95 -> 0.38 m) and re-tone to buff-matched.
# (4) Walk west of Stone: drape OSM 546643369 south gap from QS south end to the Footpaths/CELS junction.
import bpy, bmesh, os, json, math
from mathutils import Vector
from mathutils.kdtree import KDTree
REV=os.environ.get('REVERT')=='1'
D='/workspace/nj-scenes/montclair-state/'
BLANTON=['TI_Blanton_Hall_313029108_lower_UNVERIFIED','TI_Blanton_Hall_313029108_upper0_UNVERIFIED']
STONE=['TI_Stone_Hall_313028565_lower_UNVERIFIED','TI_Stone_Hall_313028565_upper0_UNVERIFIED']
SRC_B='TM_dorm_wall_streaked_UNVERIFIED'; NEW_B='TR_Blanton_infill_cream_UNVERIFIED'
SRC_S='TQ_Stone_buff_brick_UNVERIFIED'; NEW_S='TR_Stone_brick_detail_UNVERIFIED'
CN='TR_east_dorms_polish_UNVERIFIED'
SILL_MAT='TR_Stone_sill_UNVERIFIED'
WALK_NAME='TR_footway_546643369_S_gap_UNVERIFIED'

def revert():
    for n in BLANTON+STONE:
        o=bpy.data.objects.get(n)
        if not o: continue
        if 'tr_orig_mat' in o:
            want=o['tr_orig_mat']
            for s in o.material_slots:
                if s.material and s.material.name in (NEW_B,NEW_S):
                    s.material=bpy.data.materials.get(want) or s.material
            del o['tr_orig_mat']
    for o in [o for o in bpy.data.objects if 'tr_obj' in o]:
        me=o.data; t=o.type; bpy.data.objects.remove(o)
        if me and me.users==0:
            if t=='MESH': bpy.data.meshes.remove(me)
            elif t=='CAMERA': bpy.data.cameras.remove(me)
    c=bpy.data.collections.get(CN)
    if c: bpy.data.collections.remove(c)
    for n in (NEW_B,NEW_S,SILL_MAT):
        m=bpy.data.materials.get(n)
        if m: bpy.data.materials.remove(m)
    print('TR reverted')

revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

sc=bpy.context.scene
col=bpy.data.collections.new(CN); sc.collection.children.link(col); col['tr_obj']=1

# ---------- 1) Blanton infill tone (Blanton-only material copy) ----------
srcB=bpy.data.materials[SRC_B]; mB=srcB.copy(); mB.name=NEW_B; NB=mB.node_tree.nodes
# darken/warm the base ramps to finished 1980s cream-grey cladding (darker than TN piers ~0.55-0.64)
for nm in ('Color Ramp','Color Ramp.001'):
    n=NB.get(nm)
    if not n: continue
    # warm mid-grey concrete
    if nm=='Color Ramp':
        n.color_ramp.elements[0].color=(0.26,0.24,0.20,1)
        n.color_ramp.elements[1].color=(0.36,0.33,0.28,1)
    else:
        n.color_ramp.elements[0].color=(0.22,0.20,0.17,1)
        n.color_ramp.elements[1].color=(0.32,0.29,0.25,1)
# warm multiply on Base Color so infill reads clearly darker than TN piers
b=NB['Principled BSDF']; src=b.inputs['Base Color'].links[0].from_socket
mxd=mB.node_tree.nodes.new('ShaderNodeMix'); mxd.data_type='RGBA'; mxd.blend_type='MULTIPLY'; mxd.inputs['Factor'].default_value=1.0
mxd.inputs['B'].default_value=(0.72,0.68,0.60,1)
mB.node_tree.links.new(src, mxd.inputs['A']); mB.node_tree.links.new(mxd.outputs['Result'], b.inputs['Base Color'])
# slightly stronger vertical streak multiply if present
mx8=NB.get('Mix.008')
if mx8 and mx8.blend_type=='MULTIPLY':
    try: mx8.inputs['Factor'].default_value=min(1.0, mx8.inputs['Factor'].default_value*1.15)
    except Exception: pass
# darker deep-set glass / reveal so pale wall doesn't wash the openings
for nm,col_ in (('Mix.003',(0.12,0.11,0.10,1)),('Mix.004',(0.03,0.035,0.04,1))):
    n=NB.get(nm)
    if n:
        try: n.inputs['B'].default_value=col_
        except Exception: pass
srcB.use_fake_user=True
for n in BLANTON:
    o=bpy.data.objects[n]
    for s in o.material_slots:
        if s.material and s.material.name==SRC_B:
            o['tr_orig_mat']=SRC_B; s.material=mB
print('TR Blanton infill applied')

# ---------- 2+3) Stone brick detail: short buff plinth + sill/reveal shader + geometry sills ----------
srcS=bpy.data.materials[SRC_S]; mS=srcS.copy(); mS.name=NEW_S; NS=mS.node_tree.nodes; LS=mS.node_tree.links
# shorten base band 0.95 -> 0.38 m
lt=NS.get('Math.049')
if lt and lt.operation=='LESS_THAN':
    lt.inputs[1].default_value=0.38
# re-tone base Color Ramp.001 to buff-matched (was cold grey)
crb=NS.get('Color Ramp.001')
if crb:
    crb.color_ramp.elements[0].color=(0.46,0.38,0.27,1)
    crb.color_ramp.elements[1].color=(0.54,0.45,0.32,1)
# darker inset reveal around the frame (Mix.003 is frame/reveal colour in the chain; deepen bump recess)
# TQ uses Mix.003 for aluminium frame; keep frame aluminium, add a darker reveal multiply before glass via Mix.002 sill path
# Strengthen procedural sill tone (Mix.002) toward concrete ledge
ms=NS.get('Mix.002')
if ms:
    try: ms.inputs['B'].default_value=(0.42,0.40,0.36,1)
    except Exception: pass
# deepen window recess bump
bp=NS.get('Bump')
if bp:
    bp.inputs['Strength'].default_value=max(bp.inputs['Strength'].default_value,0.85)
    bp.inputs['Distance'].default_value=max(bp.inputs['Distance'].default_value,0.11)
# darker glass for clearer punched openings
mg=NS.get('Mix.004')
if mg:
    try: mg.inputs['B'].default_value=(0.03,0.035,0.04,1)
    except Exception: pass
srcS.use_fake_user=True
for n in STONE:
    o=bpy.data.objects[n]
    for s in o.material_slots:
        if s.material and s.material.name==SRC_S:
            o['tr_orig_mat']=SRC_S; s.material=mS
print('TR Stone shader (plinth+reveal) applied')

# geometry sills under punched windows (TI bay 3.3 m, opening fu 0.30..0.70, bottom at Z0+0.95+j*F)
sm=bpy.data.materials.new(SILL_MAT); sm.use_nodes=True; SN=sm.node_tree.nodes; SL=sm.node_tree.links; sb=SN['Principled BSDF']
stc=SN.new('ShaderNodeTexCoord'); snz=SN.new('ShaderNodeTexNoise'); snz.inputs['Scale'].default_value=4.0; snz.inputs['Detail'].default_value=4
SL.new(stc.outputs['Object'],snz.inputs['Vector'])
scr=SN.new('ShaderNodeValToRGB'); scr.color_ramp.elements[0].color=(0.40,0.38,0.34,1); scr.color_ramp.elements[1].color=(0.52,0.50,0.46,1)
SL.new(snz.outputs['Fac'],scr.inputs[0]); SL.new(scr.outputs['Color'],sb.inputs['Base Color'])
sb.inputs['Roughness'].default_value=0.7; sb.inputs['Specular IOR Level'].default_value=0.25
BAY=3.3; bmS=bmesh.new(); nsill=0
def sbox(bm,c,u,n,hw,d0,d1,z0,z1):
    # sill slab: from d0 (into wall) to d1 (proud); hw half-width along u
    vs=[]
    for a,b,z in ((-hw,d0,z0),(hw,d0,z0),(hw,d1,z0),(-hw,d1,z0),(-hw,d0,z1),(hw,d0,z1),(hw,d1,z1),(-hw,d1,z1)):
        p=c+u*a+n*b; vs.append(bm.verts.new((p.x,p.y,z)))
    fcs=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    for idxs in fcs:
        try: bm.faces.new([vs[i] for i in idxs])
        except ValueError: pass
objs=[bpy.data.objects[n] for n in STONE]
lo=[o for o in objs if '_lower_' in o.name][0]
lo_top=max((lo.matrix_world@v.co).z for v in lo.data.vertices)
for o in objs:
    me=o.data; mw=o.matrix_world; V=me.vertices
    dirs=me.attributes['ti_dir'].data; fl=me.attributes['ti_floor'].data
    za=me.attributes['ti_z0'].data; zt=me.attributes['ti_z1'].data
    upper='_upper' in o.name
    for p in me.polygons:
        if abs(p.normal.z)>0.3 or p.material_index!=0: continue
        ws=[mw@V[i].co for i in p.vertices]; zmin=min(w.z for w in ws); zmax=max(w.z for w in ws)
        if zmax-zmin<2.0: continue
        u=Vector(dirs[p.index].vector); u.z=0
        if u.length<0.5: continue
        u.normalize(); nvec=(mw.to_3x3()@p.normal); nvec.z=0
        if nvec.length<0.3: continue
        nvec.normalize()
        if abs(u.dot(nvec))>0.25: continue
        ss=[w.to_2d().dot(u.to_2d()) for w in ws]; s0,s1=min(ss),max(ss)
        if s1-s0<2.5: continue
        cen=mw@p.center; base=cen-u*(cen.to_2d().dot(u.to_2d())); base.z=0
        F=fl[p.index].value; Z0=za[p.index].value; Z1=zt[p.index].value
        # bay centres with window openings (fu 0.30..0.70 -> centre at .5)
        k0=math.ceil((s0+0.2)/BAY); k1=math.floor((s1-0.2)/BAY)
        j=0
        while True:
            zw=Z0+0.95+j*F   # window bottom (TI sill line)
            if zw>Z1-0.9: break
            if (not upper and zw>=lo_top-0.2) or (upper and zw<lo_top-0.1):
                j+=1; continue
            if zw<zmin+0.2 or zw>zmax-0.4:
                j+=1; continue
            for k in range(k0,k1+1):
                s=k*BAY+0.5*BAY   # bay centre
                if s<s0+0.4 or s>s1-0.4: continue
                c=base+u*s; c.z=0
                # sill: 1.40 m wide (opening 1.32 + lips), 8 cm thick, projects 7 cm, seats 2 cm into wall
                sbox(bmS,c,u,nvec,0.70,-0.02,0.07,zw-0.06,zw+0.02); nsill+=1
            j+=1
meS=bpy.data.meshes.new('TR_Stone_window_sills_UNVERIFIED'); bmS.to_mesh(meS); bmS.free(); meS.materials.append(sm)
for p in meS.polygons: p.use_smooth=False
oS=bpy.data.objects.new('TR_Stone_window_sills_UNVERIFIED',meS); col.objects.link(oS); oS['tr_obj']=1
oS['UNVERIFIED']='Stone projecting window sills after 1965/66 slides; bay/size guessed from TI 3.3 m grid'
print('TR Stone sills',nsill,'faces',len(meS.polygons))

# ---------- 4) Walk west of Stone: fill OSM 546643369 south gap ----------
dg=bpy.context.evaluated_depsgraph_get()
SD=json.load(open(D+'data/scene_data.json')); F={str(f['id']):f for f in SD['features']}
pts=[tuple(p[:2]) for p in F['546643369']['pts']]
# resample full centreline
S=[]
for (ax,ay),(bx,by) in zip(pts[:-1],pts[1:]):
    L=math.hypot(bx-ax,by-ay); n=max(1,int(L/0.75))
    for i in range(n): t=i/n; S.append((ax+(bx-ax)*t,ay+(by-ay)*t))
S.append(pts[-1])
# existing concrete walk verts (QS+QW for this way + Footpaths near)
exist=[]
for nm in ('QS_footway_546643369_UNVERIFIED','QW_footway_546643369_ext_UNVERIFIED','Footpaths_OSM'):
    o=bpy.data.objects.get(nm)
    if not o: continue
    mw=o.matrix_world
    for v in o.data.vertices:
        p=mw@v.co
        if 60<p.x<200 and 200<p.y<360: exist.append(p)
kd=KDTree(max(1,len(exist)))
for i,p in enumerate(exist): kd.insert((p.x,p.y,0),i)
kd.balance()
# Stone footprint to keep clear of interior (allow 0.6 m outside)
stone_poly=F['313028565']['pts']
def pip(x,y,poly):
    ins=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i][0],poly[i][1]; x2,y2=poly[(i+1)%n][0],poly[(i+1)%n][1]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
def near_poly(x,y,poly,r=0.5):
    # inside or within r of an edge
    if pip(x,y,poly): return True
    for (ax,ay),(bx,by) in zip(poly,poly[1:]+poly[:1]):
        dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy or 1
        t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2))
        if (x-ax-t*dx)**2+(y-ay-t*dy)**2<r*r: return True
    return False
qs=bpy.data.objects.get('QS_footway_546643369_UNVERIFIED')
qw=bpy.data.objects.get('QW_footway_546643369_ext_UNVERIFIED')
qs_south=None; qw_north=None
if qs:
    mw=qs.matrix_world; sv=[mw@v.co for v in qs.data.vertices]
    qs_south=min(sv, key=lambda v:v.y)
if qw:
    mw=qw.matrix_world; sv=[mw@v.co for v in qw.data.vertices]
    qw_north=max(sv, key=lambda v:v.y)
# SOUTH gap west of Stone + NE free end past QW (OSM continues to y~391)
flag=[False]*len(S)
for i,(x,y) in enumerate(S):
    south=112<x<155 and 218<y<256
    north=150<x<200 and 348<y<395
    if not (south or north): continue
    if near_poly(x,y,stone_poly,0.30): continue
    # prefer missing stretches; allow join samples near QS/QW ends
    d=kd.find((x,y,0))[2]
    join=False
    if qs_south and math.hypot(x-qs_south.x,y-qs_south.y)<5.0: join=True
    if qw_north and math.hypot(x-qw_north.x,y-qw_north.y)<5.0: join=True
    if d>=1.15 or join: flag[i]=True
runs=[]; cur=[]
for i,k in enumerate(flag):
    if k: cur.append(i)
    elif cur: runs.append(cur); cur=[]
if cur: runs.append(cur)
# ground
GN=['Terrain_LiDAR_DTM_1m','QJ_NE_seam_fill_UNVERIFIED','Context_skirt_3DEP_ortho_4km','QM_terrain_band_underlay_UNVERIFIED','QW_north_edge_ramp_UNVERIFIED']
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
def gz(x,y):
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
matw=qs.material_slots[0].material if qs and qs.material_slots else bpy.data.materials.get('QT_walk_concrete_joints_UNVERIFIED')
w=2.0; off=0.05; nq=0; bm=bmesh.new(); info=[]
ks=None
sv=[]
for o in (qs,qw):
    if not o: continue
    mw=o.matrix_world; sv += [mw@v.co for v in o.data.vertices]
if sv:
    ks=KDTree(len(sv))
    for i,p in enumerate(sv): ks.insert(p,i)
    ks.balance()
for r in runs:
    if len(r)<3: continue
    # optionally prepend/append a join index toward QS
    idx=list(r)
    rows=[]; cl=[0.0]
    for jj,i in enumerate(idx):
        x,y=S[i]; a=S[max(i-1,0)]; b=S[min(i+1,len(S)-1)]
        tx,ty=b[0]-a[0],b[1]-a[1]; l=math.hypot(tx,ty) or 1; nx,ny=-ty/l,tx/l
        Lp=(x+nx*w/2,y+ny*w/2); Rp=(x-nx*w/2,y-ny*w/2)
        zs=[z for z in (gz(*Lp),gz(x,y),gz(*Rp)) if z is not None]
        if not zs: rows.append(None); continue
        z=max(zs)+off
        vL=Vector((Lp[0],Lp[1],z)); vR=Vector((Rp[0],Rp[1],z))
        if ks:
            for vv in (vL,vR):
                co,_,dd=ks.find(vv)
                if dd<0.7: vv.x,vv.y,vv.z=co.x,co.y,co.z
        rows.append([bm.verts.new(vL),bm.verts.new(vR),bm.verts.new((vL.x,vL.y,vL.z-0.3)),bm.verts.new((vR.x,vR.y,vR.z-0.3))])
        if jj: cl.append(cl[-1]+math.hypot(S[idx[jj]][0]-S[idx[jj-1]][0],S[idx[jj]][1]-S[idx[jj-1]][1]))
    # taper free (non-QS) end ~3 m
    # detect which end is nearer QS
    def near_end(ii):
        x,y=S[ii]
        if qs_south and math.hypot(x-qs_south.x,y-qs_south.y)<5.0: return True
        if qw_north and math.hypot(x-qw_north.x,y-qw_north.y)<5.0: return True
        return False
    freeA=not near_end(idx[0]); freeB=not near_end(idx[-1])
    # rebuild with taper widths if needed — simpler: just end-cap free ends
    for p,q in zip(rows[:-1],rows[1:]):
        if p is None or q is None: continue
        for quad in ((p[0],q[0],q[1],p[1]),(p[2],q[2],q[0],p[0]),(p[1],q[1],q[3],p[3])):
            try: bm.faces.new(quad); nq+=1
            except ValueError: pass
    for end,fr in ((rows[0],freeA),(rows[-1],freeB)):
        if fr and end:
            try: bm.faces.new((end[0],end[1],end[3],end[2])); nq+=1
            except ValueError: pass
    info.append(dict(n=len(idx),a=[round(v,1) for v in S[idx[0]]],b=[round(v,1) for v in S[idx[-1]]],freeA=freeA,freeB=freeB))
json.dump({'runs':info,'nq':nq},open(D+'data/tr/walk_gap.json','w'))
if nq>0:
    bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.001)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(WALK_NAME); bm.to_mesh(me); bm.free()
    if not me.uv_layers: me.uv_layers.new(name='UVMap')
    for f in me.polygons:
        for li in f.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co; me.uv_layers.active.data[li].uv=(co.x/2.0,co.y/2.0+co.z/2.0)
    me.uv_layers.new(name='ortho')
    if matw: me.materials.append(matw)
    ow=bpy.data.objects.new(WALK_NAME,me); col.objects.link(ow); ow['tr_obj']=1
    ow['UNVERIFIED']='OSM 546643369 south gap west of Stone; 2.0 m width assumed; draped on LiDAR/3DEP'
    print('TR walk gap faces',nq,'runs',info)
else:
    bm.free(); print('TR walk gap EMPTY',info)

# cameras
def cam(name,loc,tgt,lens):
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=30000
    o=bpy.data.objects.new(name,cd); col.objects.link(o); o['tr_obj']=1
    o.location=Vector(loc); o.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); return o
# close-up on Stone sill + short plinth (west face)
gzc=gz(128.5,268.0) or 136.5
cam('TR_CAM_closeup_Stone_sill_plinth',(124.5,270.0,gzc+1.55),(132.0,268.0,gzc+2.2),35)
# eye-level Blanton south (infill between piers)
gzb=gz(148.0,420.0) or 137.0
cam('TR_CAM_eye_Blanton_infill_from_S',(150.0,418.0,gzb+1.65),(150.0,435.0,gzb+6.0),32)
print('TR applied; objects',len(bpy.data.objects))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
