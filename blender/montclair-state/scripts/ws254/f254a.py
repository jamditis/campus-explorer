# ws254 (CHAIN via ws208/merge208.py on main ws253g): UNIFY W63e — Feliciano E recess ground + probable entrance, flight A grass dip,
# W63d walk north end joined to the OSM walk.
# Evidence: evaluated ground probe (probe254.out): recess x -197.6..-195.2 rose 135.7 -> 136.7 m over y 168.5-172 (0.3-0.6 m above the
# landing/flight B treads); wall ray probe: Feliciano E wall at x -197.56 (y 166.5) .. -197.26 (y 171.5), -194.69 for y >= 172.
# 2023 LiDAR: only ground return under the eave is a strip at y 168 (x -198..-194, 135.5 m) -> entrance at the landing (UNVERIFIED:
# door type/width/height; no photo). Ortho (crop254): N-S light strip x -192..-189.5 continues north into the building shadow; the OSM
# walk starts at y ~190.8 (x -191..-190.4).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F254A'
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; P1=bpy.data.objects['WS251_W63b_passage_LiDAR2023_ground_patch_1m']; P2=bpy.data.objects['WS250_W63_lawn_LiDAR2023_ground_patch_1m']
COL=P1.users_collection[0]
M_STEP=bpy.data.materials.get('WS35_concrete_steps'); M_WALL=bpy.data.materials.get('OH_cheek_wall_concrete_UNVERIFIED'); M_WALK=bpy.data.materials.get('WS159_concrete_walk_broomed')
print(TAG,'mats',bool(M_STEP),bool(M_WALL),bool(M_WALK),flush=True)
O=np.load('/workspace/nj-scenes/montclair-state/scripts/ws251/d251a.npy')[0]
def oz(x,y):
    fx=x-(-204)-0.5; fy=y-128-0.5; i=min(max(int(np.floor(fx)),0),O.shape[1]-2); j=min(max(int(np.floor(fy)),0),O.shape[0]-2); tx=min(max(fx-i,0),1); ty=min(max(fy-j,0),1)
    q=O[j:j+2,i:i+2]; return float(q[0,0]*(1-tx)*(1-ty)+q[0,1]*tx*(1-ty)+q[1,0]*(1-tx)*ty+q[1,1]*tx*ty)
XW,XE,XC=-194.95,-189.5,-189.25; Z0=134.03; XR=-197.62
SEG=[(163.8,166.6,'st',Z0,135.27,8),(166.6,168.6,'wk',135.27,135.30,0),(168.6,171.6,'st',135.30,136.70,9),(171.6,176.4,'wk',136.70,136.87,0)]
def box(bm,x0,x1,y0,y1,z0,z1):
    vs=[bm.verts.new((x,y,z)) for z in (z0,z1) for y in (y0,y1) for x in (x0,x1)]
    for q in ((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)): bm.faces.new([vs[i] for i in q])
def obj(name,bm,mats):
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    me=bpy.data.meshes.new(name); bm.normal_update(); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        n=p.normal
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=(co.x,co.y) if abs(n.z)>0.5 else ((co.y if abs(n.x)>abs(n.y) else co.x),co.z)
    o=bpy.data.objects.new(name,me); COL.objects.link(o); print(TAG,'obj',name,len(me.vertices),len(me.polygons),flush=True); return o
