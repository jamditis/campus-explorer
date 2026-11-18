# Session ei (Oct 21 2026): flat membrane roofs no longer show the clay-tile normal map
# (read as corrugated ribs from the air). On faces with normal.z > ~0.985 the Principled
# normal now comes from a subtle membrane bump (seam lines Math.024 + fine wrinkle noise);
# sloped tile roofs keep the RoofingTiles006 normal map. Also gives the two plain CCOM east
# flat roof plates a procedural grey membrane (roll seams 3.05 m, mottling) instead of a flat colour.
# SAVE=1 to save; REVERT=1 restores.
import bpy, os
m=bpy.data.materials['Roof_tile_or_membrane']; nt=m.node_tree; N=nt.nodes; L=nt.links
bsdf=N['Principled BSDF']; nmap=N['Normal Map']
REV=os.environ.get('REVERT')=='1'
def rm(prefix):
    for n in [n for n in N if n.name.startswith(prefix)]: N.remove(n)
EAST=['CCOM_east_flat_roof_clean_20261014z','CCOM_east_roof_plate_z2_20261014z']
if REV:
    rm('EI_'); L.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
    for on in EAST:
        o=bpy.data.objects[on]; orig=o.get('ei_orig_mat')
        if orig: o.material_slots[0].material=bpy.data.materials[orig]
    print('EI REVERTED')
else:
    rm('EI_')
    for op,v in [('Math.003',None),('Math.037',None),('Math.038',None),('Math.024',None)]:
        print('EI op',op,N[op].operation)
    geo=N['Separate XYZ']
    fl=N.new('ShaderNodeMapRange'); fl.name='EI_flatmask'; fl.location=(bsdf.location.x-600,bsdf.location.y-900)
    fl.inputs['From Min'].default_value=0.95; fl.inputs['From Max'].default_value=0.985
    L.new(geo.outputs['Z'], fl.inputs['Value'])
    wr=N.new('ShaderNodeTexNoise'); wr.name='EI_wrinkle'; wr.inputs['Scale'].default_value=7.0; wr.inputs['Detail'].default_value=4.0
    L.new(N['Texture Coordinate.001'].outputs['Object'], wr.inputs['Vector'])
    h=N.new('ShaderNodeMath'); h.name='EI_height'; h.operation='MULTIPLY_ADD'
    L.new(N['Math.024'].outputs['Value'], h.inputs[0]); h.inputs[1].default_value=0.6
    L.new(wr.outputs['Fac'], h.inputs[2])
    bp=N.new('ShaderNodeBump'); bp.name='EI_bump'; bp.inputs['Strength'].default_value=0.12; bp.inputs['Distance'].default_value=0.02
    L.new(h.outputs['Value'], bp.inputs['Height'])
    mx=N.new('ShaderNodeMix'); mx.name='EI_normal_mix'; mx.data_type='VECTOR'
    L.new(fl.outputs['Result'], mx.inputs['Factor'])
    L.new(nmap.outputs['Normal'], mx.inputs[4]); L.new(bp.outputs['Normal'], mx.inputs[5])
    L.new(mx.outputs[1], bsdf.inputs['Normal'])
    # plain east roof plates -> procedural membrane
    for on in EAST:
        o=bpy.data.objects[on]; cur=o.material_slots[0].material
        if 'ei_orig_mat' not in o: o['ei_orig_mat']=cur.name
        base=bpy.data.materials[o['ei_orig_mat']]
        nm='EI_membrane_'+base.name
        mm=bpy.data.materials.get(nm) or base.copy(); mm.name=nm
        t=mm.node_tree; n2=t.nodes; l2=t.links
        for n in [n for n in n2 if n.name.startswith('EI_')]: n2.remove(n)
        b=[n for n in n2 if n.type=='BSDF_PRINCIPLED'][0]
        col=tuple(base.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)
        tc=n2.new('ShaderNodeTexCoord'); tc.name='EI_tc'
        sep=n2.new('ShaderNodeSeparateXYZ'); sep.name='EI_sep'; l2.new(tc.outputs['Object'],sep.inputs[0])
        # seam lines every 3.05 m along local x
        d=n2.new('ShaderNodeMath'); d.name='EI_div'; d.operation='DIVIDE'; l2.new(sep.outputs['X'],d.inputs[0]); d.inputs[1].default_value=3.05
        fr=n2.new('ShaderNodeMath'); fr.name='EI_frac'; fr.operation='PINGPONG'; l2.new(d.outputs[0],fr.inputs[0]); fr.inputs[1].default_value=0.5
        sm=n2.new('ShaderNodeMath'); sm.name='EI_seam'; sm.operation='LESS_THAN'; l2.new(fr.outputs[0],sm.inputs[0]); sm.inputs[1].default_value=0.012
        mot=n2.new('ShaderNodeTexNoise'); mot.name='EI_mottle'; mot.inputs['Scale'].default_value=0.35; mot.inputs['Detail'].default_value=5
        l2.new(tc.outputs['Object'],mot.inputs['Vector'])
        cr=n2.new('ShaderNodeValToRGB'); cr.name='EI_ramp'
        cr.color_ramp.elements[0].position=0.35; cr.color_ramp.elements[0].color=(col[0]*0.86,col[1]*0.86,col[2]*0.85,1)
        cr.color_ramp.elements[1].position=0.68; cr.color_ramp.elements[1].color=(min(1,col[0]*1.1),min(1,col[1]*1.1),min(1,col[2]*1.08),1)
        l2.new(mot.outputs['Fac'],cr.inputs['Fac'])
        ms=n2.new('ShaderNodeMix'); ms.name='EI_seamcol'; ms.data_type='RGBA'
        l2.new(sm.outputs[0],ms.inputs['Factor']); l2.new(cr.outputs['Color'],ms.inputs[6]); ms.inputs[7].default_value=(col[0]*0.7,col[1]*0.7,col[2]*0.68,1)
        l2.new(ms.outputs[2], b.inputs['Base Color'])
        wn=n2.new('ShaderNodeTexNoise'); wn.name='EI_wr'; wn.inputs['Scale'].default_value=7; l2.new(tc.outputs['Object'],wn.inputs['Vector'])
        hh=n2.new('ShaderNodeMath'); hh.name='EI_h'; hh.operation='MULTIPLY_ADD'; l2.new(sm.outputs[0],hh.inputs[0]); hh.inputs[1].default_value=0.6; l2.new(wn.outputs['Fac'],hh.inputs[2])
        bb=n2.new('ShaderNodeBump'); bb.name='EI_bump'; bb.inputs['Strength'].default_value=0.12; bb.inputs['Distance'].default_value=0.02
        l2.new(hh.outputs[0],bb.inputs['Height']); l2.new(bb.outputs['Normal'], b.inputs['Normal'])
        o.material_slots[0].material=mm
        print('EI east plate',on,'->',nm, 'scale',tuple(round(s,2) for s in o.scale))
    print('EI APPLIED')
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('EI SAVED')
