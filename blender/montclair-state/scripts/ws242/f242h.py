# ws242 Codex P1 (PR #75, AGENTS rule 7 "markings are paint"): m2c242 brought in 'JR2 Crosswalk bars at OSM 287712280'
# as a modelled mesh. Paint the bars into the crossing's asphalt instead and delete the mesh: the crossing object gets its
# own copy of its material(s) whose Base Color is mixed to crosswalk white inside each bar polygon (world-XY half-plane
# tests on Geometry.Position, so the paint stays exactly where the ortho-placed bars were). Bar polygons copied verbatim.
import bpy
from mathutils import Vector
bars=next(o for o in bpy.data.objects if o.name.startswith('JR2 Crosswalk bars at OSM 287712280'))
xing=next(o for o in bpy.data.objects if o.name.startswith('JR2 Crossing at OSM 287712280'))
M=bars.matrix_world
POLYS=[]
for p in bars.data.polygons:
    V=[(M@bars.data.vertices[i].co) for i in p.vertices]
    a=sum((V[i].x*V[(i+1)%len(V)].y-V[(i+1)%len(V)].x*V[i].y) for i in range(len(V)))
    if a<0: V=V[::-1]
    POLYS.append(V)
def paint(mat):
    m=mat.copy(); m.name=mat.name[:40]+'_ws242_xwalk_paint'
    nt=m.node_tree; N=nt.nodes; L=nt.links.new
    bsdf=next(n for n in N if n.bl_idname=='ShaderNodeBsdfPrincipled'); bc=bsdf.inputs['Base Color']
    src=bc.links[0].from_socket if bc.links else None
    geo=N.new('ShaderNodeNewGeometry'); un=None
    for V in POLYS:
        acc=None
        for i in range(len(V)):
            A=V[i]; B=V[(i+1)%len(V)]; ex,ey=B.x-A.x,B.y-A.y
            d=N.new('ShaderNodeVectorMath'); d.operation='DOT_PRODUCT'; L(geo.outputs['Position'],d.inputs[0]); d.inputs[1].default_value=(-ey,ex,0.0)
            c=N.new('ShaderNodeMath'); c.operation='ADD'; L(d.outputs['Value'],c.inputs[0]); c.inputs[1].default_value=ey*A.x-ex*A.y
            g=N.new('ShaderNodeMath'); g.operation='GREATER_THAN'; L(c.outputs[0],g.inputs[0]); g.inputs[1].default_value=0.0
            if acc is None: acc=g.outputs[0]
            else:
                mm=N.new('ShaderNodeMath'); mm.operation='MULTIPLY'; L(acc,mm.inputs[0]); L(g.outputs[0],mm.inputs[1]); acc=mm.outputs[0]
        if un is None: un=acc
        else:
            mx=N.new('ShaderNodeMath'); mx.operation='MAXIMUM'; L(un,mx.inputs[0]); L(acc,mx.inputs[1]); un=mx.outputs[0]
    mix=N.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.name='ws242_xwalk_paint_mix'
    if src: L(src,mix.inputs['A'])
    else: mix.inputs['A'].default_value=tuple(bc.default_value)
    mix.inputs['B'].default_value=(0.78,0.78,0.76,1.0)   # worn crosswalk white (tone UNVERIFIED)
    L(un,mix.inputs['Factor']); L(mix.outputs['Result'],bc)
    return m
if xing.data.users>1: print('F242H WARNING crossing mesh shared; not painted',flush=True)
else:
    for i,sl in enumerate(xing.material_slots):
        if sl.material: xing.data.materials[i]=paint(sl.material)
nb=len(POLYS); bn=bars.name
_OFF[:]=[(a,b) for a,b in _OFF if a!=bn]
bpy.data.objects.remove(bars)
print('F242H painted',nb,'bar polygons into',xing.name[:40],[m.name for m in xing.data.materials],'; bars mesh removed',flush=True)
