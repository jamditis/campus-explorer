# ws78a: lot pocket regrade. 1) sample terrain BEFORE; 2) terrain78 (GN lower-only to DTM); 3) lots/paint/island lowered by the terrain delta, clamped >= WS68 ground +4 cm; 4) trees in pocket re-seated if floating.
import bpy,bmesh,numpy as np,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
def tbvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); dg.update()
    m=o.evaluated_get(dg).to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); o.evaluated_get(dg).to_mesh_clear(); return t
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]; return h.z if h else None
if T.modifiers.get('WS78_lot_pocket_band_to_DTM_lower_only'): print('WS78A already applied'); raise SystemExit
B0=tbvh(T)
G=[o for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][0]; GB=tbvh(G)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws78/terrain78.py').read())
B1=tbvh(T)
BOX=(-258,-210,-132,-78)
def delta(x,y):
    a=hz(B0,x,y); b=hz(B1,x,y)
    return (a-b) if (a is not None and b is not None) else 0.0
OBJ=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS76_lot_','WS77_lot_median_island'))]
log={}
for o in OBJ:
    mw=o.matrix_world; mi=mw.inverted(); n=0; mx=0
    lot = 'lot_asphalt' in o.name or 'island' in o.name
    for v in o.data.vertices:
        p=mw@v.co
        if not (BOX[0]<p.x<BOX[1] and BOX[2]<p.y<BOX[3]): continue
        d=delta(p.x,p.y)
        if d<0.005: continue
        z=p.z-d
        g=hz(GB,p.x,p.y)
        if g is not None: z=max(z,g+(0.04 if lot else 0.055))
        if z<p.z-0.001:
            v.co=mi@Vector((p.x,p.y,z)); n+=1; mx=max(mx,p.z-z)
    o.data.update(); log[o.name]=(n,round(mx,2)); print('WS78A moved',o.name[:45],n,round(mx,2),flush=True)
# trees in pocket
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
trees=[]
for o in bpy.data.objects:
    if not o.name.startswith('T_') or o.type!='MESH': continue
    x,y=o.matrix_world.translation.x,o.matrix_world.translation.y
    if not (BOX[0]<x<BOX[1] and BOX[2]<y<BOX[3]): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; minz=min(p.z for p in bb)
    # ground = top-most of lots/island/terrain/WS68
    gz=[hz(B1,x,y),hz(GB,x,y)]
    for q in OBJ:
        if 'lot_asphalt' in q.name or 'island' in q.name:
            qi=q.matrix_world.inverted(); ok,loc,nn,ii=q.ray_cast(qi@Vector((x,y,400)),Vector((0,0,-1)))
            if ok: gz.append((q.matrix_world@loc).z)
    g=max(z for z in gz if z is not None)
    sh=0.0
    if minz>g-0.15: sh=minz-(g-0.25); o.location.z-=sh
    trees.append((o.name,round(x,1),round(y,1),round(minz,2),round(g,2),round(sh,2))); print('WS78A tree',trees[-1],flush=True)
T['ws78_pocket']=1
# transects
B2=tbvh(T)
for y in (-84,-86,-88,-90,-94,-100,-110,-120):
    row=[]
    for x in range(-258,-212,3):
        zs=[hz(B2,x,y),hz(GB,x,y)]
        for q in OBJ:
            if 'lot_asphalt' in q.name or 'island' in q.name:
                qi=q.matrix_world.inverted(); ok,loc,nn,ii=q.ray_cast(qi@Vector((x,y,400)),Vector((0,0,-1)))
                if ok: zs.append((q.matrix_world@loc).z)
        zs=[z for z in zs if z is not None]; row.append('%.2f'%max(zs) if zs else '.')
    print('WS78T',y,' '.join(row),flush=True)
json.dump({'moved':log,'trees':trees},open('/workspace/nj-scenes/montclair-state/scripts/ws78/apply78a_log.json','w'))
