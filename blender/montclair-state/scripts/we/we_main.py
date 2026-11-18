# we: (1) reseat floating TL dorm trees onto the rendered ground (Context_skirt) at the
# same -0.25 m sink the seated ones use; (2) move TL_tree_095/099 trunks clear of the wd
# N stair walls/rails; (3) W walk 1132693523 end onto the Bohn W door centre;
# (4) new N stair cams chosen with a tree BVH (no camera inside a crown).
import bpy, json, math, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE')=='1'
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
def ske(): return sk.evaluated_get(bpy.context.evaluated_depsgraph_get())
SKE=ske()
def gz(x,y):
    r=SKE.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return r[1].z if r[0] else None
rep={'reseat':[], 'moved':[], 'walk':{}, 'cams':{}}
def tb(o):
    mw=o.matrix_world; p0=mw.translation
    P=[(mw@v.co).z for v in o.data.vertices if ((mw@v.co).xy-p0.xy).length<0.3]
    return min(P) if P else p0.z
# --- (2) move trees off the stair
foot=[n for n in bpy.data.objects.keys() if n.startswith(('WD_Bohn_N','WD_walk_','TK_Bohn_landing'))]
def bvh_obj(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); vs=[o.matrix_world@v.co for v in m.vertices]; fs=[list(p.vertices) for p in m.polygons]; e.to_mesh_clear()
    return BVHTree.FromPolygons(vs,fs)
FB=[bvh_obj(bpy.data.objects[n]) for n in foot if bpy.data.objects[n].type=='MESH' and 'cutter' not in n]
def clear(xy):
    d=1e9
    for t in FB:
        for z in (131.0,132.5,134.0,135.5):
            r=t.find_nearest(Vector((xy.x,xy.y,z)))
            if r[0] is not None: d=min(d,(Vector((r[0].x,r[0].y))-xy).length)
    return d
for n in ['TL_tree_095_UNVERIFIED','TL_tree_099_UNVERIFIED']:
    o=bpy.data.objects[n]; p=o.matrix_world.translation.copy(); best=None
    for rad in [0.5*i for i in range(1,8)]:
        for a in range(0,360,15):
            q=Vector((p.x+rad*math.cos(math.radians(a)),p.y+rad*math.sin(math.radians(a))))
            if clear(q)>=2.0: best=q; break
        if best: break
    if best:
        o.location.x=best.x; o.location.y=best.y
        rep['moved'].append([n,[round(p.x,2),round(p.y,2)],[round(best.x,2),round(best.y,2)],round((best-p.xy).length,2),round(clear(best),2)])
bpy.context.view_layer.update()
# --- (1) reseat
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree') or o.type!='MESH': continue
    p=o.matrix_world.translation; g=gz(p.x,p.y)
    if g is None: continue
    b=tb(o); d=(g-0.25)-b
    if abs(d)>0.10:
        o.location.z+=d; o['we_dz']=round(d,3); rep['reseat'].append([o.name,round(d,2)])
bpy.context.view_layer.update()
# --- (3) W walk end shift onto door centre
G=bpy.data.objects['TK_Bohn_door_glass_W_walk_UNVERIFIED']
gv=[G.matrix_world@v.co for v in G.data.vertices]; yc=(min(p.y for p in gv)+max(p.y for p in gv))/2
w=bpy.data.objects['WD_walk_1132693523_UNVERIFIED']; mw=w.matrix_world; inv=mw.inverted()
V=[mw@v.co for v in w.data.vertices]
xmax=max(p.x for p in V); xmin=min(p.x for p in V)
end=[p for p in V if p.x>xmax-0.6]; ye=(min(p.y for p in end)+max(p.y for p in end))/2
dy=yc-ye; rep['walk']=dict(door_yc=round(yc,3),walk_end_yc=round(ye,3),dy=round(dy,3))
for v in w.data.vertices:
    p=mw@v.co; t=max(0,min(1,(p.x-(xmax-5.0))/5.0)); t=t*t*(3-2*t)
    if t<=0: continue
    q=Vector((p.x,p.y+dy*t,p.z)); g0=gz(p.x,p.y); g1=gz(q.x,q.y)
    if g0 is not None and g1 is not None: q.z+=g1-g0
    v.co=inv@q
