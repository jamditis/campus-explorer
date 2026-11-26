# ws248 W62g pass 3 (CHAIN on ws248c): instead of sinking the fan, DELETE the big fan faces (area > 1.5 m2) that lie wholly
# inside the patch box shrunk 0.5 m (x -225.5..-186.5, y 44.5..135.5; ws248f: the first box left 0.5 m holes at the patch edges) in the WS248 snap group (faces only; dense 1 m terrain stays, snapped
# to LiDAR); the LiDAR patch fills the hole. Undo f248c's 0.3 m target lowering (dense terrain = exact LiDAR, patch +2 cm).
import bpy
TAG='F248D'; MN='WS248_E_stand_LiDAR_terrain_snap'
tg=bpy.data.objects['WS248_E_stand_LiDAR2023_ground_target']; n=0
if tg.get('ws248c_lowered'):
    for v in tg.data.vertices:
        if v.co.x>-224.5 and 45<v.co.y<135: v.co.z+=0.3; n+=1
    del tg['ws248c_lowered']
print(TAG,'target verts restored',n,flush=True)
ng=bpy.data.node_groups[MN]; N=ng.nodes; L=ng.links
if 'WS248_del_fan' not in N:
    go=next(x for x in N if x.type=='GROUP_OUTPUT'); st=next(x for x in N if x.type=='SET_POSITION')
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
    def cmp(sock,op,val):
        c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L.new(sock,c.inputs[0]); c.inputs[1].default_value=val; return c.outputs[0]
    def AND(a,b):
        n_=N.new('FunctionNodeBooleanMath'); n_.operation='AND'; L.new(a,n_.inputs[0]); L.new(b,n_.inputs[1]); return n_.outputs[0]
    inb=AND(AND(cmp(sp.outputs['X'],'GREATER_THAN',-225.5),cmp(sp.outputs['X'],'LESS_THAN',-186.5)),AND(cmp(sp.outputs['Y'],'GREATER_THAN',44.5),cmp(sp.outputs['Y'],'LESS_THAN',135.5)))
    ar=N.new('GeometryNodeInputMeshFaceArea'); big=cmp(ar.outputs[0],'GREATER_THAN',1.5)
    # point bool read on the face domain = all corners true
    ev=N.new('GeometryNodeFieldOnDomain'); ev.domain='FACE'; ev.data_type='BOOLEAN'; L.new(inb,ev.inputs[0])
    dl=N.new('GeometryNodeDeleteGeometry'); dl.name='WS248_del_fan'; dl.domain='FACE'; dl.mode='ONLY_FACE'
    L.new(st.outputs[0],dl.inputs['Geometry']); L.new(AND(ev.outputs[0],big),dl.inputs['Selection']); L.new(dl.outputs[0],go.inputs[0])
    print(TAG,'delete node added',flush=True)
