# tj (Nov 4 2026 ~7:30 PM ET, MAIN, day 8 Student Center east edge). ALL UNVERIFIED, reversible (REVERT=1).
# (1) Webster Hall site stays lawn (Joe, Nov 4): grass clumps on the lawn north of Quad Road x 60..205, y 338..416 (only where the top hit is ground).
# (2) Stone/Blanton wall material copy: warmer/darker stucco + 0.95 m concrete base band. (3) Blanton entrances at the 3 OSM footway ends that meet the wall:
#     recessed dark-glass door bays with aluminium frames + thin canopies (design typical, NO refs). Cameras TJ_*.
import bpy, bmesh, os, math, random
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
def revert():
    for o in [o for o in bpy.data.objects if 'tj_obj' in o]:
        me=o.data; bpy.data.objects.remove(o)
        if me and me.users==0:
            (bpy.data.meshes if hasattr(me,'vertices') else bpy.data.cameras).remove(me)
    for o in bpy.data.objects:
        if 'tj_orig_mat' in o:
            o.data.materials[0]=bpy.data.materials[o['tj_orig_mat']]; del o['tj_orig_mat']
    m=bpy.data.materials.get('TI_dorm_wall_windows_UNVERIFIED')
    if m and 'tj_fake' in m: m.use_fake_user=False; del m['tj_fake']
    for n in ('TJ_dorm_wall_base_UNVERIFIED','TJ_door_glass_UNVERIFIED','TJ_door_frame_UNVERIFIED'):
        m=bpy.data.materials.get(n)
        if m: bpy.data.materials.remove(m)
    c=bpy.data.collections.get('TJ_east_edge_UNVERIFIED')
    if c: bpy.data.collections.remove(c)
    print('TJ reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
col=bpy.data.collections.new('TJ_east_edge_UNVERIFIED'); sc.collection.children.link(col)
GN=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','RZ2_SC_LiDAR_ground_patch','QW_DTM_north_edge_ramp_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED']
X0,X1,Y0,Y1=60,215,338,500
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
# blockers: visible meshes overlapping the box (no grass/terrain/trees/huge)
blk=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name in GN or not o.visible_get(): continue
    n=o.name.lower()
    if 'grass' in n or 'tree' in n or 'skirt' in n or 'context' in n or 'terrain' in n: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; bx=[v.x for v in bb]; by=[v.y for v in bb]
    if max(bx)-min(bx)>600 or max(by)-min(by)>600: continue
    if min(bx)<X1 and max(bx)>X0 and min(by)<Y1 and max(by)>Y0:
        blk.append((o.evaluated_get(dg),o.matrix_world,(min(bx)-.3,max(bx)+.3,min(by)-.3,max(by)+.3),o.name))
print('TJ blockers',len(blk),[b[3] for b in blk][:40])
def hit(lst,x,y):
    best=None
    for e,mw,*_ in lst:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
import json as _j
_W=_j.load(open('data/td/east_osm.json'))['ways']
LOT=_W['313029107']['pts']
LINES=[(_W[k]['pts'],{'546643370':4.2,'313029103':3.8,'313029923':3.8}.get(k,1.3)) for k,v in _W.items() if v['tags'].get('highway') in ('service',) and k not in ('313028549',)]
def _pip(x,y,P):
    ins=False
    for i in range(len(P)):
        x1,y1=P[i]; x2,y2=P[(i+1)%len(P)]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
def _near(x,y):
    for P,w in LINES:
        for i in range(len(P)-1):
            ax,ay=P[i]; bx,by=P[i+1]; dx,dy=bx-ax,by-ay; t=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy+1e-9)))
            if math.hypot(ax+t*dx-x,ay+t*dy-y)<w: return True
    return False
WALKS=['313029110','313029908','313029909','313029910']
LINES+= [(_W[k]['pts'],1.25) for k in WALKS]
LINES=[(P,w) for P,w in LINES if max(p[0] for p in P)>X0-5 and min(p[0] for p in P)<X1+5 and max(p[1] for p in P)>Y0-5 and min(p[1] for p in P)<Y1+5]
print('TJ exclusion lines',len(LINES))
nex=0
random.seed(20261104)
pts=[]; rej=0; step=0.37
y=Y0
while y<Y1:
    x=X0
    while x<X1:
        px=x+random.uniform(-.17,.17); py=y+random.uniform(-.17,.17)
        if _pip(px,py,LOT) or _near(px,py): nex+=1; x+=step; continue
        g=hit(gnd,px,py)
        if g is not None:
            bl=[b for b in blk if b[2][0]<px<b[2][1] and b[2][2]<py<b[2][3]]
            hb=hit(bl,px,py) if bl else None
            if hb is None or hb<g+0.02: pts.append((px,py,g))
            else: rej+=1
        x+=step
    y+=step
