"""2026-10-21 session ea (~3:30 PM ET): the dZ long-table build applied to the two groups dZ skipped (SOUTH0 g6, SOUTH1 g0),
now that ccom_interior_clash_cutters_20261021ea.py removed the intruders. Clear-zone/post-check use EVALUATED meshes (booleans applied).
Props ea_tbl_new / ea_tbl_hidden. Original dZ docstring follows.
2026-10-21 session dZ (~2:30 PM ET). Joe's photo 05 (refs/joe/ccom_interior_east_1f_joe_20261020_05.jpg):
the white dining tables in CCOM's 1st-floor corridor are LONG rectangular tables (about 2.1 x 0.85 m, photo-scaled from the
0.45 m chair seat / 0.72 m table, UNVERIFIED +/-0.1 m) with three chairs along each long side (5-6 seats each in the photo),
each on ONE chrome column with a T spreader and a star foot (dY), on a large charcoal rug.
For each of the 8 dd groups (dd_<SEG>_table_<n> + dd_<SEG>_tbase_<n>_dY):
 - pick a shift dx along the corridor (local +X = table long axis = corridor axis) closest to 0 for which a clear zone
   (x dx+/-1.65, y -1.17..1.12, z 0.015..1.0 m above the floor) touches no other visible mesh (BVH overlap + vertex-inside test),
   the table ends stay >= 0.6 m from the segment ends and the rug stays on the terrazzo;
 - hide (prop dZ_hidden) the old top, dY T-base, 4 chairs (dY shells + dX legs), rug and dX floor boxes;
 - build (prop dZ_new): top 2.10 x 0.85 m (same height/thickness/material), the dY T-base copied with a 1.70 m spreader and a
   star foot stretched x1.5 along the long axis, 6 chairs (3 per side at -0.68/0/+0.68 m, pulled out 0.075 m for the wider top;
   linked copies of the dY shells/dX legs, alternating the two shell colours), rug 3.2 x 2.3 m, floor boxes at the rug ends.
REVERT=1 deletes dZ_new and unhides dZ_hidden. SAVE=1 saves. Idempotent (reverts first). Report -> data/dZ/long_tables_dZ.txt"""
import bpy, bmesh, os, math, re
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
for o in [o for o in bpy.data.objects if 'ea_tbl_new' in o]:
    me=o.data; bpy.data.objects.remove(o)
    if me and me.users==0: bpy.data.meshes.remove(me)
for o in bpy.data.objects:
    if 'ea_tbl_hidden' in o:
        o.hide_render=False; o.hide_viewport=False; del o['ea_tbl_hidden']
bpy.context.view_layer.update()
REP=[]
def rep(*a):
    s=' '.join(str(x) for x in a); REP.append(s); print('EAT', s, flush=True)
if os.environ.get('REVERT')=='1':
    rep('REVERTED')
