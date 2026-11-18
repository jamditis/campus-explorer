"""wq2 2026-11-09 ~9:50 AM ET: SW canopy carpet extension (fixes straight tree-line edge in Cole oblique). Rerunnable. --save"""
import bpy,json,math,random,sys,re
from mathutils import Vector
SAVE='--save' in sys.argv
R='/workspace/nj-scenes/montclair-state'
P=json.load(open(R+'/data/ccom_mid_distance/wq2/canopy_points_sw_wq2.json'))['points']
rng=random.Random(20261109)
col=bpy.data.collections['MID_canopy_carpet_20261015ai']
for n in ['MID_canopy_carpet_SW_near_crowns_wq2','MID_canopy_carpet_SW_near_trunks_wq2','MID_canopy_carpet_SW_far_crowns_wq2']:
    o=bpy.data.objects.get(n)
    if o: m=o.data; bpy.data.objects.remove(o,do_unlink=True); bpy.data.meshes.remove(m)
def bbox(m):
    xs=[v.co for v in m.vertices]; return Vector((min(v.x for v in xs),min(v.y for v in xs),min(v.z for v in xs))),Vector((max(v.x for v in xs),max(v.y for v in xs),max(v.z for v in xs)))
cmin,cmax=bbox(bpy.data.objects['MID_canopy_carpet_proto_crown_ai'].data); tmin,tmax=bbox(bpy.data.objects['MID_canopy_carpet_proto_trunk_ai'].data)
c_hr=max(cmax.x-cmin.x,cmax.y-cmin.y)/2; c_vr=(cmax.z-cmin.z)/2; t_r=max(tmax.x-tmin.x,tmax.y-tmin.y)/2; t_h=tmax.z-tmin.z
G=[bpy.data.objects[n] for n in ("Context_skirt_3DEP_ortho_4km","BD_farfield_3DEP_ortho","Context_ground_beyond_data") if n in bpy.data.objects]
inv=[(o,o.matrix_world.inverted()) for o in G]
def gz(x,y):
    best=None
    for o,mi in inv:
        ok,loc,nor,idx=o.ray_cast(mi@Vector((x,y,3000.0)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
        if ok:
            z=(o.matrix_world@loc).z; best=z if best is None else max(best,z)
    return best
EX=[]
for o in bpy.data.objects:
    if o.type not in('MESH','CURVE') or o.hide_render: continue
    if re.search(r'(?i)canopy|carpet|ground|terrain|skirt|farfield|DTM|ortho|backdrop|sky|water|proto|grass|lawn',o.name): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)-min(xs)>400 or max(ys)-min(ys)>400: continue
    cx,cy=(min(xs)+max(xs))/2,(min(ys)+max(ys))/2
    if math.hypot(cx-26.975,cy+13.051)<450: continue
    EX.append((min(xs)-8,max(xs)+8,min(ys)-8,max(ys)+8))
print('exclusion boxes',len(EX))
def excl(x,y): return any(a<=x<=b and c<=y<=d for a,b,c,d in EX)
nc=[];nt=[];fc=[];miss=0;nex=0
for p in P:
    if excl(p['x'],p['y']): nex+=1; continue
    z=gz(p['x'],p['y'])
    if z is None: miss+=1; continue
    hr=p['rad']*(1.30 if p['near'] else 1.25)*rng.choice((0.8,0.9,1.0,1.0,1.1,1.25,1.45)); rz=rng.uniform(0,6.283)
    ax,ay=rng.uniform(0.85,1.15),rng.uniform(0.85,1.15); tilt=(rng.uniform(-.05,.05),rng.uniform(-.05,.05),rz)
    if p['near']:
        vr=hr*rng.uniform(0.62,0.9); base=rng.uniform(2.4,4.4)
        nc.append(((p['x'],p['y'],z+base+vr),(ax*hr/c_hr,ay*hr/c_hr,vr/c_vr),tilt))
        th=base+vr*0.6; trr=min(0.38,0.12+hr*0.035)
        nt.append(((p['x'],p['y'],z-0.3),(trr/t_r,trr/t_r,(th+0.3)/t_h),(0,0,rz)))
    else:
        vr=hr*rng.uniform(0.45,0.62)
        fc.append(((p['x'],p['y'],z+rng.uniform(3.5,5.5)+vr),(ax*hr/c_hr,ay*hr/c_hr,vr/c_vr),tilt))
print('near',len(nc),'far',len(fc),'miss',miss,'excluded',nex)
def make(src,name,data):
    s=bpy.data.objects[src]; me=bpy.data.meshes.new(name+'_mesh')
    me.vertices.add(len(data)); me.vertices.foreach_set('co',[c for d in data for c in d[0]])
    for an,k in (('sc',1),('rot',2)):
        a=me.attributes.new(an,'FLOAT_VECTOR','POINT'); a.data.foreach_set('vector',[c for d in data for c in d[k]])
    o=bpy.data.objects.new(name,me); col.objects.link(o)
    for md in s.modifiers:
        nm=o.modifiers.new(md.name,md.type); nm.node_group=md.node_group
    o.hide_render=s.hide_render; o.hide_viewport=s.hide_viewport
    for m in s.data.materials: me.materials.append(m)
    print('made',name,len(data))
make('MID_canopy_carpet_near_crowns_ai','MID_canopy_carpet_SW_near_crowns_wq2',nc)
make('MID_canopy_carpet_near_trunks_ai','MID_canopy_carpet_SW_near_trunks_wq2',nt)
make('MID_canopy_carpet_far_crowns_ai','MID_canopy_carpet_SW_far_crowns_wq2',fc)
# close-up cam of the new SW tree line from the Cole oblique position
c=bpy.data.objects.get('WQ2_CAM_treeline_SW_from_Cole')
if not c:
    cd=bpy.data.cameras.new('WQ2_CAM_treeline_SW_from_Cole'); c=bpy.data.objects.new('WQ2_CAM_treeline_SW_from_Cole',cd); bpy.context.scene.collection.objects.link(c)
c.location=(-160,10,185); c.rotation_euler=(math.radians(83),0,math.radians(175)); c.data.lens=45; c.data.clip_end=30000
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED',bpy.data.filepath)
