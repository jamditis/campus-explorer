# m2c241 follow-up (ws241): probe241g on ws241e: ground pokes through the merged Lot 28S asphalt (467 faces, up to 0.40 m
# at the lot's W edge) / stripes, and the Ice Arena SSW drive aisle + walk (z-fight, <= 0.05 m). Paving NOT moved (raise
# paving, never lower; the lot is OSM/ortho placed on north LiDAR). Ground pushed under instead:
#  - M3a base verts under each paving object: z = min(z, paving z - 0.06)
#  - Context skirt: one GN modifier per paving object at the END of the stack (WS234 pattern): ray-cast each evaluated skirt
#    point down onto the paving and, where it hits, hold the skirt 0.10 m under it (never raises).
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
PV=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('KP IceArena SSW drive-aisle','KP IceArena SSW walk','KQ Lot 28S asphalt','KR Lot 28S stall'))]
g=bpy.data.objects['M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam']; G=g.matrix_world; Gi=G.inverted()
me=g.data; n=len(me.vertices); co=np.empty(n*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
tot=0; mx=0
for o in PV:
    M=o.matrix_world; T=BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
    cs=[M@Vector(c) for c in o.bound_box]; x0=min(c.x for c in cs); x1=max(c.x for c in cs); y0=min(c.y for c in cs); y1=max(c.y for c in cs)
    k=0
    for i in range(n):
        p=G@Vector(co[i])
        if not (x0<=p.x<=x1 and y0<=p.y<=y1): continue
        h=T.ray_cast(Vector((p.x,p.y,p.z+3)),Vector((0,0,-1)),6)
        if h[0] is None: continue
        t=h[0].z-0.06
        if p.z>t and p.z-t<0.8:
            mx=max(mx,p.z-t); p.z=t; co[i]=tuple(Gi@p); k+=1
    tot+=k; print('F241G M3a verts under',o.name[:30],k,flush=True)
me.vertices.foreach_set('co',co.ravel()); me.update()
print('F241G M3a total lowered',tot,'max',round(mx,2),flush=True)
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
for o in PV:
    if o.name.startswith('KR'): continue   # stripes ride on the asphalt
    ng=bpy.data.node_groups.new('WS241_skirt_under_'+o.name[:20],'GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links
    gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=o
    pos=N.new('GeometryNodeInputPosition')
    up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; up.inputs[1].default_value=(0,0,50)
    L.new(pos.outputs[0],up.inputs[0])
    rc=N.new('GeometryNodeRaycast'); L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry'])
    L.new(up.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=100
    sh=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sh.inputs[0])
    sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
    tz=N.new('ShaderNodeMath'); tz.operation='SUBTRACT'; tz.inputs[1].default_value=0.10; L.new(sh.outputs['Z'],tz.inputs[0])
    cmp=N.new('ShaderNodeMath'); cmp.operation='GREATER_THAN'; L.new(sp.outputs['Z'],cmp.inputs[0]); L.new(tz.outputs[0],cmp.inputs[1])
    an=N.new('FunctionNodeBooleanMath'); an.operation='AND'; L.new(rc.outputs['Is Hit'],an.inputs[0]); L.new(cmp.outputs[0],an.inputs[1])
    cx=N.new('ShaderNodeCombineXYZ'); L.new(sp.outputs['X'],cx.inputs['X']); L.new(sp.outputs['Y'],cx.inputs['Y']); L.new(tz.outputs[0],cx.inputs['Z'])
    st=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],st.inputs['Geometry']); L.new(an.outputs[0],st.inputs['Selection']); L.new(cx.outputs[0],st.inputs['Position'])
    L.new(st.outputs[0],go.inputs[0])
    m=sk.modifiers.new(ng.name,'NODES'); m.node_group=ng; m.show_viewport=False
    import ctypes; v=ctypes.c_int.from_address(m.as_pointer()+20); v.value=v.value|1   # Realtime bit by DNA poke (merge208 pattern, no re-eval)
    print('F241G skirt modifier',m.name,flush=True)
