# ws191c: the dark wedge below the WS170b Lot 3 S-end concrete strip in the E eye view = the strip's S (back) side face exposed:
# along x -304.6..-299 its back edge stands up to ~0.16 m above the WS163 lawn (probe191e.out: x -300.2 strip 118.17 vs lawn
# 118.01, lawn regains the strip level ~0.8 m further S). 2023 LiDAR (ws170 note): ground RISES ~0.3 m S of the concrete band,
# i.e. the real lawn meets the strip back edge, no exposed face. Build: a 1.0 m lawn fillet sheet from the strip back edge
# (0.5 cm below its top, tucked 3 cm under the strip) easing (smoothstep) down onto the existing lawn (+1 cm) 1.0 m S; only
# where the lawn is > 3 cm below the edge. Lawn material from WS163. Edge heights measured by raycast, not guessed.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def _b191c(o):
    M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
STR191c=[o for o in bpy.data.objects if o.name.startswith('WS170b_Lot3_S_end_curb_concrete_strip')][0]
TS=_b191c(STR191c)
LAWN191c=[_b191c(o) for o in bpy.data.objects if o.name.startswith(('WS163_ground_patch_W_of_WS110','WS191b_','WS190b_','WS110_ground_patch_S'))]
def lawnz(x,y):
    zs=[h[0].z for t in LAWN191c for h in [t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))] if h[0]]
    return max(zs) if zs else None
cols=[]
for x in np.arange(-304.4,-299.09,0.2):
    yb=None; zb=None
    for y in np.arange(-234.6,-237.6,-0.02):
        h=TS.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if h[0]: yb,zb=y,h[0].z
        elif yb is not None: break
    if yb is None: continue
    zl=lawnz(x,yb-0.05)
    if zl is None or zb-zl<0.03: cols.append(None); continue
    cols.append((x,yb,zb))
print('FIX191C cols',sum(1 for c in cols if c),'of',len(cols),flush=True)
bm=bmesh.new(); prev=None; nf=0
R=[0.0,0.25,0.5,0.75,1.0]
for c in cols:
    if c is None: prev=None; continue
    x,yb,zb=c; row=[]
    for t in R:
        y=yb+0.03-1.03*t
        zl=lawnz(x,y)
        if zl is None: zl=zb-0.1
        s=t*t*(3-2*t)
        z=(zb-0.005)*(1-s)+(zl+0.01)*s if t>0 else zb-0.005
        if t>0: z=max(z,zl+0.01)
        row.append(bm.verts.new((x,y,z)))
    if prev:
        for k in range(len(R)-1): bm.faces.new((prev[k],row[k],row[k+1],prev[k+1])); nf+=1
    prev=row
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
me=bpy.data.meshes.new('WS191c_Lot3_S_strip_back_lawn_fillet'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
uvl=me.uv_layers.new(name='UVMap')
for l in me.loops: v=me.vertices[l.vertex_index].co; uvl.data[l.index].uv=(v.x/10.0,v.y/10.0)
ob=bpy.data.objects.new('WS191c_Lot3_S_strip_back_lawn_fillet_LiDAR_rise_UNVERIFIED',me)
lw=bpy.data.objects['WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED']
for cc in lw.users_collection: cc.objects.link(ob)
me.materials.append(lw.active_material)
print('FIX191C fillet faces',nf,'verts',len(me.vertices),flush=True)
