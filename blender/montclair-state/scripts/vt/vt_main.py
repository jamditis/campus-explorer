"""vt: Freeman N entrance -> real recessed double-height glazed entry (slide 1096). UNVERIFIED sizes."""
import bpy, bmesh, mathutils, json
from mathutils import Vector
V=Vector
ZT=135.95; ZB=129.10; DEPTH=0.74
d=V((-0.974,0.228,0)).normalized(); out=V((d.y*-1,d.x*-1,0))  # placeholder
out=V((0.228,0.974,0)).normalized(); inn=-out
A=V((-84.96,-170.83,0)); B=V((-90.30,-169.58,0))
def onwall(x):
    t=(x-A.x)/(B.x-A.x); return A+(B-A)*t
PW=onwall(-85.03); PE=onwall(-89.65)
log={'hidden':[],'trimmed':[],'new':[]}
# --- A cut wall opening
w=bpy.data.objects['Freeman Hall walls']; mw=w.matrix_world; mi=mw.inverted()
bm=bmesh.new(); bm.from_mesh(w.data)
def bis(co,no):
    geom=bm.verts[:]+bm.edges[:]+bm.faces[:]
    bmesh.ops.bisect_plane(bm,geom=geom,plane_co=mi@co,plane_no=(mi.to_3x3()@no).normalized(),dist=1e-4)
bis(V((0,0,ZT)),V((0,0,1)))
bis(PW,d); bis(PE,d)
kill=[]
for f in bm.faces:
    c=mw@f.calc_center_median()
    s=(c-PW).dot(d); off=(c-PW).dot(out)
    if 0.002<s<(PE-PW).length-0.002 and abs(off)<0.08 and c.z<ZT-0.002 and abs((mw.to_3x3()@f.normal).z)<0.3:
        kill.append(f)
log['wall_faces_removed']=len(kill)
bmesh.ops.delete(bm,geom=kill,context='FACES')
bm.to_mesh(w.data); bm.free(); w.data.update()
# --- B canopy faces off the curtain object
c=bpy.data.objects['UV_Freeman_N_entrance_curtain_doors_canopy_UNVERIFIED']; cm=c.matrix_world
bm=bmesh.new(); bm.from_mesh(c.data)
kill=[f for f in bm.faces if f.material_index==2 and 132.0<(cm@f.calc_center_median()).z<133.3]
# also verts of canopy box incl side faces: collect connected
vs=set(v for f in kill for v in f.verts)
kill2=set(kill)
for f in bm.faces:
    if f.material_index==2 and all(v in vs for v in f.verts): kill2.add(f)
log['canopy_faces_removed']=len(kill2)
bmesh.ops.delete(bm,geom=list(kill2),context='FACES')
bm.to_mesh(c.data); bm.free()
# --- C overlays that hang across the opening
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or 'Freeman' not in o.name: continue
    if o.name.startswith(('UV_Freeman_N_entrance','VC_Freeman_N_entrance_glass','UV_Freeman_N_globe','Freeman Hall walls')): continue
    bb=[o.matrix_world@V(x) for x in o.bound_box]
    cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8; zmin=min(v.z for v in bb); zmax=max(v.z for v in bb)
    cc=V((cx,cy,0)); s=(cc-PW).dot(d); off=(cc-PW).dot(out)
    if not (0.03<s<(PE-PW).length-0.03 and -0.3<off<0.6): continue
    if zmin>=ZT-0.01: continue
    if zmax<=ZT+0.02:
        o.hide_render=True; o.hide_viewport=True; o['vt_hidden']=1; log['hidden'].append(o.name)
    else:
        o['vt_trim_from']=zmin
        mwi=o.matrix_world.inverted()
        for v in o.data.vertices:
            wv=o.matrix_world@v.co
            if wv.z<ZT: wv.z=ZT+0.005; v.co=mwi@wv
        o.data.update(); log['trimmed'].append(o.name)
# --- D new recess liner: soffit, jambs, floor
col=bpy.data.collections.get('VT_Freeman_N_entrance_recess_UNVERIFIED') or bpy.data.collections.new('VT_Freeman_N_entrance_recess_UNVERIFIED')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
cream=bpy.data.materials['VB_Freeman_cream_brick_strong_UNVERIFIED']
conc=bpy.data.materials['UV_Freeman_step_concrete_UNVERIFIED']
soff=bpy.data.materials.get('VT_Freeman_soffit_plaster_UNVERIFIED')
if not soff:
    soff=bpy.data.materials.new('VT_Freeman_soffit_plaster_UNVERIFIED'); soff.use_nodes=True
    b=soff.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.62,0.6,0.56,1); b.inputs['Roughness'].default_value=0.85
    soff['vt_mat']=1
def box(name,pts,mat):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    vv=[bm.verts.new(p) for p in pts]
    for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
        bm.faces.new([vv[i] for i in f])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    me.materials.append(mat); o=bpy.data.objects.new(name,me); col.objects.link(o); o['vt_obj']=1; log['new'].append(name); return o
def slab(p0,p1,z0,z1,dep0,dep1,mat,name):
    # quad prism between wall pts p0..p1, depth dep0..dep1 along inn, z0..z1
    a=p0+inn*dep0; b=p1+inn*dep0; c2=p1+inn*dep1; dd=p0+inn*dep1
    pts=[V((q.x,q.y,z0)) for q in (a,b,c2,dd)]+[V((q.x,q.y,z1)) for q in (a,b,c2,dd)]
    return box(name,pts,mat)
slab(PW-d*0.0,PE,ZT,ZT+0.12,-0.02,DEPTH,soff,'VT_Freeman_N_entrance_soffit_UNVERIFIED')
slab(PW-d*0.12,PW,ZB,ZT+0.06,-0.02,DEPTH,cream,'VT_Freeman_N_entrance_jamb_W_UNVERIFIED')
slab(PE,PE+d*0.12,ZB,ZT+0.06,-0.02,DEPTH,cream,'VT_Freeman_N_entrance_jamb_E_UNVERIFIED')
slab(PW,PE,ZB-0.15,ZB+0.005,-0.02,DEPTH,conc,'VT_Freeman_N_entrance_floor_UNVERIFIED')
# --- E globes: hang in the recess under the soffit with stems
gm=[]
L=(PE-PW).length
for n,s in [('UV_Freeman_N_globe_pendant_UNVERIFIED',L*0.22),('UV_Freeman_N_globe_pendant_UNVERIFIED.001',L*0.78)]:
    g=bpy.data.objects[n]; g['vt_old_loc']=list(g.location)
    p=PW+d*s+inn*0.30; g.location=V((p.x,p.y,ZT-0.75))
    stem=slab(PW+d*(s-0.01),PW+d*(s+0.01),ZT-0.6,ZT,0.29,0.31,bpy.data.materials['UV_Freeman_white_frame_UNVERIFIED'],'VT_Freeman_N_globe_stem_%d'%int(s*10))
log['PW']=list(PW); log['PE']=list(PE)
json.dump(log,open('/workspace/nj-scenes/montclair-state/data/vt/vt_main.json','w'),indent=1,default=str)
print('VTLOG',json.dumps({k:(len(v) if isinstance(v,list) else v) for k,v in log.items()}))
print('HID',log['hidden']); print('TRIM',log['trimmed'])
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