else:
    TL, TW, CX, PULL = 1.05, 0.425, (-0.68, 0.0, 0.68), 0.075
    RL, RW = 1.60, 1.15
    ZONE = (1.65, -1.17, 1.12, 0.015, 1.0)
    STRUCT=('floor_terrazzo','ceiling_tile','led_strip','slot_diffuser')
    def hide(o): o['ea_tbl_hidden']=1; o.hide_render=True; o.hide_viewport=True
    def tag(o):
        for k in ('dX_new','dX2_new','dY_new','dX_hidden','dY_hidden','dZ_new','dZ_hidden'):
            if k in o: del o[k]
        o['ea_tbl_new']=1; return o
    def boxmesh(name, x0,x1,y0,y1,z0,z1, mat):
        bm=bmesh.new()
        vs=[bm.verts.new((x,y,z)) for z in (z0,z1) for (x,y) in ((x0,y0),(x1,y0),(x1,y1),(x0,y1))]
        for q in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]: bm.faces.new([vs[i] for i in q])
        me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat); return me
    def wbb(o):
        P=[o.matrix_world@Vector(c) for c in o.bound_box]
        return Vector([min(p[i] for p in P) for i in range(3)]), Vector([max(p[i] for p in P) for i in range(3)])
    bvh_cache={}
    def obvh(o):
        if o.name not in bvh_cache:
            e=o.evaluated_get(bpy.context.evaluated_depsgraph_get()); mw=e.matrix_world; me=e.data
            vs=[mw@v.co for v in me.vertices]; fs=[tuple(p.vertices) for p in me.polygons]
            bvh_cache[o.name]=(BVHTree.FromPolygons(vs,fs) if fs else None, vs)
        return bvh_cache[o.name]
    def zone_hits(M, dx, grp, z=ZONE):
        hx,y0,y1,z0,z1=z
        loc=[Vector((dx+sx*hx, y, zz)) for zz in (z0,z1) for (sx,y) in ((-1,y0),(1,y0),(1,y1),(-1,y1))]
        W=[M@p for p in loc]
        mn=Vector([min(p[i] for p in W) for i in range(3)]); mx=Vector([max(p[i] for p in W) for i in range(3)])
        bt=BVHTree.FromPolygons(W,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        Minv=M.inverted(); hits=[]
        for o in bpy.data.objects:
            if o.type!='MESH' or o.hide_render or o.name in grp or o.name.endswith(STRUCT) or len(o.data.vertices)==0: continue
            a,b=wbb(o)
            if any(b[i]<mn[i] or a[i]>mx[i] for i in range(3)): continue
            t,vs=obvh(o)
            hit=False
            if t and bt.overlap(t): hit=True
            else:
                for v in vs:
                    l=Minv@v
                    if dx-hx<l.x<dx+hx and y0<l.y<y1 and z0<l.z<z1: hit=True; break
            if hit: hits.append(o.name)
        return hits
    tb=[o for o in bpy.data.objects if o.name in ('dd_SOUTH0_tbase_6_dY','dd_SOUTH1_tbase_0_dY') and not o.hide_render]
    rep('groups', len(tb))
    for b in sorted(tb, key=lambda o:o.name):
        seg,n=re.match(r'dd_([A-Z0-9]+)_tbase_(\d+)_dY$', b.name).groups()
        M=b.matrix_world.copy(); Minv=M.inverted()
        gre=re.compile(rf'dd_{seg}_(table_{n}$|tbase_{n}_|ch_{n}_|rug_{n}$|floorbox_{n}_|tped_{n})')
        grp={o.name for o in bpy.data.objects if gre.match(o.name)}
        t=bpy.data.objects[f'dd_{seg}_table_{n}']; rug=bpy.data.objects[f'dd_{seg}_rug_{n}']
        fl=bpy.data.objects[f'dd_{seg}_floor_terrazzo']
        fx=[(Minv@(fl.matrix_world@v.co)).x for v in fl.data.vertices]; fx0,fx1=min(fx),max(fx)
        tz=[(Minv@(t.matrix_world@v.co)).z for v in t.data.vertices]; rz=[(Minv@(rug.matrix_world@v.co)).z for v in rug.data.vertices]
        cands=sorted([k*0.05 for k in range(-140,141)], key=lambda d:(abs(d), d))
        dx=None; first_hits=None
        for d in cands:
            if d-TL < fx0+0.6 or d+TL > fx1-0.6 or d-RL < fx0+0.02 or d+RL > fx1-0.02: continue
            h=zone_hits(M,d,grp)
            if first_hits is None: first_hits=(d,h)
            if os.environ.get('DBG')=='1' and abs(d*20-round(d*20))<1e-6 and round(d*20)%5==0: rep('  dbg',seg,n,round(d,2),h)
            if not h: dx=d; break
        if dx is None:
            rep(seg,n,'NO CLEAR SPOT; skipped; hits at', first_hits); continue
        rep(seg,n,'dx',round(dx,2),'floor x',round(fx0,2),round(fx1,2), 'hits at first legal', first_hits)
        coll=t.users_collection[0]; S=M@Matrix.Translation((dx,0,0))
        # hide old
        olds=[t,b,rug]+[o for o in bpy.data.objects if o.name.startswith(f'dd_{seg}_ch_{n}_') and not o.hide_render]+\
             [o for o in bpy.data.objects if o.name.startswith(f'dd_{seg}_floorbox_{n}_') and not o.hide_render]
        chairs_vis=[o for o in olds if '_ch_' in o.name]
        fbs=[o for o in olds if '_floorbox_' in o.name]
        for o in olds: hide(o)
        # top
        o=bpy.data.objects.new(f'dd_{seg}_table_{n}_ea', boxmesh(f'dd_{seg}_table_{n}_ea',-TL,TL,-TW,TW,min(tz),max(tz),t.data.materials[0]))
        o.matrix_world=S; coll.objects.link(o); tag(o)
        m=o.modifiers.new('ea_bevel','BEVEL'); m.width=0.006; m.segments=2; m.limit_method='ANGLE'
        # T-base
        h=max((Vector(v.co).z for v in b.data.vertices))
        me=b.data.copy(); me.name=f'dd_{seg}_tbase_{n}_ea'
        for v in me.vertices:
            x,y,z=v.co
            if z>h-0.05 and abs(x)>0.3: v.co.x=math.copysign(0.85,x)-(0.40-abs(x))*math.copysign(1,x)
            elif z<0.075 and math.hypot(x,y)>0.06: v.co.x=x*1.5
        o=b.copy(); o.data=me; o.name=f'dd_{seg}_tbase_{n}_ea'; o.matrix_world=S; o.hide_render=False; o.hide_viewport=False
        coll.objects.link(o); tag(o)
        # chairs
        nch=0
        for side in ('f','b'):
            tm={}
            for o0 in chairs_vis:
                mm=re.match(rf'dd_{seg}_ch_{n}_(-?[0-9.]+)_{side}_(shell_dY|legs_dX)$', o0.name)
                if mm: tm.setdefault(mm.group(1),{})[mm.group(2)]=o0
            keys=sorted(tm, key=float)
            if not keys: rep(seg,n,'no chair templates',side); continue
            for k,xk in enumerate(CX):
                key=keys[k%len(keys)]
                for part,o0 in tm[key].items():
                    L=Minv@o0.matrix_world
                    tr=L.translation.copy(); sgn=1 if tr.y>0 else -1
                    L.translation=Vector((tr.x-float(key)+xk+dx, tr.y+sgn*PULL, tr.z))
                    o=o0.copy(); o.name=f'dd_{seg}_ch_{n}_{xk:+.2f}_{side}_{part}_ea'; o.matrix_world=M@L
                    o.hide_render=False; o.hide_viewport=False; coll.objects.link(o); tag(o)
                nch+=1
        # rug
        o=bpy.data.objects.new(f'dd_{seg}_rug_{n}_ea', boxmesh(f'dd_{seg}_rug_{n}_ea',-RL,RL,-RW,RW,min(rz),max(rz),rug.data.materials[0]))
        o.matrix_world=S; coll.objects.link(o); tag(o)
        # floor boxes
        for i,o0 in enumerate(sorted(fbs,key=lambda o:o.name)[:2]):
            L=Minv@o0.matrix_world; tr=L.translation.copy(); sx=-1 if (Minv@o0.matrix_world.translation).x<0 else 1
            # floorbox mesh is centred on its own geometry; shift by the geometry centre
            c=sum((Minv@(o0.matrix_world@v.co) for v in o0.data.vertices), Vector())/len(o0.data.vertices)
            L.translation=tr+Vector((dx+sx*1.35-c.x, -c.y, 0))
            o=o0.copy(); o.name=f'dd_{seg}_floorbox_{n}_{sx}_ea'; o.matrix_world=M@L; o.hide_render=False; o.hide_viewport=False
            coll.objects.link(o); tag(o)
        rep(seg,n,'built: chairs',nch,'floorboxes',len(fbs))
    bpy.context.view_layer.update()
    # post-check: each new non-rug object vs every other visible mesh outside its group (BVH overlap)
    bvh_cache.clear()
    news=[o for o in bpy.data.objects if 'ea_tbl_new' in o]
    for o in news:
        if '_rug_' in o.name or '_floorbox_' in o.name: continue
        seg,n=re.match(r'dd_([A-Z0-9]+)_[a-z]+_(\d+)', o.name).groups()
        t,_=obvh(o); a,b2=wbb(o)
        for q in bpy.data.objects:
            if q is o or q.type!='MESH' or q.hide_render or q.name.endswith(STRUCT) or len(q.data.vertices)==0: continue
            if q.name.startswith(f'dd_{seg}_') and re.search(rf'_(table|tbase|ch|rug|floorbox)_{n}_', q.name+'_'): continue
            qa,qb=wbb(q)
            if any(qb[i]<a[i] or qa[i]>b2[i] for i in range(3)): continue
            tq,_=obvh(q)
            if tq and t and t.overlap(tq): rep('OVERLAP', o.name, q.name)
    rep('new objects', len(news))
os.makedirs(bpy.path.abspath('//data/ea'), exist_ok=True)
open(bpy.path.abspath('//data/ea/long_tables_ea.txt'),'a').write('\n'.join(REP)+'\n')
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('EAT_SAVED', flush=True)
