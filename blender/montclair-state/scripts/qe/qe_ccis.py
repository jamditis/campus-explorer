# qe (Nov 2 2026): CCIS facades in MAIN. ALL UNVERIFIED (no post-2018 CCIS photo on disk). REVERT=1 removes everything tagged qe.
# Keeps MAIN's LiDAR-fitted walls+roof (the Oct 14 north masses are appended HIDDEN as reference only, outline +-1 m).
# Adds surface-mounted window units (cream stucco surround, bronze frame+mullion, tinted glass over a dark interior card, precast sill),
# glazed entrances where MAIN walk meshes touch the footprint, and 4 cameras.
import bpy, bmesh, os, math, json
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
CN='Center for Computing and Information Science'
MATS=['QE_CCIS_trim_cream_UNVERIFIED']
NW='QE_CCIS_stucco_no_shader_windows_UNVERIFIED'; MATS.append(NW)
SLOTOBJ=[(CN+' walls',0),(CN+' roof (LiDAR)',3)]
def rm():
    for on,si in SLOTOBJ:
        o=bpy.data.objects.get(on)
        if o and o.material_slots[si].link=='OBJECT' and o.material_slots[si].material and o.material_slots[si].material.name==NW:
            o.material_slots[si].material=None; o.material_slots[si].link='DATA'
    for o in [o for o in bpy.data.objects if o.get('qe')]:
        me=o.data; bpy.data.objects.remove(o,do_unlink=True)
        if me and me.users==0:
            (bpy.data.meshes if isinstance(me,bpy.types.Mesh) else bpy.data.cameras).remove(me)
    c=bpy.data.collections.get(CN)
    if c: bpy.data.collections.remove(c)
    for m in MATS+list(bpy.context.scene.get('qe_new_mats',[])):
        if m in bpy.data.materials and bpy.data.materials[m].users==0: bpy.data.materials.remove(bpy.data.materials[m])
    if 'qe_new_mats' in bpy.context.scene: del bpy.context.scene['qe_new_mats']
    if 'qe_door_pts' in bpy.context.scene: del bpy.context.scene['qe_door_pts']
    for me in [m for m in bpy.data.meshes if m.users==0 and m.name.startswith(('QE_','CCIS '))]: bpy.data.meshes.remove(me)
if REV:
    rm(); print('QE_CCIS reverted')
