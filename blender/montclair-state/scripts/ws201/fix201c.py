# ws201 W19 pass c: after fix201b the hidden fillers (WS81 seam underlay, WS94 slit filler) poke 0-3 mm THROUGH the WS75/WS80 sheets in
# thin strips along the old seam (their dense triangles chord above the sheets) -> flat-shaded slivers read as short dark dashes.
# Tuck them: any filler vertex in the bay that has a main sheet above it (or within 2 mm) goes to 6 mm under that sheet; filler verts in real
# plan gaps (no sheet above) stay where fix201b put them (flush joint fill). Never below its ws200a height.
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-264.0,-213.0,-108.5,-93.0
MS=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75_sprague_lot_asphalt','WS80_sprague_lot_fill_asphalt'))]
V=[];F=[]
for o in MS:
    mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
TM=BVHTree.FromPolygons(V,F)
ORIG=globals().get('ORIG201',{})
n=0
for o in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS81_lot_seam_underlay','WS94_lot_slit_filler'))]:
    mw=o.matrix_world; mi=mw.inverted(); oz=ORIG.get(o.name)
    for k,v in enumerate(o.data.vertices):
        p=mw@v.co
        if not (X0<p.x<X1 and Y0<p.y<Y1): continue
        h=TM.ray_cast(Vector((p.x,p.y,p.z+0.5)),Vector((0,0,-1)),0.53)
        if h[0] is None: continue
        if h[0].z-p.z<0.002 or p.z>h[0].z-0.006:
            t=h[0].z-0.006
            if oz is not None: t=max(t,oz[k])
            if t<p.z: p.z=t; v.co=mi@p; n+=1
    o.data.update()
print('F201c tucked filler verts',n,flush=True)
del TM,V,F
