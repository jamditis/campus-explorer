# ws201 (3): faint hairline right of ISA3 (accessible lot row B, ~(-235.4,-81.0)). Probe p201isa (0.025 m top grid, real terrain):
# a 2.5-5 cm wide diagonal slit where the WS81 seam underlay shows 6-9 mm BELOW the WS75/WS76 asphalt on both sides (+ 3 mm WS75/WS76 mismatch).
# Designer call: joints in a lot mat are flush. RAISE-ONLY: WS81 verts in the box that are exposed (no lot sheet above) go to the median of
# the surrounding sheet tops (r 0.05-0.3 m) - 1 mm; covered WS81 verts sit 1.5 mm under the sheet top (the slit is narrower than the WS81 vertex spacing, so its covered verts set the slit floor).
import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-246.5,-229.5,-84.0,-76.5
TOPS=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75_sprague_lot_asphalt','WS76_accessible_lot','WS94_lot_slit_filler','WS96_lot_E_edge_gap_filler','WS199_lot_gap_patch')) and 'paint' not in o.name.lower()]
V=[];F=[]
for o in TOPS:
    mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
T=BVHTree.FromPolygons(V,F)
U=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS81_lot_seam_underlay')][0]
mw=U.matrix_world; mi=mw.inverted(); ne=0; nc=0; mx=0
for v in U.data.vertices:
    p=mw@v.co
    if not (X0<p.x<X1 and Y0<p.y<Y1): continue
    h=T.ray_cast(Vector((p.x,p.y,p.z+0.5)),Vector((0,0,-1)),0.52)
    if h[0] is not None and h[0].z>p.z-0.01:
        t=h[0].z-0.0015
        if t>p.z: mx=max(mx,t-p.z); p.z=t; v.co=mi@p; nc+=1
        continue
    zs=[]
    for r in (0.05,0.1,0.2,0.3):
        for k in range(12):
            a=k*math.pi/6; q=T.ray_cast(Vector((p.x+r*math.cos(a),p.y+r*math.sin(a),p.z+0.5)),Vector((0,0,-1)),0.6)
            if q[0] is not None and q[0].z>p.z-0.01: zs.append(q[0].z)
        if len(zs)>=4: break
    if len(zs)<2: continue
    zs.sort(); t=zs[len(zs)//2]-0.001
    if t>p.z and t-p.z<0.03: mx=max(mx,t-p.z); p.z=t; v.co=mi@p; ne+=1
U.data.update()
print('F201d WS81 exposed lifted',ne,'covered lifted',nc,'max',round(mx,3),flush=True)
del T,V,F
