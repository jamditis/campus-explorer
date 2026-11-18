# ws214e W36c: WS67 lane W edge stood ~2-5 cm above the KY carriageway edge next to it (visible crease across the lane mouth).
# WS67 W-edge verts (x < -255.3) -> KY top 0.25-0.6 m W of them + 3 mm; then both WS214 under-fill sheets clamped to (paving top - 6 mm).
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next((o for o in bpy.data.objects if o.name.startswith(p)),None)
W67=ob('WS67_CollegeAve_gap_asphalt'); KY=ob('KY_college_ave_carriageway_asphalt'); W4=ob('WS204_CollegeAve_lot_entrance_asphalt')
def bvh(o): M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
tk=bvh(KY); ne=0; dz=[]
me=W67.data; M=W67.matrix_world; Mi=M.inverted()
for v in me.vertices:
    w=M@v.co
    if w.x>=-255.3: continue
    z=None
    for off in (0.25,0.35,0.45,0.6):
        h=tk.ray_cast(Vector((w.x-off,w.y,200)),Vector((0,0,-1)),300)
        if h[0] is not None: z=h[0].z; break
    if z is None: continue
    dz.append(round(z+0.003-w.z,3)); v.co=Mi@Vector((w.x,w.y,z+0.003)); ne+=1
me.update()
TP=[bvh(o) for o in (KY,W4,W67)]
nc=0
for o in bpy.data.objects:
    if not o.name.startswith(('WS214_berm_tip_gap_asphalt_underfill','WS214_N_berm_tip_gap_asphalt_underfill')): continue
    me=o.data; M=o.matrix_world; Mi=M.inverted()
    for v in me.vertices:
        w=M@v.co; a=None
        for t in TP:
            h=t.ray_cast(Vector((w.x,w.y,200)),Vector((0,0,-1)),300)
            if h[0] is not None and (a is None or h[0].z>a): a=h[0].z
        if a is not None and w.z>a-0.006: v.co=Mi@Vector((w.x,w.y,a-0.006)); nc+=1
    me.update()
print('F214 e WS67 edge verts',ne,'dz',dz,'underfill clamped',nc,flush=True)
