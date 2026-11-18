# ws188 (Nov 16 ~1:40 PM ET) — Sprague Field: hash marks, sideline yard ticks, end-zone lettering panels. Chain AFTER ws187/fix187b.py.
# Evidence: prep/ws181_lot36/ortho181.jpg (NJOGIS Natural2020, 0.1 m/px). ws188 LOG:
#  - hash marks: column of 1-yd dots at x ~-341.5, y -200..-202.5 = 18.6 m (+-0.3) perpendicular inside the E sideline
#    -> NCAA hash 60 ft = 18.29 m (Montclair State = NCAA D-III). Far hash (30.48 m) only where turf exists. 24 in x 4 in.
#  - sideline yard ticks (24 in, 4 in inside the sideline, NCAA rule) = UNVERIFIED (not resolvable in the ortho).
#  - end zone S of goal line C: two pale rectangular panels (u -293.5..-285.7 [cut by ortho/scene W edge], -285.2..-274.0;
#    v -294.6..-291.7 in yard-line coords d=(0.971,-0.238), n=(0.238,0.971)) with 11 dark-red letter blobs (letters unreadable
#    at 0.1 m -> clean upright letter blocks, UNVERIFIED wording/shape). Lacrosse/multi-sport lines (x -334, -330.5) NOT built.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TF=next((o for o in bpy.data.objects if o.name.startswith('WS167_ground_W_of_Lot3_bank_Sprague_')),None)
TM=next((m for m in bpy.data.materials if m.name.startswith('WS186_Sprague_artificial_turf')),None)
PM=next((m for m in bpy.data.materials if m.name.startswith('WS187_Sprague_field_paint_white')),None)
if not (TF and TM and PM): print('FIX188 SKIPPED',bool(TF),bool(TM),bool(PM),flush=True)
else:
    me=TF.data; M=TF.matrix_world; ti=[i for i,m in enumerate(me.materials) if m==TM]
    vs=[M@v.co for v in me.vertices]; T=BVHTree.FromPolygons(vs,[list(p.vertices) for p in me.polygons if p.material_index in ti])
    def hz(x,y):
        h=T.ray_cast(Vector((x,y,140.0)),Vector((0,0,-1)),60.0); return None if h[0] is None else h[0].z
    k=-0.245; d=np.array([1.0,k]); d/=np.linalg.norm(d); n=np.array([-d[1],d[0]])
    def side_pt(off):
        # intersection of yard line (offset off) with the E sideline x=-322.2+0.237(y+201)
        y=-210.0
        for _ in range(50):
            x=-322.2+0.237*(y+201.0); y=k*(x+338.0)-203.95-off
        return np.array([-322.2+0.237*(y+201.0),y])
    def mk(name,mat,quads):
        V=[];F=[]
        for q in quads:
            b=len(V)
            for (x,y,dz) in q: V.append((x,y,dz))
            F.append((b,b+1,b+2,b+3))
        me2=bpy.data.meshes.new(name); me2.from_pydata(V,[],F); me2.update(); me2.materials.append(mat)
        ob=bpy.data.objects.new(name,me2)
        for c in TF.users_collection: c.objects.link(ob)
        return ob
    def rect(c,a,ha,hb,dz,step=0.25):
        # rectangle centred c, axis a (unit), half-length ha along a, hb across; subdivided along a and b, draped; None if any corner off-turf
        b=np.array([-a[1],a[0]]); na=max(1,int(np.ceil(2*ha/step))); nb=max(1,int(np.ceil(2*hb/step))); out=[]
        for i in range(na):
            for j in range(nb):
                cs=[]
                for (ii,jj) in ((i,j),(i+1,j),(i+1,j+1),(i,j+1)):
                    p=c+a*(-ha+2*ha*ii/na)+b*(-hb+2*hb*jj/nb); z=hz(*p)
                    if z is None: cs=None; break
                    cs.append((p[0],p[1],z+dz))
                if cs: out.append(cs)
        return out
    offs=[('C',9.35),('B',4.7),('A',0.0),('Z',-4.6)]+[('N%d'%i,-4.6-4.65*i) for i in range(1,12)]
    ypos=[]
    for (n1,o1),(n2,o2) in zip(offs[:-1],offs[1:]):
        for j in range(1,5): ypos.append(o1+(o2-o1)*j/5.0)
    hq=[];tq=[];nh=0;nt=0
    for o in ypos:
        S=side_pt(o)
        for D in (18.29,30.48):
            q=rect(S-d*D,d,0.305,0.05,0.006,0.31)
            if len(q)==2: hq+=q; nh+=1
        q=rect(S-d*(0.10+0.305),d,0.305,0.05,0.006,0.31)
        if len(q)==2: tq+=q; nt+=1
    mk('WS188_Sprague_hash_marks_NCAA60ft_ortho2020',PM,hq)
    mk('WS188_Sprague_sideline_yard_ticks_UNVERIFIED',PM,tq)
    # end-zone panels (u,v) -> xy
    def xy(u,v): return d*u+n*v
    pf=bpy.data.materials.new('WS188_endzone_panel_white_UNVERIFIED'); pf.use_nodes=True
    bb=pf.node_tree.nodes['Principled BSDF']; bb.inputs['Base Color'].default_value=(0.62,0.62,0.58,1); bb.inputs['Roughness'].default_value=0.85
    rm=bpy.data.materials.new('WS188_endzone_letters_red_UNVERIFIED'); rm.use_nodes=True
    bb=rm.node_tree.nodes['Principled BSDF']; bb.inputs['Base Color'].default_value=(0.42,0.05,0.045,1); bb.inputs['Roughness'].default_value=0.85
    V0,V1=-294.6,-291.7; pq=[];bq=[];lq=[]
    for (u0,u1) in ((-296.0,-285.69),(-285.23,-274.02)):
        c=xy((u0+u1)/2,(V0+V1)/2); pq+=rect(c,d,(u1-u0)/2,(V1-V0)/2,0.012)
        for (a0,a1,b0,b1) in ((u0,u1,V0,V0+0.15),(u0,u1,V1-0.15,V1),(u0,u0+0.15,V0,V1),(u1-0.15,u1,V0,V1)):
            bq+=rect(xy((a0+a1)/2,(b0+b1)/2),d,(a1-a0)/2,(b1-b0)/2,0.013,0.25)
    L=[(-293.46,-292.63),(-292.37,-290.36),(-288.73,-287.81),(-287.23,-286.33),(-284.11,-283.33),(-282.55,-281.65),(-281.45,-280.85),(-279.29,-278.25),(-278.07,-277.23),(-276.93,-275.99),(-275.49,-274.57)]
    for (a0,a1) in L:
        lq+=rect(xy((a0+a1)/2,-293.2),d,(a1-a0)/2,0.8,0.014,0.2)
    mk('WS188_Sprague_endzone_panels_ortho2020_UNVERIFIED',pf,pq)
    mk('WS188_Sprague_endzone_panel_borders_ortho2020',PM,bq)
    mk('WS188_Sprague_endzone_letter_blocks_UNVERIFIED_wording',rm,lq)
    print('FIX188 hash',nh,'ticks',nt,'panel quads',len(pq),'border quads',len(bq),'letter quads',len(lq),flush=True)