print('TJ grass pts',len(pts),'excluded lot/paths',nex,'rejected under objects',rej)
src=bpy.data.objects['QV_Richardson_NW_lawn_grass_points_UNVERIFIED']
me=bpy.data.meshes.new('TJ_Webster_lawn_grass_points_UNVERIFIED'); me.from_pydata(pts,[],[])
o=src.copy(); o.data=me; o.name='TJ_Webster_lawn_grass_points_UNVERIFIED'; o.matrix_world=__import__('mathutils').Matrix.Identity(4)
for c in list(o.users_collection): c.objects.unlink(o)
col.objects.link(o); o['tj_obj']=1; o['UNVERIFIED']='Webster Hall site kept as lawn per Joe Nov 4 2026; clump density copied from QV'
for k in [k for k in o.keys() if k.startswith(('qv','qx','ti'))]: del o[k]
# (2) wall material copy
WM=bpy.data.materials['TI_dorm_wall_windows_UNVERIFIED']; WM.use_fake_user=True; WM['tj_fake']=1; NM=WM.copy(); del NM['tj_fake']; NM.name='TJ_dorm_wall_base_UNVERIFIED'
N=NM.node_tree.nodes; L=NM.node_tree.links
for n in N:
    if n.type=='VALTORGB':
        n.color_ramp.elements[0].color=(0.33,0.31,0.28,1); n.color_ramp.elements[1].color=(0.43,0.41,0.37,1); break
b=N['Principled BSDF']; lk=b.inputs['Base Color'].links[0]; srcsock=lk.from_socket
tc=[n for n in N if n.type=='TEX_COORD'][0]; a0=[n for n in N if n.type=='ATTRIBUTE' and n.attribute_name=='ti_z0'][0]
sep=N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'],sep.inputs[0])
sub=N.new('ShaderNodeMath'); sub.operation='SUBTRACT'; L.new(sep.outputs['Z'],sub.inputs[0]); L.new(a0.outputs['Fac'],sub.inputs[1])
lt=N.new('ShaderNodeMath'); lt.operation='LESS_THAN'; L.new(sub.outputs[0],lt.inputs[0]); lt.inputs[1].default_value=0.95
ge=N.new('ShaderNodeNewGeometry'); sn=N.new('ShaderNodeSeparateXYZ'); L.new(ge.outputs['True Normal'],sn.inputs[0])
ab=N.new('ShaderNodeMath'); ab.operation='ABSOLUTE'; L.new(sn.outputs['Z'],ab.inputs[0])
wl=N.new('ShaderNodeMath'); wl.operation='LESS_THAN'; L.new(ab.outputs[0],wl.inputs[0]); wl.inputs[1].default_value=0.5
mu=N.new('ShaderNodeMath'); mu.operation='MULTIPLY'; L.new(lt.outputs[0],mu.inputs[0]); L.new(wl.outputs[0],mu.inputs[1])
nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=3.0; L.new(tc.outputs['Object'],nz.inputs['Vector'])
cr=N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.30,0.29,0.27,1); cr.color_ramp.elements[1].color=(0.40,0.39,0.36,1); L.new(nz.outputs['Fac'],cr.inputs[0])
mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; L.new(mu.outputs[0],mx.inputs['Factor']); L.new(srcsock,mx.inputs['A']); L.new(cr.outputs['Color'],mx.inputs['B'])
L.new(mx.outputs['Result'],b.inputs['Base Color'])
for o in bpy.data.objects:
    if o.name.startswith(('TI_Stone_Hall','TI_Blanton_Hall')) and o.type=='MESH':
        o['tj_orig_mat']=o.data.materials[0].name; o.data.materials[0]=NM
