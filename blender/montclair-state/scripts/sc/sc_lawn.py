# sc: foreground of SA_CAM_eye_annex_mural_from_W (skirt x -150..-95, y 288..335) still reads blue/teal: the sb lawn blend is gated by
# QV_gf (ortho-reads-green) and the 2020 ortho there is shaded blue. That strip is lawn (sb grass, OSM walks drawn on top), so add an
# ungated sub-box (8 m fade) into the same max chain. Shader-only, UNVERIFIED. REVERT=1 removes SC_ nodes and relinks SB_max -> QV_gm.
import bpy,os
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']; nt=m.node_tree; N=nt.nodes; L=nt.links
gm=N['QV_gm']
for n in [n for n in N if n.name.startswith('SC_')]: N.remove(n)
L.new(N['SB_max'].outputs[0],gm.inputs[0]); print('SCL reverted')
if os.environ.get('REVERT')!='1':
    ps=N['QV_psep']
    def nn(t,nm,**kw):
        n=N.new(t); n.name='SC_'+nm; n.label=n.name
        for k,v in kw.items(): setattr(n,k,v)
        return n
    def MN(op,a,b,nm):
        n=nn('ShaderNodeMath',nm,operation=op)
        for i,v in enumerate((a,b)):
            if isinstance(v,(int,float)): n.inputs[i].default_value=v
            else: L.new(v,n.inputs[i])
        return n.outputs[0]
    def MR(v,a,b,nm):
        n=nn('ShaderNodeMapRange',nm,interpolation_type='SMOOTHSTEP'); L.new(v,n.inputs[0]); n.inputs[1].default_value=a; n.inputs[2].default_value=b; return n.outputs[0]
    X0,X1,Y0,Y1,F=-150.,-95.,288.,335.,8.
    g=MN('MULTIPLY',MN('MULTIPLY',MR(ps.outputs['X'],X0,X0+F,'x0'),MR(ps.outputs['X'],X1,X1-F,'x1'),'bx'),MN('MULTIPLY',MR(ps.outputs['Y'],Y0,Y0+F,'y0'),MR(ps.outputs['Y'],Y1,Y1-F,'y1'),'by'),'gate')
    mx=MN('MAXIMUM',N['SB_max'].outputs[0],g,'max'); L.new(mx,gm.inputs[0])
    print('SCL added',len([n for n in N if n.name.startswith('SC_')]))
if os.environ.get('SCSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
