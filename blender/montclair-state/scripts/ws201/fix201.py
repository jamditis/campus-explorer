# ws201 W19: the thin wavy dark line in the Sprague-lot S bay = the WS81_lot_seam_underlay showing through the plan gaps between the
# WS75 and WS80 asphalt sheets, ~2.3 cm (p50; up to 5.4 cm) BELOW them -> a recessed slot whose walls/shadow read as a dark crack
# (probe p201a 0.1 m top-object grid + projection onto the ws200a close-up: every dark-line pixel sits on a WS75/WS80/WS81 boundary).
# Designer call: real lot asphalt is one continuous mat; joints between paving passes are flush. So the underlay acts as flush joint fill:
# RAISE-ONLY every WS81 vertex in the bay so it sits 4 mm under the local sheet top where covered, and 1 mm under the adjacent sheet
# surface where it is exposed in a gap (z of nearest sheet surface). Lift feathered to 0 over 1.5 m outside the bay. Sheets untouched.
import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1,FE=-264.0,-213.0,-108.5,-93.0,1.5
TOPS=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75_sprague_lot_asphalt','WS80_sprague_lot_fill_asphalt','WS82_sprague_lane_onesurface','WS94_lot_slit_filler','WS96_lot_E_edge_gap_filler'))]
V=[];F=[]
for o in TOPS:
    mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
T=BVHTree.FromPolygons(V,F)
def wt(x,y):
    d=max(X0-x,x-X1,Y0-y,y-Y1,0.0)
    if d>=FE: return 0.0
    t=1-d/FE; return t*t*(3-2*t)
U=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS81_lot_seam_underlay')][0]
mw=U.matrix_world; mi=mw.inverted(); n=0; ng=0; mx=0.0
for v in U.data.vertices:
    p=mw@v.co; w=wt(p.x,p.y)
    if w==0: continue
    h=T.ray_cast(Vector((p.x,p.y,p.z+1.0)),Vector((0,0,-1)),1.3)
    if h[0] is not None and h[0].z>p.z-0.01: tgt=h[0].z-0.004
    else:
        # exposed in a plan gap (or only a lower layer below): flush to the surrounding upper sheet surface
        zs=[]
        for r in (0.15,0.3,0.5):
            for k in range(12):
                a=k*math.pi/6; q=T.ray_cast(Vector((p.x+r*math.cos(a),p.y+r*math.sin(a),p.z+1.0)),Vector((0,0,-1)),1.3)
                if q[0] is not None and q[0].z>p.z-0.01: zs.append(q[0].z)
            if len(zs)>=3: break
        if not zs: continue
        zs.sort(); tgt=zs[len(zs)//2]-0.001; ng+=1
    d=(tgt-p.z)*w
    if d>0: p.z+=d; v.co=mi@p; n+=1; mx=max(mx,d)
U.data.update()
print('F201 WS81 lifted',n,'verts (gap',ng,') max',round(mx,3),flush=True)
del T,V,F
import gc; gc.collect()
