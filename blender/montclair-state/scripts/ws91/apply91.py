# ws91: straighten wobbly boundary edges (Joe 12:10 PM) of median/island/lot/walk/verge meshes. XY: RDP keypoints + projection,
# kinks softened, clamp; interior verts follow nearest boundary displacement with falloff. Z: raise-only (terrain +2 cm; loop smoothing <= ZCAP).
import bpy,math,os,sys
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws91'); from straight91 import loops_of,straighten_loop
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
OB=bpy.data.objects
# prefix: (eps, clamp, falloff R, zmode)  zmode: 'surf' raise-only z smoothing; 'none' xy only
CFG=[('WS89_CollegeAve_lot_median_CURB',0.08,0.15,0.30,'none'),('WS89_CollegeAve_lot_median_MULCH',0.08,0.15,0.6,'surf'),
 ('WS77_lot_median_island',0.10,0.25,0.6,'none'),
 ('WS71_Kasser_S_sidewalk',0.12,0.3,0.8,'surf'),('WS72_Kasser_SW_RHD',0.12,0.3,0.8,'surf'),('WS72b_Kasser_S_sidewalk',0.12,0.3,0.8,'surf'),
 ('WS73_curb_back_lawn_verge',0.12,0.3,0.8,'surf'),('WS83_sprague_lane_walk_edge',0.10,0.12,0.4,'none'),('WS83_lane_gutter',0.10,0.12,0.4,'none'),
 ('WS74_cogen_lot_asphalt',0.30,0.35,1.2,'surf'),('WS75_sprague_lot_asphalt',0.30,0.35,1.2,'surf'),('WS76_accessible_lot_asphalt',0.30,0.35,1.2,'surf'),('WS80_sprague_lot_fill',0.30,0.35,1.2,'surf')]
ONLY=os.environ.get('ONLY','')
ZCAP=float(os.environ.get('ZCAP','0.04'))
T=OB['Terrain_LiDAR_DTM_1m']; e=T.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=e.to_mesh()
TB=BVHTree.FromPolygons([e.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear()
def tz(x,y):
    h=TB.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else -1e9
CK=KDTree(sum(len(OB[n].data.vertices) for n in ('WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED')))
_k=0
for n in ('WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED'):
    for v in OB[n].data.vertices:
        w=OB[n].matrix_world@v.co; CK.insert(Vector((w.x,w.y,0)),_k); _k+=1
CK.balance()
KEEP=float(os.environ.get('KEEP','0.6'))
def gs_loop(a,s):
    n=len(a);out=[]
    for i in range(n):
        w=t=0
        for j in range(i-3*s,i+3*s+1):
            g=math.exp(-((i-j)/s)**2/2); w+=g; t+=g*a[j%n]
        out.append(t/w)
    return out
for pre,eps,clamp,R,zm in CFG:
    if ONLY and not pre.startswith(ONLY): continue
    if any(pre.startswith(k) for k in os.environ.get('SKIP','').split(',') if k): continue
    obs=[o for o in OB if o.type=='MESH' and o.name.startswith(pre) and not o.hide_render]
    for o in obs:
        mw=o.matrix_world; inv=mw.inverted(); me=o.data
        W=[mw@v.co for v in me.vertices]; F=[list(p.vertices) for p in me.polygons]
        new=[w.copy() for w in W]; isb=set(); disp={}
        nz0=[p.normal.z for p in me.polygons]
        for L in loops_of(F):
            P=[(W[i].x,W[i].y) for i in L]
            Q,k,md=straighten_loop(P,eps,clamp)
            zs=[W[i].z for i in L]
            if zm=='surf' and len(L)>12:
                zsm=gs_loop(zs,3)
            for j,i in enumerate(L):
                isb.add(i); dx,dy=Q[j][0]-W[i].x,Q[j][1]-W[i].y
                if not pre.startswith('WS89') and CK.find(Vector((W[i].x,W[i].y,0)))[2]<KEEP: dx=dy=0.0; Q[j]=(W[i].x,W[i].y)  # ws91: keep edges that meet the ws90 College Ave curb
                disp[i]=(dx,dy)
                z=W[i].z
                if zm=='surf':
                    if len(L)>12: z=min(max(z,zsm[j]),W[i].z+ZCAP)
                    t=tz(Q[j][0],Q[j][1])
                    if t>z-0.02: z=max(z,min(t+0.02,W[i].z+ZCAP))
                new[i]=Vector((Q[j][0],Q[j][1],z))
        if not isb: continue
        kd=KDTree(len(isb)); bl=list(isb)
        for n_,i in enumerate(bl): kd.insert(Vector((W[i].x,W[i].y,0)),n_)
        kd.balance()
        moved=0
        for i in range(len(W)):
            if i in isb: continue
            co,n_,d=kd.find(Vector((W[i].x,W[i].y,0)))
            if d>R: continue
            f=1.0 if d<0.05 else max(0.0,1-(d-0.05)/(R-0.05))
            dx,dy=disp[bl[n_]]
            if abs(dx)+abs(dy)<1e-4: continue
            new[i]=Vector((W[i].x+dx*f,W[i].y+dy*f,W[i].z)); moved+=1
        for v,p in zip(me.vertices,new): v.co=inv@p
        me.update()
        # fold check: revert faces whose (mostly horizontal) normal flipped
        bad=0
        for it in range(3):
            fl=[p for p,z0 in zip(me.polygons,nz0) if abs(z0)>0.5 and p.normal.z*z0<0.2*abs(z0)]
            if not fl: break
            for p in fl:
                for vi in p.vertices: me.vertices[vi].co=inv@W[vi]; bad+=1
            me.update()
        mx=max((math.hypot(*disp[i]) for i in isb),default=0)
        dz=max(((mw@me.vertices[i].co).z-W[i].z for i in isb),default=0)
        print('A91',o.name[:55],'bnd',len(isb),'int',moved,'maxxy %.2f'%mx,'maxdz %.3f'%dz,'revert_verts',bad)
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('A91 SAVED')
