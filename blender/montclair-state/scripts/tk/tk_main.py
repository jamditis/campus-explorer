# tk (Nov 4 2026 ~8:35 PM ET, MAIN, day 8 Student Center east edge). ALL UNVERIFIED, reversible (REVERT=1).
# Bohn Hall (OSM 232853538) as a stepped LiDAR-height massing: OSM footprint, 5 roof levels + penthouse from the 2017 1 m DSM
# (data/tk/bohn_levels.json), parapets, punched-window walls (TK copy of the TJ dorm material, slightly darker = "walls too white"
# fix, applied to the TI Stone/Blanton walls); Bohn gets its own egg-crate window material from the 1971/1975 MSU slides. Culls grass points inside the footprint. Adds TK cameras.
import bpy, bmesh, os, json, math
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
def revert():
    for o in [o for o in bpy.data.objects if 'tk_obj' in o]:
        me=o.data; bpy.data.objects.remove(o)
        if me and me.users==0 and hasattr(me,'vertices'): bpy.data.meshes.remove(me)
        elif me and me.users==0: bpy.data.cameras.remove(me)
    for o in bpy.data.objects:
        if 'tk_orig_mesh' in o:
            cur=o.data; o.data=bpy.data.meshes[o['tk_orig_mesh']]; del o['tk_orig_mesh']; del o['tk_culled']
            if cur.users==0: bpy.data.meshes.remove(cur)
    for me in bpy.data.meshes:
        if 'tk_orig_mat0' in me:
            m0=bpy.data.materials[me['tk_orig_mat0']]; me.materials[0]=m0; m0.use_fake_user=False; del me['tk_orig_mat0']
    c=bpy.data.collections.get('TK_Bohn_Hall_UNVERIFIED')
    if c: bpy.data.collections.remove(c)
    for mn in ('TK_dorm_wall_darker_UNVERIFIED','TK_Bohn_wall_eggcrate_UNVERIFIED'):
        m=bpy.data.materials.get(mn)
        if m: bpy.data.materials.remove(m)
    print('TK reverted')
revert()
if REV:
    if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
GN=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','RZ2_SC_LiDAR_ground_patch','QW_DTM_north_edge_ramp_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED']
gnd=[(bpy.data.objects[n].evaluated_get(dg),bpy.data.objects[n].matrix_world) for n in GN if n in bpy.data.objects]
def gz(x,y):
    best=None
    for e,mw in gnd:
        iw=mw.inverted(); r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        if r[0]:
            z=(mw@r[1]).z
            if best is None or z>best: best=z
    return best
def pip(x,y,poly):
    ins=False; n=len(poly)
    for i in range(n):
        x1,y1=poly[i]; x2,y2=poly[(i+1)%n]
        if (y1>y)!=(y2>y) and x<(x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: ins=not ins
    return ins
def ccw(p):
    a=sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))
    return p if a>0 else p[::-1]
# ---- material: darker copy of the TJ dorm wall
SRC=bpy.data.materials['TJ_dorm_wall_base_UNVERIFIED']; SRC.use_fake_user=True; WM=SRC.copy(); WM.name='TK_dorm_wall_darker_UNVERIFIED'
for n in WM.node_tree.nodes:
    if n.type=='VALTORGB':
        for el in n.color_ramp.elements:
            c=el.color
            if c[0]>0.3: el.color=(c[0]*0.82,c[1]*0.81,c[2]*0.79,1)
RM=bpy.data.materials['TI_roof_membrane_UNVERIFIED']
# Bohn: egg-crate grid of large recessed windows in light concrete, blank end walls (MSU Digital Commons slides 1251 (1971) + 1519 (1975), refs/bohn/)
BM=SRC.copy(); BM.name='TK_Bohn_wall_eggcrate_UNVERIFIED'
CH={'Math':(3.3,2.2),'Math.013':(0.3,0.07),'Math.014':(0.7,0.93),'Math.016':(0.46,0.66),'Math.018':(0.318,0.10),'Math.019':(0.682,0.90),'Math.022':(0.44,0.63),'Math.029':(0.29,0.06),'Math.030':(0.71,0.94)}
for nn,(old,new) in CH.items():
    n=BM.node_tree.nodes[nn]
    for i in n.inputs:
        if not i.is_linked and abs(i.default_value-old)<1e-4: i.default_value=new; break
    else: print('TK WARN const not found',nn,old)
