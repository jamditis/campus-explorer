# ws156: UNIFY #60 Freeman N end unification.
# Evidence: 1965 slide186 + 1971 slide1114 = end walls one flat blank buff brick (no full-height fin);
# 1971 slide1096 = dark individual letters "GRACE M. / FREEMAN HALL" (2 lines) mounted straight on the same pale brick at
# about door-head height beside the entrance, under the canopy level; 2007 Commons + 2019 Montclarion = one brick tone
# on piers/ends. Name verified: Montclarion 1962-05-04 dedication ("Grace M. Freeman Hall"). Model had "GRACE H." on one line
# ~9 m up on a dark plate, and a full-height striated fin (VB cream_brick_strong: bright brick + 0.26 dark mortar).
# Design: (1) fin + entrance pilaster fills clamp to the entrance-block top (= WS154 skin bottom), so above it the N end is
# one flat skin; (2) all N-band cream brick -> the WS154 end-wall brick; (3) old dressing faces proud of the skin above the
# block deleted; (4) lettering fixed (text verified, height/side UNVERIFIED), dark plate removed.
import bpy, bmesh, os, resource
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'
exec(open(M+'scripts/ws152/facade152.py').read())
C=(W_N+W_S+E_N+E_S)/4; A=W_N; u=(E_N-W_N).normalized(); n=Vector((u.y,-u.x)); L=(E_N-W_N).length
if ((W_N+E_N)/2-C).dot(n)<0: n=-n
def sd(p): q=Vector((p.x,p.y)); return (q-A).dot(u),(q-A).dot(n)
cream=bpy.data.materials['WS154_Freeman_cream_brick_endwall_plane_UNVERIFIED']
skin=next(o for o in bpy.data.objects if o.name.startswith('WS154_Freeman_N_end_wall_blank'))
zc=min((skin.matrix_world@v.co).z for v in skin.data.vertices); print('FIX156 zc',round(zc,3))
OLD=('VB_Freeman_cream_brick_strong_UNVERIFIED','UV_Freeman_cream_brick_UNVERIFIED')
SKIP=('WS154','WS152','WS156','Freeman Hall walls','roof','Roof','parapet','RTU','CAM','_RETIRED')
band=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or 'Freeman' not in o.name or any(k in o.name for k in SKIP) or not o.data.vertices: continue
    P=[o.matrix_world@v.co for v in o.data.vertices]; S=[sd(p) for p in P]
    if max(s for s,_ in S)<-1 or min(s for s,_ in S)>L+1 or max(d for _,d in S)<-2.6 or min(d for _,d in S)>3.5: continue
    band.append(o)
print('FIX156 band objs',len(band))
fin=bpy.data.objects.get('UV_Freeman_N_lettering_brick_wing_UNVERIFIED')
# --- lettering target height: landing (rail post foot) + 2.4 m (slide1096: letters at ~door head), UNVERIFIED
lp=bpy.data.objects.get('VT_Freeman_N_rail_W_post0')
landing=min((lp.matrix_world@v.co).z for v in lp.data.vertices) if lp else 130.4
zl=min(landing+2.4, zc-0.6); print('FIX156 landing',round(landing,2),'letter z',round(zl,2))
nclamp=nhide=ndel=nremap=0
for o in band:
    me=o.data
    if me.users>1: o.data=me=me.copy()
    for i,m in enumerate(me.materials):
        if m and (m.name in OLD or ('Freeman_N_cream_punch' in m.name) or ('Freeman_N_cream_depth' in m.name)): me.materials[i]=cream; nremap+=1
    simple=len(me.polygons)<=12   # thin overlay boxes (fin, pier fills, quoin punches, belts): clamp to the block top
    bm=bmesh.new(); bm.from_mesh(me); mw=o.matrix_world; mi=mw.inverted()
    if simple:
        if o==fin:   # remove the dark lettering plate (letters sit straight on the brick in slide1096)
            pl=[f for f in bm.faces if f.material_index==1]; bmesh.ops.delete(bm,geom=pl,context='FACES')
            bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS'); print('FIX156 fin plate faces',len(pl))
        zs=[(mw@v.co).z for v in bm.verts]
        if min(zs)>=zc-0.01:
            bm.free(); o.hide_render=True; o.hide_viewport=True; o.name=o.name[:40]+'_RETIRED_ws156'; nhide+=1; continue
        for v in bm.verts:
            w=mw@v.co
            if w.z>zc: w.z=zc; v.co=mi@w; nclamp+=1
    else:
        dl=[]
        for f in bm.faces:
            c=mw@f.calc_center_median(); s,d=sd(c)
            if c.z>zc+0.02 and d>PIER_OUT+0.004 and -0.5<s<L+0.5: dl.append(f)
        if dl: bmesh.ops.delete(bm,geom=dl,context='FACES'); ndel+=len(dl); print('FIX156 del proud faces',o.name,len(dl))
    bm.to_mesh(me); bm.free(); me.update()
