# ws256 subset-render CHAIN: low-memory crop. Appends a last GN modifier to the big terrain meshes that deletes faces outside
# CROP (x0,x1,y0,y1; default = CULL grown by CROPM m, default 160 m), so Cycles only syncs the visible ground
# (host balloon left ~7.4 GB; ws255 subset renders peaked at 8.4 GB VmHWM). Render-time only; never saved.
import bpy, os
_c=[float(v) for v in os.environ['CULL'].split(',')]; _m=float(os.environ.get('CROPM','160'))
_X0,_X1,_Y0,_Y1=[float(v) for v in os.environ['CROP'].split(',')] if os.environ.get('CROP') else (_c[0]-_m,_c[1]+_m,_c[2]-_m,_c[3]+_m)
def _crop_group():
    ng=bpy.data.node_groups.new('WS256_render_crop','GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links
    gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput'); pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ')
    L.new(pos.outputs[0],sep.inputs[0]); terms=[]
    for axis,val,op in ((0,_X0,'LESS_THAN'),(0,_X1,'GREATER_THAN'),(1,_Y0,'LESS_THAN'),(1,_Y1,'GREATER_THAN')):
        c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L.new(sep.outputs[axis],c.inputs[0]); c.inputs[1].default_value=val; terms.append(c)
    o1=N.new('FunctionNodeBooleanMath'); o1.operation='OR'; L.new(terms[0].outputs[0],o1.inputs[0]); L.new(terms[1].outputs[0],o1.inputs[1])
    o2=N.new('FunctionNodeBooleanMath'); o2.operation='OR'; L.new(terms[2].outputs[0],o2.inputs[0]); L.new(terms[3].outputs[0],o2.inputs[1])
    o3=N.new('FunctionNodeBooleanMath'); o3.operation='OR'; L.new(o1.outputs[0],o3.inputs[0]); L.new(o2.outputs[0],o3.inputs[1])
    d=N.new('GeometryNodeDeleteGeometry'); d.domain='POINT'; L.new(gi.outputs[0],d.inputs[0]); L.new(o3.outputs[0],d.inputs[1]); L.new(d.outputs[0],go.inputs[0])
    return ng
_ng=_crop_group(); _k=0
for _o in bpy.context.scene.objects:
    if _o.type=='MESH' and _o.data and len(_o.data.vertices)>200000:
        _md=_o.modifiers.new('WS256_render_crop','NODES'); _md.node_group=_ng; _k+=1; print('CROP256',_o.name,len(_o.data.vertices),flush=True)
print('CROP256 box %.0f %.0f %.0f %.0f objs %d'%(_X0,_X1,_Y0,_Y1,_k),flush=True)