if 'WS254_W63e_recess_stairs_landing_to_wall_UNVERIFIED' not in bpy.data.objects:
    # (0) drop the raise-only apron (it rode the hump)
    ap=bpy.data.objects.get('WS253_W63d_Feliciano_E_recess_apron_raise_only_UNVERIFIED')
    if ap: bpy.data.objects.remove(ap,do_unlink=True); print(TAG,'apron removed',flush=True)
    # (1) base terrain: bisect along the recess box lines and delete the faces wholly inside (W63b method)
    x0,x1,y0,y1=XR+0.02,-195.0,163.8,172.0; e=1e-3; M=T.matrix_world; Mi=M.inverted()
    bm=bmesh.new(); bm.from_mesh(T.data); nf0=len(bm.faces)
    def over(f):
        ws=[M@v.co for v in f.verts]; return not (max(w.x for w in ws)<x0-e or min(w.x for w in ws)>x1+e or max(w.y for w in ws)<y0-e or min(w.y for w in ws)>y1+e)
    for co,no in (((x0,0,0),(1,0,0)),((x1,0,0),(1,0,0)),((0,y0,0),(0,1,0)),((0,y1,0),(0,1,0))):
        fs=[f for f in bm.faces if over(f)]; es=list({ed for f in fs for ed in f.edges}); vv=list({v for f in fs for v in f.verts})
        pc=Mi@Vector(co); pn=(Mi.to_3x3().inverted().transposed()@Vector(no)).normalized()
        bmesh.ops.bisect_plane(bm,geom=fs+es+vv,dist=1e-4,plane_co=pc,plane_no=pn)
    dl=[f for f in bm.faces if all(x0-e<=(M@v.co).x<=x1+e and y0-e<=(M@v.co).y<=y1+e for v in f.verts)]
    ar=sum(f.calc_area() for f in dl); bmesh.ops.delete(bm,geom=dl,context='FACES_ONLY')
    print(TAG,'terrain faces',nf0,'->',len(bm.faces),'deleted',len(dl),'area %.1f m2 (box %.1f)'%(ar,(x1-x0)*(y1-y0)),flush=True)
    bm.to_mesh(T.data); bm.free(); T.data.update()
    # (2) W cheek (x -195.2..-194.95) removed so the flights + landing run to the recessed wall
    ch=bpy.data.objects['WS253_W63d_Feliciano_E_stair_cheek_walls_UNVERIFIED']; Mc=ch.matrix_world
    bm=bmesh.new(); bm.from_mesh(ch.data); dv=[v for v in bm.verts if (Mc@v.co).x<-194.9]; bmesh.ops.delete(bm,geom=dv,context='VERTS')
    bm.to_mesh(ch.data); bm.free(); ch.data.update(); print(TAG,'W cheek verts deleted',len(dv),flush=True)
    # (3) treads/landing/walk strip widened west (x XR .. XW, abutting the WS253 boxes; W end tucked into the wall)
    bm=bmesh.new()
    for (a,b,k,za,zb,nr) in SEG:
        if k=='st':
            r=(zb-za)/nr; t=(b-a)/nr
            for kk in range(nr):
                y0k=a+kk*t; y1k=(b if kk==nr-1 else a+(kk+1)*t+0.02); box(bm,XR,XW,y0k,y1k,133.70,za+(kk+1)*r)
        else:
            bb=min(b,172.0)
            vs=[bm.verts.new((x,y,z)) for z0 in (0,1) for y in (a,bb) for x in (XR,XW) for z in [(za+(zb-za)*(y-a)/(b-a))-(0.35 if z0==0 else 0)]]
            for q in ((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)): bm.faces.new([vs[i] for i in q])
    obj('WS254_W63e_recess_stairs_landing_to_wall_UNVERIFIED',bm,[M_STEP])
    # (4) new W cheek on flight A's exposed west end (south of the building corner, y < 166.3), straight cap = nosing + 0.15
    a,b,za,zb,nr=163.8,166.6,Z0,135.27,8; r=(zb-za)/nr; t=(b-a)/nr; zn=lambda y: za+r*min(nr,max(1.0,1+(y-a)/t))
    prof=[(a,zn(a)+0.15),(a+t,zn(a+t)+0.15),(b,zn(b)+0.15)]; bm=bmesh.new(); XA,XB=XR-0.25,XR
    A=[bm.verts.new((XA,y,z)) for y,z in prof]; C=[bm.verts.new((XB,y,z)) for y,z in prof]; A0=[bm.verts.new((XA,y,133.70)) for y,z in prof]; C0=[bm.verts.new((XB,y,133.70)) for y,z in prof]
    for i in range(2):
        bm.faces.new([A[i],A[i+1],C[i+1],C[i]]); bm.faces.new([A0[i],A[i],A[i+1],A0[i+1]]); bm.faces.new([C0[i],C0[i+1],C[i+1],C[i]]); bm.faces.new([A0[i],A0[i+1],C0[i+1],C0[i]])
    bm.faces.new([A0[0],C0[0],C[0],A[0]]); bm.faces.new([A0[-1],A[-1],C[-1],C0[-1]])
    obj('WS254_W63e_flightA_W_cheek_UNVERIFIED',bm,[M_WALL])
    # (5) probable entrance: glazed double door on the recessed wall at the landing (UNVERIFIED), frame + 2 leaves + transom
    def wx(y): return -197.56+0.06*(y-166.5)
    mg=None; mf=None
    for n in ('PJ_Feliciano_east_windows_UNVERIFIED',):
        o=bpy.data.objects.get(n)
        if o:
            for m in o.data.materials:
                if m and ('glass' in m.name.lower() or 'glaz' in m.name.lower()) and not mg: mg=m
                elif m and not mf: mf=m
    print(TAG,'door mats',mg.name if mg else None,mf.name if mf else None,flush=True)
    if not mg:
        mg=bpy.data.materials.new('WS254_door_glass_dark'); mg.use_nodes=True; bs=mg.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(0.03,0.04,0.05,1); bs.inputs['Roughness'].default_value=0.05; bs.inputs['Metallic'].default_value=0.6
    if not mf:
        mf=bpy.data.materials.new('WS254_door_frame_alu'); mf.use_nodes=True; bs=mf.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(0.35,0.36,0.37,1); bs.inputs['Metallic'].default_value=0.9; bs.inputs['Roughness'].default_value=0.35
    ZL=135.30; ya,yb=166.7,168.5; zt=ZL+2.25; ztr=ZL+2.75
    bm=bmesh.new()
    def slab(y0,y1,z0,z1,d0,d1,mi):
        vs=[bm.verts.new((wx(y)+d,y,z)) for z in (z0,z1) for y in (y0,y1) for d in (d0,d1)]
        for q in ((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)): f=bm.faces.new([vs[i] for i in q]); f.material_index=mi
    fw=0.07
    slab(ya-fw,ya,ZL,ztr,0.0,0.09,1); slab(yb,yb+fw,ZL,ztr,0.0,0.09,1)           # jambs
    slab(ya-fw,yb+fw,ztr,ztr+fw,0.0,0.09,1); slab(ya,yb,zt,zt+0.06,0.0,0.09,1)  # head + transom bar
    ym=(ya+yb)/2; slab(ym-0.03,ym+0.03,ZL,zt,0.0,0.09,1)                         # meeting stiles
    slab(ya,ym-0.03,ZL,ZL+0.12,0.0,0.08,1); slab(ym+0.03,yb,ZL,ZL+0.12,0.0,0.08,1)  # bottom rails
    slab(ya,yb,ZL+0.12,zt,0.02,0.04,0); slab(ya,yb,zt+0.06,ztr,0.02,0.04,0)     # glass (leaves + transom)
    for yy in (ya+0.12,yb-0.12): slab(yy-0.015,yy+0.015,ZL+0.95,ZL+1.05,0.09,0.13,1) # pull handles
    obj('WS254_W63e_Feliciano_E_entrance_doors_UNVERIFIED',bm,[mg,mf])
    # base course strip removed across the door opening
    pi=bpy.data.objects.get('PI_Feliciano_east_base_course_UNVERIFIED')
    if pi:
        Mp=pi.matrix_world; bm=bmesh.new(); bm.from_mesh(pi.data)
        df=[f for f in bm.faces if all((Mp@v.co).x<-196.8 and ya-0.1<=(Mp@v.co).y<=yb+0.1 for v in f.verts)]
        print(TAG,'base course faces in door zone',len(df),'of',len(bm.faces),flush=True)
        bm.free()
    # (6) grass dip beside the E cheek: x -189 column restored toward the original ground, kept 8 cm under the cheek cap
    def ecap(y):
        for (a,b,k,za,zb,nr) in SEG:
            if k=='st' and a-1e-6<=y<=b+1e-6:
                r=(zb-za)/nr; t=(b-a)/nr; zn=lambda yy: za+r*min(nr,max(1.0,1+(yy-a)/t))
                need=max(oz(-188.8,a+(b-a)*i/20)+0.10-zn(a+(b-a)*i/20) for i in range(21)); return zn(y)+max(0.15,need)
        return None
    for P in (P1,P2):
        me=P.data; Mw=P.matrix_world; Mi2=Mw.inverted(); n=0
        for v in me.vertices:
            w=Mw@v.co
            if XC+0.05<w.x<=-188.9 and 163.8<=w.y<=171.6:
                c=ecap(w.y)
                if c is None: continue
                zt2=min(oz(w.x,w.y),c-0.08)
                if zt2>w.z+0.01: w.z=zt2; v.co=Mi2@w; n+=1
        me.update(); print(TAG,'dip fix',P.name,'verts raised',n,flush=True)
    # (7) walk N end: slab x -191.98..-189.5 from y 183.5 to 191.0 (OSM walk starts ~190.8), draped on max(base, W63 patch) + 6 cm
    bv=[]
    for o in (T,P2):
        me=o.data; Mo=o.matrix_world; vv=[Mo@v.co for v in me.vertices]
        ps=[p.vertices[:] for p in me.polygons if any(-196<vv[i].x<-186 and 181<vv[i].y<194 for i in p.vertices)]
        bv.append(BVHTree.FromPolygons(vv,ps))
    def gz(x,y):
        z=-1e9
        for b in bv:
            h=b.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
            if h[0]: z=max(z,h[0].z)
        return z
    def gtop(y): return max(gz(xx,yy) for xx in (-191.9,-190.7,-189.6) for yy in (y-0.25,y,y+0.25))+0.06
    z_end=max(oz(-191.9,183.5),oz(-190.7,183.5),oz(-189.6,183.5))+0.06
    ys=list(np.arange(183.5,191.01,0.5)); tops=[]
    for i,y in enumerate(ys):
        g=gtop(y); w=min(1.0,(y-183.5)/1.5); tops.append(z_end*(1-w)+max(g,z_end if i==0 else g)*w if i>0 else z_end)
    print(TAG,'Nwalk tops',' '.join('%.2f'%z for z in tops),'ground',' '.join('%.2f'%(gtop(y)-0.06) for y in ys),flush=True)
    bm=bmesh.new(); xw,xe=-191.98,-189.5
    Tp=[(bm.verts.new((xw,y,z)),bm.verts.new((xe,y,z))) for y,z in zip(ys,tops)]; Bt=[(bm.verts.new((xw,y,z-0.35)),bm.verts.new((xe,y,z-0.35))) for y,z in zip(ys,tops)]
    n=len(ys)-1
    for i in range(n):
        bm.faces.new([Tp[i][0],Tp[i][1],Tp[i+1][1],Tp[i+1][0]]); bm.faces.new([Bt[i][0],Bt[i+1][0],Bt[i+1][1],Bt[i][1]])
        bm.faces.new([Tp[i][0],Tp[i+1][0],Bt[i+1][0],Bt[i][0]]); bm.faces.new([Tp[i][1],Bt[i][1],Bt[i+1][1],Tp[i+1][1]])
    bm.faces.new([Tp[0][0],Bt[0][0],Bt[0][1],Tp[0][1]]); bm.faces.new([Tp[n][0],Tp[n][1],Bt[n][1],Bt[n][0]])
    obj('WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED',bm,[M_WALK])
