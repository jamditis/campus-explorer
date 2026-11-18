# Session is (2026-10-25): replace ir's cell-based seat arris (8 cm faces, ragged where the grid steps around the curve)
# with a shader edge-wear mask: Bevel-normal vs true-normal (radius ~2.5 cm) gives a thin, continuous band on every
# convex edge; an AO term (local, 0.12 m) zeroes it in concave corners so the joint dirt from iq stays dark.
# NOTE (is debug, 2:40 PM): mask renders show the bevel term mostly catches CONCAVE row junctions (which the AO term then
# zeroes); convex fronts are already rounded by smooth-by-angle shading, so the visible effect is very slight. Widening
# (radius 0.05, edge 0.55-0.97, AO 0.62-0.82) was tested in a debug render only and did not help. Next: a position-based mask.
# Order: ip build -> iq patch -> ir patch -> is patch. Env: SAVE=1, REVERT=1 (removes the 'is' nodes; arris faces stay reverted).
import bpy, os
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
SEAT=1
names=[m.name if m else None for m in me.materials]
# (a) put ir arris faces back on the seat stone (material slot kept, unused)
if 'ir_amphi_seat_arris' in names:
    k=names.index('ir_amphi_seat_arris'); c=0
    for p in me.polygons:
        if p.material_index==k: p.material_index=SEAT; c+=1
    me.update(); print('IS arris faces reverted',c)
def bsdf(m): return [x for x in m.node_tree.nodes if x.bl_idname=='ShaderNodeBsdfPrincipled'][0]
MATS=[('hn_amphi_seat_stone_blocks',1.22),('hn_amphi_riser_coursed_stone',1.15),('io_amphi_aisle_stone',1.18)]
for nm_,gain in MATS:
    m=bpy.data.materials[nm_]; nt=m.node_tree
    old=[n for n in nt.nodes if n.label.startswith('is_')]
    if old:
        # rewire base colour around our multiply, then delete
        mx=[n for n in old if n.label=='is_mul'][0]; src=mx.inputs[1].links[0].from_socket
        nt.links.new(src,bsdf(m).inputs['Base Color'])
        for n in old: nt.nodes.remove(n)
        print('IS removed old',nm_)
    if os.environ.get('REVERT')=='1': continue
    b=bsdf(m); src=b.inputs['Base Color'].links[0].from_socket
    def N(t,lab):
        n=nt.nodes.new(t); n.label=lab; return n
    bev=N('ShaderNodeBevel','is_bevel'); bev.samples=6; bev.inputs['Radius'].default_value=0.035
    geo=N('ShaderNodeNewGeometry','is_geo')
    dot=N('ShaderNodeVectorMath','is_dot'); dot.operation='DOT_PRODUCT'
    nt.links.new(bev.outputs['Normal'],dot.inputs[0]); nt.links.new(geo.outputs['Normal'],dot.inputs[1])
    em=N('ShaderNodeMapRange','is_edge'); em.inputs['From Min'].default_value=0.80; em.inputs['From Max'].default_value=0.985
    em.inputs['To Min'].default_value=1.0; em.inputs['To Max'].default_value=0.0; em.clamp=True
    nt.links.new(dot.outputs['Value'],em.inputs['Value'])
    ao=N('ShaderNodeAmbientOcclusion','is_ao'); ao.only_local=True; ao.samples=8; ao.inputs['Distance'].default_value=0.12
    am=N('ShaderNodeMapRange','is_aomask'); am.inputs['From Min'].default_value=0.80; am.inputs['From Max'].default_value=0.95; am.clamp=True
    nt.links.new(ao.outputs['AO'],am.inputs['Value'])
    # break-up noise so the wear isn't a perfect line
    tc=N('ShaderNodeTexCoord','is_tc'); nz=N('ShaderNodeTexNoise','is_noise'); nz.inputs['Scale'].default_value=9.0; nz.inputs['Detail'].default_value=4
    nt.links.new(tc.outputs['Object'],nz.inputs['Vector'])
    nm=N('ShaderNodeMapRange','is_nmask'); nm.inputs['From Min'].default_value=0.35; nm.inputs['From Max'].default_value=0.6; nm.inputs['To Min'].default_value=0.35; nm.clamp=True
    nt.links.new(nz.outputs['Fac'],nm.inputs['Value'])
    m1=N('ShaderNodeMath','is_m1'); m1.operation='MULTIPLY'; nt.links.new(em.outputs[0],m1.inputs[0]); nt.links.new(am.outputs[0],m1.inputs[1])
    m2=N('ShaderNodeMath','is_m2'); m2.operation='MULTIPLY'; nt.links.new(m1.outputs[0],m2.inputs[0]); nt.links.new(nm.outputs[0],m2.inputs[1])
    mx=N('ShaderNodeMixRGB','is_mul'); mx.blend_type='MULTIPLY'
    mx.inputs[2].default_value=(gain,gain*0.995,gain*0.985,1)
    nt.links.new(m2.outputs[0],mx.inputs[0]); nt.links.new(src,mx.inputs[1]); nt.links.new(mx.outputs[0],b.inputs['Base Color'])
    # slightly smoother where worn
    if not b.inputs['Roughness'].links:
        r0=b.inputs['Roughness'].default_value
        rm=N('ShaderNodeMapRange','is_rough'); rm.inputs['To Min'].default_value=r0; rm.inputs['To Max'].default_value=max(0.0,r0-0.1)
        nt.links.new(m2.outputs[0],rm.inputs['Value']); nt.links.new(rm.outputs[0],b.inputs['Roughness'])
    print('IS edgewear',nm_,'gain',gain)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('IS SAVED')
