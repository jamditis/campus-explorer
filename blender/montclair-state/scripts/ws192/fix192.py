# ws192: WS170b Lot 3 S-end concrete strip E END FACE (STATE ws191 "small light end face"). probe192.out: strip top 118.328 flat,
# E end at x ~ -298.82..-299.0 (slanted), WS191b lawn just E sits 118.22-118.31 -> the end face stands 2-11 cm proud and catches
# light. 2023 LiDAR (ws170/ws191 notes): ground continues rising gently E/S of the band under the canopy; a real cast pad ends flush
# with the turf that's banked against it (no exposed end face). Build: a 0.9 m lawn fillet from the strip's E top edge (0.5 cm below
# the top, tucked 3 cm under it) easing (smoothstep) down and TUCKING 2 cm under the WS191b lawn at its far edge and along its S side (ws192 cut test: a +1 cm far edge drew a dark crease), only where the lawn is >2 cm below the edge and
# only S of y -235.10 (the N corner meets the Lot 3 asphalt / curb line, left as is). Heights by raycast. Lawn mat from WS163.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def _b192(o):
    M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
STR192=[o for o in bpy.data.objects if o.name.startswith('WS170b_Lot3_S_end_curb_concrete_strip')][0]
TS192=_b192(STR192)
LAWN192=[_b192(o) for o in bpy.data.objects if o.name.startswith(('WS191b_','WS191c_','WS163_ground_patch_W_of_WS110','WS110_ground_patch_S'))]
def lawnz192(x,y):
    zs=[h[0].z for t in LAWN192 for h in [t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))] if h[0]]
    return max(zs) if zs else None
cols192=[]
for y in np.arange(-235.10,-236.47,-0.08):
    xe=None; ze=None
    for x in np.arange(-299.6,-298.3,0.01):
        h=TS192.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if h[0]: xe,ze=x,h[0].z
        elif xe is not None: break
    if xe is None: cols192.append(None); continue
    zl=lawnz192(xe+0.05,y)
    if zl is None or ze-zl<0.02: cols192.append(None); continue
    cols192.append((y,xe,ze))
print('FIX192 cols',sum(1 for c in cols192 if c),'of',len(cols192),flush=True)
bm=bmesh.new(); prev=None; nf=0
R192=[0.0,0.2,0.4,0.6,0.8,1.0]
for i192,c in enumerate(cols192):
    if c is None: prev=None; continue
    y,xe,ze=c; row=[]
    edge192=(i192==len(cols192)-1 or cols192[i192+1] is None)
    for t in R192:
        x=xe-0.03+0.93*t
        zl=lawnz192(x,y)
        if zl is None: zl=ze-0.1
        s=t*t*(3-2*t)
        z=(ze-0.005)*(1-s)+(zl-0.02)*s if t>0 else ze-0.005
        if 0<t<1: z=max(z,zl+0.004)
        if edge192 and t>0: z=min(z,zl-0.015)
        row.append(bm.verts.new((x,y,z)))
    if prev:
        for k in range(len(R192)-1): bm.faces.new((prev[k],prev[k+1],row[k+1],row[k])); nf+=1
    prev=row
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS192_Lot3_S_strip_E_end_lawn_fillet'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
uvl=me.uv_layers.new(name='UVMap')
for l in me.loops: v=me.vertices[l.vertex_index].co; uvl.data[l.index].uv=(v.x/10.0,v.y/10.0)
ob=bpy.data.objects.new('WS192_Lot3_S_strip_E_end_lawn_fillet_LiDAR_rise_UNVERIFIED',me)
lw=bpy.data.objects['WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED']
for cc in lw.users_collection: cc.objects.link(ob)
me.materials.append(lw.active_material)
print('FIX192 fillet faces',nf,'verts',len(me.vertices),flush=True)
