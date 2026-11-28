# ws271b (merge208 CHAIN, on ws271a): UNIFY #4 Sprague grandstand lawn — seam step between WS68_RHD_ground_northDTM (W of x -249)
# and Terrain_LiDAR_DTM_1m (E of it). probe271d/e (first-hit grid, modifiers on, hidden helpers excluded) found Terrain_LiDAR
# standing 0.3-0.7 m above WS68 at the seam for y -121...-131 (the ws86 hump-to-DTM feather never reached x -249), which reads
# from the air as a straight crease/facet line. New GN modifier WS271_grandstand_seam_terrain_feather_lower_only (right after WS86):
# per vertex, delta = min(0, zWS68(-249.5, y) - zTerrain(-248.5, y)); offset z by delta * smoothstep weight (1 at the seam ->
# 0 at x -243.6), tapered to 0 at y -136/-119. Lower only, lawn only (no paving/walks in the band; probe271e). Not a raise.
import bpy, numpy as np, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
TAG='F271B'; OB=bpy.data.objects
ter=OB['Terrain_LiDAR_DTM_1m']; A=[o for o in OB if o.name.startswith('WS68_RHD_ground_northDTM')][0]
print(TAG,'A',A.name[:40],'identity',ter.matrix_world==Matrix.Identity(4),A.matrix_world==Matrix.Identity(4),flush=True)
assert ter.matrix_world==Matrix.Identity(4) and A.matrix_world==Matrix.Identity(4)
NG='WS271_grandstand_seam_terrain_feather_lower_only'   # 'terrain' in the name keeps it ON in subrend234 subset renders (TRX regex)
ng=bpy.data.node_groups.new(NG,'GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links.new
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput'); sp=N.new('GeometryNodeSetPosition')
pos=N.new('GeometryNodeInputPosition'); sx=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sx.inputs[0])
oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=A; oi.transform_space='RELATIVE'
def ray(target,xc):
    c=N.new('ShaderNodeCombineXYZ'); c.inputs['X'].default_value=xc; c.inputs['Z'].default_value=300.0; L(sx.outputs['Y'],c.inputs['Y'])
    r=N.new('GeometryNodeRaycast'); L(target,r.inputs['Target Geometry']); L(c.outputs[0],r.inputs['Source Position'])
    r.inputs['Ray Direction'].default_value=(0,0,-1); r.inputs['Ray Length'].default_value=500.0
    s=N.new('ShaderNodeSeparateXYZ'); L(r.outputs['Hit Position'],s.inputs[0]); return r,s
ra,sa=ray(oi.outputs['Geometry'],-249.5); rb,sb=ray(gi.outputs[0],-248.5)
def M(op,a=None,b=None,va=0.0,vb=0.0):
    m=N.new('ShaderNodeMath'); m.operation=op
    if a is not None: L(a,m.inputs[0])
    else: m.inputs[0].default_value=va
    if b is not None: L(b,m.inputs[1])
    else: m.inputs[1].default_value=vb
    return m.outputs[0]
d=M('SUBTRACT',sa.outputs['Z'],sb.outputs['Z']); d=M('MINIMUM',d,None,vb=0.0)
d=M('MULTIPLY',d,ra.outputs['Is Hit']); d=M('MULTIPLY',d,rb.outputs['Is Hit'])
def MR(src,f0,f1,t0,t1):
    m=N.new('ShaderNodeMapRange'); m.interpolation_type='SMOOTHSTEP'; m.clamp=True; L(src,m.inputs['Value'])
    m.inputs['From Min'].default_value=f0; m.inputs['From Max'].default_value=f1; m.inputs['To Min'].default_value=t0; m.inputs['To Max'].default_value=t1
    return m.outputs['Result']
wx=MR(sx.outputs['X'],-249.6,-243.6,1.0,0.0); wy1=MR(sx.outputs['Y'],-136.0,-134.0,0.0,1.0); wy2=MR(sx.outputs['Y'],-121.0,-119.0,1.0,0.0)
w=M('MULTIPLY',M('MULTIPLY',wx,wy1),wy2); off=M('MULTIPLY',d,w)
cz=N.new('ShaderNodeCombineXYZ'); L(off,cz.inputs['Z'])
L(gi.outputs[0],sp.inputs['Geometry']); L(cz.outputs[0],sp.inputs['Offset']); L(sp.outputs[0],go.inputs[0])
mod=ter.modifiers.new(NG,'NODES'); mod.node_group=ng
names=[m.name for m in ter.modifiers]; i86=names.index('WS86_grandstand_hump_to_DTM_lower_only')
ter.modifiers.move(len(names)-1,i86+1)
print(TAG,'order',[m.name for m in ter.modifiers][i86-1:i86+4],flush=True)
# verify: evaluate both grounds and compare at the seam / band
for o in (ter,A):
    for m in o.modifiers: m.show_viewport=True
dg=bpy.context.evaluated_depsgraph_get()
def tree(o,on=True):
    oe=o.evaluated_get(dg); me=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(me)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if not any(-256<v.co.x<-238 and -140<v.co.y<-114 for v in f.verts)],context='FACES')
    t=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear(); return t
TB,TA=tree(ter),tree(A)
def hz(t,x,y):
    r=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return r[0].z if r[0] else np.nan
for y in np.arange(-120.5,-136,-1.0):
    print(TAG,'y',y,'A(-249.5)',round(hz(TA,-249.5,y),2),'T(-248.5)',round(hz(TB,-248.5,y),2),'T(-246)',round(hz(TB,-246,y),2),'T(-243)',round(hz(TB,-243,y),2),flush=True)
for o in (ter,A):
    for m in o.modifiers: m.show_viewport=False
# merge208 restores only the modifiers it switched off at load (_OFF); register the new one so poke_restore turns its
# viewport (Realtime) bit back on before the save, like the other terrain modifiers (pattern of the ws260 scripts).
_OFF.append((ter.name,mod.name))
print(TAG,'registered for viewport restore',mod.name,flush=True)
