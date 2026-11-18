"""ws31: CCOM dock drive rebuild — the Roads_OSM dock drive (x≈-6..0, y -56..-20) rode 0.4–0.9 m above the LiDAR terrain on its west
and the jf3 apron on its east. Lower the drive (and its granite curb) onto one profile matching the apron grade, then seat terrain under
all pavement (seat.py RAISE=1), drape grass with the terrain, and strip lawn-edge / grass points that now sit on or poke through paving."""
import bpy, bmesh, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'
sc=bpy.context.scene
DX0,DX1,DY0,DY1=-8.0,1.2,-58.0,-19.0
def zt(y):  # apron grade fit (y -36 -> 135.59, y -24 -> 136.17); north run to the LiDAR grade at y -54 (134.55)
    if y>=-36: return 135.59+(y+36)*0.0483
    return 134.55+(y+54)*(135.59-134.55)/18.0
def taper(y):
    if y<-56: return 0.0
    if y<-53: return (y+56)/3
    if y>-20: return 0.0
    if y>-26: return (-20-y)/6
    return 1.0
road=bpy.data.objects['Roads_OSM']; mw=road.matrix_world; inv=mw.inverted()
# per-y drive centre z (old)
pts=[mw@v.co for v in road.data.vertices]
sel=[p for p in pts if DX0<p.x<DX1 and DY0<p.y<DY1]
ys=np.array([p.y for p in sel]); zs=np.array([p.z for p in sel])
def zold(y):
    m=np.abs(ys-y)<1.5
    return float(np.median(zs[m])) if m.any() else None
cnt=0; dzlog=[]
for v in road.data.vertices:
    p=mw@v.co
    if not(DX0<p.x<DX1 and DY0<p.y<DY1): continue
    zo=zold(p.y)
    if zo is None: continue
    d=(zt(p.y)-zo)*taper(p.y)
    if d>0: d=0.0
    v.co=inv@Vector((p.x,p.y,p.z+d)); cnt+=1; dzlog.append(d)
road.data.update(); print('drive verts lowered',cnt,'dz min %.2f'%min(dzlog))
cur=bpy.data.objects.get('Curbs_granite_OSM')
if cur:
    cm=cur.matrix_world; ci=cm.inverted(); c2=0
    def pts_of(o):
        if o.type=='MESH': return [(v,'co') for v in o.data.vertices]
        out=[]
        for sp in o.data.splines:
            out+= [(q,'co') for q in sp.bezier_points] if sp.type=='BEZIER' else [(q,'co4') for q in sp.points]
        return out
    for q,k in pts_of(cur):
        if k=='co4': p=cm@Vector(q.co[:3])
        else: p=cm@q.co
        if not(DX0-1<p.x<DX1+1 and DY0<p.y<DY1): continue
        zo=zold(p.y)
        if zo is None: continue
        d=(zt(p.y)-zo)*taper(p.y)
        if d>=0: continue
        n=ci@Vector((p.x,p.y,p.z+d))
        if k=='co4': q.co=(n.x,n.y,n.z,q.co[3])
        else:
            dl=n-q.co; q.co=n; q.handle_left+=dl; q.handle_right+=dl
        c2+=1
    print('curb pts lowered',c2,cur.type)
os.environ.update(BOX='-10,8,-60,-16',RAISE='1',PRAD='4',ITER='300',TAG='dock')
exec(open(R+'/scripts/ws31/seat.py').read())
# strip lawn edge / grass points over paving
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
bm=bmesh.new()
for o in [road,bpy.data.objects['CCOM_dock_apron_20261014jf3']]+([cur] if cur else []):
    ev=o.evaluated_get(dg); me2=ev.to_mesh()
    t=bmesh.new(); t.from_mesh(me2); t.transform(o.matrix_world); tm=bpy.data.meshes.new('t'); t.to_mesh(tm); t.free(); bm.from_mesh(tm); bpy.data.meshes.remove(tm); ev.to_mesh_clear()
PB2=BVHTree.FromBMesh(bm); bm.free()
for name in ('Lawn_worn_edge_along_walks','Lawn_grass_instanced (3g)','dS_grass_ccom_points'):
    o=bpy.data.objects.get(name)
    if not o: continue
    m=o.matrix_world; b=bmesh.new(); b.from_mesh(o.data); kill=[]
    for v in b.verts:
        p=m@v.co
        if not(-14<p.x<8 and -60<p.y<-16): continue
        h=PB2.ray_cast(Vector((p.x,p.y,p.z+3)),Vector((0,0,-1)),6)
        if h[0] is not None and abs(h[0].z-p.z)<0.6: kill.append(v)
    bmesh.ops.delete(b,geom=kill,context='VERTS'); b.to_mesh(o.data); b.free(); o.data.update(); print('removed over paving',name,len(kill))