# (3) Blanton entrances (OSM footway ends on the wall)
def mat(name,col_,rough,metal=0.0,trans=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; bb=m.node_tree.nodes['Principled BSDF']
    bb.inputs['Base Color'].default_value=col_; bb.inputs['Roughness'].default_value=rough; bb.inputs['Metallic'].default_value=metal
    return m
GL=mat('TJ_door_glass_UNVERIFIED',(0.03,0.04,0.05,1),0.05); FR=mat('TJ_door_frame_UNVERIFIED',(0.55,0.56,0.57,1),0.35,0.9)
import json
E=json.load(open('data/ti/east_levels.json'))['313029108']['outer']
def seg(p):
    best=None
    for i in range(len(E)):
        a=Vector((*E[i],0)); c=Vector((*E[(i+1)%len(E)],0)); q=Vector((*p,0)); d=c-a; t=max(0,min(1,(q-a).dot(d)/d.length_squared))
        r=((a+d*t-q).length,a+d*t,d.normalized())
        if best is None or r[0]<best[0]: best=r
    return best
def box(bm,cx,u,n,w,dpt,z0,z1,off):
    vs=[]
    for su in (-w/2,w/2):
        for sn_ in (off,off+dpt):
            for z in (z0,z1):
                p=cx+u*su+n*sn_; vs.append(bm.verts.new((p.x,p.y,z)))
    bmesh.ops.convex_hull(bm,input=vs)
DOORS=[(149.9,431.8),(92.4,419.1),(97.1,439.6)]
cen=Vector((sum(p[0] for p in E)/len(E),sum(p[1] for p in E)/len(E),0))
made=0
for p in DOORS:
    d,c,u=seg(p)
    if d>0.5: continue
    # shift door centre 1.6 m inside the segment ends (corner door at 92.4,419.1)
    a=None
    n=Vector((-u.y,u.x,0))
    if n.dot(c-cen)<0: n=-n
    g=hit(gnd,c.x+n.x*2,c.y+n.y*2) or 137.0
    bmF=bmesh.new(); bmG=bmesh.new()
    W=2.6; H=2.75
    # frame surround (proud 6 cm), glass recessed (2 cm proud of wall, i.e. inside frame), canopy
    box(bmF,c,u,n,W+0.24,0.06,g,g+H+0.12,0.0)
    box(bmG,c,u,n,W,0.02,g+0.02,g+H,0.06)
    box(bmF,c,u,n,0.06,0.03,g+0.02,g+H,0.08)        # centre stile
    box(bmF,c,u,n,W,0.03,g+2.15,g+2.21,0.08)        # transom
    box(bmF,c,u,n,W+1.0,1.6,g+H+0.35,g+H+0.55,0.0)  # canopy
    for bm_,m_,nm in ((bmF,FR,'frame'),(bmG,GL,'glass')):
        me=bpy.data.meshes.new('TJ_Blanton_entrance_%d_%s_UNVERIFIED'%(made,nm)); bm_.to_mesh(me); bm_.free(); me.materials.append(m_)
        ob=bpy.data.objects.new(me.name,me); col.objects.link(ob); ob['tj_obj']=1; ob['UNVERIFIED']='door at OSM footway end on the Blanton wall; design/size typical, no refs'
    made+=1; print('TJ door',made,[round(v,1) for v in c],'ground',round(g,2))
# (4) walks at the Blanton doors (OSM footways ending on the wall), 2.0 m draped concrete ribbons
wm=None
for n in ('QW_footway_546643369_ext_UNVERIFIED',):
    if n in bpy.data.objects: wm=bpy.data.objects[n].data.materials[0] if bpy.data.objects[n].data.materials else None
for k in WALKS:
    P=[Vector((*p,0)) for p in _W[k]['pts']]; S=[]
    for i in range(len(P)-1):
        a,b=P[i],P[i+1]; L_=(b-a).length; n=max(1,int(L_/0.8))
        for j in range(n): S.append(a+(b-a)*(j/n))
    S.append(P[-1])
    bm=bmesh.new(); prev=None
    for i,p in enumerate(S):
        d=(S[min(i+1,len(S)-1)]-S[max(i-1,0)]).normalized(); nn=Vector((-d.y,d.x,0))
        row=[]
        for sd in (-1.0,1.0):
            q=p+nn*sd; g=hit(gnd,q.x,q.y) or 136.5
            row.append(bm.verts.new((q.x,q.y,g+0.06)))
        row=[bm.verts.new((row[0].co.x,row[0].co.y,row[0].co.z-0.2))]+row+[bm.verts.new((row[1].co.x,row[1].co.y,row[1].co.z-0.2))]
        if prev:
            for a_ in range(3): bm.faces.new((prev[a_],prev[a_+1],row[a_+1],row[a_]))
        prev=row
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new('TJ_walk_%s_UNVERIFIED'%k); bm.to_mesh(me); bm.free()
    if wm: me.materials.append(wm)
    ob=bpy.data.objects.new(me.name,me); col.objects.link(ob); ob['tj_obj']=1; ob['UNVERIFIED']='OSM footway %s centreline, 2.0 m width typical'%k
    print('TJ walk',k,len(S))
def cam(name,loc,tgt,lens):
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=30000; o=bpy.data.objects.new(name,cd); col.objects.link(o); o['tj_obj']=1
    o.location=loc; d=Vector(tgt)-Vector(loc); o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2); return o
g=hit(gnd,150,412) or 137
cam('TJ_CAM_closeup_Blanton_S_entrance',(152,412,g+1.7),(149.9,431.8,g+2.0),30)
g=hit(gnd,100,330) or 137
cam('TJ_CAM_eye_Webster_lawn_Blanton_from_S',(100,330,g+1.7),(125,430,g+6),26)
print('TJ applied; objects',len(bpy.data.objects))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
