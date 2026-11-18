# nw (Oct 30 2026 ~10:40 PM ET, MAIN): (1) LiDAR terrain/grass that showed through at 1F level INSIDE the CCOM roof footprint
# (incl. the top-left strip of the plan aerial, x -11.6..-2.1 / y 17..20.3 and the x -11.6..-11 sliver E of the tower) -> auto
# blocked-out fill cells (0.5 m grid, run-length merged; only where a downward ray at 142.9 hits Terrain AND the CCOM roof covers
# the point +-1.5 m in x and y, so nothing leaks outside the walls under the eaves); (2) 10 cm rubber cove skirting at the feet of
# every CCOM inward room shell; NW cameras. ALL UNVERIFIED (no photos of these zones).
import bpy, os, json, mathutils, bmesh
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NW_CCOM_1F_fill_cells_skirting_20261030nw'; sc=bpy.context.scene
FM='NV_blocked_out_floor_joints_UNVERIFIED'; SKM='NW_rubber_cove_base_UNVERIFIED'
def revert():
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                if d.name in bpy.data.cameras: bpy.data.cameras.remove(d)
                elif d.name in bpy.data.meshes: bpy.data.meshes.remove(d)
        bpy.data.collections.remove(c)
    m=bpy.data.materials.get(SKM)
    if m and m.users==0: bpy.data.materials.remove(m)
    for k in ('nw_state','nw_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='nw'; o['msu_verified']='UNVERIFIED'
fm=bpy.data.materials[FM]
# ---- (1) probe with BVH trees (scene.ray_cast rebuilt per call = far too slow): world-space tris of every render-visible mesh
# in the region (roofs/ceilings HP excluded; Terrain tagged), plus a roof BVH of the CCOM roof objects.
import numpy as np
from mathutils.bvhtree import BVHTree
HP=('CCOM_Win_Wing_A_ceil','CCOM_east_roof_plate_z2','CCOM_east_flat_roof_clean','School of Communication and Media roof','CCOM_int_lounge_ceil','School of Communication and Media hip','el coping','ek coping','el roof exhaust')
G=0.5; X0,X1,Y0,Y1=-25.0,35.0,-27.0,42.0
def tris(o,zlo,zhi):
    me=o.data; me.calc_loop_triangles(); n=len(me.loop_triangles)
    if n==0: return None
    co=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
    M=np.array(o.matrix_world); co=co@M[:3,:3].T+M[:3,3]
    t=np.empty(n*3,dtype=np.int64); me.loop_triangles.foreach_get('vertices',t); t=t.reshape(-1,3)
    P=co[t]; c=P.mean(axis=1)
    k=(c[:,0]>X0-2)&(c[:,0]<X1+2)&(c[:,1]>Y0-2)&(c[:,1]<Y1+2)&(P[:,:,2].max(1)>zlo)&(P[:,:,2].min(1)<zhi)
    return P[k]
V=[];F=[];TAG=[];RV=[];RF=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    lo=[min(c[i] for c in cs) for i in range(3)]; hi=[max(c[i] for c in cs) for i in range(3)]
    if hi[0]<X0-2 or lo[0]>X1+2 or hi[1]<Y0-2 or lo[1]>Y1+2: continue
    isroof=o.name.startswith(('School of Communication and Media roof','School of Communication and Media hip')) or (o.name.startswith('CCOM') and 'roof' in o.name.lower())
    if isroof:
        P=tris(o,140,170)
        if P is not None and len(P):
            b0=len(RV); RV.extend(map(tuple,P.reshape(-1,3))); RF.extend([(b0+3*q,b0+3*q+1,b0+3*q+2) for q in range(len(P))])
    if o.name.startswith(HP) or hi[2]<136.5 or lo[2]>142.9: continue
    P=tris(o,136.5,142.9)
    if P is None or not len(P): continue
    b0=len(V); V.extend(map(tuple,P.reshape(-1,3))); F.extend([(b0+3*q,b0+3*q+1,b0+3*q+2) for q in range(len(P))]); TAG.extend([o.name.startswith('Terrain')]*len(P))
bv=BVHTree.FromPolygons(V,F,all_triangles=True); rb=BVHTree.FromPolygons(RV,RF,all_triangles=True)
print('NW bvh tris',len(F),'roof tris',len(RF))
nx=int((X1-X0)/G); ny=int((Y1-Y0)/G); dn=mathutils.Vector((0,0,-1))
roof=[[rb.ray_cast(mathutils.Vector((X0+(i+.5)*G,Y0+(j+.5)*G,190)),dn)[0] is not None for i in range(nx)] for j in range(ny)]
cells=set(); R=3  # 3 cells = 1.5 m
for j in range(R,ny-R):
    for i in range(R,nx-R):
        if not all(roof[j+dj][i+di] for di,dj in ((0,0),(R,0),(-R,0),(0,R),(0,-R),(R,R),(-R,-R),(R,-R),(-R,R))): continue
        loc,nrm,idx,d=bv.ray_cast(mathutils.Vector((X0+(i+.5)*G,Y0+(j+.5)*G,142.9)),dn)
        if loc is not None and TAG[idx] and loc.z<137.73: cells.add((i,j))
print('NW fill cells raw',len(cells))
ZT=float(os.environ.get('ZT','137.74'))
bm=bmesh.new(); runs=0
for j in range(ny):
    i=0
    while i<nx:
        if (i,j) in cells:
            k=i
            while (k+1,j) in cells: k+=1
            x0=X0+i*G-0.02; x1=X0+(k+1)*G+0.02; y0=Y0+j*G-0.02; y1=Y0+(j+1)*G+0.02
            r=bmesh.ops.create_cube(bm,size=1.0)
            for v in r['verts']: v.co=mathutils.Vector(((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),(136.9+ZT)/2+v.co.z*(ZT-136.9)))
            runs+=1; i=k+1
        else: i+=1
me=bpy.data.meshes.new('NW_fill_cells'); bm.to_mesh(me); bm.free(); me.materials.append(fm)
o=bpy.data.objects.new('NW 1F fill cells where terrain showed inside the CCOM footprint (UNVERIFIED)',me); col.objects.link(o); tag(o,'floor')
state['fill_cells']=len(cells); state['fill_runs']=runs
print('NW fill runs',runs, 'cells',sorted(cells)[:3])
# ---- (2) skirting at the feet of the CCOM inward room shells
sk=bpy.data.materials.new(SKM); sk.use_nodes=True; b=sk.node_tree.nodes['Principled BSDF']
b.inputs['Base Color'].default_value=(0.085,0.08,0.075,1); b.inputs['Roughness'].default_value=0.55
H=float(os.environ.get('SKH','0.10')); T=0.012
bm=bmesh.new(); nsh=0
def addbox(x0,x1,y0,y1,z0,z1):
    r=bmesh.ops.create_cube(bm,size=1.0)
    for v in r['verts']: v.co=mathutils.Vector(((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),(z0+z1)/2+v.co.z*(z1-z0)))
for s in list(bpy.data.objects):
    if s.type!='MESH' or s.hide_render or 'room shell' not in s.name or len(s.data.vertices)!=8: continue
    ws=[s.matrix_world@v.co for v in s.data.vertices]
    lo=[min(v[i] for v in ws) for i in range(3)]; hi=[max(v[i] for v in ws) for i in range(3)]
    if not (-25<lo[0] and hi[0]<35 and -27<lo[1] and hi[1]<42 and 135<lo[2]<146): continue
    if hi[0]-lo[0]<1.0 or hi[1]-lo[1]<1.0: continue
    z0=lo[2]+0.003; z1=lo[2]+H; e=0.004
    addbox(lo[0]+e,hi[0]-e,lo[1]+e,lo[1]+e+T,z0,z1); addbox(lo[0]+e,hi[0]-e,hi[1]-e-T,hi[1]-e,z0,z1)
    addbox(lo[0]+e,lo[0]+e+T,lo[1]+e+T,hi[1]-e-T,z0,z1); addbox(hi[0]-e-T,hi[0]-e,lo[1]+e+T,hi[1]-e-T,z0,z1)
    nsh+=1
me=bpy.data.meshes.new('NW_cove_base'); bm.to_mesh(me); bm.free(); me.materials.append(sk)
o=bpy.data.objects.new('NW rubber cove skirting at room shell feet (UNVERIFIED)',me); col.objects.link(o); tag(o,'trim'); o.visible_shadow=False
state['skirt_shells']=nsh; print('NW skirting shells',nsh)
# ---- cameras
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
def camcopy(nm,src):
    s=bpy.data.objects[src]; c=s.data.copy(); c.name=nm; o=bpy.data.objects.new(nm,c); o.matrix_world=s.matrix_world.copy(); col.objects.link(o); tag(o,'camera')
f=lambda k,d: tuple(float(x) for x in os.environ.get(k,d).split(','))
cam('NW_CAM_aerial_cutaway_plan_top_left_fill_N_of_atrium',f('ALOC','-2,10,176'),f('ATGT','-3,17,138'),float(os.environ.get('ALENS','28')))
camcopy('NW_CAM_eye_atrium_looking_west_to_doors','NU_CAM_eye_atrium_looking_west_to_doors')
camcopy('NW_CAM_eye_1F_open_floor_cafe_looking_east','NU_CAM_eye_1F_open_floor_cafe_looking_east')
cam('NW_CAM_closeup_cutaway_top_left_fill_N_of_atrium',f('CLLOC','-2.5,26.5,146'),f('CLTGT','-7,19.4,137.7'),float(os.environ.get('CLLENS','28')))
sc['nw_state']=json.dumps(state)
sc['nw_note']='nw: auto 1F fill cells where terrain showed inside the CCOM roof footprint (top-left strip etc.); rubber cove skirting at room-shell feet; NW cameras; UNVERIFIED'
print('NW objects',len(col.objects),'total',len(bpy.data.objects),state)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
