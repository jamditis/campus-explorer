# ws78c: WS68 ground east blend column (x -256..-248.6) was still ramped up to the OLD (1-1.8 m too high) terrain edge -> olive spikes/ridge at the island W tip.
# Lower WS68 verts there to min(z, north dtm_filled); then lots/paint/island verts that rested on that ridge follow it down by the same amount.
import bpy,numpy as np,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
g=np.load('/workspace/nj-scenes/montclair-state/north/data/grid_1m.npz'); N=g['dtm_filled']
def dtm(x,y):
    fx=x+600-0.5; fy=y+260-0.5; i=int(math.floor(fx)); j=int(math.floor(fy)); a=fx-i; b=fy-j
    return float((N[j,i]*(1-a)+N[j,i+1]*a)*(1-b)+(N[j+1,i]*(1-a)+N[j+1,i+1]*a)*b)
G=[o for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][0]
def bvh(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]; return h.z if h else None
B0=bvh(G); mw=G.matrix_world; mi=mw.inverted(); n=0; mx=0
for v in G.data.vertices:
    p=mw@v.co
    if -256<=p.x<=-248 and -132<=p.y<=-78:
        z=min(p.z,dtm(p.x,p.y))
        if z<p.z-0.01: mx=max(mx,p.z-z); v.co=mi@Vector((p.x,p.y,z)); n+=1
G.data.update(); print('WS78C WS68 verts lowered',n,round(mx,2),flush=True)
B1=bvh(G)
OBJ=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS76_lot_','WS77_lot_median_island'))]
for o in OBJ:
    m=o.matrix_world; im=m.inverted(); k=0
    for v in o.data.vertices:
        p=m@v.co
        if not (-257<=p.x<=-246 and -132<=p.y<=-78): continue
        a=hz(B0,p.x,p.y); b=hz(B1,p.x,p.y)
        if a is None or b is None or a-b<0.02: continue
        if p.z<a+0.25: v.co=im@Vector((p.x,p.y,p.z-(a-b))); k+=1
    o.data.update(); print('WS78C followed',o.name[:45],k,flush=True)
for y in (-82,-84,-86,-88,-90,-94):
    print('WS78CT',y,' '.join('%.2f'%(hz(B1,x,y) or 0) for x in (-256,-254,-252,-250,-249)),flush=True)
