"""ty review fix: E entrances 405/406/407 — rebuild steps using OSM node xy grade (OFF shift sampled a skirt hole → 1.55 m stairwell)."""
import bpy, bmesh, os, json, math
from mathutils import Vector
SAVE=os.environ.get('SAVE')=='1'
D='/workspace/nj-scenes/montclair-state/'
GR=140.06; RISER=0.152; TREAD=0.30
ENT=json.load(open(D+'data/tx/nursing_entr_nodes.json'))
FP=[tuple(p) for p in json.load(open(D+'data/tx/nursing_geom.json'))['footprint']]
nFP=len(FP)
A=sum(FP[i][0]*FP[(i+1)%nFP][1]-FP[(i+1)%nFP][0]*FP[i][1] for i in range(nFP))/2
ccw=A>0
OFF={3:(3,4,1.6),4:(3,4,-1.6),8:(8,8,0),12:(12,13,1.6),13:(13,13,0),14:(13,14,-1.6)}

def edge_info(i):
    p=Vector((*FP[i],0)); q=Vector((*FP[(i+1)%nFP],0)); e=q-p; u=e.normalized()
    nr=Vector((u.y,-u.x,0)) if ccw else Vector((-u.y,u.x,0))
    return p,q,u,nr

def entr_frame(en):
    i=en['i']; a,b,off=OFF[i]
    if a==b:
        p1,q1,u1,n1=edge_info(i); p0,q0,u0,n0=edge_info((i-1)%nFP)
        u,nr=(u1,n1) if (q1-p1).length>=(q0-p0).length else (u0,n0)
        c=Vector((*FP[i],0))
    else:
        p,q,u,nr=edge_info(a); c=Vector((*FP[i],0))+u*off
    return c,u,nr

dg=bpy.context.evaluated_depsgraph_get()
GN=[n for n in ('Terrain_LiDAR_DTM_1m','SA_ground_lower_patch_UNVERIFIED','RZ2_SC_LiDAR_ground_patch_UNVERIFIED','Context_skirt_3DEP_ortho_4km') if n in bpy.data.objects]
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN]
def gz(x,y):
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best

def box_mesh(bm,c,u,n,w,dep0,dep1,z0,z1,mi=0):
    u=Vector((u[0],u[1],0)).normalized(); n=Vector((n[0],n[1],0)).normalized(); c=Vector((c[0],c[1],0))
    vs=[]
    for z in (z0,z1):
        for a,b in ((-1,dep0),(1,dep0),(1,dep1),(-1,dep1)):
            p=c+u*(a*w/2)+n*b; vs.append(bm.verts.new((p.x,p.y,z)))
    for f in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)):
        try: bm.faces.new([vs[i] for i in f]).material_index=mi
        except ValueError: pass

# remove old landing mesh + E footways that were snapped to wrong bottoms; rebuild
old=bpy.data.objects.get('TY Partridge entrance steps+landings (UNVERIFIED)')
mats=list(old.data.materials) if old else []
col=bpy.data.collections.get('TY_Nursing_Partridge_approaches_UNVERIFIED')
if old:
    me=old.data; bpy.data.objects.remove(old,do_unlink=True)
    if me and me.users==0: bpy.data.meshes.remove(me)

# also remove E stub walks 405/406/407 to re-snap
for wid in ('313026405','313026406','313026407'):
    o=bpy.data.objects.get('TY_footway_%s_to_Partridge_UNVERIFIED'%wid)
    if o:
        me=o.data; bpy.data.objects.remove(o,do_unlink=True)
        if me and me.users==0: bpy.data.meshes.remove(me)

