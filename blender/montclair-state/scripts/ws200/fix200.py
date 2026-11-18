# ws200 W5: WS169c_Lot3_S_end_lawn_bridge (ws169 hidden under-layer, LiDAR 1 m facets). Probe p200a (0.25 m top-object grid, real GN terrain):
# its 0.41 m plan jitter at (-327.6,-232.2) is NEVER visible (fully under WS181 Lot 36 asphalt); only 22 cells reach the top: 1-7 cm
# poke-ups through the WS187 bank-toe lawn at x -314..-310.7, y -233.3..-230.7 (+1 mm under WS185 at (-338.5,-229)) = lumpy facets on
# the bank toe. Fix: keep it as a hidden under-layer -> every WS169c vertex covered by a visible lawn/paving sheet is clamped to
# >= 4 cm under that sheet (lowering a hidden under-layer only; covering sheets untouched).
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def _o(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
B200=_o('WS169c_Lot3_S_end_lawn_bridge')
COV200=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS187_Lot3_W_shoulder_toe','WS185_Lot36_N_grass','WS162_Lot3_W_shoulder_lawn','WS186_Lot3_S_bank_lawn','WS163_ground_patch_W_of_WS110','WS181_Lot36_asphalt','WS163_Lot3_aisle_S_drive','WS167_ground_W_of_Lot3_bank'))]
V=[];F=[]
for o in COV200:
    mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
T200=BVHTree.FromPolygons(V,F); mw=B200.matrix_world; mi=mw.inverted(); n=0; mx=0
for v in B200.data.vertices:
    w=mw@v.co; zs=[]; z0=w.z+3
    for _ in range(6):
        h=T200.ray_cast(Vector((w.x,w.y,z0)),Vector((0,0,-1)),z0-(w.z-1))
        if not h[0]: break
        zs.append(h[0].z); z0=h[0].z-0.001
    zc=min(zs) if zs else None   # lowest covering sheet over this vertex (lawn on lawn)
    if zc is not None and w.z>zc-0.04:
        nz=zc-0.04; mx=max(mx,w.z-nz); w.z=nz; v.co=mi@w; n+=1
B200.data.update()
print('F200 W5 clamp',n,'verts max',round(mx,3),'covers',[(o.name[:24],len(o.modifiers)) for o in COV200],flush=True)