# swap Stone/Blanton walls to the darker copy (orig kept)
sw=0
for o in bpy.data.objects:
    if 'ti_obj' in o and o.type=='MESH' and o.data.materials and o.data.materials[0] and o.data.materials[0].name=='TJ_dorm_wall_base_UNVERIFIED':
        o.data['tk_orig_mat0']=o.data.materials[0].name; o.data.materials[0]=WM; sw+=1
print('TK walls darkened on',sw,'TI meshes')
col=bpy.data.collections.new('TK_Bohn_Hall_UNVERIFIED'); sc.collection.children.link(col)
def mass(name,poly,zb,z1,floor,z0g,note,par=0.5,blank=2.4):
    poly=ccw([tuple(p[:2]) for p in poly]); bm=bmesh.new()
    vs=[bm.verts.new((x,y,zb)) for x,y in poly]; f=bm.faces.new(vs)
    r=bmesh.ops.extrude_face_region(bm,geom=[f]); top=[g for g in r['geom'] if isinstance(g,bmesh.types.BMFace)][0]
    for v in top.verts: v.co.z=z1
    bmesh.ops.reverse_faces(bm,faces=[f])
    bmesh.ops.inset_region(bm,faces=[top],thickness=0.3,depth=0)
    for v in top.verts: v.co.z=z1-par
    bm.normal_update()
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.materials.append(BM); me.materials.append(RM)
    for k,t in (('ti_dir','FLOAT_VECTOR'),('ti_floor','FLOAT'),('ti_z0','FLOAT'),('ti_z1','FLOAT')): me.attributes.new(k,t,'FACE')
    V=me.vertices; DIRS=[]; MI=[]; Z1=[]
    # collinear runs of footprint edges (direction change < 20 deg) -> run length per edge
    ne=len(poly); ED=[]
    for i in range(ne):
        a=poly[i]; b=poly[(i+1)%ne]; ED.append((math.atan2(b[1]-a[1],b[0]-a[0]),math.hypot(b[0]-a[0],b[1]-a[1]),((a[0]+b[0])/2,(a[1]+b[1])/2)))
    rid=[0]*ne
    for i in range(1,ne):
        dd=abs((ED[i][0]-ED[i-1][0]+math.pi)%(2*math.pi)-math.pi); rid[i]=rid[i-1]+(1 if dd>math.radians(20) else 0)
    if ne>1 and abs((ED[0][0]-ED[-1][0]+math.pi)%(2*math.pi)-math.pi)<=math.radians(20):
        last=rid[-1]; rid=[0 if r==last else r for r in rid]
    RL={}
    for i in range(ne): RL[rid[i]]=RL.get(rid[i],0)+ED[i][1]
    def runlen(cx,cy):
        i=min(range(ne),key=lambda k:(ED[k][2][0]-cx)**2+(ED[k][2][1]-cy)**2); return RL[rid[i]]
    for p in me.polygons:
        best=(0,(1,0))
        for i in range(len(p.vertices)):
            a=V[p.vertices[i]].co; c=V[p.vertices[(i+1)%len(p.vertices)]].co; dx,dy=c.x-a.x,c.y-a.y; l=math.hypot(dx,dy)
            if l>best[0]: best=(l,(dx/l,dy/l))
        Z1.append(z0g if (abs(p.normal.z)<0.5 and runlen(p.center.x,p.center.y)<blank) else z1)
        DIRS.extend((best[1][0],best[1][1],0)); MI.append(1 if (p.normal.z>0.9 and p.center.z<z1-0.3) else 0)
    n=len(me.polygons)
    me.attributes['ti_dir'].data.foreach_set('vector',DIRS); me.attributes['ti_floor'].data.foreach_set('value',[floor]*n)
    me.attributes['ti_z0'].data.foreach_set('value',[z0g]*n); me.attributes['ti_z1'].data.foreach_set('value',Z1)
    me.polygons.foreach_set('material_index',MI)
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['tk_obj']=1; o['UNVERIFIED']=note
    return o