w.data.update(); w['we_dy']=round(dy,3)
# --- (4) cams
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); SKE=ske()
C=Vector((224.7,414.2,133.3))
TV=[];TF=[];off=0
for o in bpy.data.objects:
    if o.name.startswith('TL_tree') and (o.matrix_world.translation.xy-C.xy).length<35:
        for v in o.data.vertices: TV.append(o.matrix_world@v.co)
        for f in o.data.polygons: TF.append([i+off for i in f.vertices])
        off=len(TV)
TB=BVHTree.FromPolygons(TV,TF)
st=bpy.data.objects['WD_Bohn_N_steps_313029912_UNVERIFIED']; SV=[st.matrix_world@v.co for v in st.data.vertices]
tg=[SV[i] for i in range(0,len(SV),max(1,len(SV)//14))]+[Vector((228.8,412.7,132.6)),Vector((222.8,413.8,134.7))]
cands=[]
for rad in (5,6.5,8,10,12,14):
    for a in range(20,170,10):
        x=C.x+rad*math.cos(math.radians(a)); y=C.y+rad*math.sin(math.radians(a))
        if 221.7<x<231.9 and 410.5<y<416.5: continue
        g=gz(x,y)
        if g is None or g<128: continue
        for h in (1.65,3.2):
            c=Vector((x,y,g+h))
            # inside crown? short rays in many directions
            near=0
            for dx in (-1,0,1):
                for dyy in (-1,0,1):
                    for dz in (-0.3,0,0.6):
                        dvec=Vector((dx,dyy,dz))
                        if dvec.length==0: continue
                        r=TB.ray_cast(c,dvec.normalized(),2.5)
                        if r[0] is not None: near+=1
            vis=0
            for t in tg:
                d=t-c; r=TB.ray_cast(c,d.normalized(),d.length-0.1)
                if r[0] is None: vis+=1
            cands.append((vis-near*0.5,vis,near,rad,a,h,[round(c.x,2),round(c.y,2),round(c.z,2)]))
cands.sort(key=lambda k:-k[0])
# verify top candidates with full scene ray to targets (building occlusion)
def scene_ok(c):
    ok=0
    for t in tg:
        d=t-c; r=sc.ray_cast(dg,c,d.normalized(),distance=d.length+0.2)
        if r[0] and (r[4].name.startswith(('WD_','TK_Bohn_landing'))): ok+=1
    return ok
chosen={}
for k in cands[:60]:
    c=Vector(k[6]); key='eye' if k[5]<2 else 'high'
    if key in chosen: continue
    s=-1
    if k[2]==0: chosen[key]=(c,s,k)
    if len(chosen)==2: break
rep['cands_top']=[list(k) for k in cands[:10]]
col=bpy.data.collections['WD_Bohn_approach_walks_steps_UNVERIFIED']
def cam(name,loc,tgt,lens):
    o=bpy.data.objects.get(name)
    if o: bpy.data.objects.remove(o)
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=30000; cd.clip_start=0.1
    o=bpy.data.objects.new(name,cd); col.objects.link(o); o['we_obj']=1
    o.location=loc; o.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); return o
tgt=Vector((225.2,414.0,133.4))
for key,(c,s,k) in chosen.items():
    nm='WE_CAM_eye_Bohn_N_stair_clear' if key=='eye' else 'WE_CAM_closeup_Bohn_N_stair_clear'
    cam(nm,c,tgt,24 if key=='eye' else 30); rep['cams'][nm]=dict(loc=[round(x,2) for x in c],scene_vis=s,of=len(tg),k=list(k))
json.dump(rep,open('data/we/apply.json','w'),indent=1)
print('MOVED',rep['moved']); print('RESEAT',len(rep['reseat'])); print('WALK',rep['walk']); print('CAMS',rep['cams']); print('TOP',rep['cands_top'][:5])
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
