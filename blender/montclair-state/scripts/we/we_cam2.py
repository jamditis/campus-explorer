import bpy, json, math, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE')=='1'
dg=bpy.context.evaluated_depsgraph_get()
C=Vector((225.5,413.6,133.3))
V=[];F=[];names=[]
GV=[];GF=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or 'cutter' in o.name or o.name=='Context_ground_beyond_data': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(p.x for p in bb);x1=max(p.x for p in bb);y0=min(p.y for p in bb);y1=max(p.y for p in bb)
    if x1<C.x-25 or x0>C.x+25 or y1<C.y-25 or y0>C.y+25: continue
    e=o.evaluated_get(dg)
    try: m=e.to_mesh()
    except: continue
    mw=o.matrix_world; off=len(V)
    big=(x1-x0)>200
    for v in m.vertices:
        p=mw@v.co; V.append(p)
    for f in m.polygons:
        if big:
            c=mw@f.center
            if abs(c.x-C.x)>30 or abs(c.y-C.y)>30: continue
        F.append([i+off for i in f.vertices])
    names.append(o.name); e.to_mesh_clear()
T=BVHTree.FromPolygons(V,F)
print('BVH objs',len(names),'faces',len(F))
st=bpy.data.objects['WD_Bohn_N_steps_313029912_UNVERIFIED']
sm=st.evaluated_get(dg).to_mesh(); SB=BVHTree.FromPolygons([st.matrix_world@v.co for v in sm.vertices],[list(p.vertices) for p in sm.polygons])
tg=[]
for i in range(9):
    for j in range(5):
        x=222.4+i*0.6; y=412.7+j*0.75
        r=SB.ray_cast(Vector((x,y,150)),Vector((0,0,-1)))
        if r[0] is not None and r[1].z>0.7: tg.append(r[0]+Vector((0,0,0.05)))
tg+=[Vector((228.8,412.7,132.5)),Vector((229.8,413.4,132.5))]
SK=bpy.data.objects['Context_skirt_3DEP_ortho_4km'].evaluated_get(dg)
LD=bpy.data.objects['TK_Bohn_landing_N_steps_UNVERIFIED']
def ground(x,y):
    if 226.6<x<231.0 and 411.3<y<414.2: return 132.45
    r=SK.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    return r[1].z if r[0] else None
best=[]
for ix in range(-16,17):
    for iy in range(-14,17):
        x=C.x+ix; y=C.y+iy
        if 222.2<x<231.5 and 411.0<y<416.1 and not (226.6<x<231.0 and 411.3<y<414.2): continue
        g=ground(x,y)
        if g is None: continue
        for h in (1.65,3.5):
            c=Vector((x,y,g+h))
            d0=(C-c); dist=d0.length
            if dist<4 or dist>18: continue
            # nearby clutter in view direction (foliage within 3 m in the cone)
            vis=0
            for t in tg:
                d=t-c; r=T.ray_cast(c,d.normalized(),d.length)
                if r[0] is None or (r[0]-t).length<0.08: vis+=1
            cone=0
            fwd=d0.normalized(); side=fwd.cross(Vector((0,0,1))).normalized(); up=side.cross(fwd)
            for a in (-0.35,0,0.35):
                for b in (-0.2,0,0.2):
                    dd=(fwd+side*a+up*b).normalized(); r=T.ray_cast(c,dd,dist*0.7)
                    if r[0] is not None: cone+=1
            best.append((vis-cone*1.5,vis,cone,h,round(dist,1),[round(c.x,2),round(c.y,2),round(c.z,2)]))
best.sort(key=lambda k:-k[0])
print('TOP',len(tg),best[:8])
eye=[b for b in best if b[3]<2][0]; hi=[b for b in best if b[3]>2][0]
col=bpy.data.collections['WD_Bohn_approach_walks_steps_UNVERIFIED']
def cam(name,loc,tgt,lens):
    o=bpy.data.objects.get(name)
    if o: bpy.data.objects.remove(o)
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=30000; cd.clip_start=0.1
    o=bpy.data.objects.new(name,cd); col.objects.link(o); o['we_obj']=1
    o.location=loc; o.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); return o
cam('WE_CAM_eye_Bohn_N_stair_clear',Vector(eye[5]),C,22)
cam('WE_CAM_closeup_Bohn_N_stair_clear',Vector(hi[5]),C,26)
json.dump(dict(top=best[:20],eye=eye,hi=hi),open('data/we/cam2.json','w'))
print('EYE',eye,'HI',hi)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