E=json.load(open('data/tk/bohn_levels.json')); out=E['outer']
zs=sorted(z for z in (gz(x,y) for x,y in out) if z is not None)
z0g=zs[len(zs)//2] if zs else E['ground_med']; zb=(zs[0] if zs else E['ground_med']-6)-0.4
print('TK ground boundary min/med/max',round(zs[0],2),round(z0g,2),round(zs[-1],2))
note='OSM 232853538 footprint (ODbL) + 2017 NJ LiDAR DSM roof levels; walls/windows/parapet typical, NO facade refs'
FL=2.75
made=[mass('TK_Bohn_Hall_232853538_base_UNVERIFIED',out,zb,E['base_top'],FL,z0g,note,blank=8.0)]
prev_top=E['base_top']
for L in E['levels']:
    for i,(pp,top) in enumerate(zip(L['polys'],L['tops'])):
        par=1.1 if L['name']=='PH' else 0.5
        made.append(mass('TK_Bohn_Hall_%s_%d_UNVERIFIED'%(L['name'],i),pp,prev_top-0.6,top,FL,z0g,note,par,blank=(999 if L['name']=='PH' else 8.0)))
    prev_top=max(L['tops'])
# overlap check
xs=[p[0] for p in out]; ys=[p[1] for p in out]
for o in bpy.data.objects:
    if o.type!='MESH' or 'tk_obj' in o or o.hide_render: continue
    n=o.name.lower()
    if any(k in n for k in ('terrain','skirt','grass','ground','context','sky','bd_')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; bx=[v.x for v in bb]; by=[v.y for v in bb]
    if max(bx)-min(bx)>400: continue
    if min(bx)<max(xs) and max(bx)>min(xs) and min(by)<max(ys) and max(by)>min(ys): print('TK overlap',o.name,round(min(bx)),round(max(bx)),round(min(by)),round(max(by)))
def near_edge(x,y,P,d):
    for i in range(len(P)):
        a=Vector((P[i][0],P[i][1],0)); b=Vector((P[(i+1)%len(P)][0],P[(i+1)%len(P)][1],0)); q=Vector((x,y,0))
        t=max(0,min(1,(q-a).dot(b-a)/max((b-a).length_squared,1e-9)))
        if (a+(b-a)*t-q).length<d: return True
    return False
tot=0; x0,x1,y0,y1=min(xs)-1,max(xs)+1,min(ys)-1,max(ys)+1
for o in bpy.data.objects:
    if o.type!='MESH' or 'grass' not in o.name.lower() or not o.data.vertices or len(o.data.polygons)>0: continue
    mw=o.matrix_world; idx=[]
    for v in o.data.vertices:
        w=mw@v.co
        if x0<w.x<x1 and y0<w.y<y1 and (pip(w.x,w.y,out) or near_edge(w.x,w.y,out,0.8)): idx.append(v.index)
    if not idx: continue
    me=o.data; o['tk_orig_mesh']=me.name; me.use_fake_user=True; nm=me.copy(); nm.name=me.name+'.tk'; o.data=nm; o['tk_culled']=len(idx)
    bm=bmesh.new(); bm.from_mesh(nm); bm.verts.ensure_lookup_table(); bmesh.ops.delete(bm,geom=[bm.verts[i] for i in idx],context='VERTS'); bm.to_mesh(nm); bm.free()
    tot+=len(idx); print('TK grass culled',o.name,len(idx),'left',len(nm.vertices))
print('TK grass total',tot)

# entrances where OSM steps 313029912 / footway 1132693523 end on the Bohn wall (positions OSM, design invented)
GM=bpy.data.materials.get('TJ_door_glass_UNVERIFIED'); FM=bpy.data.materials.get('TJ_door_frame_UNVERIFIED')
oc=ccw([tuple(p) for p in out])
def boxo(name,c,u,n,w,d0,d1,z0,z1,mat):
    bm=bmesh.new(); vs=[]
    for a in (-w/2,w/2):
        for dd in (d0,d1):
            for z in (z0,z1): vs.append(bm.verts.new((c[0]+u[0]*a+n[0]*dd,c[1]+u[1]*a+n[1]*dd,z)))
    bmesh.ops.convex_hull(bm,input=vs); me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['tk_obj']=1; o['UNVERIFIED']='door at OSM path end; design invented'; return o
nd=0
for tag,(px,py) in (('N_steps',(231.0,412.4)),('W_walk',(216.0,403.2))):
    best=None
    for i in range(len(oc)):
        a=Vector((*oc[i],0)); b=Vector((*oc[(i+1)%len(oc)],0)); q=Vector((px,py,0)); t=max(0,min(1,(q-a).dot(b-a)/(b-a).length_squared)); d=(a+(b-a)*t-q).length
        if (b-a).length<4.5: continue
        if best is None or d<best[0]: best=(d,a,b,t)
    d,a,b,t=best; L=(b-a).length; u=(b-a).normalized(); t=min(max(t,2.2/L),1-2.2/L); c=a+(b-a)*t; n=Vector((u.y,-u.x,0))
    z=gz(c.x+n.x*1.2,c.y+n.y*1.2) or z0g
    boxo('TK_Bohn_door_frame_%s_UNVERIFIED'%tag,c,u,n,3.2,-0.05,0.12,z-0.3,z+2.75,FM)
    boxo('TK_Bohn_door_glass_%s_UNVERIFIED'%tag,c,u,n,2.8,0.12,0.14,z,z+2.55,GM)
    boxo('TK_Bohn_door_stile_%s_UNVERIFIED'%tag,c,u,n,0.08,0.14,0.17,z,z+2.55,FM)
    boxo('TK_Bohn_door_transom_%s_UNVERIFIED'%tag,c,u,n,2.8,0.14,0.17,z+2.1,z+2.18,FM)
    boxo('TK_Bohn_canopy_%s_UNVERIFIED'%tag,c,u,n,4.2,-0.05,1.7,z+3.0,z+3.22,FM)
    boxo('TK_Bohn_landing_%s_UNVERIFIED'%tag,c,u,n,4.2,0.0,1.9,z-0.35,z+0.03,bpy.data.materials.get('TJ_door_frame_UNVERIFIED'))
    nd+=1; print('TK door',tag,[round(c.x,1),round(c.y,1),round(z,2)],'edge',round(L,1))
def cam(name,loc,tgt,lens):
    cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=30000; o=bpy.data.objects.new(name,cd); col.objects.link(o); o['tk_obj']=1
    o.location=loc; d=Vector(tgt)-Vector(loc)
    o.rotation_euler=(math.pi/2+math.atan2(d.z,math.hypot(d.x,d.y)),0,math.atan2(d.y,d.x)-math.pi/2); return o
ga=gz(150,330) or 137
cam('TK_CAM_oblique_Bohn_from_SW',(120,270,ga+70),(226,382,150),30)
ge=gz(165,395) or 135
cam('TK_CAM_eye_Bohn_from_W',(165,395,ge+1.65),(222,384,ge+14),24)
gc=gz(196,372) or 133
cam('TK_CAM_closeup_Bohn_SW_corner',(192,362,gc+3),(208,376,gc+8),30)
gw=gz(204,407) or 133
cam('TK_CAM_closeup_Bohn_W_entrance',(203,409,gw+1.7),(216,402.5,gw+2.0),30)
print('TK applied',len(made),'masses; objects',len(bpy.data.objects))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