bm=bmesh.new(); meta=[]; SD=json.load(open(D+'data/scene_data.json')); F={str(f['id']):f for f in SD['features']}
for en in ENT:
    c,u,nr=entr_frame(en)
    # grade at OSM node xy (entr['xy']) and 1.5 m out — prefer node for E face
    nx,ny=en['xy']
    z_node=gz(nx,ny); z_out=gz(*(c+nr*1.5).to_2d())
    cands=[z for z in (z_node,z_out,gz(*(c+nr*0.4).to_2d())) if z is not None]
    # for east face (nr.x>0.5): use max of samples so skirt holes don't invent a stairwell
    if nr.x>0.5:
        z_grade=max(cands) if cands else GR-0.1
    else:
        z_grade=sorted(cands)[len(cands)//2] if cands else GR-0.1
    rise=max(0.0,GR-z_grade)
    if rise>1.55: z_grade=GR-1.55; rise=1.55
    n_risers=max(1,int(round(rise/RISER))) if rise>0.08 else 0
    rh=(rise/n_risers) if n_risers else 0.0
    Wdoor=2.8
    box_mesh(bm,c,u,nr,Wdoor+0.4,0.05,1.15,GR-0.12,GR+0.02,0)
    for k in range(n_risers):
        z1=GR-k*rh; z0=z1-rh
        d0=1.15+k*TREAD; d1=d0+TREAD
        box_mesh(bm,c,u,nr,Wdoor+0.2+0.05*k,d0,d1,z0-0.02,z1,1)
    d_end=1.15+n_risers*TREAD
    box_mesh(bm,c,u,nr,Wdoor+0.5,d_end,d_end+1.4,z_grade-0.05,z_grade+0.06,0)
    meta.append(dict(way=en['way'],xy=[round(c.x,2),round(c.y,2)],z_grade=round(z_grade,3),rise=round(rise,3),n_risers=n_risers,
        bottom_xy=[round((c+nr*(d_end+0.7)).x,2),round((c+nr*(d_end+0.7)).y,2)],
        sill_xy=[round((c+nr*0.6).x,2),round((c+nr*0.6).y,2)],outward=[round(nr.x,3),round(nr.y,3)]))

bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new('TY Partridge entrance steps+landings (UNVERIFIED)'); bm.to_mesh(me); bm.free()
for m in mats: me.materials.append(m)
for p in me.polygons: p.use_smooth=False
o=bpy.data.objects.new('TY Partridge entrance steps+landings (UNVERIFIED)',me); col.objects.link(o); o['ty_obj']=1
o['UNVERIFIED']='riser/tread guessed; E grades use OSM-node max to avoid skirt-hole stairwells (ty fix)'
print('TY fix landings',meta)

# re-drape short E walks
matw=bpy.data.materials.get('SC_walk_concrete_joints_UNVERIFIED')
def resample(pts,step=0.55):
    S=[]
    for (ax,ay),(bx,by) in zip(pts[:-1],pts[1:]):
        L=math.hypot(bx-ax,by-ay); n=max(1,int(L/step))
        for i in range(n):
            t=i/n; S.append((ax+(bx-ax)*t,ay+(by-ay)*t))
    S.append(tuple(pts[-1][:2])); return S

# refresh gnd including walks
for nm in list(bpy.data.objects.keys()):
    if nm.startswith('SB_') or nm.startswith('TY_footway_'):
        if bpy.data.objects[nm].type=='MESH' and nm not in GN:
            GN.append(nm)
gnd=[(bpy.data.objects[n].evaluated_get(bpy.context.evaluated_depsgraph_get()),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
def gz2(x,y):
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best

for wid in ('313026405','313026406','313026407'):
    feat=F.get(wid); m=next(x for x in meta if x['way']==wid)
    pts=[tuple(p[:2]) for p in feat['pts']]
    cx=sum(p[0] for p in FP)/len(FP); cy=sum(p[1] for p in FP)/len(FP)
    if math.hypot(pts[0][0]-cx,pts[0][1]-cy)<math.hypot(pts[-1][0]-cx,pts[-1][1]-cy):
        pts=list(reversed(pts))
    force=Vector((m['bottom_xy'][0],m['bottom_xy'][1],m['z_grade']))
    S=resample(pts,0.5); S[-1]=(force.x,force.y)
    bm=bmesh.new(); rows=[]; nq=0; w=2.2
    for i,(x,y) in enumerate(S):
        a=S[max(i-1,0)]; b=S[min(i+1,len(S)-1)]
        tx,ty=b[0]-a[0],b[1]-a[1]; L=math.hypot(tx,ty) or 1; nx,ny=-ty/L,tx/L
        Lp=(x+nx*w/2,y+ny*w/2); Rp=(x-nx*w/2,y-ny*w/2)
        zs=[z for z in (gz2(*Lp),gz2(x,y),gz2(*Rp)) if z is not None]
        if not zs: rows.append(None); continue
        z=max(zs)+0.05
        if math.hypot(x-force.x,y-force.y)<2.5: z=max(z,force.z+0.04)
        vL=bm.verts.new((Lp[0],Lp[1],z)); vR=bm.verts.new((Rp[0],Rp[1],z))
        vLb=bm.verts.new((Lp[0],Lp[1],z-0.28)); vRb=bm.verts.new((Rp[0],Rp[1],z-0.28))
        rows.append([vL,vR,vLb,vRb])
    for p,q in zip(rows[:-1],rows[1:]):
        if not p or not q: continue
        for quad in ((p[0],q[0],q[1],p[1]),(p[2],q[2],q[0],p[0]),(p[1],q[1],q[3],p[3])):
            try: bm.faces.new(quad); nq+=1
            except ValueError: pass
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new('TY_footway_%s_to_Partridge_UNVERIFIED'%wid); bm.to_mesh(me); bm.free()
    if matw: me.materials.append(matw)
    o=bpy.data.objects.new(me.name,me); col.objects.link(o); o['ty_obj']=1
    o['UNVERIFIED']='OSM centreline drape; width 2.2 m assumed'
    print('TY fix walk',wid,'faces',nq,'rise',m['rise'],'risers',m['n_risers'])

# update approaches.json
prev=json.load(open(D+'data/ty/approaches.json'))
prev['landings']=meta; prev['elandings_fix']='OSM-node max grade on E face'
json.dump(prev,open(D+'data/ty/approaches.json','w'),indent=2)
print('TY fix objs',len(bpy.data.objects),'ty',sum(1 for o in bpy.data.objects if o.get('ty_obj')))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