print('FIX156 remap slots',nremap,'clamped verts',nclamp,'retired',nhide,'deleted faces',ndel)
# --- lettering
for o in [o for o in bpy.data.objects if o.type=='FONT' and 'FREEMAN' in o.data.body.upper()]:
    cu=o.data; old=cu.body; cu.body='GRACE M.\nFREEMAN HALL'; cu.align_x='CENTER'; cu.align_y='CENTER'
    mwl=o.matrix_world.copy(); t=mwl.translation.copy(); nl=mwl.to_3x3()@Vector((0,0,1)); nl.z=0; nl.normalize()
    t.z=zl
    if fin:   # seat on the fin face: ray from 1 m out back along -normal
        fi=fin.matrix_world.inverted(); o0=t+nl*1.0
        ok,loc,nor,_=fin.ray_cast(fi@o0,(fi.to_3x3()@(-nl)).normalized())
        if ok: t=fin.matrix_world@loc+nl*(cu.extrude+0.006); print('FIX156 letter seated on fin')
    mwl.translation=t; o.matrix_world=mwl
    o.name='UV_Freeman_N_lettering_GRACE_M_FREEMAN_HALL_ws156_UNVERIFIED_height'
    bpy.context.view_layer.update(); print('FIX156 lettering',repr(old),'->',repr(cu.body),'at',tuple(round(x,2) for x in t),'dims',tuple(round(x,2) for x in o.dimensions))
# --- cameras
T=bpy.data.objects.get('Terrain_LiDAR_DTM_1m')
def gz(x,y,d):
    if not T: return d
    mi=T.matrix_world.inverted(); ok,loc,_,_=T.ray_cast(mi@Vector((x,y,300)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
    return (T.matrix_world@loc).z if ok else d
def cam(name,pos,tgt,lens):
    c=bpy.data.objects.get(name) or bpy.data.objects.new(name,bpy.data.cameras.new(name))
    c.data.lens=lens; c.location=pos; c.rotation_euler=(tgt-pos).to_track_quat('-Z','Y').to_euler()
    if c.name not in bpy.context.scene.collection.objects: bpy.context.scene.collection.objects.link(c)
    print('FIX156 cam',name,tuple(round(x,1) for x in pos))
mid=(W_N+E_N)/2
p=mid+n*42+u*14; cam('WS156_CAM_oblique_Freeman_N_end_from_NE',Vector((p.x,p.y,163.0)),Vector((mid.x,mid.y,138)),24)
p=mid+n*34-u*3; cam('WS156_CAM_eye_Freeman_N_end_from_N_lawn',Vector((p.x,p.y,gz(p.x,p.y,128.5)+1.6)),Vector((mid.x,mid.y,136.5)),28)
fc=W_N+u*(L-1.8)   # fin centre (E end)
p=fc+n*14+u*9; cam('WS156_CAM_eye_Freeman_N_entrance_from_NE',Vector((p.x,p.y,gz(p.x,p.y,129.0)+1.6)),Vector((fc.x-u.x*4,fc.y-u.y*4,132.5)),28)
p=fc+n*5.5+u*1.5; cam('WS156_CAM_closeup_Freeman_N_lettering',Vector((p.x,p.y,gz(p.x,p.y,129.5)+1.6)),Vector((fc.x,fc.y,zl-0.3)),35)
bpy.ops.wm.save_as_mainfile(filepath=os.environ.get('OUT156',M+'montclair_state_ws156a.blend'),copy=True)
print('SAVED_WS156A RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
