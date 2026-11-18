"""2026-10-21 session dY (~1:35 PM ET). Joe's photo 05 (refs/joe/ccom_interior_east_1f_joe_20261020_05.jpg):
 - each white dining table stands on ONE chrome column (centred) with a 4-arm chrome star foot, not two posts;
 - the grey upholstered shell chairs have a back that widens upward to a ROUNDED top (dX had softly squared tops).
(a) For each dd_<SEG>_table_<n>: hide its two posts dd_<SEG>_tped_<n>, dd_<SEG>_tped_<n>.001 and their dX cross feet (prop dY_hidden),
    build one centred T-base (prop dY_new): chrome column Ø0.07 from the floor to the top's underside, a 0.80 m spreader rail under the
    top along the table's long axis (the "T"), and a 4-arm star foot (0.36 m arms, splayed 45° to the long axis) with round glides.
(b) For each dX dining-chair shell dd_<SEG>_ch_..._shell_dX: hide it and build a dY shell at the same matrix: same cushioned seat
    plus a back whose outline is a rounded-top shield (0.43 m wide at the seat, 0.50 m near the top, top corners r 0.14 m,
    crown 0.92 m, 0.07 m thick, reclined 0.10 m), bevel 22 mm. Same material.
Sizes photo-scaled from the 0.45 m seat (UNVERIFIED +/-0.05 m). Positions/headings unchanged from dd/dX.
REVERT=1 deletes dY_new and unhides dY_hidden. SAVE=1 saves. Idempotent (reverts first)."""
import bpy, bmesh, os, math, re
from mathutils import Vector, Matrix
def bbw(o):
    P=[o.matrix_world@Vector(c) for c in o.bound_box]
    return Vector([min(p[i] for p in P) for i in range(3)]), Vector([max(p[i] for p in P) for i in range(3)])
for o in [o for o in bpy.data.objects if 'dY_new' in o]:
    me=o.data; bpy.data.objects.remove(o)
    if me and me.users==0: bpy.data.meshes.remove(me)
for o in bpy.data.objects:
    if 'dY_hidden' in o:
        o.hide_render=False; o.hide_viewport=False; del o['dY_hidden']
bpy.context.view_layer.update()
if os.environ.get('REVERT')=='1':
    print('DY_REVERTED', flush=True)
