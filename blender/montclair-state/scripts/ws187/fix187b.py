# ws187 (Nov 16 ~12:55 PM ET) — Sprague Field painted lines (chain AFTER ws186/fix186b.py: needs the turf material on the field faces).
# Evidence: prep/ws181_lot36/ortho181.jpg (NJOGIS Natural2020, 0.1 m/px, x -355..-295, y -260..-200), brightness-peak picks (ws187 LOG):
#   yard line A (-340,-203.7) (-337,-204.4) (-334,-205.1) (-331,-205.9) (-329.5,-206.2) -> slope -0.245 (-13.8 deg), y(-338) = -203.95
#   line B y(-338) -208.65 (4.7 m S = 5 yd), line C y(-338) -213.3 (S-most line; red end-zone lettering S of it, x -352..-335),
#   line Z 4.6 m N of A (seen at x -334 y -200.4, at the ortho's N edge); lines N of Z extrapolated at 5 yd (4.65 m) = UNVERIFIED (no ortho).
#   E sideline row picks (-322.2,-201) (-323.2,-205) (-324.1,-209) (-325.1,-213) (-325.7,-215.5) (-326.0,-216.5), fades by -217.5:
#   x = -322.2 + 0.237*(y+201) (perpendicular to the yard lines); yard lines end at it (A fades at x -324, C at -325.5 in the ortho).
# Built: 0.10 m (4 in, NCAA/HS) white paint strips draped +6 mm on the turf faces only. Positions +-0.3 m, widths/ends UNVERIFIED.
# NOT built: end-zone lettering (letters unreadable at 0.3 m), the white goal-frame marking at (-353..-345,-211..-207), hash marks / numbers.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TF=next((o for o in bpy.data.objects if o.name.startswith('WS167_ground_W_of_Lot3_bank_Sprague_')),None)
TM=next((m for m in bpy.data.materials if m.name.startswith('WS186_Sprague_artificial_turf')),None)
if not (TF and TM): print('FIX187B SKIPPED turf object/material missing',bool(TF),bool(TM),flush=True)
else:
    me=TF.data; M=TF.matrix_world; ti=[i for i,m in enumerate(me.materials) if m==TM]
    vs=[M@v.co for v in me.vertices]; fl=[(list(p.vertices),p.material_index) for p in me.polygons]
    tfaces=[f for f,mi in fl if mi in ti]; T=BVHTree.FromPolygons(vs,tfaces)
    def hz(x,y):
        h=T.ray_cast(Vector((x,y,140.0)),Vector((0,0,-1)),60.0); return None if h[0] is None else h[0].z
    S0=np.array([-322.2,-201.0]); S1=np.array([-322.2+0.237*(-16.0),-217.0]); sd=(S1-S0)/np.linalg.norm(S1-S0)
    k=-0.245; d=np.array([1.0,k]); d/=np.linalg.norm(d); nrm=np.array([-d[1],d[0]])
    def ylineA(x,off): return k*(x+338.0)-203.95-off
    def side_x(y): return S0[0]+(y-S0[1])*(sd[0]/sd[1])
    lines=[]
    for nm,off in [('A',0.0),('B',4.7),('C_S_end',9.35),('Z',-4.6)]+[('N%d_extrap_UNVERIFIED'%i,-4.6-4.65*i) for i in range(1,12)]:
        # intersection with the sideline: solve x where line y meets sideline
        xs=-356.0; xe=None
        for x in np.arange(-356,-300,0.02):
            if x>=side_x(ylineA(x,off)): xe=x; break
        if xe is None: continue
        lines.append((nm,[(x,ylineA(x,off)) for x in np.arange(xs,xe+1e-6,0.25)]+[(xe,ylineA(xe,off))]))
    ycs=[y for y in np.arange(-150.0,-217.0-1e-6,-0.25)]
    lines.append(('E_sideline',[(side_x(y),y) for y in ycs]))
    V=[];F=[];rep={}
    for nm,pts in lines:
        segs=[];cur=[]
        for (x,y) in pts:
            z=hz(x,y)
            if z is None:
                if len(cur)>1: segs.append(cur)
                cur=[]; continue
            cur.append((x,y,z))
        if len(cur)>1: segs.append(cur)
        L=0.0
        for sg in segs:
            P=np.array([p[:2] for p in sg]); base=len(V)
            for i,(x,y,z) in enumerate(sg):
                t=P[min(i+1,len(P)-1)]-P[max(i-1,0)]; t/=np.linalg.norm(t); n=np.array([-t[1],t[0]])*0.05
                for s in (-1,1):
                    q=(x+s*n[0],y+s*n[1]); zz=hz(*q); V.append((q[0],q[1],(zz if zz is not None else z)+0.006))
            for i in range(len(sg)-1): a=base+2*i; F.append((a,a+2,a+3,a+1))
            L+=float(np.sum(np.linalg.norm(np.diff(P,axis=0),axis=1)))
        rep[nm]=round(L,1)
    mm=bpy.data.materials.new('WS187_Sprague_field_paint_white_UNVERIFIED'); mm.use_nodes=True
    b=mm.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.78,0.80,0.76,1); b.inputs['Roughness'].default_value=0.85
    mesh=bpy.data.meshes.new('WS187_Sprague_field_lines'); mesh.from_pydata(V,[],F); mesh.update(); mesh.materials.append(mm)
    ob=bpy.data.objects.new('WS187_Sprague_yard_goal_sidelines_ortho2020_UNVERIFIED',mesh)
    for c in TF.users_collection: c.objects.link(ob)
    print('FIX187B field lines len m',rep,'verts',len(V),'faces',len(F),flush=True)