else:
    rm()
    col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
    # 1. reference masses from north, hidden
    M0=set(m.name for m in bpy.data.materials)
    NB='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
    with bpy.data.libraries.load(NB,link=False) as (src,dst):
        dst.objects=[n for n in src.objects if n.startswith('CCIS ')]
    for o in dst.objects:
        if o is None: continue
        col.objects.link(o); o['qe']=1; o.hide_render=True; o.hide_viewport=True
        o.name=('QE_ref_'+o.name)[:63]
    bpy.context.scene['qe_new_mats']=[m.name for m in bpy.data.materials if m.name not in M0]
    print('QE_appended',[o.name for o in dst.objects if o])
    base=bpy.data.materials['Wall_stucco_mission']; nw=base.copy(); nw.name=NW; T=nw.node_tree
    for l in list(T.links):
        if (l.to_node.name in ('Mix Shader','Mix Shader.001') and l.to_socket.name=='Fac') or l.to_node.name=='Bump': T.links.remove(l)
    T.nodes['Mix Shader'].inputs['Fac'].default_value=0.0; T.nodes['Mix Shader.001'].inputs['Fac'].default_value=0.0; T.nodes['Bump'].inputs['Height'].default_value=0.0
    for on,si in SLOTOBJ:
        o=bpy.data.objects[on]; assert o.material_slots[si].material.name=='Wall_stucco_mission'; o.material_slots[si].link='OBJECT'; o.material_slots[si].material=nw
    if os.environ.get('SHOWL1')=='1':
        for o in dst.objects:
            if o and ('L1_main' in o.name or 'L0_south' in o.name):
                o.hide_render=False; o.hide_viewport=False
                for sl in o.material_slots: sl.link='OBJECT'; sl.material=nw
                print('QE_L1bb',o.name,[tuple(round(x,1) for x in (o.matrix_world@__import__('mathutils').Vector(c))) for c in (o.bound_box[0],o.bound_box[6])])
    # materials
    def M(n): return bpy.data.materials[n]
    trim=bpy.data.materials.new(MATS[0]); trim.use_nodes=True
    bs=trim.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(0.80,0.74,0.62,1); bs.inputs['Roughness'].default_value=0.85
    frameM=M('PE_Dickson_coping_dark_bronze_UNVERIFIED'); sillM=M('North_Feliciano_sill_tan'); glassM=M('PS_slot_glass_tinted_UNVERIFIED'); darkM=M('PS_slot_interior_dark_UNVERIFIED')
    mats=[trim,frameM,sillM,glassM,darkM]
    poly=[Vector((x,y)) for x,y in json.load(open('north/data/day_heroes/day7_geom.json'))['buildings'][CN]['poly_m']][:-1]
    area=sum(poly[i].x*poly[(i+1)%len(poly)].y-poly[(i+1)%len(poly)].x*poly[i].y for i in range(len(poly)))/2
    W=bpy.data.objects[CN+' walls']; R=bpy.data.objects[CN+' roof (LiDAR)']
    segs=[]
    for p in W.data.polygons:
        if abs(p.normal.z)>0.2: continue
        vs=[W.matrix_world@W.data.vertices[i].co for i in p.vertices]
        segs.append((Vector((sum(v.x for v in vs)/len(vs),sum(v.y for v in vs)/len(vs))),min(v.z for v in vs),max(v.z for v in vs)))
    dg=bpy.context.evaluated_depsgraph_get(); Re=R.evaluated_get(dg); Rinv=R.matrix_world.inverted()
    def roof_at(xy):
        o=Rinv@Vector((xy.x,xy.y,200)); d=(Rinv.to_3x3()@Vector((0,0,-1))).normalized()
        ok,loc,n,i=Re.ray_cast(o,d)
        return (R.matrix_world@loc).z if ok else None
    def wall_at(xy):
        best=[s for s in segs if (s[0]-xy).length<1.0]
        if not best: return None
        return max(s[1] for s in best), max(s[2] for s in best)
    # walk contacts -> entrances
    walks=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and ('walk' in o.name.lower() or 'footway' in o.name.lower() or 'path' in o.name.lower()) and 'joint' not in o.name.lower() and 'lip' not in o.name.lower() and 'grime' not in o.name.lower() and 'curb' not in o.name.lower()]
    hits=[]
    for o in walks:
        mw=o.matrix_world
        bb=[mw@Vector(c) for c in o.bound_box]
        if max(v.x for v in bb)<0 or min(v.x for v in bb)>46 or max(v.y for v in bb)<180 or min(v.y for v in bb)>250: continue
        for v in o.data.vertices:
            w=mw@v.co; p=Vector((w.x,w.y))
            for i in range(len(poly)):
                a,b=poly[i],poly[(i+1)%len(poly)]; e=b-a; L=e.length; t=max(0,min(L,(p-a).dot(e)/L))
                if (a+e*(t/L)-p).length<0.9 and 1.5<t<L-1.5: hits.append((i,t,w.z))
    ent={}
    HZ={}
    for i,t,n in hits: ent.setdefault(i,[]).append(t); HZ.setdefault(i,[]).append((t,n))
    entr=[]
    for i,ts in ent.items():
        ts.sort(); cl=[[ts[0]]]
        for t in ts[1:]:
            if t-cl[-1][-1]<2.5: cl[-1].append(t)
            else: cl.append([t])
        for c in cl:
            if len(c)>=3:
                zs=sorted(z for t,z in HZ[i] if c[0]-0.01<=t<=c[-1]+0.01); entr.append((i,(c[0]+c[-1])/2,zs[len(zs)//2]))
    print('QE_walks',len(walks),'hits',len(hits),'entr',entr)
    bm=bmesh.new()
    def box(c,ax,ay,az,hx,hy,hz,mi):
        # c centre, ax/ay/az unit axes, half sizes
        vs=[bm.verts.new(c+ax*sx*hx+ay*sy*hy+az*sz*hz) for sx in(-1,1) for sy in(-1,1) for sz in(-1,1)]
        for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
            try: bm.faces.new([vs[k] for k in f]).material_index=mi
            except ValueError: pass
    def quad(c,ax,az,hx,hz,mi):
        vs=[bm.verts.new(c+ax*sx*hx+az*sz*hz) for sx,sz in((-1,-1),(1,-1),(1,1),(-1,1))]
        bm.faces.new(vs).material_index=mi
    Z=Vector((0,0,1)); nwin=0; nent=0; log=[]
    def window(p,t,n,zb,w,h,door=False):
        # p: wall point (xy, z ignored); t along, n outward
        c=Vector((p.x,p.y,zb+h/2))
        quad(c+n*0.012,t,Z,w/2,h/2,4)          # dark interior card
        quad(c+n*0.045,t,Z,w/2,h/2,3)          # glass
        s=0.16; d=0.09  # stucco surround ring width / projection
        box(c+t*(w/2+s/2)+n*d/2,t,n,Z,s/2,d/2,h/2+s,0); box(c-t*(w/2+s/2)+n*d/2,t,n,Z,s/2,d/2,h/2+s,0)
        box(c+Z*(h/2+s/2)+n*d/2,t,n,Z,w/2,d/2,s/2,0)
        f=0.055; fd=0.075
        for sx in(-1,1): box(c+t*sx*(w/2-f/2)+n*fd/2,t,n,Z,f/2,fd/2,h/2,1)
        box(c+Z*(h/2-f/2)+n*fd/2,t,n,Z,w/2,fd/2,f/2,1)
        if door:
            box(c+n*fd/2,t,n,Z,0.03,fd/2,h/2,1)                                 # meeting stile
            box(c+Z*(h/2-0.6)+n*fd/2,t,n,Z,w/2,fd/2,0.03,1)                      # transom bar
            box(Vector((p.x,p.y,zb+h+s+0.12))+n*0.75,t,n,Z,w/2+0.5,0.75,0.08,0)  # canopy slab
            box(Vector((p.x,p.y,zb-0.06))+n*0.9,t,n,Z,w/2+0.4,0.9,0.06,2)        # landing
        else:
            box(c-Z*(h/2-f/2)+n*fd/2,t,n,Z,w/2,fd/2,f/2,1)
            box(c+n*fd/2,t,n,Z,0.025,fd/2,h/2,1)                                # centre mullion
            box(c+Z*(h/2-0.55)+n*fd/2,t,n,Z,w/2,fd/2,0.022,1)                   # transom
            box(c-Z*(h/2+0.05)+n*0.11,t,n,Z,w/2+0.2,0.11,0.05,2)                # precast sill
    DP=[]
    SP=float(os.environ.get('SP','3.0')); WW=1.25; WH=1.85; ST=3.95
    for i in range(len(poly)):
        a,b=poly[i],poly[(i+1)%len(poly)]; e=b-a; L=e.length; t2=e.normalized()
        n2=Vector((t2.y,-t2.x)) if area>0 else Vector((-t2.y,t2.x))
        t=Vector((t2.x,t2.y,0)); n=Vector((n2.x,n2.y,0))
        es=[(ii,u) for ii,u,_ in entr if ii==i]
        for ii,u,wz in [e_ for e_ in entr if e_[0]==i]:
            p=a+t2*u; wa=wall_at(p)
            if wa: DP.append((p.x,p.y,wz)); window(p,t,n,wz+0.03,2.0,3.0,door=True); nent+=1; log.append(('door',i,round(u,1),round(wz,2),'wallbase',round(wa[0],2)))
        if L<3.2: continue
        k=max(1,int((L-1.6)//SP)); off=(L-(k-1)*SP)/2 if k>1 else L/2
        for j in range(k):
            u=off+j*SP; p=a+t2*u; wa=wall_at(p)
            if not wa: continue
            zb,zt=wa; rz=roof_at(p-n2*0.6)
            top=max(zt,rz) if (rz is not None and rz<zt+8) else zt
            for s in range(6):
                sill=zb+1.0+s*ST
                if sill+WH>top-0.8: break
                if s==0 and any(abs(u-ue)<2.3 for _,ue in es): continue
                window(p,t,n,sill,WW,WH); nwin+=1
    if os.environ.get('CURTAIN','1')=='1': exec(open('scripts/qe/qe_curtain.py').read())
    me=bpy.data.meshes.new('QE_CCIS_window_units_UNVERIFIED'); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    ob=bpy.data.objects.new('QE_CCIS_window_units_entrances_UNVERIFIED',me); ob['qe']=1; col.objects.link(ob)
    bpy.context.scene['qe_door_pts']=DP
    print('QE_CCIS windows',nwin,'entrances',nent,log,'polys',len(me.polygons))
    # cameras
    def ground(x,y):
        ok,loc,*_=bpy.context.scene.ray_cast(dg,Vector((x,y,250)),Vector((0,0,-1)))
        return loc.z if ok else 138.5
    def cam(name,pos,tgt,lens=28):
        cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=3000; c=bpy.data.objects.new(name,cd); c['qe']=1; col.objects.link(c)
        c.location=pos; c.rotation_euler=(Vector(tgt)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
    C=Vector((22.0,215.6,147))
    cam('QE_CAM_oblique_ccis_from_SW',(-45,150,205),(22,214,146),35)
    trees=[]
    for o in bpy.context.scene.objects:
        if o.type in('MESH','CURVES') and not o.hide_render and (o.name.startswith(('T_','NT','Tree','tree')) or 'Tree' in o.name):
            l=o.matrix_world.translation
            if -80<l.x<120 and 130<l.y<300: trees.append((Vector((l.x,l.y)),max(o.dimensions.x,o.dimensions.y)/2))
    def clear(px,py,tx,ty):
        a=Vector((px,py)); b=Vector((tx,ty)); e=b-a; L=e.length
        for c,r in trees:
            t_=max(0,min(L*0.6,(c-a).dot(e)/L)); 
            if (a+e*(t_/L)-c).length<r+1.0: return False
        return True
    def eyecam(name,ang0,tgt,R0=34):
        for dA in (0,8,-8,16,-16,24,-24,32,-32,40,-40):
            for RR in (R0,R0-8,R0+8):
                a=math.radians(ang0+dA); px=22+RR*math.cos(a); py=215.6+RR*math.sin(a)
                if clear(px,py,tgt[0],tgt[1]):
                    g=ground(px,py); cam(name,(px,py,g+1.7),(tgt[0],tgt[1],g+7),24); print('QE_eyecam',name,round(px,1),round(py,1),dA,RR); return
        print('QE_eyecam none',name)
    eyecam('QE_CAM_eye_ccis_west',190,(12,212))
    eyecam('QE_CAM_eye_ccis_east',0,(33,220))
    if entr:
        i,u,_=entr[0]; a,b=poly[i],poly[(i+1)%len(poly)]; t2=(b-a).normalized(); n2=Vector((t2.y,-t2.x)) if area>0 else Vector((-t2.y,t2.x))
        p=a+t2*u; q=p+n2*9+t2*3.5; gq=ground(q.x,q.y); zb=entr[0][2]
        cam('QE_CAM_closeup_ccis_entrance',(q.x,q.y,gq+1.6),(p.x,p.y,zb+2.4),30)
        print('QE_closecam',tuple(round(x,2) for x in q),i,round(u,2))