else:
    def hide(o): o['dY_hidden']=1; o.hide_render=True; o.hide_viewport=True
    def mk(name, bm, mat, coll, M, bevel=None, seg=3):
        me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth=True
        me.materials.append(mat)
        o=bpy.data.objects.new(name, me); o.matrix_world=M; o['dY_new']=1; coll.objects.link(o)
        if bevel:
            m=o.modifiers.new('dY_bevel','BEVEL'); m.width=bevel; m.segments=seg; m.limit_method='ANGLE'
            m2=o.modifiers.new('dY_wn','WEIGHTED_NORMAL'); m2.keep_sharp=True
        return o
    def box(bm, x0,x1,y0,y1,z0,z1):
        vs=[bm.verts.new((x,y,z)) for z in (z0,z1) for (x,y) in ((x0,y0),(x1,y0),(x1,y1),(x0,y1))]
        for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]: bm.faces.new([vs[i] for i in q])
    def cyl(bm, top, bot, r0, r1, n=12):
        top=Vector(top); bot=Vector(bot); ax=(top-bot).normalized()
        u=ax.orthogonal().normalized(); w=ax.cross(u)
        a=[bm.verts.new(bot+(u*math.cos(2*math.pi*k/n)+w*math.sin(2*math.pi*k/n))*r1) for k in range(n)]
        b=[bm.verts.new(top+(u*math.cos(2*math.pi*k/n)+w*math.sin(2*math.pi*k/n))*r0) for k in range(n)]
        for k in range(n): bm.faces.new([a[k],a[(k+1)%n],b[(k+1)%n],b[k]])
        bm.faces.new(a[::-1]); bm.faces.new(b)
    # ---- (a) T-bases
    nt=0
    for t in [o for o in bpy.data.objects if re.match(r'dd_[A-Z0-9]+_table_\d+$', o.name)]:
        seg,n=re.match(r'dd_([A-Z0-9]+)_table_(\d+)$', t.name).groups()
        p0=bpy.data.objects.get(f'dd_{seg}_tped_{n}'); p1=bpy.data.objects.get(f'dd_{seg}_tped_{n}.001')
        if not (p0 and p1): continue
        a0,b0=bbw(p0); a1,b1=bbw(p1); c0=(a0+b0)/2; c1=(a1+b1)/2
        tmn,tmx=bbw(t); fl=min(a0.z,a1.z); under=tmn.z
        c=(c0+c1)/2; ax=Vector((c1.x-c0.x,c1.y-c0.y,0)).normalized()
        yaw=math.atan2(ax.y,ax.x)   # local +X = long axis
        M=Matrix.Translation((c.x,c.y,fl))@Matrix.Rotation(yaw,4,'Z')
        for o in (p0,p1): hide(o)
        for o in bpy.data.objects:
            if o.name in (f'dd_{seg}_tped_{n}_foot_dX', f'dd_{seg}_tped_{n}_001_foot_dX'): hide(o)
        h=under-fl; coll=p0.users_collection[0]; chrome=p0.data.materials[0]
        bm=bmesh.new()
        cyl(bm,(0,0,h-0.02),(0,0,0.05),0.035,0.035,n=16)               # column
        cyl(bm,(0,0,0.07),(0,0,0.02),0.06,0.07,n=16)                   # hub
        box(bm,-0.40,0.40,-0.025,0.025,h-0.045,h-0.005)                # T spreader under the top
        box(bm,-0.05,0.05,-0.20,0.20,h-0.04,h-0.005)                   # short cross cleat
        for k in range(4):
            a=math.pi/4+k*math.pi/2; e=(0.36*math.cos(a),0.36*math.sin(a),0.018)
            cyl(bm,(0.05*math.cos(a),0.05*math.sin(a),0.045),e,0.02,0.014,n=8)
            cyl(bm,(e[0],e[1],0.02),(e[0],e[1],0.0),0.022,0.022,n=10)   # glide
        mk(f'dd_{seg}_tbase_{n}_dY', bm, chrome, coll, M, bevel=0.006, seg=2)
        nt+=1
    # ---- (b) rounder chair backs
    def shield(bm, w0, w1, zb, zt, r, y0, th, lean, nr=6):
        # outline in local XZ (x width, z height), rounded top corners; extruded in -y (thickness), reclined in -y by lean*(z-zb)/(zt-zb)
        pts=[(-w0/2,zb),(w0/2,zb)]
        wr=w1/2
        for k in range(nr+1):  # right top corner
            a=0+ (math.pi/2)*k/nr; pts.append((wr-r+r*math.cos(a), zt-r+r*math.sin(a)))
        for k in range(nr+1):  # left top corner
            a=math.pi/2+(math.pi/2)*k/nr; pts.append((-wr+r+r*math.cos(a), zt-r+r*math.sin(a)))
        def V(x,z,dy):
            s=(z-zb)/(zt-zb); return bm.verts.new((x, y0+dy-lean*s, z))
        f=[V(x,z,0) for x,z in pts]; b=[V(x,z,-th) for x,z in pts]
        bm.faces.new(f); bm.faces.new(b[::-1])
        m=len(pts)
        for k in range(m): bm.faces.new([f[k],b[k],b[(k+1)%m],f[(k+1)%m]][::-1])
    nb=0
    for s in [o for o in bpy.data.objects if re.match(r'dd_[A-Z0-9]+_ch_.*_shell_dX$', o.name) and not o.hide_render and 'dY_hidden' not in o]:
        M=s.matrix_world.copy(); mat=s.data.materials[0]; coll=s.users_collection[0]
        hide(s)
        bm=bmesh.new()
        box(bm,-0.235,0.235,-0.22,0.24,0.40,0.47)                       # cushioned seat (as dX)
        shield(bm,0.43,0.50,0.44,0.92,0.14,-0.205,0.07,0.10)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        mk(s.name[:-len('shell_dX')]+'shell_dY', bm, mat, coll, M, bevel=0.022)
        nb+=1
    print('DY tbases', nt, 'chairs', nb, flush=True)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('DY_SAVED', flush=True)
