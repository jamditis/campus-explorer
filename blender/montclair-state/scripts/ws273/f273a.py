# ws273 f273a (merge208 CHAIN): UNIFY #4a + #4b — one lawn tone over the Sprague grandstand lawn / lot-pocket strip.
# #4b: the dark rectangle S of the Sprague lot (x -249..-235.5, y -113..-106) = PB regrid faces of Terrain_LiDAR_DTM_1m (GN-made,
#      not in the base mesh) carrying Ground_ortho_grass, which drapes the 2020 ortho there: the dark ribbed roof of the 2020
#      structure that stood on this lot (+ its NE shadow). New last GN WS273_lot_pocket_S_lawn_material sets those faces to the
#      grandstand lawn (WS82_Lawn_grandstand_no_ortho_UNVERIFIED) — only Ground_ortho_grass faces inside the box.
# #4a: the straight tone line at x -249 = WS68_Ground_ortho_grass_north2020 (W) vs the WS82 lawn (E). W of the seam the ortho is
#      the same 2020 roof (x -272..-249), so WS68 faces with centres in x -273..-249, y -136..-98 also get the WS82 lawn; the
#      edge moves to the roof's W edge where the ortho shows real grass. UNVERIFIED: what the ground is today (no post-2020 ortho).
import bpy
TAG='F273A'
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; A=[o for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground_northDTM')][0]
LAWN=bpy.data.materials['WS82_Lawn_grandstand_no_ortho_UNVERIFIED']; OG=bpy.data.materials['Ground_ortho_grass']
# --- #4b GN on Terrain (last in the stack)
ng=bpy.data.node_groups.new('WS273_lot_pocket_S_lawn_material','GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
ms=N.new('GeometryNodeMaterialSelection'); ms.inputs['Material'].default_value=OG
pos=N.new('GeometryNodeInputPosition'); sx=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sx.inputs[0])
def cmp(sock,op,val):
    c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L.new(sock,c.inputs[0]); c.inputs[1].default_value=val; return c.outputs[0]
B=(-249.2,-235.5,-113.3,-105.5)
conds=[cmp(sx.outputs[0],'GREATER_THAN',B[0]),cmp(sx.outputs[0],'LESS_THAN',B[1]),cmp(sx.outputs[1],'GREATER_THAN',B[2]),cmp(sx.outputs[1],'LESS_THAN',B[3]),ms.outputs[0]]
acc=conds[0]
for c in conds[1:]:
    a=N.new('FunctionNodeBooleanMath'); a.operation='AND'; L.new(acc,a.inputs[0]); L.new(c,a.inputs[1]); acc=a.outputs[0]
sm=N.new('GeometryNodeSetMaterial'); sm.inputs['Material'].default_value=LAWN
L.new(gi.outputs[0],sm.inputs['Geometry']); L.new(acc,sm.inputs['Selection']); L.new(sm.outputs[0],go.inputs[0])
md=T.modifiers.new('WS273_lot_pocket_S_lawn_material','NODES'); md.node_group=ng; md.show_viewport=True; md.show_render=True
print(TAG,'T mods last',[m.name for m in T.modifiers][-3:],'viewport',md.show_viewport,flush=True)
# --- #4a WS68 faces -> lawn
me=A.data; mw=A.matrix_world
names=[m.name if m else None for m in me.materials]
if LAWN.name not in names: me.materials.append(LAWN); names.append(LAWN.name)
li=names.index(LAWN.name); n=0; xs=[]; ys=[]
for p in me.polygons:
    c=mw@p.center
    if -273.0<c.x<-249.0 and -136.0<c.y<-98.0 and names[p.material_index]!=LAWN.name:
        p.material_index=li; n+=1; xs.append(c.x); ys.append(c.y)
me.update()
print(TAG,'WS68 faces -> lawn',n,'x',round(min(xs),1),round(max(xs),1),'y',round(min(ys),1),round(max(ys),1),'mats',names,flush=True)
print(TAG,'uv T',[u.name for u in T.data.uv_layers],'uv A',[u.name for u in me.uv_layers],flush=True)
print(TAG,'LAWN nodes',[(n.bl_idname, getattr(n,'uv_map',None) or getattr(n,'attribute_name',None)) for n in LAWN.node_tree.nodes if n.bl_idname in ('ShaderNodeUVMap','ShaderNodeAttribute','ShaderNodeTexCoord','ShaderNodeTexImage')],flush=True)
