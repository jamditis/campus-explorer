# ws186b (Nov 16 ~11:47 AM ET) — Sprague Field is ARTIFICIAL TURF (2020 NJOGIS ortho: yard lines + red end-zone lettering, flat 115.7,
# 2023 LiDAR intensity 4.5–5.2k vs real grass 9.8–11.2k; prep/ws185_lot36N/NOTES.md §1). Main drew it with the striped campus lawn shader.
# Faces of the ground sheets whose centre lies inside the fix185 turf-edge curb (circle c=(-342.26,-179.12) R 44, W of the E straight) get a
# uniform artificial-turf material: no mowing stripes, dense even green (tone from the sunlit 2020 ortho, UNVERIFIED), faint infill speckle,
# low sheen. Yard lines / lettering NOT drawn (only in the ortho at 0.3 m; positions UNVERIFIED) — later pass.
import bpy, math
from mathutils import Vector
CX,CY,R=-342.26,-179.12,44.00
def sx(y): return -317.6+(y+214.2)*(1.9/14.2)
def inside(x,y): return math.hypot(x-CX,y-CY)<R+0.40 and x<sx(y)+0.40   # faces straddling the curb: the curb ribbon + lot + strip sit over the edge
m=bpy.data.materials.get('WS186_Sprague_artificial_turf_ortho2020_UNVERIFIEDtone')
if m is None:
    m=bpy.data.materials.new('WS186_Sprague_artificial_turf_ortho2020_UNVERIFIEDtone'); m.use_nodes=True; nt=m.node_tree; N=nt.nodes; L=nt.links
    bs=N['Principled BSDF']; bs.inputs['Roughness'].default_value=0.9; bs.inputs['Specular IOR Level'].default_value=0.15   # matte: no sky sheen at grazing angles
    tc=N.new('ShaderNodeTexCoord'); n1=N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value=0.35; n1.inputs['Detail'].default_value=3.0
    n2=N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value=60.0; n2.inputs['Detail'].default_value=1.0
    L.new(tc.outputs['Object'],n1.inputs['Vector']); L.new(tc.outputs['Object'],n2.inputs['Vector'])
    r=N.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color=(0.022,0.062,0.018,1); r.color_ramp.elements[1].color=(0.034,0.082,0.026,1)
    L.new(n1.outputs['Fac'],r.inputs['Fac'])
    mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.inputs['Factor'].default_value=0.12
    L.new(r.outputs['Color'],mx.inputs[6]); mx.inputs[7].default_value=(0.030,0.030,0.028,1)   # black rubber infill speckle
    g=N.new('ShaderNodeMath'); g.operation='GREATER_THAN'; g.inputs[1].default_value=0.62; L.new(n2.outputs['Fac'],g.inputs[0])
    mm=N.new('ShaderNodeMath'); mm.operation='MULTIPLY'; mm.inputs[1].default_value=0.5; L.new(g.outputs[0],mm.inputs[0]); L.new(mm.outputs[0],mx.inputs['Factor'])
    L.new(mx.outputs[2],bs.inputs['Base Color'])
    bp=N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.15; L.new(n2.outputs['Fac'],bp.inputs['Height']); L.new(bp.outputs['Normal'],bs.inputs['Normal'])
tot={}
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith(('WS181','WS182','WS185','WS186','WS184','WS169_light','WS167_Sprague_E_b')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<-386 or min(v.x for v in bb)>-316 or max(v.y for v in bb)<-224 or min(v.y for v in bb)>-136: continue
    me=o.data; M=o.matrix_world; sel=[]
    for p in me.polygons:
        if p.normal.z<0.7: continue
        c=M@p.center
        if not inside(c.x,c.y): continue
        sl=me.materials[p.material_index] if len(me.materials) else None
        if sl is not None and 'lawn' not in sl.name.lower() and 'grass' not in sl.name.lower(): continue
        sel.append(p)
    if not sel: continue
    if m.name not in [x.name for x in me.materials if x]: me.materials.append(m)
    k=[x.name if x else None for x in me.materials].index(m.name)
    for p in sel: p.material_index=k
    me.update(); tot[o.name[:36]]=len(sel)
print('FIX186B turf faces',tot,flush=True)
